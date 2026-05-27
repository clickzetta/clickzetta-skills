# Dynamic Table

Dynamic Table is an **auto-maintained data processing object** in Lakehouse — you define a SQL query, and the system automatically performs incremental computation and persists the results. No manual writes are needed.

Analogy: A Dynamic Table is like an "auto-refreshing Excel formula sheet" — when the underlying data changes, the results update automatically.

## Comparison with Other Table Types

| Aspect | Dynamic Table | Regular Table | Materialized View | View |
|--------|--------|--------|----------|------|
| Data Stored | Yes | Yes | Yes | No |
| Auto-refresh | Incremental refresh | Manual write | Refresh | — |
| DML Support | No | Yes | No | No |
| Primary Use | Data processing pipelines | Raw data storage | Query acceleration | Logic encapsulation |

**When to use a Dynamic Table**: When you need to automatically compute and store results based on upstream tables. The typical scenario is the ODS → DWD → ADS data processing pipeline.

**When not to use a Dynamic Table**: If you only need transparent acceleration of existing queries, use a Materialized View. If you only need logic encapsulation without storing data, use a View.

## Refresh Mechanism

Dynamic Tables support two refresh modes, automatically selected by the system based on query complexity:

- **Incremental refresh**: Only processes data added since the last refresh. Fast with low resource consumption.
- **Full refresh**: Recomputes all data. Suitable for complex aggregations or queries that cannot be processed incrementally.

Refresh is controlled by the `TARGET_LAG` parameter, with a minimum setting of `1 MINUTE`.

## Quick Example

```sql
-- Create a Dynamic Table: compute daily order amounts
CREATE DYNAMIC TABLE dws_daily_orders
TARGET_LAG = '5 MINUTES'
AS
SELECT
    DATE(created_at) AS order_date,
    COUNT(*)         AS order_cnt,
    SUM(amount)      AS total_amount
FROM ods_orders
GROUP BY DATE(created_at);
```

## Related Documents

- [Dynamic Table Introduction](dynamic_table_summary.md) — core concepts and working principles
- [CREATE DYNAMIC TABLE](create-dynamic-table.md) — full syntax
- [Incremental Computing](incremental-computing.md) — incremental refresh principles
- [Real-time Pipeline Selection Guide](realtime-pipeline-selection-guide.md)
