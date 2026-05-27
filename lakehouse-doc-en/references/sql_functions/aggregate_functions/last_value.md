### LAST_VALUE Function

```
last_value(expr [, ignoreNulls]) [FILTER (WHERE condition)]
last(expr [, ignoreNulls]) [FILTER (WHERE condition)]
```

#### Description

The `LAST_VALUE` function returns the last value in an aggregation group or window. You can optionally choose whether to ignore `NULL` values. `last` is an alias for `last_value`.

#### Parameters

* `expr`: An expression of any type whose last value is to be retrieved.
* `ignoreNulls`: An optional boolean parameter, defaulting to `false`.
  * `false` (default): returns the last value, even if it is `NULL`.
  * `true`: ignores `NULL` values, returns the last non-`NULL` value.

#### Return Type

* Returns the same data type as the input expression.
* Returns the last value in the aggregation group or window.

#### Notes

* If all values are `NULL` (and `ignoreNulls` is `true`), returns `NULL`.
* If the input is an empty set, returns `NULL`.
* In a `GROUP BY` query, returns the last value for each group. Use `WITHIN GROUP (ORDER BY ...)` to specify a deterministic order.

#### Examples

1. Basic usage: return the last value

```sql
SELECT last_value(col), last(col)
FROM VALUES (10), (5), (20) AS tab(col);
+-----------------+-----------+
| last_value(col) | last(col) |
+-----------------+-----------+
| 20              | 20        |
+-----------------+-----------+
```

2. Handling NULL values (default: returns the last value, even if NULL)

```sql
SELECT last_value(col), last(col)
FROM VALUES (NULL), (5), (NULL) AS tab(col);
+-----------------+-----------+
| last_value(col) | last(col) |
+-----------------+-----------+
| NULL            | NULL      |
+-----------------+-----------+
```

3. Ignore NULL values, return the last non-NULL value

```sql
SELECT last_value(col, true), last(col, true)
FROM VALUES (NULL), (5), (NULL) AS tab(col);
+-----------------------+------------------+
| last_value(col, true) | last(col, true)  |
+-----------------------+------------------+
| 5                     | 5                |
+-----------------------+------------------+
```

4. Use WITHIN GROUP (ORDER BY ...) to specify order

```sql
SELECT a,
       last_value(b) WITHIN GROUP(ORDER BY c) as last_b,
       last_value(b, true) WITHIN GROUP(ORDER BY c) as last_non_null_b
FROM VALUES
  ('apple', 11, 22),
  ('apple', 1, 2),
  ('orange', NULL, 1),
  ('orange', 111, 2),
  ('orange', NULL, 3)
AS t(a, b, c)
GROUP BY a;
+--------+--------+-----------------+
| a      | last_b | last_non_null_b |
+--------+--------+-----------------+
| apple  | 11     | 11              |
| orange | NULL   | 111             |
+--------+--------+-----------------+
```

5. Use FILTER clause to conditionally retrieve the last value

```sql
SELECT last_value(col) FILTER (WHERE col < 15)
FROM VALUES (3), (10), (7), (12) AS tab(col);
+-------------------------------------------+
| last_value(col) FILTER (WHERE (col < 15)) |
+-------------------------------------------+
| 12                                        |
+-------------------------------------------+
```
