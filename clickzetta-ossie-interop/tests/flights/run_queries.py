#!/usr/bin/env python3
"""Run the flights semantic_view() queries through cz-cli and compare with sqlite-computed expectations.

Usage: python3 run_queries.py --cz-cli "cz-cli -p uat" --schema ossie_flights_test --queries queries.json --out DIR
Writes DIR/q_<name>.json (raw cz-cli output) and prints PASS/FAIL/OBSERVED lines.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from czossie_common import parse_cli_rows  # noqa: E402


def norm(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    s = str(v).strip()
    if s.lower() in ("true", "false"):
        return 1.0 if s.lower() == "true" else 0.0
    try:
        return round(float(s), 3)
    except ValueError:
        return s[:10] if len(s) >= 10 and s[4:5] == "-" and s[7:8] == "-" else s


def key(row):
    return tuple((0, "") if v is None else (1, v) if isinstance(v, float) else (2, v) for v in row)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cz-cli", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--queries", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cli = shlex.split(a.cz_cli)
    fails = 0
    for q in json.load(open(a.queries)):
        sql = f"SELECT * FROM semantic_view({a.schema}.{q['view']} {q['sv_args']})"
        p = subprocess.run(cli + ["sql", "--no-limit", "-e", sql], capture_output=True, text=True)
        raw = p.stdout + ("\n--- stderr ---\n" + p.stderr if p.stderr else "")
        open(os.path.join(a.out, f"q_{q['name']}.json"), "w").write(f"-- {sql}\n{raw}")
        if p.returncode != 0:
            status = "OBSERVED" if q["expected"] is None else "FAIL"
            fails += status == "FAIL"
            print(f"{status:8} query {q['name']}: cz-cli error: {' '.join(raw.split())[:300]}")
            continue
        try:
            rows = parse_cli_rows(p.stdout)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL     query {q['name']}: cannot parse output ({exc})")
            fails += 1
            continue
        got = sorted((tuple(norm(v) for v in r.values()) for r in rows), key=key)
        if q["expected"] is None:
            print(f"OBSERVED query {q['name']}: {len(got)} rows: {got[:6]}")
            continue
        exp = sorted((tuple(norm(v) for v in r) for r in q["expected"]), key=key)
        if got == exp:
            print(f"PASS     query {q['name']} ({len(got)} rows match sqlite)")
        else:
            fails += 1
            print(f"FAIL     query {q['name']}:\n         expected {exp}\n         got      {got}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
