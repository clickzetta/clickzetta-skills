# SQL Pipeline Scenarios

Worked examples for common pipeline patterns. Read this file when the user asks to build a specific type of pipeline.

## Scenario A: Kafka → Dynamic Table (real-time ETL)

```sql
-- Step 1: Create Pipe to continuously ingest Kafka data to ODS layer
-- ⚠️ ClickZetta does not support CREATE OR REPLACE PIPE — use CREATE PIPE or DROP then CREATE
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
      '', '', '', '',
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
  order_id, user_id, amount,
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

## Scenario B: Table Stream + Dynamic Table (CDC UPSERT)

```sql
-- Step 1: Create Stream on source table to capture changes
CREATE TABLE STREAM ods.orders_stream
  ON TABLE ods.orders
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Step 2: Dynamic Table consumes Stream, filters latest state
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_latest
  REFRESH INTERVAL 2 MINUTE vcluster default
AS
SELECT order_id, user_id, amount, status, created_at
FROM ods.orders_stream
WHERE __change_type IN ('INSERT', 'UPDATE_AFTER');
```

## Scenario C: Materialized View for BI query acceleration

```sql
-- ⚠️ ClickZetta does not support CREATE OR REPLACE MATERIALIZED VIEW
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

-- Manual refresh
REFRESH MATERIALIZED VIEW dws.mv_daily_revenue;

-- Drop (⚠️ must use DROP MATERIALIZED VIEW, not DROP TABLE)
DROP MATERIALIZED VIEW dws.mv_daily_revenue;
```

## Scenario D: Operations

```sql
-- Suspend / resume dynamic table
ALTER DYNAMIC TABLE dwd.orders_clean SUSPEND;
ALTER DYNAMIC TABLE dwd.orders_clean RESUME;

-- View refresh history to diagnose failures
SHOW DYNAMIC TABLE REFRESH HISTORY dwd.orders_clean LIMIT 10;

-- Suspend / resume Pipe
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = true;
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = false;
```

## Scenario E: Parameterized Dynamic Table (partition-based refresh)

```sql
-- Create parameterized dynamic table using SESSION_CONFIGS
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_partitioned
  REFRESH INTERVAL 30 MINUTE vcluster default
AS
SELECT order_id, user_id, amount, status, created_at, DATE(created_at) AS dt
FROM ods.orders
WHERE dt = SESSION_CONFIGS('target_date', CAST(CURRENT_DATE() AS STRING));

-- Manually trigger refresh with parameter
REFRESH DYNAMIC TABLE dwd.orders_partitioned
  WITH PROPERTIES ('target_date' = '2024-06-15');
```

Use case: migrating traditional daily/hourly full ETL jobs to incremental — replace scheduling variables (e.g. `${bizdate}`) with SESSION_CONFIGS for parameterized partition refresh.

## Scenario F: Dynamic Table DML (manual data correction)

Dynamic Tables **do not support DML** (INSERT/UPDATE/DELETE). To correct data:

**Option 1: Rebuild (recommended)** — correct data in the source table and wait for the next auto-refresh.

**Option 2: Use a regular table** — for scenarios requiring frequent manual corrections, use a regular table + scheduled Studio task instead of a dynamic table.
