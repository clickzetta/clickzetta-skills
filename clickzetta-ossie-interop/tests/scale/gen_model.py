#!/usr/bin/env python3
"""Generate a synthetic Ossie Core Spec model of a chosen size, for the scale test.

The shape is a chain: `ds_0` is the root and `ds_i` carries a foreign key to `ds_{i-1}`, so the
relationship chain is as deep as the model is wide and the importer has to resolve multi-hop joins
rather than one hop from a hub. Every dataset carries `--fields` fields (a mix of dimensions, one
time dimension, and numeric facts) and the metrics are spread across them.

    gen_model.py --datasets 50 --fields 20 --metrics 50 -o big.ossie.yaml
    gen_model.py --datasets 20 --metrics 5 --multitable 5 -o mixed.ossie.yaml

`--multitable R` makes R of the metrics span two datasets. Those are the expensive ones: the
importer splits each into two PRIVATE per-table metrics plus a view-scoped derived metric, and the
sidecar grows accordingly. Keep it low unless the split itself is what you are measuring.

Everything is written as ANSI_SQL, so the model imports without --overrides.
"""

from __future__ import annotations

import argparse
import json
import sys

VERSION = "0.2.0.dev0"


def build(datasets: int, fields: int, metrics: int, multitable: int, source_prefix: str) -> dict:
    if fields < 2:
        raise SystemExit("--fields must be at least 2 (a key and something to aggregate)")

    model: dict = {"name": "SCALE_MODEL", "datasets": [], "relationships": [], "metrics": []}

    for i in range(datasets):
        ds_name = f"ds_{i}"
        key = f"id_{i}"
        ds: dict = {
            "name": ds_name,
            "source": f"{source_prefix}.PUBLIC.T_{i:04d}",
            "primary_key": [key],
            "description": f"Synthetic dataset {i}",
            "fields": [],
        }
        # the key itself, as a dimension
        ds["fields"].append(field(key, f"{ds_name}.{key}", dimension=True))
        # a time dimension every few datasets, to exercise is_time
        if i % 4 == 0:
            ds["fields"].append(field(f"ts_{i}", f"DATE_TRUNC('DAY', {ds_name}.ts_{i})",
                                      dimension=True, is_time=True))
        # dimensions
        n_dim = max(0, (fields - 2) // 2)
        for j in range(n_dim):
            ds["fields"].append(field(f"{ds_name}_attr_{j}", f"{ds_name}.attr_{j}", dimension=True))
        # numeric facts, always at least one so a metric can exist
        n_fact = max(1, fields - 2 - n_dim)
        for j in range(n_fact):
            ds["fields"].append(field(f"{ds_name}_amount_{j}", f"{ds_name}.amount_{j}"))
        model["datasets"].append(ds)

        if i > 0:  # chain ds_i -> ds_{i-1}
            model["relationships"].append({
                "name": f"{ds_name}_to_ds_{i - 1}",
                "from": ds_name,
                "to": f"ds_{i - 1}",
                "from_columns": [f"parent_{i}"],
                "to_columns": [f"id_{i - 1}"],
            })
            # the FK column has to exist in the parent's child table to be referenceable
            model["datasets"][i]["fields"].append(
                field(f"parent_{i}", f"{ds_name}.parent_{i}", dimension=True))

    # metrics: single-table ones first, then the multi-table split
    single = max(0, metrics - multitable)
    for k in range(single):
        d = model["datasets"][k % datasets]
        j = k % max(1, sum(1 for f in d["fields"] if "_amount_" in f["name"]))
        model["metrics"].append({
            "name": f"metric_{k}",
            "expression": ansi(f"SUM({d['name']}.amount_{j})"),
            "description": f"Single-table metric {k}",
        })
    for r in range(multitable):
        a = model["datasets"][r % datasets]
        b = model["datasets"][(r + 1) % datasets]
        model["metrics"].append({
            "name": f"multi_metric_{r}",
            "expression": ansi(f"SUM({a['name']}.amount_0) / COUNT(DISTINCT {b['name']}.id_{(r + 1) % datasets})"),
            "description": f"Metric spanning {a['name']} and {b['name']}",
        })
    return {"version": VERSION, "semantic_model": [model]}


def ansi(expression: str) -> dict:
    return {"dialects": [{"dialect": "ANSI_SQL", "expression": expression}]}


def field(name: str, expression: str, dimension: bool = False, is_time: bool = False) -> dict:
    f: dict = {"name": name, "expression": ansi(expression)}
    if dimension:
        f["dimension"] = {"is_time": True} if is_time else {}
    return f


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", type=int, default=10)
    ap.add_argument("--fields", type=int, default=10)
    ap.add_argument("--metrics", type=int, default=10)
    ap.add_argument("--multitable", type=int, default=0)
    ap.add_argument("--source-prefix", default="SCALE_DB")
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args()
    doc = build(a.datasets, a.fields, a.metrics, a.multitable, a.source_prefix)
    try:
        import yaml
    except ImportError:
        sys.stderr.write("PyYAML is required: python3 -m pip install pyyaml\n")
        raise SystemExit(2)
    with open(a.output, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=1000)
    m = doc["semantic_model"][0]
    print(json.dumps({"datasets": len(m["datasets"]),
                      "fields": sum(len(d["fields"]) for d in m["datasets"]),
                      "relationships": len(m["relationships"]),
                      "metrics": len(m["metrics"])}))


if __name__ == "__main__":
    main()
