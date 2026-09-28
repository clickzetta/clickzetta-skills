#!/usr/bin/env python3
"""Test helper: derive empty physical tables and smoke queries for an imported Ossie model.

  gen_empty_tables.py sourcemap MODEL SCHEMA          -> prints --source-map arguments (one per line)
  gen_empty_tables.py tables DDL MODEL --out DIR      -> DIR/tables.sql, DIR/drop.sql, DIR/queries.txt

Columns are every <alias>.<column> the view's expressions, keys and relationships use. Types come
from the Ossie field datatype when the field is a bare column; otherwise DOUBLE for columns under
SUM/AVG/arithmetic, STRING for the rest. Relationship columns share one type on both sides.
The tables stay empty: the point is that ClickZetta accepts the view and compiles every query.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from czossie_common import iter_dialects, load_yaml  # noqa: E402
from ossie_to_sv import pick_models  # noqa: E402
from sv_ddl import parse_ddl  # noqa: E402

TYPES = {"String": "STRING", "Integer": "BIGINT", "Decimal": "DECIMAL(18,4)", "Float": "DOUBLE",
         "Boolean": "BOOLEAN", "Date": "DATE", "DateTime": "TIMESTAMP_NTZ", "DateTimeTz": "TIMESTAMP"}


def sourcemap(model_path: str, schema: str) -> None:
    prefixes = set()
    for m in pick_models(load_yaml(model_path)):
        for d in m.get("datasets") or []:
            parts = str(d.get("source", "")).split(".")
            if len(parts) >= 2:
                prefixes.add(".".join(parts[:-1]))
    for p in sorted(prefixes):
        print(f"{p}={schema}")


def tables(ddl_path: str, model_path: str, out: str) -> None:
    ddl = parse_ddl(open(ddl_path, encoding="utf-8").read())
    model = pick_models(load_yaml(model_path))[0]
    dtype: dict[tuple, str] = {}
    for d in model.get("datasets") or []:
        for f in d.get("fields") or []:
            for _, e in iter_dialects(f.get("expression")):
                if re.fullmatch(r"`?\w+`?", e.strip()) and f.get("datatype") in TYPES:
                    dtype[(d["name"].lower(), e.strip("` ").lower())] = TYPES[f["datatype"]]
    src = {t["alias"].lower(): t["source"] for t in ddl["tables"]}
    cols: dict[str, dict[str, str]] = {a: {} for a in src}
    metric_names = {m["name"].lower() for m in ddl["metrics"]}

    def add(alias: str, col: str, numeric: bool = False) -> None:
        a, c = alias.lower(), col.strip("`").lower()
        if a not in cols:
            return
        declared = dtype.get((a, c))
        if declared:
            cols[a][c] = declared
        elif numeric:
            cols[a][c] = "DOUBLE"
        else:
            cols[a].setdefault(c, "STRING")

    for kind in ("facts", "dimensions", "metrics"):
        for m in ddl[kind]:
            e = m["expression"]
            num_zone = " ".join(re.findall(r"\b(?:SUM|AVG)\s*\(([^()]*(?:\([^()]*\))*[^()]*)\)", e, re.I))
            for a, c in re.findall(r"(?<![\w.`])`?(\w+)`?\s*\.\s*`?(\w+)`?", e):
                if kind == "metrics" and c.lower() in metric_names:
                    continue
                add(a, c, numeric=f"{a}.{c}" in num_zone or bool(re.search(rf"{a}\.{c}\s*[*/+-]|[*/+-]\s*{a}\.{c}", e)))
    for t in ddl["tables"]:
        for c in t["primary_key"]:
            add(t["alias"], c)
    for r in ddl["relationships"]:
        for fc, tc in zip(r["from_columns"], r["to_columns"] or []):
            add(r["from"], fc)
            add(r["to"], tc)
            a, b = (r["from"].lower(), fc.lower()), (r["to"].lower(), tc.lower())
            ty = "STRING" if "STRING" in (cols[a[0]].get(a[1]), cols[b[0]].get(b[1])) else "BIGINT"
            cols[a[0]][a[1]] = cols[b[0]][b[1]] = ty
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "tables.sql"), "w") as fh:
        for a, cs in cols.items():
            body = ", ".join(f"`{c}` {t}" for c, t in cs.items()) or "`dummy` STRING"
            fh.write(f"CREATE TABLE {src[a]} ({body});\n")
    with open(os.path.join(out, "drop.sql"), "w") as fh:
        for a in cols:
            fh.write(f"DROP TABLE IF EXISTS {src[a]};\n")
    with open(os.path.join(out, "queries.txt"), "w") as fh:
        for m in ddl["metrics"]:
            if not m["private"]:
                fh.write("METRICS " + (f"{m['table']}.{m['name']}" if m["table"] else m["name"]) + "\n")
        for d in ddl["dimensions"]:
            if not d["private"]:
                fh.write(f"DIMENSIONS {d['table']}.`{d['name']}`\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sourcemap", "tables"])
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--out")
    x = ap.parse_args()
    if x.mode == "sourcemap":
        sourcemap(x.a, x.b)
    else:
        tables(x.a, x.b, x.out)


if __name__ == "__main__":
    main()
