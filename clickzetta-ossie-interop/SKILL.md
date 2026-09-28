---
name: clickzetta-ossie-interop
description: |
  Exchange ClickZetta Lakehouse Semantic Views with Apache Ossie, the open semantic model interchange standard. Export a semantic view to Ossie Core Spec YAML, import Ossie YAML (including Snowflake READ_OSSIE_YAML output, dbt, Databricks and other converters) as a CREATE SEMANTIC VIEW, check round trips, and derive an Ossie ontology skeleton (concepts, relationships, mappings). Deterministic scripts do the parsing, generation and validation; the agent handles judgement calls such as rewriting Snowflake expressions and wording ontology verbalizations.
  Triggered when the user says "Ossie", "Open Semantic Interchange", "export semantic view to YAML", "import Ossie YAML", "migrate Snowflake semantic view to ClickZetta", "semantic model interchange", "ontology from semantic view", "ontology_mappings".
  Keywords: ossie, open semantic interchange, semantic model, semantic view, yaml, interoperability, snowflake, ontology, custom_extensions, round trip, cz-cli
---

# ClickZetta ⇄ Apache Ossie

[Apache Ossie](https://github.com/apache/ossie) is a vendor-neutral YAML standard for semantic models. It has three layers:

| Ossie layer | What it holds | ClickZetta counterpart |
|---|---|---|
| Ontology (`ontology`, `ontology_mappings`) | Business concepts, relationships, rules, and mappings from logical fields to concepts | Derived by this skill (`derive_ontology.py`) + human review |
| Logical (Core Spec `semantic_model`) | datasets, fields, relationships, metrics | **Semantic View**: TABLES, RELATIONSHIPS, FACTS, DIMENSIONS, METRICS |
| Physical (`dataset.source`) | Tables and views in the platform | Lakehouse tables referenced in `TABLES (<alias> AS <schema>.<table> ...)` |

This skill gives the agent a CLI toolchain for the three jobs. Scripts live in `scripts/` (Python 3.9+, needs `pyyaml`; `jsonschema` for validation; `sqlglot` optional):

| Script | Job |
|---|---|
| `sv_dump.py` | Read a semantic view with cz-cli (SHOW CREATE, DESC EXTENDED, SHOW SEMANTIC …) into one JSON file |
| `sv_to_ossie.py` | **Export**: dump → Ossie Core Spec YAML |
| `ossie_to_sv.py` | **Import**: Ossie YAML → `CREATE OR REPLACE SEMANTIC VIEW` (+ `ALTER … SET PROPERTIES` sidecar) |
| `enrich_from_ontology.py` | For ontology files whose embedded model lacks keys, relationships, roles or metrics: infer them from the ontology (+ agent review file) |
| `validate_ossie.py` | Validate Core Spec or ontology files (vendored JSON Schemas + reference checks) |
| `ossie_diff.py` | Semantic diff of two Ossie files (round-trip check) |
| `derive_ontology.py` | Ontology skeleton from a Core Spec model; TODO markers where judgement is needed |

Reference docs (read on demand):
- [references/mapping.md](references/mapping.md) — field-by-field Ossie ⇄ ClickZetta mapping, `custom_extensions[CLICKZETTA]`, the sidecar, known losses.
- [references/snowflake-interop.md](references/snowflake-interop.md) — Snowflake ⇄ ClickZetta through Ossie, `--overrides` workflow.
- [references/ontology-derivation.md](references/ontology-derivation.md) — derivation rules and what the agent/human must finish.

Set `SK=<path to this skill>` and `P=<cz-cli profile>` in the commands below.

---

## Workflow 1 — Export a semantic view to Ossie

```bash
# 1. Read the view (read-only statements)
python3 $SK/scripts/sv_dump.py --profile $P --view my_schema.sales_sv -o sales_sv.dump.json
# 2. Convert and validate
python3 $SK/scripts/sv_to_ossie.py sales_sv.dump.json -o sales_sv.ossie.yaml --issues export_issues.json
python3 $SK/scripts/validate_ossie.py sales_sv.ossie.yaml
```

- `sv_dump.py` passes `--write` to `SHOW CREATE SEMANTIC VIEW` only. The statement is read-only, but cz-cli's keyword guard refuses anything containing `CREATE` without the flag. All other statements run without it.
- Expressions are written under the `ANSI_SQL` dialect. Ossie has no ClickZetta dialect, and `ANSI_SQL` is the documented fallback. If an expression uses a ClickZetta-only function, say so to the user, because other tools may not parse it.
- For a target that only accepts the released 0.1.1 spec, such as Snowflake `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_OSSIE_YAML`, add `--spec-version 0.1.1`. This drops `datatype`.
- Report `export_issues.json` warnings to the user. Treat them as findings; don't hide them.

## Workflow 2 — Import an Ossie file as a semantic view

```bash
# 1. Generate DDL (exit code 1 = errors to fix first; the file is still written for inspection)
python3 $SK/scripts/ossie_to_sv.py model.ossie.yaml --view my_schema.sales_sv \
    --source-map "SALES_DB.PUBLIC=my_schema" -o create_sales_sv.sql --issues import_issues.json
# 2. Review the issues and the DDL, then execute (DDL needs --write; the file may hold 2 statements)
cz-cli -p $P sql --write --batch -f create_sales_sv.sql > create.out.json
grep -q '"error":{' create.out.json && echo "FAILED - see create.out.json"
# 3. Smoke-test with a query
cz-cli -p $P sql -e "SELECT * FROM semantic_view(my_schema.sales_sv DIMENSIONS customers.region METRICS order_items.revenue)"
```

> ⚠️ `cz-cli sql --batch` exits 0 even when a statement fails. The failure is only in that statement's JSON (`"error":{...}`). Always check the output, as in step 2.

What the importer does for you (all verified on ClickZetta):
- **Column qualification.** `<alias>.<member> AS <expr>` resolves `<expr>` against every logical table. A bare `distance` is ambiguous once two tables have that column, so bare column names in field expressions are prefixed with the dataset alias. The as-written expression goes to the sidecar.
- **Relationship names.** Every relationship is emitted as `<name> AS a (fk) REFERENCES b (pk)`. Names are required for **role-playing joins**: two relationships between the same two tables, such as ROUTE → AIRPORT for departure and destination. Unnamed, ClickZetta rejects them with `declares conflicting relationships`.
- **Multi-table metrics.** Ossie metrics are model-level; ClickZetta metrics are table-scoped unless their name has no table prefix.
  - A metric that combines other tables' metrics becomes a **view-scoped metric** (`rev_per_cust AS o.revenue / c.cust_cnt`).
  - A metric that aggregates columns of several tables directly, such as `SUM(sales.amount) / COUNT(DISTINCT customer.id)`, is rejected by ClickZetta. The importer splits each single-table aggregate into a `PRIVATE` helper metric and combines them in a view-scoped metric.
  - Export hides the helpers and restores the original expression.
- **Bare columns in metrics** (Databricks/Omni style, `SUM(o_totalprice)`, `COUNT(*)`): assigned to the dataset that has that field, otherwise to the single fact table (the dataset nothing references).
- **Keys.** `PRIMARY KEY` is optional for a logical table, but the referenced side of a relationship needs one. When it is missing, the relationship's `to_columns` are used and a warning is raised. If two relationships reach the same keyless table through **different** columns, only one of them can be the key, so the other reference is necessarily invalid and the import stops with an error rather than hand over a `CREATE` that cannot run.

Agent responsibilities during import. Each maps to an issue the script reports:

| Issue says | Agent does |
|---|---|
| `using SNOWFLAKE expression verbatim` | Check the function against **clickzetta-sql-migration**. If it needs rewriting, put the ClickZetta form in an overrides YAML and re-run with `--overrides` |
| `source ... has 3 parts` | Confirm the target schema with the user and pass `--source-map OLD_PREFIX=schema` |
| `relationships reference [...], used as PRIMARY KEY` | Confirm with the user that those columns are unique in the referenced table |
| `to_columns [...] are not the primary key of '<x>'` | Two relationships reach a keyless table through different columns, so whichever key the importer inferred makes the other reference invalid and ClickZetta **will** reject the view (`dost not match any PRIMARY KEY or UNIQUE key`). Ask which column set identifies a row, set it as that dataset's `primary_key`, and re-run — the view cannot be created until then. `tests/fixtures/converters/orionbelt_obml.ossie.yaml` is a real case |
| `more than one relationship path from 'X' to 'Y'` | Ask which path the metric means. Record it as `custom_extensions[CLICKZETTA].using: [relationship names]`, which becomes `USING (...)`. Without it, grouping the metric by Y fails at query time |
| `split into PRIVATE per-table metrics` | Tell the user the metric is now computed per table and then combined. For example, CLV divides total sales by **all** customers in the customer table, not only buyers |
| `window metric not representable` | ClickZetta window metrics may only `PARTITION BY` / `ORDER BY` declared dimensions (not metrics or aggregates), so ranking by a metric cannot be imported. Tell the user; the metric stays in the sidecar |
| `bare column(s) ... exist in several datasets` | Qualify the column (`dataset.column`) in an overrides file |
| `extension keys [...] have no ClickZetta equivalent` | Tell the user which Snowflake features (verified queries, custom instructions, …) are not carried over |

Overrides file example:

```yaml
datasets.orders.fields.is_completed: "IF(orders.status = 'COMPLETED', 1, 0)"
metrics.completion_rate: "SUM(orders.is_completed) / NULLIF(COUNT(orders.order_id), 0)"
datasets.orders.source: "my_schema.orders"
```

The generated `ALTER SEMANTIC VIEW … SET PROPERTIES ('ossie_sidecar_0' = 'OSSIE1:…')` stores the metadata that ClickZetta has no column for or rewrites on storage:
- as-written expressions (ClickZetta turns `a || b` into `concat(a, b)` and adds `ASC` to window `ORDER BY`);
- synonyms as written (ClickZetta lower-cases and re-orders them);
- labels, datatypes, relationship `ai_context`, and other vendors' `custom_extensions`. A later export restores it, which keeps the round trip lossless. Use `--no-sidecar` if the user does not want properties written.

## Workflow 2b — Import an Ossie *ontology* file (e.g. apache/ossie `examples/flights.yaml`)

Ontology files often keep the structure only in the ontology layer: the embedded `semantic_model` has no `primary_key`, no `relationships`, no `dimension` blocks (so every field is a fact) and no metrics. Imported as-is, it gives a view of unconnected tables (`ossie_to_sv.py` warns `no relationships`). First enrich it from the ontology:

```bash
python3 $SK/scripts/enrich_from_ontology.py flights.yaml -o flights.core.yaml --issues enrich.json
```

The script derives:
- **primary keys** from each concept's `identify_by` and object mappings;
- **relationships** from `link_mappings` that point to entities owned by another dataset;
- **field roles** from the mapped concept's built-in type: identifiers, references and strings become dimensions, Date/DateTime become time dimensions, numbers become facts;
- **metrics** from `derived_by` rules such as `AVG[Flight.departure_delay ...]`. A join path in the rule (`WHERE Airport == Flight.route.departure`) becomes the metric's `USING (flight_route, route_departure)`.

It reports every inference. The agent then writes a review file for what the ontology leaves open:
- fields the ontology does not map;
- numeric buckets that should be dimensions;
- counts and other KPIs;
- the join path of each metric (`using:`) wherever the graph has more than one.

It also flags join-graph shapes to raise with the user. Both are supported by ClickZetta through named relationships plus `USING`, but each metric must say which path it means:
- **role-playing joins**, such as ROUTE → AIRPORT as both departure and destination;
- **multiple join paths**, such as FLIGHT → CARRIER directly and through AIRCRAFT.

`USING` lists one or more relationship names. Naming any relationship on the intended path is enough, and other tables stay reachable as usual. ClickZetta accepts unknown names in `USING` without an error, so the importer checks them.

```bash
python3 $SK/scripts/enrich_from_ontology.py flights.yaml -o flights.core.yaml --review review.yaml
python3 $SK/scripts/ossie_to_sv.py flights.core.yaml --view my_schema.flights_sv \
    --source-map "DATABASE.SCHEMA=my_schema" -o flights_sv.sql
```

See `tests/flights/review.yaml` for a worked review. The flights test checks the resulting view against independently computed results, including departure-airport and arrival-airport metrics in one query.

## Workflow 3 — Round-trip check

```bash
python3 $SK/scripts/sv_dump.py --profile $P --view my_schema.sales_sv_copy -o copy.dump.json
python3 $SK/scripts/sv_to_ossie.py copy.dump.json -o copy.ossie.yaml
python3 $SK/scripts/ossie_diff.py original.ossie.yaml copy.ossie.yaml     # prints EQUIVALENT or the differences
```

Use `--ignore datatype,source` when comparing against a file from another platform.

## Workflow 4 — Derive an ontology

```bash
python3 $SK/scripts/derive_ontology.py sales_sv.ossie.yaml -o sales.ontology.yaml --attributes
python3 $SK/scripts/validate_ossie.py sales.ontology.yaml      # warns on every TODO
```

The script builds the mechanical parts:
- one EntityType per dataset;
- identifiers from primary keys;
- ManyToOne relationships from foreign keys;
- attribute relationships from dimensions (`--attributes`);
- `ontology_mappings` with `object_mappings` and `link_mappings`, and the semantic model embedded.

Metrics stay in the Core Spec model. Then:
1. **Agent drafts** a natural `verbalizes` phrase for every `TODO` (for example `{Order} is placed by {Customer}`), renames concepts to business names (`OrderItems` → `OrderLine`), and proposes `requires` rules (for example `Amount > 0`) from comments, enum values and data.
2. **Human confirms.** Show the concept list, the relationships and the proposed rules. Ontology semantics are a business decision.
3. Re-validate until there are no TODO warnings.

---

## Quick reference: how ClickZetta concepts land in Ossie

| ClickZetta | Ossie |
|---|---|
| Logical table `alias AS schema.table PRIMARY KEY (...)` | `datasets[]`: `name`, `source`, `primary_key` |
| `FACTS` item | field **without** a `dimension` block |
| `DIMENSIONS` item | field with `dimension: {}`; `is_time = true` → `dimension.is_time: true` |
| `METRICS` item (table-scoped) | model-level `metrics[]`; owning table in `custom_extensions[CLICKZETTA].table` |
| `METRICS` item without table prefix (view-scoped) | model-level `metrics[]` with no `table` |
| metric `USING (rel, ...)` | `custom_extensions[CLICKZETTA].using` |
| `RELATIONSHIPS name AS a (fk) REFERENCES b (pk)` | `relationships[]`: `name`, `from: a`, `to: b` |
| `WITH SYNONYMS` / `COMMENT` | `ai_context.synonyms` / `description` |
| `PRIVATE`, `is_unique`, `enum_values`, `VARIABLES` | `custom_extensions[CLICKZETTA]` |
| data type (from `SHOW SEMANTIC …`) | `datatype` (String, Integer, Decimal, Float, Boolean, Date, DateTime, DateTimeTz, Opaque) |

Full details and loss notes: [references/mapping.md](references/mapping.md).

---

## Tests

| Command | Needs a database | Covers |
|---|---|---|
| `bash tests/run_offline_tests.sh` | no | parse / export / import / round trip, Snowflake-style import, flights and tpcds imports, converter outputs, every CLI flag, error handling and exit codes, the profile lock |
| `python3 tests/scale/run_scale_test.py` | no | synthetic models from 5 to 100 datasets (1224 fields, a 99-deep relationship chain) through the whole round trip, with a per-step time budget |
| `python3 tests/scale/run_scale_test.py --profile <profile>` | yes | the same, plus a 7-chunk sidecar through a real `ALTER … SET PROPERTIES` and `DESC EXTENDED` |
| `bash tests/run_live_test.sh <profile>` | yes | sales view export → import → round trip → query equality, syntax probes, Snowflake-style import |
| `bash tests/flights/run_flights_test.sh <profile>` | yes | apache/ossie flights ontology → view; 13 queries checked against sqlite |
| `bash tests/tpcds/run_tpcds_test.sh <profile>` | yes | apache/ossie tpcds model → view; multi-table and window metrics checked against sqlite |
| `bash tests/converters/run_converter_smoke.sh <profile>` | yes | Databricks / Omni / NVIDIA / GoodData / OrionBelt outputs create a view and every query compiles |

Live tests create only schema `ossie_skill_test` or `ossie_flights_test`, stop if it already exists, and drop it at the end.

Run the live ones **one at a time**: they take a per-profile lock (`tests/lib/lock.sh`) and a second
run against the same profile exits 3 immediately. Two at once contend for one vcluster and both
start failing with `JOB_TIMEOUT`, which looks like a product problem and is not. If a run is killed,
remove the stale directory the abort message names (`tests/.locks/<profile>.lock`).

---

## FAQ

| Issue | Cause | Solution |
|---|---|---|
| A script exits **2** | It could not run at all: unreadable, non-UTF-8, malformed or empty input, a directory, bad usage, a file with no `semantic_model`, a dump with no `ddl`. One `error: <sentence>` line on stderr says which | Fix that input. Exit **1** means the opposite: it ran and found problems (invalid model, differences, error-level issues) — read the issues, not the file path |
| Querying an imported multi-table metric gives `CZLH-65000 Compiler internal error ... column not found` | The derived metric that combines the per-table `PRIVATE` parts indirectly references a **parent-grain** metric, and you grouped it by a **finer-grain** dimension. ClickZetta rejects that with a clear `CZLH-42000` grain error when the parent metric is queried directly, but crashes when only the derived metric is asked for. Engine defect, reproducible in isolation — see [references/mapping.md](references/mapping.md) | Group by an equal-or-coarser dimension. `SHOW SEMANTIC DIMENSIONS IN <view> FOR METRIC <metric>` lists exactly the legal ones, so use it to build the query instead of guessing |
| `sv_dump.py` prints `ddl=NO` | `SHOW CREATE SEMANTIC VIEW` returned nothing or an unexpected envelope | Check `raw.show_create` in the dump JSON; the view name must be `schema.view` |
| Import DDL fails `cannot resolve column` | A Snowflake/other-dialect expression refers to something ClickZetta cannot resolve, or a table-qualified metric touches another table's column | Rewrite via `--overrides`; for cross-table arithmetic use per-table metrics + a view-scoped metric (the importer does this for plain aggregates) |
| DDL executed but the view does not exist | `cz-cli --batch` exits 0 on failure | Check the output for `"error":{` |
| `declares conflicting relationships` | Two unnamed relationships between the same tables | Name them (`name AS a (fk) REFERENCES b (pk)`); the importer always does |
| Query fails `more than one relationship path ... must select one with USING` | The metric has several paths to a grouped table | Set `custom_extensions[CLICKZETTA].using` and re-import |
| `must reference a declared dimension by its alias` | Window metric partitions/orders by a raw column, a metric or an aggregate | Use a qualified dimension alias; ranking by a metric is not supported |
| `directly aggregates columns from more than one logical table` | Hand-written multi-table aggregate | Per-table metrics combined in a view-scoped metric |
| `COMMENT 'it''s'` reads back as `its` | `''` is two adjacent literals in ClickZetta, not an escape | Escape with backslash: `'it\'s'` (the importer does) |
| `SHOW CREATE` refused with `WRITE_NOT_ALLOWED` | cz-cli keyword guard sees `CREATE` | Add `--write`; the statement is still read-only |
| `Syntax error at or near 'WITH'` | Dimension metadata out of order | Generated DDL already orders `WITH SYNONYMS` first. Keep that order when editing by hand |
| Snowflake file has `SNOW_DB.SCHEMA.TABLE` sources | Ossie sources are platform paths | `--source-map "SNOW_DB.SCHEMA=my_schema"` |
| Round trip reports changed `datatype` | The file was not imported by this skill (no sidecar), and datatype comes from ClickZetta column types | Expected across platforms. Use `--ignore datatype` |
| Validation fails on `version` | The file is 0.1.1 and a strict tool expects 0.2.0.dev0, or the reverse | `validate_ossie.py` accepts both. Use `--spec-version` on export for the target |
| Ontology validation warns `TODO` | Verbalizations need business wording | Agent drafts, human confirms (Workflow 4) |

Related skills: **clickzetta-semantic-view** (DDL and query syntax), **clickzetta-sql-migration** (Snowflake → ClickZetta function rewrites), **clickzetta-analytics-agent** (use the imported view in the Analytics Agent).
