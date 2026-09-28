#!/usr/bin/env python3
"""Generate physical tables + data for the apache/ossie flights example, and expected query results.

Writes, into --out:
  tables.sql      CREATE TABLE + INSERT statements for ClickZetta (schema given by --schema)
  queries.json    [{name, view, sv_args, expected: [[...], ...], order_by}]  expected results are
                  computed independently with sqlite from the same rows, never from ClickZetta.
The data honours the ontology rules (e.g. a flight's carrier equals its aircraft's carrier,
cancel codes in A-D, scheduled departure < scheduled arrival, distance groups 1..10).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3

CARRIERS = [("DL", "Delta Air Lines"), ("UA", "United Airlines"), ("AA", "American Airlines")]
AIRPORTS = [  # code, name, city, state_code, state_nm, market, lat, lon, opened
    ("ATL", "Hartsfield-Jackson Atlanta International", "Atlanta", "GA", "Georgia", "Atlanta", 33.640700, -84.427700, "1926-09-15"),
    ("DCA", "Ronald Reagan Washington National", "Arlington", "VA", "Virginia", "Washington DC", 38.852100, -77.037700, "1941-06-16"),
    ("JFK", "John F. Kennedy International", "New York", "NY", "New York", "New York City", 40.641300, -73.778100, "1948-07-01"),
    ("ORD", "O'Hare International", "Chicago", "IL", "Illinois", "Chicago", 41.974200, -87.907300, "1944-01-01"),
    ("LAX", "Los Angeles International", "Los Angeles", "CA", "California", "Los Angeles", 33.941600, -118.408500, "1930-06-07"),
]
ROUTES = [  # orig, dest, distance, group
    ("ATL", "DCA", 547, 3), ("DCA", "ATL", 547, 3), ("JFK", "LAX", 2475, 10),
    ("ORD", "JFK", 740, 3), ("LAX", "ORD", 1745, 7), ("ATL", "JFK", 760, 4),
]
AIRCRAFT = [  # tail, serial, name, seats, carrier, manufacturer, model, year, capacity
    ("N101DL", "SN-33001", "Peach State", 180, "DL", "Boeing", "737-900", "2015", 174200),
    ("N202DL", "SN-45002", "Spirit of Atlanta", 191, "DL", "Airbus", "A321", "2018", 206000),
    ("N301UA", "SN-29003", "Friend Ship", 176, "UA", "Boeing", "757-200", "2002", 255000),
    ("N401AA", "SN-51004", "Flagship Dallas", 150, "AA", "Airbus", "A320", "2012", 172000),
    ("N402AA", "SN-52005", "Flagship Miami", 172, "AA", "Boeing", "737-800", "2016", 174200),
]
RUNWAYS = [  # airport, designator, length, shape
    ("ATL", "08L/26R", 9000.0, "POLYGON((0 0,1 0,1 1,0 1,0 0))"), ("ATL", "09R/27L", 12390.0, "POLYGON((0 0,2 0,2 1,0 1,0 0))"),
    ("JFK", "04L/22R", 12079.0, "POLYGON((0 0,3 0,3 1,0 1,0 0))"), ("ORD", "10L/28R", 13000.0, "POLYGON((0 0,4 0,4 1,0 1,0 0))"),
    ("LAX", "25R/07L", 11095.0, "POLYGON((0 0,5 0,5 1,0 1,0 0))"), ("DCA", "01/19", 7169.0, "POLYGON((0 0,6 0,6 1,0 1,0 0))"),
]


def flights():
    rows = []
    base = dt.datetime(2026, 3, 1, 6, 0)
    for i in range(24):
        orig, dest, dist, _ = ROUTES[i % len(ROUTES)]
        tail = AIRCRAFT[i % len(AIRCRAFT)]
        carrier = tail[4]
        sched_dep = base + dt.timedelta(days=i // 6, hours=(i % 6) * 2)
        sched_dur = round(dist / 8.0 + 30, 1)
        sched_arr = sched_dep + dt.timedelta(minutes=sched_dur)
        cancelled = i in (5, 17)
        diverted = i == 11
        dep_delay = None if cancelled else float((i * 7) % 45 - 5)
        arr_delay = None if cancelled else float((i * 11) % 50 - 10)
        dep = None if cancelled else sched_dep + dt.timedelta(minutes=dep_delay)
        arr = None if cancelled else sched_arr + dt.timedelta(minutes=arr_delay)
        wheels_off = None if cancelled else dep + dt.timedelta(minutes=15)
        wheels_on = None if cancelled else arr - dt.timedelta(minutes=8)
        air_time = None if cancelled else round((wheels_on - wheels_off).total_seconds() / 60, 1)
        duration = None if cancelled else round((arr - dep).total_seconds() / 60, 1)
        rows.append({
            "id": f"F{i + 1:04d}", "nr": f"{carrier}{100 + i}", "carrier_code": carrier, "tail_nr": tail[0],
            "route_id": f"{orig} -> {dest}", "date": sched_dep.date().isoformat(),
            "scheduled_departure": sched_dep, "scheduled_arrival": sched_arr, "scheduled_duration": sched_dur,
            "departure": dep, "arrival": arr, "wheels_off": wheels_off, "wheels_on": wheels_on,
            "dep_delay": dep_delay, "arr_delay": arr_delay, "air_time": air_time, "duration": duration,
            "distance": float(dist), "cancelled": cancelled, "cancel_code": "B" if cancelled else None,
            "diverted": diverted})
    return rows


TABLES = {  # table -> [(column, clickzetta type, sqlite type)]
    "runways": [("airport_code", "STRING"), ("length", "DECIMAL(10,1)"), ("shape", "STRING"), ("designator", "STRING")],
    "aircraft": [("serial_nr", "STRING"), ("name", "STRING"), ("nr_seats", "INT"), ("tail_nr", "STRING"),
                 ("carrier_code", "STRING"), ("manufacturer", "STRING"), ("model", "STRING"), ("year", "STRING"),
                 ("capacity", "INT")],
    "airports": [("state_code", "STRING"), ("market_nm", "STRING"), ("longitude", "DECIMAL(9,6)"), ("opened", "DATE"),
                 ("state_nm", "STRING"), ("city_nm", "STRING"), ("name", "STRING"), ("code", "STRING"),
                 ("latitude", "DECIMAL(9,6)")],
    "flights": [("dep_delay", "DECIMAL(8,1)"), ("air_time", "DECIMAL(8,1)"), ("nr", "STRING"), ("carrier_code", "STRING"),
                ("duration", "DECIMAL(8,1)"), ("scheduled_departure", "TIMESTAMP_NTZ"), ("arr_delay", "DECIMAL(8,1)"),
                ("cancelled", "BOOLEAN"), ("cancel_code", "STRING"), ("distance", "DECIMAL(8,1)"), ("id", "STRING"),
                ("scheduled_arrival", "TIMESTAMP_NTZ"), ("wheels_on", "TIMESTAMP_NTZ"), ("date", "DATE"),
                ("wheels_off", "TIMESTAMP_NTZ"), ("scheduled_duration", "DECIMAL(8,1)"), ("tail_nr", "STRING"),
                ("departure", "TIMESTAMP_NTZ"), ("route_id", "STRING"), ("diverted", "BOOLEAN"), ("arrival", "TIMESTAMP_NTZ")],
    "carriers": [("code", "STRING"), ("name", "STRING")],
    "routes": [("orig_airport_code", "STRING"), ("dest_airport_code", "STRING"), ("distance", "DECIMAL(8,1)"),
               ("dist_grp", "INT"), ("id", "STRING"), ("name", "STRING")],
}


def data() -> dict[str, list[dict]]:
    name_of = {a[0]: a[2] for a in AIRPORTS}
    return {
        "carriers": [{"code": c, "name": n} for c, n in CARRIERS],
        "airports": [{"code": a[0], "name": a[1], "city_nm": a[2], "state_code": a[3], "state_nm": a[4],
                      "market_nm": a[5], "latitude": a[6], "longitude": a[7], "opened": a[8]} for a in AIRPORTS],
        "routes": [{"orig_airport_code": o, "dest_airport_code": d, "distance": float(x), "dist_grp": g,
                    "id": f"{o} -> {d}", "name": f"{name_of[o]} to {name_of[d]}"} for o, d, x, g in ROUTES],
        "aircraft": [{"tail_nr": t, "serial_nr": s, "name": n, "nr_seats": seats, "carrier_code": c,
                      "manufacturer": m, "model": mo, "year": y, "capacity": cap}
                     for t, s, n, seats, c, m, mo, y, cap in AIRCRAFT],
        "runways": [{"airport_code": a, "designator": d, "length": l, "shape": s} for a, d, l, s in RUNWAYS],
        "flights": flights(),
    }


def lit(v, typ: str) -> str:
    if v is None:
        return "NULL"
    if typ == "BOOLEAN":
        return "TRUE" if v else "FALSE"
    if typ == "DATE":
        return f"DATE '{v}'"
    if typ.startswith("TIMESTAMP"):
        return f"CAST('{v.strftime('%Y-%m-%d %H:%M:%S')}' AS TIMESTAMP_NTZ)"
    if typ in ("INT",) or typ.startswith("DECIMAL"):
        return str(v)
    return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"


def q(c: str) -> str:
    return f"`{c}`"


QUERIES = [  # name, view, semantic_view args, sqlite SQL computing the same thing
    ("by_carrier", "flights_sv",
     "DIMENSIONS CARRIER.name METRICS FLIGHT.flight_count, FLIGHT.cancelled_flights, FLIGHT.avg_departure_delay",
     "SELECT c.name, COUNT(f.id), SUM(f.cancelled), AVG(f.dep_delay) FROM flights f JOIN carriers c ON f.carrier_code=c.code GROUP BY c.name"),
    ("by_route", "flights_sv",
     "DIMENSIONS ROUTE.name METRICS FLIGHT.flight_count, FLIGHT.avg_departure_delay, FLIGHT.avg_arrival_delay",
     "SELECT r.name, COUNT(f.id), AVG(f.dep_delay), AVG(f.arr_delay) FROM flights f JOIN routes r ON f.route_id=r.id GROUP BY r.name"),
    ("by_distance_group", "flights_sv",
     "DIMENSIONS ROUTE.dist_grp METRICS FLIGHT.total_flight_distance, FLIGHT.flight_count",
     "SELECT r.dist_grp, SUM(f.distance), COUNT(f.id) FROM flights f JOIN routes r ON f.route_id=r.id GROUP BY r.dist_grp"),
    ("by_date", "flights_sv",
     "DIMENSIONS FLIGHT.`date` METRICS FLIGHT.flight_count, FLIGHT.diverted_flights",
     "SELECT f.date, COUNT(f.id), SUM(f.diverted) FROM flights f GROUP BY f.date"),
    ("by_manufacturer_flights", "flights_sv",
     "DIMENSIONS AIRCRAFT.manufacturer METRICS FLIGHT.flight_count",
     "SELECT a.manufacturer, COUNT(f.id) FROM flights f JOIN aircraft a ON f.tail_nr=a.tail_nr GROUP BY a.manufacturer"),
    ("fleet_seats", "flights_sv",
     "DIMENSIONS AIRCRAFT.manufacturer METRICS AIRCRAFT.total_seats",
     "SELECT manufacturer, SUM(nr_seats) FROM aircraft GROUP BY manufacturer"),
    ("runways_by_state", "flights_sv",
     "DIMENSIONS AIRPORT.state_code METRICS RUNWAY.runway_count",
     "SELECT a.state_code, COUNT(r.designator) FROM runways r JOIN airports a ON r.airport_code=a.code GROUP BY a.state_code"),
    ("cancelled_flag", "flights_sv",
     "DIMENSIONS FLIGHT.cancelled METRICS FLIGHT.flight_count",
     "SELECT f.cancelled, COUNT(f.id) FROM flights f GROUP BY f.cancelled"),
    # Same carrier question on the tree-shaped view (one join path per table pair).
    ("by_carrier_tree", "flights_tree_sv",
     "DIMENSIONS CARRIER.name METRICS FLIGHT.flight_count, FLIGHT.cancelled_flights, FLIGHT.avg_departure_delay",
     "SELECT c.name, COUNT(f.id), SUM(f.cancelled), AVG(f.dep_delay) FROM flights f JOIN carriers c ON f.carrier_code=c.code GROUP BY c.name"),
    # Airport.average_departure_delay from the ontology: grouped by the route's DEPARTURE airport.
    # On the tree-shaped view there is only the departure role.
    ("dep_airport_delay_tree", "flights_tree_sv",
     "DIMENSIONS AIRPORT.name METRICS FLIGHT.avg_departure_delay",
     "SELECT a.name, AVG(f.dep_delay) FROM flights f JOIN routes r ON f.route_id=r.id JOIN airports a ON r.orig_airport_code=a.code GROUP BY a.name"),
    # The full view has BOTH roles (named relationships); each metric picks its path with USING.
    ("dep_airport_delay", "flights_sv",
     "DIMENSIONS AIRPORT.name METRICS FLIGHT.avg_departure_delay, FLIGHT.flight_count",
     "SELECT a.name, AVG(f.dep_delay), COUNT(f.id) FROM flights f JOIN routes r ON f.route_id=r.id JOIN airports a ON r.orig_airport_code=a.code GROUP BY a.name"),
    ("arr_airport_delay", "flights_sv",
     "DIMENSIONS AIRPORT.name METRICS FLIGHT.avg_arrival_delay",
     "SELECT a.name, AVG(f.arr_delay) FROM flights f JOIN routes r ON f.route_id=r.id JOIN airports a ON r.dest_airport_code=a.code GROUP BY a.name"),
    # One query, two roles of the same table: departure-airport metric next to arrival-airport metric.
    ("both_roles_by_carrier", "flights_sv",
     "DIMENSIONS CARRIER.name METRICS FLIGHT.avg_departure_delay, FLIGHT.avg_arrival_delay",
     "SELECT c.name, AVG(f.dep_delay), AVG(f.arr_delay) FROM flights f JOIN carriers c ON f.carrier_code=c.code GROUP BY c.name"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", default="ossie_flights_test")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = data()
    lines = [f"-- Physical tables for apache/ossie examples/flights.yaml (schema {a.schema})"]
    db = sqlite3.connect(":memory:")
    for t, cols in TABLES.items():
        lines.append(f"CREATE TABLE {a.schema}.{t} ({', '.join(f'{q(c)} {ty}' for c, ty in cols)});")
        values = [f"({', '.join(lit(r.get(c), ty) for c, ty in cols)})" for r in d[t]]
        lines.append(f"INSERT INTO {a.schema}.{t} ({', '.join(q(c) for c, _ in cols)}) VALUES\n  " + ",\n  ".join(values) + ";")
        db.execute(f"CREATE TABLE {t} ({', '.join(q(c) for c, _ in cols)})")
        for r in d[t]:
            vals = [r.get(c) for c, _ in cols]
            vals = [v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, dt.datetime) else (int(v) if isinstance(v, bool) else v)
                    for v in vals]
            db.execute(f"INSERT INTO {t} VALUES ({', '.join('?' * len(cols))})", vals)
    with open(os.path.join(a.out, "tables.sql"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    out = []
    for name, view, args, sql in QUERIES:
        exp = [list(r) for r in db.execute(sql).fetchall()] if sql else None
        out.append({"name": name, "view": view, "sv_args": args, "expected": exp})
    with open(os.path.join(a.out, "queries.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote tables.sql ({sum(len(v) for v in d.values())} rows) and queries.json ({len(out)} queries)")


if __name__ == "__main__":
    main()
