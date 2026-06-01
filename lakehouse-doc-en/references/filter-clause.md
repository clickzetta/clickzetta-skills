# FILTER Clause

`FILTER (WHERE condition)` is an optional clause for aggregate functions that filters rows before the aggregation is computed. It is equivalent to adding a condition inside the aggregation, but more concise than using `CASE WHEN`.

## Syntax

```Plain
aggregate_function(expr) FILTER (WHERE condition)
```

Applicable to all aggregate functions: `SUM`, `COUNT`, `AVG`, `MAX`, `MIN`, `GROUP_CONCAT`, etc.

## Comparison with CASE WHEN

```SQL
-- Traditional approach: CASE WHEN
SELECT
    SUM(CASE WHEN status = 'paid' THEN amount END)   AS paid_total,
    COUNT(CASE WHEN status = 'paid' THEN 1 END)      AS paid_count

-- FILTER approach: more concise
SELECT
    SUM(amount)  FILTER (WHERE status = 'paid')      AS paid_total,
    COUNT(*)     FILTER (WHERE status = 'paid')      AS paid_count
FROM orders;
```

## Examples

```SQL
-- Prepare data
CREATE TABLE doc_orders (id INT, amount INT, status STRING, region STRING);
INSERT INTO doc_orders VALUES
    (1, 100, 'paid',    'north'),
    (2, 200, 'pending', 'north'),
    (3, 150, 'paid',    'south'),
    (4, 300, 'paid',    'south'),
    (5, 80,  'pending', 'north');

-- Compute multiple conditional aggregations at once
SELECT
    SUM(amount)   FILTER (WHERE status = 'paid')              AS paid_total,
    SUM(amount)   FILTER (WHERE status = 'pending')           AS pending_total,
    COUNT(*)      FILTER (WHERE status = 'paid')              AS paid_count,
    AVG(amount)   FILTER (WHERE region = 'north')             AS north_avg,
    MAX(amount)   FILTER (WHERE status = 'paid' AND amount > 100) AS max_large_paid
FROM doc_orders;
```

| paid_total | pending_total | paid_count | north_avg | max_large_paid |
|-----------|--------------|-----------|-----------|---------------|
| 550 | 280 | 3 | 126 | 300 |

## Using FILTER with Window Functions

`FILTER` can also be combined with window functions:

```SQL
SELECT
    id,
    amount,
    SUM(amount) FILTER (WHERE status = 'paid') OVER (PARTITION BY region) AS region_paid_sum
FROM doc_orders;
```

## Notes

- The `FILTER` clause executes after `GROUP BY` and before `HAVING`.
- Conditions can reference original columns but cannot reference aliases defined in the SELECT list.
- `COUNT(*) FILTER (WHERE ...)` is equivalent to `COUNT_IF(condition)`.

## Related Documentation

- [GROUP BY](groupby.md)
- [Window Functions](windowfunction.md)
- [COUNT_IF](sql_functions/aggregate_functions/count_if.md)
