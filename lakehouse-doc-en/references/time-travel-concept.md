# Time Travel Principles

Time Travel is Singdata Lakehouse's historical data access feature, allowing users to query data states at any point in time or recover deleted/modified data.

## What is Time Travel

Time Travel is implemented based on the MVCC (Multi-Version Concurrency Control) mechanism. Every table in Lakehouse maintains multiple historical versions. Each data change (INSERT/UPDATE/DELETE/TRUNCATE) generates a new version, while older versions remain accessible.

```
Timeline ----------------------------------------------------------->

Version 1: [A, B, C]          <-- Initial create
             |
Version 2: [A, B, C, D]       <-- Insert D
             |
Version 3: [A, X, C, D]       <-- Update B to X
             |
Version 4: [A, X, C]          <-- Delete D
             |
     Query any point-in-time snapshot
```

## How MVCC Works

### Version Generation

Each time a transaction commits, Lakehouse generates a new table version:

| Operation | Version Change |
|---|---|
| `INSERT` | New rows added, version number increments |
| `UPDATE` | Old version marks rows as deleted, new version inserts them |
| `DELETE` | Rows marked as deleted |
| `TRUNCATE` | Entire table marked as a new version (empty) |

### Version Query

Use the `TIMESTAMP AS OF` clause to query data at a specified point in time:

```sql
-- Query data from 1 hour ago
SELECT * FROM orders TIMESTAMP AS OF CURRENT_TIMESTAMP() - INTERVAL 1 HOUR;

-- Query data at a specific point in time
SELECT * FROM orders TIMESTAMP AS OF '2024-01-15 10:00:00';
```

The system finds the most recent version before that point in time and returns a snapshot of that version's data.

## Three Core Capabilities of Time Travel

### 1. Historical Data Query

Query data states at any past point in time, used for:
- Data comparison analysis (comparing changes at different points in time)
- Auditing and compliance (tracing historical data states)
- Troubleshooting (viewing data states before modification)

### 2. Data Recovery (UNDROP)

Recover deleted tables:

```sql
-- View deletion history
SHOW TABLES HISTORY;

-- Recover a deleted table
UNDROP TABLE orders;
```

**Scope**: Regular tables, dynamic tables, materialized views, table streams

### 3. Data Rollback (RESTORE)

Roll back a table to a specified point in time:

```sql
-- View version history
DESC HISTORY orders;

-- Roll back to a specified point in time
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-15 10:00:00';
```

**Difference from UNDROP**:
- `UNDROP`: Recovers a dropped table (the table no longer exists)
- `RESTORE`: Rolls back data in an existing table (the table still exists, but data was modified/deleted by mistake)

## Retention Period

The Time Travel retention period (`data_retention_days`) determines how long historical data remains accessible:

| Configuration | Description |
|---|---|
| Default value | 1 day (24 hours) |
| Value range | 0-90 days |
| Set to 0 | No historical versions are retained; Time Travel cannot be used |
| Beyond the period | Historical versions are physically deleted and cannot be recovered |

```sql
-- Change the retention period to 7 days
ALTER TABLE orders SET PROPERTIES ('data_retention_days'='7');
```

## Storage Cost

Time Travel consumes additional storage space to preserve historical versions:

- Storage cost is proportional to data change frequency and retention period
- Tables that are frequently updated consume more storage under long retention periods
- It is recommended to set the retention period appropriately based on business needs

## Usage Limitations

| Limitation | Description |
|---|---|
| Views not supported | Regular views do not store data and do not support Time Travel |
| External schemas not supported | Historical versions of external data sources are not managed by Lakehouse |
| Uncommitted real-time write data | Data written by RealtimeStream that has not been committed does not support Time Travel |
| Beyond retention period | Historical versions cannot be queried or recovered after physical deletion |

## Typical Scenarios

### Scenario 1: Recovering Accidentally Deleted Data

```sql
-- Accidentally executed DELETE
DELETE FROM orders WHERE date < '2024-01-01';

-- View data before deletion
SELECT COUNT(*) FROM orders TIMESTAMP AS OF '2024-01-15 09:59:00';

-- Recover data
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-15 09:59:00';
```

### Scenario 2: Recovering an Accidentally Dropped Table

```sql
-- Accidentally executed DROP TABLE
DROP TABLE important_data;

-- View deletion record
SHOW TABLES HISTORY LIKE 'important_data%';

-- Recover the table
UNDROP TABLE important_data;
```

### Scenario 3: Tracing Data Changes

```sql
-- View the version history of a table
DESC HISTORY orders;
+---------+-------------------------+------------+-------------+----------+-----------+
| version | time                    | total_rows | total_bytes | user     | operation |
+---------+-------------------------+------------+-------------+----------+-----------+
| 5       | 2024-01-15 11:00:00.000 | 1000       | 50000       | analyst  | INSERT    |
| 4       | 2024-01-15 10:30:00.000 | 950        | 47500       | etl_job  | UPDATE    |
| 3       | 2024-01-15 10:00:00.000 | 900        | 45000       | etl_job  | INSERT    |
+---------+-------------------------+------------+-------------+----------+-----------+

-- Compare data differences between version 3 and version 5
SELECT * FROM orders TIMESTAMP AS OF '2024-01-15 10:00:00'
EXCEPT
SELECT * FROM orders TIMESTAMP AS OF '2024-01-15 11:00:00';
```

## Related Documentation

- [Time Travel Queries](TIMETRAVEL.md)
- [UNDROP TABLE](UNDROP-TABLE.md)
- [RESTORE TABLE](restore.md)
- [DESC HISTORY](desc-history.md)
- [Data Lifecycle](data-lifecycle.md)
