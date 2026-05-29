# REFRESH DYNAMIC TABLE

## Overview

Manually triggers an immediate refresh of a dynamic table, forcing one incremental or full refresh before the next scheduled cycle. The system automatically selects the optimal strategy (incremental or full).

## Syntax

```Plain
REFRESH DYNAMIC TABLE [<schema_name>.]<dt_name>
```

## Parameters

- `<schema_name>`: Optional. Specifies the schema name; defaults to the current schema if omitted.
- `<dt_name>`: The name of the dynamic table to refresh.

## Examples

```sql
REFRESH DYNAMIC TABLE dt_hourly_stats;

REFRESH DYNAMIC TABLE doc_test.dt_hourly_stats;
```

## Notes

- A manual refresh triggers one additional refresh only and does not affect the existing automatic scheduling cycle.
- The system automatically determines whether to perform an incremental or full refresh; you cannot specify this manually.

## Related Documentation

- [REFRESH MATERIALIZED VIEW](refresh-materialized-view.md) — refresh a materialized view
- [CREATE DYNAMIC TABLE](create-dynamic-table.md)
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md) — pause/resume/modify the refresh interval
