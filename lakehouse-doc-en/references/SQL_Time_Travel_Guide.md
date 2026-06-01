# Lakehouse Time Travel Data Recovery Guide

## Overview

In data warehouse operations, accidentally deleted data, erroneous updates, or the need to compare historical states are common scenarios. Singdata Lakehouse provides Time Travel functionality, allowing you to query data from any historical version and even recover deleted tables. This guide is organized by business scenario to help you quickly master historical data recovery and restoration methods.

### Quick Navigation

* [Query Historical Version Data](#query-historical-version-data) -- Use TIMESTAMP AS OF to travel back
* [Compare Historical and Current Data](#compare-historical-and-current-data) -- Use UNION ALL to compare changes
* [Recover Accidentally Dropped Tables](#recover-accidentally-dropped-tables) -- Use UNDROP TABLE to recover
* [Restore to a Specific Point in Time](#restore-to-a-specific-point-in-time) -- Use RESTORE TABLE to rollback

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `SELECT ... TIMESTAMP AS OF` | Query a historical version | View data before erroneous operations, audit |
| `SHOW TABLES HISTORY` | View table deletion history | Confirm information about accidentally dropped tables |
| `UNDROP TABLE` | Recover a dropped table | Quick recovery after accidental table drop |
| `RESTORE TABLE TO TIMESTAMP AS OF` | Restore a table to a specific point in time | Data rollback after erroneous updates |
| `DESC HISTORY` | View table operation history | Audit table change operations |

***

## Prerequisites

The following examples use a simulated orders table `orders_history`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS orders_history (
    order_id INT,
    customer_id INT,
    amount DOUBLE,
    status STRING
);

-- Insert initial data
INSERT INTO orders_history VALUES
(1, 101, 500, 'completed'),
(2, 102, 300, 'pending');
```

***

## Query Historical Version Data

Use `TIMESTAMP AS OF` to query the table's data state at a specific point in time.

```sql
-- Query the data from 1 minute ago (ensure a historical version exists at that point in time)
SELECT * FROM orders_history 
TIMESTAMP AS OF (CURRENT_TIMESTAMP() - INTERVAL '1' MINUTE);
```

**Result Explanation**:
* If no write operations have been performed on the table within the last hour, the current data is returned.
* If write operations have been performed, the historical version before the write is returned.

> ⚠️ **Note**: The Time Travel retention period defaults to 1 day and can be configured up to 90 days. Data beyond the retention period cannot be queried.

***

## Compare Historical and Current Data

Combine historical and current data in a single query to quickly identify data changes.

```sql
-- Compare current data with data from 1 hour ago
SELECT 'current' as version, * FROM orders_history
UNION ALL
SELECT '1_hour_ago' as version, * FROM orders_history 
TIMESTAMP AS OF (CURRENT_TIMESTAMP() - INTERVAL '1' HOUR)
ORDER BY order_id, version DESC;
```

**Use Cases**:
* Audit data changes
* Troubleshoot erroneous updates
* Verify ETL results

***

## Recover Accidentally Dropped Tables

After accidentally dropping a table, use `UNDROP TABLE` for quick recovery.

```sql
-- Simulate an accidental drop
DROP TABLE orders_history;

-- View deletion history
SHOW TABLES HISTORY LIKE 'orders_history';

-- Recover the table
UNDROP TABLE orders_history;
```

**Result Verification**:

```sql
SELECT * FROM orders_history;
```

> 💡 **Tip**: Recovered tables retain their original table type (e.g., a Dynamic Table remains a Dynamic Table after recovery).

***

## Restore to a Specific Point in Time

Use `RESTORE TABLE` to roll back table data to a specific point in time, suitable for erroneous update scenarios.

```sql
-- Erroneous update
UPDATE orders_history SET status = 'cancelled';

-- Restore to the state before the update
RESTORE TABLE orders_history TO TIMESTAMP AS OF (CURRENT_TIMESTAMP() - INTERVAL '5' MINUTE);
```

**Notes**:
* `RESTORE TABLE` overwrites current data; use with caution.
* It is recommended to back up the current data to a new table before restoring: `CREATE TABLE backup AS SELECT * FROM orders_history;`

***

## View Table Operation History

Use `DESC HISTORY` to view all change records for a table.

```sql
-- View table history
DESC HISTORY orders_history;
```

**Returned Information**:
* `version`: Version number
* `time`: Operation time
* `operation`: Operation type (INSERT, UPDATE, DELETE, etc.)
* `user`: Executing user

***

## Clean Up Test Data

After completing Time Travel verification, it is recommended to clean up the test table:

```sql
-- Drop test table
DROP TABLE IF EXISTS orders_history;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Retention Period Configuration**: Set via the `data_retention_days` parameter; defaults to 1 day. Important tables are recommended to be set to 7 days or longer.
2. **Storage Cost**: Time Travel retains historical version data, consuming additional storage space.
3. **Dynamic Tables**: Dynamic Tables also support Time Travel, but historical versions are overwritten after refresh.
4. **RESTORE Limitations**: `RESTORE TABLE` does not support Materialized Views; it only applies to regular tables and Dynamic Tables.

***

## Related Documentation

* [Time Travel](timetravel.md)
* [UNDROP TABLE](undrop-table.md)
* [RESTORE TABLE](restore.md)
