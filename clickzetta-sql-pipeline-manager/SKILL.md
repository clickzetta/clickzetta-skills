---
name: clickzetta-sql-pipeline-manager
description: >
  Manage SQL data pipeline objects in ClickZetta Lakehouse, including Dynamic Tables,
  Materialized Views, Table Streams, and Pipes.
  Covers the full lifecycle: create, modify, suspend/resume, drop, and status inspection.
  SQL command operations only — does not cover the Lakehouse Studio GUI.

  Trigger when the user says "create dynamic table", "create materialized view", "create Pipe",
  "create table stream", "suspend/resume dynamic table", "view refresh history",
  "change refresh interval", "ingest from Kafka", "continuous import from object storage",
  "CDC change capture", "incremental computation", "real-time ETL",
  "data pipeline", "pipeline", "stream processing", "dynamic table refresh failed",
  "help me design ETL", "build a data pipeline", "data ingestion plan",
  "Medallion Architecture", "Bronze Silver Gold", "lakehouse layering",
  "Bronze layer", "Silver layer", "Gold layer".
  Keywords: SQL pipeline, dynamic table, materialized view, table stream, Pipe, data pipeline
---

# ClickZetta SQL Data Pipeline Management

## ⚠️ Key Syntax Differences: ClickZetta vs Standard SQL / Snowflake

These are the most common mistakes — always use ClickZetta-specific syntax:

| Feature | ❌ Wrong (Snowflake/Standard SQL) | ✅ ClickZetta Correct |
|---|---|---|
| Dynamic Table compute cluster | `WAREHOUSE = compute_wh` | `vcluster default` (name directly, no equals sign) |
| Dynamic Table refresh schedule | `TARGET_LAG = '1 minutes'` | `REFRESH INTERVAL 1 MINUTE vcluster default` |
| Kafka read function | `TABLE(READ_KAFKA(KAFKA_BROKER => ...))` | `read_kafka('broker', 'topic', '', 'group', '', '', '', '', 'raw', 'raw', 0, MAP(...))` — positional args |
| Materialized View scheduled refresh | `REFRESH EVERY 1 HOUR` | `REFRESH INTERVAL 60 MINUTE vcluster default` (same syntax as Dynamic Table) |
| Materialized View manual refresh | `REFRESH MATERIALIZED VIEW` inside CREATE | Execute `REFRESH MATERIALIZED VIEW <name>;` separately |
| Modify Dynamic Table SQL | `ALTER DYNAMIC TABLE ... AS ...` | `CREATE OR REPLACE DYNAMIC TABLE ...` (ALTER does not support modifying the AS clause) |
| JSON field access | `$1:field::TYPE` or `data:key` | `parse_json(value::string)['field']::TYPE` or `data['key']` |
| COPY INTO import format | `FILE_FORMAT = (TYPE = CSV)` | `USING CSV OPTIONS(...)` |
| COPY INTO export format | `USING CSV` | `FILE_FORMAT = (TYPE = CSV)` |

---

## Guide: Clarify the User's Intent

After receiving a request, determine the user's intent and choose the corresponding workflow:

> What do you want to do?
>
> **A. Design and create a new data pipeline** (complete SQL from data source through all layers) → Enter Pipeline Wizard
> **B. Manage existing pipeline objects** (modify DT refresh interval, suspend/resume, view refresh history) → Execute the corresponding operation directly
> **C. Troubleshoot pipeline issues** (DT refresh failure, Pipe stopped ingesting, Stream backlog) → Enter troubleshooting flow

**If the user has already stated clearly what they want (e.g., "create a pipeline from Kafka to DWD", "suspend this dynamic table"), proceed directly without asking again.**

---

## Pipeline Wizard

Use this mode when the user wants to design or build a complete data pipeline. Trigger phrases include:
"help me design/build ETL", "complete data pipeline", "ingest data from Kafka/OSS", "ODS→DWD→DWS", "end-to-end pipeline",
"Medallion Architecture", "Bronze/Silver/Gold", "lakehouse layering".

### Layer Naming Conventions

Users may use different layer naming schemes with the same meaning — preserve the user's preferred naming:

| User says | Meaning | Suggested Schema names |
|---|---|---|
| Bronze / Silver / Gold | Medallion Architecture | `bronze` / `silver` / `gold` |
| ODS / DWD / DWS | Chinese data warehouse convention | `ods` / `dwd` / `dws` |
| Raw / Cleansed / Aggregated | Generic English description | `raw` / `cleansed` / `agg` |

**Do not map Bronze to ODS, Silver to DWD, etc. — preserve the user's chosen naming and use the corresponding schema and table name prefixes in SQL.**

**Schema names must include a business/project prefix to avoid conflicts with other projects.** If the user has not provided a prefix, ask for the project or business domain name, then generate prefixed schema names:

```sql
-- ❌ Prone to naming conflicts — avoid this
CREATE SCHEMA IF NOT EXISTS bronze;

-- ✅ Add a project prefix
CREATE SCHEMA IF NOT EXISTS ecommerce_bronze;
CREATE SCHEMA IF NOT EXISTS ecommerce_silver;
CREATE SCHEMA IF NOT EXISTS ecommerce_gold;
```

### Requirements Gathering

**If the user has already provided sufficient information (data source, fields, layer requirements, project prefix), generate the complete SQL directly without asking further questions.**

If information is incomplete, use an interactive Q&A tool (e.g., `question`) to collect the following and present option menus; if no such tool is available, list all questions in a single text response:

```
question({
  questions: [
    {
      question: "Data source?",
      options: [
        { label: "Kafka", description: "Provide broker address and topic name" },
        { label: "Object Storage (OSS/S3/COS)", description: "Provide Volume path and file format" },
        { label: "Existing Lakehouse table (INSERT only)", description: "Dynamic Table reads directly from source table" },
        { label: "Existing Lakehouse table (with UPDATE/DELETE)", description: "Requires Table Stream + Dynamic Table" }
      ]
    },
    {
      question: "Refresh frequency?",
      options: [
        { label: "Real-time (seconds)", description: "REFRESH INTERVAL 10~60 SECOND" },
        { label: "Near real-time (minutes)", description: "REFRESH INTERVAL 1~10 MINUTE" },
        { label: "Low frequency (hourly/daily)", description: "REFRESH INTERVAL 1 HOUR or 1 DAY" }
      ]
    }
  ]
})
```

Also confirm: project/business prefix (for schema naming), layer requirements (how many layers, what each layer does), and target table field structure. These can be asked after the user responds, or inferred from context.

### Generate Complete SQL

After receiving answers, generate complete end-to-end SQL including all of the following:

```
1. Schema creation (CREATE SCHEMA IF NOT EXISTS, using the user's chosen layer names)
2. Ingestion layer table creation (if external ingestion is involved)
3. Data entry point (Pipe or Table Stream, based on source type)
4. Intermediate layer Dynamic Tables (cleansing/filtering, REFRESH INTERVAL N MINUTE VCLUSTER name)
5. Serving layer Dynamic Tables (aggregation/dimensions, REFRESH INTERVAL N MINUTE VCLUSTER name)
6. Execute REFRESH DYNAMIC TABLE immediately after each Dynamic Table is created (reset refresh baseline)
7. Verification commands (SHOW + REFRESH HISTORY)
8. Operations commands (SUSPEND/RESUME)
```

**After generating SQL, save each segment as a Studio task (code as an asset):**

In data pipeline development, all SQL should be saved as Studio tasks as manageable code assets:

```bash
# DDL SQL → save as DRAFT task (no Cron)
cz-cli task save-content <ddl_task_name> --content "<ddl_sql>"

# ETL/transformation SQL → save as scheduled task (with Cron + dependencies)
cz-cli task save-content <etl_task_name> --content "<etl_sql>"
cz-cli task save-cron <etl_task_name> --cron '0 30 2 * * ? *'
cz-cli task deploy <etl_task_name>
```

> Dynamic Table DDL should also be saved as a DRAFT task (`03_ddl_dws_ads`) for easy reference and multi-environment migration.

**⚠️ DDL tasks vs data flow tasks — scheduling rules (hard constraints, must not be violated):**

| Task type | Criteria | Scheduling config | Studio status |
|---|---|---|---|
| DDL task | Contains `CREATE / DROP / ALTER TABLE/SCHEMA` | **No Cron, no dependencies** | DRAFT |
| Data flow task | Data sync, ETL transformation, data quality checks | Configure Cron + upstream/downstream dependencies | PUBLISHED |
| Dynamic Table | DWS/ADS aggregation layer | **No Studio task needed** — system auto-refreshes | — |

> When AI generates SQL pipelines involving Studio task orchestration, the above rules must be followed. Do not generate Cron scheduling for DDL statements.

**Source → entry object selection rules:**
- Kafka → `CREATE PIPE ... AS COPY INTO ... FROM (SELECT ... FROM read_kafka('broker', 'topic', '', 'group', '', '', '', '', 'raw', 'raw', 0, MAP(...)))`
- Object storage (OSS/S3/COS) → `CREATE PIPE ... VIRTUAL_CLUSTER = 'name' INGEST_MODE = 'LIST_PURGE' AS COPY INTO ... FROM VOLUME <volume_name> USING <format> PURGE=true`
- Existing table + has UPDATE/DELETE → `CREATE TABLE STREAM ... WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')`, intermediate layer filters `__change_type IN ('INSERT', 'UPDATE_AFTER', 'DELETE')`
- Existing table + INSERT only → Dynamic Table reads directly `FROM` source table

**Refresh frequency rules:**
- First transformation layer (Bronze→Silver or ODS→DWD): use the user-specified refresh frequency (e.g., `REFRESH INTERVAL 1 MINUTE vcluster default`)
- Downstream layers: set their own refresh frequency based on business requirements (e.g., `REFRESH INTERVAL 5 MINUTE vcluster default`)

---

## Object Type Quick Reference

| Object | Use case | Key characteristics |
|---|---|---|
| **Dynamic Table** | Real-time / near real-time incremental ETL | SQL-defined, auto incremental refresh, second/minute-level latency |
| **Materialized View** | Fixed aggregation to accelerate queries | Pre-computed storage, manual or scheduled full refresh |
| **Table Stream** | CDC change data capture | Captures INSERT/UPDATE/DELETE, consumed by Dynamic Tables |
| **Pipe** | Continuous data ingestion | Auto continuous import from Kafka or object storage, no scheduling needed |

## Decision Tree

```
User requirement
├── Continuously ingest from external source (Kafka / OSS / S3)
│   └── → Pipe
├── Real-time / incremental transformation on existing tables
│   ├── Need to detect UPDATE/DELETE → Table Stream + Dynamic Table
│   └── INSERT append only → Dynamic Table (reads source table directly)
├── Fixed aggregation, real-time not required
│   └── → Materialized View
└── Multi-layer ETL (ODS→DWD→DWS or Bronze→Silver→Gold)
    └── → Multiple cascaded Dynamic Tables (each layer with its own REFRESH INTERVAL)
```

## Step 0: Confirm Connection

Before any operation, confirm you are connected to ClickZetta Lakehouse. Refer to the `clickzetta-lakehouse-connect` skill for connection parameters.

## Step 1: Select Object Type

Use the decision tree to select the object type, then read the corresponding reference file:

| Object | Reference file |
|---|---|
| Dynamic Table | [references/dynamic-table.md](references/dynamic-table.md) |
| Materialized View | [references/materialized-view.md](references/materialized-view.md) |
| Table Stream | [references/table-stream.md](references/table-stream.md) |
| Pipe | [references/pipe.md](references/pipe.md) |

## Step 2: Generate and Execute SQL

After reading the corresponding reference file, generate complete runnable SQL based on the user's parameters.

**Required parameter checklist:**
- Dynamic Table: `REFRESH INTERVAL N MINUTE vcluster name`, AS query
- Table Stream: source table name, MODE (STANDARD or APPEND_ONLY)
- Pipe (Kafka): bootstrap_servers, topic, group_id, target table (positional parameter syntax)
- Pipe (object storage): Volume path, file format, target table, `PURGE=true` (LIST_PURGE mode)

If the user has not provided a VCLUSTER, default to `default` (GP-type cluster).

## Step 3: Verify

```sql
-- Verify Dynamic Table
SHOW TABLES WHERE is_dynamic = true;
SHOW DYNAMIC TABLE REFRESH HISTORY <name> LIMIT 5;

-- Verify Materialized View
SHOW TABLES WHERE is_materialized_view = true;

-- Verify Table Stream
SHOW TABLE STREAMS;
SELECT COUNT(*) FROM <stream_name>;  -- check pending change count

-- Verify Pipe
SHOW PIPES;
```

---

## Typical Scenario Examples

### Scenario A: Kafka → Dynamic Table (Real-time ETL)

```sql
-- Step 1: Create Pipe to continuously ingest Kafka data into ODS layer
-- ⚠️ Note: ClickZetta does not support CREATE OR REPLACE PIPE; use CREATE PIPE or DROP then CREATE
CREATE PIPE kafka_orders_pipe
  VIRTUAL_CLUSTER = 'default'
  BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO ods.orders FROM (
  SELECT
    j['order_id']::STRING,
    j['user_id']::STRING,
    j['amount']::DECIMAL(10,2),
    j['status']::STRING,
    j['created_at']::TIMESTAMP
  FROM (
    SELECT parse_json(value::string) AS j
    FROM read_kafka(
      'kafka.example.com:9092',  -- bootstrap_servers
      'orders',                   -- topic
      '',                         -- reserved
      'lakehouse_ingest',         -- group_id
      '', '', '', '',             -- positional params left empty, managed by Pipe
      'raw', 'raw', 0,
      MAP('kafka.security.protocol', 'PLAINTEXT')
    )
  )
);

-- Step 2: Dynamic Table for DWD layer cleansing (incremental refresh every minute)
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_clean
  REFRESH INTERVAL 1 MINUTE vcluster default
AS
SELECT
  order_id,
  user_id,
  amount,
  UPPER(status) AS status,
  created_at,
  DATE(created_at) AS dt
FROM ods.orders
WHERE amount > 0;

-- Step 3: Dynamic Table for DWS layer aggregation (refresh every 5 minutes)
CREATE OR REPLACE DYNAMIC TABLE dws.order_hourly
  REFRESH INTERVAL 5 MINUTE vcluster default
AS
SELECT
  DATE_TRUNC('hour', created_at) AS hour,
  status,
  COUNT(*) AS order_cnt,
  SUM(amount) AS total_amount
FROM dwd.orders_clean
GROUP BY 1, 2;
```

### Scenario B: Table Stream + Dynamic Table (CDC UPSERT)

```sql
-- Step 1: Create Stream on source table to capture changes
CREATE TABLE STREAM ods.orders_stream
  ON TABLE ods.orders
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Step 2: Dynamic Table consumes Stream, filters for latest state
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_latest
  REFRESH INTERVAL 2 MINUTE vcluster default
AS
SELECT order_id, user_id, amount, status, created_at
FROM ods.orders_stream
WHERE __change_type IN ('INSERT', 'UPDATE_AFTER');
```

### Scenario C: Materialized View to Accelerate BI Queries

```sql
-- Create a materialized view with hourly refresh
-- ⚠️ Note: ClickZetta does not support CREATE OR REPLACE MATERIALIZED VIEW
-- Method 1: DROP then CREATE (recommended)
DROP MATERIALIZED VIEW IF EXISTS dws.mv_daily_revenue;
CREATE MATERIALIZED VIEW dws.mv_daily_revenue
  COMMENT 'Daily revenue summary for BI tools'
  REFRESH INTERVAL 60 MINUTE vcluster default
AS
SELECT
  DATE(created_at) AS day,
  region,
  SUM(amount) AS revenue,
  COUNT(DISTINCT user_id) AS uv
FROM dwd.orders_clean
GROUP BY 1, 2;

-- Method 2: Use BUILD DEFERRED + DISABLE QUERY REWRITE (complex, not recommended)
-- CREATE OR REPLACE MATERIALIZED VIEW ... BUILD DEFERRED DISABLE QUERY REWRITE AS ...

-- Manually trigger refresh
REFRESH MATERIALIZED VIEW dws.mv_daily_revenue;

-- Drop materialized view (⚠️ must use DROP MATERIALIZED VIEW, not DROP TABLE)
DROP MATERIALIZED VIEW dws.mv_daily_revenue;
```

### Scenario D: Operations

```sql
-- Suspend Dynamic Table (e.g., during cluster maintenance)
ALTER DYNAMIC TABLE dwd.orders_clean SUSPEND;

-- Resume
ALTER DYNAMIC TABLE dwd.orders_clean RESUME;

-- View refresh history to troubleshoot failures
SHOW DYNAMIC TABLE REFRESH HISTORY dwd.orders_clean LIMIT 10;

-- Pause Pipe
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = true;

-- Resume Pipe
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = false;
```

### Scenario E: Parameterized Dynamic Table (Partition-based Refresh)

Use the `SESSION_CONFIGS()` function to define parameterized queries, passing partition values at refresh time to control the refresh scope:

```sql
-- Create a parameterized Dynamic Table (using SESSION_CONFIGS to define parameters)
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_partitioned
  REFRESH INTERVAL 30 MINUTE vcluster default
AS
SELECT order_id, user_id, amount, status, created_at, DATE(created_at) AS dt
FROM ods.orders
WHERE dt = SESSION_CONFIGS('target_date', CAST(CURRENT_DATE() AS STRING));

-- Manually trigger refresh with parameters
REFRESH DYNAMIC TABLE dwd.orders_partitioned
  WITH PROPERTIES ('target_date' = '2024-06-15');
```

> **Use case**: When migrating traditional daily/hourly full ETL jobs to incremental jobs, replace scheduling variables (e.g., `${bizdate}`) with SESSION_CONFIGS for parameterized partition refresh.

### Scenario F: Dynamic Table DML Operations (Manual Data Correction)

⚠️ **Important**: ClickZetta Dynamic Tables **do not support DML operations** (INSERT/UPDATE/DELETE) by default. For data correction, the following options are available:

**Option 1: Rebuild the Dynamic Table (recommended)**
```sql
-- 1. Correct data in the source table
-- 2. Wait for the Dynamic Table to auto-refresh (the next REFRESH INTERVAL will trigger a full refresh)
```

**Option 2: Use a regular table instead of a Dynamic Table**
```sql
-- For scenarios requiring frequent manual corrections, use a regular table + scheduled Studio task
-- instead of a Dynamic Table
CREATE TABLE dwd.orders_manual (
  order_id STRING,
  user_id STRING,
  amount DECIMAL(10,2),
  status STRING,
  created_at TIMESTAMP,
  dt DATE
);
```

> ⚠️ **Dynamic Table limitations**:
> - Dynamic Tables are read-only; INSERT/UPDATE/DELETE are not supported
> - Data corrections should be made in the source table; the Dynamic Table will auto-refresh
> - For manual data control, use a regular table + Studio scheduled task

---

## Common Errors

| Error | Cause | Solution |
|---|---|---|
| `VCluster not available` | Compute cluster not started or name is wrong | Verify VCLUSTER name, check cluster status |
| Dynamic Table refresh failed | SQL query error or source table schema changed | Run `SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'xxx'` to view error details |
| Stream data is empty | Already consumed or past retention period | Check source table `data_retention_days`, confirm whether data was consumed |
| Pipe stopped ingesting | Kafka offset issue or connection dropped | Run `DESC PIPE EXTENDED` to check status, verify Kafka connection |
| `Cannot ALTER AS clause` | Attempted to modify Dynamic Table SQL via ALTER | Use `CREATE OR REPLACE DYNAMIC TABLE` instead |
| `CREATE OR REPLACE PIPE` syntax error | ClickZetta does not support this syntax | Use `CREATE PIPE` or `DROP PIPE` then `CREATE` |
| `CREATE OR REPLACE MATERIALIZED VIEW` syntax error | Only supports `REWRITE DISABLED + BUILD DEFER` mode | Use `DROP MATERIALIZED VIEW` + `CREATE MATERIALIZED VIEW` |
| `DROP TABLE` fails on materialized view | Object type mismatch | Use `DROP MATERIALIZED VIEW` (not `DROP TABLE`) |
| Dynamic Table DML error `not allowed` | Dynamic Tables do not support DML | Correct data in source table, or use a regular table + scheduled task |
| `SET cz.sql.dt.allow.dml` error | Session statement not supported | Dynamic Tables do not support DML; use an alternative approach |

---

## Delivery Acceptance Checklist

After pipeline creation, **verify each item — do not skip**:

```sql
-- 1. Row count comparison: each layer's row count matches expectations
SELECT COUNT(*) FROM ods.<table>;   -- ODS count ≈ source
SELECT COUNT(*) FROM dwd.<table>;   -- DWD count ≤ ODS (after cleansing)
SELECT COUNT(*) FROM dws.<table>;   -- DWS count matches aggregation logic

-- 2. Dynamic Table refresh status
SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 5;
-- Confirm latest status = SUCCESS, refresh_mode = INCREMENTAL or FULL

-- 3. Key field non-null rate
SELECT
  COUNT(*) AS total,
  COUNT(key_field) AS non_null,
  ROUND(COUNT(key_field) * 100.0 / COUNT(*), 2) AS non_null_pct
FROM <schema>.<table>;
-- Core business fields should have non-null rate > 99%

-- 4. Primary key uniqueness (DWD fact tables)
SELECT key_col, COUNT(*) AS cnt
FROM dwd.<table>
GROUP BY key_col
HAVING cnt > 1
LIMIT 10;
-- Empty result = no duplicates, as expected

-- 5. Pipe ingestion status (if applicable)
SHOW PIPES;
-- status = RUNNING, last_ingested_timestamp continuously updating
```

**Acceptance criteria:**
- [ ] Row counts at each layer match expectations
- [ ] Dynamic Table latest refresh status is SUCCESS
- [ ] Key field non-null rate > 99%
- [ ] DWD layer primary keys have no duplicates
- [ ] Pipe status is RUNNING (if applicable)
- [ ] All DDL tasks are in DRAFT status (if Studio tasks are involved)
- [ ] No redundant Studio scheduled tasks at DWS/ADS layer

---

## Reference Documentation

- [Incremental Computation Overview](https://www.yunqi.tech/documents/streaming_data_pipeline_overview)
- [Dynamic Table](https://www.yunqi.tech/documents/dynamic-table)
- [Table Stream Change Data Capture](https://www.yunqi.tech/documents/table_stream)
- [Materialized View](https://www.yunqi.tech/documents/materialized_ddl)
- [Pipe Overview](https://www.yunqi.tech/documents/pipe-summary)
- [Real-time ETL with Dynamic Table](https://www.yunqi.tech/documents/tutorials-streaming-data-pipeline-with_dynamic-table)
- [LLM Full Documentation Index](https://yunqi.tech/llms-full.txt)
