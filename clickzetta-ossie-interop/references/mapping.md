# Ossie ⇄ ClickZetta Semantic View mapping

Spec baseline: Apache Ossie Core Spec `0.2.0.dev0` (released: `0.1.1`) and Ontology `0.2.0.dev0`.
Vendored schemas: `scripts/schemas/` (Apache-2.0, see `NOTICE.md`).
Every ClickZetta behaviour below was verified against a live Lakehouse (tests in `tests/`).

## Model level

| Ossie `semantic_model[]` | ClickZetta | Direction notes |
|---|---|---|
| `name` | view name (without schema) | Import: the view name comes from `--view`; a different model name is kept in the sidecar |
| `description` | view `COMMENT = '...'` | Both directions |
| `ai_context` (string or object) | none | Sidecar |
| `datasets` | `TABLES (...)` | See below |
| `relationships` | `RELATIONSHIPS (...)` | See below |
| `metrics` | `METRICS (...)`: table-scoped, or view-scoped when the name has no table prefix | See below |
| `custom_extensions[CLICKZETTA].variables` | `VARIABLES (name TYPE DEFAULT v COMMENT '...')` | Both directions. `SHOW CREATE` prints defaults as Java literals (`100.00BD`); export strips the suffix |
| `custom_extensions[CLICKZETTA].view` | `schema.view` it was exported from | Export only (bookkeeping) |
| other vendors' `custom_extensions` | none | Sidecar |

## Datasets ⇄ logical tables

| Ossie `datasets[]` | ClickZetta `TABLES` item |
|---|---|
| `name` | alias. Non-identifier names become snake_case (original kept in the sidecar) |
| `source` | `AS <schema>.<table>`. Import: `--source-map` rewrites prefixes, 3-part names drop the first part (warning), 1-part names get the view's schema. `SHOW CREATE` returns `workspace.schema.table`; export drops the view's own workspace |
| `primary_key` | `PRIMARY KEY (...)`. Optional for a logical table, but **required on the referenced side of a relationship** (`columns of REFERENCES ... does not match any PRIMARY KEY or UNIQUE key`). Import falls back to the first `unique_keys` entry, then to the `to_columns` of relationships pointing at the dataset (warning). A derived key is marked in the sidecar and not exported |
| `unique_keys` | none | Sidecar |
| `description` | `COMMENT = '...'` |
| `ai_context.synonyms` | `WITH SYNONYMS ('a', 'b')` |

## Fields ⇄ FACTS / DIMENSIONS

Ossie decides the role by the **presence of the `dimension` block**, not by the data type:

| Ossie field | ClickZetta |
|---|---|
| has `dimension: {...}` | `DIMENSIONS` item |
| no `dimension` block | `FACTS` item (row-level) |
| `dimension.is_time: true`, or `is_time` unset and `datatype` ∈ {Date, Time, DateTime, DateTimeTz} | `is_time = true` |
| `dimension.is_time: false` on a temporal datatype | clause omitted; `false` kept in the sidecar |
| `expression.dialects[]` | `AS <expression>`. Dialect chosen by `--prefer-dialect` (default ANSI_SQL, SNOWFLAKE, DATABRICKS, BIGQUERY). Bare column names are qualified with the dataset alias (see below) |
| `description` | `COMMENT = '...'` (dimensions and facts) |
| `ai_context.synonyms` | `WITH SYNONYMS = (...)` (dimensions and facts) |
| `label` | none, sidecar |
| `datatype` | none. Sidecar keeps it (or "none" when the source had none); without a sidecar, export takes `data_type` from `SHOW SEMANTIC …` |
| `custom_extensions[CLICKZETTA].access = PRIVATE` | `PRIVATE` prefix |
| `custom_extensions[CLICKZETTA].is_unique` | `is_unique = true` |
| `custom_extensions[CLICKZETTA].enum_values` | `enum_values = [...]`. Numeric lists read back as numbers |
| `custom_extensions[CLICKZETTA].kind = fact_aggregate` | an aggregate FACT (`FACTS (t.x AS COUNT(...))`). Ossie fields are row-level, so other tools will not understand it |
| `custom_extensions[SNOWFLAKE]` `synonyms` / `access_modifier` / `is_enum`+`sample_values` | synonyms / PRIVATE / enum_values |

**Why expressions are qualified.** In `<alias>.<member> AS <expr>`, `<expr>` is resolved against all logical tables of the view. `FLIGHT.distance AS distance` fails with `reference distance is ambiguous, could be flight, route` as soon as another table has a `distance` column. The importer writes `FLIGHT.distance AS FLIGHT.distance`, skipping functions, keywords, type names, date parts and VARIABLES. Member names themselves may repeat across tables (`p.name` and `c.name`); queries must then use the qualified name.

A dimension may borrow a parent table's column (`o.cust_region AS c.region`); a FACT may not.

## Metrics

ClickZetta has two metric scopes:
- **table-scoped** `<alias>.<name> AS <expr>`: may aggregate columns of its own table only. A window `OVER (...)` may still name other tables' dimensions.
- **view-scoped** `<name> AS <expr>` (no prefix; `SHOW SEMANTIC METRICS` reports `table_name` NULL): combines metrics of several tables, each computed at its own grain.

| Ossie `metrics[]` | ClickZetta |
|---|---|
| `name` + `custom_extensions[CLICKZETTA].table` | `<table>.<name>` |
| `name`, no `table`, expression aggregates one dataset | `<that table>.<name>` |
| `name`, no `table`, expression combines metrics of several datasets | view-scoped `<name>` (bare metric references are qualified) |
| `name`, no `table`, expression aggregates columns of several datasets | each single-table aggregate becomes `PRIVATE <table>.<name>__<table>_<n>`, combined by a view-scoped `<name>`. Export hides the helpers (sidecar `helper_metrics`) and restores the original expression |
| bare columns (`SUM(o_totalprice)`, `COUNT(*)`) | assigned to the dataset with that field, else to the single fact table (no incoming relationship) |
| `custom_extensions[CLICKZETTA].using` | `USING (rel, ...)` before `AS` |
| `expression` | `AS <aggregate expression>` |
| `description` | `COMMENT = '...'` |
| `ai_context.synonyms` | `WITH SYNONYMS = (...)` |
| `datatype` | sidecar (without it, export takes `data_type` from `SHOW SEMANTIC METRICS`) |
| `custom_extensions[CLICKZETTA].access = PRIVATE` | `PRIVATE` prefix |

Two ClickZetta metrics with the same name on different tables become `<table>_<name>` in Ossie. The original name is kept in `custom_extensions[CLICKZETTA].name`.

**Not representable:** a window metric that partitions or orders by a metric or aggregate, such as `RANK() OVER (PARTITION BY store.s_store_sk ORDER BY SUM(sales.amount) DESC)`. ClickZetta requires `must reference a declared dimension by its alias`, and ordering by a metric (`ORDER BY o.revenue`) is rejected the same way. The importer leaves such metrics out with a warning, keeps them in the sidecar (`metrics_not_in_view`) and restores them on export.

## Relationships

| Ossie | ClickZetta |
|---|---|
| `name` | `<name> AS ...`. Always emitted. `SHOW SEMANTIC RELATIONSHIPS` reads names back upper-case (empty when unnamed); `SHOW CREATE` keeps them as written |
| `from` (many side) / `from_columns` | `<from_alias> (<cols>)` |
| `to` (one side) / `to_columns` | `REFERENCES <to_alias> (<cols>)` |
| `ai_context` | sidecar (relationships have no WITH SYNONYMS) |

**Role-playing joins and multiple paths.** Two relationships between the same pair of tables (ROUTE → AIRPORT for departure and destination) are accepted only when named; unnamed, ClickZetta raises `declares conflicting relationships`. When a metric can reach a table along more than one path, grouping it by that table fails with `more than one relationship path ... must select one with USING (<relationship_name>)`. `USING` takes one or more relationship names; naming any relationship on the intended path is enough, and the metric's other joins are unaffected. Metrics without an ambiguous grouping (totals, own-table dimensions) work without `USING`. ClickZetta does not validate names in `USING`; the importer does.

Import orders `TABLES` so that referenced tables come first.

## `custom_extensions[CLICKZETTA]` schema

`data` is a JSON string (Ossie requirement). Keys written by this skill:

```json
{
  "access": "PRIVATE",
  "is_unique": true,
  "enum_values": ["EAST", "WEST"],
  "native_type": "ARRAY<STRING>",
  "kind": "fact_aggregate",
  "table": "order_items",
  "using": ["flight_operated_by", "route_departure"],
  "name": "revenue",
  "view": "my_schema.sales_sv",
  "variables": [{"name": "min_amount", "type": "DECIMAL(12,2)", "default": "100.00", "comment": "..."}]
}
```

`native_type` accompanies `datatype: Opaque` for types outside Ossie's portable list (ARRAY, MAP, STRUCT, JSON, BINARY, VECTOR, …).

## The sidecar (lossless round trip)

Import writes the metadata ClickZetta cannot hold, or rewrites when it stores a view, as zlib+base64 JSON into view properties:

```sql
-- Written by ossie_to_sv.py; values are split into 2000-character chunks (6000-character values verified)
ALTER SEMANTIC VIEW my_schema.sales_sv SET PROPERTIES ('ossie_sidecar_0' = 'OSSIE1:0:1:eNp9...');
```

What it holds:
- the as-written expression of every field and metric (ClickZetta rewrites `a || b` to `concat(concat(a, b))`, window `ORDER BY x` to `x ASC`, and function names to `` `sum`(...) ``);
- synonyms as written (ClickZetta lower-cases and re-orders them);
- labels, datatypes (including "none"), `unique_keys`, derived keys, relationship names and `ai_context`, helper metrics, metrics not in the view, other vendors' extensions.

Export finds `OSSIE1:<i>:<n>:<data>` chunks in `DESC EXTENDED` output and restores them:
- **Expressions.** If the live expression still matches the stored one (after folding the rewrites above), the stored `dialects` list is restored unchanged. Otherwise the live expression is emitted as `ANSI_SQL`, the other stored dialects are kept, and a warning says the view changed since import.
- **Synonyms and descriptions** come from the live view; stored synonyms only restore case and order.

Base64 is used because `DESC EXTENDED` output drops single quotes and escapes newlines in property values.

## Reading a view back

| Source | Holds |
|---|---|
| `SHOW CREATE SEMANTIC VIEW` | Full DDL: relationship names, `USING`, synonyms (`WITH SYNONYMS('a')`), comments (`COMMENT 'x'`, no `=`). Not `is_unique`/`is_time`/`enum_values`. Needs `--write` in cz-cli (keyword guard), though it is read-only |
| `DESC EXTENDED` | Member rows `(<table>.<name>, <expression>, <comment>)`, each followed by metadata rows `('', <key>, <value>)` for `synonyms`, `is_unique`, `is_time`, `enum_values`, `private`. No metric `USING`. Properties in the `properties` row |
| `SHOW SEMANTIC TABLES/RELATIONSHIPS/FACTS/DIMENSIONS/METRICS` | Names (upper-case), data types, access |

String literals escape quotes with a backslash (`'it\'s'`). `'it''s'` is two adjacent literals and reads back as `its`.

## Known losses

| Item | Why |
|---|---|
| Relationship `ai_context`, labels, `unique_keys` (without sidecar) | No ClickZetta clause |
| `is_unique` / `is_time` written as `false` | ClickZetta reads these back as `true` whenever the clause exists. Import therefore never writes `= false` |
| Dataset `source` as a SQL query | ClickZetta `TABLES` needs a table or view. Create a view first |
| Window metric ranked by a metric/aggregate | Not supported by ClickZetta. Kept in the sidecar only |
| Multi-table aggregate semantics | After splitting, each part is computed at its own table's grain: `SUM(sales) / COUNT(DISTINCT customer.id)` divides by all customers, not only buyers |
| Snowflake verified queries, custom instructions, non-additive dimensions | No ClickZetta equivalent. Kept in the sidecar and reported |
| Synonyms that another vendor keeps in its `custom_extensions` | Import lifts them to ClickZetta `synonyms`, so the re-export writes the standard field and the vendor block does not come back byte-for-byte. The information survives; `ossie_diff.py` still reports a `~ synonyms` difference |
| `is_enum` / `sample_values` / `access_modifier` in a Snowflake vendor block | Re-expressed as `custom_extensions[CLICKZETTA]` `enum_values` / `access`. Same information under a different vendor key, so the diff is not empty |
| Cross-vendor round trip in general | Because the above move information between the standard fields and per-vendor blocks, a Snowflake → ClickZetta → Ossie pass is **not** `EQUIVALENT`. `tests/run_live_test.sh` reports the remaining differences as `INFO`, not as a failure; use `--ignore synonyms,extensions` to silence the representation shifts and see only real losses |

## Engine limitation behind multi-table metrics

A metric that spans datasets is imported as per-table `PRIVATE` metrics plus a view-scoped derived
metric that divides them, e.g. `clv AS store_sales.clv_1 / customer.clv_2`. That derived metric
indirectly pulls in a **parent-grain** metric, so grouping it by a **finer-grain** dimension is an
illegal fan-out. ClickZetta reports that correctly when the parent metric is queried directly:

```
CZLH-42000: invalid dimension 'o.st': its logical table 'o' has a finer grain than
metric 'c.regions' ... A metric can only be grouped by dimensions at an equal or coarser grain
```

but crashes instead when only the derived metric is requested, which is how an imported model is
normally queried:

```
CZLH-65000: Compiler internal error - generating logical plan failed,
            error message column not found: o.status ... based on op cz::optimizer::TableScan
```

This is an engine defect, reproducible in isolation from three tiny tables and two metrics — not
something the import can avoid, since the derived metric is the whole point of the split. Before
grouping a multi-table metric, ask which dimensions are legal at all:

```sql
SHOW SEMANTIC DIMENSIONS IN <view> FOR METRIC <metric>;   -- equal-or-coarser grain dimensions only
```

`tests/run_live_test.sh` records the crash as an `INFO` probe so it is not mistaken for a
regression in this skill.
