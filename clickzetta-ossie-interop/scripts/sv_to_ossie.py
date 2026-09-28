#!/usr/bin/env python3
"""Export: ClickZetta semantic view -> Apache Ossie Core Spec YAML.

Input is the JSON written by sv_dump.py (or, offline, a CREATE SEMANTIC VIEW file via --ddl).

Usage:
  python3 sv_to_ossie.py dump.json -o model.ossie.yaml [--issues issues.json]
  python3 sv_to_ossie.py --ddl view.sql -o model.ossie.yaml
  python3 sv_to_ossie.py dump.json -o out.yaml --spec-version 0.1.1   # e.g. for Snowflake import

Mapping (see references/mapping.md):
  logical table -> dataset          FACTS -> field (no dimension block)
  DIMENSIONS    -> field + dimension (is_time)
  METRICS       -> model-level metric (owning table kept in custom_extensions[CLICKZETTA].table)
  RELATIONSHIPS -> relationships    VARIABLES / PRIVATE / is_unique / enum_values / metric USING -> custom_extensions[CLICKZETTA]
  WITH SYNONYMS -> ai_context.synonyms, COMMENT -> description
Expressions are emitted as-is under the ANSI_SQL dialect (Ossie has no CLICKZETTA dialect).
If the view carries an Ossie sidecar (written by ossie_to_sv.py), Ossie-only metadata is restored.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from czossie_common import (OSSIE_VERSION, TEMPORAL, VENDOR, CliError, Issues, as_list, cz_to_ossie_type,
                            decode_sidecar, dump_yaml, get_ext, load_json_file, norm_expr, read_text,
                            run_cli, set_ext)
from sv_ddl import parse_ddl

DESC_META = {"synonyms", "is_unique", "is_time", "enum_values"}


def lk(*parts) -> str:
    return ".".join(str(p).lower() for p in parts if p is not None)


def parse_desc_extended(rows: list[dict]) -> dict[str, dict]:
    """Collect is_unique / is_time / enum_values / synonyms per dimension ("table.name", lower-case).

    Verified layout: a member row is (column_name="<table>.<name>", data_type=<expression>,
    comment=<comment>); each metadata line under it is (column_name="", data_type=<key>,
    comment=<value>), e.g. ("", "enum_values", "EAST,WEST") or ("", "is_time", "true").
    """
    meta: dict[str, dict] = {}
    section, current = "", None
    for r in rows:
        col = str(r.get("column_name") or r.get("col_name") or "").strip()
        low = col.lower()
        if col.startswith("#"):
            section, current = low.lstrip("# ").strip(), None
            continue
        if "dimension" not in section:
            continue
        if col:
            current = low
            continue
        key = str(r.get("data_type") or "").strip().lower()
        if key in DESC_META and current:
            meta.setdefault(current, {})[key] = r.get("comment")
    out: dict[str, dict] = {}
    for dim, m in meta.items():
        d: dict = {}
        for flag in ("is_unique", "is_time"):
            if flag in m:
                d[flag] = str(m[flag]).strip().lower() in ("true", "1", "yes")
        if "enum_values" in m:
            v = m["enum_values"]
            vals = v if isinstance(v, list) else as_list(str(v))
            # DESC shows "1,2,3" for numeric enums: give numbers back when every value is one
            if vals and all(re.fullmatch(r"-?(0|[1-9]\d*)(\.\d+)?", str(x)) for x in vals):
                vals = [float(x) if "." in str(x) else int(x) for x in vals]
            d["enum_values"] = vals
        if "synonyms" in m:
            d["synonyms"] = as_list(m["synonyms"])
        out[dim] = d
    return out


def build_ai_context(synonyms: list[str], stored: object | None, side: dict | None = None) -> object | None:
    as_written = (side or {}).get("synonyms_as_written")
    if as_written and sorted(x.lower() for x in as_written) == sorted(x.lower() for x in synonyms):
        synonyms = list(as_written)  # ClickZetta lower-cases and re-orders synonyms
    if isinstance(stored, dict):
        ctx = dict(stored)
        if synonyms:
            ctx["synonyms"] = synonyms
        else:
            ctx.pop("synonyms", None)
        return ctx or None
    if isinstance(stored, str) and stored:
        return {"instructions": stored, "synonyms": synonyms} if synonyms else stored
    return {"synonyms": synonyms} if synonyms else None


def restore_expression(current: str, side: dict | None, dialect: str, issues: Issues, path: str) -> dict:
    """Rebuild the dialects list, preferring the stored multi-dialect list when still valid."""
    if not side or not side.get("dialects"):
        return {"dialects": [{"dialect": dialect, "expression": current}]}
    stored = [dict(d) for d in side["dialects"]]
    if any(norm_expr(d["expression"]) == norm_expr(current) for d in stored) or \
            (side.get("used") and norm_expr(side["used"]) == norm_expr(current)):
        return {"dialects": stored}
    if side.get("used") and norm_expr(side["used"]) != norm_expr(current):
        issues.warn("expression changed in ClickZetta since import; emitted it as "
                    f"{dialect} and kept other stored dialects for review", path)
    rest = [d for d in stored if d["dialect"] != dialect]
    return {"dialects": [{"dialect": dialect, "expression": current}] + rest}


def convert(dump: dict, dialect: str, spec_version: str, issues: Issues) -> dict:
    ddl = parse_ddl(dump.get("ddl") or "")
    view = dump.get("view") or ddl.get("name") or "semantic_view"
    raw_text = json.dumps(dump.get("raw") or {}) + json.dumps(dump.get("desc_extended") or [])
    try:
        side = decode_sidecar(raw_text) or {}
    except ValueError as exc:
        issues.warn(f"ignoring Ossie sidecar: {exc}")
        side = {}
    if side:
        issues.info("Ossie sidecar found in view properties; restoring Ossie-only metadata")

    show = {k: {} for k in ("tables", "facts", "dimensions", "metrics")}
    for kind in ("facts", "dimensions", "metrics"):
        for r in dump.get(kind) or []:
            show[kind][lk(r.get("table_name"), r.get("name"))] = r
    for r in dump.get("tables") or []:
        show["tables"][lk(r.get("table_name"))] = r
    desc_meta = parse_desc_extended(dump.get("desc_extended") or [])

    # SHOW CREATE qualifies everything as workspace.schema.name
    name_parts = str(ddl.get("name") or "").split(".")
    ws = name_parts[0].lower() if len(name_parts) == 3 else None

    # ---- datasets
    datasets, ds_by_alias = [], {}
    tables = ddl["tables"] or [{"alias": r.get("table_name", "").lower(), "source": r.get("base_table"),
                                "primary_key": as_list(r.get("primary_key")), "synonyms": [], "comment": None}
                               for r in dump.get("tables") or []]
    for t in tables:
        alias = t["alias"]
        srow = show["tables"].get(lk(alias), {})
        sd = (side.get("datasets") or {}).get(alias.lower(), {})
        ds: dict = {"name": sd.get("name", alias)}
        cur_source = t["source"] or srow.get("base_table")
        # SHOW CREATE returns workspace.schema.table; the importer wrote schema.table
        used, cur = str(sd.get("source_used", "")).lower(), str(cur_source).lower()
        same = bool(used) and (used == cur or cur.endswith("." + used))
        if not same and ws and str(cur_source).lower().startswith(ws + ".") and str(cur_source).count(".") == 2:
            cur_source = str(cur_source)[len(ws) + 1:]  # drop the view's own workspace: schema.table
        ds["source"] = sd["source"] if sd.get("source") and same else cur_source
        pk = t["primary_key"] or as_list(srow.get("primary_key"))
        if pk and not sd.get("pk_inferred"):  # the importer derived it; the source had none
            ds["primary_key"] = pk
        if sd.get("unique_keys"):
            ds["unique_keys"] = sd["unique_keys"]
        comment = t.get("comment") or srow.get("comment")
        if comment:
            ds["description"] = comment
        ctx = build_ai_context(t["synonyms"] or as_list(srow.get("synonyms")), sd.get("ai_context"), sd)
        if ctx:
            ds["ai_context"] = ctx
        ds["fields"] = []
        if sd.get("custom_extensions"):
            ds["custom_extensions"] = sd["custom_extensions"]
        datasets.append(ds)
        ds_by_alias[alias.lower()] = ds

    def member_rows(kind: str) -> list[dict]:
        rows = list(ddl[kind])
        if not rows:  # no DDL: fall back to SHOW rows (expressions unknown)
            for r in dump.get(kind) or []:
                rows.append({"table": r.get("table_name"), "name": str(r.get("name")).lower(),
                             "expression": None, "private": str(r.get("access", "")).upper() == "PRIVATE"})
        return rows

    # ---- fields (facts, dimensions)
    for kind in ("facts", "dimensions"):
        for m in member_rows(kind):
            table = m.get("table") or show[kind].get(lk(None, m["name"]), {}).get("table_name")
            srow = show[kind].get(lk(table, m["name"]), {})
            if not table:
                table = srow.get("table_name")
            path = f"{kind}.{table}.{m['name']}"
            ds = ds_by_alias.get(str(table).lower())
            if ds is None:
                issues.error(f"{kind[:-1]} '{m['name']}' has no owning logical table", path)
                continue
            sf = (side.get("fields") or {}).get(lk(table, m["name"]), {})
            if m.get("expression") is None:
                issues.error("expression unavailable (SHOW CREATE output missing)", path)
                continue
            f: dict = {"name": sf.get("name", m["name"]),
                       "expression": restore_expression(m["expression"], sf, dialect, issues, path)}
            dm = desc_meta.get(lk(table, m["name"]), {})
            meta = {**dm, **{k: v for k, v in m.items() if k in DESC_META}}
            dtype, native = cz_to_ossie_type(srow.get("data_type"))
            dtype = sf.get("datatype", dtype)
            if kind == "dimensions":
                dim: dict = {}
                if meta.get("is_time"):
                    dim["is_time"] = True
                elif sf.get("is_time") is False:
                    dim["is_time"] = False
                f["dimension"] = dim
            if sf.get("label"):
                f["label"] = sf["label"]
            desc = m.get("comment") or srow.get("comment") or sf.get("description")
            if desc:
                f["description"] = desc
            if dtype:
                f["datatype"] = dtype
            syn = meta.get("synonyms") or as_list(srow.get("synonyms")) or sf.get("synonyms") or []
            ctx = build_ai_context(syn, sf.get("ai_context"), sf)
            if ctx:
                f["ai_context"] = ctx
            if sf.get("custom_extensions"):
                f["custom_extensions"] = sf["custom_extensions"]
            private = m.get("private") or str(srow.get("access", "")).upper() == "PRIVATE"
            set_ext(f, {"access": "PRIVATE" if private else None,
                        "is_unique": True if meta.get("is_unique") else None,
                        "enum_values": meta.get("enum_values") or None,
                        "native_type": native,
                        "kind": "fact_aggregate" if kind == "facts" and _is_aggregate(m["expression"]) else None})
            if kind == "facts" and _is_aggregate(m["expression"]):
                issues.info("aggregate FACT exported as a field; Ossie fields are row-level, so other "
                            "tools may not understand it (kept in custom_extensions[CLICKZETTA].kind)", path)
            ds["fields"].append(f)

    # ---- metrics (model level)
    metrics, seen = [], {}
    helpers = {h.lower() for h in side.get("helper_metrics") or []}
    for m in member_rows("metrics"):
        table = m.get("table")
        srow = show["metrics"].get(lk(table, m["name"]), {})
        table = table or srow.get("table_name")
        if lk(table, m["name"]) in helpers:
            continue  # PRIVATE per-table part generated by the importer; the original metric is restored
        path = f"metrics.{table}.{m['name']}"
        sm = (side.get("metrics") or {}).get(lk(table, m["name"]), {})
        name = sm.get("name", m["name"])
        if name.lower() in seen:
            issues.warn(f"metric name '{name}' is defined on several tables; renamed to "
                        f"'{str(table).lower()}_{name}' (original kept in custom_extensions)", path)
            name = f"{str(table).lower()}_{name}"
        seen[name.lower()] = True
        if m.get("expression") is None:
            issues.error("expression unavailable (SHOW CREATE output missing)", path)
            continue
        mt: dict = {"name": name,
                    "expression": restore_expression(m["expression"], sm, dialect, issues, path)}
        desc = m.get("comment") or srow.get("comment")
        if desc:
            mt["description"] = desc
        dtype, native = cz_to_ossie_type(srow.get("data_type"))
        dtype = sm.get("datatype", dtype)
        if dtype:
            mt["datatype"] = dtype
        ctx = build_ai_context(m.get("synonyms") or as_list(srow.get("synonyms")) or sm.get("synonyms") or [],
                               sm.get("ai_context"), sm)
        if ctx:
            mt["ai_context"] = ctx
        if sm.get("custom_extensions"):
            mt["custom_extensions"] = sm["custom_extensions"]
        private = m.get("private") or str(srow.get("access", "")).upper() == "PRIVATE"
        set_ext(mt, {"table": str(table).lower() if table else None,
                     "name": m["name"] if name != m["name"] else None,
                     "access": "PRIVATE" if private else None, "native_type": native,
                     "using": m.get("using") or None})
        metrics.append(mt)

    for mt in side.get("metrics_not_in_view") or []:
        issues.info(f"metric '{mt.get('name')}' restored from the sidecar; it is not part of the ClickZetta "
                    "view (window ordered by an aggregate/metric is not supported there)", "metrics")
        metrics.append(mt)

    # ---- relationships
    rels, show_rels = [], dump.get("relationships") or []
    for r in ddl["relationships"] or [{"name": x.get("relationship_name"), "from": x.get("table_name"),
                                       "from_columns": as_list(x.get("columns")), "to": x.get("ref_table_name"),
                                       "to_columns": as_list(x.get("ref_columns"))} for x in show_rels]:
        key = "|".join([r["from"].lower(), r["to"].lower(), ",".join(c.lower() for c in r["from_columns"])])
        sr = (side.get("relationships") or {}).get(key, {})
        name = sr.get("name") or r.get("name")
        to_cols = r["to_columns"]
        for x in show_rels:
            if str(x.get("table_name", "")).lower() == r["from"].lower() and \
               str(x.get("ref_table_name", "")).lower() == r["to"].lower() and \
               [c.lower() for c in as_list(x.get("columns"))] == [c.lower() for c in r["from_columns"]]:
                name = name or str(x.get("relationship_name") or "").lower() or None
                to_cols = to_cols or as_list(x.get("ref_columns"))
        if not to_cols:
            to_cols = ds_by_alias.get(r["to"].lower(), {}).get("primary_key", [])
        rel = {"name": name or f"{r['from'].lower()}_to_{r['to'].lower()}",
               "from": ds_by_alias.get(r["from"].lower(), {}).get("name", r["from"]),
               "to": ds_by_alias.get(r["to"].lower(), {}).get("name", r["to"]),
               "from_columns": r["from_columns"], "to_columns": to_cols}
        if sr.get("ai_context"):
            rel["ai_context"] = sr["ai_context"]
        if sr.get("custom_extensions"):
            rel["custom_extensions"] = sr["custom_extensions"]
        rels.append(rel)

    # ---- model
    sm_side = side.get("model") or {}
    model: dict = {"name": sm_side.get("name", view.split(".")[-1])}
    if ddl.get("comment"):
        model["description"] = ddl["comment"]
    if sm_side.get("ai_context"):
        model["ai_context"] = sm_side["ai_context"]
    for ds in datasets:
        if not ds["fields"]:
            del ds["fields"]
    model["datasets"] = datasets
    if rels:
        model["relationships"] = rels
    if metrics:
        model["metrics"] = metrics
    if sm_side.get("custom_extensions"):
        model["custom_extensions"] = sm_side["custom_extensions"]
    variables = []
    for v in ddl["variables"] or []:
        v = dict(v)
        v["type"] = str(v.get("type") or "").upper()
        if v.get("default") is not None:  # SHOW CREATE prints Java literals: 100.00BD, 5L
            v["default"] = re.sub(r"^(-?\d+(?:\.\d+)?)(?:BD|L|D|F|S|Y)$", r"\1", str(v["default"]).strip())
        variables.append(v)
    set_ext(model, {"view": view, "variables": variables or None})

    if spec_version != OSSIE_VERSION:
        _downgrade(model, spec_version, issues)
    return {"version": spec_version, "semantic_model": [model]}


def _is_aggregate(expr: str) -> bool:
    import re
    return bool(re.match(r"\s*(COUNT|SUM|AVG|MIN|MAX|APPROX_COUNT_DISTINCT|MEDIAN|STDDEV|VARIANCE)\s*\(", expr, re.I))


def _downgrade(model: dict, version: str, issues: Issues) -> None:
    """0.1.1 predates `datatype`; strip it so strict 0.1.1 consumers accept the file."""
    n = 0
    for ds in model["datasets"]:
        for f in ds.get("fields", []):
            n += f.pop("datatype", None) is not None
    for m in model.get("metrics", []):
        n += m.pop("datatype", None) is not None
    if n:
        issues.info(f"spec {version}: removed {n} 'datatype' attributes (introduced after 0.1.1)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dump", nargs="?", help="JSON from sv_dump.py")
    ap.add_argument("--ddl", help="CREATE SEMANTIC VIEW text file (offline mode)")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--dialect", default="ANSI_SQL", help="dialect label for emitted expressions")
    ap.add_argument("--spec-version", default=OSSIE_VERSION, choices=[OSSIE_VERSION, "0.1.1"])
    ap.add_argument("--issues", help="write issues as JSON")
    a = ap.parse_args()
    if not a.dump and not a.ddl:
        ap.error("give a dump file or --ddl")
    dump = load_json_file(a.dump) if a.dump else {}
    if a.ddl:
        dump["ddl"] = read_text(a.ddl)
    if not isinstance(dump, dict):
        raise CliError(f"{a.dump} is not a dump object; expected the JSON written by sv_dump.py")
    ddl_text = dump.get("ddl") or ""
    if not ddl_text.strip():
        src = a.dump or a.ddl
        raise CliError(f"{src} carries no CREATE SEMANTIC VIEW statement (no usable 'ddl'); "
                       f"re-run sv_dump.py against the view")
    issues = Issues()
    doc = convert(dump, a.dialect, a.spec_version, issues)
    dump_yaml(doc, a.output)
    issues.report()
    issues.write_json(a.issues)
    m = doc["semantic_model"][0]
    print(f"wrote {a.output}: {len(m['datasets'])} datasets, "
          f"{sum(len(d.get('fields', [])) for d in m['datasets'])} fields, "
          f"{len(m.get('relationships', []))} relationships, {len(m.get('metrics', []))} metrics")
    sys.exit(1 if issues.has_errors else 0)


if __name__ == "__main__":
    run_cli(main)
