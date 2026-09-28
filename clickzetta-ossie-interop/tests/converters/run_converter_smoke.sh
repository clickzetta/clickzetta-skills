#!/usr/bin/env bash
# Smoke test: Ossie files written by other tools (Apache Ossie converters: Databricks, Omni, NVIDIA,
# GoodData, OrionBelt) -> ClickZetta semantic views.
#
#   bash tests/converters/run_converter_smoke.sh <cz-cli-profile> [file.ossie.yaml ...]
#
# Per file: import (sources mapped to the test schema), create empty tables derived from the view,
# create the view, run every public metric and dimension once (must compile), export and diff.
# Everything lives in schema ossie_skill_test (created here; the script stops if it already exists)
# and is dropped at the end. Results: tests/converters/out/<timestamp>/
set -uo pipefail
PROFILE="${1:?usage: bash tests/converters/run_converter_smoke.sh <cz-cli-profile> [files...]}"; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
S="$HERE/../../scripts"
. "$HERE/../lib/lock.sh"
FILES=("$@"); [ ${#FILES[@]} -gt 0 ] || FILES=("$HERE"/../fixtures/converters/*.ossie.yaml)
SCHEMA=ossie_skill_test
OUT="$HERE/out/$(date +%Y%m%d_%H%M%S)"; mkdir -p "$OUT"
SUMMARY="$OUT/summary.txt"
CZ=(cz-cli -p "$PROFILE")
log() { echo "$*" | tee -a "$SUMMARY"; }
res() { log "$1  $2"; }
PY=python3
sql()  { "${CZ[@]}" sql --no-limit --no-truncate "$@"; }
sqlw() { "${CZ[@]}" sql --write --no-limit --no-truncate "$@"; }
batch() {  # batch <out-file> <cz-cli args...>: --batch exits 0 even when a statement fails, so check the JSON
  local out="$1"; shift
  sqlw --batch "$@" > "$out" 2>&1 && ! grep -q '"error":{' "$out"
}
CUR=""
cleanup() {
  [ -n "$CUR" ] && { sqlw -e "DROP SEMANTIC VIEW IF EXISTS $SCHEMA.conv_sv" >> "$OUT/99_cleanup.log" 2>&1
                     sqlw --batch -f "$CUR/drop.sql" >> "$OUT/99_cleanup.log" 2>&1; }
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

for f in "${FILES[@]}"; do
  n=$(basename "$f" .ossie.yaml); D="$OUT/$n"; mkdir -p "$D"
  log "=== $n"
  MAP=(); while read -r m; do MAP+=(--source-map "$m"); done < <($PY "$HERE/gen_empty_tables.py" sourcemap "$f" $SCHEMA)
  # Some real converter outputs cannot become a runnable view without a human deciding a key.
  # orionbelt_obml: 'calendar' has no primary_key and two relationships reach it through different
  # columns (ym, date), so whichever one is inferred as the key makes the other invalid. The
  # importer says so at error level; the fixture is expected to stop there.
  expect_import_error() {
    case "$1" in
      orionbelt_obml) echo "will reject this view" ;;
      *) echo "" ;;
    esac
  }
  want=$(expect_import_error "$n")
  if ! $PY "$S/ossie_to_sv.py" "$f" --view $SCHEMA.conv_sv "${MAP[@]}" -o "$D/import.sql" --issues "$D/issues.json" > "$D/import.log" 2>&1; then
    if [ -n "$want" ] && grep -q "$want" "$D/import.log"; then
      res PASS "$n: import stops on an unresolvable key, DDL still written for inspection"
      continue
    fi
    res FAIL "$n: import reported errors: $(grep ERROR "$D/import.log" | head -2 | cut -c1-220 | tr '\n' ' ')"; continue
  fi
  if [ -n "$want" ]; then
    res FAIL "$n: expected the import to error ('$want') but it succeeded - drop the expectation if that is now correct"; continue
  fi
  res PASS "$n: import ($(grep -c WARNING "$D/import.log") warnings)"
  $PY "$HERE/gen_empty_tables.py" tables "$D/import.sql" "$f" --out "$D" > "$D/gen.log" 2>&1 || { res FAIL "$n: gen tables (see gen.log)"; continue; }
  CUR="$D"
  if ! batch "$D/tables.json" -f "$D/tables.sql"; then res FAIL "$n: create tables (see tables.json)"
  elif ! batch "$D/create.json" -f "$D/import.sql"; then
    res FAIL "$n: create view: $(grep -o '"message":"[^"]*' "$D/create.json" | head -1 | cut -c12-240)"
  else
    res PASS "$n: create view"
    ok=0; bad=0; i=0
    while read -r q; do
      i=$((i+1))
      if sql -e "SELECT * FROM semantic_view($SCHEMA.conv_sv $q)" > "$D/q_$i.json" 2>&1; then ok=$((ok+1))
      else bad=$((bad+1)); log "      query failed: $q -> $(grep -o '"message":"[^"]*' "$D/q_$i.json" | head -1 | cut -c12-200)"; fi
    done < "$D/queries.txt"
    [ $bad -eq 0 ] && res PASS "$n: $ok queries compile" || res FAIL "$n: $bad of $((ok+bad)) queries failed"
    $PY "$S/sv_dump.py" --cz-cli "cz-cli -p $PROFILE" --view $SCHEMA.conv_sv -o "$D/dump.json" > "$D/dump.log" 2>&1 \
      && $PY "$S/sv_to_ossie.py" "$D/dump.json" -o "$D/export.yaml" > "$D/export.log" 2>&1 \
      && $PY "$S/validate_ossie.py" "$D/export.yaml" > "$D/validate.log" 2>&1 \
      && { $PY "$S/ossie_diff.py" "$f" "$D/export.yaml" --ignore source > "$D/diff.txt" 2>&1 \
             && res PASS "$n: export equals the source file" || res INFO "$n: export differences in $n/diff.txt ($(wc -l < "$D/diff.txt" | tr -d ' ') lines)"; } \
      || res FAIL "$n: export (see dump.log / export.log / validate.log)"
  fi
  sqlw -e "DROP SEMANTIC VIEW IF EXISTS $SCHEMA.conv_sv" >> "$D/drop.log" 2>&1
  sqlw --batch -f "$D/drop.sql" >> "$D/drop.log" 2>&1
  CUR=""
done
log "done - results in $OUT"
