# REFRESH MATERIALIZED VIEW

## Overview

Manually triggers a full recomputation of a materialized view, completely rebuilding the data from the source tables and resetting the materialized view status to valid. A materialized view is automatically invalidated after DML changes to its source tables. Running this command restores its ability to participate in query rewriting.

## Syntax

```Plain
REFRESH MATERIALIZED VIEW [<schema_name>.]<mv_name>
```

## Parameters

- `<schema_name>`: Optional. Specifies the schema name; defaults to the current schema if omitted.
- `<mv_name>`: The name of the materialized view to refresh.

## Examples

```sql
REFRESH MATERIALIZED VIEW mv_sales_summary;

REFRESH MATERIALIZED VIEW doc_test.mv_sales_summary;
```

## Notes

- This performs a full recomputation. When source tables are large, this consumes significant compute resources. It is recommended to run this during off-peak hours.
- A materialized view is automatically invalidated after INSERT, UPDATE, or DELETE operations on its source tables. While invalidated, it can still be queried directly but does not participate in query rewriting.

## Related Documentation

- [REFRESH DYNAMIC TABLE](refresh-dynamic-table.md) — refresh a dynamic table
- [CREATE MATERIALIZED VIEW](create-materialized-view.md)
- [ALTER MATERIALIZED VIEW](alter-materialized-view.md) — pause/resume automatic refresh scheduling
