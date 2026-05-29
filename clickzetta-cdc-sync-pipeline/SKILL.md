---
name: clickzetta-cdc-sync-pipeline
description: |
  Create and manage ClickZetta Lakehouse multi-table real-time sync (CDC) tasks, syncing entire MySQL / PostgreSQL
  databases or multiple tables to Lakehouse in real time.
  Supports three sync modes: full database mirror, multi-table mirror, and sharded table merge.
  Based on Binlog (MySQL) or WALs (PostgreSQL) for second-level end-to-end latency, with full load + incremental two-phase sync.
  Triggered when the user says "multi-table real-time sync", "full database sync", "database mirror",
  "CDC full database", "multi-table CDC", "sharded table merge", "MySQL full database sync to Lakehouse",
  "PostgreSQL full database sync", "multi-table realtime sync", "database migration",
  "full load + incremental sync", "sync operations", "sync SOP", "sync alert configuration",
  "Binlog position expired", "server-id conflict", "full re-sync", "add sync table".
  Covers source database preparation (parameter configuration + permissions), three sync mode selection,
  task creation and deployment, operations SOP (full re-sync/add table/data repair),
  monitoring and alerting (5 alert rules + IM webhook), and detailed troubleshooting —
  all ClickZetta Studio specific logic.
  Keywords: CDC, real-time sync, MySQL, PostgreSQL, change data capture, mirror, merge, multi-table
---

# Multi-table Real-time Sync (CDC) Pipeline Workflow

## Wizard: Collect Required Information

Before creating a CDC sync task, use an interactive question tool (e.g., `question`) to collect the following information via option menus. If no such tool is available, list all questions in text at once:

```
question({
  questions: [
    {
      question: "Source database type?",
      options: [
        { label: "MySQL", description: "Including Aurora MySQL, PolarDB MySQL — based on Binlog" },
        { label: "PostgreSQL", description: "Including Aurora PG, PolarDB PG — based on WALs, requires 14+" }
      ]
    },
    {
      question: "Sync mode?",
      options: [
        { label: "Full database mirror", description: "Sync entire database, auto-adapts to new tables" },
        { label: "Multi-table mirror", description: "Specify which tables to sync" },
        { label: "Sharded table merge", description: "Merge sharded tables into one target table" }
      ]
    },
    {
      question: "Is the source database already prepared?",
      options: [
        { label: "Ready", description: "MySQL: Binlog enabled, account has REPLICATION permission; PG: wal_level=logical" },
        { label: "Not sure, help me check", description: "I'll help verify source configuration" }
      ]
    }
  ]
})
```

After collecting the above, also confirm the target schema (e.g., `ods`).

**If the user has already provided sufficient information, proceed directly to the workflow without showing the menu.**

## Applicable Scenarios

- Sync entire MySQL / PostgreSQL databases or multiple tables to Lakehouse in real time (CDC change capture)
- Full database mirror: database-level granularity, auto-adapts to new tables
- Multi-table mirror: table-level selection, supports automatic schema change detection
- Sharded table merge: merge sharded table data into a single target table
- Full load + incremental two-phase sync, second-level end-to-end latency
- Keywords: multi-table real-time sync, full database sync, CDC, sharded table merge, database migration

## Comparison with Other Sync Methods

| Dimension | Multi-table Real-time Sync (This Skill) | Single-table Real-time Sync | Batch Sync |
|-----------|----------------------------------------|---------------------------|------------|
| Task Type ID | `281` (multi-table real-time sync) | `28` | `10` / `291` |
| Sync Granularity | Full database/multi-table/sharded merge | Single table/topic | Single/multi-table |
| Run Mode | Continuously running (streaming CDC) | Continuously running (streaming) | Scheduled (batch) |
| Data Sources | MySQL / PostgreSQL | Kafka/MySQL/PG/SQL Server | Multiple |
| Scheduling | Not required, runs upon submission | Not required | Cron required |
| Applicable Skill | `clickzetta-cdc-sync-pipeline` | `clickzetta-realtime-sync-pipeline` | `clickzetta-batch-sync-pipeline` |

## Supported Data Sources

### Source

| Data Source Type | Incremental Read Mode | Database Version | ds_type |
|-----------------|----------------------|-----------------|---------|
| MySQL (including Aurora MySQL, PolarDB MySQL) | Binlog | 5.6+, 8.x | 5, 39, 19 |
| PostgreSQL (including Aurora PG, PolarDB PG) | WALs | 14+ | 7, 40, 48 |
| SQL Server | CDC | - | 8 |
| TiDB | - | - | 17 |

### Target

| Data Source | ds_type |
|------------|---------|
| Lakehouse | 1 |
| Kafka | 2 |

## Prerequisites

- ClickZetta Lakehouse Studio account with permissions to create sync tasks
- Source data source already configured in Studio (via Studio UI, not SQL Storage Connection), with CDC-required permissions
- Sync VCluster available (multi-table real-time sync task_type=281 must use a Sync VCluster)
- **Execution environment (one of the following, cz-cli preferred)**:
  - **cz-cli path**: cz-cli installed (`brew install cz-cli or refer to official docs`) and `cz-cli setup` completed
  - **MCP path**: clickzetta-studio-mcp tools available (`create_task`, `save_cdc_realtime_task`, `publish_task`, `list_data_sources`, `LH_show_object_list`, etc.)

## Environment Detection (Read Before Execution)

Before starting any operation, determine the current execution environment:

**Step 1: Check if cz-cli is available**
```bash
cz-cli --version
```
- If command exists → **use cz-cli path** (see "cz-cli Alternative Path" section at the end of this document)
- If command not found → continue to check MCP

**Step 2: Check if MCP is available (only when cz-cli is unavailable)**

Try calling the `list_data_sources` tool to query the data source list.
- If tool exists in tool list → **use MCP path** (default path in this document)
- If tool not found → stop execution and prompt the user:
  > "Neither cz-cli nor MCP tools are available in the current environment. Please install one of them before retrying.
  > cz-cli installation: `brew install cz-cli or refer to official docs`, then run `cz-cli setup`
  > MCP installation: refer to clickzetta-studio-mcp configuration docs"

> ⚠️ **Important distinction**: CDC multi-table sync uses **Studio data sources** (configured via Studio UI or API), not SQL `CREATE STORAGE CONNECTION`.
> - `CREATE STORAGE CONNECTION` only supports object storage types (OSS/COS/S3) and Kafka
> - MySQL / PostgreSQL relational database connections are configured via **Studio Data Source Management**
> - Use `list_data_sources` API to view configured data sources

## Source Database Preparation

### MySQL Parameter Requirements

Verify the following parameters on the source MySQL database:

| Parameter | Required Value | Query Method |
|-----------|---------------|--------------|
| `log_bin` | ON | `SHOW GLOBAL VARIABLES LIKE 'log_bin'` |
| `binlog_format` | ROW | `SHOW GLOBAL VARIABLES LIKE 'binlog_format'` |
| `binlog_row_image` | FULL | `SHOW GLOBAL VARIABLES LIKE 'binlog_row_image'` |
| `binlog_expire_logs_seconds` | ≥86400 (recommended) | - |

MySQL permission requirements (recommend executing as root):
- Metadata read: `SELECT` on information_schema + target database tables
- Binlog sync: `REPLICATION SLAVE`, `REPLICATION CLIENT`
- Full load: `SELECT` on target tables

### PostgreSQL Parameter Requirements

The following parameters require a PostgreSQL Server restart after modification:

| Parameter | Required Value | Description |
|-----------|---------------|-------------|
| `wal_level` | logical | Enables logical decoding |
| `max_replication_slots` | ≥10 | Maximum number of slots allowed |
| `max_wal_senders` | ≥10 | Maximum concurrent WAL sender processes |

PostgreSQL permission requirements (recommend executing as admin):
- Metadata read: `SELECT` on information_schema
- WAL sync: `REPLICATION` permission
- Full load: `SELECT` on target tables
- Create publication: `CREATE` permission

> **PostgreSQL special note**: A replication slot must be configured. Different tasks should not reuse the same slot. If a slot is occupied when the task starts, it will fail to start.

## Workflow

### Step 1: Confirm Sync VCluster Availability

```
Use LH_show_object_list (object_type='VCLUSTERS') to view available virtual clusters.
Filter for clusters where vcluster_type contains SYNC.
If no Sync VCluster is available, prompt the user to create one before proceeding.
```

### Step 2: Find Source Data Source

```
Use list_data_sources to view configured data sources.
Filter by type:
- MySQL: ds_type=5
- PostgreSQL: ds_type=7
Record the source datasource_id and datasource_type.
```

### Step 3: Explore Source Data Structure

```
Use list_namespaces to view the source database list.
Use list_metadata_objects to view tables under a database.
Confirm the sync scope (full database / specific tables / sharded tables).
```

### Step 4: Select Sync Mode

Choose one of three modes based on user requirements:

| Mode | pipeline_type | Use Case |
|------|--------------|----------|
| Full database mirror | 3 | Sync all tables in a database, auto-adapts to new tables |
| Multi-table mirror | 1 | Sync selected specific tables, supports automatic schema change detection |
| Sharded table merge | 2 | Merge sharded table data into a single target table |

### Step 5: Create Multi-table Real-time Sync Task

```
Use create_task to create the task:
- task_type: 281 (multi-table real-time sync)
- task_name: custom name (e.g., "cdc_sync_mysql_orders_db")
- data_folder_id: target folder ID (obtainable via list_folders)

Record the returned task_id (i.e., data_file_id).
```

### Step 6: Configure Sync Content

```
Use save_cdc_realtime_task to configure sync:
- data_file_id: task_id returned in Step 5
- pipeline_type: mode selected in Step 4 (1=multi-table mirror, 2=sharded table merge, 3=full database mirror)
- source_datasource_list: [{"datasourceId": <id>, "datasourceType": <type>}]
- sync_object_list:
  - Full database mirror: [{"schemaName": "<database_name>"}] (specify database name only)
  - Multi-table mirror: [{"schemaName": "<db>", "tableName": "<table>"}, ...]
  - Sharded table merge: configure via regex or batch file
- target_datasource: {"datasourceId": <lakehouse_id>, "datasourceType": 1}
- sync_mode: 1 (full load + incremental, recommended) or 2 (incremental only)
- save_mode: 2 (append, recommended for new tasks)
```

> **sync_mode explanation**:
> - `1` (full load + incremental): full load of historical data first, then starts incremental CDC — recommended for first use
> - `2` (incremental only): captures changes from current position only — suitable when historical data already exists

### Step 7: Submit and Deploy

```
Use publish_task to submit the task:
- task_id: task ID
- task_version: current version number (obtainable via get_task_detail)

The task does not start automatically after submission — manual start is required.
```

> **Important**: Multi-table real-time sync tasks are continuously running streaming tasks. No scheduling configuration is needed (do not call save_task_configuration). Start manually in Studio UI after submission.

### Step 8: Start the Task

Start the task in Studio UI, selecting the start method:

| Start Method | Description | Use Case |
|-------------|-------------|----------|
| Stateless start | Full sync of all data (full load → incremental) | First start |
| Resume from last saved state | Resume from the stop position | Restart after stop |
| Custom start position | MySQL: specify binlog file/time; PG: specify LSN | Data re-sync |

During the full load phase, you can configure maximum concurrency to control pressure on the source database.

### Step 9: Operations and Monitoring

```
After starting, the task goes through three phases: Initialization → Full Load → Incremental Sync.

Monitoring metrics:
- Data read / data written (record count)
- Average read rate / average write rate
- Failover count
- Per-table level: latest read position, latest update time, data latency

Per-table operations:
- Priority execution: increase full load priority for a table
- Cancel run / force stop: stop sync for a single table
- Re-sync: perform full load + incremental again for that table
- Backfill sync: re-sync partial data based on filter conditions
- View exceptions: view Schema Evolution exceptions, etc.
```

## Three Sync Modes in Detail

### Full Database Mirror

- Configured at database granularity — select database only, not individual tables
- Auto-adapts to new tables added to the database
- Suitable for scenarios requiring a complete mirror of an entire database

### Multi-table Mirror

- Select specific tables to sync at table granularity
- Supports automatic detection of column additions and deletions
- Supports batch configuration (upload configuration file)
- PostgreSQL requires replication slot configuration (decoderbufs or pgoutput plugin)

### Sharded Table Merge

- Merges sharded table data into a single target table
- Uses "virtual tables" as an intermediate layer: when creating a virtual table, define filter conditions based on data source/schema/table names to map matching source tables to the same virtual table
- Two configuration methods:
  - Rule-based: regex matching to filter tables (e.g., all tables starting with `abc`)
  - File-based: upload configuration file for batch specification
- Extended fields feature: add extra columns to the target table to record source information (server/database/schema/table names)
- Sharded table primary key conflict resolution: enable extended fields and set them as composite primary key to avoid write conflicts from records with the same primary key across different shards
- Heterogeneous column merge: when sharded tables have inconsistent column structures, the system automatically validates and reports differences — use the heterogeneous column merge feature to handle this

## Advanced Parameters

The following advanced parameters can be set in the task "Parameters" area (not recommended to adjust by default — contact technical support before adjusting):

| Parameter | Description | Default | Tuning Advice |
|-----------|-------------|---------|---------------|
| `step1.taskmanager.memory.process.size` | Incremental sync process total memory | 1600m | Increase to 4000m for very large full loads |
| `step2.taskmanager.memory.process.size` | Full load process total memory | 2000m | - |
| `step1.taskmanager.memory.task.off-heap.size` | Incremental sync off-heap memory | 256m | Increase to 500M for very large full loads |
| `lh.table.cz.common.output.file.max.size` | Full load single file split size | 33554432 | - |
| `pod.limit.memory` | Submit client memory limit | 1Gi | - |

## Stop and Undeploy

### Stop Task

- Stopping automatically saves the incremental sync position
- Stop during full load phase: incomplete tables will re-sync from full load on restart
- Stop during incremental phase: resumes from stop position on restart
- Recovery: click "Start", select "Resume from last saved state" for checkpoint recovery
- To backtrack data: select "Custom start position", specify binlog file/position (MySQL) or LSN (PostgreSQL) — ensure the specified position has not expired

### Undeploy Task (High Risk)

- Does not save sync position — re-deployment requires full re-sync
- Does not clean up data already synced to target, does not delete target tables
- Re-sync does not recreate tables: full load uses insert overwrite, incremental uses merge into
- Use only when: the task is definitively no longer needed, or task state is abnormal and needs repair

## Operations SOP

### Supplementary Full Load After Initial Start

Three approaches when full load was not selected at first start but historical data is needed later:

| Approach | Operation | Impact |
|----------|-----------|--------|
| Approach 1: Single-table re-sync | Execute "Re-sync" for the specified table | Source data synced to temp table, insert overwrite to target table, no query impact |
| Approach 2: Single-table backfill | Execute "Backfill sync" for the specified table, filter condition set to `where 1=1` | Data pulled from source to temp table based on condition, delete + merge into target table |
| Approach 3: Undeploy and redeploy | Stop → Undeploy → Deploy → Start (select full load) | Clears position info, full load + incremental re-sync, does not delete target tables |

### Add Sync Tables

1. Edit the task, add the tables to sync, save
2. Submit task for deployment
3. Stop the task in Operations Center, then restart
4. After restart, new tables are automatically synced (full load if configured, otherwise incremental only)
5. Does not affect sync progress of existing tables

### Add/Remove Data Sources/Schemas/Tables for Sharded Tables

- Edit directly in the task development interface
- Save → Submit → Restart task to take effect
- New objects will automatically execute full load if configured
- Does not affect sync progress of existing tables

### Priority Sync for Important Tables

- During full load phase, use "Priority execution" for important tables
- Jumps the queue in the resource pool to prioritize full load for that table

### Pause/Resume Single-table Incremental Sync

- Pause: execute "Stop incremental sync" for a table to pause change message consumption
- Resume: execute "Resume incremental sync" — to ensure data continuity, a full load from source is performed
- Use case: during sudden high traffic from source, pause less important tables to free processing resources for important ones

### Single-table Data Repair

| Operation | Description | Write Method |
|-----------|-------------|--------------|
| Re-sync | Re-sync full source table data | Sync to temp table → insert overwrite to target table |
| Backfill sync | Pull partial/full data from source based on filter conditions | Sync to temp table → delete related data from target → merge into target |

## Monitoring and Alerting Configuration

### Recommended Alert Rules

Configure the following 5 alert rules for comprehensive task health monitoring:

| Alert Type | Monitored Item | Description |
|-----------|---------------|-------------|
| Task Failover | Multi-table real-time sync job failover | Monitors task runtime stability |
| Task Stopped | Multi-table real-time sync task run failure | Alerts on unexpected task stop |
| Single-table Exception | Multi-table real-time sync target table change failure | Schema Evolution failure, single field exceeding 10M limit, etc. |
| End-to-end Latency | Multi-table real-time sync latency | Time interval from source to target |
| Read Position Lag | Multi-table real-time sync read position lag | Gap between read position and source latest position |

Each alert can have additional filter attributes (workspace, task name, etc.). Without filters, all multi-table real-time tasks under the instance are monitored by default.

### IM Alert Bot Configuration

1. Configure a group bot in Feishu/WeCom, obtain the webhook URL
2. Add a webhook configuration in the product, select Feishu/WeCom as channel, enter the webhook URL
3. Enable webhook in the notification policy
4. Select the notification policy with webhook enabled in the monitoring rule

## Examples

### Example 1: MySQL Full Database Real-time Sync to Lakehouse

User says: "Sync the MySQL ecommerce database to Lakehouse in real time"

Steps:
1. Source preparation: confirm MySQL has Binlog enabled (`binlog_format=ROW`), create sync account with REPLICATION SLAVE and SELECT permissions
2. `list_data_sources` to find MySQL data source (ds_type=5) and Lakehouse data source
3. `create_task(task_type=281, task_name="realtime_sync_ecommerce")` → get studio_url
4. In Studio UI: select full database mirror → select ecommerce database → configure target workspace → sync_mode select full load + incremental
5. `publish_task(...)` to submit — task immediately begins full load initialization, then automatically switches to incremental CDC

### Example 2: Sharded Table Merge Sync

User says: "I have three sharded tables order_0, order_1, order_2 that need to be merged into one orders table"

Steps:
1. `create_task(task_type=281, task_name="sync_sharding_orders")`
2. In Studio UI: select sharded table merge → select order_0/order_1/order_2 → set target table as orders → configure extended fields (e.g., `__source_table__`) to identify source
3. `publish_task(...)` to submit

## Troubleshooting

### Quick Reference Table

| Issue | Investigation |
|-------|--------------|
| `CREATE STORAGE CONNECTION TYPE MYSQL` error | ❌ ClickZetta does not support MySQL/PostgreSQL type Storage Connections. CDC data sources are configured via **Studio UI Data Source Management**, not SQL commands |
| Task creation failed | Check if a Sync VCluster is available |
| Source connection failed | Check Studio data source configuration, network reachability, account permissions |
| Binlog read failed | Confirm MySQL `log_bin=ON`, `binlog_format=ROW`, `binlog_row_image=FULL` |
| WAL read failed | Confirm PostgreSQL `wal_level=logical`, slot not occupied by another task |
| Slot startup conflict | Different tasks should not reuse the same slot — check if another running task is occupying it |
| Slow full load | Adjust maximum concurrency, check source database load, increase memory parameters |
| Increasing incremental latency | Check Sync VCluster resources, whether source data volume has spiked |
| Schema Evolution exception | Use "View exceptions" to see details — note that column type changes are not supported |
| Sharded table primary key conflict | Enable extended fields and set as composite primary key |

### Incremental Sync Failures

#### Binlog Position Expired

- Symptom: error `The connector is trying to read binlog starting at ... but this is no longer available on the server`
- Cause: the specified binlog file has been purged by MySQL periodic cleanup, or the task was stopped too long causing position expiration
- Resolution:
  1. Execute `SHOW MASTER STATUS` on source to query current latest binlog file and position
  2. Restart sync task with the latest file and position (select "Custom start position")
  3. If lost data needs recovery, execute "Re-sync" for the affected tables

#### Server-id Conflict

- Symptom: error `A slave with the same server_uuid/server_id as this slave has connected to the master`
- Cause: the task's assigned server-id (range 5400-6400) conflicts with another sync tool/task on the same database
- Resolution: check if other sync tasks or tools are syncing binlog on the same database instance, restart the sync task

#### Data Source Timezone Configuration Error

- Symptom: error `The MySQL server has a timezone offset ... which does not match the configured timezone`
- Cause: the timezone configured in the data source (default Asia/Shanghai) does not match the actual database timezone
- Resolution: confirm the database's configured timezone, modify the timezone in the data source configuration

#### Binlog Event Size Exceeded

- Symptom: error `log event entry exceeded max_allowed_packet`
- Cause: database `max_allowed_packet` is smaller than a binlog event size, or binlog file is corrupted
- Resolution:
  1. Contact DBA to increase `max_allowed_packet` (max 1G), re-sync after it takes effect
  2. If still failing after adjustment (binlog may be corrupted), restart task with a newer position to skip the problematic position
  3. Execute "Re-sync" for tables that may have missing data

### Full Load Failures

#### PK Length Exceeded

- Symptom: error `Encoded key size 191 exceeds max size 128`
- Cause: source table primary key total field length exceeds 128 bytes, or extended field composite primary key is too long in sharded table merge scenarios
- Resolution: add a parameter in the sync task configuration to increase the PK length limit

### Sync Task Failover

#### Disconnected from Lakehouse Ingestion Service

- Symptom: failover details contain `Async commit for instance ... failed. rpcProxy call hit final failed after max retry reached`
- Cause: typically occurs during Lakehouse service upgrades, connection interrupted
- Resolution:
  1. Task usually auto-recovers after service upgrade completes
  2. If failover persists, manually restart the task
  3. If still unrecoverable, check Lakehouse Ingestion Service health status

#### Binlog Event Deserialization Failed

- Symptom: failover details contain `Failed to deserialize data of EventHeaderV4`
- Cause: sudden burst of binlog events from source (mass updates/bulk deletes), write-side backpressure causes read-side to stop consuming, binlog client connection times out
- Resolution:
  1. Short-term traffic spike: task usually auto-recovers within limited failover attempts
  2. Persistent occurrence: increase MySQL parameters `slave_net_timeout` and `thread_pool_idle_timeout`
  3. Temporary adjustment (lost on restart): `SET GLOBAL slave_net_timeout = 120; SET GLOBAL thread_pool_idle_timeout = 120;`
  4. Permanent adjustment: modify MySQL configuration file

### Table Enters Blocklist

#### Schema Evolution Failed

- Symptom: table status automatically changes to sync stopped, with messages like `pk column different`, `pk column type mismatch`, `invalid modify column`
- Cause: source table structure changed in a way not supported by Lakehouse (PK column list change, PK column type change, incompatible column type modification)
- Resolution:
  1. Check source table structure, correct it to the proper structure
  2. Execute "Re-sync" for the stopped table — after full load completes, incremental data will continue syncing

## Known Limitations

- **Cannot create MySQL/PostgreSQL Connection via SQL**: `CREATE STORAGE CONNECTION TYPE MYSQL/POSTGRESQL` will error with `no connection info factory for connection kind 'STORAGE', type 'mysql'`. CDC data sources must be configured via Studio UI Data Source Management
- Schema Evolution does not support column type changes or automatic new table detection
- Only tables with primary key (PK) fields are supported — non-PK tables cannot be synced
- If different source databases/tables contain records with the same primary key, sync results will be abnormal
- Do not manually create/modify/delete target tables unless necessary (the system auto-manages target table structure)
- MySQL unsupported column types: `year` (value mismatch)
- PostgreSQL unsupported column types: `varbit`, `bytea`, `TIMETZ`, `interval`, `NAME` (value mismatch), `NUMERIC`, `decimal` (precision mismatch — target has higher precision)

---

## cz-cli Alternative Path

> Use this section only when cz-cli is available and MCP is not. Step numbers correspond to the MCP path above.
> All operations are delegated to the built-in agent via `cz-cli agent run`, which has full Studio MCP tool access.

### Quick Path: Create Task + Studio UI Configuration

```bash
# Create CDC multi-table real-time sync task (task_type=281, i.e., MULTI_REALTIME)
cz-cli task create "cdc_<database>" --type MULTI_REALTIME --folder <folder_name>
# Returns task_id and studio_url — complete data source selection, table mapping, etc. at studio_url

# After configuration, deploy (CDC tasks need no scheduling, runs continuously upon submission)
cz-cli task deploy "cdc_<database>" -y
```

### Mode 1: Full Database Mirror Sync (cz-cli agent version)

```bash
# Steps 1-9 combined: let the agent complete the full CDC database sync task creation
cz-cli agent run "Create a CDC multi-table real-time sync task, mirror the entire <database> database from MySQL data source <source_ds_name> to Lakehouse, use Sync VCluster, task name cdc_<database>, place in <folder_name> folder" \
  --format a2a --dangerously-skip-permissions
```

For scenarios requiring fine-grained control, split into steps:

```bash
# Step 1: Confirm Sync VCluster availability
cz-cli agent run "List all available VClusters, filter for clusters where vcluster_type contains SYNC, confirm a Sync VCluster is available" \
  --format a2a --dangerously-skip-permissions

# Step 2: Find data sources
cz-cli agent run "List all configured data sources, including MySQL type (ds_type=5), record source and target Lakehouse data source names" \
  --format a2a --dangerously-skip-permissions

# Steps 3-4: Create and configure CDC task (full database mirror)
cz-cli agent run "Create a CDC multi-table real-time sync task (task_type=281), pipeline_type full database mirror (3), source datasource=<source_ds_name>, sync all tables in <database>, target Lakehouse, task name cdc_<database>" \
  --format a2a --dangerously-skip-permissions

# Step 5: Submit and deploy
cz-cli agent run "Submit CDC task cdc_<database> to start continuous running" \
  --format a2a --dangerously-skip-permissions
```

---

### Mode 2: Multi-table Mirror Sync (cz-cli agent version)

```bash
# Create multi-table mirror CDC task (specify specific tables)
cz-cli agent run "Create a CDC multi-table real-time sync task (task_type=281), pipeline_type multi-table mirror (1), source datasource=<source_ds_name>, sync tables <table1>, <table2>, <table3> from <database>, target Lakehouse, task name cdc_<database>_selected" \
  --format a2a --dangerously-skip-permissions
```

---

### Mode 3: Sharded Table Merge Sync (cz-cli agent version)

```bash
# Create sharded table merge CDC task (multiple source tables merged to single target)
cz-cli agent run "Create a CDC multi-table real-time sync task (task_type=281), pipeline_type sharded table merge (2), source datasource=<source_ds_name>, merge multiple tables from <database> to Lakehouse target table, task name cdc_<database>_merged" \
  --format a2a --dangerously-skip-permissions
```

---

### Operations and Monitoring (cz-cli version)

```bash
# View recent run history
cz-cli runs list --task <task_name>

# View run details
cz-cli runs detail <run_id>

# View execution logs
cz-cli attempts log <run_id>

# Undeploy task (stop continuous running)
cz-cli task undeploy <task_name> -y
```

---

## Delivery Acceptance Checklist

After the CDC sync task is deployed and running, **verify each item**:

```sql
-- 1. Row count comparison: after full load phase, ODS layer row count matches source
SELECT COUNT(*) FROM <ods_schema>.<table>;

-- 2. Incremental verification: insert a test record to source, confirm it syncs to Lakehouse
-- Execute INSERT on source MySQL, wait 10-30 seconds, then query in Lakehouse

-- 3. Key field non-null rate
SELECT
  COUNT(*) AS total,
  COUNT(key_field) AS non_null,
  ROUND(COUNT(key_field) * 100.0 / COUNT(*), 2) AS non_null_pct
FROM <ods_schema>.<table>;

-- 4. Check _op field distribution (for CDC ingestion)
SELECT _op, COUNT(*) FROM <ods_schema>.<table> GROUP BY _op;
-- Normal should have I (INSERT) records; UPDATE/DELETE scenarios will have U/D
```

**Acceptance Criteria:**
- [ ] Full load phase complete, ODS layer row count matches source
- [ ] Incremental test data written, synced to Lakehouse within 30 seconds
- [ ] Key field non-null rate meets expectations
- [ ] _op field distribution is reasonable (no abnormally large number of D records)
- [ ] Task status is continuously running (RUNNING), no frequent restarts
- [ ] Column type mapping is correct (pay attention to BIT/ENUM/TEXT and other heterogeneous types)
