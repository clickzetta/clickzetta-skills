#!/usr/bin/env python3
"""Enrich the semantic model embedded in an Ossie ontology file, using the ontology itself.

Many Ossie files (e.g. apache/ossie examples/flights.yaml) carry the business structure in the
ontology layer only: the embedded semantic_model has no primary keys, no relationships, no
dimension blocks and no metrics. A ClickZetta semantic view needs all of those. This script reads
them off the ontology deterministically and writes a Core Spec file that ossie_to_sv.py can import:

  primary_key    <- the identifying expressions of each dataset's home concept
                    (object_mappings / referent_mappings; the home concept is the one whose
                    name matches the dataset, otherwise the one with most link mappings there)
  relationships  <- link_mappings children whose role concept is an EntityType identified
                    from another dataset (plus referent mappings nested in identifiers)
  field roles    <- the concept each field maps to: identifiers / FK columns / strings /
                    booleans -> dimension; Date / DateTime -> time dimension; numeric -> fact;
                    unmapped fields keep the Ossie default (fact) and are reported
  datatype       <- built-in type reached through the concept's `extends` chain
  metrics        <- `derived_by` rules of the form AGG[Concept.relationship ...]; a join path in
                    the rule (`WHERE X == Flight.route.departure`) becomes the metric's
                    custom_extensions[CLICKZETTA].using (ClickZetta metric USING clause)

Everything inferred is reported, so the agent can review it; judgement calls go in a review file:

  # review.yaml (all keys optional)
  dimensions:       [ROUTE.dist_grp]            # force dimension
  time_dimensions:  [FLIGHT.date]
  facts:            [AIRCRAFT.nr_seats]          # force fact
  primary_keys:     {RUNWAY: [airport_code, designator]}
  drop_relationships: [route_departure]
  metrics:
    - {name: flight_count, expression: "COUNT(FLIGHT.id)", description: "Number of flights",
       using: [flight_operated_by, route_departure]}
  using:            {avg_departure_delay: [flight_route, route_departure, flight_operated_by]}
  datatypes:        {FLIGHT.cancelled: Boolean}

Usage:
  python3 enrich_from_ontology.py flights.yaml -o flights.core.yaml [--review review.yaml] [--issues i.json]
"""
from __future__ import annotations

import argparse
import copy
import re
import sys

from czossie_common import OSSIE_VERSION, CliError, Issues, dump_yaml, get_ext, load_yaml, run_cli, set_ext

# What the Ossie schema allows inside a semantic_model. `version` is NOT among them: it belongs at
# the document root. Ontology files often nest it anyway (apache/ossie examples/flights.yaml has
# `ontology_mappings[0].semantic_model.version`), and copying it through makes the emitted core file
# fail validation with "Additional properties are not allowed ('version' was unexpected)".
MODEL_KEYS = frozenset({"name", "description", "ai_context", "datasets", "relationships",
                        "metrics", "custom_extensions"})

BUILTIN = {"Any", "Boolean", "Date", "DateTime", "Decimal", "Float", "Integer", "String"}
NUMERIC = {"Decimal", "Float", "Integer"}
REF_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*(?:WHERE\b(.*))?$", re.I | re.S)
AGG_RE = re.compile(r"\b(AVG|SUM|MIN|MAX|COUNT)\s*\[\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)", re.I)
PATH_RE = re.compile(r"==\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)")


class Enricher:
    def __init__(self, doc: dict, issues: Issues):
        self.doc, self.issues = doc, issues
        self.concepts = {c["concept"]: c for c in doc.get("ontology") or []}
        om = (doc.get("ontology_mappings") or [None])[0]
        if not om:
            raise CliError("no ontology_mappings in input; expected an Ossie ontology file")
        self.model = copy.deepcopy(om["semantic_model"])
        self.cmaps = om.get("concept_mappings") or []
        self.ds = {d["name"]: d for d in self.model.get("datasets") or []}
        self.fields = {d: {f["name"] for f in x.get("fields") or []} for d, x in self.ds.items()}
        self.ref_fields: set[tuple] = set()

    # ----------------------------------------------------------- concept helpers
    def builtin_of(self, concept: str | None, seen=None) -> str | None:
        if concept is None:
            return None
        if concept in BUILTIN:
            return concept
        seen = seen or set()
        if concept in seen or concept not in self.concepts:
            return None
        seen.add(concept)
        for e in self.concepts[concept].get("extends") or []:
            b = self.builtin_of(e, seen)
            if b:
                return b
        return None

    def rel_role(self, concept: str, rel: str) -> str | None:
        name = rel.split(".")[-1]
        owner = rel.split(".")[0] if "." in rel else concept
        for r in (self.concepts.get(owner) or {}).get("relationships") or []:
            if r.get("name") == name:
                roles = r.get("roles") or []
                return roles[-1].get("concept") if roles else None
        return None

    def ref(self, expr: str) -> tuple[str, str, str | None] | None:
        m = REF_RE.match(expr or "")
        if not m or m.group(1) not in self.ds:
            return None
        return m.group(1), m.group(2), (m.group(3) or "").strip() or None

    def leaves(self, concept: str, om: dict) -> list[tuple[str, str, str]]:
        """Flatten an object mapping to [(identifying_rel_path, dataset, field)]."""
        out = []
        if isinstance(om.get("expression"), str):
            r = self.ref(om["expression"])
            if r:
                out.append(("", r[0], r[1]))
        for rm in om.get("referent_mappings") or []:
            rel = rm.get("relationship")
            if isinstance(rm.get("expression"), str):
                r = self.ref(rm["expression"])
                if r and not r[2]:
                    out.append((rel, r[0], r[1]))
            if rm.get("referent_mappings"):
                sub = self.rel_role(concept, rel)
                for p, d, f in self.leaves(sub or concept, {"referent_mappings": rm["referent_mappings"]}):
                    out.append((f"{rel}.{p}" if p else rel, d, f))
        return out

    # ----------------------------------------------------------- inference
    def home_concepts(self) -> dict[str, str]:
        """dataset -> concept whose identity lives in that dataset."""
        candidates: dict[str, list[tuple[int, str]]] = {}
        for cm in self.cmaps:
            c = cm.get("concept")
            for om in cm.get("object_mappings") or []:
                dss = {d for _, d, _ in self.leaves(c, om)}
                if len(dss) == 1:
                    d = dss.pop()
                    n_links = sum(len(lm.get("children") or []) + 1 for lm in cm.get("link_mappings") or [])
                    candidates.setdefault(d, []).append((n_links, c))
        home = {}
        for d, cands in candidates.items():
            norm = lambda s: re.sub(r"[^a-z]", "", s.lower()).rstrip("s")
            named = [c for _, c in cands if norm(c) == norm(d)]
            home[d] = named[0] if named else max(cands)[1]
            if not named:
                self.issues.warn(f"home concept of {d} guessed as {home[d]} (no name match)", f"datasets.{d}")
        return home

    def run(self, review: dict) -> dict:
        home = self.home_concepts()
        concept_home = {c: d for d, c in home.items()}
        pk: dict[str, list[str]] = {}
        # --- primary keys from identifiers
        for cm in self.cmaps:
            c = cm.get("concept")
            if c not in concept_home:
                continue
            d = concept_home[c]
            for om in cm.get("object_mappings") or []:
                lv = [x for x in self.leaves(c, om) if x[1] == d]
                if lv:
                    ident = self.concepts.get(c, {}).get("identify_by") or []
                    order = {n: i for i, n in enumerate(ident)}
                    lv.sort(key=lambda x: order.get(x[0].split(".")[0], 99))
                    pk[d] = [self.column(d, f) for _, _, f in lv]
                    break
        for d, cols in (review.get("primary_keys") or {}).items():
            pk[d] = cols
            self.issues.info(f"primary key set by review: {cols}", f"datasets.{d}")
        for d, x in self.ds.items():
            if d in pk:
                x["primary_key"] = pk[d]
                self.issues.info(f"primary_key {pk[d]} from identifier of concept {home.get(d)}", f"datasets.{d}")
            else:
                self.issues.error("no identifying mapping found; add primary_keys in the review file", f"datasets.{d}")

        # --- field -> concept, relationships
        field_concept: dict[tuple, str] = {}
        key_fields: set[tuple] = set()
        rels, seen = [], set()

        def add_rel(src_ds: str, rel: str, target: str, cols_by_path: list[tuple[str, str]]):
            tgt_ds = concept_home.get(target)
            if not tgt_ds:
                self.issues.info(f"'{rel}' points to {target}, which has no dataset of its own - "
                                 "kept as attributes, no relationship", f"datasets.{src_ds}")
                return
            if tgt_ds == src_ds and not cols_by_path:
                return
            tgt_ident = self.concepts.get(target, {}).get("identify_by") or []
            order = {n: i for i, n in enumerate(tgt_ident)}
            cols_by_path.sort(key=lambda x: order.get(x[0].split(".")[0], 99))
            from_cols = [self.column(src_ds, f) for _, f in cols_by_path]
            to_cols = pk.get(tgt_ds) or []
            if len(from_cols) != len(to_cols):
                self.issues.warn(f"cannot align {from_cols} with key {to_cols} of {tgt_ds}; skipped", f"datasets.{src_ds}.{rel}")
                return
            name = f"{src_ds.lower()}_{rel.lower()}"
            key = (src_ds, tgt_ds, tuple(from_cols))
            if key in seen:
                return
            seen.add(key)
            rels.append({"name": name, "from": src_ds, "to": tgt_ds, "from_columns": from_cols, "to_columns": to_cols})
            for _, f in cols_by_path:
                key_fields.add((src_ds, f))

        for cm in self.cmaps:
            c = cm.get("concept")
            for om in cm.get("object_mappings") or []:
                for path, d, f in self.leaves(c, om):
                    key_fields.add((d, f))
                    if path:
                        # nested referent: identifying relationship to another entity (e.g. Runway.airport)
                        top = path.split(".")[0]
                        role = self.rel_role(c, top)
                        if role and self.concepts.get(role, {}).get("type") == "EntityType" and "." in path \
                                and concept_home.get(c) == d:
                            add_rel(d, top, role, [(path.split(".", 1)[1], f)])
            for lm in cm.get("link_mappings") or []:
                self.walk_links(c, lm, field_concept, add_rel)

        for r in rels:
            self.issues.info(f"relationship {r['from']}({', '.join(r['from_columns'])}) -> "
                             f"{r['to']}({', '.join(r['to_columns'])})", f"relationships.{r['name']}")
        drop = set(review.get("drop_relationships") or [])
        rels = [r for r in rels if r["name"] not in drop]
        by_target: dict[tuple, list] = {}
        for r in rels:
            by_target.setdefault((r["from"], r["to"]), []).append(r["name"])
        for (f, t), names in by_target.items():
            if len(names) > 1:
                self.issues.warn(f"{len(names)} relationships from {f} to {t} ({', '.join(names)}): role-playing "
                                 "joins; check that the target platform can tell them apart", "relationships")
        adj: dict[str, list] = {}
        for r in rels:
            adj.setdefault(r["from"], []).append((r["name"], r["to"]))

        def paths(a: str, seen: tuple) -> list[tuple]:
            out = []
            for name, b in adj.get(a, []):
                if b in seen:
                    continue
                out.append(((name,), b))
                out += [((name,) + p, e) for p, e in paths(b, seen + (b,))]
            return out

        for a in adj:
            ends: dict[str, list] = {}
            for p, e in paths(a, (a,)):
                ends.setdefault(e, []).append(" > ".join(p))
            for e, ps in ends.items():
                if len(ps) > 1 and len({x.split(" > ")[0] for x in ps}) > 1:
                    self.issues.warn(f"{a} reaches {e} along {len(ps)} join paths ({'; '.join(ps)}); results can "
                                     "differ by path unless the data keeps them consistent", "relationships")
        if rels:
            self.model["relationships"] = rels

        # --- field roles and datatypes
        forced_dim = set(review.get("dimensions") or [])
        forced_time = set(review.get("time_dimensions") or [])
        forced_fact = set(review.get("facts") or [])
        dtypes = review.get("datatypes") or {}
        for d, x in self.ds.items():
            for f in x.get("fields") or []:
                qn, k = f"{d}.{f['name']}", (d, f["name"])
                concept = field_concept.get(k)
                b = self.builtin_of(concept)
                if qn in dtypes:
                    b = dtypes[qn]
                elif b is None and (k in key_fields or k in self.ref_fields):
                    b = "String"
                if b and b != "Any":
                    f["datatype"] = b
                if qn in forced_fact:
                    role, why = "fact", "review"
                elif qn in forced_time:
                    role, why = "time", "review"
                elif qn in forced_dim:
                    role, why = "dimension", "review"
                elif k in key_fields:
                    role, why = "dimension", "identifier / foreign key"
                elif k in self.ref_fields:
                    role, why = "dimension", f"references entity via {concept}"
                elif b in ("Date", "DateTime"):
                    role, why = "time", f"maps to {concept} ({b})"
                elif b in NUMERIC:
                    role, why = "fact", f"maps to {concept} ({b})"
                elif b:
                    role, why = "dimension", f"maps to {concept} ({b})"
                else:
                    role, why = "fact", "not mapped by the ontology (Ossie default: no dimension block)"
                    self.issues.warn("field is not mapped by the ontology; left as fact - review its role", f"datasets.{qn}")
                f.pop("dimension", None)
                if role == "dimension":
                    f["dimension"] = {}
                elif role == "time":
                    f["dimension"] = {"is_time": True}
                self.issues.info(f"{role}: {why}", f"datasets.{qn}")

        # --- metrics from derived_by + review
        metrics, names = list(self.model.get("metrics") or []), {m["name"] for m in self.model.get("metrics") or []}
        for c in self.concepts.values():
            for r in c.get("relationships") or []:
                for rule in r.get("derived_by") or []:
                    for agg, cpt, rel in AGG_RE.findall(rule):
                        src = self.field_for(cpt, rel, field_concept, concept_home)
                        if not src:
                            self.issues.warn(f"derived_by '{rule}' uses {cpt}.{rel}, which maps to no field", f"ontology.{c['concept']}.{r['name']}")
                            continue
                        name = f"{agg.lower()}_{rel}"
                        if name in names:
                            continue
                        names.add(name)
                        m = {"name": name,
                             "expression": {"dialects": [{"dialect": "ANSI_SQL", "expression": f"{agg.upper()}({src[0]}.{src[1]})"}]},
                             "description": f"Derived from ontology rule on {c['concept']}.{r['name']}: {rule}"}
                        using = self.rule_path(rule, cpt, concept_home, rels)
                        set_ext(m, {"table": src[0], "using": using or None})
                        metrics.append(m)
                        self.issues.info(f"metric {name} = {agg.upper()}({src[0]}.{src[1]}) from derived_by", f"metrics.{name}")
        for m in review.get("metrics") or []:
            mm = {"name": m["name"], "expression": {"dialects": [{"dialect": "ANSI_SQL", "expression": m["expression"]}]}}
            if m.get("description"):
                mm["description"] = m["description"]
            set_ext(mm, {"table": m.get("table"), "using": m.get("using") or None})
            metrics.append(mm)
            self.issues.info("metric added by review", f"metrics.{m['name']}")
        known = {r["name"] for r in rels}
        for name, using in (review.get("using") or {}).items():
            for mm in metrics:
                if mm["name"] == name:
                    set_ext(mm, {**get_ext(mm), "using": list(using)})
                    self.issues.info(f"join path set by review: USING ({', '.join(using)})", f"metrics.{name}")
        for mm in metrics:
            using = get_ext(mm).get("using") or []
            gone = [u for u in using if u not in known]
            if gone:  # e.g. the relationship was dropped by the review
                self.issues.warn(f"USING {gone} not among the relationships; removed from the metric",
                                 f"metrics.{mm['name']}")
                set_ext(mm, {**get_ext(mm), "using": [u for u in using if u in known] or None})
        if metrics:
            self.model["metrics"] = metrics
        # hoist a version nested in the source model to the document root, where the schema wants it,
        # and keep anything else the schema rejects out of the emitted model
        version = self.doc.get("version") or self.model.get("version") or OSSIE_VERSION
        stray = sorted(set(self.model) - MODEL_KEYS)
        if stray:
            self.issues.info(f"moved out of semantic_model: {', '.join(stray)} "
                             f"(the Ossie schema only allows {', '.join(sorted(MODEL_KEYS))} there)",
                             "semantic_model")
        model = {k: v for k, v in self.model.items() if k in MODEL_KEYS}
        return {"version": version, "semantic_model": [model]}

    def rule_path(self, rule: str, concept: str, concept_home: dict, rels: list[dict]) -> list[str]:
        """`... WHERE Airport == Flight.route.departure ...` -> [flight_route, route_departure]."""
        by_name = {r["name"]: r for r in rels}
        for chain in PATH_RE.findall(rule):
            hops = chain.split(".")
            if hops[0] != concept or concept not in concept_home:
                continue
            ds, out = concept_home[concept], []
            for hop in hops[1:]:
                r = by_name.get(f"{ds.lower()}_{hop.lower()}")
                if not r:
                    self.issues.warn(f"join path '{chain}' in derived_by has no relationship for "
                                     f"'{ds}.{hop}'; metric left without USING", "metrics")
                    return []
                out.append(r["name"])
                ds = r["to"]
            return out
        return []

    def walk_links(self, concept: str, lm: dict, field_concept: dict, add_rel) -> None:
        om = lm.get("object_mapping") or {}
        for child in lm.get("children") or []:
            com = child.get("object_mapping") or {}
            target = com.get("concept")
            rel = child.get("relationship") or ""
            lv = self.leaves(target or concept, com)
            if target and self.concepts.get(target, {}).get("type") == "EntityType":
                src = {d for _, d, _ in lv}
                if len(src) == 1:
                    add_rel(src.pop(), rel, target, [(p, f) for p, _, f in lv])
                for p, d, f in lv:
                    # a reference to an entity is categorical: type it by the identifying value's concept
                    idc = self.rel_role(target, p.split(".")[0]) if p else None
                    if idc and self.concepts.get(idc, {}).get("type") == "EntityType" and "." in p:
                        idc = self.rel_role(idc, p.split(".")[-1])
                    field_concept.setdefault((d, f), idc or target)
                    self.ref_fields.add((d, f))
            else:
                role_c = target or self.rel_role(concept, rel)
                for _, d, f in lv:
                    field_concept.setdefault((d, f), role_c)
            self.walk_links(target or concept, child, field_concept, add_rel)
        # unary relationships filtered with WHERE <field> == TRUE  -> boolean flag fields
        for rm in om.get("referent_mappings") or []:
            r = self.ref(rm.get("expression") or "")
            if r and r[2]:
                m = re.search(r"([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*==?\s*TRUE", r[2], re.I)
                if m and m.group(1) in self.ds:
                    field_concept.setdefault((m.group(1), m.group(2)), "Boolean")

    def field_for(self, concept: str, rel: str, field_concept: dict, concept_home: dict):
        role = self.rel_role(concept, rel)
        d = concept_home.get(concept)
        for cm in self.cmaps:
            if cm.get("concept") != concept:
                continue
            for lm in cm.get("link_mappings") or []:
                for ch in lm.get("children") or []:
                    if ch.get("relationship") == rel:
                        lv = self.leaves(role or concept, ch.get("object_mapping") or {})
                        if lv:
                            return lv[0][1], lv[0][2]
        return None

    def column(self, d: str, field: str) -> str:
        for f in self.ds[d].get("fields") or []:
            if f["name"] == field:
                for dl in (f.get("expression") or {}).get("dialects") or []:
                    if re.match(r"^[A-Za-z_]\w*$", dl.get("expression", "").strip()):
                        return dl["expression"].strip()
        return field


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ontology")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--review", help="YAML with judgement calls (see docstring)")
    ap.add_argument("--issues")
    ap.add_argument("--quiet", action="store_true", help="only print warnings and errors")
    a = ap.parse_args()
    issues = Issues()
    doc = load_yaml(a.ontology)
    out = Enricher(doc, issues).run(load_yaml(a.review) if a.review else {})
    dump_yaml(out, a.output)
    if a.quiet:
        issues.items = [i for i in issues.items if i["severity"] != "info"]
    issues.report()
    issues.write_json(a.issues)
    m = out["semantic_model"][0]
    print(f"wrote {a.output}: {sum(1 for d in m['datasets'] if d.get('primary_key'))}/{len(m['datasets'])} datasets keyed, "
          f"{len(m.get('relationships', []))} relationships, {len(m.get('metrics', []))} metrics")
    sys.exit(1 if issues.has_errors else 0)


if __name__ == "__main__":
    run_cli(main)
