# Materialized View SQL Reference

> **⚠️ ClickZetta-specific syntax**
> - Scheduled refresh: `REFRESH INTERVAL 10 MINUTE vcluster default` (same syntax as Dynamic Table)
> - Manual refresh: `REFRESH MATERIALIZED VIEW <name>;`
> - Modify comments with `ALTER TABLE`, not `ALTER MATERIALIZED VIEW`

Materialized Views pre-compute and physically store query results, making them ideal for fixed-dimension aggregation acceleration. Unlike Dynamic Tables, Materialized Views support manual or scheduled refresh but do not support incremental refresh.

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

**Key parameters:**
- `REFRESH INTERVAL 10 MINUTE vcluster default`: scheduled automatic refresh (same syntax as Dynamic Table)
- Omitting the REFRESH clause: only manual refresh via `REFRESH MATERIALIZED VIEW <name>;`
- `BUILD DEFERRED`: deferred build — does not compute results immediately at creation time
- `DISABLE QUERY REWRITE`: disables query rewrite (MV will not automatically accelerate queries)

**Examples:**
```sql
-- Materialized View with scheduled auto-refresh (every 10 minutes)
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
-- Suspend automatic refresh
ALTER MATERIALIZED VIEW <name> SUSPEND;

-- Resume automatic refresh
ALTER MATERIALIZED VIEW <name> RESUME;

-- Modify comment
ALTER TABLE <mv_name> SET COMMENT '<comment>';

-- Modify column comment (Materialized Views use ALTER TABLE syntax)
ALTER TABLE <mv_name> CHANGE COLUMN <col_name> COMMENT '<comment>';
```

> Note: Use `ALTER TABLE` (not `ALTER MATERIALIZED VIEW`) to modify comments on a Materialized View.

## REFRESH MATERIALIZED VIEW

```sql
-- Manually trigger a full refresh
REFRESH MATERIALIZED VIEW <name>;
```

## DROP MATERIALIZED VIEW

```sql
DROP MATERIALIZED VIEW [ IF EXISTS ] <name>;
```

## SHOW / DESC

```sql
-- List all Materialized Views in the current schema
SHOW TABLES WHERE is_materialized_view = true;

-- Filter by name
SHOW TABLES LIKE 'mv_%' WHERE is_materialized_view = true;

-- View Materialized View structure
DESC MATERIALIZED VIEW <name>;
DESCRIBE MATERIALIZED VIEW <name> EXTENDED;

-- View full CREATE statement
SHOW CREATE TABLE <name>;
```

## Dynamic Table vs Materialized View — Selection Guide

| Scenario | Recommended |
|---|---|
| Need second/minute-level automatic incremental refresh | Dynamic Table |
| Fixed aggregation, manual or low-frequency refresh | Materialized View |
| Need CDC change detection | Dynamic Table + Table Stream |
| Accelerate BI queries, real-time data not required | Materialized View |

## Reference Documentation

- [CREATE MATERIALIZED VIEW](https://www.yunqi.tech/documents/CREATEMATERIALIZEDVIEW)
- [ALTER MATERIALIZED VIEW](https://www.yunqi.tech/documents/alter-materialzied-view)
- [REFRESH MATERIALIZED VIEW](https://www.yunqi.tech/documents/REFRESH)
- [DROP MATERIALIZED VIEW](https://www.yunqi.tech/documents/DROPMATERIALIZEDVIEW)
- [SHOW MATERIALIZED VIEWS](https://www.yunqi.tech/documents/show-materialized-view)
- [Materialized View Concepts and Use Cases](https://www.yunqi.tech/documents/MATERIALIZEDVIEW)
- [Materialized View DDL Summary](https://www.yunqi.tech/documents/materialized_ddl)
