#!/usr/bin/env bash
# Offline tests: no database needed. Exercises parse -> export -> import -> re-export -> diff,
# Snowflake-style import, and ontology derivation, using the fixtures in tests/fixtures.
# Usage: bash tests/run_offline_tests.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
S="$HERE/../scripts"
F="$HERE/fixtures"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
PY="${PYTHON:-python3}"
pass=0; fail=0; knowns=0
ok()   { echo "PASS  $*"; pass=$((pass+1)); }
bad()  { echo "FAIL  $*"; fail=$((fail+1)); }

# 1. export from DDL text
$PY "$S/sv_to_ossie.py" --ddl "$F/sales_sv.sql" -o "$OUT/e1.yaml" >/dev/null 2>"$OUT/e1.log" \
  && ok "export sales_sv.sql" || bad "export sales_sv.sql ($(cat "$OUT/e1.log"))"
$PY "$S/validate_ossie.py" "$OUT/e1.yaml" >"$OUT/v1.log" && ok "validate export" || { bad "validate export"; cat "$OUT/v1.log"; }

# 2. import it back and simulate the database read-back (DDL + sidecar in DESC EXTENDED)
$PY "$S/ossie_to_sv.py" "$OUT/e1.yaml" --view ossie_skill_test.sales_sv_rt -o "$OUT/rt.sql" 2>"$OUT/rt.log" \
  && ok "import exported model" || { bad "import exported model"; cat "$OUT/rt.log"; }
$PY - "$OUT/rt.sql" "$OUT/dump_rt.json" <<'EOF'
import json, sys
sql = open(sys.argv[1]).read()
create, _, alter = sql.partition("ALTER SEMANTIC VIEW")
json.dump({"view": "ossie_skill_test.sales_sv_rt", "ddl": create, "raw": {"desc_extended": alter}},
          open(sys.argv[2], "w"))
EOF
$PY "$S/sv_to_ossie.py" "$OUT/dump_rt.json" -o "$OUT/e2.yaml" >/dev/null 2>&1 && ok "re-export" || bad "re-export"
if $PY "$S/ossie_diff.py" "$OUT/e1.yaml" "$OUT/e2.yaml" >"$OUT/diff.log"; then ok "round trip equivalent"
else bad "round trip differs"; cat "$OUT/diff.log"; fi

# 3. Snowflake-style Ossie import
if $PY "$S/ossie_to_sv.py" "$F/snowflake_orders.ossie.yaml" --view ossie_skill_test.snow_orders_sv \
     --source-map "SNOW_DB.SALES=ossie_skill_test" -o "$OUT/snow.sql" --issues "$OUT/snow_issues.json" 2>/dev/null; then
  ok "snowflake import (no overrides)"
else bad "snowflake import (no overrides)"; fi
grep -q "IFF(" "$OUT/snow.sql" && ok "without overrides SNOWFLAKE expression kept verbatim" || bad "IFF expected"
$PY - "$OUT/snow_issues.json" <<'EOF' && ok "snowflake issues reported" || bad "snowflake issues missing"
import json, sys
msgs = " ".join(i["message"] for i in json.load(open(sys.argv[1])))
assert "SNOWFLAKE expression verbatim" in msgs and "custom_instructions" in msgs, msgs
EOF
$PY "$S/ossie_to_sv.py" "$F/snowflake_orders.ossie.yaml" --view ossie_skill_test.snow_orders_sv \
  --source-map "SNOW_DB.SALES=ossie_skill_test" --overrides "$F/snowflake_overrides.yaml" -o "$OUT/snow2.sql" 2>/dev/null
grep -q "IF(orders.status" "$OUT/snow2.sql" && ! grep -q "IFF(" "$OUT/snow2.sql" \
  && grep -q "ossie_skill_test.customers" "$OUT/snow2.sql" && grep -q "PRIVATE orders.order_id" "$OUT/snow2.sql" \
  && grep -q "enum_values = \['EAST', 'WEST'\]" "$OUT/snow2.sql" && ok "overrides / source-map / private / enum applied" \
  || { bad "overrides"; cat "$OUT/snow2.sql"; }

# 4. ontology derivation
$PY "$S/derive_ontology.py" "$OUT/e1.yaml" -o "$OUT/onto.yaml" --attributes >/dev/null && ok "derive ontology" || bad "derive ontology"
$PY "$S/validate_ossie.py" "$OUT/onto.yaml" >"$OUT/vo.log" || true
grep -q "^VALID" "$OUT/vo.log" && ok "ontology schema + references valid (TODO warnings expected)" || { bad "ontology invalid"; cat "$OUT/vo.log"; }
grep -q "TODO" "$OUT/vo.log" && ok "TODO verbalizations flagged" || bad "TODO not flagged"

# 5. apache/ossie examples/flights.yaml: keys/relationships/roles only exist in the ontology layer
FL="$F/flights.ossie.yaml"
$PY "$S/ossie_to_sv.py" "$FL" --view s.v -o "$OUT/fl_raw.sql" 2>"$OUT/fl_raw.log" >/dev/null \
  && ! grep -q "^RELATIONSHIPS" "$OUT/fl_raw.sql" && grep -q "no relationships" "$OUT/fl_raw.log" \
  && ok "raw flights import: isolated tables, warns to enrich from the ontology" || bad "raw flights import"
$PY "$S/enrich_from_ontology.py" "$FL" -o "$OUT/fl_core.yaml" --review "$HERE/flights/review.yaml" --quiet >/dev/null 2>&1 \
  && ok "flights enriched from ontology" || bad "flights enrich"
$PY - "$OUT/fl_core.yaml" <<'EOF2' && ok "flights keys / relationships / roles / metrics inferred" || bad "flights inference"
import sys, yaml
m = yaml.safe_load(open(sys.argv[1]))["semantic_model"][0]
ds = {d["name"]: d for d in m["datasets"]}
assert ds["RUNWAY"]["primary_key"] == ["designator", "airport_code"], ds["RUNWAY"]["primary_key"]
assert all(ds[d]["primary_key"] for d in ds)
rels = {r["name"]: r for r in m["relationships"]}
assert rels["flight_route"]["from_columns"] == ["route_id"] and rels["route_departure"]["from_columns"] == ["orig_airport_code"]
f = {x["name"]: x for x in ds["FLIGHT"]["fields"]}
assert "dimension" not in f["dep_delay"] and f["date"]["dimension"] == {"is_time": True} and "dimension" in f["cancel_code"]
assert {x["name"] for x in m["metrics"]} >= {"avg_departure_delay", "avg_arrival_delay", "flight_count"}
EOF2
$PY "$S/ossie_to_sv.py" "$OUT/fl_core.yaml" --view ossie_flights_test.flights_sv --source-map "DATABASE.SCHEMA=ossie_flights_test" \
  -o "$OUT/fl.sql" >/dev/null 2>&1 && grep -q 'FLIGHT.`date` AS FLIGHT.`date`' "$OUT/fl.sql" \
  && grep -q 'ROUTE.distance AS ROUTE.distance' "$OUT/fl.sql" && grep -q 'route_departure AS ROUTE (orig_airport_code) REFERENCES AIRPORT (code)' "$OUT/fl.sql" \
  && grep -q 'route_destination AS ROUTE (dest_airport_code) REFERENCES AIRPORT (code)' "$OUT/fl.sql" \
  && ok "flights DDL generated (reserved words quoted, columns qualified, named role-playing relationships)" || bad "flights DDL"
$PY - "$OUT/fl.sql" "$OUT/fl_dump.json" <<'EOF2'
import json, sys
create, _, alter = open(sys.argv[1]).read().partition("ALTER SEMANTIC VIEW")
json.dump({"view": "ossie_flights_test.flights_sv", "ddl": create, "raw": {"desc_extended": alter}}, open(sys.argv[2], "w"))
EOF2
$PY "$S/sv_to_ossie.py" "$OUT/fl_dump.json" -o "$OUT/fl_back.yaml" >/dev/null 2>&1
$PY "$S/ossie_diff.py" "$OUT/fl_core.yaml" "$OUT/fl_back.yaml" >/dev/null && ok "flights round trip equivalent" || bad "flights round trip"

# 6. apache/ossie tpcds example: multi-table metrics, window metric ranked by an aggregate
$PY "$S/ossie_to_sv.py" "$F/tpcds.ossie.yaml" --view ossie_skill_test.tpcds_sv --source-map "tpcds.public=ossie_skill_test" \
  -o "$OUT/tpcds.sql" 2>"$OUT/tpcds.log" >/dev/null
grep -q "^    customer_lifetime_value AS store_sales.customer_lifetime_value__store_sales_1 / customer.customer_lifetime_value__customer_2" "$OUT/tpcds.sql" \
  && grep -q "PRIVATE customer.customer_lifetime_value__customer_2 AS COUNT(DISTINCT customer.c_customer_sk)" "$OUT/tpcds.sql" \
  && ok "tpcds multi-table metric split into PRIVATE helpers + view-scoped metric" || bad "tpcds metric split"
! grep -q "brand_rank_in_store AS" "$OUT/tpcds.sql" && grep -q "brand_rank_in_store.*not representable" "$OUT/tpcds.log" \
  && ok "tpcds window metric ordered by an aggregate left out" || bad "tpcds window metric"
# assert the WHOLE window expression, frame clause included: a bare-column qualification pass
# that swallows the ROW keyword produces `CURRENT store_sales.ROW`, which ClickZetta rejects with
# `expected.keyword, ROW, store_sales` at CREATE time. Grepping only the ORDER BY prefix misses it.
grep -q "store_sales.cumulative_sales AS SUM(SUM(store_sales.ss_ext_sales_price)) OVER (ORDER BY date_dim.d_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)" "$OUT/tpcds.sql" \
  && ! grep -q "CURRENT store_sales.ROW" "$OUT/tpcds.sql" \
  && ok "tpcds window metric keeps its frame clause (ROW stays a keyword)" || bad "tpcds cumulative_sales frame clause"
$PY - "$OUT/tpcds.sql" "$OUT/tpcds_dump.json" <<'EOF2'
import json, sys
create, _, alter = open(sys.argv[1]).read().partition("ALTER SEMANTIC VIEW")
json.dump({"view": "ossie_skill_test.tpcds_sv", "ddl": create, "raw": {"desc_extended": alter}}, open(sys.argv[2], "w"))
EOF2
$PY "$S/sv_to_ossie.py" "$OUT/tpcds_dump.json" -o "$OUT/tpcds_back.yaml" >/dev/null 2>&1
$PY "$S/ossie_diff.py" "$F/tpcds.ossie.yaml" "$OUT/tpcds_back.yaml" --ignore source >/dev/null \
  && ok "tpcds round trip equivalent (helpers hidden, skipped metric restored)" || bad "tpcds round trip"

# 7. converter outputs: bare columns (Databricks style) and keys inferred from relationships
$PY "$S/ossie_to_sv.py" "$F/converters/databricks_fixtureA.ossie.yaml" --view s.v -o "$OUT/dbx.sql" >/dev/null 2>&1
grep -q "orders.total_revenue AS SUM(orders.o_totalprice)" "$OUT/dbx.sql" && grep -q "orders.order_count AS COUNT(\*)" "$OUT/dbx.sql" \
  && ok "bare metric columns assigned to the fact table" || bad "bare metric columns"
$PY "$S/ossie_to_sv.py" "$F/converters/gooddata_tpcds.ossie.yaml" --view s.v -o "$OUT/gd.sql" 2>"$OUT/gd.log" >/dev/null
# GoodData's date_dim is a virtual date dimension (no fields, no key); the relationship references
# ss_sold_date_sk on it. The key is taken from to_columns with a warning.
grep -A1 "date_dim AS" "$OUT/gd.sql" | grep -q "PRIMARY KEY (ss_sold_date_sk)" && grep -q "used as PRIMARY KEY" "$OUT/gd.log" \
  && ok "referenced table without key gets the relationship's to_columns" || bad "inferred key"

# 8. CLI flag matrix. Every option of every script is exercised here or in the live test;
#    before this section 11 of 24 documented flags were never run by any test.
MM="$F/multimodel_dialects.ossie.yaml"
SRC="--source-map FLAG_DB.PUBLIC=ossie_skill_test"

# --dialect: relabels every emitted expression
$PY "$S/sv_to_ossie.py" --ddl "$F/sales_sv.sql" -o "$OUT/dia.yaml" --dialect CLICKZETTA >/dev/null 2>&1 || true
grep -q -- "- dialect: CLICKZETTA" "$OUT/dia.yaml" && ! grep -q -- "- dialect: ANSI_SQL" "$OUT/dia.yaml" \
  && ok "--dialect relabels expressions" || bad "--dialect"

# --spec-version 0.1.1: the header changes here; the datatype strip is asserted in the live test,
# where dumps actually carry data types
$PY "$S/sv_to_ossie.py" --ddl "$F/sales_sv.sql" -o "$OUT/v011.yaml" --spec-version 0.1.1 >/dev/null 2>&1 || true
head -1 "$OUT/v011.yaml" | grep -q "0.1.1" && ok "--spec-version 0.1.1 sets the header" || bad "--spec-version header"
$PY "$S/validate_ossie.py" "$OUT/v011.yaml" >/dev/null 2>&1 && ok "--spec-version 0.1.1 output validates" || bad "--spec-version output"

# --model: a file with several models must not be guessed at
$PY "$S/ossie_to_sv.py" "$MM" --view ossie_skill_test.mm -o "$OUT/mm_none.sql" >"$OUT/mm_none.log" 2>&1 \
  && bad "--model: multi-model file accepted without --model" \
  || { grep -q "several semantic models" "$OUT/mm_none.log" && grep -q "FLAG_SECONDARY" "$OUT/mm_none.log" \
       && ok "--model: multi-model file refuses to guess" || bad "--model refusal message"; }
$PY "$S/ossie_to_sv.py" "$MM" --model FLAG_SECONDARY --view ossie_skill_test.mm $SRC -o "$OUT/mm2.sql" >/dev/null 2>&1 \
  && grep -q "other AS ossie_skill_test.other" "$OUT/mm2.sql" && grep -q "other_count" "$OUT/mm2.sql" \
  && ok "--model selects the named model" || bad "--model selection"
$PY "$S/ossie_to_sv.py" "$MM" --model NOPE --view ossie_skill_test.mm $SRC -o "$OUT/mmbad.sql" >"$OUT/mmbad.log" 2>&1 \
  && bad "--model: unknown name accepted" \
  || { grep -q "not found" "$OUT/mmbad.log" && ok "--model: unknown name rejected" || bad "--model unknown-name message"; }

# --prefer-dialect: chooses which dialect's expression is emitted
$PY "$S/ossie_to_sv.py" "$MM" --model FLAG_PRIMARY --view ossie_skill_test.mm $SRC -o "$OUT/pd_ansi.sql" >/dev/null 2>&1 || true
grep -q "event_day AS CAST(events.ts AS DATE)" "$OUT/pd_ansi.sql" && ok "--prefer-dialect default prefers ANSI_SQL" || bad "--prefer-dialect default"
$PY "$S/ossie_to_sv.py" "$MM" --model FLAG_PRIMARY --view ossie_skill_test.mm $SRC \
    --prefer-dialect SNOWFLAKE,ANSI_SQL -o "$OUT/pd_snow.sql" --issues "$OUT/pd_snow_issues.json" >/dev/null 2>&1 || true
grep -q "event_day AS TO_DATE(events.ts)" "$OUT/pd_snow.sql" && $PY - "$OUT/pd_snow_issues.json" <<'EOF3' \
  && ok "--prefer-dialect SNOWFLAKE picks it and reports the verbatim use" || bad "--prefer-dialect SNOWFLAKE"
import json, sys
msgs = " ".join(i["message"] for i in json.load(open(sys.argv[1])))
assert "SNOWFLAKE expression verbatim" in msgs, msgs
EOF3
$PY "$S/ossie_to_sv.py" "$MM" --model FLAG_PRIMARY --view ossie_skill_test.mm $SRC \
    --prefer-dialect DATABRICKS -o "$OUT/pd_dbx.sql" >/dev/null 2>&1 || true
grep -q "event_day AS to_date(events.ts)" "$OUT/pd_dbx.sql" && ok "--prefer-dialect DATABRICKS picks it" || bad "--prefer-dialect DATABRICKS"

# --no-sidecar: the metadata-preserving ALTER is not emitted
for sc in on off; do
  extra=""; [ "$sc" = off ] && extra="--no-sidecar"
  $PY "$S/ossie_to_sv.py" "$F/snowflake_orders.ossie.yaml" --view ossie_skill_test.snow_orders_sv \
      --source-map "SNOW_DB.SALES=ossie_skill_test" --overrides "$F/snowflake_overrides.yaml" $extra \
      -o "$OUT/sc_$sc.sql" >/dev/null 2>&1 || true
done
grep -q "^ALTER SEMANTIC VIEW" "$OUT/sc_on.sql" && ! grep -q "^ALTER SEMANTIC VIEW" "$OUT/sc_off.sql" \
  && ok "--no-sidecar suppresses the sidecar ALTER" || bad "--no-sidecar"

# 9. every converter fixture (only 2 of 8 were exercised before). Each must import, produce the
#    characteristic DDL, and re-export into a file that still validates.
conv() {  # conv <file> <expected-grep> <label> [expected-error-substring]
  local rc=0
  $PY "$S/ossie_to_sv.py" "$F/converters/$1" --view ossie_skill_test.conv_sv \
      -o "$OUT/conv.sql" --issues "$OUT/conv_issues.json" >"$OUT/conv.log" 2>&1 || rc=$?
  if [ -n "${4:-}" ]; then
    # fixture cannot become a runnable view without a human deciding a key, so the import must stop
    # at error level rather than hand over DDL that ClickZetta is certain to reject
    [ "$rc" = 1 ] && grep -q "$4" "$OUT/conv.log" \
      || { bad "converter $3: expected an error mentioning '$4' (exit $rc)"; return; }
  elif [ "$rc" != 0 ]; then
    bad "converter $3: import failed ($(head -1 "$OUT/conv.log"))"; return
  fi
  grep -q "$2" "$OUT/conv.sql" || { bad "converter $3: missing '$2'"; return; }
  $PY - "$OUT/conv.sql" "$OUT/conv_dump.json" <<'EOF3'
import json, sys
create, _, alter = open(sys.argv[1], encoding="utf-8").read().partition("ALTER SEMANTIC VIEW")
json.dump({"view": "ossie_skill_test.conv_sv", "ddl": create, "raw": {"desc_extended": alter}},
          open(sys.argv[2], "w"))
EOF3
  $PY "$S/sv_to_ossie.py" "$OUT/conv_dump.json" -o "$OUT/conv_back.yaml" >/dev/null 2>&1 \
    && $PY "$S/validate_ossie.py" "$OUT/conv_back.yaml" >/dev/null 2>&1 \
    && ok "converter $3 (imports, exports, re-validates)" || bad "converter $3 round trip"
}
conv databricks_fixtureA.ossie.yaml "orders_to_customer AS orders (o_custkey) REFERENCES customer (c_custkey)" "databricks_fixtureA"
conv databricks_fixtureB.ossie.yaml "PRIMARY KEY (o_orderkey)" "databricks_fixtureB (key from unique key)"
conv databricks_tpcds.ossie.yaml   "PRIMARY KEY (c_customer_sk)" "databricks_tpcds"
conv gooddata_tpcds.ossie.yaml     "PRIMARY KEY (ss_sold_date_sk)" "gooddata_tpcds (key from to_columns)"
conv nvidia_sales.ossie.yaml       "orders_to_customers AS orders (customer_id) REFERENCES customers (customer_id)" "nvidia_sales"
conv omni_fixtureA.ossie.yaml      "orders_to_customer AS orders (o_custkey) REFERENCES customer (c_custkey)" "omni_fixtureA"
conv orionbelt_obml.ossie.yaml     "PRIMARY KEY (ym)" "orionbelt_obml (key from relationships, keyless calendar)" "will reject this view"
conv orionbelt_tpcds.ossie.yaml    "PRIMARY KEY (c_customer_sk)" "orionbelt_tpcds"

# 10. error handling and the exit-code contract. Bad input must fail with one clear line and
#     exit 2, never with a Python traceback. Codes are the same across every script:
#       0 = ran, nothing to report   1 = ran and found problems   2 = could not run
#     `known` records a defect without failing the run; the suite currently has none, and the
#     point of this section is to keep it that way.
known() { echo "KNOWN $*"; knowns=$((knowns+1)); }
exits() {  # exits <label> <expected-code> <cmd...>
  local label="$1" want="$2"; shift 2
  local log="$OUT/err_${label// /_}.log"
  rc=0; "$@" >"$log" 2>&1 || rc=$?
  if [ "$rc" != "$want" ]; then
    bad "$label: exit $rc, expected $want - $(head -1 "$log")"; return
  fi
  if grep -q "Traceback (most recent call last)" "$log"; then
    bad "$label: exits $want but with a raw Python traceback"; return
  fi
  # CliError prints "error: ..."; argparse usage errors print "<prog>: error: ...". Both are one line.
  if [ "$want" = 2 ] && ! grep -qE "^error: |: error: " "$log"; then
    bad "$label: exit 2 without an 'error: ...' line"; return
  fi
  ok "$label (exit $rc, one clean line)"
}
printf 'broken: [unclosed\n'                       > "$OUT/bad.yaml"
printf 'version: 0.2.0.dev0\nsemantic_model: []\n' > "$OUT/nomodel.yaml"
printf '{"view":"x.y"}\n'                          > "$OUT/baddump.json"
printf 'not json at all\n'                         > "$OUT/notjson.json"
printf ''                                          > "$OUT/empty.yaml"
printf 'not: an ossie file at all\n'               > "$OUT/notossie.yaml"
# every script in scripts/, not just the six in the main workflow: sv_ddl.py and sv_dump.py were
# missed on the first pass and kept crashing on bad input
exits "sv_ddl on a missing file"          2 $PY "$S/sv_ddl.py" "$OUT/nope.sql"
exits "sv_ddl without an argument"        2 $PY "$S/sv_ddl.py"
exits "sv_dump with a broken --cz-cli"    2 $PY "$S/sv_dump.py" --view t.v --cz-cli /nonexistent/cz-cli -o "$OUT/d.json"
exits "sv_to_ossie on malformed YAML"     2 $PY "$S/sv_to_ossie.py" "$OUT/bad.yaml" -o "$OUT/e.yaml"
# a round-trip check must never call two model-less files equivalent: if an export ever produced an
# empty model, that answer would keep the safety net green
exits "ossie_diff on two model-less files" 2 $PY "$S/ossie_diff.py" "$OUT/nomodel.yaml" "$OUT/notossie.yaml"
exits "ossie_diff on a model-less file"    2 $PY "$S/ossie_diff.py" "$OUT/nomodel.yaml" "$OUT/e1.yaml"
# unreadable or unusable input -> 2
exits "ossie_to_sv on a missing file"     2 $PY "$S/ossie_to_sv.py" "$OUT/nope.yaml" --view t.v -o "$OUT/e.sql"
exits "ossie_to_sv on malformed YAML"     2 $PY "$S/ossie_to_sv.py" "$OUT/bad.yaml" --view t.v -o "$OUT/e.sql"
exits "ossie_to_sv on an empty file"      2 $PY "$S/ossie_to_sv.py" "$OUT/empty.yaml" --view t.v -o "$OUT/e.sql"
exits "ossie_to_sv on an empty model"     2 $PY "$S/ossie_to_sv.py" "$OUT/nomodel.yaml" --view t.v -o "$OUT/e.sql"
exits "ossie_to_sv on a directory"        2 $PY "$S/ossie_to_sv.py" "$OUT" --view t.v -o "$OUT/e.sql"
exits "sv_to_ossie on broken JSON"        2 $PY "$S/sv_to_ossie.py" "$OUT/notjson.json" -o "$OUT/e.yaml"
exits "sv_to_ossie on a dump with no ddl" 2 $PY "$S/sv_to_ossie.py" "$OUT/baddump.json" -o "$OUT/e.yaml"
exits "sv_to_ossie on a missing --ddl"    2 $PY "$S/sv_to_ossie.py" --ddl "$OUT/nope.sql" -o "$OUT/e.yaml"
exits "validate on a missing file"        2 $PY "$S/validate_ossie.py" "$OUT/nope.yaml"
exits "validate on malformed YAML"        2 $PY "$S/validate_ossie.py" "$OUT/bad.yaml"
exits "ossie_diff on a missing file"      2 $PY "$S/ossie_diff.py" "$OUT/nope.yaml" "$OUT/nope2.yaml"
exits "ossie_diff on malformed YAML"      2 $PY "$S/ossie_diff.py" "$OUT/bad.yaml" "$OUT/nomodel.yaml"
exits "derive_ontology on a missing file" 2 $PY "$S/derive_ontology.py" "$OUT/nope.yaml" -o "$OUT/ont.yaml"
exits "enrich_from_ontology missing file" 2 $PY "$S/enrich_from_ontology.py" "$OUT/nope.yaml" -o "$OUT/ont.yaml"
# readable but unusable input keeps its own code, so 2 does not swallow every failure
exits "derive_ontology on an empty model" 2 $PY "$S/derive_ontology.py" "$OUT/nomodel.yaml" -o "$OUT/ont.yaml"
# a readable file that is merely invalid is 1, not 2
printf 'version: 0.2.0.dev0\nsemantic_model:\n- name: X\n  datasets: []\n  relationships:\n  - name: r\n    from: nope\n    to: nope2\n    from_columns: [a]\n    to_columns: [b]\n' \
  > "$OUT/invalid.yaml"
exits "validate on a readable but invalid model" 1 $PY "$S/validate_ossie.py" "$OUT/invalid.yaml"
exits "ossie_diff on two different models"       1 $PY "$S/ossie_diff.py" "$OUT/e1.yaml" "$OUT/invalid.yaml"
# positive controls: the same scripts still succeed on good input
exits "sv_ddl on a real DDL file"                0 $PY "$S/sv_ddl.py" "$F/sales_sv.sql"
exits "validate on a valid model"                0 $PY "$S/validate_ossie.py" "$OUT/e1.yaml"
exits "ossie_diff on a model and itself"         0 $PY "$S/ossie_diff.py" "$OUT/e1.yaml" "$OUT/e1.yaml"

# 11. round-trip sensitivity. A diff that never reports a difference proves nothing, so mutate
#     one expression and require the check to catch it; then confirm the sidecar is what brings
#     the other platform's expressions back.
cp "$OUT/e1.yaml" "$OUT/mut.yaml"
$PY - "$OUT/mut.yaml" <<'EOF3'
import re, sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"SUM\(order_items\.quantity", "SUM(order_items.qty", s, count=1)
assert n == 1, "mutation did not apply"
open(p, "w", encoding="utf-8").write(s2)
EOF3
$PY "$S/ossie_diff.py" "$OUT/e1.yaml" "$OUT/mut.yaml" >/dev/null 2>&1 \
  && bad "diff called a mutated model equivalent" \
  || ok "diff detects a single-token expression change"

$PY "$S/ossie_to_sv.py" "$F/snowflake_orders.ossie.yaml" --view ossie_skill_test.snow_sv \
    --source-map "SNOW_DB.SALES=ossie_skill_test" --overrides "$F/snowflake_overrides.yaml" \
    -o "$OUT/sd.sql" >/dev/null 2>&1 || true
$PY - "$OUT/sd.sql" "$OUT/sd_dump.json" <<'EOF3'
import json, sys
create, _, alter = open(sys.argv[1], encoding="utf-8").read().partition("ALTER SEMANTIC VIEW")
json.dump({"view": "ossie_skill_test.snow_sv", "ddl": create, "raw": {"desc_extended": alter}},
          open(sys.argv[2], "w"))
EOF3
$PY "$S/sv_to_ossie.py" "$OUT/sd_dump.json" -o "$OUT/sd_back.yaml" --issues "$OUT/sd_issues.json" >/dev/null 2>&1 || true
$PY - "$OUT/sd_issues.json" "$OUT/sd_back.yaml" <<'EOF3' \
  && ok "sidecar restores the other platform's dialect and expressions" || bad "sidecar restore"
import json, sys, yaml
msgs = " ".join(i["message"] for i in json.load(open(sys.argv[1])))
assert "sidecar found" in msgs, msgs
d = yaml.safe_load(open(sys.argv[2]))
f = {x["name"]: x for ds in d["semantic_model"][0]["datasets"] for x in ds.get("fields", [])}
ex = f["is_completed"]["expression"]["dialects"][0]
assert ex["dialect"] == "SNOWFLAKE", ex
assert "IFF(" in ex["expression"], ex
EOF3

# Ignoring the two representation shifts (which field carries a synonym; which vendor key holds an
# extension) the Snowflake round trip must be clean. Anything still differing would be a real loss
# that references/mapping.md does not list.
$PY "$S/ossie_diff.py" "$F/snowflake_orders.ossie.yaml" "$OUT/sd_back.yaml" \
    --ignore synonyms,extensions >"$OUT/sd_diff.txt" 2>&1 \
  && ok "Snowflake round trip is lossless beyond the documented representation shifts" \
  || { bad "Snowflake round trip lost something unmapped"; head -5 "$OUT/sd_diff.txt"; }

# 12. the lock that keeps two live suites off the same profile. Two at once contend for one
#     vcluster and both start failing with JOB_TIMEOUT, which reads as a product problem. Pure
#     shell, so it is tested here rather than in a live suite.
LOCKT="$OUT/locktest"; mkdir -p "$LOCKT"
locktry() { ( LOCK_ROOT="$LOCKT"; . "$HERE/lib/lock.sh"; acquire_lock "$1" ) >/dev/null 2>&1; }
locktry alpha && ok "lock: first holder acquires" || bad "lock: first acquire failed"
locktry alpha && bad "lock: second holder was not refused" || ok "lock: second holder refused"
locktry beta  && ok "lock: a different profile is independent" || bad "lock: profiles not independent"
# release has to happen in the shell that holds it: releasing from elsewhere must be a no-op, or a
# bystander could free a lock a running suite depends on
( LOCK_ROOT="$LOCKT"; . "$HERE/lib/lock.sh"; acquire_lock gamma && release_lock ) >/dev/null 2>&1 \
  && locktry gamma && ok "lock: released by its holder, then reacquirable" \
  || bad "lock: not released by its holder"

echo "offline tests: $pass passed, $fail failed, $knowns known defects"
[ "$fail" -eq 0 ]
