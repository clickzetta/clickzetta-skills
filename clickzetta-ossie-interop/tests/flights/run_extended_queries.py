#!/usr/bin/env python3
"""Extended semantic_view() verification: FACTS, WHERE and outer SQL.

`run_queries.py` checks DIMENSIONS+METRICS against expectations computed up front in sqlite. This
script covers what that misses, and checks it a different way: every case runs the `semantic_view()`
query **and** a hand-written query over the physical tables, then compares the two result multisets.
Agreement between two independent implementations is the evidence, so nothing has to be recorded
ahead of time and the script works against any schema built by gen_flights.py.

    python3 run_extended_queries.py --cz-cli "cz-cli -p <profile>" --schema ossie_flights_demo --out DIR

Cases that must be *rejected* assert on the engine's message instead of comparing rows.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# each case: name, sv (a full SELECT), plain (equivalent over the physical tables) or expect_error
CASES = [
    # ---- FACTS: row-level projection, no aggregation -------------------------------------------
    {
        "name": "facts_aircraft_seats",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv FACTS AIRCRAFT.nr_seats)",
        "plain": "SELECT nr_seats FROM {s}.aircraft",
    },
    {
        "name": "facts_with_dimension",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS AIRCRAFT.manufacturer FACTS AIRCRAFT.nr_seats)",
        "plain": "SELECT manufacturer, nr_seats FROM {s}.aircraft",
    },
    {
        "name": "facts_flight_delay",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS FLIGHT.carrier_code FACTS FLIGHT.dep_delay)",
        "plain": "SELECT carrier_code, dep_delay FROM {s}.flights",
    },
    {
        "name": "facts_runway_length",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS RUNWAY.airport_code FACTS RUNWAY.length)",
        "plain": "SELECT airport_code, length FROM {s}.runways",
    },
    # ---- inner WHERE ---------------------------------------------------------------------------
    {
        "name": "where_qualified_dimension",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS CARRIER.name "
              "METRICS FLIGHT.flight_count WHERE CARRIER.name = 'Delta Air Lines')",
        "plain": "SELECT c.name, COUNT(f.id) FROM {s}.carriers c JOIN {s}.flights f "
                 "ON f.carrier_code = c.code WHERE c.name = 'Delta Air Lines' GROUP BY c.name",
    },
    {
        "name": "where_boolean_dimension",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS FLIGHT.cancelled "
              "METRICS FLIGHT.flight_count WHERE FLIGHT.cancelled = true)",
        "plain": "SELECT cancelled, COUNT(id) FROM {s}.flights WHERE cancelled = true GROUP BY cancelled",
    },
    {
        "name": "where_on_a_fact",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS FLIGHT.carrier_code "
              "FACTS FLIGHT.dep_delay WHERE FLIGHT.dep_delay > 10)",
        "plain": "SELECT carrier_code, dep_delay FROM {s}.flights WHERE dep_delay > 10",
    },
    # ---- outer SQL over the semantic_view() result ---------------------------------------------
    {
        "name": "outer_order_by_limit",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS CARRIER.name "
              "METRICS FLIGHT.flight_count) ORDER BY flight_count DESC LIMIT 2",
        "plain": "SELECT c.name, COUNT(f.id) AS n FROM {s}.carriers c JOIN {s}.flights f "
                 "ON f.carrier_code = c.code GROUP BY c.name ORDER BY n DESC LIMIT 2",
    },
    {
        "name": "outer_subquery_filters_an_aggregate",
        "sv": "SELECT * FROM (SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS CARRIER.name "
              "METRICS FLIGHT.flight_count)) t WHERE t.flight_count > 8",
        "plain": "SELECT c.name, COUNT(f.id) AS n FROM {s}.carriers c JOIN {s}.flights f "
                 "ON f.carrier_code = c.code GROUP BY c.name HAVING COUNT(f.id) > 8",
    },
    {
        "name": "cte",
        "sv": "WITH per_carrier AS (SELECT * FROM semantic_view({s}.flights_sv "
              "DIMENSIONS CARRIER.name METRICS FLIGHT.flight_count)) "
              "SELECT name FROM per_carrier WHERE flight_count = 9",
        "plain": "SELECT c.name FROM {s}.carriers c JOIN {s}.flights f ON f.carrier_code = c.code "
                 "GROUP BY c.name HAVING COUNT(f.id) = 9",
    },
    {
        "name": "join_with_a_physical_table",
        "sv": "SELECT sv.name, sv.flight_count, c.code FROM semantic_view({s}.flights_sv "
              "DIMENSIONS CARRIER.name METRICS FLIGHT.flight_count) sv "
              "JOIN {s}.carriers c ON sv.name = c.name ORDER BY sv.name",
        "plain": "SELECT c.name, COUNT(f.id), c.code FROM {s}.carriers c JOIN {s}.flights f "
                 "ON f.carrier_code = c.code GROUP BY c.name, c.code ORDER BY c.name",
    },
    # ---- role-playing joins, the hard part of this model ---------------------------------------
    {
        "name": "departure_role",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS AIRPORT.name "
              "METRICS FLIGHT.avg_departure_delay)",
        "plain": "SELECT a.name, AVG(f.dep_delay) FROM {s}.airports a "
                 "JOIN {s}.routes r ON r.orig_airport_code = a.code "
                 "JOIN {s}.flights f ON f.route_id = r.id GROUP BY a.name",
    },
    {
        "name": "arrival_role",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS AIRPORT.name "
              "METRICS FLIGHT.avg_arrival_delay)",
        "plain": "SELECT a.name, AVG(f.arr_delay) FROM {s}.airports a "
                 "JOIN {s}.routes r ON r.dest_airport_code = a.code "
                 "JOIN {s}.flights f ON f.route_id = r.id GROUP BY a.name",
    },
    {
        "name": "two_hop_runways",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS AIRPORT.state_code "
              "METRICS RUNWAY.runway_count)",
        "plain": "SELECT a.state_code, COUNT(rw.designator) FROM {s}.airports a "
                 "JOIN {s}.runways rw ON rw.airport_code = a.code GROUP BY a.state_code",
    },
    # ---- short names are only usable when they are unambiguous ---------------------------------
    {
        "name": "short_name_is_unique",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS manufacturer "
              "METRICS total_seats)",
        "plain": "SELECT manufacturer, SUM(nr_seats) FROM {s}.aircraft GROUP BY manufacturer",
    },
    {
        "name": "ambiguous_short_name_is_rejected",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS name METRICS FLIGHT.flight_count)",
        "expect_error": "ambiguous",
    },
    # ---- the constraints the docs promise ------------------------------------------------------
    {
        "name": "facts_and_metrics_cannot_be_mixed",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS CARRIER.name "
              "METRICS FLIGHT.flight_count FACTS AIRCRAFT.nr_seats)",
        "expect_error": "FACTS and METRICS cannot be requested in the same semantic_view() query",
    },
    {
        "name": "where_cannot_reference_a_metric",
        "sv": "SELECT * FROM semantic_view({s}.flights_sv DIMENSIONS CARRIER.name "
              "METRICS FLIGHT.flight_count WHERE FLIGHT.flight_count > 1)",
        "expect_error": "is not allowed in the semantic_view() WHERE clause",
    },
]


def run(cz_cli: list[str], sql: str) -> tuple[bool, object]:
    p = subprocess.run(cz_cli + ["sql", "--no-limit", "--no-truncate", "-e", sql],
                       capture_output=True, text=True)
    text = (p.stdout or p.stderr).strip()
    if not text:
        return False, "no output"
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return False, text[:300]
    if isinstance(obj, dict) and obj.get("error"):
        return False, obj["error"].get("message", str(obj["error"]))
    if isinstance(obj, dict) and "rows" in obj:
        return True, {"columns": obj.get("columns") or [], "rows": obj.get("rows") or []}
    return False, text[:300]


def norm(v):
    """A sortable, comparable key. Numbers come back at different scales from the two
    implementations (4.50000 vs 4.5), and NULLs have to sort next to numbers, not against them."""
    if v is None:
        return (0, 0.0, "")           # NULL sorts before everything, consistently
    if isinstance(v, bool):
        return (1, float(v), "")
    try:
        return (2, round(float(v), 4), "")
    except (TypeError, ValueError):
        return (3, 0.0, str(v))


def bag(result) -> list:
    return sorted(tuple(norm(v) for v in row) for row in result["rows"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cz-cli", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cz = a.cz_cli.split()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    passed = failed = 0

    for c in CASES:
        name = c["name"]
        sql = c["sv"].format(s=a.schema)
        # terminated with `;` so the artifact is a statement that can be run as-is. The same text
        # goes to cz-cli via -e, where the semicolon is redundant but harmless.
        (out / f"x_{name}.sql").write_text(sql + ";\n", encoding="utf-8")
        ok, got = run(cz, sql)

        if "expect_error" in c:
            if ok:
                print(f"FAIL  {name}: accepted, expected an error about '{c['expect_error']}'")
                failed += 1
            elif c["expect_error"].lower() in str(got).lower():
                print(f"PASS  {name}: rejected - {str(got)[:90]}")
                passed += 1
            else:
                print(f"FAIL  {name}: wrong error - {str(got)[:120]}")
                failed += 1
            continue

        plain_sql = c["plain"].format(s=a.schema)
        (out / f"x_{name}.plain.sql").write_text(plain_sql + ";\n", encoding="utf-8")
        ok2, want = run(cz, plain_sql)
        if not ok:
            print(f"FAIL  {name}: semantic_view() failed - {str(got)[:140]}")
            failed += 1
        elif not ok2:
            print(f"FAIL  {name}: the plain-SQL control failed - {str(want)[:140]}")
            failed += 1
        elif bag(got) == bag(want):
            print(f"PASS  {name}: {len(got['rows'])} rows, identical to the plain-SQL control")
            json.dump({"semantic_view": got, "plain_sql": want},
                      open(out / f"x_{name}.result.json", "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            passed += 1
        else:
            print(f"FAIL  {name}: {len(got['rows'])} rows vs {len(want['rows'])} from plain SQL")
            for r in (bag(got)[:4]):
                print(f"        sv   : {r}")
            for r in (bag(want)[:4]):
                print(f"        plain: {r}")
            failed += 1

    print(f"\nextended queries: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
