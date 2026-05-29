# Query Syntax

Query syntax covers the complete syntax for SELECT statements, including JOIN, aggregation, window functions, Time Travel historical queries, and execution plan analysis.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [SELECT Basic Syntax](query-syntax.md) | Full syntax for SELECT, FROM, WHERE, ORDER BY, LIMIT |
| [WITH (Common Table Expressions)](WITH.md) | CTE syntax — name subqueries for reuse and improved readability |
| [JOIN](JOIN.md) | INNER/LEFT/RIGHT/FULL/CROSS JOIN syntax and examples |
| [Map Join](mapjoin.md) | JOIN optimization hint to force small-table broadcast |
| [LATERAL VIEW](lateralview.md) | Expand array or map columns; used with explode/posexplode |
| [GROUP BY](groupby.md) | Aggregation grouping; supports ROLLUP, CUBE, GROUPING SETS |
| [Window Functions](WINDOWFUNCTION.md) | OVER clause, PARTITION BY, ORDER BY, window frame definition |
| [TABLESAMPLE](tablesample.md) | Random sampling of a table for quick data exploration |
| [QUALIFY](sql-qualify.md) | Filter window function results; equivalent to wrapping a WHERE around a window function |
| [Set Operations (UNION/INTERSECT/EXCEPT)](set-operations.md) | Merge, intersect, and subtract results from multiple queries |
| [VALUES](values.md) | Inline data — construct row sets without creating a table |
| [TIME TRAVEL](TIMETRAVEL.md) | Query historical versions of a table by timestamp or version number |
| [EXPLAIN](EXPLAIN.md) | View the query execution plan for performance analysis and optimization |

---

## Common Operations

### Basic Query

```SQL
-- Query with filter and sort
SELECT order_id, customer_id, amount
FROM public.orders
WHERE created_at >= '2024-01-01'
ORDER BY amount DESC
LIMIT 100;
```

### CTE (Common Table Expression)

```SQL
WITH monthly_sales AS (
  SELECT DATE_TRUNC('month', order_date) AS month,
         SUM(amount) AS total
  FROM orders
  GROUP BY 1
)
SELECT month, total,
       total - LAG(total) OVER (ORDER BY month) AS mom_change
FROM monthly_sales;
```

### Window Functions

```SQL
-- Rank within group
SELECT customer_id, order_id, amount,
       RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS rank_in_customer
FROM orders;

-- Rolling average
SELECT order_date, amount,
       AVG(amount) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_7d
FROM daily_sales;
```

### Time Travel

```SQL
-- Query historical data at a specific point in time
SELECT * FROM orders TIMESTAMP AS OF '2024-01-15 00:00:00';

-- Query historical data at a specific version
SELECT * FROM orders VERSION AS OF 5;
```

### EXPLAIN

```SQL
-- View execution plan
EXPLAIN SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [Time Travel Guide](time_travel_guide.md) | Complete use cases and notes for Time Travel |
| [SQL Functions](functions.md) | Complete built-in function reference |
