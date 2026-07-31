---
name: clickzetta-dbt-studio-pipeline
description: |
  Publish all dbt models to Studio as assets and configure scheduled execution.
  All dbt model SQL code is centrally managed in Studio; models needing periodic execution
  get scheduling configuration. Reads dbt manifest.json, rewrites incremental SQL for
  scheduling parameters, guides user confirmation, then deploys automatically.
  Trigger when the user wants dbt models to run or be scheduled in Studio — mentions
  "publish dbt to Studio", "dbt scheduling", "dbt asset management", "dbt manifest",
  "dbt Studio tasks", "dbt pipeline deployment", or asks "how do I schedule dbt".
  Keywords: dbt Studio, publish dbt, dbt scheduling, dbt manifest, Studio asset, dbt deployment
---

# clickzetta-dbt-studio-pipeline

See [references/studio-task-sop.md](references/studio-task-sop.md) for complete cz-cli task command reference.
See [references/parameter-guide.md](references/parameter-guide.md) for Studio parameter types and bizdate configuration.

For the **complete end-to-end pipeline architecture** (ingestion → dbt modeling → Studio publishing), use the `clickzetta-dbt-project-setup` skill.

**If the user is migrating an existing dbt project from Databricks / Snowflake / Redshift**, first invoke the `clickzetta-sql-migration` skill (covers adapter switch, `dbt_project.yml` cleanup, incremental strategy migration, and macro compatibility). Return here for Studio deployment after the project compiles on ClickZetta.

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

## Workflow

This skill runs as a series of conversation turns. Each turn ends with a question to the user — no Studio tasks are created until the user responds to that turn's question.

---

### Turn 0 — Read manifest, explain scope, ask profile

Read `target/manifest.json`. If it doesn't exist or is stale, run `dbt compile --profiles-dir .` first.

Count: total models (N), models needing scheduling (table/incremental/snapshot = M), dynamic_table models (auto-refresh, no scheduling needed).

Then explain to the user what this session covers — fill in the actual N and M:

> This session covers two things, both required:
>
> **① Asset management (all N models)**: Each model gets two Studio records — a DDL statement in `00_ddl` (what this table is), and the ETL execution logic in the layer directory (how it runs). Kept in DRAFT so the team can see the full pipeline in Studio.
>
> **② Scheduling (M models — table/incremental/snapshot only)**: Configure cron, dependencies, deploy as PUBLISHED.
>
> dynamic_table models ({count} total): no scheduling needed — `refresh_interval` drives auto-refresh. view models: no scheduling needed.

Then run `cz-cli profile list` and ask: "Which profile should I use for deployment?"

**Stop here.**

---

### Turn 1 — Confirm directory structure and scope

Read the dbt project's `dbt_project.yml` to determine the actual layer names (staging/marts, bronze/silver/gold, ods/dwd/ads, or custom). Build the Studio directory structure to match.

Propose the Studio directory structure based on the actual layers found:
```
{project}_dw/
├── 00_ddl/          ← initialization DDL for table/incremental/view only (not dynamic_table)
├── 01_{layer1}/     ← e.g. 01_staging/ or 01_bronze/
├── 02_{layer2}/     ← e.g. 02_marts/ or 02_silver/
├── 03_{layer3}/     ← e.g. 03_gold/ or 03_dwd/ (if exists)
├── ...              ← additional layers as needed
├── {N}_snapshots/   ← snapshot ETL, PUBLISHED + scheduled
└── {N+1}_dqc/       ← data quality checks, optional
```
Naming: DDL tasks as `ddl_{layer}_{model}`, ETL/DT tasks as `{layer}_{model}`.

Ask: "Does this structure work, or do you want to customize? Also, are there any models you want to exclude from publishing?"

**Stop here.**

---

### Turn 2 — Show incremental SQL rewrites, confirm schedule

If there are incremental models: show all before/after SQL diffs in one message (not one by one). Ask the user to confirm all or flag specific ones to adjust.

Also ask: "What schedule for the M models that need it?" (daily at 03:00 for T+1 / hourly / custom cron) and "Which VCluster?" (default or specify).

**Stop here.**

---

### Turn 3 — Final confirmation, then execute

Show the complete execution plan:
- Total tasks to create (N DDL + ETL tasks)
- Directory structure
- Schedule times and VCluster
- Which models are DRAFT only vs PUBLISHED + scheduled

Ask: "Confirm and deploy?"

Only after confirmation: create all Studio tasks, upload SQL, configure schedules and dependencies.

---

### Turn 4 — Verify and wrap up

After deployment:
1. Check row counts in target tables, confirm task status
2. Output Studio links for all tasks
3. Note: DQC tasks need manual configuration in Studio UI (cz-cli doesn't support DQC type yet)
4. Suggest next steps: verify scheduling tomorrow, configure BI connections, set up alerts

## SQL Content Rules

Key fields per model in `manifest.json`:
- `config.materialized`: determines DDL wrapping and whether scheduling is needed
- `depends_on.nodes`: upstream dependencies (for Studio task dependency config)
- `meta.incremental_field` / `meta.incremental_strategy`: written by modeling skill

Each model gets **one or two tasks** in Studio depending on materialization type. The directory structure mirrors the dbt project's layer structure:

```
{project}_dw/
├── 00_ddl/        ← initialization DDL for table/incremental/view (not dynamic_table)
├── 01_{layer1}/   ← matches dbt project layer (staging, bronze, ods, etc.)
├── 02_{layer2}/   ← matches dbt project layer (marts, silver, dwd, etc.)
└── ...
```

Task naming:
- DDL tasks (inside `00_ddl/`): named `ddl_{layer}_{model}` — e.g. `ddl_staging_stg_orders`
- ETL/DT tasks (inside layer dirs): named `{layer}_{model}` — e.g. `stg_orders`, `fct_orders`

**`00_ddl/` directory** — initialization DDL for table/incremental/view only. `dynamic_table` does NOT go here.

| materialization | SQL | Task name |
|---|---|---|
| `view` | `CREATE OR REPLACE VIEW {db}.{schema}.{model} AS {compiled_sql}` | `ddl_{layer}_{model}` |
| `table` | `CREATE OR REPLACE TABLE {db}.{schema}.{model} AS {compiled_sql}` | `ddl_{layer}_{model}` |
| `incremental` | `CREATE TABLE IF NOT EXISTS {db}.{schema}.{model} AS {compiled_sql}` | `ddl_{layer}_{model}` |
| `snapshot` | Not uploaded — managed by dbt | — |

**Layer directories (`01_staging/`, `02_marts/`, etc.)** — one task per model in its own layer:

| materialization | Task type | Content | State | Scheduling |
|---|---|---|---|---|
| `view` | SQL | `CREATE OR REPLACE VIEW ...` | DRAFT | None — computed at query time |
| `table` | SQL | `CREATE OR REPLACE TABLE ... AS {compiled_sql}` | PUBLISHED | Scheduled |
| `incremental` | SQL | Incremental-filtered SQL with bizdate param | PUBLISHED | Scheduled |
| `dynamic_table` | SQL | `CREATE OR REPLACE DYNAMIC TABLE ... REFRESH INTERVAL {N} MINUTE vcluster {vc} AS {compiled_sql}` | DRAFT | None — auto-refreshes |
| `python` | PYTHON | The model's `.py` source code (the `model(dbt, session)` function) | DRAFT | None — executed via `dbt run` |
| `snapshot` | — | Not uploaded — managed by dbt | — | — |

`python` models belong in their layer directory (same as SQL models). Use task type `PYTHON` when creating via `cz-cli task create --type PYTHON`. The content is the model's `.py` file. No DDL entry in `00_ddl/` needed — Python models write their own output table.

For `dynamic_table`, read `refresh_interval` and `refresh_vc` from `manifest.json` → `config` block (set by the modeling skill). Example:
```sql
CREATE OR REPLACE DYNAMIC TABLE quick_start.dbt_demo.stg_customers
  REFRESH INTERVAL 30 MINUTE vcluster default
AS
select ...
```

`{db}` = `target.database`, `{schema}` from manifest's `schema` field.

## Incremental SQL Rewrite Rules

dbt incremental models come in two types — handle them differently:

**Type 1 — Self-driven** (model has `{% if is_incremental() %} where updated_at >= ... {% endif %}`):
- The dbt compiled SQL already contains the incremental filter logic
- Upload the compiled SQL as-is to the ETL directory — **no rewrite needed**
- Must configure upstream data sync task as a dependency so source data is ready before triggering:
  `cz-cli task save-config <task> --deps replace --dep-tasks '[{"taskId": <sync_task_id>}]'`
- If no upstream sync task exists yet, inform the user to create one via `clickzetta-data-ingest-pipeline` first

**Type 2 — Partition-based** (`insert_overwrite` with `partition_by`, no `is_incremental()` filter in the model):
- The dbt compiled SQL is the full SELECT with no time filter
- Rewrite by injecting a WHERE clause with a Studio scheduling parameter:

| Schedule | Time field type | WHERE clause to inject | params |
|---|---|---|---|
| Daily | Date field (dt/date) | `WHERE dt = '${bizdate}'` | `{"bizdate":"bizdate"}` |
| Daily | Timestamp field (*_at/*_time) | `WHERE DATE(col) = '${bizdate}'` | `{"bizdate":"bizdate"}` |
| Hourly | Timestamp field | `WHERE col >= '${start_time}' AND col < '${end_time}'` | `{"start_time":"$[yyyy-MM-dd HH:00:00,-1h]","end_time":"$[yyyy-MM-dd HH:00:00,0h]"}` |
| Full load (table type) | — | No rewrite | none |

**How to tell which type**: check `meta.incremental_strategy` in manifest.json. If `insert_overwrite` with `partition_by` → Type 2. If `merge` or `delete+insert` with `updated_at` filter → Type 1.

**Important**: `save-content --params` automatically declares the corresponding parameter definitions in the Studio task; Studio injects them automatically during scheduling.

## Routing

| Scenario | Route to |
|---|---|
| No dbt project yet | `clickzetta-dbt-project-setup` |
| dbt models not developed yet | `clickzetta-dbt-modeling` |
| Managing Studio tasks only (no dbt involved) | `clickzetta-studio-task-manager` |
