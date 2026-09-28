#!/usr/bin/env bash
# End-to-end test: apache/ossie examples/tpcds_semantic_model.yaml -> ClickZetta semantic view.
#
#   bash tests/tpcds/run_tpcds_test.sh <cz-cli-profile>
#
# The file already has keys, 4 relationships and ANSI_SQL metrics, so it imports directly. It covers
# multi-table metrics (split into PRIVATE per-table metrics + a view-scoped metric), window metrics,
# a `||` dimension and 3-part sources mapped with --source-map.
# Everything lives in schema ossie_skill_test (created here; the script stops if it already exists)
# and is dropped at the end, also on failure. Results: tests/tpcds/out/<timestamp>/
set -uo pipefail
PROFILE="${1:?usage: bash tests/tpcds/run_tpcds_test.sh <cz-cli-profile>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
S="$HERE/../../scripts"
. "$HERE/../lib/lock.sh"
MODEL="$HERE/../fixtures/tpcds.ossie.yaml"   # copy of apache/ossie examples/tpcds_semantic_model.yaml
SCHEMA=ossie_skill_test
OUT="$HERE/out/$(date +%Y%m%d_%H%M%S)"; mkdir -p "$OUT"
SUMMARY="$OUT/summary.txt"
CZ=(cz-cli -p "$PROFILE")
log() { echo "$*" | tee -a "$SUMMARY"; }
res() { log "$1  $2"; }
command -v cz-cli >/dev/null || { echo "cz-cli not found in PATH"; exit 2; }
PY=python3
$PY -c "import yaml, jsonschema" 2>/dev/null || { echo "needs pyyaml + jsonschema"; exit 2; }
sql()  { "${CZ[@]}" sql --no-limit --no-truncate "$@"; }
sqlw() { "${CZ[@]}" sql --write --no-limit --no-truncate "$@"; }
batch() {  # batch <out-file> <cz-cli args...>: --batch exits 0 even when a statement fails, so check the JSON
  local out="$1"; shift
  sqlw --batch "$@" > "$out" 2>&1 && ! grep -q '"error":{' "$out"
}
log "tpcds test: profile=$PROFILE"

cleanup() {
  sqlw -e "DROP SEMANTIC VIEW IF EXISTS $SCHEMA.tpcds_sv" >> "$OUT/99_cleanup.log" 2>&1
  for t in store_sales date_dim customer item store; do sqlw -e "DROP TABLE IF EXISTS $SCHEMA.$t" >> "$OUT/99_cleanup.log" 2>&1; done
  if sqlw -e "DROP SCHEMA IF EXISTS $SCHEMA" >> "$OUT/99_cleanup.log" 2>&1; then log "cleanup: schema $SCHEMA dropped"
  else log "cleanup: DROP SCHEMA failed - see 99_cleanup.log"; fi
  release_lock
}
trap cleanup EXIT
# after the trap, so an early exit anywhere below still releases the lock through cleanup().
# On refusal we hold nothing, so drop the trap rather than let cleanup claim to have dropped a
# schema this run never created.
acquire_lock "$PROFILE" || { trap - EXIT; exit 3; }

if ! sqlw -e "CREATE SCHEMA $SCHEMA" > "$OUT/01_schema.json" 2>&1; then
  log "ABORT: could not create schema $SCHEMA (already exists?) - see 01_schema.json"; exit 1
fi

$PY "$HERE/gen_tpcds.py" --schema $SCHEMA --out "$OUT" > /dev/null
batch "$OUT/02_tables.json" -f "$OUT/tables.sql" && res PASS "create 5 tables + data" || { res FAIL "create tables (see 02_tables.json)"; exit 1; }

$PY "$S/validate_ossie.py" "$MODEL" > "$OUT/10_validate.log" 2>&1 && res PASS "tpcds model validates" || res FAIL "tpcds validation"
$PY "$S/ossie_to_sv.py" "$MODEL" --view $SCHEMA.tpcds_sv --source-map "tpcds.public=$SCHEMA" \
  -o "$OUT/11_tpcds_sv.sql" --issues "$OUT/11_import.json" > "$OUT/11_import.log" 2>&1 \
  && res PASS "import generates DDL" || res FAIL "import (see 11_import.log)"
grep -q "^    customer_lifetime_value AS " "$OUT/11_tpcds_sv.sql" && grep -q "PRIVATE customer.customer_lifetime_value__customer_" "$OUT/11_tpcds_sv.sql" \
  && res PASS "multi-table metric split into PRIVATE per-table metrics + view-scoped metric" || res FAIL "multi-table metric split"
! grep -q "brand_rank_in_store AS" "$OUT/11_tpcds_sv.sql" && grep -q "brand_rank_in_store.*not representable" "$OUT/11_import.log" \
  && res PASS "window metric ordered by an aggregate left out with a warning" || res FAIL "brand_rank_in_store handling"
batch "$OUT/12_create.json" -f "$OUT/11_tpcds_sv.sql" && res PASS "create tpcds_sv" || res FAIL "create tpcds_sv (see 12_create.json)"

$PY "$HERE/../flights/run_queries.py" --cz-cli "cz-cli -p $PROFILE" --schema $SCHEMA --queries "$OUT/queries.json" --out "$OUT" \
  2>&1 | tee -a "$SUMMARY"

$PY "$S/sv_dump.py" --cz-cli "cz-cli -p $PROFILE" --view $SCHEMA.tpcds_sv -o "$OUT/20_dump.json" > "$OUT/20_dump.log" 2>&1 \
  && res PASS "dump tpcds_sv" || res FAIL "dump (see 20_dump.log)"
$PY "$S/sv_to_ossie.py" "$OUT/20_dump.json" -o "$OUT/21_export.yaml" > "$OUT/21_export.log" 2>&1 && res PASS "export" || res FAIL "export (see 21_export.log)"
$PY "$S/validate_ossie.py" "$OUT/21_export.yaml" > "$OUT/22_validate.log" 2>&1 && res PASS "exported model validates" || res FAIL "exported model validation"
# the source file names tpcds.public.*; the view uses the mapped schema, so sources differ by design
$PY "$S/ossie_diff.py" "$MODEL" "$OUT/21_export.yaml" --ignore source > "$OUT/23_diff.txt" 2>&1 \
  && res PASS "export equals the source model (helper metrics hidden, original expressions restored)" \
  || res FAIL "export differs (see 23_diff.txt)"
log "done - results in $OUT"
