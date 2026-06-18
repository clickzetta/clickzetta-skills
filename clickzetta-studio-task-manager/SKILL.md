---
name: clickzetta-studio-task-manager
description: |
  Manage ClickZetta Lakehouse Studio tasks: task types (data development SQL/Python/Shell, batch sync
  INTEGRATION/MULTI_DI, real-time CDC MULTI_REALTIME, Kafka streaming REALTIME), folder organization,
  cz-cli task commands, scheduling (7-field cron + Quartz quirks), dependency management,
  Python task creation + save-script, DRAFT/offline state control, and troubleshooting.
  Implements "separation of DDL and pipeline management": DDL tasks as drafts,
  ETL tasks with scheduling, Dynamic Tables with auto-refresh.
  Triggered when the user says "create Studio task", "task folder", "task scheduling", "cz-cli task",
  "task dependency", "task failed", "task status", "ETL task orchestration", "task management",
  "DDL task", "scheduling DAG", "Studio task", "task types", "which sync to choose",
  "offline sync", "batch sync", "CDC sync", "Kafka streaming", "Python task", "save-script",
  "undeploy", "task cron", "WHERE condition".
  Keywords: Studio task, task management, cz-cli task, scheduling, DAG, DDL draft, ETL pipeline,
  task folder, task types, offline sync, CDC, INTEGRATION, MULTI_DI, MULTI_REALTIME, REALTIME,
  Python task, save-script, undeploy, DRAFT, cron
---

# ClickZetta Studio Task Management

See [references/engineering-sop.md](references/engineering-sop.md) for the complete new project launch process, incremental iteration guide, and delivery checklist.
See [references/troubleshooting.md](references/troubleshooting.md) for common issues, type mapping, scheduling best practices, sync task troubleshooting, and multi-environment management.

**When the user is writing Python task code** (Session creation, file I/O, watermark patterns, Databricks migration), also read the `clickzetta-zettapark` skill → [references/studio-task-pattern.md](../clickzetta-zettapark/references/studio-task-pattern.md) for Studio-specific patterns (get_active_lakehouse_engine, save-script, task parameters, volume paths).

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

## cz-cli task Commands

### Folder Management

```bash
cz-cli task create-folder <folder_name>       # Create folder (NOT "task folder create")
cz-cli task folder-tree                       # Show full folder hierarchy
cz-cli task list-folders                      # List top-level folders
cz-cli task delete-folder <folder> -y         # Delete empty folder
```

### Query Tasks

```bash
cz-cli task list [--folder <folder>]          # List tasks
cz-cli task search <keyword>                  # Search by name with resolved path
cz-cli task get <task_id>                     # Get task metadata
cz-cli task status <task_id>                  # Combined draft + deployed status
cz-cli task content <task_id>                 # Get task script + schedule config
cz-cli task deps <task_id>                    # Show draft dependencies
cz-cli task downstream <task_id>              # Downstream tasks that depend on this
cz-cli task schedule-info <task_id>           # Published schedule state
```

### Data Development Tasks (SQL / Python / Shell)

```bash
# Create
cz-cli task create <name> --type PYTHON --folder <folder>
cz-cli task create <name> --type SQL --folder <folder>
cz-cli task create <name> --type SHELL --folder <folder>

# Save content
cz-cli task save-content <task> --content "<sql>"        # SQL tasks
cz-cli task save-script <task> --script-file ./main.py   # Python tasks (use save-script, not save-content)

# Python task: one-step create + configure
cz-cli task create-setup <name> --type PYTHON --folder <folder> \
  --script-file ./main.py --cron '0 0 6 * * * *' --vc default
```

### Scheduling (Cron) — 7-Field Format

> ⚠️ **Lakehouse uses 7-field cron: `sec min hour day month weekday year`** (NOT 5-field).
> Storage converts input to Quartz-style `0 00 02 * * ? *` — the `?` is normal.
> `*` in hour field is rejected on some instances — use `0-23` range: `0 0 0-23 * * * *`.

```bash
# Set cron (preserves non-cron settings like deps/retry/VC)
cz-cli task save-cron <task> --cron '0 0 6 * * * *'      # Daily at 06:00
cz-cli task save-cron <task> --cron '0 0 0-23 * * * *'    # Every hour (use range, not *)
cz-cli task save-cron <task> --cron '0 0 */2 * * * *'     # Every 2 hours
cz-cli task save-cron <task> --cron '0 30 6 * * * *'      # Daily at 06:30
```

| Conventional | Lakehouse 7-field | Meaning |
|---|---|---|
| `0 2 * * *` (5-field) | `0 0 2 * * * *` | Daily at 02:00 |
| `0 * * * *` (5-field) | `0 0 0-23 * * * *` | Every hour (range, not `*`) |
| `*/2 * * * *` (every 2h) | `0 0 */2 * * * *` | Every 2 hours |
| `30 2 * * *` (5-field) | `0 30 2 * * * *` | Daily at 02:30 |

Preview future run times:
```bash
cz-cli task cron-preview '0 0 6 * * * *'
```

### Dependency & Retry Configuration

```bash
# Set dependencies + retry + timeout (preserves cron)
cz-cli task save-config <parent_id> \
  --dep-tasks '[{"taskId":<child_id>,"taskName":"<name>"}]' \
  --retry-count 3 --retry-interval 5 --retry-unit m \
  --timeout 120 --timeout-unit m --vc default

# Note: the old `--deps replace` flag is no longer used.
# `save-config` handles non-cron config; `save-cron` handles cron.
# The two are orthogonal — use both for a complete schedule config.
```

### Deploy and Execute

```bash
# Lifecycle
cz-cli task deploy <task> [-y]                # Publish/online (alias: online)
cz-cli task undeploy <task> -y                 # Take offline (alias: offline) — DRAFT for SQL/Python, stopped for sync
cz-cli task delete <task> -y                   # Delete (must undeploy first for published tasks)

# Ad-hoc execution
cz-cli task execute <task> [--vc <vc>]         # Execute once (does NOT follow scheduling deps)
cz-cli task start <task>                       # Start a CDC/streaming task
cz-cli task stop <task>                        # Stop a CDC/streaming task

# Monitoring
cz-cli runs list [--task <id>] [--limit 10]    # List run instances
cz-cli runs logs <run_id>                      # View execution log (NOT "task logs")
cz-cli runs detail <run_id>                    # Full run metadata
cz-cli runs wait <run_id>                      # Poll until run completes
cz-cli task stats                              # Task + run summary statistics
```

### Sync Task Creation — Four Flavors

#### 1. Single-table Offline Batch Sync (INTEGRATION, task_type=10)

3-step flow — source probing → config → save:

```bash
# Step 1: Create and probe source schema
cz-cli task create-offline-sync <name> \
  --folder <folder> --source <ds_name> \
  --source-db <db> --source-table <table> \
  --target-schema <schema> --target-table <table>

# Step 2: Re-fetch schema with Agent review (produces recommendations: splitPk, WHERE, write_mode)
cz-cli task offline-sync-schema <task_id> \
  --source <ds> --source-db <db> --source-table <table> \
  --target-schema <schema> --target-table <table>

# Step 3: Save with Agent-generated config JSON
cz-cli task save-offline-sync <task_id> \
  --config '<json>' --vc <integration_vc> --target-schema <schema>

# If save-offline-sync returns create_table_ddl:
#   write DDL to file → cz-cli sql --file /tmp/table.sql --write → THEN deploy
cz-cli task save-cron <task_id> --cron '0 0 2 * * * *' --vc <integration_vc>
cz-cli task deploy <task_id> -y
```

#### 2. Multi-table Offline Batch Sync (MULTI_DI, task_type=291)

One-step create + configure (use `--tables` to avoid syncing entire database including system tables):

```bash
cz-cli task create-batch-sync <name> \
  --folder <folder> --source <ds_name> \
  --database <db> --tables "t1,t2,t3" \          # Always specify tables!
  --pipeline-type 1 \                             # 1=mirror, 2=merge
  --batch-size 4 --connections 4 --parallelism 4 \
  --pk-write-mode OVERWRITE --non-pk-write-mode OVERWRITE \
  --cron '0 0 2 * * * *'                          # --cron now takes effect at creation
```

**⚠️ `--tables` is critical** — omitting it syncs ALL tables in the database. MySQL instances often expose 35K+ system tables; syncing everything can take days and exhaust resources.

#### 3. Multi-table Real-time CDC (MULTI_REALTIME, task_type=281)

```bash
# Whole-database mirror with full+incremental
cz-cli task create-realtime-sync <name> \
  --folder <folder> --source <ds_name> \
  --database <db> --tables "t1,t2" \              # Or omit for whole-database (be careful)
  --pipeline-type 3 \                              # 1=tables mirror, 2=merge, 3=whole-database
  --sync-mode 1 \                                  # 1=full+incremental, 2=incremental only
  --skip-check                                     # Skip CDC prerequisite check if known-good

# Deploy → start
cz-cli task deploy <task_id> -y
cz-cli task start <task_id>
```

#### 4. Kafka Streaming Sync (REALTIME)

```bash
cz-cli task create-stream-sync <name> \
  --folder <folder> --source <kafka_ds> \
  --topic <topic> --target-schema <schema> --target-table <table> \
  --mode latest-offset --codec json \
  --cron '0 */10 * * * * *'                       # heartbeat cron

# Creates DDL for target table (5 columns: __key__, __value__, __partition__, __offset__, __timestamp__)
# Note: field mapping must be configured via Studio UI before meaningful data arrives
```

---

## Sync Task VC (Virtual Cluster)

Sync tasks run on a dedicated INTEGRATION-type VCluster — not the default query VCluster.

```bash
# Find sync-capable VClusters
cz-cli sql --sync "SHOW VCLUSTERS"

# Check a specific VC's type (vcluster_type must be INTEGRATION)
cz-cli sql --sync "DESC VCLUSTER <name>"

# Resume if SUSPENDED (common after inactivity)
cz-cli sql --sync "ALTER VCLUSTER <name> RESUME" --write
```

If no INTEGRATION VC exists:
```sql
CREATE VCLUSTER IF NOT EXISTS sync_vc VCLUSTER_TYPE=INTEGRATION VCLUSTER_SIZE=1 AUTO_RESUME=TRUE;
```

---

## INTEGRATION Config JSON + WHERE Condition Guide

`save-offline-sync --config` requires a complete JSON with `templateKey`, `sourceConnection`, `sinkConnection`, `jobs[]`. The `offline-sync-schema` output includes a `source_params_template` that can be used as the base.

### WHERE Condition Syntax

> ⚠️ **WHERE goes to the source database via JDBC** — use the source database's SQL dialect, NOT Lakehouse SQL.

| Source | Correct WHERE | Wrong |
|---|---|---|
| PostgreSQL | `created_at >= '2026-01-01'::date` (PG cast) | `created_at >= DATE '2026-01-01'` |
| PostgreSQL | `id >= 0 AND id <= 100` | — |
| MySQL | `created_at >= '2026-01-01'` | `created_at >= DATE '2026-01-01'` |
| SQL Server | `created_at >= '2026-01-01'` | — |

### Scheduling Variables

```sql
-- ${bizdate} is replaced by the scheduler engine at trigger time
-- ⚠️ Manual execute does NOT resolve ${bizdate} — use hardcoded dates for testing
WHERE created_at >= '${bizdate}'::date   -- PG: daily incremental
WHERE dt >= '${bizdate}'                 -- MySQL: daily incremental
```

| Behavior | Detail |
|---|---|
| `${bizdate}` in scheduler | Replaced with the current business date (e.g., `2026-06-17`) |
| `${bizdate}` in manual `execute` | **NOT replaced** — sends literal `${bizdate}` to source DB → error |
| Empty WHERE `""` | **Rejected** by CLI — empty string WHERE is now intercepted |
| No WHERE (initial full load) | Omit the `where` key from `params` entirely, or set `writeMode: OVERWRITE` |

### writeMode Behavior

| writeMode | Behavior | 0 rows from source |
|---|---|---|
| `OVERWRITE` | Truncate target, then INSERT | **⚠️ Target NOT truncated** — old data remains |
| `APPEND` | INSERT without truncating | Target unchanged (correct for incremental) |

> ⚠️ **OVERWRITE + WHERE returning 0 rows does NOT clear the target table.** The sync engine skips the truncate step when the source query produces no rows. For the first incremental window after a full load, ensure the WHERE covers at least the current day to avoid data gaps.

### Source Type Mapping Principles

When building the `sink.columns` array, map source types to Lakehouse types following these principles:

| Principle | Example |
|---|---|
| String: all char/text/varchar → STRING (safe default) | PG `varchar`, `text`, `bpchar` → `STRING` |
| Numeric: INT family maps directly | PG `int4`→`INT`, `int8`→`BIGINT` |
| Decimal: preserve precision | PG `numeric(10,2)`→`DECIMAL(10,2)`, `money`→`DECIMAL(19,4)` |
| Time: use TIMESTAMP for all datetime | PG `timestamp`, `timestamptz`→`TIMESTAMP` |
| PG special: `serial`→`INT`, `vector`→`STRING` or `VECTOR(FLOAT, dim)` | Confirm dimension with user |
| PG `bit(1)`/`bit(n)` without context → `STRING` (safe); DWD can cast | Avoid `BOOLEAN` for BIT(1) per ODS principle |
| PG `_text`, `_int4` (underscore arrays) → `ARRAY<element_type>` | `_text`→`ARRAY<STRING>` |
| MySQL `BIT(1)` → `TINYINT` (ODS), `CAST(... AS BOOLEAN)` (DWD) | `BOOLEAN` may cause sync failures |
| **Column name case**: PG `a` and `A` collide in Iceberg → rename one column in sink | Use `COMMENT 'original PG column A'` on renamed column |
