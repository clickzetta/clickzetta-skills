---
name: clickzetta-cdc-sync-pipeline
description: |
  Create and manage ClickZetta Lakehouse multi-table real-time sync (CDC) tasks, syncing
  MySQL/PostgreSQL databases to Lakehouse. Three sync modes: full database mirror,
  multi-table mirror, sharded table merge. Binlog/WALs-based with full load + incremental sync.
  Triggered when the user says "multi-table real-time sync", "full database sync", "database mirror",
  "CDC full database", "multi-table CDC", "sharded table merge", "MySQL full database sync",
  "PostgreSQL full database sync", "database migration", "sync operations", "sync SOP",
  "Binlog position expired", "full re-sync", "add sync table".
  Covers source DB preparation, sync mode selection, task deployment, operations SOP,
  monitoring/alerting, and troubleshooting — all ClickZetta Studio specific logic.
  Keywords: CDC, real-time sync, MySQL, PostgreSQL, change data capture, mirror, merge, multi-table
---

# Multi-table Real-time Sync (CDC) Pipeline Workflow

See [references/troubleshooting.md](references/troubleshooting.md) for troubleshooting, cz-cli alternative path, and delivery checklist.

## Wizard: Collect Required Information

Ask the user three questions: (1) Source database type — MySQL (Binlog-based) or PostgreSQL (WALs-based, requires v14+)? (2) Sync mode — full database mirror, multi-table mirror, or sharded table merge? (3) Is the source database already prepared (MySQL: Binlog enabled + REPLICATION permission; PG: wal_level=logical)?

Also confirm the target schema (e.g., `ods`).

**If the user has already provided sufficient information, proceed directly without showing the menu.**

## Comparison with Other Sync Methods

| Dimension | Multi-table Real-time Sync (This Skill) | Single-table Real-time Sync | Batch Sync |
|---|---|---|---|
| Task Type ID | `281` | `28` | `10` / `291` |
| Sync Granularity | Full database / multi-table / sharded merge | Single table/topic | Single/multi-table |
| Run Mode | Continuously running (streaming CDC) | Continuously running | Scheduled (batch) |
| Applicable Skill | `clickzetta-cdc-sync-pipeline` | `clickzetta-realtime-sync-pipeline` | `clickzetta-batch-sync-pipeline` |

## Prerequisites

- Source database prepared with CDC permissions (see Source Database Preparation below)
- Source data source configured in Studio UI (not via SQL `CREATE STORAGE CONNECTION` — that only supports object storage and Kafka)
- Sync VCluster available (task_type=281 requires a Sync VCluster)
- cz-cli or MCP tools available

## Environment Detection

```bash
cz-cli --version   # if exists → use cz-cli path (see references/troubleshooting.md)
```
If cz-cli not found, check if MCP `list_data_sources` tool is available. If neither is available, prompt the user to install one.

## Source Database Preparation

### MySQL

| Parameter | Required Value | Query |
|---|---|---|
| `log_bin` | ON | `SHOW GLOBAL VARIABLES LIKE 'log_bin'` |
| `binlog_format` | ROW | `SHOW GLOBAL VARIABLES LIKE 'binlog_format'` |
| `binlog_row_image` | FULL | `SHOW GLOBAL VARIABLES LIKE 'binlog_row_image'` |
| `binlog_expire_logs_seconds` | ≥86400 | — |

Permissions: `SELECT` on information_schema + target tables, `REPLICATION SLAVE`, `REPLICATION CLIENT`.

### PostgreSQL

| Parameter | Required Value |
|---|---|
| `wal_level` | logical |
| `max_replication_slots` | ≥10 |
| `max_wal_senders` | ≥10 |

Permissions: `SELECT` on information_schema, `REPLICATION`, `CREATE` (for publication).

> PostgreSQL: each task needs its own replication slot — never reuse slots across tasks.

## Workflow

### Step 1: Confirm Sync VCluster

```
LH_show_object_list(object_type='VCLUSTERS') → filter for vcluster_type containing SYNC
```

### Step 2: Find Source Data Source

```
list_data_sources → filter by type (MySQL: ds_type=5, PostgreSQL: ds_type=7)
Record datasource_id and datasource_type.
```

### Step 3: Explore Source Data Structure

```
list_namespaces → view source database list
list_metadata_objects → view tables under a database
Confirm sync scope (full database / specific tables / sharded tables).
```

### Step 4: Select Sync Mode

| Mode | pipeline_type | Use Case |
|---|---|---|
| Full database mirror | 3 | Sync all tables, auto-adapts to new tables |
| Multi-table mirror | 1 | Sync selected tables, supports schema change detection |
| Sharded table merge | 2 | Merge sharded tables into a single target table |

### Step 5: Create Task

```
create_task(task_type=281, task_name="cdc_sync_<database>", data_folder_id=<folder_id>)
Record returned task_id.
```

### Step 6: Configure Sync Content

```
save_cdc_realtime_task(
  data_file_id=<task_id>,
  pipeline_type=<mode from Step 4>,
  source_datasource_list=[{"datasourceId": <id>, "datasourceType": <type>}],
  sync_object_list=<tables or database>,
  target_datasource={"datasourceId": <lakehouse_id>, "datasourceType": 1},
  sync_mode=1,   # 1=full load + incremental (recommended), 2=incremental only
  save_mode=2    # 2=append (recommended for new tasks)
)
```

### Step 7: Submit and Deploy

```
publish_task(task_id=<id>, task_version=<version>)
```

> CDC tasks do not start automatically after submission — start manually in Studio UI.

### Step 8: Start the Task

| Start Method | Use Case |
|---|---|
| Stateless start | First start (full load → incremental) |
| Resume from last saved state | Restart after stop |
| Custom start position | Data re-sync (specify binlog file/time or LSN) |

### Step 9: Monitor

After starting, the task goes through: Initialization → Full Load → Incremental Sync.

Key metrics: data read/written, average read/write rate, failover count, per-table latency.

Per-table operations: priority execution, re-sync, backfill sync, view exceptions.

## Three Sync Modes in Detail

### Full Database Mirror
- Database-level granularity — select database only, not individual tables
- Auto-adapts to new tables added to the database

### Multi-table Mirror
- Table-level selection, supports automatic column add/drop detection
- PostgreSQL requires replication slot configuration (decoderbufs or pgoutput plugin)

### Sharded Table Merge
- Merges sharded tables into a single target table via "virtual tables"
- Two configuration methods: rule-based (regex) or file-based (upload config file)
- Enable extended fields to record source info (`__source_table__`) and avoid primary key conflicts

## Operations SOP

### Add Sync Tables
1. Edit task, add tables, save
2. Submit for deployment
3. Stop then restart — new tables sync automatically (full load if configured)
4. Does not affect existing tables' sync progress

### Single-table Data Repair

| Operation | Write Method |
|---|---|
| Re-sync | Sync to temp table → insert overwrite to target |
| Backfill sync | Sync to temp table → delete related data → merge into target |

## Monitoring and Alerting

Configure these 5 alert rules:

| Alert Type | Monitored Item |
|---|---|
| Task Failover | Multi-table real-time sync job failover |
| Task Stopped | Multi-table real-time sync task run failure |
| Single-table Exception | Target table change failure (Schema Evolution, field size exceeded) |
| End-to-end Latency | Time from source to target |
| Read Position Lag | Gap between read position and source latest position |

IM webhook: configure Feishu/WeCom group bot → add webhook URL in product → enable in notification policy.

## Known Limitations

- Cannot create MySQL/PostgreSQL Connection via SQL (`CREATE STORAGE CONNECTION TYPE MYSQL` will error)
- Schema Evolution does not support column type changes
- Only tables with primary key (PK) fields are supported
- Do not manually create/modify/delete target tables (system auto-manages structure)
- MySQL unsupported: `year` column type
- PostgreSQL unsupported: `varbit`, `bytea`, `TIMETZ`, `interval`, `NAME`, `NUMERIC`/`decimal` (precision mismatch)
