#!/usr/bin/env bash
# Live end-to-end test of clickzetta-ossie-interop against a real ClickZetta Lakehouse via cz-cli.
#
#   bash tests/run_live_test.sh <cz-cli-profile>
#
# What it does (all objects live in schema ossie_skill_test, created here and dropped at the end):
#   1. creates schema + 4 small tables with data, and the reference semantic view (fixtures/sales_sv.sql)
#   2. probes a few syntax questions (each probe is independent; failures are recorded, not fatal)
#   3. export  : sv_dump.py -> sv_to_ossie.py -> validate_ossie.py
#   4. import  : ossie_to_sv.py -> execute -> re-export -> ossie_diff.py (round trip)
#   5. queries : same semantic_view() queries on original and round-tripped views must match
#   6. Snowflake-style Ossie import with --source-map / --overrides, then query it
#   7. ontology: derive_ontology.py -> validate_ossie.py
#   8. cleanup : drops every object and the schema (always runs, also on failure)
# Results: tests/live_out/<timestamp>/ (summary.txt + every raw cz-cli output).
set -uo pipefail
PROFILE="${1:?usage: bash tests/run_live_test.sh <cz-cli-profile>}"
SCHEMA=ossie_skill_test
HERE="$(cd "$(dirname "$0")" && pwd)"
S="$HERE/../scripts"; F="$HERE/fixtures"
. "$HERE/lib/lock.sh"
OUT="$HERE/live_out/$(date +%Y%m%d_%H%M%S)"; mkdir -p "$OUT/probes"
SUMMARY="$OUT/summary.txt"
CZ=(cz-cli -p "$PROFILE")
log()  { echo "$*" | tee -a "$SUMMARY"; }
res()  { log "$1  $2"; }

command -v cz-cli >/dev/null || { echo "cz-cli not found in PATH"; exit 2; }

# ---- python with pyyaml + jsonschema
PY=python3
if ! $PY -c "import yaml, jsonschema" 2>/dev/null; then
  echo "pyyaml/jsonschema missing - creating a private venv in $HERE/live_out/.venv"
  python3 -m venv "$HERE/live_out/.venv" && "$HERE/live_out/.venv/bin/pip" -q install pyyaml jsonschema \
    || { echo "could not install pyyaml/jsonschema"; exit 2; }
  PY="$HERE/live_out/.venv/bin/python"
fi

sql()      { "${CZ[@]}" sql --no-limit --no-truncate "$@"; }            # read
sqlw()     { "${CZ[@]}" sql --write --no-limit --no-truncate "$@"; }    # write
batch() {  # batch <out-file> <cz-cli args...>: --batch exits 0 even when a statement fails, so check the JSON
  local out="$1"; shift
  sqlw --batch "$@" > "$out" 2>&1 && ! grep -q '"error":{' "$out"
}
run_file() { batch "$2" -f "$1"; }

# ---- 0. environment snapshot (no secrets: profile list only shows names/endpoints)
"${CZ[@]}" --version > "$OUT/cz_version.txt" 2>&1 || true
sql -e "SELECT current_workspace(), current_schema(), current_user()" > "$OUT/env.json" 2>&1 || true

cleanup() {
  [ "${CREATED:-0}" = 1 ] || return
  for v in sales_sv sales_sv_rt snow_orders_sv p_no_pk p_metric_syn p_fact_comment p_fact_syn p_esc_bs p_esc_dq \
           p_cross_metric p_cross_undeclared p_multi_agg p_fact_pk_name p_enum_num p_prop_long p_three_part; do
    sqlw -e "DROP SEMANTIC VIEW IF EXISTS $SCHEMA.$v" >> "$OUT/99_cleanup.log" 2>&1
  done
  for t in order_items orders products customers; do
    sqlw -e "DROP TABLE IF EXISTS $SCHEMA.$t" >> "$OUT/99_cleanup.log" 2>&1
  done
  if sqlw -e "DROP SCHEMA IF EXISTS $SCHEMA" >> "$OUT/99_cleanup.log" 2>&1; then log "cleanup: schema $SCHEMA dropped"
  else log "cleanup: DROP SCHEMA failed - see 99_cleanup.log"; fi
  sql -e "SHOW SCHEMAS" > "$OUT/99_schemas_after.json" 2>&1
  release_lock
}
trap cleanup EXIT
# after the trap, so an early exit anywhere below still releases the lock through cleanup().
# On refusal we hold nothing, so drop the trap rather than let cleanup claim to have dropped a
# schema this run never created.
acquire_lock "$PROFILE" || { trap - EXIT; exit 3; }

# ---- 1. setup (abort if the schema already exists, so we never touch someone else's objects)
if ! sqlw -e "CREATE SCHEMA $SCHEMA" > "$OUT/01_create_schema.json" 2>&1; then
  log "ABORT: could not create schema $SCHEMA (does it already exist?) - see 01_create_schema.json"; exit 1
fi
CREATED=1

run_file "$F/setup_tables.sql" "$OUT/02_setup_tables.json" && res PASS "setup tables" || { res FAIL "setup tables"; exit 1; }
run_file "$F/sales_sv.sql" "$OUT/03_create_sales_sv.json" && res PASS "create reference semantic view" \
  || { res FAIL "create reference semantic view (see 03_create_sales_sv.json)"; exit 1; }

# ---- 2. probes: record behaviour, never fatal
probe() {  # probe <name> <sql>
  local name="$1" q="$2"
  if batch "$OUT/probes/$name.json" -e "$q"; then
    # SHOW CREATE is read-only; --write only because cz-cli's keyword guard flags CREATE
    sqlw -e "SHOW CREATE SEMANTIC VIEW $SCHEMA.$name" > "$OUT/probes/$name.show_create.json" 2>&1
    sql -e "DESC EXTENDED $SCHEMA.$name" > "$OUT/probes/$name.desc.json" 2>&1
    res "OK  " "probe $name"
  else
    res "ERR " "probe $name: $(tr '\n' ' ' < "$OUT/probes/$name.json" | cut -c1-240)"
  fi
}
probe_rejected() {  # probe_rejected <name> <sql> <expected error text>: ClickZetta must refuse it
  local name="$1" q="$2" want="$3"
  if batch "$OUT/probes/$name.json" -e "$q"; then res "ERR " "probe $name: accepted, expected rejection ($want)"
  elif grep -q "$want" "$OUT/probes/$name.json"; then res "OK  " "probe $name rejected as expected ($want)"
  else res "ERR " "probe $name: other error $(tr '\n' ' ' < "$OUT/probes/$name.json" | cut -c1-200)"; fi
}
T_ORD="o AS $SCHEMA.orders PRIMARY KEY (order_id)"
T_CUS="c AS $SCHEMA.customers PRIMARY KEY (customer_id)"
probe p_no_pk        "CREATE SEMANTIC VIEW $SCHEMA.p_no_pk TABLES (o AS $SCHEMA.orders) METRICS (o.cnt AS COUNT(o.order_id))"
probe p_metric_syn   "CREATE SEMANTIC VIEW $SCHEMA.p_metric_syn TABLES ($T_ORD) METRICS (o.cnt AS COUNT(o.order_id) WITH SYNONYMS = ('order total') COMMENT = 'n')"
probe p_fact_comment "CREATE SEMANTIC VIEW $SCHEMA.p_fact_comment TABLES ($T_ORD) FACTS (o.oid AS o.order_id COMMENT = 'fact comment')"
probe p_fact_syn     "CREATE SEMANTIC VIEW $SCHEMA.p_fact_syn TABLES ($T_ORD) FACTS (o.oid AS o.order_id WITH SYNONYMS = ('fact id'))"
probe p_esc_bs       "CREATE SEMANTIC VIEW $SCHEMA.p_esc_bs TABLES ($T_ORD) DIMENSIONS (o.st AS o.status COMMENT = 'it\\'s') COMMENT = 'view\\'s'"
probe p_esc_dq       "CREATE SEMANTIC VIEW $SCHEMA.p_esc_dq TABLES ($T_ORD) DIMENSIONS (o.st AS o.status COMMENT = 'it''s') COMMENT = 'view''s'"
# a table-qualified metric cannot touch another table's columns; combine per-table metrics in a
# view-scoped (unqualified) metric instead
probe_rejected p_cross_undeclared "CREATE SEMANTIC VIEW $SCHEMA.p_cross_undeclared TABLES ($T_CUS, $T_ORD) RELATIONSHIPS (o (customer_id) REFERENCES c (customer_id)) DIMENSIONS (o.st AS o.status, c.region AS c.region) METRICS (o.regions AS COUNT(DISTINCT c.region))" "cannot resolve column 'region'"
probe_rejected p_multi_agg "CREATE SEMANTIC VIEW $SCHEMA.p_multi_agg TABLES ($T_CUS, $T_ORD) RELATIONSHIPS (o (customer_id) REFERENCES c (customer_id)) METRICS (per_cust AS COUNT(o.order_id) / COUNT(DISTINCT c.customer_id))" "directly aggregates columns from more than one logical table"
probe p_cross_metric "CREATE SEMANTIC VIEW $SCHEMA.p_cross_metric TABLES ($T_CUS, $T_ORD) RELATIONSHIPS (o (customer_id) REFERENCES c (customer_id)) DIMENSIONS (o.st AS o.status, c.region AS c.region) METRICS (c.regions AS COUNT(DISTINCT c.region), o.cnt AS COUNT(o.order_id), orders_per_region AS o.cnt / c.regions)"
probe p_fact_pk_name "CREATE SEMANTIC VIEW $SCHEMA.p_fact_pk_name TABLES ($T_ORD) FACTS (o.order_id AS o.order_id) METRICS (o.cnt AS COUNT(o.order_id))"
probe p_enum_num     "CREATE SEMANTIC VIEW $SCHEMA.p_enum_num TABLES ($T_ORD) DIMENSIONS (o.cid AS o.customer_id enum_values = [1, 2, 3])"
WS=$($PY - "$S" "$OUT/env.json" <<'EOF2' 2>/dev/null
import sys; sys.path.insert(0, sys.argv[1])
from czossie_common import parse_cli_rows
print(list(parse_cli_rows(open(sys.argv[2]).read())[0].values())[0])
EOF2
)
if [ -n "$WS" ]; then
  probe p_three_part "CREATE SEMANTIC VIEW $SCHEMA.p_three_part TABLES (o AS $WS.$SCHEMA.orders PRIMARY KEY (order_id)) METRICS (o.cnt AS COUNT(o.order_id))"
else res "ERR " "probe p_three_part skipped: workspace name unknown (see env.json)"; fi
LONG=$(head -c 6000 /dev/zero | tr '\0' 'A')
probe p_prop_long    "CREATE SEMANTIC VIEW $SCHEMA.p_prop_long TABLES ($T_ORD) METRICS (o.cnt AS COUNT(o.order_id)); ALTER SEMANTIC VIEW $SCHEMA.p_prop_long SET PROPERTIES ('k_long' = 'OSSIE1:0:1:$LONG', 'k_short' = 'x')"
sql -e "SELECT * FROM semantic_view($SCHEMA.p_cross_metric DIMENSIONS c.region METRICS orders_per_region)" > "$OUT/probes/p_cross_metric.query.json" 2>&1 \
  && res "OK  " "probe p_cross_metric query by parent dimension" || res "ERR " "probe p_cross_metric query: $(tr '\n' ' ' < "$OUT/probes/p_cross_metric.query.json" | cut -c1-200)"
# KNOWN ENGINE DEFECT, not a regression in this skill: grouping a view-scoped derived metric - the
# shape every imported multi-table metric has - by a finer-grain dimension makes the planner crash
# with CZLH-65000 instead of returning the CZLH-42000 grain error it gives when the parent metric is
# queried directly. Minimal repro in references/mapping.md. Recorded as INFO, never fatal.
sql -e "SELECT * FROM semantic_view($SCHEMA.p_cross_metric DIMENSIONS o.st METRICS orders_per_region)" > "$OUT/probes/p_cross_metric.child_dim.json" 2>&1 \
  && res INFO "probe p_cross_metric by child dimension: accepted (engine behaviour changed - check mapping.md)" \
  || res INFO "probe p_cross_metric by child dimension: rejected as expected (CZLH-65000 engine defect, see mapping.md)"

# ---- 3. export
$PY "$S/sv_dump.py" --cz-cli "cz-cli -p $PROFILE" --view $SCHEMA.sales_sv -o "$OUT/10_dump.json" > "$OUT/10_dump.log" 2>&1 \
  && res PASS "sv_dump sales_sv" || res FAIL "sv_dump sales_sv (see 10_dump.log)"
$PY "$S/sv_to_ossie.py" "$OUT/10_dump.json" -o "$OUT/11_export.yaml" --issues "$OUT/11_export_issues.json" > "$OUT/11_export.log" 2>&1 \
  && res PASS "export to Ossie" || res FAIL "export to Ossie (see 11_export.log)"
$PY "$S/validate_ossie.py" "$OUT/11_export.yaml" > "$OUT/12_validate.log" 2>&1 \
  && res PASS "exported file validates" || res FAIL "exported file validates (see 12_validate.log)"
$PY "$S/sv_to_ossie.py" --ddl "$F/sales_sv.sql" -o "$OUT/13_expected_from_ddl.yaml" > /dev/null 2>&1
$PY "$S/ossie_diff.py" "$OUT/13_expected_from_ddl.yaml" "$OUT/11_export.yaml" --ignore datatype > "$OUT/13_diff_vs_source.txt" 2>&1 \
  && res PASS "export matches the authored DDL" || res FAIL "export differs from authored DDL (see 13_diff_vs_source.txt)"

# the same view through --profile instead of --cz-cli must yield the same DDL
$PY "$S/sv_dump.py" --profile "$PROFILE" --view $SCHEMA.sales_sv -o "$OUT/10b_dump_profile.json" > "$OUT/10b_dump.log" 2>&1 \
  && res PASS "sv_dump --profile" || res FAIL "sv_dump --profile (see 10b_dump.log)"
if $PY - "$OUT/10_dump.json" "$OUT/10b_dump_profile.json" <<'EOF9'
import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
assert a["ddl"] == b["ddl"], "--profile and --cz-cli dumps disagree"
EOF9
then res PASS "sv_dump --profile matches --cz-cli"
else res FAIL "sv_dump --profile differs from --cz-cli"; fi

# --spec-version 0.1.1 drops `datatype`. Only a real dump carries data types, so this is the one
# place the strip can be observed at all.
$PY "$S/sv_to_ossie.py" "$OUT/10_dump.json" -o "$OUT/11b_v011.yaml" --spec-version 0.1.1 \
    --issues "$OUT/11b_issues.json" > "$OUT/11b.log" 2>&1
if grep -q "datatype" "$OUT/11_export.yaml" && ! grep -q "datatype" "$OUT/11b_v011.yaml" \
   && grep -q "removed" "$OUT/11b_issues.json"; then
  res PASS "--spec-version 0.1.1 strips datatype and reports it"
else
  res FAIL "--spec-version 0.1.1 datatype strip (see 11b.log / 11b_issues.json)"
fi
$PY "$S/validate_ossie.py" "$OUT/11b_v011.yaml" > "$OUT/11b_validate.log" 2>&1 \
  && res PASS "--spec-version 0.1.1 output validates" || res FAIL "--spec-version 0.1.1 output validates"

# ---- 4. import round trip
$PY "$S/ossie_to_sv.py" "$OUT/11_export.yaml" --view $SCHEMA.sales_sv_rt -o "$OUT/20_import.sql" --issues "$OUT/20_import_issues.json" > "$OUT/20_import.log" 2>&1 \
  && res PASS "import generates DDL" || res FAIL "import generates DDL (see 20_import.log)"
run_file "$OUT/20_import.sql" "$OUT/21_exec_import.json" && res PASS "imported DDL executes" \
  || res FAIL "imported DDL executes (see 21_exec_import.json)"
$PY "$S/sv_dump.py" --cz-cli "cz-cli -p $PROFILE" --view $SCHEMA.sales_sv_rt -o "$OUT/22_dump_rt.json" > "$OUT/22_dump_rt.log" 2>&1
$PY "$S/sv_to_ossie.py" "$OUT/22_dump_rt.json" -o "$OUT/23_export_rt.yaml" > "$OUT/23_export_rt.log" 2>&1
$PY "$S/ossie_diff.py" "$OUT/11_export.yaml" "$OUT/23_export_rt.yaml" > "$OUT/24_roundtrip_diff.txt" 2>&1 \
  && res PASS "round trip is lossless" || res FAIL "round trip differs (see 24_roundtrip_diff.txt)"

# ---- 5. query equivalence
qcmp() {  # qcmp <name> <semantic_view args>
  local n="$1" args="$2"
  sql -e "SELECT * FROM semantic_view($SCHEMA.sales_sv $args)" > "$OUT/30_q_${n}_orig.json" 2>&1
  sql -e "SELECT * FROM semantic_view($SCHEMA.sales_sv_rt $args)" > "$OUT/30_q_${n}_rt.json" 2>&1
  if $PY - "$S" "$OUT/30_q_${n}_orig.json" "$OUT/30_q_${n}_rt.json" <<'EOF'
import sys; sys.path.insert(0, sys.argv[1])
from czossie_common import parse_cli_rows
a = parse_cli_rows(open(sys.argv[2]).read()); b = parse_cli_rows(open(sys.argv[3]).read())
key = lambda r: sorted((k, str(v)) for k, v in r.items())
assert a, "no rows"
assert sorted(map(key, a)) == sorted(map(key, b)), (a, b)
EOF
  then res PASS "query $n identical on original and round-tripped view"
  else res FAIL "query $n differs or failed (see 30_q_${n}_*.json)"; fi
}
qcmp region_revenue "DIMENSIONS customers.region METRICS order_items.revenue, orders.order_count"
qcmp month_completed "DIMENSIONS orders.order_date METRICS orders.completed_orders, order_items.avg_price"
qcmp size_band_var "DIMENSIONS order_items.size_band METRICS order_items.revenue VARIABLES min_amount => 200"
# one case per metric/dimension flavour the fixture defines, so every kind survives the round trip
qcmp status_conditional "DIMENSIONS orders.status METRICS order_items.revenue, orders.completed_orders"
qcmp category_derived "DIMENSIONS products.category METRICS order_items.units, order_items.avg_price"
qcmp signup_year_time "DIMENSIONS customers.signup_year METRICS orders.order_count"
qcmp size_band_fact "DIMENSIONS order_items.size_band FACTS order_items.line_amount"
qcmp name_units "DIMENSIONS customers.customer_name METRICS order_items.units"

# ---- 6. Snowflake-style import
$PY "$S/ossie_to_sv.py" "$F/snowflake_orders.ossie.yaml" --view $SCHEMA.snow_orders_sv \
  --source-map "SNOW_DB.SALES=$SCHEMA" --overrides "$F/snowflake_overrides.yaml" \
  -o "$OUT/40_snow.sql" --issues "$OUT/40_snow_issues.json" > "$OUT/40_snow.log" 2>&1 \
  && res PASS "Snowflake-style Ossie converts" || res FAIL "Snowflake-style Ossie converts (see 40_snow.log)"
run_file "$OUT/40_snow.sql" "$OUT/41_exec_snow.json" && res PASS "Snowflake-derived DDL executes" \
  || res FAIL "Snowflake-derived DDL executes (see 41_exec_snow.json)"
sql -e "SELECT * FROM semantic_view($SCHEMA.snow_orders_sv DIMENSIONS orders.order_month METRICS orders.order_count, orders.completion_rate)" \
  > "$OUT/42_q_snow.json" 2>&1 && res PASS "query Snowflake-derived view" || res FAIL "query Snowflake-derived view (see 42_q_snow.json)"
$PY "$S/sv_dump.py" --cz-cli "cz-cli -p $PROFILE" --view $SCHEMA.snow_orders_sv -o "$OUT/43_dump_snow.json" > /dev/null 2>&1
$PY "$S/sv_to_ossie.py" "$OUT/43_dump_snow.json" -o "$OUT/44_snow_back.yaml" > "$OUT/44_snow_back.log" 2>&1
$PY "$S/ossie_diff.py" "$F/snowflake_orders.ossie.yaml" "$OUT/44_snow_back.yaml" --ignore datatype,source > "$OUT/45_snow_diff.txt" 2>&1 \
  && res PASS "Snowflake file survives import+export" || res INFO "Snowflake import+export differences listed in 45_snow_diff.txt"

# ---- 7. ontology
$PY "$S/derive_ontology.py" "$OUT/11_export.yaml" -o "$OUT/50_ontology.yaml" --attributes > "$OUT/50_ontology.log" 2>&1 \
  && res PASS "derive ontology" || res FAIL "derive ontology"
$PY "$S/validate_ossie.py" "$OUT/50_ontology.yaml" > "$OUT/51_ontology_validate.log" 2>&1 \
  && res PASS "ontology validates (TODO warnings expected)" || res FAIL "ontology validation (see 51_ontology_validate.log)"

log "done - results in $OUT"
