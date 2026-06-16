# Dynamic Table SQL Reference

> **⚠️ ClickZetta-specific Syntax**
> - Refresh scheduling: `REFRESH INTERVAL 5 MINUTE vcluster default` (not `TARGET_LAG`)
> - Modifying refresh interval or compute cluster requires `CREATE OR REPLACE`, `ALTER` does not support this
> - `ALTER DYNAMIC TABLE` only supports: SUSPEND / RESUME / SET COMMENT / RENAME COLUMN / CHANGE COLUMN COMMENT / SET/UNSET PROPERTIES
> - Drop using `DROP DYNAMIC TABLE` (not `DROP TABLE`)
> - Restore using `UNDROP TABLE` (not `UNDROP DYNAMIC TABLE`)
> - DESC using `DESC TABLE name` (does not support `DESC DYNAMIC TABLE name EXTENDED`)

Dynamic Tables are core incremental computation objects in ClickZetta Lakehouse. They are defined by SQL queries and refresh incrementally without manual scheduling.

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

**Key Parameters:**
- `REFRESH INTERVAL <n> MINUTE`: Refresh interval, minimum 1 minute
- `vcluster`: Name of compute cluster for running refresh tasks (directly followed by name, no equals sign or quotes)
- `OR REPLACE`: Replace if dynamic table with same name exists (must use this to modify SQL logic or scheduling configuration)
- Recommended to use GP-type cluster (e.g. `default`), AP-type clusters do not support small file compaction

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

> Note: To modify refresh interval, compute cluster, or SQL query logic, must use `CREATE OR REPLACE DYNAMIC TABLE`, ALTER does not support these operations.

## REFRESH DYNAMIC TABLE (Manual Trigger)

```sql
-- Manually trigger one refresh
REFRESH DYNAMIC TABLE <name>;
```

## DROP DYNAMIC TABLE

```sql
-- ⚠️ Must use DROP DYNAMIC TABLE, cannot use DROP TABLE
DROP DYNAMIC TABLE [ IF EXISTS ] <name>;

-- Restore deleted dynamic table (⚠️ use UNDROP TABLE, not UNDROP DYNAMIC TABLE)
UNDROP TABLE <name>;
```

## SHOW / DESC

```sql
-- List all dynamic tables in current schema
SHOW TABLES WHERE is_dynamic = true;

-- List dynamic tables in specified schema
SHOW TABLES IN <schema_name> WHERE is_dynamic = true;

-- View dynamic table structure
DESC TABLE <name>;

-- View complete CREATE TABLE statement
SHOW CREATE TABLE <name>;

-- View refresh history (status, duration, trigger method, incremental rows)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = '<dt_name>' LIMIT 20;
```

> ⚠️ **DESC Note**: For dynamic tables use `DESC TABLE name`, does not support `DESC DYNAMIC TABLE name EXTENDED` (EXTENDED will error).

## Important Notes

- To modify SQL logic, refresh interval, compute cluster → use `CREATE OR REPLACE`, cannot use `ALTER`
- Minimum refresh interval is 1 minute
- Drop using `DROP DYNAMIC TABLE` (not `DROP TABLE`)
- Restore using `UNDROP TABLE` (not `UNDROP DYNAMIC TABLE`)
- Refresh failures do not affect table queryability (returns data from last successful version)
- Non-simple add/drop column `CREATE OR REPLACE` triggers a full refresh
- Recommended to use GP-type cluster (e.g. `default`), AP-type clusters do not support small file compaction

## Parameterized Dynamic Tables (SESSION_CONFIGS)

Use `SESSION_CONFIGS()` function to define parameterized queries, pass partition values during refresh to control refresh scope:

```sql
-- Create parameterized dynamic table
CREATE OR REPLACE DYNAMIC TABLE dwd.orders_partitioned
  REFRESH INTERVAL 30 MINUTE vcluster default
AS
SELECT order_id, user_id, amount, dt
FROM ods.orders
WHERE dt = SESSION_CONFIGS('target_date', CAST(CURRENT_DATE() AS STRING));

-- Manually trigger refresh with parameter
REFRESH DYNAMIC TABLE dwd.orders_partitioned
  WITH PROPERTIES ('target_date' = '2024-06-15');
```

Use case: Transforming traditional daily full ETL into incremental tasks, use SESSION_CONFIGS to replace scheduling variables.

## Dynamic Table DML Operations

Dynamic tables do not support DML by default, must enable parameter first (need SET before each DML):

```sql
-- ⚠️ Must execute SET in same session/batch, then execute DML
SET cz.sql.dt.allow.dml = true;
INSERT INTO <name> VALUES (...);

-- Delete
SET cz.sql.dt.allow.dml = true;
DELETE FROM <name> WHERE ...;
```

> ⚠️ **DML Notes**:
> - `SET cz.sql.dt.allow.dml = true` must be in same execution batch with DML statement
> - After executing DML, next auto-refresh will trigger **full refresh** (not incremental), may take longer
> - UPDATE may error due to internal hidden column (`MV__KEY`), recommend using DELETE + INSERT instead
> - Only use DML in special scenarios like data correction

## Reference Documentation

- [CREATE DYNAMIC TABLE](https://www.yunqi.tech/documents/create-dynamic-table)
- [ALTER DYNAMIC TABLE](https://www.yunqi.tech/documents/alter-dynamic-table)
- [DROP DYNAMIC TABLE](https://www.yunqi.tech/documents/drop-dynamic-table)
- [SHOW DYNAMIC TABLES](https://www.yunqi.tech/documents/show-dynamic-table)
- [SHOW DYNAMIC TABLE REFRESH HISTORY](https://www.yunqi.tech/documents/refresh-history)
- [Dynamic Table Introduction](https://www.yunqi.tech/documents/dynamic_table_summary)
- [View Dynamic Table Refresh Mode](https://www.yunqi.tech/documents/dynamic-table-incre)
- [Traditional Offline Task to Incremental Practice](https://www.yunqi.tech/documents/transformt-dt)
- [Dynamic Table Parameterized Definition Support](https://www.yunqi.tech/documents/dynamicTable-parmaters)
- [Dynamic Table DML Statement Support](https://www.yunqi.tech/documents/dynamicTable-dml)
