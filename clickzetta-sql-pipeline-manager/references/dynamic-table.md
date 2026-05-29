# Dynamic Table SQL Reference

> **⚠️ ClickZetta-specific syntax**
> - Refresh schedule syntax: `REFRESH INTERVAL 5 MINUTE vcluster default` (not `TARGET_LAG`)
> - Modifying the schedule interval or compute cluster requires `CREATE OR REPLACE`; `ALTER` does not support this
> - `ALTER DYNAMIC TABLE` only supports: SUSPEND / RESUME / SET COMMENT / RENAME COLUMN / CHANGE COLUMN COMMENT / SET/UNSET PROPERTIES
> - Drop with `DROP DYNAMIC TABLE` (not `DROP TABLE`)
> - Restore with `UNDROP TABLE` (not `UNDROP DYNAMIC TABLE`)
> - Describe with `DESC TABLE name` (does not support `DESC DYNAMIC TABLE name EXTENDED`)

Dynamic Tables are the core incremental computation objects in ClickZetta Lakehouse. Defined by a SQL query, they refresh automatically and incrementally without manual scheduling.

## CREATE DYNAMIC TABLE

```sql
CREATE [ OR REPLACE ] DYNAMIC TABLE <name>
  [ (<column_list>) ]
  [ PARTITIONED BY (<col_name>) ]
  [ CLUSTERED BY (<col_name>) ]
  [ COMMENT <comment> ]
  [ PROPERTIES ( data_lifecycle = <day_num> ) ]
  REFRESH [ START WITH TIMESTAMP '<timestamp>' ] INTERVAL <n> { SECOND | MINUTE | HOUR | DAY }
  vcluster <vcluster_name>
AS
  <query>;
```

**Key parameters:**
- `REFRESH INTERVAL <n> MINUTE`: refresh interval, minimum 1 minute
- `vcluster`: name of the compute cluster to run refresh jobs (name directly, no equals sign or quotes)
- `OR REPLACE`: replaces an existing Dynamic Table with the same name (required when modifying SQL logic or scheduling config)
- Recommended: use a GP-type cluster (e.g., `default`); AP-type clusters do not support small file compaction

**Examples:**
```sql
-- Basic example: refresh order summary every 5 minutes
CREATE OR REPLACE DYNAMIC TABLE dw.order_summary
  REFRESH INTERVAL 5 MINUTE vcluster default
AS
SELECT
  date_trunc('hour', created_at) AS hour,
  region,
  COUNT(*) AS order_cnt,
  SUM(amount) AS total_amount
FROM ods.orders
GROUP BY 1, 2;

-- Modify refresh interval (must use CREATE OR REPLACE)
CREATE OR REPLACE DYNAMIC TABLE dw.order_summary
  REFRESH INTERVAL 10 MINUTE vcluster default
AS
SELECT
  date_trunc('hour', created_at) AS hour,
  region,
  COUNT(*) AS order_cnt,
  SUM(amount) AS total_amount
FROM ods.orders
GROUP BY 1, 2;
```

## ALTER DYNAMIC TABLE

```sql
-- Suspend refresh
ALTER DYNAMIC TABLE <name> SUSPEND;

-- Resume refresh
ALTER DYNAMIC TABLE <name> RESUME;

-- Modify comment
ALTER DYNAMIC TABLE <name> SET COMMENT '<comment>';

-- Rename column
ALTER DYNAMIC TABLE <name> RENAME COLUMN <old_col> TO <new_col>;

-- Modify column comment (note: use CHANGE COLUMN)
ALTER DYNAMIC TABLE <name> CHANGE COLUMN <col_name> COMMENT '<comment>';

-- Modify properties
ALTER DYNAMIC TABLE <name> SET PROPERTIES ('key' = 'value');
ALTER DYNAMIC TABLE <name> UNSET PROPERTIES ('key');
```

> Note: To modify the refresh interval, compute cluster, or SQL query logic, use `CREATE OR REPLACE DYNAMIC TABLE`. ALTER does not support these operations.

## REFRESH DYNAMIC TABLE (Manual Trigger)

```sql
-- Manually trigger a single refresh
REFRESH DYNAMIC TABLE <name>;
```

## DROP DYNAMIC TABLE

```sql
-- ⚠️ Must use DROP DYNAMIC TABLE, not DROP TABLE
DROP DYNAMIC TABLE [ IF EXISTS ] <name>;

-- Restore a dropped Dynamic Table (⚠️ use UNDROP TABLE, not UNDROP DYNAMIC TABLE)
UNDROP TABLE <name>;
```

## SHOW / DESC

```sql
-- List all Dynamic Tables in the current schema
SHOW TABLES WHERE is_dynamic = true;

-- List Dynamic Tables in a specific schema
SHOW TABLES IN <schema_name> WHERE is_dynamic = true;

-- View Dynamic Table structure
DESC TABLE <name>;

-- View full CREATE statement
SHOW CREATE TABLE <name>;

-- View refresh history (status, duration, trigger type, incremental row count)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = '<dt_name>' LIMIT 20;
```

> ⚠️ **DESC note**: Use `DESC TABLE name` for Dynamic Tables. `DESC DYNAMIC TABLE name EXTENDED` is not supported (EXTENDED will cause an error).

## Notes

- To modify SQL logic, refresh interval, or compute cluster → use `CREATE OR REPLACE`; `ALTER` is not supported for these
- Minimum refresh interval is 1 minute
- Drop with `DROP DYNAMIC TABLE` (not `DROP TABLE`)
- Restore with `UNDROP TABLE` (not `UNDROP DYNAMIC TABLE`)
- Refresh failures do not affect queryability (returns data from the last successful version)
- A `CREATE OR REPLACE` that is not a simple add/drop column will trigger a full refresh
- Recommended: use a GP-type cluster (e.g., `default`); AP-type clusters do not support small file compaction

## Parameterized Dynamic Table (SESSION_CONFIGS)

Use the `SESSION_CONFIGS()` function to define parameterized queries, passing partition values at refresh time to control the refresh scope:

```sql
-- Create a parameterized Dynamic Table
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_partitioned
  REFRESH INTERVAL 30 MINUTE vcluster default
AS
SELECT order_id, user_id, amount, dt
FROM ods.orders
WHERE dt = SESSION_CONFIGS('target_date', CAST(CURRENT_DATE() AS STRING));

-- Manually trigger refresh with parameters
REFRESH DYNAMIC TABLE dwd.orders_partitioned
  WITH PROPERTIES ('target_date' = '2024-06-15');
```

Use case: migrating traditional daily full ETL jobs to incremental jobs, replacing scheduling variables with SESSION_CONFIGS.

## Dynamic Table DML Operations

Dynamic Tables do not support DML by default. You must enable the parameter first (must be set before each DML operation):

```sql
-- ⚠️ Must execute SET in the same session/batch before the DML
SET cz.sql.dt.allow.dml = true;
INSERT INTO <name> VALUES (...);

-- Delete
SET cz.sql.dt.allow.dml = true;
DELETE FROM <name> WHERE ...;
```

> ⚠️ **DML notes**:
> - `SET cz.sql.dt.allow.dml = true` must be in the same execution batch as the DML statement
> - After a DML operation, the next automatic refresh will trigger a **full refresh** (not incremental), which may take longer
> - UPDATE may fail due to internal hidden columns (`MV__KEY`); use DELETE + INSERT instead
> - Use DML only for special cases such as data correction

## Reference Documentation

- [CREATE DYNAMIC TABLE](https://www.yunqi.tech/documents/create-dynamic-table)
- [ALTER DYNAMIC TABLE](https://www.yunqi.tech/documents/alter-dynamic-table)
- [DROP DYNAMIC TABLE](https://www.yunqi.tech/documents/drop-dynamic-table)
- [SHOW DYNAMIC TABLES](https://www.yunqi.tech/documents/show-dynamic-table)
- [SHOW DYNAMIC TABLE REFRESH HISTORY](https://www.yunqi.tech/documents/refresh-history)
- [Dynamic Table Overview](https://www.yunqi.tech/documents/dynamic_table_summary)
- [View Dynamic Table Refresh Mode](https://www.yunqi.tech/documents/dynamic-table-incre)
- [Migrating Traditional Offline Jobs to Incremental](https://www.yunqi.tech/documents/transformt-dt)
- [Parameterized Dynamic Table](https://www.yunqi.tech/documents/dynamicTable-parmaters)
- [Dynamic Table DML Support](https://www.yunqi.tech/documents/dynamicTable-dml)
