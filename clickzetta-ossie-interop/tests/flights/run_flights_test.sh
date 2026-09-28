#!/usr/bin/env bash
# End-to-end test: apache/ossie examples/flights.yaml -> ClickZetta semantic view, queried and checked.
#
#   bash tests/flights/run_flights_test.sh <cz-cli-profile> [path/to/flights.yaml]
#
# Everything lives in schema ossie_flights_test (created here; the script stops if it already
# exists) and is dropped at the end, also on failure. Results: tests/flights/out/<timestamp>/
set -uo pipefail
PROFILE="${1:?usage: bash tests/flights/run_flights_test.sh <cz-cli-profile> [flights.yaml]}"
HERE="$(cd "$(dirname "$0")" && pwd)"
S="$HERE/../../scripts"
. "$HERE/../lib/lock.sh"
FLIGHTS="${2:-$HERE/../fixtures/flights.ossie.yaml}"   # copy of apache/ossie examples/flights.yaml
[ -f "$FLIGHTS" ] || { echo "flights.yaml not found; pass its path as the 2nd argument"; exit 2; }
SCHEMA=ossie_flights_test
OUT="$HERE/out/$(date +%Y%m%d_%H%M%S)"; mkdir -p "$OUT"
SUMMARY="$OUT/summary.txt"
CZ=(cz-cli -p "$PROFILE")
log() { echo "$*" | tee -a "$SUMMARY"; }
res() { log "$1  $2"; }
command -v cz-cli >/dev/null || { echo "cz-cli not found in PATH"; exit 2; }
PY=python3
if ! $PY -c "import yaml, jsonschema" 2>/dev/null; then
  VENV="$HERE/../live_out/.venv"
  [ -x "$VENV/bin/python" ] || { python3 -m venv "$VENV" && "$VENV/bin/pip" -q install pyyaml jsonschema; } || exit 2
  PY="$VENV/bin/python"
fi
sql()  { "${CZ[@]}" sql --no-limit --no-truncate "$@"; }
sqlw() { "${CZ[@]}" sql --write --no-limit --no-truncate "$@"; }
batch() {  # batch <out-file> <cz-cli args...>: --batch exits 0 even when a statement fails, so check the JSON
  local out="$1"; shift
  sqlw --batch "$@" > "$out" 2>&1 && ! grep -q '"error":{' "$out"
}
log "flights test: profile=$PROFILE file=$FLIGHTS"
"${CZ[@]}" --version > "$OUT/cz_version.txt" 2>&1 || true
sql -e "SELECT current_workspace(), current_user()" > "$OUT/env.json" 2>&1 || true

cleanup() {
  for v in flights_sv flights_tree_sv flights_raw_sv; do sqlw -e "DROP SEMANTIC VIEW IF EXISTS $SCHEMA.$v" >> "$OUT/99_cleanup.log" 2>&1; done
  for t in flights runways routes aircraft airports carriers; do sqlw -e "DROP TABLE IF EXISTS $SCHEMA.$t" >> "$OUT/99_cleanup.log" 2>&1; done
  if sqlw -e "DROP SCHEMA IF EXISTS $SCHEMA" >> "$OUT/99_cleanup.log" 2>&1; then log "cleanup: schema $SCHEMA dropped"
  else log "cleanup: DROP SCHEMA failed - see 99_cleanup.log"; fi
  release_lock
}
trap cleanup EXIT
# after the trap, so an early exit anywhere below still releases the lock through cleanup().
# On refusal we hold nothing, so drop the trap rather than let cleanup claim to have dropped a
# schema this run never created.
acquire_lock "$PROFILE" || { trap - EXIT; exit 3; }

# ---- 1. schema, tables, data
if ! sqlw -e "CREATE SCHEMA $SCHEMA" > "$OUT/01_schema.json" 2>&1; then
  log "ABORT: could not create schema $SCHEMA (already exists?) - see 01_schema.json"; exit 1
fi
$PY "$HERE/gen_flights.py" --schema $SCHEMA --out "$OUT" > /dev/null
batch "$OUT/02_tables.json" -f "$OUT/tables.sql" && res PASS "create 6 tables + data" \
  || { res FAIL "create tables (see 02_tables.json)"; exit 1; }
sql -e "SELECT COUNT(*) FROM $SCHEMA.flights" > "$OUT/02_count.json" 2>&1

# ---- 2. the Ossie file as-is
$PY "$S/validate_ossie.py" "$FLIGHTS" > "$OUT/10_validate_source.log" 2>&1 && res PASS "flights.yaml validates" || res FAIL "flights.yaml validation"
$PY "$S/ossie_to_sv.py" "$FLIGHTS" --view $SCHEMA.flights_raw_sv --source-map "DATABASE.SCHEMA=$SCHEMA" \
  -o "$OUT/11_raw.sql" > "$OUT/11_raw.log" 2>&1 && grep -q "no relationships" "$OUT/11_raw.log" \
  && res PASS "raw import: embedded model has no keys/relationships -> isolated tables + warning (expected)" \
  || res FAIL "raw import (see 11_raw.log)"

# ---- 3. enrich from the ontology, with and without the agent review
$PY "$S/enrich_from_ontology.py" "$FLIGHTS" -o "$OUT/20_core_auto.yaml" --issues "$OUT/20_enrich_auto.json" > "$OUT/20_enrich_auto.log" 2>&1
$PY "$S/enrich_from_ontology.py" "$FLIGHTS" -o "$OUT/21_core.yaml" --review "$HERE/review.yaml" --issues "$OUT/21_enrich.json" > "$OUT/21_enrich.log" 2>&1 \
  && res PASS "enrich from ontology (+ review)" || res FAIL "enrich (see 21_enrich.log)"
$PY "$S/validate_ossie.py" "$OUT/21_core.yaml" > "$OUT/22_validate_core.log" 2>&1 && res PASS "enriched core model validates" || res FAIL "enriched core validation"
printf 'drop_relationships: [route_destination, aircraft_carrier]\n' > "$OUT/review_dep.yaml"
cat "$HERE/review.yaml" >> "$OUT/review_dep.yaml"
$PY "$S/enrich_from_ontology.py" "$FLIGHTS" -o "$OUT/23_core_dep.yaml" --review "$OUT/review_dep.yaml" > /dev/null 2>&1

# ---- 4. import and create the semantic views
$PY "$S/ossie_to_sv.py" "$OUT/21_core.yaml" --view $SCHEMA.flights_sv --source-map "DATABASE.SCHEMA=$SCHEMA" \
  -o "$OUT/30_flights_sv.sql" --issues "$OUT/30_import.json" > "$OUT/30_import.log" 2>&1 \
  && res PASS "import generates DDL" || res FAIL "import (see 30_import.log)"
if batch "$OUT/31_create_flights_sv.json" -f "$OUT/30_flights_sv.sql"; then
  res PASS "create flights_sv (named role-playing ROUTE->AIRPORT relationships + two FLIGHT->CARRIER paths, metrics pick paths with USING)"
else
  res OBSERVED "flights_sv with role-playing joins rejected: $(tr '\n' ' ' < "$OUT/31_create_flights_sv.json" | cut -c1-300)"
fi
$PY "$S/ossie_to_sv.py" "$OUT/23_core_dep.yaml" --view $SCHEMA.flights_tree_sv --source-map "DATABASE.SCHEMA=$SCHEMA" \
  -o "$OUT/32_flights_tree_sv.sql" > /dev/null 2>&1
batch "$OUT/33_create_dep_sv.json" -f "$OUT/32_flights_tree_sv.sql" && res PASS "create flights_tree_sv (tree-shaped: route_destination and aircraft_carrier dropped)" \
  || res FAIL "create flights_tree_sv (see 33_create_dep_sv.json)"
if ! grep -q '^PASS  create flights_sv' "$SUMMARY"; then  # fall back so the remaining queries still run
  sed "s/$SCHEMA.flights_tree_sv/$SCHEMA.flights_sv/g" "$OUT/32_flights_tree_sv.sql" > "$OUT/34_fallback.sql"
  batch "$OUT/34_fallback.json" -f "$OUT/34_fallback.sql" && res INFO "flights_sv created from the departure-only model as fallback"
fi
for k in TABLES RELATIONSHIPS FACTS DIMENSIONS METRICS; do
  sql -e "SHOW SEMANTIC $k IN $SCHEMA.flights_sv" > "$OUT/35_show_$k.json" 2>&1
done

# ---- 5. queries vs independent sqlite results
$PY "$HERE/run_queries.py" --cz-cli "cz-cli -p $PROFILE" --schema $SCHEMA --queries "$OUT/queries.json" --out "$OUT" \
  2>&1 | tee -a "$SUMMARY"

# ---- 5b. FACTS, WHERE and outer SQL. The 13 above only ever use DIMENSIONS+METRICS; each case here
#          is compared against a hand-written query over the physical tables instead of a
#          precomputed expectation, so the check is an independent implementation.
$PY "$HERE/run_extended_queries.py" --cz-cli "cz-cli -p $PROFILE" --schema $SCHEMA --out "$OUT" \
  2>&1 | tee -a "$SUMMARY"

# ---- 6. export back to Ossie and compare with what was imported
$PY "$S/sv_dump.py" --cz-cli "cz-cli -p $PROFILE" --view $SCHEMA.flights_sv -o "$OUT/40_dump.json" > "$OUT/40_dump.log" 2>&1 \
  && res PASS "dump flights_sv" || res FAIL "dump flights_sv (see 40_dump.log)"
$PY "$S/sv_to_ossie.py" "$OUT/40_dump.json" -o "$OUT/41_export.yaml" > "$OUT/41_export.log" 2>&1 && res PASS "export flights_sv to Ossie" || res FAIL "export (see 41_export.log)"
$PY "$S/validate_ossie.py" "$OUT/41_export.yaml" > "$OUT/42_validate_export.log" 2>&1 && res PASS "exported model validates" || res FAIL "exported model validation"
$PY "$S/ossie_diff.py" "$OUT/21_core.yaml" "$OUT/41_export.yaml" > "$OUT/43_diff.txt" 2>&1 \
  && res PASS "export equals the imported model (sidecar restores Ossie-only metadata)" || res FAIL "export differs (see 43_diff.txt)"

# ---- 7. ontology back from the exported model
$PY "$S/derive_ontology.py" "$OUT/41_export.yaml" -o "$OUT/50_ontology.yaml" > "$OUT/50_derive.log" 2>&1
$PY "$S/validate_ossie.py" "$OUT/50_ontology.yaml" > "$OUT/51_validate_ontology.log" 2>&1 && res PASS "derived ontology validates" || res FAIL "derived ontology validation"
log "done - results in $OUT"
