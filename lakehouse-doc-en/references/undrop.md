# UNDROP Command Reference

## Description

Restores deleted Singdata Lakehouse data objects. `UNDROP` relies on the Time Travel mechanism and can only restore objects that were deleted within the data retention period.

## Syntax

```sql
UNDROP TABLE <table_name>
```

> ⚠️ **Note**: `UNDROP` currently uses the unified `UNDROP TABLE` syntax, regardless of whether the original object was a regular table, dynamic table, or materialized view.

## Supported Object Types

| Object Type | Recovery Syntax | Prerequisites |
|---------|---------|---------|
| Regular Table | `UNDROP TABLE <name>` | Within the `data_retention_days` retention period |
| Dynamic Table | `UNDROP TABLE <name>` | Within the `data_retention_days` retention period |
| Materialized View | `UNDROP TABLE <name>` | Within the `data_retention_days` retention period |

Objects such as views, external tables, schemas, and VClusters do not support UNDROP and cannot be restored via this command after being dropped.

## Notes

- If an object with the same name already exists, `UNDROP` will error. You must rename or drop the existing object first.
- Objects beyond the Time Travel retention period cannot be restored. The default retention period is 1 day, adjustable via the `data_retention_days` property.
- `UNDROP` restores the object definition and data, but does not restore views or dynamic tables that depend on the object.

## Syntax Reference

- [UNDROP TABLE](UNDROP-TABLE.md)
- [UNDROP DYNAMIC TABLE](undrop-dynamic-table.md)
- [UNDROP MATERIALIZED VIEW](undrop-materialized-view.md)
- [Time Travel](time-travel-concept.md)
