---
name: clickzetta-dbt-modeling
description: |
  dbt-clickzetta data modeling wizard. Autonomously discovers Lakehouse data sources,
  infers modeling strategies, generates sources.yml and model files, and runs the full test suite.
  Presents choices rather than blank forms — explores data first, then proposes a justified plan for user confirmation.

  Trigger this skill whenever the user wants to turn raw Lakehouse data into usable analytical tables,
  even if they don't mention dbt or ClickZetta by name. Typical scenarios:
  - Explicitly mentions dbt (dbt modeling, dbt model, sources.yml, incremental, snapshot, dbt run, dbt test)
  - Wants to do ETL transformation, data cleansing, or layered modeling on Lakehouse data
  - Wants to build dimension tables, fact tables, or summary tables
  - Has raw data and wants to produce tables ready for reporting or analysis
  - Asks "how do I turn these tables into a queryable dataset"
  - Already has a dbt project set up and wants to start building models
---

# clickzetta-dbt-modeling

See [references/materialization-guide.md](references/materialization-guide.md) for materialization type selection, index strategy, partition strategy, and dynamic table configuration.
See [references/incremental-patterns.md](references/incremental-patterns.md) for incremental strategy details.
See [references/test-strategy.md](references/test-strategy.md) for test coverage standards and custom test templates.
See [references/grant-patterns.md](references/grant-patterns.md) for grant configuration (multi-tenant / data security scenarios).

---

## Goal

Transform raw Lakehouse data into business-value dbt models, validated by tests.
Users don't need to describe table schemas — you discover them, you infer the strategy, users only confirm or adjust.

## Workflow

**Explore → Confirm scope → Infer → Single confirmation → Generate → Execute**

1. **Explore**: Quickly discover available data, then **immediately interact with the user** — do not silently explore for a long time.

   **Step 1a — Schema list** (fast, ~2 seconds): Run `cz-cli schema list` to get all schemas.
   Immediately show the user what was found and ask which schemas contain the raw data they want to model. Present the schema names as options. **Do not proceed to table-level exploration until the user has confirmed scope** — this is the first interaction checkpoint and the user should see something within seconds of the skill starting.

   **Step 1b — Table list** (after user selects schemas): Run `cz-cli table list` on the selected schemas only. Show the table list to the user.

   **Step 1c — Branch decision** (must pass this gate before inferring):

   - **Data found and suitable** → proceed to step 2
   - **No relevant tables in current schema** → ask the user whether to expand scope. Present three options: explore other schemas in the same workspace (list them), explore other workspaces, or let the user specify a table/schema directly.
   - **Data exists but not suitable for modeling** → show what was found and why it's not suitable, then ask what the user wants to do. Present options: proceed anyway with available data, ingest missing/better data first (stay in conversation and continue modeling after ingestion), or point to different data.
   - **No raw data anywhere in Lakehouse** → ask the user about their data source and route to the appropriate ingestion skill. Present options: relational database batch sync or CDC, Kafka/message queue, files (OSS/S3/CSV), or user will prepare data themselves.

   **For no-data and unsuitable-data cases: do not route away and abandon the session.** Tell the user: "Once ingestion is done, come back here and tell me — I'll pick up from where we left off and continue with modeling."

   **Do not proceed to inference or generate any model files when data is absent or unsuitable** — models built on empty or malformed tables will fail `dbt test`, and field inference will be completely wrong, creating more rework.

2. **Infer**: Combine four dimensions to automatically infer materialization type and incremental strategy (rules in references/materialization-guide.md):
   - **Table name**: identify fact / dimension / aggregation naming patterns
   - **Columns**: presence of `updated_at` / `dt` / primary key fields — key question: are rows modified after insert, or append-only?
   - **Row count**: `SELECT COUNT(*)` to determine data volume
   - **Growth history**: check last 7 days new rows and modification patterns

   **The single most important question**: does the output table need DML (merge/update/delete by primary key)?
   - **YES** → `incremental` (dynamic_table is read-only, cannot merge)
   - **NO** → `dynamic_table` is the default for everything else: ODS/staging, DWD dimensions, DWS/ADS aggregations, append-only facts

   **Key inference rule for aggregation models** (DWS/ADS layer): customer stats, daily revenue, product performance, store rankings — default to `dynamic_table`. Only use `incremental` when the aggregation must include only a specific time window (e.g. "yesterday only").

3. **Single confirmation**: Summarize all model inference results in one table, let user choose A (confirm all) / B (adjust) / C (partial modeling)

4. **Generate**: After confirmation, generate sources.yml, staging models, marts models, schema.yml in one pass

5. **Execute**: Confirm before each step, in order — skip steps where no files exist:
   - `dbt seed`: only when `seeds/` directory contains `.csv` files
   - `dbt run`: always
   - `dbt snapshot`: only when `snapshots/` directory contains `.sql` files
   - `dbt test`: always

Present options via interactive question tool at every user decision point. If no such tool is available, list options in text. **Do not execute anything before receiving the user's answer.**

**Expand scope question** (when no relevant tables in current schema):
```
question({
  questions: [{
    question: "No relevant tables found in the current schema. How would you like to proceed?",
    options: [
      { label: "Explore other schemas", description: "Search other schemas in the same workspace" },
      { label: "Explore other workspaces", description: "Search across other workspaces" },
      { label: "Specify tables directly", description: "I'll tell you the exact table name or schema to use" }
    ]
  }]
})
```

**Data not suitable question** (when data exists but has issues):
```
question({
  questions: [{
    question: "Found data but it may not be ready for modeling. What would you like to do?",
    options: [
      { label: "Proceed anyway", description: "Model with what's available, fix data issues later" },
      { label: "Ingest missing / better data first", description: "Set up an ingestion pipeline, then come back to model" },
      { label: "Point me to the right data", description: "I'll specify a different schema or table" }
    ]
  }]
})
```

**No data question** (when Lakehouse has no raw data at all):
```
question({
  questions: [{
    question: "No raw data found in Lakehouse. What's your data source?",
    options: [
      { label: "Relational database (MySQL / PostgreSQL / SQL Server)", description: "Batch sync or CDC → clickzetta-data-ingest-pipeline" },
      { label: "Kafka / message queue", description: "Real-time ingestion → clickzetta-kafka-ingest-pipeline" },
      { label: "Files (OSS / S3 / local CSV)", description: "File import pipeline → clickzetta-data-ingest-pipeline" },
      { label: "I'll prepare the data myself", description: "Come back when data is ready" }
    ]
  }]
})
```

**Model confirmation question** (after inference, step 3):
```
question({
  questions: [{
    question: "Here's the proposed modeling plan. How would you like to proceed?",
    options: [
      { label: "Confirm all", description: "Generate all models as proposed" },
      { label: "Adjust some models", description: "I want to change materialization type or strategy for specific models" },
      { label: "Partial modeling", description: "Only model a subset of the tables" }
    ]
  }]
})

## Key Constraints

- `database: "{{ target.database }}"` in sources.yml — resolves to workspace name at runtime; never hardcode the workspace name
- Incremental models published to Studio require Agent SQL rewriting (see `clickzetta-dbt-studio-pipeline`)
- Record incremental fields in each incremental model's schema.yml `meta` block:
  ```yaml
  meta:
    incremental_field: updated_at      # incremental filter field name
    incremental_strategy: merge        # incremental strategy
  ```
  This is the standard interface read by `clickzetta-dbt-studio-pipeline` — without it, the agent cannot auto-detect incremental fields during Studio publishing and will need to ask the user.

## Generated File Structure

Generate files in the following directory structure after confirmation:

```
models/
├── staging/
│   ├── stg_{source}_{table}.sql    # one staging model per raw table
│   └── schema.yml                  # sources definition + column-level tests
├── marts/
│   ├── dim_{entity}.sql            # dimension tables
│   ├── fct_{event}.sql             # fact tables
│   └── schema.yml
└── snapshots/                      # only create when SCD requirements exist
    └── {table}_snapshot.sql
```

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
| Need to batch sync data from database / files | `clickzetta-data-ingest-pipeline` |
| Need real-time ingestion from Kafka / message queue | `clickzetta-kafka-ingest-pipeline` |
| Need CDC real-time sync from source database | `clickzetta-cdc-sync-pipeline` |

## Completion Criteria

- `dbt test` 0 errors
- Incremental fields recorded in schema.yml `meta` (for use by `clickzetta-dbt-studio-pipeline`)

## Next Steps After Modeling (proactively present to user)

Present the following options after modeling is complete — let the user choose the direction:

**A. Publish to Studio + configure scheduled execution** → `clickzetta-dbt-studio-pipeline`
Publish all model code as assets to Studio; configure cron auto-scheduling for table/incremental/snapshot models.

**B. Connect BI tools and start reporting** → `clickzetta-bi-connect`
Connect marts layer tables to Tableau / Metabase / FineReport or other BI tools for direct query and analysis.

**C. Configure data quality monitoring**
Add singular tests or integrate DQC for key metrics (daily order count, total revenue) with threshold alerts.

**D. Continue expanding models**
Add new business domain models, or optimize existing models (add indexes, partitioning, adjust VCluster).

**E. Verify data first**
Query marts layer manually with `cz-cli sql` or BI tools to confirm data looks correct before deciding next steps.

Don't only suggest Studio scheduling — the user may be more urgently interested in connecting BI or verifying data. Let them choose.
