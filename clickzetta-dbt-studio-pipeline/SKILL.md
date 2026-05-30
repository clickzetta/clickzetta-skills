---
name: clickzetta-dbt-studio-pipeline
description: |
  Publish all dbt models to Studio as assets and configure scheduled execution.
  All dbt model SQL code is centrally managed in Studio (code asset management);
  models that need periodic execution get additional scheduling configuration.
  Reads dbt manifest.json, Agent rewrites incremental SQL to inject scheduling parameters,
  guides user confirmation, then fully automated deployment.

  Trigger this skill whenever the user wants dbt models to run or be scheduled in Studio,
  even if they don't use the word "asset". Typical scenarios:
  - Explicitly mentions publishing/scheduling (publish dbt to Studio, dbt scheduling, dbt asset management,
    dbt manifest, dbt model scheduling, dbt Studio tasks, dbt pipeline deployment,
    publish dbt models as Studio tasks, dbt code assets, Studio unified dbt management)
  - Wants dbt models to run automatically every day / every hour
  - Asks "how do I schedule dbt after it runs"
  - Wants to see dbt SQL code in Studio
  - Wants to configure dependencies or retry policies for dbt models
---

# clickzetta-dbt-studio-pipeline

See [references/studio-task-sop.md](references/studio-task-sop.md) for complete cz-cli task command reference.
See [references/parameter-guide.md](references/parameter-guide.md) for Studio parameter types and bizdate configuration.

---

## Goal

Publish all dbt project SQL code to Studio for unified code management and automated scheduling.
Users don't need to write cz-cli commands manually — you read the manifest, rewrite SQL, configure parameters; users only confirm key decisions.

## Two Goals, Equally Important

**Asset management** (all models): Create SQL tasks in Studio, upload code, keep in DRAFT state.
Purpose: the team can see the complete data pipeline code in Studio, enabling unified code management and traceability.

**Scheduling** (only table/incremental/snapshot): Configure cron + dependencies + deploy as PUBLISHED.
view and dynamic_table don't need scheduling — view is computed at query time, dynamic_table has its own refresh mechanism; scheduling would cause duplicate execution.

Both goals must be completed — neither can be skipped. Asset management is the foundation; scheduling is incremental configuration on top of it.

## Opening Statement (must say first, before any action)

After the skill triggers, **the first thing is to explain to the user what will be done this session** — don't jump straight to technical operations. Explain in plain language:

> This session covers two things, both required:
>
> **① Asset management (all N models)**: Each model gets two Studio records — a DDL statement (`CREATE OR REPLACE TABLE/VIEW AS ...`) in the `00_ddl` directory, and the ETL execution logic in the layer directory (incremental-filtered SQL or full-rebuild SQL). Kept in DRAFT state so the team can see the complete data pipeline definition and execution logic in Studio.
>
> **② Scheduling (only table/incremental/snapshot, M models total)**: Configure cron schedule, dependencies, and deploy as PUBLISHED so they run automatically.
>
> dynamic_table with `refresh_interval` set: **no Studio scheduling needed** — the system auto-refreshes on its own schedule. Only create a Studio task for a dynamic_table if it uses manual refresh mode (i.e. you want to trigger `REFRESH DYNAMIC TABLE` as part of a dependency chain).
> view: no scheduling needed — computed at query time.

Then proceed to the key decision points. **Don't skip this opening** — when users say "publish to Studio" they typically only have scheduling in mind and don't know about asset management; if not mentioned, it gets skipped.

## Preparation: Read dbt Compiled Artifacts

Before starting asset management, confirm compiled artifacts exist — asset management uploads compiled SQL, not dbt template syntax; Studio doesn't understand Jinja:

```bash
# If target/ doesn't exist or manifest.json is stale, compile first
dbt compile --profiles-dir .

# Compiled artifact paths
target/manifest.json          # model metadata (materialization type, dependency graph)
target/compiled/<project>/    # compiled SELECT SQL (needs DDL wrapping before upload)
```

Key fields per model in `manifest.json`:
- `config.materialized`: determines DDL wrapping method and whether scheduling is needed
- `depends_on.nodes`: upstream dependencies (used to configure Studio task dependencies, ensuring execution order)
- `meta.incremental_field` / `meta.incremental_strategy`: incremental fields (written by modeling skill)

## SQL Content Rules

Each model corresponds to **two tasks** in Studio, placed in different directories:

**`00_ddl` directory**: DDL create statements defining table structure, for manual execution or initialization:

| materialization | SQL in 00_ddl |
|---|---|
| `view` | `CREATE OR REPLACE VIEW {db}.{schema}.{model} AS {compiled_sql}` |
| `table` | `CREATE OR REPLACE TABLE {db}.{schema}.{model} AS {compiled_sql}` |
| `incremental` | `CREATE TABLE IF NOT EXISTS {db}.{schema}.{model} AS {compiled_sql}` |
| `dynamic_table` | `CREATE DYNAMIC TABLE {db}.{schema}.{model} REFRESH_INTERVAL='...' VC='...' AS {compiled_sql}` |
| `snapshot` | Not uploaded — managed by dbt |

**`01_staging` / `02_marts` etc. directories**: ETL execution logic, the actual content run during scheduling:

| materialization | SQL in ETL directory |
|---|---|
| `view` | Same as DDL (`CREATE OR REPLACE VIEW ...`), rebuilds view definition each run, DRAFT no scheduling |
| `table` | `CREATE OR REPLACE TABLE ... AS {compiled_sql}`, full rebuild |
| `incremental` | Incremental-filtered SQL (see Incremental SQL Rewrite Rules), with bizdate parameter, scheduled execution |
| `dynamic_table` | No ETL task needed — auto-refreshes |
| `snapshot` | Not uploaded |

`{db}` = `target.database` (workspace name), `{schema}` read from manifest's `schema` field.

**The complete meaning of asset management**: each model has two records in Studio — the DDL in `00_ddl` (what this table is) + the execution logic in the ETL directory (how this table runs). Both are required.

## Key Decision Points

Ask the user to confirm each decision before executing. **Do not execute anything before receiving the user's answer** — acting early creates Studio tasks that need manual cleanup. Use AskUserQuestion if available, otherwise present options as a numbered list in text.

1. **cz-cli profile**: Run `cz-cli profile list`, show the available profiles, and ask the user which one to use for deployment.

2. **Studio directory structure**: Propose the recommended structure below and ask the user to confirm or customize.

   ```
   {project}_dw/
   ├── 00_ddl/          ← ALL DDL statements (CREATE TABLE/VIEW/DYNAMIC TABLE), DRAFT, no scheduling
   ├── 01_staging/      ← staging layer ETL (view DDL + SELECT), DRAFT, no scheduling
   ├── 02_marts/        ← marts layer ETL (table/incremental), PUBLISHED, scheduled
   ├── 03_snapshots/    ← snapshot layer, PUBLISHED, scheduled
   └── 04_dqc/          ← data quality checks, optional
   ```

   **Naming conventions** (consistent with `clickzetta-studio-task-manager`):
   - DDL tasks: `ddl_{layer}_{model}` (e.g. `ddl_staging_stg_orders`, `ddl_marts_fct_orders`)
   - ETL tasks: `{layer}_{model}` with no prefix (e.g. `stg_orders`, `fct_orders`)
   - dynamic_table models with `refresh_interval`: **no ETL task needed** — auto-refreshes; only add a Studio task if using manual refresh mode

3. **Asset management scope**: Ask whether to publish all models or exclude specific ones. If excluding, ask which models to skip.

4. **Incremental SQL rewrite**: For each incremental model, show the before/after SQL diff and ask the user to confirm the rewrite. Options: confirm all, or adjust a specific model.

5. **Scheduling configuration**: Ask two things — what schedule (daily at 03:00 for standard T+1, hourly for near real-time, or custom cron) and which VCluster to use (default_ap or specify another).

6. **Final confirmation**: Show the complete execution plan (total task count, directory structure, schedule times) and ask the user to confirm before deploying.


## Incremental SQL Rewrite Rules

dbt compiled SQL is the full version (no incremental filter). Before publishing to Studio, Agent rewrites based on schedule frequency:

| Schedule | Time field type | Rewrite method | params |
|---|---|---|---|
| Daily | Date field (dt/date) | `WHERE dt = '${bizdate}'` | `{"bizdate":"bizdate"}` |
| Daily | Timestamp field (*_at/*_time) | `WHERE DATE(col) = '${bizdate}'` | `{"bizdate":"bizdate"}` |
| Hourly | Timestamp field | `WHERE col >= '${start_time}' AND col < '${end_time}'` | `{"start_time":"$[yyyy-MM-dd HH:00:00,-1h]","end_time":"$[yyyy-MM-dd HH:00:00,0h]"}` |
| Full load (table type) | — | No rewrite | none |

**Self-driven incremental models** (`WHERE updated_at >= (SELECT MAX(updated_at) FROM {{ this }})`):
- SQL itself does not need rewriting — upload as-is to the ETL directory
- But must configure upstream data sync task as a dependency to ensure source data is ready before triggering — **this sync task already exists** (created by `clickzetta-data-ingest-pipeline` etc.); this skill does not create new data pipeline tasks
- Ask user for the upstream sync task name or ID (use `cz-cli task list` to find it), then configure dependency:
  `cz-cli task save-config <task> --deps replace --dep-tasks '[{"taskId": <sync_task_id>}]'`
- If user has no upstream sync task yet, inform them to create one via `clickzetta-data-ingest-pipeline` first, then return to configure the dependency

**Important**: `save-content --params` automatically declares the corresponding parameter definitions in the Studio task; Studio injects them automatically during scheduling.

## Verification and Next Steps

After deployment:
1. Self-verify: check row counts in target tables, confirm task status is online
2. Output Studio direct links for all tasks (`https://{instance}.studio.clickzetta.com/task/{id}`)
3. Inform user: DQC tasks need to be manually configured as DQC type in Studio UI (cz-cli doesn't support this yet)
4. Suggest next steps: verify scheduling tomorrow, configure BI connections, set up alerts

## Routing

| Scenario | Route to |
|---|---|
| No dbt project yet | `clickzetta-dbt-project-setup` |
| dbt models not developed yet | `clickzetta-dbt-modeling` |
| Managing Studio tasks only (no dbt involved) | `clickzetta-studio-task-manager` |
