---
name: clickzetta-realtime-sync-pipeline
description: |
  Create and manage ClickZetta Lakehouse real-time sync tasks (single-table), syncing data from external sources
  to Lakehouse in real time.
  Supports Kafka, MySQL, PostgreSQL, and other data sources as the source, with Lakehouse as the target.
  Real-time sync tasks are continuously running streaming tasks — no scheduling required; they start running upon submission.
  Triggered when the user says "Studio real-time sync", "realtime sync", "single-table CDC sync",
  "real-time data sync", "Kafka real-time sync to Lakehouse", "MySQL single-table real-time sync",
  "single-table real-time sync", "real-time data migration".
  Covers real-time sync task creation, data source configuration, column mapping (including JSONPath computed columns),
  deployment, and operations — all ClickZetta Studio specific logic.
  Keywords: real-time sync, single table, Kafka source, MySQL source, streaming, CDC
---

# Single-table Real-time Sync Pipeline Workflow

## Wizard: Collect Required Information

Before creating a real-time sync task, use an interactive question tool (e.g., `question`) to collect the following information via option menus. If no such tool is available, list all questions in text at once:

Ask the user two questions: (1) What is the data source type — Kafka (topic real-time ingestion, supports JSON message parsing), MySQL/Aurora MySQL (single-table CDC), PostgreSQL/Aurora PG (single-table CDC), or SQL Server (single-table CDC)? (2) What is the sync granularity — single table/topic (supported by this skill, fine-grained configuration) or full database/multi-table (use clickzetta-cdc-sync-pipeline instead)?

**If the user has already provided sufficient information, proceed directly to the workflow without showing the menu.**

---

## Applicable Scenarios

- Sync data from external sources to Lakehouse in real time (low latency, continuously running)
- Kafka Topic → Lakehouse table (supports JSON message parsing)
- MySQL / PostgreSQL / SQL Server databases → Lakehouse table (CDC change capture)
- High data freshness requirements — second-level or minute-level latency
- Single source table/topic to single target table real-time sync
- Keywords: real-time sync, CDC, streaming sync, Kafka real-time sync

## Comparison with Other Sync Methods

| Dimension | Real-time Sync (This Skill) | Batch Sync | Multi-table Real-time Sync |
|-----------|---------------------------|------------|--------------------------|
| Task Type ID | `14` (REALTIME/CDC) | `10` / `291` | `281` |
| Sync Granularity | Single table/topic | Single/multi-table | Full database/multi-table |
| Run Mode | Continuously running (streaming) | Scheduled (batch) | Continuously running (streaming) |
| Scheduling | Not required, runs upon submission | Cron expression required | Not required, runs upon submission |
| Latency | Seconds to minutes | Depends on schedule interval | Seconds to minutes |
| Applicable Skill | `clickzetta-realtime-sync-pipeline` | `clickzetta-batch-sync-pipeline` | `clickzetta-cdc-sync-pipeline` |

## Prerequisites

- ClickZetta Lakehouse Studio account with permissions to create sync tasks and target tables
- Source data source already configured in Studio (Kafka / MySQL / PostgreSQL / SQL Server, etc.)
- Target Lakehouse data source available
- Sync VCluster available (real-time sync task_type=14 requires a Sync VCluster)
- **Execution environment (one of the following, cz-cli preferred)**:
  - **cz-cli path**: cz-cli installed (`brew install cz-cli or refer to official docs`) and `cz-cli setup` completed
  - **MCP path**: clickzetta-studio-mcp tools available (`create_task`, `save_integration_task`, `publish_task`, `list_data_sources`, `LH_show_object_list`, etc.)

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

## Workflow

### Step 1: Confirm Sync VCluster Availability

```
Use LH_show_object_list (object_type='VCLUSTERS') to view available virtual clusters.
Filter for clusters where vcluster_type contains SYNC.
If no Sync VCluster is available, create one before proceeding.
```

### Step 2: Find Available Data Sources

```
Use list_data_sources to view configured data source list.
Filter by type:
- Kafka: ds_type=2
- MySQL: ds_type=5
- PostgreSQL: ds_type=7
- SQL Server: ds_type=8
Record the source datasource_name and target Lakehouse datasource_name.
```

### Step 3: Explore Source Data Structure (Optional)

```
Use list_namespaces to view the source data source's namespaces (databases/schemas).
Use list_metadata_objects to view tables/topics under a namespace.
Use get_metadata_detail to view the column structure of a specific table/topic.
```

### Step 4: Create Real-time Sync Task

```
Use create_task to create the task:
- task_type: 14 (real-time sync)
- task_name: custom task name (recommend including source and target info, e.g., "rt_sync_kafka_orders")
- data_folder_id: target folder ID (obtainable via list_folders)

Record the returned task_id and studio_url.
```

### Step 5: Configure Sync Content

```
Use save_integration_task to configure sync:
- task_id: task ID returned in Step 4
- source_datasource_name: source data source name
- source_schema: source database/schema (for Kafka, the namespace containing the topic)
- source_table: source table name or Kafka topic name
- source_ds_type: source type (2=Kafka, 5=MySQL, 7=PostgreSQL, 8=SQL Server)
- sink_datasource_name: target Lakehouse data source name
- sink_schema: target schema (default: public)
- sink_table: target table name (optional, defaults to same as source table)
- sink_ds_type: 1 (Lakehouse)
```

> **Note**: The system automatically retrieves source and target metadata to generate column mappings. If the target table does not exist, it will be auto-created.

### Step 6: Kafka JSON Message Parsing (Kafka Source Only)

If the Kafka topic message format is JSON, you can add computed columns in Studio UI to parse nested fields:

- Use JSONPath rules to parse content from the value field
- Examples: `$.id` extracts the top-level id field, `$.data.code` extracts a nested field
- By default, Kafka topic built-in fields (key, value, timestamp, partition, offset) are used for mapping
- Computed column configuration must be done in Studio UI (open via studio_url)

### Step 7: Submit and Deploy

```
Real-time sync tasks do not require scheduling configuration (no need to call save_task_configuration).
Use publish_task to submit the task directly:
- task_id: task ID
- task_version: current version number (obtainable via get_task_detail)

The task starts running continuously upon submission.
```

> **Important**: Real-time sync tasks do not support test runs in development state — submission is production deployment.

### Step 8: Operations and Monitoring

```
After submission, manage real-time sync tasks in the Operations Center:

View task status: get_task_detail
View run history: list_task_run (note: real-time tasks run continuously, unlike batch tasks with periodic instances)

In Studio UI you can:
- Start/stop the task
- View sync latency and throughput
- View error logs
```

---

## Supported Data Sources

### Source

| Data Source | ds_type | Description |
|------------|---------|-------------|
| Kafka | 2 | Supports JSON message parsing (JSONPath computed columns) |
| MySQL | 5 | CDC change capture |
| PostgreSQL | 7 | CDC change capture |
| SQL Server | 8 | CDC change capture |
| Aurora MySQL | 39 | CDC change capture |
| Aurora PostgreSQL | 40 | CDC change capture |
| PolarDB MySQL | 19 | CDC change capture |
| PolarDB PostgreSQL | 48 | CDC change capture |

### Target

| Data Source | ds_type |
|------------|---------|
| Lakehouse | 1 |

## Troubleshooting

| Issue | Investigation |
|-------|--------------|
| Task creation failed | Check if a Sync VCluster is available (`LH_show_object_list` to view VCLUSTERS, filter for SYNC type) |
| Source connection failed | Check data source connection info, network reachability, account permissions |
| No data consumed from Kafka | Check topic name, consumer offset settings, Kafka cluster connectivity |
| JSON parsing failed | Check JSONPath expression correctness, verify message format is valid JSON |
| Increasing sync latency | Check if Sync VCluster resources are sufficient, whether source data volume has spiked |
| Target table write failed | Check if target table exists, column type compatibility, sufficient permissions |
| Task stopped unexpectedly | Check execution logs (`list_executions` + `get_execution_log`) for specific errors |

## Notes

### Run Mode

- Real-time sync tasks are continuously running streaming tasks — they start running upon submission without scheduling
- Test runs in development state are not supported
- After stopping, manual restart is required

### Sync VCluster Requirements

- Real-time sync tasks (task_type=14) must use a Sync VCluster
- Confirm a Sync VCluster is available before creating the task
- Check via `LH_show_object_list` (object_type='VCLUSTERS'), filter for clusters where vcluster_type contains SYNC

### Kafka Source Special Notes

- Supports specifying consumer start offset (earliest / latest / specific offset)
- JSON messages can be parsed via JSONPath computed columns for nested fields
- Default fields include: key, value, timestamp, partition, offset

### Choosing Between Single-table and Multi-table Real-time Sync

- Single-table real-time sync (this skill): suitable for fine-grained sync of a single table/topic
- Multi-table real-time sync (`clickzetta-cdc-sync-pipeline`): suitable for full database CDC, multi-table batch real-time sync
- If you need to sync all tables in a database, use multi-table real-time sync

---

## cz-cli Alternative Path

> Use this section only when cz-cli is available and MCP is not. Step numbers correspond to the MCP path above.
> All operations are delegated to the built-in agent via `cz-cli agent run`, which has full Studio MCP tool access.

### Single-table Real-time Sync (cz-cli Version)

**Quick path**: Create the task directly, then configure data source in Studio UI

```bash
# Step 1: Create real-time sync task (task_type=14, i.e., REALTIME/CDC)
cz-cli task create "rt_sync_<table>" --type REALTIME --folder <folder_name>
# Returns task_id and studio_url — complete data source configuration and column mapping at studio_url

# Step 2: After configuration, deploy the task (real-time sync needs no scheduling, runs continuously upon submission)
cz-cli task deploy "rt_sync_<table>" -y
```

**Full agent path** (when agent is needed for data source exploration and configuration):

```bash
# One-shot: let the agent complete the full real-time sync task creation
cz-cli agent run "Create a real-time sync task (task_type=14), sync data source <source_ds_name> <schema>.<table> (or Kafka topic <topic>) to Lakehouse public schema in real time, use Sync VCluster, task name rt_sync_<table>, place in <folder_name> folder" \
  --format a2a --dangerously-skip-permissions
```

For scenarios requiring fine-grained control, split into steps:

```bash
# Step 1: Confirm Sync VCluster availability
cz-cli agent run "List all available VClusters, filter for clusters where vcluster_type contains SYNC, confirm a Sync VCluster is available" \
  --format a2a --dangerously-skip-permissions

# Step 2: Find data sources
cz-cli agent run "List all configured data sources, filter by type (Kafka: ds_type=2, MySQL: ds_type=5, PostgreSQL: ds_type=7, SQL Server: ds_type=8), record source and target Lakehouse data source names" \
  --format a2a --dangerously-skip-permissions

# Step 3 (Optional): Explore source data structure
cz-cli agent run "View namespace list for data source <source_ds_name>, and the table/topic list and column structure under <schema>" \
  --format a2a --dangerously-skip-permissions

# Steps 4-5: Create and configure real-time sync task
cz-cli agent run "Create a real-time sync task (task_type=14), source datasource=<source_ds_name>, schema=<schema>, table=<table> (source_ds_type=<type>), target Lakehouse public.<table>, task name rt_sync_<table>" \
  --format a2a --dangerously-skip-permissions

# Step 7: Submit and deploy
cz-cli agent run "Submit real-time sync task rt_sync_<table> to start continuous running" \
  --format a2a --dangerously-skip-permissions
```

> **Note**: Real-time sync tasks do not require scheduling configuration — they start running continuously upon submission. Kafka JSON message computed column configuration must be done in Studio UI.

---

### Operations and Monitoring (cz-cli Version)

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
