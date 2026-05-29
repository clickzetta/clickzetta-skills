# Refresh Materialized View or Dynamic Table (REFRESH)

## Description

The `REFRESH` command is used to manually trigger a data refresh for materialized views or dynamic tables, ensuring they reflect the latest source table data.

- **Materialized View**: When the source table undergoes data changes, the materialized view automatically becomes invalid and cannot be used for query rewriting. Manually executing `REFRESH` restores the materialized view to a valid state.
- **Dynamic Table**: Dynamic tables typically refresh automatically based on the configured refresh interval. Manually executing `REFRESH` triggers an immediate refresh before the next scheduled cycle.

For more details, see [Materialized View](MATERIALIZEDVIEW.md).

## Syntax

### Refresh a Materialized View

```Plain
REFRESH MATERIALIZED VIEW [schema_name.]<mv_name>
```

### Refresh a Dynamic Table

```Plain
REFRESH DYNAMIC TABLE [schema_name.]<dt_name>
```

## Parameter Description

| Parameter | Required | Description |
|---|---|---|
| `schema_name` | No | Specifies the schema name. If not specified, the current schema is used by default. |
| `mv_name` | Yes (Materialized View) | The name of the materialized view to refresh. |
| `dt_name` | Yes (Dynamic Table) | The name of the dynamic table to refresh. |

## Return Value

`REFRESH` does not return a result set upon successful execution.

## Examples

### Example 1: Refresh a Materialized View

```SQL
REFRESH MATERIALIZED VIEW doc_test.mv_test_sales;
```

### Example 2: Refresh a Materialized View in the Current Schema

```SQL
REFRESH MATERIALIZED VIEW mv_sales_summary;
```

### Example 3: Refresh a Dynamic Table

```SQL
REFRESH DYNAMIC TABLE doc_test.dt_test_refresh;
```

### Example 4: Refresh a Dynamic Table in the Current Schema

```SQL
REFRESH DYNAMIC TABLE dt_hourly_stats;
```

## Notes

- **Difference between materialized views and dynamic tables**:
  - `REFRESH MATERIALIZED VIEW` performs a full recomputation, completely rebuilding the materialized view data from the source tables.
  - `REFRESH DYNAMIC TABLE` determines whether to perform an incremental or full refresh based on system assessment, automatically selecting the optimal strategy.

- **Resource consumption**: Refresh operations consume compute resources, especially when the source table contains a large volume of data. It is recommended to execute refreshes during off-peak hours to avoid impacting other queries.

- **Invalid state**: A materialized view automatically becomes invalid after DML operations (such as INSERT, UPDATE, DELETE) on the source table. While invalid, the materialized view does not participate in query rewriting but can still be directly queried (returning data from the last refresh).

- **Dynamic table automatic refresh**: Dynamic tables are usually scheduled automatically based on the `REFRESH INTERVAL` configuration. A manual `REFRESH` only triggers one additional refresh and does not affect the automatic scheduling cycle.

- **Viewing refresh history**: Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to view the historical refresh records of a dynamic table, including whether it was an incremental refresh and the refresh duration.

## Related Commands

- [CREATE MATERIALIZED VIEW](create-materialized-view.md): Creates a materialized view.
- [CREATE DYNAMIC TABLE](create-dynamic-table.md): Creates a dynamic table.
- [SHOW DYNAMIC TABLE REFRESH HISTORY](refresh-history.md): Views the refresh history of a dynamic table.
- [DESC EXTENDED](desc-materialized-view.md): Views detailed information about a materialized view.
