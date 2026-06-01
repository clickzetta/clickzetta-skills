---
name: clickzetta-batch-sync-pipeline
description: |
  Create and manage ClickZetta Lakehouse batch sync tasks, supporting both single-table and multi-table modes.
  Single-table mode is suitable for simple source-to-target table sync; multi-table mode supports full database mirror,
  multi-table mirror, and sharded table merge.
  Triggered when the user says "batch sync", "offline sync", "sync database to Lakehouse", "full database migration",
  "multi-table sync", "periodic sync", "scheduled data sync", "sharded table merge", "offline data migration".
  Covers single-table/multi-table batch sync task creation, data source configuration, column mapping,
  sync rules, scheduling, deployment, and task operations — all ClickZetta Studio specific logic.
  Keywords: batch sync, offline sync, full load, mirror, multi-table sync, scheduled sync
---

# Batch Sync Pipeline Workflow

## Wizard: Collect Required Information

Before creating a sync task, use an interactive question tool (e.g., `question`) to collect the following information via option menus. If no such tool is available, list all questions in text at once:

Ask the user three questions: (1) What is the data source type — MySQL (e.g. aliyun_mysql), PostgreSQL (e.g. pg_prod), SQL Server, or OSS/S3/COS object storage? (2) What is the sync scope — single-table sync, multi-table mirror (entire database or selected tables), or sharded table merge? (3) What write mode — full overwrite (OVERWRITE, recommended) or incremental append (APPEND)?

After collecting the above, also confirm: target schema (e.g., `ods`) and schedule time (e.g., daily at 02:00). These can be asked after the user responds, or inferred from context.

**If the user has already provided sufficient information, proceed directly to the workflow without showing the menu.**

---

## Prerequisites

- ClickZetta Lakehouse Studio account with permissions to create sync tasks and target tables
- Source data source already configured in Studio (with SELECT permission)
- Target Lakehouse data source available (with CREATE and INSERT permissions)
- cz-cli installed and profile configured (verify with `cz-cli profile status`)

---

## Applicable Scenarios

- Periodically sync data from external databases (MySQL / PostgreSQL / SQL Server, etc.) to Lakehouse
- Single-table batch sync: simple source table → target table periodic sync
- Multi-table batch sync: full database migration, multi-table batch sync, sharded table merge
- Low data freshness requirements — batch updates on daily/hourly schedules

---

## Mode Selection

| Dimension | Single-table Batch Sync | Multi-table Batch Sync |
|-----------|------------------------|----------------------|
| Task Type ID | `1` (DI/INTEGRATION) | `291` (MULTI_DI) |
| Sync Granularity | One source table → one target table | Full database / multiple tables → multiple target tables |
| Use Case | Simple sync, fine-grained single-table control | Full database migration, batch sync, sharded table merge |
| Schema Evolution | Not supported | Supported (new columns auto-adapted) |
| Auto Table Creation | Manual or quick-create required | Auto-creates target table if not exists |
| Write Mode | Determined by data source | overwrite / upsert selectable |

> **Important**: Both task types are UI_ONLY types — task content must be configured in the Studio Web UI.
> cz-cli handles task creation, scheduling, deployment, and operations; data source selection and column mapping are configured in Studio UI.

---

## Workflow

> **Important**: Batch sync task **content configuration** (source table selection, column mapping, sync rules, etc.) must be completed in the Studio Web UI.
> cz-cli handles task creation, scheduling, deployment, and operations; data source selection and column mapping are configured in Studio UI.

### Step 1: Create Task with cz-cli

```bash
# Single-table batch sync (task_type=1, i.e., DI/INTEGRATION)
cz-cli task create "sync_orders_daily" --type DI --folder <folder_name>

# Multi-table batch sync (task_type=291, i.e., MULTI_DI)
cz-cli task create "sync_ecommerce_db" --type MULTI_DI --folder <folder_name>
```

The command returns `task_id` and `studio_url`. Complete data source configuration at the `studio_url`.

### Step 2: Configure Sync Content in Studio UI

Open the `studio_url` returned in Step 1 and complete the following in Studio:

**Source Data Configuration**
- Select source data source type and connection (supported types are shown in Studio UI; use `cz-cli datasource list` to view configured data sources)
- Single-table: specify schema and table name
- Multi-table: select full database / check multiple tables / configure merge rules

**Target Settings**
- Select target Lakehouse data source and workspace
- Configure target schema and table name
- Multi-table mode supports naming rules (with `{SOURCE_DATABASE}`, `{SOURCE_TABLE}` variables)

**Sync Rules (Multi-table mode)**
- Schema Evolution: new columns from source are auto-adapted; deleted columns are written as Null
- Write Mode: non-primary-key tables → overwrite; primary-key tables → overwrite or upsert

### Step 3: Debug Run in Studio UI

Click the "Run" button to debug and verify data source connectivity and configuration.

### Step 4: Configure Scheduling and Deploy with cz-cli

```bash
# Configure schedule (see --help for parameters)
cz-cli task save-cron <task_name> --help

# Deploy task
cz-cli task deploy <task_name> -y
```

> Batch sync tasks (task_type=1 and 291) must use a Sync VCluster — general-purpose or analytics VClusters are not supported.

### Step 5: Verify and Monitor

```bash
cz-cli runs list --task <task_name>      # View run history
cz-cli runs detail <run_id>              # View run details
cz-cli attempts log <run_id>             # View execution logs
cz-cli runs refill <task_name> --help    # Backfill data (--help for parameters)
```

---

## Task Operations

| Operation | cz-cli Command | Description |
|-----------|---------------|-------------|
| Undeploy | `cz-cli task undeploy <task> -y` | Stop task and remove from scheduler (irreversible) |
| Backfill | `cz-cli runs refill <task> --from D --to D -y` | Backfill data for historical periods |
| View Dependencies | `cz-cli runs deps <task>` | View published upstream/downstream dependencies |
| View Runs | `cz-cli runs list --task <task>` | View run instance list |

Multi-table batch sync tasks are managed in Studio under "Task Operations" → "Scheduled Tasks", where you can view:
- Task Instance Tab: read/write row counts and sync rate per table
- Sync Objects Tab: mapping of all source tables to target tables

---

## Delivery Acceptance Checklist

After the sync task is deployed and running, **verify each item**:

```sql
-- 1. Row count comparison: target table row count matches source
SELECT COUNT(*) FROM <ods_schema>.<table>;
-- Compare with source MySQL/PG: SELECT COUNT(*) FROM <table>

-- 2. Key field non-null rate
SELECT
  COUNT(*) AS total,
  COUNT(key_field) AS non_null,
  ROUND(COUNT(key_field) * 100.0 / COUNT(*), 2) AS non_null_pct
FROM <ods_schema>.<table>;
```

**Acceptance Criteria:**
- [ ] Target table row count matches source
- [ ] Key field non-null rate meets expectations
- [ ] Latest task run status is SUCCESS
- [ ] Column type mapping is correct (pay attention to BIT/ENUM/TEXT and other heterogeneous types)
- [ ] Cron schedule is configured correctly; next execution time is as expected

---

## Troubleshooting

| Issue | Investigation |
|-------|--------------|
| Task creation failed | Verify account has task creation permissions; check if folder ID exists |
| Source connection failed | Check data source connection info, network reachability, account permissions |
| Column mapping failed | Check column type compatibility between source and target tables |
| Slow sync speed | Adjust concurrency (max 10) and sync rate; check source database load |
| Schema Evolution failed | Primary key column changes not supported; type changes only support same-type widening (int8→int16→int32→int64) |
| Partial table failure in multi-table sync | Check per-table status in instance detail "Sync Objects" tab; failed tables can be re-run individually |
| Data inconsistency in upsert mode | Verify target table has correct primary key definition; check for primary key conflicts in source data |
| Wrong VCluster type | Batch sync must use Sync VCluster — verify type with `SHOW VCLUSTERS` |

---

## Notes

**Permission Requirements**
- Source: the account configured in the data source must have SELECT permission
- Target: the task owner must have CREATE and INSERT permissions

**Performance Considerations**
- Configure concurrency appropriately to avoid excessive load on the source database
- First execution initializes all sync objects and may take longer
- Schedule execution during low-load windows on the source database

**Schema Evolution Limitations (Multi-table Batch Sync)**
- Primary key column changes are not supported (Lakehouse primary key table limitation)
- Column type changes only support same-type widening (int8 → int16 → int32 → int64)
- Cross-type conversions are not supported (e.g., int → double)

**Supported Data Sources**
- Source: relational databases (MySQL, PostgreSQL, SQL Server, etc.) and their cloud variants (Aurora, PolarDB, etc.). The specific supported list is shown in Studio UI; use `cz-cli datasource list` to view configured data sources
- Target: Lakehouse
