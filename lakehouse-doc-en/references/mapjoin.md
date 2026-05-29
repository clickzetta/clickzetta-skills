# Map Join Optimization

## Overview

Map Join is an efficient JOIN optimization technique in Lakehouse, especially suitable for **small table to large table** JOIN scenarios. Map Join broadcasts the small table to each compute node and completes the JOIN directly in the Map phase, avoiding expensive Shuffle and Reduce processes, thereby saving resources and improving query performance.

## Syntax

Add the `/*+ MAPJOIN(table_alias) */` hint to the query, where `table_alias` is the alias of the small table to broadcast into memory:

```SQL
SELECT /*+ MAPJOIN(small_table_alias) */
    col1, col2, ...
FROM large_table large_alias
JOIN small_table small_table_alias
ON large_alias.key = small_table_alias.key;
```

## Advantages

1. Eliminates the Shuffle phase, reducing network transfer and disk I/O overhead.
2. Avoids data skew issues since data does not need to be distributed by the JOIN column.
3. Significantly improves query performance for small-table-to-large-table JOIN scenarios.

## Limitations

1. The small table must fit entirely in memory; otherwise, an out-of-memory error may occur. Currently, Lakehouse limits the small table size to **1 GB**.
2. Only applicable to small-table-to-large-table JOINs, not suitable for large-table-to-large-table scenarios.

## Examples

### Example 1: Employee and department association query

The `departments` table (3 rows) is a small table, and the `employees` table (5 rows) is a large table. Broadcast `departments` to each node to complete the JOIN.

```SQL
SELECT /*+ MAPJOIN(d) */
    e.id,
    e.name,
    e.salary,
    d.dept_name,
    d.manager
FROM doc_test.employees e
JOIN doc_test.departments d
ON e.dept = d.dept_name;
```

Result:

```
+----+-------+----------+-------------+---------+
| id | name  | salary   | dept_name   | manager |
+----+-------+----------+-------------+---------+
|  1 | Alice | 12000.00 | Engineering | Charlie |
|  2 | Bob   |  9500.00 | Engineering | Charlie |
|  3 | Carol |  8500.00 | Marketing   | Diana   |
|  4 | Dave  |  6500.00 | Marketing   | Diana   |
|  5 | Eve   |  6000.00 | HR          | Frank   |
+----+-------+----------+-------------+---------+
```

### Example 2: Order and product association query

The `products` table (5 rows) is a small table, and the `orders` table is a large table.

```SQL
SELECT /*+ MAPJOIN(p) */
    o.order_id,
    o.customer_id,
    o.amount,
    p.name   AS product_name,
    p.price  AS unit_price,
    p.category
FROM doc_test.orders o
JOIN doc_test.products p
ON o.product = p.name;
```

### Example 3: Multi-table JOIN with multiple broadcast tables

You can specify multiple small tables in a single hint:

```SQL
SELECT /*+ MAPJOIN(d, p) */
    e.name,
    d.dept_name,
    p.name AS product_name
FROM doc_test.employees e
JOIN doc_test.departments d ON e.dept = d.dept_name
JOIN doc_test.products p    ON p.category = 'Electronics';
```

## Notes

- The table name in the `MAPJOIN` hint is the **query alias**, not the original table name.
- If the small table exceeds 1 GB, Lakehouse ignores the hint and automatically falls back to a regular JOIN.
- Map Join does not support FULL OUTER JOIN and RIGHT OUTER JOIN (the small table must be on the right side).
- In Lakehouse, the optimizer can also automatically select Map Join based on statistics, so manual hints are not always required.
