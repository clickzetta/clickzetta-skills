# Materialized View SQL Reference

> **⚠️ ClickZetta-specific Syntax**
> - Scheduled refresh: `REFRESH INTERVAL 10 MINUTE vcluster default` (same syntax as dynamic tables)
> - Manual refresh: `REFRESH MATERIALIZED VIEW <name>;`
> - Modify comment using `ALTER TABLE`, not `ALTER MATERIALIZED VIEW`

Materialized views pre-compute query results and store them physically, suitable for fixed-dimension aggregation acceleration scenarios. Difference from dynamic tables: materialized views support manual or scheduled refresh, do not support incremental refresh.

## CREATE MATERIALIZED VIEW

```sql
CREATE [ OR REPLACE ] MATERIALIZED VIEW <name>
  [ COMMENT = '<comment>' ]
  [ BUILD DEFERRED ]
  [ REFRESH INTERVAL <N> { SECOND | MINUTE | HOUR | DAY } vcluster <vcluster_name> ]
  [ DISABLE QUERY REWRITE ]
AS
  <query>;
```

**Key Parameters:**
- `REFRESH INTERVAL 10 MINUTE vcluster default`: Scheduled auto-refresh (same syntax as dynamic tables)
- Without REFRESH clause: can only manually trigger `REFRESH MATERIALIZED VIEW <name>;`
- `BUILD DEFERRED`: Deferred build, does not compute results immediately upon creation
- `DISABLE QUERY REWRITE`: Disable query rewrite (does not automatically use MV to accelerate queries)

**Examples:**
```sql
-- Scheduled auto-refresh materialized view (every 10 minutes)
CREATE MATERIALIZED VIEW mv_dept_stats
REFRESH INTERVAL 10 MINUTE vcluster default
AS
SELECT
  d.dept_id,
  d.dept_name,
  COUNT(e.emp_id) AS emp_count,
  AVG(e.salary) AS avg_salary
FROM departments d
JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_id, d.dept_name;

-- Modify refresh interval (requires CREATE OR REPLACE)
CREATE OR REPLACE MATERIALIZED VIEW mv_dept_stats
BUILD DEFERRED
REFRESH INTERVAL 20 MINUTE vcluster default
DISABLE QUERY REWRITE
AS
SELECT
  d.dept_id,
  d.dept_name,
  d.location,
  ANY_VALUE(d.col1) AS col1,
  COUNT(e.emp_id) AS emp_count,
  AVG(e.salary) AS avg_salary
FROM departments d
JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_id, d.dept_name, d.location;

-- Manual refresh
REFRESH MATERIALIZED VIEW mv_dept_stats;
```

## ALTER MATERIALIZED VIEW

```sql
-- Suspend auto-refresh
ALTER MATERIALIZED VIEW <name> SUSPEND;

-- Resume auto-refresh
ALTER MATERIALIZED VIEW <name> RESUME;

-- Modify comment
ALTER TABLE <mv_name> SET COMMENT '<comment>';

-- Modify column comment (materialized view uses ALTER TABLE syntax)
ALTER TABLE <mv_name> CHANGE COLUMN <col_name> COMMENT '<comment>';
```

> Note: Modifying comments for materialized views uses `ALTER TABLE`, not `ALTER MATERIALIZED VIEW`.

## REFRESH MATERIALIZED VIEW

```sql
-- Manually trigger full refresh
REFRESH MATERIALIZED VIEW <name>;
```

## DROP MATERIALIZED VIEW

```sql
DROP MATERIALIZED VIEW [ IF EXISTS ] <name>;
```

## SHOW / DESC

```sql
-- List all materialized views in current schema
SHOW TABLES WHERE is_materialized_view = true;

-- Filter by name
SHOW TABLES LIKE 'mv_%' WHERE is_materialized_view = true;

-- View materialized view structure
DESC MATERIALIZED VIEW <name>;
DESCRIBE MATERIALIZED VIEW <name> EXTENDED;

-- View complete CREATE TABLE statement
SHOW CREATE TABLE <name>;
```

## Dynamic Table vs Materialized View Selection Guide

| Scenario | Recommendation |
|---|---|
| Need second/minute-level auto incremental refresh | Dynamic Table |
| Fixed aggregation, manual or low-frequency refresh | Materialized View |
| Need CDC change awareness | Dynamic Table + Table Stream |
| Accelerate BI queries, data does not need to be real-time | Materialized View |

## Reference Documentation

- [CREATE MATERIALIZED VIEW](https://www.yunqi.tech/documents/CREATEMATERIALIZEDVIEW)
- [ALTER MATERIALIZED VIEW](https://www.yunqi.tech/documents/alter-materialzied-view)
- [REFRESH MATERIALIZED VIEW](https://www.yunqi.tech/documents/REFRESH)
- [DROP MATERIALIZED VIEW](https://www.yunqi.tech/documents/DROPMATERIALIZEDVIEW)
- [SHOW MATERIALIZED VIEWS](https://www.yunqi.tech/documents/show-materialized-view)
- [Materialized View Concepts and Scenarios](https://www.yunqi.tech/documents/MATERIALIZEDVIEW)
- [Materialized View DDL Summary](https://www.yunqi.tech/documents/materialized_ddl)