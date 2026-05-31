# Job Monitoring & Data Recovery SQL Reference

## Job Monitoring (information_schema)

```sql
-- Real-time jobs
SHOW JOBS LIMIT 20;
SHOW JOBS IN VCLUSTER default_ap LIMIT 20;

-- Cancel a job
CANCEL JOB '2026050118342658136171272';

-- Explain query plan
EXPLAIN SELECT * FROM orders WHERE order_date = '2024-01-01';
EXPLAIN EXTENDED SELECT * FROM orders WHERE order_date = '2024-01-01';

-- Slow queries TOP 20 (last 7 days)
SELECT job_id, job_creator, execution_time, input_bytes, job_text
FROM information_schema.job_history
WHERE pt_date >= CAST(CURRENT_DATE - INTERVAL 7 DAY AS DATE)
  AND status = 'SUCCEED'
ORDER BY execution_time DESC LIMIT 20;

-- Failed jobs (last 24 hours)
SELECT job_id, job_creator, error_message, start_time, job_text
FROM information_schema.job_history
WHERE pt_date >= CAST(CURRENT_DATE - INTERVAL 1 DAY AS DATE)
  AND status = 'FAILED'
ORDER BY start_time DESC;

-- CRU consumption by user (last 30 days)
SELECT job_creator,
       COUNT(*) AS job_count,
       ROUND(SUM(cru), 2) AS total_cru,
       ROUND(AVG(execution_time), 1) AS avg_exec_sec
FROM information_schema.job_history
WHERE pt_date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS DATE)
  AND status = 'SUCCEED'
GROUP BY job_creator ORDER BY total_cru DESC;

-- Job distribution by cluster
SELECT virtual_cluster, COUNT(*) AS job_count, ROUND(SUM(cru), 2) AS total_cru
FROM information_schema.job_history
WHERE pt_date >= CAST(CURRENT_DATE - INTERVAL 7 DAY AS DATE)
GROUP BY virtual_cluster ORDER BY total_cru DESC;
```

---

## Data Recovery

```sql
-- View deleted tables
SHOW TABLES HISTORY IN my_schema;
SHOW TABLES HISTORY LIKE '%orders%';

-- Recover dropped table / dynamic table / materialized view
UNDROP TABLE my_schema.orders;
UNDROP TABLE my_schema.my_dynamic_table;
UNDROP TABLE my_schema.my_mv;
-- ⚠️ External functions use UNDROP FUNCTION (not UNDROP EXTERNAL FUNCTION)
UNDROP FUNCTION my_schema.my_ext_function;

-- View table version history
DESC HISTORY my_schema.orders;
-- Returns: version, time, total_rows, total_bytes, user, operation, job_id

-- Restore to a point in time (overwrites current data)
-- ⚠️ Timestamp must use CAST() or full millisecond format — not a plain string
-- ❌ Wrong: RESTORE TABLE t TO TIMESTAMP AS OF '2024-01-15';
-- ✅ Correct:
RESTORE TABLE my_schema.orders TO TIMESTAMP AS OF CAST('2024-01-15 10:00:00' AS TIMESTAMP);
RESTORE TABLE my_schema.orders TO TIMESTAMP AS OF CURRENT_TIMESTAMP() - INTERVAL '2' HOURS;
RESTORE TABLE my_schema.orders TO TIMESTAMP AS OF '2024-01-15 10:00:00.123';  -- full ms format

-- Query historical data (read-only, no overwrite)
SELECT * FROM my_schema.orders TIMESTAMP AS OF CAST('2024-01-15 10:00:00' AS TIMESTAMP);

-- Set Time Travel retention period (0-90 days)
ALTER TABLE my_schema.orders SET PROPERTIES ('data_retention_days' = '30');
```

**Constraints:**
- `RESTORE TABLE` target timestamp cannot be earlier than table creation time
- `UNDROP` requires being within `data_retention_days` retention period (default: 1 day)
- Materialized views support UNDROP but not RESTORE

---

## Storage Optimization

```sql
-- Compact small files (async, GP cluster only)
OPTIMIZE my_schema.orders;

-- Synchronous execution (wait for completion)
OPTIMIZE my_schema.orders OPTIONS('cz.sql.optimize.table.async' = 'false');

-- Optimize specific partition
OPTIMIZE my_schema.orders WHERE dt = '2024-01-01';
OPTIMIZE my_schema.orders WHERE dt = '2024-01-01' AND region = 'cn';

-- Auto-compact after DML (GP cluster)
SET cz.sql.compaction.after.commit = true;
INSERT INTO my_schema.orders SELECT * FROM staging;

-- Collect table statistics (improves query plans)
ANALYZE TABLE my_schema.orders COMPUTE STATISTICS;
ANALYZE TABLE my_schema.orders COMPUTE STATISTICS NOSCAN;  -- fast, size only
ANALYZE TABLE my_schema.orders COMPUTE STATISTICS FOR COLUMNS order_date, customer_id;
ANALYZE TABLES IN my_schema COMPUTE STATISTICS;

-- Truncate table (keep structure)
TRUNCATE TABLE my_schema.staging;
TRUNCATE TABLE my_schema.orders WHERE dt = '2024-01-01';  -- specific partition

-- Storage usage: large tables
SELECT table_schema, table_name,
       ROUND(bytes / 1024.0 / 1024 / 1024, 2) AS size_gb, row_count
FROM information_schema.tables
WHERE table_type = 'MANAGED_TABLE'
ORDER BY bytes DESC LIMIT 20;

-- Sort key recommendations (system analysis)
SELECT table_name, col, statement, ratio
FROM information_schema.sortkey_candidates
ORDER BY ratio DESC;
```

**Constraints:**
- OPTIMIZE only works on GP clusters — not supported on AP clusters

---

## Schema & Object Management

```sql
-- Schema management
CREATE SCHEMA IF NOT EXISTS dwd;
ALTER SCHEMA ods SET COMMENT 'ODS raw data layer';
ALTER SCHEMA old_name RENAME TO new_name;
DROP SCHEMA IF EXISTS temp_schema CASCADE;
USE SCHEMA my_schema;

-- Table management
ALTER TABLE my_schema.orders ADD COLUMN (discount DECIMAL(5,2) COMMENT 'Discount rate');
ALTER TABLE my_schema.orders CHANGE COLUMN order_id SET COMMENT 'Unique order identifier';
ALTER TABLE my_schema.orders SET PROPERTIES ('data_lifecycle' = '90');
ALTER TABLE my_schema.orders SET PROPERTIES ('hint.sort.columns' = 'order_date');
ALTER TABLE my_schema.orders RENAME TO my_schema.orders_v2;
DROP TABLE IF EXISTS my_schema.temp_table;
DROP DYNAMIC TABLE IF EXISTS my_schema.my_dt;
DROP MATERIALIZED VIEW IF EXISTS my_schema.my_mv;

-- Count objects by type in a schema
SELECT
  CASE WHEN is_view THEN 'VIEW'
       WHEN is_materialized_view THEN 'MV'
       WHEN is_dynamic THEN 'DT'
       WHEN is_external THEN 'EXTERNAL'
       ELSE 'TABLE' END AS type,
  COUNT(*) AS cnt
FROM (SHOW TABLES IN my_schema)
GROUP BY 1;

-- Find stale tables (not updated in 30+ days)
SELECT table_schema, table_name, last_modify_time,
       ROUND(bytes / 1024.0 / 1024 / 1024, 2) AS size_gb
FROM information_schema.tables
WHERE table_type = 'MANAGED_TABLE'
  AND last_modify_time < CURRENT_TIMESTAMP - INTERVAL 30 DAY
ORDER BY bytes DESC;
```
