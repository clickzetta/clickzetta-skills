# SHOW DYNAMIC TABLE REFRESH HISTORY

## Overview

This command shows the refresh execution history for Dynamic Tables, including the refresh mode (incremental / full / skipped), duration, trigger type, row change counts, and failure reasons for each refresh. It is the primary tool for diagnosing whether refreshes are running normally, falling back to full, or accumulating.

## Syntax

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY [ WHERE <expr> ] [ LIMIT <num> ];
```

- `WHERE <expr>`: filter by any returned field. For example: `WHERE name = 'my_dt' AND state = 'FAILED'`
- `LIMIT <num>`: limit the number of returned rows. Range: 1–10000. Defaults to the most recent 100 rows.

## Return Fields

| Field | Type | Description |
|------|------|------|
| `workspace_name` | string | Workspace name |
| `schema_name` | string | Schema name |
| `name` | string | Dynamic Table name |
| `virtual_cluster` | string | VCluster used for this refresh |
| `start_time` | timestamp | Refresh start time |
| `end_time` | timestamp | Refresh end time |
| `duration` | object | Refresh elapsed time, format: `{"0":0,"1":0,"2":<nanoseconds>,"3":0}`. Divide the `"2"` field value by 1,000,000,000 to get seconds. |
| `state` | string | Execution result: `SUCCEED` / `FAILED` |
| `refresh_trigger` | string | Trigger type: `SYSTEM_SCHEDULED` (automatically triggered on schedule) / `MANUAL` (manually triggered by a user, including Studio scheduler triggers) |
| `refresh_mode` | string | Refresh mode. See description below. |
| `error_message` | string | Error message when the refresh failed; null on success |
| `source_tables` | array | List of upstream tables used in this incremental computation. Empty array when `NO_DATA`. |
| `stats` | object | Row change statistics. Only populated for `INCREMENTAL` refreshes. Format: `{"rows_deleted":"N","rows_inserted":"N"}` |
| `job_id` | string | Job ID. View details in the Studio job monitor. |

### refresh_mode Values

| Value | Meaning | stats |
|----|------|-------|
| `NO_DATA` | No upstream changes; this refresh was skipped with no computation | null |
| `INCREMENTAL` | Incremental computation; only upstream changed rows were processed | `{"rows_deleted":"N","rows_inserted":"N"}` |
| `FULL` | Full recomputation; the entire table was recomputed | null (or full row count) |

> 💡 **Tip**: For `INCREMENTAL`, `stats.rows_inserted` includes both new rows and updated rows (an UPDATE is internally represented as a delete followed by an insert). After `CREATE OR REPLACE DYNAMIC TABLE`, the first refresh may use `INCREMENTAL` mode but insert all rows (equivalent to a full rebuild); in that case `stats.rows_inserted` equals the total row count.

## Examples

View the most recent 10 refreshes for a specific Dynamic Table:

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY
WHERE name = 'dws_sales_dashboard'
LIMIT 10;
```

Filter for failed records:

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY
WHERE name = 'dws_sales_dashboard' AND state = 'FAILED';
```

View the most recent refreshes for all Dynamic Tables in the current Schema (omitting WHERE returns all in the current Schema):

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY LIMIT 100;
```

## Diagnosing Common Issues

**Is the refresh falling back to full?**

Check `refresh_mode`: `FULL` means the engine judged that the incremental cost was too high and automatically fell back to full. Persistent full refreshes suggest the SQL structure exceeds the incremental engine's processing scope; inspect the query.

**Is the refresh accumulating?**

Calculate `duration` from `start_time` and `end_time`, and compare with the refresh interval. If a single refresh takes close to or longer than the refresh interval, tasks are accumulating — the next run is triggered before the previous one finishes. Increase the refresh interval or upgrade the VCluster size.

**Are upstream source table changes being detected?**

For `INCREMENTAL` refreshes, `source_tables` lists upstream tables where changes were detected. If `source_tables` is empty and the result is `NO_DATA`, no new changes were detected from upstream during this scheduling cycle.

**Is `NO_DATA` normal?**

`NO_DATA` is normal. It means the upstream had no changes in this scheduling cycle and the engine skipped computation. It is not a failure or a problem.

## Related Documentation

- [Viewing Dynamic Table Refresh Mode](dynamic-table-incre.md) — relationship with this command (this page is the full reference; the linked page is an introduction)
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md) — manually trigger a refresh (`ALTER DYNAMIC TABLE dt REFRESH`)
- [Dynamic Table](om-dynamic-table.md) — refresh mechanism and usage limitations
