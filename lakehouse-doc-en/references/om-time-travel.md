# Time Travel

Time Travel is the Lakehouse's **historical data access and recovery** mechanism, allowing you to query the data state of a table at any historical point in time, or roll back a table to a previous version.

## What You Can Do

| Capability | Description |
|------|------|
| Query historical data | View the data state of a table at a specific point in time |
| Recover accidentally deleted data | Roll back a table to a version before the erroneous operation |
| Recover dropped tables | Restore a dropped table using `UNDROP TABLE` |
| Audit data changes | View the historical version list of a table |

## Quick Example

```sql
-- Query data at a specific time yesterday
SELECT * FROM orders
TIMESTAMP AS OF '2024-01-15 10:00:00';

-- View the historical versions of a table
DESC HISTORY orders;

-- Roll back a table to a specified version
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-15 10:00:00';

-- Recover a dropped table
UNDROP TABLE orders;
```

> ⚠️ `TIMESTAMP AS OF` only accepts literal constants and does not support expressions like `NOW() - INTERVAL 1 DAY`.

## Data Retention Configuration

The historical data retention period for Time Travel is controlled by `data_retention_days`, with a default of 1 day and a maximum of 90 days. Historical versions beyond the retention period cannot be accessed.

```sql
-- Set the data retention days for a table
ALTER TABLE orders SET data_retention_days = 7;
```

## Related Documentation

- [Time Travel Detailed Description](timetravel-summary.md)
- [Time Travel Concepts](time-travel-concept.md)
- [Data Lifecycle Management](data-lifecycle.md)
