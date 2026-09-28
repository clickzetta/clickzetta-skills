# Snowflake ⇄ ClickZetta through Ossie

Snowflake provides native SQL functions for Ossie (Preview at the time of writing; check Snowflake docs for current status):

| Snowflake function | Use |
|---|---|
| `SYSTEM$READ_OSSIE_YAML_FROM_SEMANTIC_VIEW('db.schema.view')` | Export a Snowflake semantic view as Ossie YAML |
| `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_OSSIE_YAML('db.schema', '<yaml>')` | Create a Snowflake semantic view from Ossie YAML (accepts spec 0.1.1; prefers SNOWFLAKE dialect, then ANSI_SQL) |

## What Snowflake's export looks like

> Status: the list below comes from Snowflake documentation. The skill's Snowflake test fixture
> (`tests/fixtures/snowflake_orders.ossie.yaml`) is hand-written to match it; a file produced by a real
> Snowflake account has not been run through the importer yet.

- A `semantic_model:` list with one model.
- Expressions only under the `SNOWFLAKE` dialect.
- Sources as 3-part upper-case names (`DB.SCHEMA.TABLE`).
- Snowflake-only features under `custom_extensions` with `vendor_name: SNOWFLAKE`:
  - model: `variables`, `verified_queries`, `custom_instructions`, `tags`;
  - field: `synonyms`, `sample_values`, `is_enum`, `access_modifier`;
  - metric: `synonyms`, `access_modifier`, `non_additive_dimensions`.
- Labels and data types are not included. Non-equi joins are dropped.

## Snowflake → ClickZetta

```bash
# 1. In Snowflake, save the output of SYSTEM$READ_OSSIE_YAML_FROM_SEMANTIC_VIEW to snow.yaml
# 2. First pass: see what needs attention
python3 $SK/scripts/ossie_to_sv.py snow.yaml --view my_schema.orders_sv \
    --source-map "SNOW_DB.SALES=my_schema" -o orders_sv.sql --issues issues.json
```

For each issue `using SNOWFLAKE expression verbatim: <expr>`:
1. Look the functions up in **clickzetta-sql-migration** (Snowflake → ClickZetta function map).
2. If the expression works unchanged in ClickZetta, do nothing.
3. Otherwise add a ClickZetta rewrite to `overrides.yaml`, keyed by the path in the issue:

```yaml
datasets.orders.fields.is_completed: "IF(orders.status = 'COMPLETED', 1, 0)"
metrics.completion_rate: "SUM(orders.is_completed) / NULLIF(COUNT(orders.order_id), 0)"
```

```bash
# 3. Second pass with the rewrites, then create and smoke-test
python3 $SK/scripts/ossie_to_sv.py snow.yaml --view my_schema.orders_sv \
    --source-map "SNOW_DB.SALES=my_schema" --overrides overrides.yaml -o orders_sv.sql
cz-cli -p $P sql --write --batch -f orders_sv.sql
```

The physical tables must already exist in ClickZetta with the same column names. Moving the data is out of scope; see the ingestion skills.

Mapped automatically:

| Snowflake extension key | ClickZetta |
|---|---|
| `synonyms` (field, metric) | `WITH SYNONYMS` (dimensions, facts and metrics all accept it) |
| `access_modifier` containing `private` | `PRIVATE` |
| `is_enum: true` + `sample_values` | `enum_values = [...]` |

Everything else (`verified_queries`, `custom_instructions`, `non_additive_dimensions`, `tags`, Snowflake `variables`) is reported as a warning and kept in the sidecar. Tell the user which of these were not carried over.

## ClickZetta → Snowflake

```bash
python3 $SK/scripts/sv_dump.py --profile $P --view my_schema.sales_sv -o dump.json
python3 $SK/scripts/sv_to_ossie.py dump.json -o sales_sv.ossie.yaml --spec-version 0.1.1
```

Then call `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_OSSIE_YAML('<db>.<schema>', '<yaml>')` in Snowflake. Before that:
- Rewrite `dataset.source` values to Snowflake table names.
- Check that ClickZetta-specific functions in `ANSI_SQL` expressions exist in Snowflake. For any that don't, add a `SNOWFLAKE` dialect entry to the expression.
- Expressions read from ClickZetta may be in its stored form (`` `sum`(x) ``, `concat(...)` for `||`); for a view imported by this skill the sidecar restores the original text.
- View-scoped metrics (no `table`) and `custom_extensions[CLICKZETTA].using` have no Snowflake counterpart in the file; check that Snowflake resolves the join path you intend.
- ClickZetta `VARIABLES`, `PRIVATE`, `is_unique` and `enum_values` travel in `custom_extensions[CLICKZETTA]`. Snowflake keeps unknown extensions as metadata but does not act on them.

A round trip Snowflake → ClickZetta → Ossie restores the original SNOWFLAKE expressions from the sidecar. Rewritten expressions come back as an additional `ANSI_SQL` entry, so both platforms' versions travel together.
