---
name: clickzetta-studio-task-manager
description: |
  Manage ClickZetta Lakehouse Studio tasks, covering task type descriptions (batch sync/multi-table batch sync/
  real-time sync/multi-table real-time sync/data development), task folder organization, task type differentiation,
  cz-cli task command family, scheduling configuration, dependency management, and common issue troubleshooting.
  Implements the "separation of DDL and pipeline management" engineering standard: DDL tasks as drafts,
  ETL tasks with scheduling, Dynamic Tables with auto-refresh.
  Triggered when the user says "create Studio task", "task folder", "task scheduling", "cz-cli task",
  "task dependency", "task failed", "task status", "full database sync task", "ETL task orchestration",
  "task management", "separation of DDL and pipeline", "DDL task", "scheduling DAG", "task folder",
  "Studio task", "batch sync", "real-time sync", "multi-table real-time sync", "data development task",
  "task types", "which sync to choose", "sync task differences".
  Keywords: Studio task, task management, cz-cli task, scheduling, DAG, DDL draft, ETL pipeline, task folder, offline sync, realtime sync, CDC, task types
---

# ClickZetta Studio Task Management

See [references/engineering-sop.md](references/engineering-sop.md) for the complete new project launch process, incremental iteration guide, and delivery checklist.
See [references/troubleshooting.md](references/troubleshooting.md) for common issues, MySQL type mapping, scheduling best practices, and multi-environment management.

## Wizard: Clarify Intent

Upon receiving a task management request, ask what the user wants to do: build a new pipeline from scratch, manage existing tasks (view status, modify config, configure dependencies, rerun, backfill), troubleshoot task issues, or run a standards compliance check.

**If the user has clearly stated what they want to do, proceed directly without asking.**

For **building from scratch**, also collect: business domain/project name, data source type, layering structure.

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

Also run `cz-cli datasource list` to view configured external data sources.

### Step 2: Technical Selection

Ask where the data comes from: external database, Kafka, object storage, Lakehouse internal ETL, end-to-end pipeline, or not sure.

- External database → ask: real-time CDC or batch offline?
- Object storage → ask: SQL Pipe (continuous) or Studio batch sync (periodic)?
- Kafka → ask: SQL Pipe (READ_KAFKA) or Studio real-time sync task?

### Step 3: Plan Confirmation (required, cannot skip)

Present complete plan summary: business scenario, data source, sync method, layering structure, target schema, scheduling. Ask user to confirm or adjust.

After confirmation, route to the appropriate skill:

| Data Source | Method | Skill |
|---|---|---|
| External DB | Real-time single-table CDC | `clickzetta-realtime-sync-pipeline` |
| External DB | Real-time multi-table/full DB CDC | `clickzetta-cdc-sync-pipeline` |
| External DB | Batch offline | `clickzetta-batch-sync-pipeline` |
| Kafka | SQL Pipe | `clickzetta-kafka-ingest-pipeline` |
| Kafka | Studio real-time sync | `clickzetta-realtime-sync-pipeline` |
| Object storage | SQL Pipe | `clickzetta-oss-ingest-pipeline` |
| Object storage | Studio batch sync | `clickzetta-batch-sync-pipeline` |
| Lakehouse internal ETL | — | `clickzetta-sql-pipeline-manager` |
| End-to-end / Not sure | — | `clickzetta-dw-modeling` |

---

## Studio Task Types

| Task Type | Data Source | Run Mode | Freshness | Skill |
|---|---|---|---|---|
| Batch Sync | Relational DB | Scheduled (Cron) | Hourly/daily | `clickzetta-batch-sync-pipeline` |
| Multi-table Batch Sync | Relational DB | Scheduled (Cron) | Hourly/daily | `clickzetta-batch-sync-pipeline` |
| Real-time Sync | **Kafka only** | Continuously running | Seconds/minutes | `clickzetta-realtime-sync-pipeline` |
| Multi-table Real-time (CDC) | MySQL / PostgreSQL | Continuously running | Seconds | `clickzetta-cdc-sync-pipeline` |
| Data Development (SQL/Python/Shell) | Any | Scheduled or manual | Depends on schedule | This skill |

---

## Core Principle: Separation of DDL and Pipeline

| Task Type | Content | Scheduling | Status |
|---|---|---|---|
| **DDL table creation** | CREATE TABLE / SCHEMA | ❌ No Cron, no dependencies | DRAFT |
| **Data sync** | External source → ODS | ✅ Cron (batch) or continuous (real-time) | PUBLISHED |
| **ETL transformation** | ODS→DWD cleaning SQL | ✅ Cron + depends on upstream sync | PUBLISHED |
| **Data quality** | Row count checks, NULL validation | ✅ Cron + depends on ETL | PUBLISHED |
| **DWS/ADS aggregation** | Metric summaries | ❌ Use Dynamic Table, no task needed | — |

> ⚠️ **DDL tasks must never have Cron** — repeated CREATE TABLE causes `SCHEDULE_TASK_HAD_CHILDREN_NODES_EXCEPTION`.
> ⚠️ **Do not create scheduled tasks for DWS/ADS** — Dynamic Tables auto-refresh; extra tasks waste resources.
> ⚠️ **Never use SQL tasks to simulate data sync** — `SELECT FROM EXTERNAL` syntax is not supported.

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

DWS/ADS: Dynamic Tables with `refresh_interval` — **no task needed**.

**Naming conventions:**

| Type | Pattern | Example |
|---|---|---|
| Folder | `{domain}_dw` | `retail_dw` |
| DDL task | `ddl_{layer}_{table}` | `ddl_ods_orders` |
| ETL task | `{layer}_{table}` | `dwd_fct_orders` |
| Sync task | `sync_{source}_to_{target}` | `sync_mysql_to_ods` |

---

## cz-cli task Commands

```bash
# Folder management
cz-cli task folder create <folder_name>
cz-cli task folder list

# Query tasks
cz-cli task list [--folder <folder>]
cz-cli task get <task_id>

# Create task
cz-cli task create --name <name> --type SQL --folder <folder> --vcluster default --sql-file ./sql.sql
cz-cli task create --name <name> --type SINGLE_DI --folder <folder>   # single-table sync

# Content and scheduling
cz-cli task save-content <task_id> --content "<sql>"
cz-cli task save-cron <task_id> --cron '0 30 2 * * ? *'
cz-cli task save-config <task_id> --deps replace --dep-tasks '[{"taskId":<id>}]'

# Deploy and run
cz-cli task deploy <task_id> [-y]
cz-cli task execute <task_id>
cz-cli task run <task_id>
cz-cli task logs <task_id>
```

> ⚠️ **MULTI_DI (full database sync)**: `cz-cli` creates the task framework only. Source/target column mapping **must be configured in Studio UI** before publishing.
