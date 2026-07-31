---
name: clickzetta-studio-task-manager
description: |
  Manage ClickZetta Studio tasks: data development (SQL/Python/Shell), batch sync
  (INTEGRATION/MULTI_DI), real-time CDC (MULTI_REALTIME), Kafka streaming (REALTIME),
  and composite Flow DAGs. Covers folder organization, 7-field cron scheduling,
  dependency management, Python task creation (save-script), DRAFT/offline state control,
  and troubleshooting. Separates DDL (drafts) from ETL pipelines (scheduled).
  Trigger: "create Studio task", "task scheduling", "cz-cli task", "task dependency",
  "DDL task", "ETL orchestration", "sync task", "Flow task", "组合任务",
  "task cron", "save-script", "undeploy", "task failed", "batch sync", "CDC sync".
  Keywords: Studio task, task management, cz-cli task, scheduling, DAG, DDL draft,
  ETL pipeline, sync task, CDC, INTEGRATION, MULTI_DI, MULTI_REALTIME, REALTIME,
  Python task, save-script, undeploy, DRAFT, cron, Flow, composite task, 组合任务
---

# ClickZetta Studio Task Management

See [references/engineering-sop.md](references/engineering-sop.md) for the complete new project launch process, incremental iteration guide, and delivery checklist.
See [references/troubleshooting.md](references/troubleshooting.md) for common issues, type mapping, scheduling best practices, sync task troubleshooting, and multi-environment management.

**When the user is writing Python task code** (Session creation, file I/O, watermark patterns, Databricks migration), also invoke the `clickzetta-zettapark` skill for Studio-specific patterns (get_active_lakehouse_engine, save-script, task parameters, volume paths).

## Wizard: Clarify Intent

Upon receiving a task management request, ask what the user wants to do: build a new pipeline from scratch, manage existing tasks (view status, modify config, configure dependencies, rerun, backfill), troubleshoot task issues, or run a standards compliance check.

**If the user has already stated what they want to do, proceed directly without asking.**

For **building from scratch**, also collect: business domain/project name, data source type, available datasources, and layering structure.

---

## Data Pipeline Wizard (Building from Scratch)

### Step 0: Requirements Input

Ask whether the user has a requirements document (PRD, design doc — paste or upload). If yes, auto-extract business scenario, data sources, target outputs, freshness requirements. If no, ask three questions: (1) Business scenario (BI reports / real-time monitoring / data science / data sharing)? (2) Data consumers (BI tools / analysts / downstream APIs / data scientists)? (3) Freshness requirements (T+1 / hourly / minute-level / second-level CDC)?

Also confirm: core metric definitions and project/domain name (used for folder and schema naming).

### Step 1: Data Exploration (autonomous, no user input needed)

```sql
SHOW SCHEMAS;
SHOW TABLES IN <relevant_schema>;
SELECT table_schema, table_name, ROUND(bytes/1024.0/1024/1024, 2) AS size_gb, row_count
FROM information_schema.tables WHERE table_type = 'MANAGED_TABLE'
ORDER BY bytes DESC NULLS LAST LIMIT 20;
SELECT * FROM <schema>.<table> LIMIT 5;
```

Also run `cz-cli datasource list` to view configured external data sources, and `cz-cli task folder-tree` to see existing folder layout.

### Step 2: Technical Selection

Ask where the data comes from: external database, Kafka, object storage, Lakehouse internal ETL, end-to-end pipeline, or not sure.

- External database → ask: real-time CDC or batch offline?
- Object storage → ask: SQL Pipe (continuous) or Studio batch sync (periodic)?
- Kafka → ask: SQL Pipe (READ_KAFKA) or Studio real-time sync task?

### Step 3: Plan Confirmation (required, cannot skip)

Present complete plan summary: business scenario, data source, sync method, layering structure, target schema, scheduling. If multi-table sync, confirm which **specific tables** to include (omit `--tables` to sync entire database — dangerous for MySQL with system tables). Ask user to confirm or adjust.

After confirmation, route to the appropriate skill:

| Data Source | Method | Skill |
|---|---|---|
| External DB | Real-time single-table CDC | `clickzetta-realtime-sync-pipeline` |
| External DB | Real-time multi-table/full DB CDC | `clickzetta-cdc-sync-pipeline` |
| External DB | Batch offline single-table | `clickzetta-batch-sync-pipeline` |
| External DB | Batch offline multi-table | `clickzetta-batch-sync-pipeline` |
| Kafka | SQL Pipe | `clickzetta-kafka-ingest-pipeline` |
| Kafka | Studio real-time sync | `clickzetta-realtime-sync-pipeline` |
| Object storage | SQL Pipe | `clickzetta-oss-ingest-pipeline` |
| Object storage | Studio batch sync | `clickzetta-batch-sync-pipeline` |
| Lakehouse internal ETL | — | `clickzetta-sql-pipeline-manager` |
| End-to-end / Not sure | — | `clickzetta-dw-modeling` |

---

## Studio Task Types

| Task Type | CLI Create Command | Data Source | Run Mode | Freshness | Skill |
|---|---|---|---|---|---|
| Data Development (SQL/Python/Shell) | `task create --type SQL\|PYTHON\|SHELL` | Any | Scheduled (Cron) or manual | Depends on schedule | This skill |
| **Composite Task (Flow / 组合任务)** | `task create --type FLOW` | Any | Scheduled (Cron) or manual | Depends on schedule | This skill |
| Batch Sync (single-table) | `task create-offline-sync` | MySQL / PG / SQL Server / Oracle | Scheduled (Cron) | Hourly/daily | `clickzetta-batch-sync-pipeline` |
| Batch Sync (multi-table) | `task create-batch-sync` | MySQL / PG / SQL Server / Oracle | Scheduled (Cron) | Hourly/daily | `clickzetta-batch-sync-pipeline` |
| Real-time CDC (multi-table) | `task create-realtime-sync` | MySQL / PG | Continuously running | Seconds | `clickzetta-cdc-sync-pipeline` |
| Kafka Streaming | `task create-stream-sync` | Kafka / AutoMQ | Continuously running | Seconds/minutes | `clickzetta-kafka-ingest-pipeline` |

---

## Core Principle: Separation of DDL and Pipeline

| Task Type | Content | Scheduling | Status |
|---|---|---|---|
| **DDL table creation** | CREATE TABLE / SCHEMA | ❌ No Cron, no dependencies | DRAFT |
| **Data sync** | External source → ODS | ✅ Cron (batch) or continuous (real-time) | PUBLISHED |
| **ETL transformation** | ODS→DWD cleaning SQL/Python | ✅ Cron + depends on upstream sync | PUBLISHED |
| **Data quality** | Row count checks, NULL validation | ✅ Cron + depends on ETL | PUBLISHED |
| **DWS/ADS aggregation** | Metric summaries | ❌ Use Dynamic Table — save DDL as DRAFT task, no scheduling needed | DRAFT |

> ⚠️ **DDL tasks must never have Cron** — repeated CREATE TABLE causes `SCHEDULE_TASK_HAD_CHILDREN_NODES_EXCEPTION`.
> ⚠️ **Do not create scheduled tasks for DWS/ADS** — Dynamic Tables auto-refresh; extra tasks waste resources.
> ⚠️ **Never use SQL tasks to simulate data sync** — `SELECT FROM EXTERNAL` syntax is not supported.

---

## DRAFT State Management

Two different task families behave differently after creation:

| Family | After `create` | After `deploy` | After `undeploy` |
|---|---|---|---|
| **Data Development** (SQL/Python/Shell) | `edit_state=10` (DRAFT) | `edit_state=20` (published) | `edit_state=10` (DRAFT) |
| **Sync Tasks** (INTEGRATION/MULTI_DI/etc.) | `edit_state=published` ⚠️ auto-published | `edit_state=published` | `edit_state=published` (but `cdc_status=stopped/offline`) |

Key implications:
- Sync tasks are **auto-published on creation** — you must `undeploy` to take offline before deleting
- Python/SQL tasks stay DRAFT until explicitly deployed — use `undeploy` to revert after testing
- `undeploy` requires `-y` flag: `cz-cli task undeploy <id> -y`
- Delete a published task: undeploy first, then delete — `undeploy` returns `status: offline`

---

## Task Folder Organization

```
<domain>_dw/
├── 00_ddl/     ← ALL DDL (CREATE TABLE/VIEW/DT) — DRAFT, run once manually
├── 01_sync/    ← Data sync tasks — Cron, runs first in dependency chain
├── 02_ods/     ← ODS ETL (if needed) — DRAFT (view) or Cron (ETL)
├── 03_dwd/     ← DWD ETL — Cron, depends on 01_sync
└── 04_dqc/     ← Data quality checks (optional) — Cron, depends on 03_dwd
```

DWS/ADS: Dynamic Tables with `refresh_interval` — save DDL as **DRAFT task** (code asset), no scheduling or deployment needed.

**Naming conventions:**

| Type | Pattern | Example |
|---|---|---|
| Folder | `{domain}_dw` | `retail_dw` |
| DDL task | `ddl_{layer}_{table}` | `ddl_ods_orders` |
| ETL task | `{layer}_{table}` | `dwd_fct_orders` |
| Sync task | `sync_{source}_to_{target}` | `sync_mysql_to_ods` |

---

## Non-obvious Command Behaviors

Things that `--help` won't warn you about:

**Naming traps**
- Folder: `task create-folder` (NOT `task folder create`)
- Run logs: `runs logs <run_id>` (NOT `task logs`)
- Python content: `task save-script` (NOT `save-content` — they use different APIs)

**Two orthogonal schedule commands** — use both for a complete config:
- `task save-cron` — sets cron expression only, preserves retry/deps/VC
- `task save-schedule` — sets retry/deps/VC/timeout only, preserves cron

**Cron: 7-field format, NOT 5-field**
```
sec min hour dom month dow year
0   0   2    *   *     ?   *     ← Daily at 02:00
```
- `*` in hour field is rejected on some instances — use `0-23` range instead
- Input is converted to Quartz style (`?` replaces `*` in dow) — this is normal
- Use `cz-cli task cron-preview '<cron>'` to verify before saving

**`${bizdate}` is NOT resolved on manual execute**
- Scheduled runs: replaced by the scheduler with current business date
- Manual `cz-cli task execute`: sends literal `${bizdate}` → source DB error
- Workaround: `cz-cli task execute <task> --param bizdate=2026-06-18`

**`flow instances` uses `--flow-instance`, not `--instance`**
- `--instance` is a global option (ClickZetta instance name) — would be swallowed
- Use: `cz-cli task flow instances <flow> --flow-instance <schedule_instance_id>`
- The `schedule_instance_id` comes from `task flow run` output

**Delete requires undeploy first**
- Published tasks (any type): `undeploy -y` → `delete -y`
- Sync tasks stay `edit_state=published` even after undeploy — check `cdc_status` instead

For sync task creation, VC setup, config JSON, WHERE conditions, and type mapping:
→ See [references/sync-task-guide.md](references/sync-task-guide.md)

For composite (Flow) task creation, node management, dependencies, and parameters:
→ See [references/flow-composite-task.md](references/flow-composite-task.md)

For troubleshooting, type mapping, scheduling best practices:
→ See [references/troubleshooting.md](references/troubleshooting.md)

For the complete new project launch process and delivery checklist:
→ See [references/engineering-sop.md](references/engineering-sop.md)


