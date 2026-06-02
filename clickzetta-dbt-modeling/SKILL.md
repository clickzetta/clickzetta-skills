---
name: clickzetta-dbt-modeling
description: |
  dbt-clickzetta data modeling wizard. Autonomously discovers Lakehouse data sources,
  infers modeling strategies, generates sources.yml and model files, and runs the full test suite.
  Presents choices rather than blank forms — explores data first, then proposes a justified plan for user confirmation.
  Trigger when the user wants to turn raw Lakehouse data into usable analytical tables — mentions dbt
  (dbt modeling, dbt model, sources.yml, incremental, dbt run, dbt test), wants ETL transformation,
  dimension/fact tables, or asks "how do I turn these tables into a queryable dataset".
  Keywords: dbt, dbt modeling, sources.yml, incremental, dbt run, dbt test, dimension table, fact table, ETL
---

# clickzetta-dbt-modeling

See [references/materialization-guide.md](references/materialization-guide.md) for materialization type selection, index strategy, partition strategy, and dynamic table configuration.
See [references/incremental-patterns.md](references/incremental-patterns.md) for incremental strategy details.
See [references/test-strategy.md](references/test-strategy.md) for test coverage standards and custom test templates.
See [references/grant-patterns.md](references/grant-patterns.md) for grant configuration (multi-tenant / data security scenarios).

For the **complete end-to-end pipeline architecture** (ingestion → modeling → Studio publishing), see [../clickzetta-dbt-project-setup/references/elt-standards.md](../clickzetta-dbt-project-setup/references/elt-standards.md).

---

## Goal

Transform raw Lakehouse data into business-value dbt models, validated by tests.
Users don't need to describe table schemas — you discover them, you infer the strategy, users only confirm or adjust.

## Workflow

This skill runs as a series of conversation turns. Each turn ends with a question to the user — no files are written and no dbt commands are run until the user responds to that turn's question.

---

### Turn 0 — Discover schemas, ask which to use

Run `cz-cli schema list`. Show the user the schema list immediately and ask:
> "Which schemas contain the raw data you want to model?"

Present the schema names as options. **Stop here.**

If no schemas exist at all → ask about the data source and route to the appropriate ingestion skill. Tell the user: "Once data is ingested, come back and I'll pick up from here."

---

### Turn 1 — Explore selected schemas, ask about business context

After the user selects schemas, run `cz-cli table list` on those schemas. Show the table list.

Then ask three things:
1. **Business scenario**: what does this data represent? (e.g. retail orders, user behavior, finance — helps name models correctly)
2. **Target layers**: which layers to build? If the project was set up with `clickzetta-dbt-project-setup`, use the layering mode already chosen. Otherwise ask the user — common options:
   - dbt standard: staging → marts (add intermediate if needed)
   - Medallion: bronze → silver → gold
   - Traditional DW: ODS → DWD → DWS → ADS
   - Custom: specify layer names
3. **Data freshness requirement**: how fresh does the data need to be? (near-real-time / minute-level, T+1 daily batch, or mixed) — this determines whether to use dynamic_table (continuous refresh) or incremental (scheduled batch), which has significant cost implications

Also branch on data quality:
- **No relevant tables found** → ask: explore other schemas, explore other workspaces, or specify tables directly?
- **Data exists but looks unsuitable** (empty tables, no meaningful columns) → show what was found and why it's a concern. Ask: proceed anyway, ingest better data first (stay in conversation), or point to different data?

**Stop here. Do not run any COUNT or DESC queries yet.**

---

### Turn 2 — Analyze data, present modeling plan

After the user confirms business context and layers, run the analysis (tell the user "Analyzing table structures and data volumes..."):
- `DESC TABLE` each source table — identify columns, types, primary keys
- `SELECT COUNT(*)` — determine data volume
- Check growth history (last 7 days new rows)

Use these dimensions plus the Decision Tree in [references/materialization-guide.md](references/materialization-guide.md) to infer materialization and strategy for each model.

**Default to `dynamic_table`** for most models — it handles T+1 batch, large tables, and near-real-time equally well. Only switch to `incremental` when dynamic_table genuinely cannot do the job:
- The model needs to process a **specific time window** (yesterday's data only, last hour only) — dynamic_table always reflects full current state
- The model must run **after a specific upstream Studio task** (dependency ordering)
- The source is a **Table Stream** and you need to process changes by type or control offset advancement

The confirmation table format depends on materialization type:

| Model | Materialization | Key config | Notes |
|---|---|---|---|
| stg_orders | dynamic_table | refresh_interval: 5 MINUTE | Staging, near-real-time |
| dim_customers | dynamic_table | refresh_interval: 30 MINUTE | Small dimension, low-frequency |
| fct_orders_daily | incremental | strategy: insert_overwrite, partition: dt | T+1 batch, cheaper than DT |
| fct_orders_stream | incremental | strategy: merge, source: orders_stream | CDC stream source |
| dws_daily_revenue | incremental | strategy: insert_overwrite, partition: dt | Daily aggregation, T+1 |

For each model, briefly explain **why** that materialization was chosen — not just what it is. This helps the user make an informed decision.

Ask: "Confirm all and generate / adjust specific models / partial modeling (subset only)?"

**Stop here. Do not write any files.**

---

### Turn 3 — Generate files

Only after the user confirms the plan: generate all files in one pass.

Generate the directory structure to match the user's chosen layering mode. Examples:

```
# dbt standard
models/
├── staging/
│   ├── stg_{source}_{table}.sql
│   └── schema.yml
├── intermediate/          # only if needed for complex JOINs
│   └── int_{entity}__{verb}.sql
└── marts/
    ├── dim_{entity}.sql
    ├── fct_{event}.sql
    └── schema.yml

# Medallion
models/
├── bronze/
│   ├── {source}_{table}.sql
│   └── schema.yml
├── silver/
│   ├── {entity}.sql
│   └── schema.yml
└── gold/
    ├── {metric}.sql
    └── schema.yml

# Traditional DW
models/
├── ods/
│   ├── ods_{source}_{table}.sql
│   └── schema.yml
├── dwd/
│   ├── dwd_{domain}_{table}.sql
│   └── schema.yml
├── dws/
│   └── dws_{domain}_{metric}.sql
└── ads/
    └── ads_{subject}_{metric}.sql
```

For custom layering, generate directories matching the layer names the user specified.

Templates and schema.yml conventions are in the **Generated File Structure** section below.

After writing files, tell the user what was created and ask: "Ready to run `dbt run` and `dbt test`?"

---

### Turn 4 — Execute

Only after the user says yes, run commands in order:
- `dbt seed` — only if `seeds/` has `.csv` files
- `dbt run`
- `dbt snapshot` — only if `snapshots/` has `.sql` files
- `dbt test`

Report results after each command. If `dbt test` fails, diagnose and fix before declaring completion.

## Key Constraints

- `database: "{{ target.database }}"` in sources.yml — resolves to workspace name at runtime; never hardcode the workspace name
- **`dynamic_table` models do NOT need Studio scheduling** — `refresh_interval` drives automatic refresh; creating a Studio cron task for them is redundant and wasteful
- **`dynamic_table` models do NOT need Studio dependency config** — the system tracks upstream dependencies automatically through the DAG
- Only `incremental` / `table` / `snapshot` models need Studio scheduling via `clickzetta-dbt-studio-pipeline`
- Record incremental fields in each incremental model's schema.yml `meta` block:
  ```yaml
  meta:
    incremental_field: updated_at      # incremental filter field name
    incremental_strategy: merge        # incremental strategy
  ```
  This is the standard interface read by `clickzetta-dbt-studio-pipeline` — without it, the agent cannot auto-detect incremental fields during Studio publishing and will need to ask the user.

## Generated File Structure

Generate files in the directory structure matching the user's chosen layering mode (see Turn 3 above). The naming conventions below apply regardless of which layering pattern is used:

**dbt standard naming** (staging/marts):
```
stg_{source}_{table}.sql    # staging: one per raw table
dim_{entity}.sql            # dimension tables
fct_{event}.sql             # fact tables
int_{entity}__{verb}.sql    # intermediate (double underscore)
```

**Medallion naming** (bronze/silver/gold):
```
{source}_{table}.sql        # bronze: raw, minimal transformation
{entity}.sql                # silver: cleaned, conformed
{metric}.sql                # gold: aggregated, business-ready
```

**Traditional DW naming** (ODS/DWD/DWS/ADS):
```
ods_{source}_{table}.sql    # ODS layer
dwd_{domain}_{table}.sql    # DWD layer
dws_{domain}_{metric}.sql   # DWS layer
ads_{subject}_{metric}.sql  # ADS layer
```

**`dynamic_table` model template** (default for most layers):
```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 MINUTE',
    refresh_vc='default'
) }}
select
    ...
from {{ ref('upstream_model') }}
```

**`incremental` model template** (only when time-window control or Studio dependency is required):

Two patterns — choose based on how the model will be triggered:

**Pattern A — self-driven** (dbt decides what to process based on existing data):
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id',
    on_schema_change='append_new_columns'
) }}
select order_id, customer_id, amount, status, updated_at
from {{ source('raw', 'orders') }}
{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}
```

**Pattern B — partition overwrite** (Studio injects the date parameter at scheduling time):
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt',
    on_schema_change='append_new_columns'
) }}
select dt, region, count(*) as order_count, sum(amount) as revenue
from {{ source('raw', 'orders') }}
where status = 'completed'
group by dt, region
-- No is_incremental() filter needed — insert_overwrite replaces the entire partition each run
-- When published to Studio, the WHERE clause is injected by the scheduling parameter (bizdate)
```

**`on_schema_change` default**: always set `on_schema_change='append_new_columns'` on incremental models — the default `ignore` silently drops new columns from upstream, causing data loss that is hard to diagnose.

sources.yml goes inside `models/staging/schema.yml` (not a separate file):
```yaml
sources:
  - name: {source_name}
    database: "{{ target.database }}"
    schema: {raw_schema}
    tables:
      - name: {table}
```

**Comment persistence**: When generating schema.yml, write `description` for every model and column, and add `persist_docs` config — this way `dbt run` automatically writes comments into Lakehouse table and column metadata, visible in Studio, BI tools, and data catalogs:

```yaml
models:
  - name: fct_orders
    description: "Orders fact table, one row per order, incremental merge strategy"
    config:
      persist_docs:
        relation: true    # write table comment
        columns: true     # write column comments
    columns:
      - name: order_id
        description: "Unique order identifier"
```

Enable globally in `dbt_project.yml` to avoid repeating per model:
```yaml
models:
  {project_name}:
    +persist_docs:
      relation: true
      columns: true
```

**Test coverage standards** (add by default when generating schema.yml, see [references/test-strategy.md](references/test-strategy.md)):

| Test type | When to apply | Example |
|---|---|---|
| `not_null` | All primary keys and non-nullable business fields | order_id, customer_id |
| `unique` | All primary key fields | order_id |
| `relationships` | Fact table foreign keys → dimension table primary keys | fct_orders.customer_id → dim_customers.customer_id |
| `accepted_values` | Enum fields (status, type) | status: [pending, completed, cancelled] |

## Routing

| Scenario | Route to |
|---|---|
| No dbt project yet | `clickzetta-dbt-project-setup` |
| Models developed, ready to publish and schedule | `clickzetta-dbt-studio-pipeline` |
| User prefers SQL modeling without dbt | `clickzetta-dw-modeling` |
| Need to batch sync data from database / files | `clickzetta-data-ingest-pipeline` |
| Need real-time ingestion from Kafka / message queue | `clickzetta-kafka-ingest-pipeline` |
| Need CDC real-time sync from source database | `clickzetta-cdc-sync-pipeline` |

## Completion Criteria

- `dbt test` 0 errors
- `dynamic_table` models have `refresh_interval` and `refresh_vc` set in `{{ config() }}` and recorded in schema.yml `meta`:
  ```yaml
  models:
    - name: fct_orders
      config:
        meta:
          refresh_interval: "5 MINUTE"
          refresh_vc: default
  ```
- `incremental` models have `incremental_field` and `incremental_strategy` recorded in schema.yml `meta` (for use by `clickzetta-dbt-studio-pipeline`):
  ```yaml
  models:
    - name: fct_orders_incremental
      config:
        meta:
          incremental_field: updated_at
          incremental_strategy: merge
  ```

## Next Steps After Modeling (proactively present to user)

Present the following options after modeling is complete — let the user choose the direction:

**A. Publish model code to Studio as assets** → `clickzetta-dbt-studio-pipeline`
Publish SQL code to Studio for unified code management. Only `table` / `incremental` / `snapshot` models need scheduling — `dynamic_table` models self-refresh and do not need Studio cron tasks.

**B. Connect BI tools and start reporting** → `lakehouse-doc-en` official BI / JDBC / SQLAlchemy connection docs
Connect marts layer tables to Tableau / Metabase / FineReport or other BI tools for direct query and analysis.

**C. Configure data quality monitoring**
Add singular tests or integrate DQC for key metrics (daily order count, total revenue) with threshold alerts.

**D. Continue expanding models**
Add new business domain models, or optimize existing models (add indexes, partitioning, adjust VCluster).

**E. Verify data first**
Query marts layer manually with `cz-cli sql` or BI tools to confirm data looks correct before deciding next steps.

Don't only suggest Studio scheduling — the user may be more urgently interested in connecting BI or verifying data. Let them choose.
