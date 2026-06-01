# Map Join Optimization

## Introduction

Map Join is an efficient JOIN optimization in Lakehouse, particularly suited for **small table and large table** JOIN scenarios. Map Join broadcasts the small table to each compute node and completes the JOIN directly in the Map phase, avoiding expensive Shuffle and Reduce operations, thereby saving resources and improving query performance.

## Syntax

Add the `/*+ MAPJOIN(table_alias) */` hint to the query, where `table_alias` is the alias of the small table to be broadcast into memory:

```SQL
SELECT /*+ MAPJOIN(small_table_alias) */
    col1, col2, ...
FROM large_table large_alias
JOIN small_table small_table_alias
ON large_alias.key = small_table_alias.key;
```

## Advantages

1. Eliminates the Shuffle phase, reducing network transfer and disk I/O overhead.
2. Avoids data skew issues, since data does not need to be distributed by JOIN column.
3. Significantly improves query speed for small table JOIN large table scenarios.

## Notes

1. The small table must fit entirely in memory; otherwise it may cause out-of-memory errors. Lakehouse currently limits the small table size to **1 GB**.
2. Only suitable for small table and large table JOINs; not appropriate for large table and large table scenarios.

## Usage Examples

### Example 1: Employee and Department Join Query

The `departments` table (3 rows) is the small table; the `employees` table (5 rows) is the large table. Broadcast `departments` to each node to complete the JOIN.

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

### Example 2: Order and Product Join Query

The `products` table (5 rows) is the small table; the `orders` table is the large table.

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

### Example 3: Specifying Multiple Broadcast Tables in a Multi-Table JOIN

Multiple small tables can be specified in the same hint:

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

- The table name in the `MAPJOIN` hint is the **alias used in the query**, not the original table name.
- If the small table exceeds 1 GB, Lakehouse will ignore the hint and automatically fall back to a regular JOIN.
- Map Join does not support FULL OUTER JOIN or RIGHT OUTER JOIN (the small table must be on the right side).
- In Lakehouse, the optimizer also automatically selects Map Join based on statistics, so you don't need to add the hint manually every time.
