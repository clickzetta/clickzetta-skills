#!/usr/bin/env python3
"""Semantic diff of two Ossie Core Spec files (round-trip check).

Compares what matters, not formatting: datasets (source, keys, description, synonyms), fields
(role, effective is_time, expressions per dialect, description, datatype, label, synonyms),
metrics, relationships and model-level text. Expressions are compared whitespace-, case- and
backtick-insensitively. custom_extensions are compared per vendor, except bookkeeping keys that
this skill writes itself (CLICKZETTA: view, native_type, table, name, kind).

Usage:
  python3 ossie_diff.py original.yaml roundtrip.yaml [--ignore datatype,source] [--json]
Exit 0 when equivalent, 1 when differences were found.
"""
from __future__ import annotations

import argparse
import json
import sys

from czossie_common import TEMPORAL, CliError, iter_dialects, load_yaml, norm_expr, run_cli

BOOKKEEPING = {"CLICKZETTA": {"view", "native_type", "table", "name", "kind"}}


def _models(doc) -> dict[str, dict]:
    if isinstance(doc, dict) and isinstance(doc.get("semantic_model"), list):
        ms = doc["semantic_model"]
    elif isinstance(doc, dict) and "datasets" in doc:
        ms = [doc]
    else:
        ms = []
    return {m.get("name", "").lower(): m for m in ms}


def _syn(obj: dict) -> list:
    ctx = obj.get("ai_context")
    return sorted(ctx.get("synonyms") or []) if isinstance(ctx, dict) else []


def _ctx_rest(obj: dict):
    ctx = obj.get("ai_context")
    if isinstance(ctx, dict):
        return {k: v for k, v in ctx.items() if k != "synonyms"} or None
    return ctx or None


def _exts(obj: dict) -> dict:
    out = {}
    for e in obj.get("custom_extensions") or []:
        v = str(e.get("vendor_name", "")).upper()
        try:
            data = json.loads(e.get("data") or "{}")
        except json.JSONDecodeError:
            data = e.get("data")
        if isinstance(data, dict):
            data = {k: x for k, x in data.items() if k not in BOOKKEEPING.get(v, set())}
        if data:
            out[v] = data
    return out


def _expr(obj: dict) -> list:
    return sorted((d, norm_expr(e)) for d, e in iter_dialects(obj.get("expression")))


def _field(f: dict) -> dict:
    dim = f.get("dimension")
    is_time = None
    if dim is not None:
        is_time = dim.get("is_time")
        if is_time is None:
            is_time = f.get("datatype") in TEMPORAL
    return {"role": "dimension" if dim is not None else "fact", "is_time": is_time,
            "expression": _expr(f), "description": f.get("description"), "datatype": f.get("datatype"),
            "label": f.get("label"), "synonyms": _syn(f), "ai_context": _ctx_rest(f), "extensions": _exts(f)}


def norm(m: dict, ignore: set) -> dict:
    out = {"description": m.get("description"), "ai_context": _ctx_rest(m), "extensions": _exts(m),
           "datasets": {}, "metrics": {}, "relationships": {}}
    for d in m.get("datasets") or []:
        src = str(d.get("source", "")).lower()
        if "source" in ignore:
            src = src.split(".")[-1]
        out["datasets"][d["name"].lower()] = {
            "source": src, "primary_key": [c.lower() for c in d.get("primary_key") or []],
            "unique_keys": d.get("unique_keys"), "description": d.get("description"), "synonyms": _syn(d),
            "ai_context": _ctx_rest(d), "extensions": _exts(d),
            "fields": {f["name"].lower(): _field(f) for f in d.get("fields") or []}}
    for x in m.get("metrics") or []:
        out["metrics"][x["name"].lower()] = {
            "expression": _expr(x), "description": x.get("description"), "datatype": x.get("datatype"),
            "synonyms": _syn(x), "ai_context": _ctx_rest(x), "extensions": _exts(x)}
    for r in m.get("relationships") or []:
        key = "|".join([r["from"].lower(), r["to"].lower(), ",".join(c.lower() for c in r["from_columns"])])
        out["relationships"][key] = {"name": r.get("name"), "to_columns": [c.lower() for c in r["to_columns"]],
                                     "ai_context": _ctx_rest(r), "extensions": _exts(r)}
    if ignore:
        _drop(out, ignore - {"source"})
    return out


def _drop(node, keys: set) -> None:
    if isinstance(node, dict):
        for k in list(node):
            if k in keys:
                del node[k]
            else:
                _drop(node[k], keys)


def diff(a, b, path: str = "") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f"{path}.{k}" if path else k
            if k not in a:
                out.append(f"+ {p}: {json.dumps(b[k], ensure_ascii=False)[:200]}")
            elif k not in b:
                out.append(f"- {p}: {json.dumps(a[k], ensure_ascii=False)[:200]}")
            else:
                out.extend(diff(a[k], b[k], p))
        return out
    if a != b:
        return [f"~ {path}: {json.dumps(a, ensure_ascii=False)[:200]} -> {json.dumps(b, ensure_ascii=False)[:200]}"]
    return []


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--ignore", default="", help="comma list of keys to ignore (e.g. datatype,source,label)")
    ap.add_argument("--json", action="store_true")
    x = ap.parse_args()
    ignore = {k.strip() for k in x.ignore.split(",") if k.strip()}
    ma, mb = _models(load_yaml(x.a)), _models(load_yaml(x.b))
    # Two files that hold no model at all would compare as EQUIVALENT, which is the one answer a
    # round-trip check must never give by accident: it would stay green if an export ever produced
    # an empty model. Refuse instead.
    for path, models in ((x.a, ma), (x.b, mb)):
        if not models:
            raise CliError(f"{path} holds no semantic model to compare; expected an Ossie file with "
                           f"a non-empty semantic_model (run validate_ossie.py to inspect it)")
    if len(ma) == 1 and len(mb) == 1:  # a round trip may rename the model; compare the single models
        ma, mb = {"model": next(iter(ma.values()))}, {"model": next(iter(mb.values()))}
    out = diff({k: norm(v, ignore) for k, v in ma.items()}, {k: norm(v, ignore) for k, v in mb.items()})
    if x.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print("\n".join(out) if out else "EQUIVALENT")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    run_cli(main)
