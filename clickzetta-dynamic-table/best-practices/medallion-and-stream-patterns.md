# Medallion Architecture and Table Stream Combination Patterns

## Medallion Three-layer Pipeline

```
Bronze (raw data)
    ↓ Dynamic Table (cleansing, INCREMENTAL)
Silver (cleansed data)
    ↓ Dynamic Table (aggregation, FULL)
Gold (metric data)
    ↓ BI tools query directly
```

### Bronze → Silver (Incremental Cleansing)

```sql
-- Prerequisite: enable change tracking on source table
ALTER TABLE bronze.raw_orders SET PROPERTIES ('change_tracking' = 'true');

CREATE DYNAMIC TABLE IF NOT EXISTS silver.orders_cleaned
REFRESH INTERVAL 15 MINUTE vcluster default
AS
SELECT
  order_id,
  customer_id,
  CAST(amount AS DECIMAL(18,2))  AS amount,
  CAST(created_at AS TIMESTAMP)  AS created_at,
  COALESCE(region, 'unknown')    AS region
FROM bronze.raw_orders
WHERE order_id IS NOT NULL AND amount > 0;
```

### Silver → Gold (Aggregated Metrics, typically FULL)

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS gold.orders_daily_summary
REFRESH INTERVAL 60 MINUTE vcluster default
AS
SELECT
  DATE(created_at)              AS stat_date,
  region,
  COUNT(*)                      AS order_count,
  SUM(amount)                   AS total_revenue,
  COUNT(DISTINCT customer_id)   AS unique_customers
FROM silver.orders_cleaned
GROUP BY 1, 2;
```

---

## Combined with Table Stream (Event-driven)

Table Stream captures source table changes; Dynamic Table consumes the Stream for incremental processing.

### Basic Pattern

```sql
-- 1. Enable change tracking on source table
ALTER TABLE bronze.raw_orders SET PROPERTIES ('change_tracking' = 'true');

-- 2. Create Table Stream
CREATE TABLE STREAM bronze.orders_stream
  ON TABLE bronze.raw_orders
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- 3. Dynamic Table consumes Stream
-- Note: when Stream is used as DT source, each refresh consumes the offset
CREATE DYNAMIC TABLE IF NOT EXISTS silver.orders_incremental
REFRESH INTERVAL 5 MINUTE vcluster default
AS
SELECT order_id, customer_id, amount, status
FROM bronze.orders_stream
WHERE __change_type IN ('INSERT', 'UPDATE_AFTER');
```

### MERGE INTO + Table Stream (Alternative to Non-partitioned DT Deduplication)

When deduplication by primary key is needed and the source table has continuous writes, MERGE INTO is recommended over Dynamic Table:

```sql
-- 1. Create Table Stream
CREATE TABLE STREAM source_stream ON TABLE source_table
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD', 'SHOW_INITIAL_ROWS' = 'TRUE');

-- 2. Create target table
CREATE TABLE target_table (
    id BIGINT,
    col1 STRING,
    col2 INT,
    event_time TIMESTAMP
);

-- 3. Scheduled MERGE INTO to consume Stream
MERGE INTO target_table t
USING (
    SELECT id, col1, col2, event_time,
        CASE WHEN `value` IS NULL OR `value` = '' THEN 'DELETE' ELSE 'UPSERT' END AS op
    FROM source_stream
) s ON t.id = s.id
WHEN MATCHED AND s.op = 'UPSERT' THEN UPDATE SET
    t.col1 = s.col1, t.col2 = s.col2, t.event_time = s.event_time
WHEN NOT MATCHED AND s.op = 'UPSERT' THEN INSERT
    (id, col1, col2, event_time) VALUES (s.id, s.col1, s.col2, s.event_time);
```

---

## Real-time Report Materialization

```sql
-- Refresh hourly sales summary for direct BI tool queries
CREATE DYNAMIC TABLE IF NOT EXISTS rpt.sales_hourly
REFRESH INTERVAL 60 MINUTE vcluster default
AS
SELECT
  DATE_TRUNC('hour', order_time) AS hour_bucket,
  product_category,
  SUM(amount)                    AS revenue,
  COUNT(*)                       AS order_cnt,
  AVG(amount)                    AS avg_order_value
FROM silver.orders_cleaned
WHERE order_time >= DATEADD(day, -30, CURRENT_DATE)
GROUP BY 1, 2;
```
