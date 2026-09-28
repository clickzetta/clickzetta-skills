#!/usr/bin/env python3
"""Import: Apache Ossie Core Spec YAML -> ClickZetta CREATE OR REPLACE SEMANTIC VIEW DDL.

Accepts Ossie files written by any tool, including Snowflake's
SYSTEM$READ_OSSIE_YAML_FROM_SEMANTIC_VIEW output and this skill's own export.

Usage:
  python3 ossie_to_sv.py model.yaml --view my_schema.my_view -o create.sql [--issues issues.json]
  python3 ossie_to_sv.py model.yaml --view s.v --model orders_model \
      --source-map "SALES_DB.PUBLIC=my_schema" --overrides overrides.yaml -o create.sql

Options worth knowing:
  --prefer-dialect  order used to pick an expression (default ANSI_SQL,SNOWFLAKE,DATABRICKS,BIGQUERY).
                    Non-ANSI picks are reported so the agent can review/rewrite them.
  --source-map      rewrite dataset.source prefixes (case-insensitive, repeatable) before use.
  --overrides       YAML {path: replacement} for expressions/sources the agent rewrote, e.g.
                      datasets.orders.fields.order_month: "DATE_TRUNC('MONTH', orders.order_date)"
                      metrics.total_revenue: "SUM(orders.amount)"
                      datasets.orders.source: "my_schema.orders"
  --no-sidecar      do not emit the ALTER ... SET PROPERTIES that preserves Ossie-only metadata.

Exit code 1 when any error-level issue was found (the DDL is still written for inspection).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict

from czossie_common import (TEMPORAL, VENDOR, CliError, Issues, encode_sidecar, get_ext, ident, iter_dialects,
                            load_yaml, matching_paren, norm_expr, other_exts, qualify_columns, quote_bare,
                            run_cli, snake, sql_str)

DEFAULT_PREF = ["ANSI_SQL", "SNOWFLAKE", "DATABRICKS", "BIGQUERY"]


def pick_models(doc) -> list[dict]:
    if isinstance(doc, list):
        return [m for m in doc if isinstance(m, dict)]
    if isinstance(doc, dict):
        if isinstance(doc.get("semantic_model"), list):
            return doc["semantic_model"]
        if isinstance(doc.get("semantic_model"), dict):
            return [doc["semantic_model"]]
        if "datasets" in doc:
            return [doc]
        if isinstance(doc.get("ontology_mappings"), list):  # an ontology file: use embedded models
            return [om["semantic_model"] for om in doc["ontology_mappings"] if om.get("semantic_model")]
    raise CliError("no semantic_model found in input; expected an Ossie file with a "
                   "semantic_model, a datasets key, or ontology_mappings")


class Importer:
    def __init__(self, model: dict, view: str, pref: list[str], source_map: list[tuple[str, str]],
                 overrides: dict, issues: Issues):
        self.m, self.view, self.pref, self.smap, self.ovr, self.issues = model, view, pref, source_map, overrides, issues
        self.schema = view.split(".")[0] if "." in view else None
        self.side: dict = {"model": {}, "datasets": {}, "fields": {}, "metrics": {}, "relationships": {}}
        self.alias: dict[str, str] = {}   # ossie dataset name (lower) -> cz alias

    # ------------------------------------------------------------ helpers
    def name_of(self, name: str, path: str) -> str:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            return name
        new = snake(name)
        self.issues.warn(f"name '{name}' is not a plain identifier; using '{new}' "
                         "(original kept in sidecar). Expressions referring to the old name must be fixed", path)
        return new

    def expr(self, obj: dict, path: str, side: dict) -> str | None:
        if path in self.ovr:
            used = str(self.ovr[path])
            side["used"] = used
            side["dialects"] = [{"dialect": d, "expression": e} for d, e in iter_dialects(obj.get("expression"))]
            self.issues.info("expression taken from --overrides", path)
            return used
        avail = dict(iter_dialects(obj.get("expression")))
        for d in self.pref:
            if d in avail:
                if d != "ANSI_SQL" and re.search(r"\w\s*\(|::|\bIFF\b", avail[d], re.I):
                    self.issues.info(f"using {d} expression verbatim: `{avail[d]}` - review ClickZetta "
                                     "compatibility (see clickzetta-sql-migration) and supply --overrides "
                                     "if it needs rewriting", path)
                # always kept: ClickZetta rewrites expressions when it stores them (`||` -> concat,
                # ORDER BY x -> x ASC, `count`(...)), so export needs the as-written text
                side["dialects"] = [{"dialect": k, "expression": v} for k, v in avail.items()]
                side["used"] = avail[d]
                return avail[d]
        self.issues.error(f"no usable dialect (have {sorted(avail)}; preference {self.pref})", path)
        return None

    def map_source(self, src: str, path: str) -> str:
        if path in self.ovr:
            return str(self.ovr[path])
        s = src.strip()
        if re.search(r"\s", s) or s.lower().startswith("select"):
            self.issues.error("dataset.source is a query; ClickZetta TABLES needs a table or view. "
                              "Create a view for it and pass the view via --overrides", path)
            return s
        for old, new in self.smap:
            if s.lower() == old.lower() or s.lower().startswith(old.lower() + "."):
                s = new + s[len(old):]
                break
        parts = [p.strip('`"') for p in s.split(".")]
        if len(parts) >= 3:
            self.issues.warn(f"source '{src}' has {len(parts)} parts; ClickZetta uses schema.table - "
                             f"using '{'.'.join(parts[-2:])}'. Use --source-map to control this", path)
            parts = parts[-2:]
        if len(parts) == 1 and self.schema:
            parts = [self.schema] + parts
        return ".".join(p.lower() if p.isupper() else p for p in parts)

    # ------------------------------------------------------------ build
    def build(self) -> tuple[str, list[str]]:
        m, issues = self.m, self.issues
        datasets = m.get("datasets") or []
        if not datasets:
            issues.error("model has no datasets")
        for ds in datasets:
            self.alias[ds["name"].lower()] = self.name_of(ds["name"], f"datasets.{ds['name']}")

        tables, facts, dims, metrics, rels = [], [], [], [], []
        var_names = {str(v.get("name", "")).lower() for v in get_ext(m).get("variables") or []}
        pk_of: dict[str, list[str]] = {}
        names_by_table: dict[str, set] = defaultdict(set)
        dims_by_table: dict[str, set] = defaultdict(set)   # alias (lower) -> dimension member names (lower)
        field_tables: dict[str, set] = defaultdict(set)    # field name / bare column (lower) -> aliases

        referenced_cols: dict[str, list[str]] = {}
        for r in m.get("relationships") or []:
            referenced_cols.setdefault(str(r.get("to", "")).lower(), list(r.get("to_columns") or []))

        # ---------------- tables and fields
        for ds in datasets:
            a = self.alias[ds["name"].lower()]
            p = f"datasets.{ds['name']}"
            sd: dict = {}
            if a != ds["name"]:
                sd["name"] = ds["name"]
            src = self.map_source(ds.get("source", ""), p + ".source")
            if src != ds.get("source"):
                sd["source"], sd["source_used"] = ds.get("source"), src
            pk = ds.get("primary_key") or []
            if not pk and ds.get("unique_keys"):
                pk = ds["unique_keys"][0]
                sd["pk_inferred"] = True
                issues.info(f"no primary_key; using first unique key {pk} as PRIMARY KEY", p)
            if not pk and referenced_cols.get(ds["name"].lower()):
                # ClickZetta: the referenced side of a relationship needs a PRIMARY KEY / UNIQUE key
                pk = referenced_cols[ds["name"].lower()]
                sd["pk_inferred"] = True
                issues.warn(f"no primary_key; relationships reference {pk}, used as PRIMARY KEY (ClickZetta "
                            "requires a key on the referenced table) - check the columns are unique", p)
            pk_of[a.lower()] = pk
            if ds.get("unique_keys"):
                sd["unique_keys"] = ds["unique_keys"]
            syn = _synonyms(ds)
            line = f"    {ident(a)} AS {src}"
            if pk:  # optional in ClickZetta; required only on the referenced side of a relationship
                line += f"\n        PRIMARY KEY ({', '.join(ident(c) for c in pk)})"
            if syn:
                line += f"\n        WITH SYNONYMS ({', '.join(sql_str(x) for x in syn)})"
            if ds.get("description"):
                line += f"\n        COMMENT = {sql_str(ds['description'])}"
            tables.append((a, line))
            _keep_ctx(sd, ds)
            if other_exts(ds):
                sd["custom_extensions"] = other_exts(ds)
            if sd:
                self.side["datasets"][a.lower()] = sd

            for f in ds.get("fields") or []:
                fp = f"{p}.fields.{f['name']}"
                fname = self.name_of(f["name"], fp)
                if fname.lower() in names_by_table[a.lower()]:
                    issues.error(f"duplicate member name '{fname}' in table '{a}'", fp)
                names_by_table[a.lower()].add(fname.lower())
                sf: dict = {}
                if fname != f["name"]:
                    sf["name"] = f["name"]
                e = self.expr(f, fp, sf)
                if e is None:
                    continue
                cz = get_ext(f)
                sfx = get_ext(f, "SNOWFLAKE")
                private = str(cz.get("access", "")).upper() == "PRIVATE" or \
                    "private" in str(sfx.get("access_modifier", "")).lower()
                qe = qualify_columns(quote_bare(e), a, var_names)
                if norm_expr(qe) != norm_expr(e):
                    # keep the as-written expression so export restores it unchanged
                    sf.setdefault("dialects", [{"dialect": d, "expression": x}
                                               for d, x in iter_dialects(f.get("expression"))])
                    sf["used"] = qe
                head = f"    {'PRIVATE ' if private else ''}{ident(a)}.{ident(fname)} AS {qe}"
                is_dim = "dimension" in f or cz.get("kind") == "dimension"
                if cz.get("kind") == "fact_aggregate":
                    is_dim = False
                field_tables[fname.lower()].add(a)
                if re.fullmatch(r"`?\w+`?", e.strip()):
                    field_tables[e.strip().strip("`").lower()].add(a)
                if is_dim:
                    dims_by_table[a.lower()].add(fname.lower())
                    meta = []
                    syn = _synonyms(f)
                    if syn:
                        meta.append(f"WITH SYNONYMS = ({', '.join(sql_str(x) for x in syn)})")
                    if cz.get("is_unique") or sfx.get("is_unique"):
                        meta.append("is_unique = true")
                    dim = f.get("dimension") or {}
                    is_time = dim.get("is_time")
                    if is_time is None:
                        is_time = f.get("datatype") in TEMPORAL
                    elif is_time is False and f.get("datatype") in TEMPORAL:
                        sf["is_time"] = False
                    if is_time:
                        meta.append("is_time = true")
                    enum = cz.get("enum_values")
                    if not enum and sfx.get("is_enum") and sfx.get("sample_values"):
                        enum = sfx["sample_values"]
                        issues.info("SNOWFLAKE is_enum + sample_values mapped to enum_values", fp)
                    if enum:
                        meta.append("enum_values = [" + ", ".join(_lit(v) for v in enum) + "]")
                    if f.get("description"):
                        meta.append(f"COMMENT = {sql_str(f['description'])}")
                    dims.append(head + "".join("\n        " + x for x in meta))
                else:  # FACTS take WITH SYNONYMS and COMMENT too (verified on ClickZetta)
                    meta = []
                    if _synonyms(f):
                        meta.append(f"WITH SYNONYMS = ({', '.join(sql_str(x) for x in _synonyms(f))})")
                    if f.get("description"):
                        meta.append(f"COMMENT = {sql_str(f['description'])}")
                    facts.append(head + "".join("\n        " + x for x in meta))
                if f.get("label"):
                    sf["label"] = f["label"]
                # "" = the source had no datatype; stops export from adding the SHOW type
                sf["datatype"] = f.get("datatype") or ""
                _keep_ctx(sf, f)
                if other_exts(f):
                    sf["custom_extensions"] = other_exts(f)
                if sfx:
                    _report_snowflake(sfx, fp, issues)
                if sf:
                    self.side["fields"][f"{a.lower()}.{fname.lower()}"] = sf

        # ---------------- relationships
        # Always named: ClickZetta accepts several relationships between the same two logical tables
        # (role-playing joins, e.g. ROUTE -> AIRPORT for departure and destination) only when they
        # are named, and metrics pick one path with USING (<relationship_name>).
        deps: dict[str, set] = defaultdict(set)
        edges: dict[str, list] = defaultdict(list)      # from alias -> [(to alias, relationship ident)]
        rel_ident: dict[str, str] = {}                  # ossie relationship name (lower) -> cz identifier
        for r in m.get("relationships") or []:
            rp = f"relationships.{r.get('name')}"
            fa, ta = self.alias.get(str(r["from"]).lower()), self.alias.get(str(r["to"]).lower())
            if not fa or not ta:
                issues.error(f"relationship refers to unknown dataset ({r['from']} -> {r['to']})", rp)
                continue
            if len(r["from_columns"]) != len(r["to_columns"]):
                issues.error("from_columns and to_columns differ in length", rp)
            known = {c for c, tabs in field_tables.items() if ta in tabs}
            odd = [c for c in r["to_columns"] if c.lower() not in known]
            if known and odd:
                issues.warn(f"to_columns {odd} are not fields of '{ta}' - check the relationship in the file", rp)
            if not pk_of.get(ta.lower()):
                issues.error(f"'{ta}' is referenced by a relationship but has no primary_key/unique_keys; "
                             "add one to the Ossie file", rp)
            elif [c.lower() for c in r["to_columns"]] != [c.lower() for c in pk_of.get(ta.lower(), [])]:
                # Not a maybe: ClickZetta requires the referenced columns to be the PRIMARY KEY (or a
                # UNIQUE key), so the generated CREATE is guaranteed to fail. An error, not a warning,
                # so ossie_to_sv exits 1 and the agent stops instead of executing DDL that cannot run.
                issues.error(f"to_columns {r['to_columns']} are not the primary key of '{ta}' "
                             f"{pk_of.get(ta.lower())}; ClickZetta will reject this view - give '{ta}' "
                             f"that key, or point the relationship at its primary key", rp)
            rname = self.name_of(r.get("name") or f"{fa}_{'_'.join(r['from_columns'])}_{ta}", rp)
            if rname.lower() in {x.lower() for x in rel_ident.values()}:
                issues.error(f"duplicate relationship name '{rname}'", rp)
            rel_ident[str(r.get("name") or rname).lower()] = rname
            rels.append(f"    {ident(rname)} AS {ident(fa)} ({', '.join(ident(c) for c in r['from_columns'])}) "
                        f"REFERENCES {ident(ta)} ({', '.join(ident(c) for c in r['to_columns'])})")
            deps[fa.lower()].add(ta.lower())
            edges[fa.lower()].append((ta.lower(), rname))
            key = "|".join([fa.lower(), ta.lower(), ",".join(c.lower() for c in r["from_columns"])])
            sr = {"name": r.get("name")}
            _keep_ctx(sr, r, keep_string=True, whole=True)
            if r.get("custom_extensions"):
                sr["custom_extensions"] = r["custom_extensions"]
            self.side["relationships"][key] = sr

        has_in = {t for outs in edges.values() for t, _ in outs}
        roots = [x for x in (a for a, _ in tables) if x.lower() not in has_in and (edges.get(x.lower()) or len(tables) == 1)]
        self.root = roots[0] if len(roots) == 1 else None   # the fact table in a star (Databricks `source`)
        self.field_tables = field_tables
        self.var_names = var_names
        if len(datasets) > 1 and not rels:
            issues.warn(f"{len(datasets)} datasets but no relationships: the view's tables cannot be combined in "
                        "one query. If the file is an ontology (e.g. apache/ossie flights.yaml), run "
                        "enrich_from_ontology.py first")

        # ---------------- metrics
        ds_names = {d["name"].lower() for d in datasets}
        metric_owner: dict[str, str] = {}
        for mt in m.get("metrics") or []:
            mp = f"metrics.{mt['name']}"
            cz = get_ext(mt)
            sm: dict = {}
            cz_name = cz.get("name") or mt["name"]
            mname = self.name_of(cz_name, mp)
            if mname != mt["name"]:
                sm["name"] = mt["name"]
            e = self.expr(mt, mp, sm)
            if e is None:
                continue
            bad = _window_problems(e, {d: self.alias[d].lower() for d in ds_names}, dims_by_table)
            if bad:
                issues.warn(f"window metric not representable in ClickZetta ({bad}): PARTITION BY / ORDER BY may "
                            "only name declared dimensions (qualified), not metrics or aggregates. Left out of "
                            "the view; kept in the sidecar and restored on export", mp)
                self.side.setdefault("metrics_not_in_view", []).append(mt)
                continue
            owner = cz.get("table")
            if owner and owner.lower() not in ds_names:
                issues.warn(f"custom_extensions table '{owner}' is not a dataset; inferring owner", mp)
                owner = None
            body, helpers = e.strip(), []
            if not owner:
                owner, body, helpers = self.plan_metric(e, mname, ds_names, metric_owner, mp)
            if body != e.strip():
                # keep the as-written expression so export restores it unchanged
                sm.setdefault("dialects", [{"dialect": d, "expression": x}
                                           for d, x in iter_dialects(mt.get("expression"))])
                sm["used"] = body
            sfx = get_ext(mt, "SNOWFLAKE")
            private = str(cz.get("access", "")).upper() == "PRIVATE" or \
                "private" in str(sfx.get("access_modifier", "")).lower()
            for h_alias, h_name, h_expr in helpers:
                metrics.append(f"    PRIVATE {ident(h_alias)}.{ident(h_name)} AS {h_expr}\n"
                               f"        COMMENT = {sql_str('part of ' + mname + ' (generated by clickzetta-ossie-interop)')}")
                self.side.setdefault("helper_metrics", []).append(f"{h_alias.lower()}.{h_name.lower()}")
                metric_owner[h_name.lower()] = h_alias.lower()
            if owner is None:  # view-scoped: unqualified name, body combines per-table metrics
                a = None
                metric_owner[mname.lower()] = None
                head = f"    {'PRIVATE ' if private else ''}{ident(mname)}"
                if cz.get("using"):
                    issues.warn("USING is ignored on a view-scoped metric; put it on the per-table metrics", mp)
            else:
                a = self.alias.get(str(owner).lower(), owner)
                metric_owner[mname.lower()] = a.lower()
                if mname.lower() in names_by_table[a.lower()]:
                    issues.error(f"metric '{mname}' clashes with a field of table '{a}'", mp)
                names_by_table[a.lower()].add(mname.lower())
                using = []
                for u in cz.get("using") or []:
                    if str(u).lower() in rel_ident:
                        using.append(rel_ident[str(u).lower()])
                    else:  # ClickZetta accepts unknown names in USING silently, so check here
                        issues.error(f"custom_extensions using '{u}' is not a relationship of the model", mp)
                if not using:
                    amb = _ambiguous_targets(a.lower(), edges)
                    if amb:
                        issues.warn("more than one relationship path from '" + a + "' to " + ", ".join(
                            f"'{t}' ({' | '.join(ps)})" for t, ps in sorted(amb.items())) + "; grouping this "
                            "metric by those tables fails until a path is chosen - set "
                            "custom_extensions[CLICKZETTA].using to the relationship name(s)", mp)
                use = f" USING ({', '.join(ident(u) for u in using)})" if using else ""
                head = f"    {'PRIVATE ' if private else ''}{ident(a)}.{ident(mname)}{use}"
            line = f"{head} AS {body}"
            if _synonyms(mt):
                line += f"\n        WITH SYNONYMS = ({', '.join(sql_str(x) for x in _synonyms(mt))})"
            if mt.get("description"):
                line += f"\n        COMMENT = {sql_str(mt['description'])}"
            metrics.append(line)
            # "" = the source had no datatype; stops export from adding the SHOW METRICS type
            sm["datatype"] = mt.get("datatype") or ""
            _keep_ctx(sm, mt)
            if other_exts(mt):
                sm["custom_extensions"] = other_exts(mt)
            if sfx:
                _report_snowflake(sfx, mp, issues)
            if sm:
                self.side["metrics"][f"{a.lower()}.{mname.lower()}" if a else mname.lower()] = sm

        # ---------------- variables and model
        cz_model = get_ext(m)
        variables = []
        for v in cz_model.get("variables") or []:
            line = f"    {ident(v['name'])} {v['type']}"
            if v.get("default") not in (None, ""):
                line += f" DEFAULT {v['default']}"
            if v.get("comment"):
                line += f" COMMENT {sql_str(v['comment'])}"
            variables.append(line)
        sfm = get_ext(m, "SNOWFLAKE")
        if sfm:
            _report_snowflake(sfm, "model", issues)
        sd_model: dict = {}
        if m.get("name") and m["name"] != self.view.split(".")[-1]:
            sd_model["name"] = m["name"]
        _keep_ctx(sd_model, m, keep_string=True)
        if other_exts(m):
            sd_model["custom_extensions"] = other_exts(m)
        self.side["model"] = sd_model

        # ---------------- assemble (referenced tables first)
        order = _topo([a for a, _ in tables], deps)
        tmap = {a.lower(): line for a, line in tables}
        parts = [f"-- Generated by clickzetta-ossie-interop/scripts/ossie_to_sv.py from Ossie model '{m.get('name')}'",
                 f"CREATE OR REPLACE SEMANTIC VIEW {self.view}",
                 "TABLES (\n" + ",\n".join(tmap[a] for a in order) + "\n)"]
        for kw, items in (("RELATIONSHIPS", rels), ("VARIABLES", variables), ("FACTS", facts),
                          ("DIMENSIONS", dims), ("METRICS", metrics)):
            if items:
                parts.append(f"{kw} (\n" + ",\n".join(items) + "\n)")
        if m.get("description"):
            parts.append(f"COMMENT = {sql_str(m['description'])}")
        create = "\n".join(parts) + ";\n"
        return create, self.sidecar_sql()

    def plan_metric(self, e: str, mname: str, ds_names: set, metric_owner: dict, path: str):
        """Decide where an Ossie (model-level) metric lives in ClickZetta.

        Returns (owner dataset or None for view-scoped, body, helpers[(alias, name, expr)]).
        Verified rules: a table-qualified metric may aggregate one table only (window OVER
        clauses may still reference other tables' dimensions); a metric combining metrics of
        several tables must be view-scoped (unqualified name); a metric that aggregates columns
        of several tables directly is rejected, so each single-table aggregate is split into a
        PRIVATE helper metric and the metric itself becomes view-scoped.
        """
        e = self._resolve_bare_columns(e, metric_owner, path)
        spans = _aggregate_spans(e)
        ds_re = {d: re.compile(rf"(?<![\w.`]){re.escape(d)}\s*\.", re.I) for d in ds_names}
        span_tables = [{d for d, rx in ds_re.items() if rx.search(e[a:b])} for a, b in spans]
        outside = "".join(e[i] if not any(a <= i < b for a, b in spans) else " " for i in range(len(e)))
        refs: dict[str, str | None] = {}  # referenced metric name -> owner alias (None = view-scoped)
        for mn, own in metric_owner.items():
            if re.search(rf"(?<![\w`]){re.escape(mn)}(?![\w`])", outside, re.I):
                refs[mn] = own
        agg_tables = set().union(*span_tables) if span_tables else set()
        owners = {self.alias[d].lower() for d in agg_tables} | {o for o in refs.values() if o}
        view_ref = any(o is None for o in refs.values())
        if not view_ref and len(owners) <= 1:
            if owners:
                own = owners.pop()
                return next(d for d in ds_names if self.alias[d].lower() == own), \
                    self._qualify_metric_refs(e, refs), []
            if self.root:
                self.issues.info(f"metric names no dataset (e.g. COUNT(*)); assigned to the fact table "
                                 f"'{self.root}' (the only dataset without incoming relationships)", path)
                return next(d for d in ds_names if self.alias[d] == self.root), e.strip(), []
            first = next(iter(ds_names), None)
            self.issues.warn(f"metric names no dataset and there is no single fact table; assigned to '{first}' - "
                             "set custom_extensions[CLICKZETTA].table", path)
            return first, e.strip(), []
        # several tables: view-scoped; split direct multi-table aggregation into helper metrics
        body, helpers, shift = e, [], 0
        if len(agg_tables) > 1 or (agg_tables and (refs or view_ref)):
            for n, ((a, b), tabs) in enumerate(zip(spans, span_tables), 1):
                if len(tabs) != 1:
                    self.issues.error(f"aggregate `{e[a:b]}` references {sorted(tabs) or 'no'} dataset(s); "
                                      "cannot split it into a per-table metric - rewrite it via --overrides", path)
                    continue
                alias = self.alias[next(iter(tabs))]
                h = f"{mname}__{alias.lower()}_{n}"
                helpers.append((alias, h, e[a:b].strip()))
                rep = f"{ident(alias)}.{ident(h)}"
                body = body[:a + shift] + rep + body[b + shift:]
                shift += len(rep) - (b - a)
            self.issues.warn(f"metric aggregates columns of several datasets ({sorted(agg_tables)}); split into "
                             f"PRIVATE per-table metrics {[h for _, h, _ in helpers]} combined by a view-scoped "
                             "metric (ClickZetta rejects multi-table aggregates). Export restores the original", path)
        else:
            self.issues.info("metric combines metrics of several tables; created as a view-scoped metric", path)
        return None, self._qualify_metric_refs(body, refs).strip(), helpers

    def _resolve_bare_columns(self, e: str, metric_owner: dict, path: str) -> str:
        """Bare column names in a metric (Databricks/Omni style: `SUM(o_totalprice)`) -> alias.column.
        A name that is a field of exactly one dataset goes there; otherwise to the fact table."""
        skip = set(metric_owner) | self.var_names
        unresolved, ambiguous = set(), set()

        def resolve(name: str):
            if name.lower() in skip:
                return None
            hits = self.field_tables.get(name.lower(), set())
            if len(hits) == 1:
                return next(iter(hits))
            if len(hits) > 1:
                ambiguous.add(name)
                return None
            if self.root:
                return self.root
            unresolved.add(name)
            return None

        out = qualify_columns(e, resolve, frozenset())
        if ambiguous:
            self.issues.error(f"bare column(s) {sorted(ambiguous)} exist in several datasets; qualify them "
                              "(dataset.column) via --overrides", path)
        if unresolved:
            self.issues.warn(f"bare column(s) {sorted(unresolved)} match no field and there is no single fact "
                             "table; left unqualified", path)
        if out != e:
            self.issues.info(f"bare columns qualified: `{out.strip()}`", path)
        return out

    def _qualify_metric_refs(self, e: str, refs: dict) -> str:
        """Bare references to other metrics -> <alias>.<metric> (view-scoped ones stay bare)."""
        for mn, own in refs.items():
            if own:
                e = re.sub(rf"(?<![\w.`]){re.escape(mn)}(?![\w`(])", f"{ident(own)}.{mn}", e, flags=re.I)
        return e

    def sidecar_sql(self) -> list[str]:
        side = {k: v for k, v in self.side.items() if v}
        if not side:
            return []
        props = encode_sidecar(side)
        body = ",\n    ".join(f"{sql_str(k)} = {sql_str(v)}" for k, v in props)
        return [f"-- Ossie-only metadata ({len(props)} chunk(s)); read back by sv_to_ossie.py\n"
                f"ALTER SEMANTIC VIEW {self.view} SET PROPERTIES (\n    {body}\n);\n"]


def _synonyms(obj: dict) -> list[str]:
    ctx = obj.get("ai_context")
    if isinstance(ctx, dict) and ctx.get("synonyms"):
        return [str(s) for s in ctx["synonyms"]]
    sfx = get_ext(obj, "SNOWFLAKE")
    return [str(s) for s in sfx.get("synonyms") or []]


def _keep_ctx(side: dict, obj: dict, keep_string: bool = True, whole: bool = False) -> None:
    """Keep ai_context parts the view cannot hold. Synonyms live in WITH SYNONYMS, but ClickZetta
    stores them lower-cased and re-ordered, so the as-written list is kept when that would change it.
    `whole`: the object has no WITH SYNONYMS clause (relationships) - keep everything."""
    ctx = obj.get("ai_context")
    if isinstance(ctx, dict):
        rest = {k: v for k, v in ctx.items() if k != "synonyms"}
        if rest or (whole and ctx):
            side["ai_context"] = ctx
    elif isinstance(ctx, str) and ctx and keep_string:
        side["ai_context"] = ctx
    syn = _synonyms(obj)
    if syn and not whole and syn != sorted(x.lower() for x in syn):
        side["synonyms_as_written"] = syn


def _lit(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return sql_str(str(v))


SNOWFLAKE_HANDLED = {"synonyms", "access_modifier", "is_enum", "sample_values"}


def _report_snowflake(sfx: dict, path: str, issues: Issues) -> None:
    rest = sorted(k for k in sfx if k not in SNOWFLAKE_HANDLED)
    if rest:
        issues.warn(f"SNOWFLAKE extension keys {rest} have no ClickZetta equivalent; they are kept in "
                    "the sidecar only (agent: decide whether any need manual handling)", path)


AGG_FUNCS = {"SUM", "COUNT", "AVG", "MIN", "MAX", "MEDIAN", "STDDEV", "STDDEV_POP", "STDDEV_SAMP", "VARIANCE",
             "VAR_POP", "VAR_SAMP", "APPROX_COUNT_DISTINCT", "COUNT_IF", "ANY_VALUE", "PERCENTILE",
             "PERCENTILE_APPROX", "APPROX_PERCENTILE", "BIT_AND", "BIT_OR", "BOOL_AND", "BOOL_OR",
             "COLLECT_LIST", "COLLECT_SET", "GROUP_CONCAT", "LISTAGG", "STRING_AGG", "CORR", "COVAR_POP",
             "COVAR_SAMP"}


def _aggregate_spans(e: str) -> list[tuple[int, int]]:
    """Outermost aggregate calls as (start, end) offsets, a trailing FILTER (...) included;
    an OVER (...) window after the call is not part of the span."""
    spans, i = [], 0
    for m in re.finditer(r"`?([A-Za-z_]+)`?\s*\(", e):
        if m.start() < i or m.group(1).upper() not in AGG_FUNCS:
            continue
        if m.start() > 0 and (e[m.start() - 1].isalnum() or e[m.start() - 1] in "_."):
            continue
        close = matching_paren(e, m.end() - 1)
        end = close + 1
        f = re.match(r"\s*FILTER\s*\(", e[end:], re.I)
        if f:
            end = matching_paren(e, end + f.end() - 1) + 1
        spans.append((m.start(), end))
        i = end
    return spans


def _window_problems(e: str, alias_of: dict[str, str], dims_by_table: dict[str, set]) -> str | None:
    """Check OVER (...) clauses: ClickZetta accepts only qualified declared dimensions there."""
    for m in re.finditer(r"\bOVER\s*\(", e, re.I):
        clause = e[m.end():matching_paren(e, m.end() - 1)]
        if _aggregate_spans(clause):
            return f"aggregate in `OVER ({clause.strip()})`"
        for ds, col in re.findall(r"(?<![\w.`])`?([A-Za-z_]\w*)`?\s*\.\s*`?([A-Za-z_]\w*)`?", clause):
            alias = alias_of.get(ds.lower())
            if alias and col.lower() not in dims_by_table.get(alias, set()):
                return f"`{ds}.{col}` in OVER is not a declared dimension"
    return None


def _ambiguous_targets(start: str, edges: dict[str, list]) -> dict[str, list[str]]:
    """Tables reachable from `start` over more than one relationship path -> the paths (as names)."""
    paths: dict[str, list[str]] = defaultdict(list)

    def walk(node: str, trail: list[str], seen: set) -> None:
        for to, rname in edges.get(node, ()):
            if to in seen:
                continue
            p = trail + [rname]
            paths[to].append(" > ".join(p))
            walk(to, p, seen | {to})

    walk(start, [], {start})
    return {t: ps for t, ps in paths.items() if len(ps) > 1}


def _topo(aliases: list[str], deps: dict[str, set]) -> list[str]:
    out, seen = [], set()

    def visit(a: str, stack: set) -> None:
        if a in seen or a in stack:
            return
        stack.add(a)
        for d in sorted(deps.get(a, ())):
            visit(d, stack)
        seen.add(a)
        out.append(a)

    for a in aliases:
        visit(a.lower(), set())
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ossie")
    ap.add_argument("--view", required=True, help="target schema.view_name")
    ap.add_argument("--model", help="semantic_model name when the file has several")
    ap.add_argument("--prefer-dialect", default=",".join(DEFAULT_PREF))
    ap.add_argument("--source-map", action="append", default=[], help="OLD_PREFIX=new_prefix")
    ap.add_argument("--overrides", help="YAML {path: expression-or-source}")
    ap.add_argument("--no-sidecar", action="store_true")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--issues", help="write issues as JSON")
    a = ap.parse_args()

    models = pick_models(load_yaml(a.ossie))
    if not models:
        raise CliError(f"no semantic model in {a.ossie}: 'semantic_model' is empty")
    if a.model:
        models = [x for x in models if x.get("name") == a.model]
        if not models:
            raise CliError(f"model '{a.model}' not found in {a.ossie}")
    elif len(models) > 1:
        raise CliError("file has several semantic models; choose one with --model: " +
                       ", ".join(str(x.get("name")) for x in models))
    smap = [tuple(x.split("=", 1)) for x in a.source_map]
    overrides = load_yaml(a.overrides) if a.overrides else {}
    issues = Issues()
    imp = Importer(models[0], a.view, [d.strip().upper() for d in a.prefer_dialect.split(",")],
                   smap, overrides or {}, issues)
    create, extra = imp.build()
    with open(a.output, "w", encoding="utf-8") as fh:
        fh.write(create)
        if not a.no_sidecar:
            for s in extra:
                fh.write("\n" + s)
    issues.report()
    issues.write_json(a.issues)
    print(f"wrote {a.output}")
    sys.exit(1 if issues.has_errors else 0)


if __name__ == "__main__":
    run_cli(main)
