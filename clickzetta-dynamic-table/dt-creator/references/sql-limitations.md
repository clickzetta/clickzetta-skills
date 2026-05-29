# Dynamic Table SQL Limitations and Support Matrix

This document lists the SQL patterns that Dynamic Table incremental computation supports and does not support.

## JOIN Type Support

| JOIN type | Incremental support | Notes |
|-----------|---------|------|
| INNER JOIN | ✅ | Fully supported |
| LEFT JOIN (LEFT OUTER) | ✅ | Fully supported |
| RIGHT JOIN (RIGHT OUTER) | ✅ | Fully supported |
| FULL OUTER JOIN | ✅ | Fully supported |
| LEFT SEMI JOIN | ✅ | Fully supported |
| LEFT ANTI JOIN | ✅ | Fully supported |

## Aggregate Function Support

### Aggregate functions that support incremental computation

- `SUM`, `SUM0`, `COUNT`, `COUNT_IF`, `MIN`, `MAX`, `MIN_BY`, `MAX_BY`
- `AVG`, `STDDEV_SAMP`, `STDDEV_POP`, `VAR_SAMP`, `VAR_POP`
- `Percentile`, `Median`, `COUNT_DISTINCT`
- `BIT_OR`, `BIT_AND`, `BIT_XOR`, `BOOL_OR`, `BOOL_AND`
- `GROUP_BITMAP` series
- `COLLECT_SET`, `COLLECT_LIST`, `COLLECT_SET_ON_ARRAY`, `COLLECT_LIST_ON_ARRAY`
- `MAP_AGG`, `WM_CONCAT`

### Aggregate functions with unstable results (incremental results may differ from full refresh)

- `ANY_VALUE`, `FIRST_VALUE`, `LAST_VALUE`
- `APPROX_COUNT_DISTINCT`, `APPROX_HISTOGRAM`, `APPROX_TOP_K`, `APPROX_PERCENTILE`
- `JSON_MERGE_AGG`

## Window Function Support

### Supported window functions

- `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `PERCENT_RANK`
- `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`
- `COUNT`, `SUM`, `SUM0`, `MIN`, `MAX`, `AVG`
- `LEAD`, `LAG`, `CUME_DIST`, `NTILE`
- `COLLECT_LIST`, `COLLECT_SET`, `COLLECT_SET_ON_ARRAY`, `COLLECT_LIST_ON_ARRAY`

## ORDER BY / LIMIT / OFFSET

`ORDER BY`, `LIMIT`, and `OFFSET` syntax are supported.

⚠️ Global `ORDER BY` inside a DT is not recommended. Global sorting has very high overhead on every incremental refresh. It is recommended to apply sorting logic when querying data downstream, not during the ETL modeling stage.

## Non-deterministic Functions

Non-deterministic functions (such as `NOW()`, `CURRENT_TIMESTAMP`, `CURRENT_DATE`, `random()`, etc.) are supported by default when they do not participate in computation logic. Specifically, as long as these functions do not appear in the following positions, they can be used normally:
- `PARTITION BY` key of a window function
- `JOIN` key
- `GROUP BY` key
- Input arguments of other functions

Typical use case: output the data processing time directly in SELECT, recording the moment each row was processed by the DT refresh:

```sql
CREATE DYNAMIC TABLE order_with_process_time AS
SELECT
    id,
    amount,
    status,
    CURRENT_TIMESTAMP AS process_time  -- records the processing time at refresh; output directly to target table
FROM orders
WHERE status = 'completed';
```

Time functions are constant-folded to the current refresh timestamp on each REFRESH.

## UDF / UDAF / UDTF

Custom functions must be declared as deterministic at creation time to use incremental computation in a DT. Custom functions not declared as deterministic will cause incremental computation to be disabled.

## Source Table Type Limitations

- **Virtual views (VIEW)**: cannot be used as input tables for a DT; will disable incremental computation
- **External tables (External Table)**: incremental computation is not supported
