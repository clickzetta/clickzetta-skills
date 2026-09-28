#!/usr/bin/env python3
"""Derive an Apache Ossie ontology skeleton from a Core Spec semantic model.

Deterministic rules (same spirit as the OrionBelt converter):
  dataset                 -> EntityType concept (PascalCase of the dataset name)
  single-column PK        -> ValueType <Concept>Key + identifying OneToOne relationship
  composite PK            -> one identifying relationship per PK column (entity role when the
                             column is also a single-column FK, otherwise a ValueType role)
  relationship (FK)       -> ManyToOne relationship on the many-side concept
  dimension fields        -> ManyToOne attribute relationships to built-in value types (--attributes)
  PK / FK / field columns -> ontology_mappings (object_mappings + link_mappings)
  metrics                 -> stay in the embedded core model (not ontology concepts)

Everything that needs business judgement is left as a marked placeholder:
  verbalizes contains "TODO"  -> the agent drafts a natural phrase, a human confirms
  requires / derived_by       -> not generated; add business rules explicitly
validate_ossie.py warns on every remaining TODO.

Usage:
  python3 derive_ontology.py model.ossie.yaml -o model.ontology.yaml [--attributes] [--model NAME]
"""
from __future__ import annotations

import argparse
import copy
import sys

from czossie_common import OSSIE_VERSION, CliError, dump_yaml, load_yaml, pascal, run_cli

BUILTIN_FOR = {"String": "String", "Integer": "Integer", "Decimal": "Decimal", "Float": "Float",
               "Boolean": "Boolean", "Date": "Date", "DateTime": "DateTime", "DateTimeTz": "DateTime"}


def _models(doc) -> list[dict]:
    if isinstance(doc, dict) and isinstance(doc.get("semantic_model"), list):
        return doc["semantic_model"]
    if isinstance(doc, dict) and "datasets" in doc:
        return [doc]
    raise CliError("input is not an Ossie core semantic model file")


def ensure_key_fields(m: dict) -> list[str]:
    """Ontology mappings reference logical fields, so every PK/FK column must exist as a field."""
    added = []
    need: dict[str, set] = {}
    for d in m.get("datasets") or []:
        need.setdefault(d["name"], set()).update(d.get("primary_key") or [])
    for r in m.get("relationships") or []:
        need.setdefault(r["from"], set()).update(r["from_columns"])
        need.setdefault(r["to"], set()).update(r["to_columns"])
    for d in m.get("datasets") or []:
        have = {f["name"].lower() for f in d.get("fields") or []}
        for col in sorted(need.get(d["name"], ())):
            if col.lower() not in have:
                d.setdefault("fields", []).append({
                    "name": col, "expression": {"dialects": [{"dialect": "ANSI_SQL", "expression": f"{d['name']}.{col}"}]},
                    "dimension": {}, "description": f"Key column {col} (added for ontology mapping)"})
                added.append(f"{d['name']}.{col}")
    return added


def derive(m: dict, attributes: bool) -> dict:
    m = copy.deepcopy(m)
    added = ensure_key_fields(m)
    if added:
        print("info: added key fields to the embedded semantic model so mappings can reference them: "
              + ", ".join(added), file=sys.stderr)
    dss = m.get("datasets") or []
    concept = {d["name"]: pascal(d["name"]) for d in dss}
    fields = {d["name"]: {f["name"]: f for f in d.get("fields") or []} for d in dss}
    comps: list[dict] = []
    value_types: list[dict] = []
    ident: dict[str, dict] = {}     # dataset -> {"simple": col} or {"parts": [(rel, col, target_ds|None)]}
    fk_single: dict[tuple, str] = {}
    for r in m.get("relationships") or []:
        if len(r["from_columns"]) == 1:
            fk_single[(r["from"], r["from_columns"][0])] = r["to"]

    def vt_for(ds: str, col: str) -> str:
        f = fields[ds].get(col) or {}
        return BUILTIN_FOR.get(f.get("datatype"), "String")

    # ---- concepts with identifiers
    for d in dss:
        name, c = d["name"], concept[d["name"]]
        comp: dict = {"concept": c, "type": "EntityType"}
        if d.get("description"):
            comp["description"] = d["description"]
        rels: list[dict] = []
        pk = d.get("primary_key") or []
        if len(pk) == 1:
            key_vt = f"{c}Key"
            value_types.append({"concept": key_vt, "type": "ValueType",
                                "description": f"Identifier values of {c} (from {name}.{pk[0]})",
                                "extends": [vt_for(name, pk[0])]})
            rels.append({"name": pk[0], "roles": [{"concept": key_vt}], "multiplicity": "OneToOne",
                         "verbalizes": [f"{{{c}}} is identified by {{{key_vt}}}"]})
            comp["identify_by"] = [pk[0]]
            ident[name] = {"simple": pk[0]}
        elif len(pk) > 1:
            parts = []
            for col in pk:
                tgt = fk_single.get((name, col))
                role = concept[tgt] if tgt else vt_for(name, col)
                rels.append({"name": col, "roles": [{"concept": role}], "multiplicity": "ManyToOne",
                             "verbalizes": [f"{{{c}}} has {col.replace('_', ' ')} {{{role}}}"]})
                parts.append((col, col, tgt))
            comp["identify_by"] = list(pk)
            ident[name] = {"parts": parts}
        comp["relationships"] = rels
        comps.append(comp)

    by_concept = {x["concept"]: x for x in comps}
    # ---- FK relationships
    for r in m.get("relationships") or []:
        c_from, c_to = concept.get(r["from"]), concept.get(r["to"])
        if not c_from or not c_to:
            continue
        comp = by_concept[c_from]
        if r["from"] in ident and "parts" in ident[r["from"]] and \
                len(r["from_columns"]) == 1 and r["from_columns"][0] in (p[0] for p in ident[r["from"]]["parts"]):
            continue  # already an identifying relationship
        rname = r["to"] if r["to"] not in {x["name"] for x in comp["relationships"]} else r["name"]
        rel = {"name": rname, "roles": [{"concept": c_to}], "multiplicity": "ManyToOne",
               "verbalizes": [f"{{{c_from}}} TODO relates to {{{c_to}}}"]}
        if r.get("ai_context") and isinstance(r["ai_context"], dict) and r["ai_context"].get("instructions"):
            rel["description"] = r["ai_context"]["instructions"]
        rel["_fk"] = r
        comp["relationships"].append(rel)

    # ---- attribute relationships
    if attributes:
        for d in dss:
            comp = by_concept[concept[d["name"]]]
            used = {x["name"] for x in comp["relationships"]}
            fk_cols = {c for r in m.get("relationships") or [] if r["from"] == d["name"] for c in r["from_columns"]}
            for f in d.get("fields") or []:
                if "dimension" not in f or "added for ontology mapping" in f.get("description", "") \
                        or f["name"] in used or f["name"] in (d.get("primary_key") or []) \
                        or f["name"] in fk_cols:
                    continue
                vt = BUILTIN_FOR.get(f.get("datatype"), "String")
                rel = {"name": f["name"], "roles": [{"concept": vt}], "multiplicity": "ManyToOne",
                       "verbalizes": [f"{{{comp['concept']}}} has {f['name'].replace('_', ' ')} {{{vt}}}"]}
                if f.get("description"):
                    rel["description"] = f["description"]
                rel["_attr"] = f["name"]
                comp["relationships"].append(rel)

    # ---- mappings
    def obj_map(ds: str, cols: list[str], target: str) -> dict | None:
        """Object mapping that finds `target` dataset's entity from columns of `ds`."""
        idt = ident.get(target)
        if not idt:
            return None
        if "simple" in idt:
            return {"concept": concept[target], "expression": f"{ds}.{cols[0]}"}
        return {"concept": concept[target],
                "referent_mappings": [{"relationship": f"{concept[target]}.{p[0]}", "expression": f"{ds}.{c}"}
                                      for p, c in zip(idt["parts"], cols)]}

    cmaps = []
    for d in dss:
        name, c = d["name"], concept[d["name"]]
        idt = ident.get(name)
        if not idt:
            continue
        if "simple" in idt:
            root = {"expression": f"{name}.{idt['simple']}"}
        else:
            refs = []
            for rel, col, tgt in idt["parts"]:
                if tgt and "simple" in ident.get(tgt, {}):
                    refs.append({"relationship": rel, "referent_mappings": [
                        {"relationship": f"{concept[tgt]}.{ident[tgt]['simple']}", "expression": f"{name}.{col}"}]})
                else:
                    refs.append({"relationship": rel, "expression": f"{name}.{col}"})
            root = {"referent_mappings": refs}
        children = []
        for rel in by_concept[c]["relationships"]:
            if "_fk" in rel:
                om = obj_map(name, rel["_fk"]["from_columns"], rel["_fk"]["to"])
                if om:
                    children.append({"relationship": rel["name"], "object_mapping": om})
            elif "_attr" in rel:
                children.append({"relationship": rel["name"], "object_mapping": {
                    "concept": rel["roles"][0]["concept"], "expression": f"{name}.{rel['_attr']}"}})
        cm = {"concept": c, "object_mappings": [dict(root)]}
        if children:
            cm["link_mappings"] = [{"object_mapping": dict(root), "children": children}]
        cmaps.append(cm)
    for comp in comps:
        for rel in comp["relationships"]:
            rel.pop("_fk", None)
            rel.pop("_attr", None)
        if not comp["relationships"]:
            del comp["relationships"]

    out = {"version": OSSIE_VERSION, "name": f"{pascal(m['name'])}Ontology"}
    out["description"] = f"Ontology skeleton derived from semantic model '{m['name']}'. " \
                         "Review TODO verbalizations and add business rules (requires / derived_by)."
    out["ontology"] = value_types + comps
    out["ontology_mappings"] = [{"name": f"{m['name']}_mapping",
                                 "description": f"Maps semantic model '{m['name']}' to the ontology",
                                 "semantic_model": m, "concept_mappings": cmaps}]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ossie")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--model")
    ap.add_argument("--attributes", action="store_true", help="also map dimension fields to attribute relationships")
    a = ap.parse_args()
    models = _models(load_yaml(a.ossie))
    if a.model:
        models = [x for x in models if x.get("name") == a.model]
    if len(models) != 1:
        raise CliError("choose exactly one model with --model")
    out = derive(models[0], a.attributes)
    dump_yaml(out, a.output)
    todo = sum("TODO" in v for c in out["ontology"] for r in c.get("relationships", []) for v in r["verbalizes"])
    print(f"wrote {a.output}: {len(out['ontology'])} concepts, {todo} verbalization(s) marked TODO")
    sys.exit(0)


if __name__ == "__main__":
    run_cli(main)
