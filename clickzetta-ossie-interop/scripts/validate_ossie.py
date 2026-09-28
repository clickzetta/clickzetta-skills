#!/usr/bin/env python3
"""Validate an Apache Ossie file: Core Spec semantic model or ontology (auto-detected).

Checks
  core:      JSON Schema (vendored schemas/ossie-schema.json), unique names, relationship
             dataset references and column arity, to_columns covers a key, metric/field
             expressions reference known datasets, optional SQL parse with sqlglot.
  ontology:  JSON Schema (schemas/ontology.json, core schema registered locally), plus the
             embedded semantic models, concept references (roles / extends / identify_by /
             mapping concepts), verbalizes placeholders, and dataset.field references in
             mapping expressions.

Usage:
  python3 validate_ossie.py FILE [--strict] [--json]
Exit code 0 = valid (warnings allowed unless --strict), 1 = invalid, 2 = cannot run.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys

from czossie_common import OSSIE_VERSION, Issues, iter_dialects, load_yaml, run_cli

HERE = os.path.dirname(os.path.abspath(__file__))
CORE_ID = "https://raw.githubusercontent.com/apache/ossie/main/core-spec/ossie-schema.json"
BUILTINS = {"Any", "Boolean", "Date", "DateTime", "Decimal", "Float", "Integer", "String"}


def _schema(name: str) -> dict:
    with open(os.path.join(HERE, "schemas", name), encoding="utf-8") as fh:
        return json.load(fh)


def schema_errors(doc: dict, kind: str, issues: Issues) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        issues.warn("jsonschema not installed - schema check skipped (python3 -m pip install jsonschema)")
        return
    core = _schema("ossie-schema.json")
    main = core if kind == "core" else _schema("ontology.json")
    version = str(doc.get("version", ""))
    if version == "0.1.1":
        # released 0.1.1 lacks later additions only; accept its version string
        issues.info("version 0.1.1 checked against the 0.2.0.dev0 schema with the version relaxed")
        main = copy.deepcopy(main)
        main["properties"]["version"] = {"type": "string", "enum": ["0.1.1", OSSIE_VERSION]}
    kwargs = {}
    if kind == "ontology":
        try:
            from referencing import Registry, Resource
            res = Resource.from_contents(core)
            kwargs["registry"] = Registry().with_resources([(CORE_ID, res), (core["$id"], res)])
        except ImportError:  # jsonschema < 4.18
            from jsonschema import RefResolver
            kwargs["resolver"] = RefResolver.from_schema(main, store={CORE_ID: core, core["$id"]: core})
    v = Draft202012Validator(main, **kwargs)
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in e.absolute_path) or "(root)"
        issues.error(f"schema: {e.message[:300]}", path)


def check_model(m: dict, base: str, issues: Issues, sql: bool) -> dict[str, set]:
    """Semantic checks for one SemanticModel. Returns {dataset: {field names}}."""
    fields: dict[str, set] = {}

    def dup(names: list, what: str, path: str) -> None:
        seen = set()
        for n in names:
            if n in seen:
                issues.error(f"duplicate {what} name '{n}'", path)
            seen.add(n)

    dss = m.get("datasets") or []
    dup([d.get("name") for d in dss], "dataset", base)
    for d in dss:
        fields[d.get("name")] = {f.get("name") for f in d.get("fields") or []}
        dup([f.get("name") for f in d.get("fields") or []], "field", f"{base}.{d.get('name')}")
    dup([x.get("name") for x in m.get("metrics") or []], "metric", base)
    dup([x.get("name") for x in m.get("relationships") or []], "relationship", base)
    by_name = {d.get("name"): d for d in dss}
    for r in m.get("relationships") or []:
        p = f"{base}.relationships.{r.get('name')}"
        for side in ("from", "to"):
            if r.get(side) not in by_name:
                issues.error(f"'{side}' references unknown dataset '{r.get(side)}'", p)
        fc, tc = r.get("from_columns") or [], r.get("to_columns") or []
        if len(fc) != len(tc):
            issues.error(f"from_columns ({len(fc)}) and to_columns ({len(tc)}) differ in length", p)
        tgt = by_name.get(r.get("to"))
        if tgt and tc:
            keys = [k for k in [tgt.get("primary_key")] + list(tgt.get("unique_keys") or []) if k]
            if keys and not any(set(k) <= set(tc) for k in keys):
                issues.warn(f"to_columns {tc} do not cover a key of '{r.get('to')}'", p)
    ds_names = set(by_name)
    for mt in m.get("metrics") or []:
        p = f"{base}.metrics.{mt.get('name')}"
        for dialect, expr in iter_dialects(mt.get("expression")):
            for q in re.findall(r"(?<![\w.'\"])([A-Za-z_]\w*)\s*\.\s*[A-Za-z_]", _strip_strings(expr)):
                if q not in ds_names and q.lower() not in {x.lower() for x in ds_names}:
                    issues.warn(f"{dialect} expression qualifies unknown dataset '{q}'", p)
    if sql:
        _sql_checks(m, base, issues)
    return fields


def _strip_strings(s: str) -> str:
    return re.sub(r"'(?:[^'\\]|\\.|'')*'", "''", s)


def _sql_checks(m: dict, base: str, issues: Issues) -> None:
    try:
        import sqlglot
    except ImportError:
        issues.info("sqlglot not installed - SQL parse check skipped")
        return
    dmap = {"ANSI_SQL": None, "SNOWFLAKE": "snowflake", "DATABRICKS": "databricks", "BIGQUERY": "bigquery"}
    items = [(f"{base}.{d.get('name')}.{f.get('name')}", f) for d in m.get("datasets") or []
             for f in d.get("fields") or []] + [(f"{base}.metrics.{x.get('name')}", x) for x in m.get("metrics") or []]
    for p, obj in items:
        for dialect, expr in iter_dialects(obj.get("expression")):
            if dialect not in dmap:
                continue
            try:
                sqlglot.parse_one(f"SELECT {expr}", dialect=dmap[dialect])
            except Exception as exc:  # noqa: BLE001 - report any parser failure as a warning
                issues.warn(f"{dialect} expression did not parse with sqlglot: {str(exc).splitlines()[0][:160]}", p)


def check_ontology(doc: dict, issues: Issues, sql: bool) -> None:
    comps = doc.get("ontology") or []
    concepts = {c.get("concept") for c in comps}
    for c in comps:
        if c.get("concept") in BUILTINS:
            issues.error(f"concept '{c['concept']}' redefines a built-in concept", f"ontology.{c['concept']}")
    known = concepts | BUILTINS
    rel_names: dict[str, set] = {}
    for c in comps:
        cn, p = c.get("concept"), f"ontology.{c.get('concept')}"
        for e in c.get("extends") or []:
            if e not in known:
                issues.error(f"extends unknown concept '{e}'", p)
        if c.get("type") == "ValueType" and not c.get("extends"):
            issues.warn("value type should extend a built-in value type (directly or indirectly)", p)
        rels = c.get("relationships") or []
        rel_names[cn] = {r.get("name") for r in rels}
        for r in rels:
            rp = f"{p}.{r.get('name')}"
            role_concepts = [cn] + [ro.get("concept") for ro in r.get("roles") or []]
            for rc in role_concepts[1:]:
                if rc not in known:
                    issues.error(f"role concept '{rc}' is not defined", rp)
            for vb in r.get("verbalizes") or []:
                for ph in re.findall(r"\{([^}]+)\}", vb):
                    if ph not in role_concepts and ph.split(":")[0] not in role_concepts:
                        issues.warn(f"verbalization placeholder '{{{ph}}}' is not a role of this relationship", rp)
                if "TODO" in vb:
                    issues.warn("verbalization still contains TODO - needs a human/agent-written phrase", rp)
        for idr in c.get("identify_by") or []:
            if idr not in rel_names[cn]:
                issues.error(f"identify_by names unknown relationship '{idr}'", p)
    for i, om in enumerate(doc.get("ontology_mappings") or []):
        base = f"ontology_mappings[{i}]"
        model = om.get("semantic_model") or {}
        fields = check_model(model, base + ".semantic_model", issues, sql)
        for cm in om.get("concept_mappings") or []:
            cp = f"{base}.{cm.get('concept')}"
            if cm.get("concept") not in concepts:
                issues.error(f"concept mapping for undefined concept '{cm.get('concept')}'", cp)
            for expr, path in _mapping_exprs(cm, cp):
                for ds, fld in re.findall(r"(?<![\w.])([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)", _strip_strings(expr)):
                    if ds in fields and fld not in fields[ds]:
                        issues.error(f"'{ds}.{fld}' is not a field of dataset '{ds}'", path)
                    elif ds not in fields and ds not in concepts:
                        issues.warn(f"expression qualifies unknown dataset '{ds}'", path)


def _mapping_exprs(node, path):
    if isinstance(node, dict):
        if isinstance(node.get("expression"), str):
            yield node["expression"], path
        for k, v in node.items():
            if k != "expression":
                yield from _mapping_exprs(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _mapping_exprs(v, f"{path}[{i}]")


def validate(doc, sql: bool = True) -> Issues:
    issues = Issues()
    if not isinstance(doc, dict):
        issues.error("top level must be a mapping")
        return issues
    kind = "ontology" if "ontology" in doc or "ontology_mappings" in doc else "core"
    issues.info(f"detected {kind} document")
    schema_errors(doc, kind, issues)
    if kind == "core":
        for m in doc.get("semantic_model") or []:
            check_model(m, f"semantic_model.{m.get('name')}", issues, sql)
    else:
        check_ontology(doc, issues, sql)
    return issues


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--no-sql", action="store_true", help="skip the sqlglot parse check")
    ap.add_argument("--json", action="store_true", help="print issues as JSON")
    a = ap.parse_args()
    issues = validate(load_yaml(a.file), sql=not a.no_sql)
    if a.json:
        print(json.dumps(issues.items, indent=2, ensure_ascii=False))
    else:
        issues.report(sys.stdout)
    bad = issues.has_errors or (a.strict and any(i["severity"] == "warning" for i in issues.items))
    print(f"{'INVALID' if bad else 'VALID'}: {a.file}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    run_cli(main)
