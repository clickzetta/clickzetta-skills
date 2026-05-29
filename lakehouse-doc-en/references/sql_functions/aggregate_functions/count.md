### COUNT Function

#### Description

The `COUNT` function returns the number of rows in a set of data. It can count the total number of all rows, the number of non-`NULL` values in specified columns, or the number of distinct values in specified columns.

#### Syntax

```sql
COUNT(*) [FILTER (WHERE condition)]
COUNT([DISTINCT] expr1[, expr2, ...]) [FILTER (WHERE condition)]
```

#### Parameters

* `exprN`: An expression of any type.

#### Return Results

* The return value type is `BIGINT`.
* When using the `COUNT(*)` form, all rows are counted, including those containing `NULL` values.
* When using the `COUNT(expr1[, expr2, ...])` form, if any column in a row is `NULL`, that row is ignored.
* When using the `COUNT(DISTINCT expr1[, expr2, ...])` form, the specified columns are first deduplicated, and then the number of non-`NULL` values is counted.

#### Examples

1. Count all rows (including those containing `NULL` values):
```sql
SELECT COUNT(*) FROM VALUES (NULL), (1), (3), (4) AS tab(col);
+----------+
| count(1) |
+----------+
| 4        |
+----------+
```

2. Count the number of non-`NULL` values in the specified columns:
```sql
SELECT COUNT(a, b) FROM VALUES (NULL, NULL), (1, NULL), (NULL, 3), (4, 5) AS tab(a, b);
+------------+
| count(a,b) |
+------------+
| 1          |
+------------+
```

3. Count the number of distinct values in the specified columns (ignoring `NULL` values):
```sql
SELECT COUNT(DISTINCT a, b)
FROM VALUES (1, NULL), (1, NULL), (4, 5), (4, 5), (1, 2) AS tab(a, b);
+-----------------------+
| count(DISTINCT a, b)  |
+-----------------------+
| 2                     |
+-----------------------+
```

4. Count the number of rows with a specific value in a column:
```sql
SELECT COUNT(*) FROM customers WHERE status = 'active';
+----------+
| count(1) |
+----------+
| 150      |
+----------+
```

5. Count the number of distinct products in sales records (ignoring `NULL` values):
```sql
SELECT COUNT(DISTINCT product_id) FROM sales_records;
+------------------------------+
| count(DISTINCT `product_id`) |
+------------------------------+
| 50                           |
+------------------------------+
```

6. Use the FILTER clause to conditionally count rows:
```sql
SELECT COUNT(*) FILTER (WHERE col > 2) FROM VALUES (1), (2), (3), (4), (NULL) AS tab(col);
+--------------------------------------+
| count(1) FILTER (WHERE (col > 2))    |
+--------------------------------------+
| 2                                    |
+--------------------------------------+
```

7. Combine the FILTER clause with DISTINCT to count distinct values:
```sql
SELECT COUNT(DISTINCT a) FILTER (WHERE b > 1) FROM VALUES (1, 1), (1, 2), (2, 2), (3, 1) AS tab(a, b);
+------------------------------------------------------+
| count(DISTINCT a) FILTER (WHERE (b > 1))             |
+------------------------------------------------------+
| 2                                                    |
+------------------------------------------------------+
```
