# Drop Materialized View (DROP MATERIALIZED VIEW)

## Usage

The `DROP MATERIALIZED VIEW` command is used to drop an existing materialized view in order to release related resources.

> **Data Recovery**: After a materialized view is dropped, it can be restored within the data retention period (default 1 day, configurable up to 90 days) using the `UNDROP TABLE` command. Note that the recovery syntax uniformly uses `UNDROP TABLE`, not `UNDROP MATERIALIZED VIEW`.

## Syntax

```sql
DROP MATERIALIZED VIEW [ IF EXISTS ] [schema_name.]<mv_name>
```

## Parameter Description

| Parameter | Description |
|---|---|
| `IF EXISTS` | Optional. If the materialized view does not exist, no error is thrown |
| `schema_name` | Optional. The name of the schema |
| `mv_name` | The name of the materialized view to drop |

## Examples

### Example 1: Drop a materialized view

```sql
DROP MATERIALIZED VIEW my_mv;
```

### Example 2: Safe drop (no error if the materialized view does not exist)

```sql
DROP MATERIALIZED VIEW IF EXISTS my_mv;
```

### Example 3: Drop a materialized view in a specified schema

```sql
DROP MATERIALIZED VIEW analytics.order_stats_mv;
```

### Example 4: Drop and restore

```sql
-- Drop the materialized view
DROP MATERIALIZED VIEW analytics.order_stats_mv;

-- Restore the materialized view (note: use UNDROP TABLE, not UNDROP MATERIALIZED VIEW)
UNDROP TABLE analytics.order_stats_mv;

-- Verify restoration
SELECT * FROM analytics.order_stats_mv;
```

## Notes

- **Object Type Matching**: To drop a materialized view, you must use `DROP MATERIALIZED VIEW`. Using `DROP TABLE` will result in an error:
  ```
  The operation 'DROP TABLE' requires a 'TABLE'. 
  But 'xxx' is a MATERIALIZED VIEW, please use 'DROP MATERIALIZED VIEW' instead.
  ```

- **Batch Dropping Not Supported**: The syntax `DROP MATERIALIZED VIEW mv1, mv2, mv3` is not supported. You must drop each one individually.

- **Data Recovery**: Within the `data_retention_days` retention period, a dropped materialized view can be restored via `UNDROP TABLE`.

- **Dependency Check**: Before dropping, confirm that the materialized view is no longer referenced by other queries or objects.

## Related Documents

- [CREATE MATERIALIZED VIEW](create-materialized-view.md): Create a materialized view
- [UNDROP TABLE](UNDROP-TABLE.md): Restore a dropped table / dynamic table / materialized view
