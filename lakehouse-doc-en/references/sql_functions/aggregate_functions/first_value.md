### FIRST_VALUE Function

```
first_value(expr [, ignoreNulls]) [FILTER (WHERE condition)]
first(expr [, ignoreNulls]) [FILTER (WHERE condition)]
```

#### Description

The `FIRST_VALUE` function returns the first value in an aggregation group or window. You can optionally choose whether to ignore `NULL` values. `first` is an alias for `first_value`.

#### Parameters

* `expr`: An expression of any type whose first value is to be retrieved.
* `ignoreNulls`: An optional boolean parameter, defaulting to `false`.
  * `false` (default): returns the first value, even if it is `NULL`
  * `true`: ignores `NULL` values, returns the first non-`NULL` value

#### Return Type

* Returns the same data type as the input expression.
* Returns the first value in the aggregation group or window.

#### Notes

* If all values are `NULL` (and `ignoreNulls` is `true`), returns `NULL`.
* If the input is an empty set, returns `NULL`.
* The order of values depends on the input order of the data (non-deterministic). Use `WITHIN GROUP (ORDER BY ...)` to specify a deterministic order.

#### Examples

1. Basic usage: return the first value

```sql
SELECT first_value(col), first(col)
FROM VALUES (10), (5), (20) AS tab(col);
+------------------+------------+
| first_value(col) | first(col) |
+------------------+------------+
| 10               | 10         |
+------------------+------------+
```

2. Handling NULL values (default: returns the first value, even if NULL)

```sql
SELECT first_value(col), first(col)
FROM VALUES (NULL), (5), (NULL) AS tab(col);
+------------------+------------+
| first_value(col) | first(col) |
+------------------+------------+
| NULL             | NULL       |
+------------------+------------+
```

3. Ignore NULL values, return the first non-NULL value

```sql
SELECT first_value(col, true), first(col, true)
FROM VALUES (NULL), (5), (NULL) AS tab(col);
+------------------------+-------------------+
| first_value(col, true) | first(col, true)  |
+------------------------+-------------------+
| 5                      | 5                 |
+------------------------+-------------------+
```

4. Use WITHIN GROUP (ORDER BY ...) to specify order

```sql
SELECT a,
       first_value(b) WITHIN GROUP(ORDER BY c) as first_b,
       first_value(b, true) WITHIN GROUP(ORDER BY c) as first_non_null_b
FROM VALUES
  ('apple', 11, 22),
  ('apple', 1, 2),
  ('orange', NULL, 1),
  ('orange', 111, 2),
  ('orange', NULL, 3)
AS t(a, b, c)
GROUP BY a;
+--------+---------+------------------+
| a      | first_b | first_non_null_b |
+--------+---------+------------------+
| apple  | 1       | 1                |
| orange | NULL    | 111              |
+--------+---------+------------------+
```

5. Get the first and last value for each group

```sql
SELECT
  category,
  first_value(value) as first_val,
  last_value(value) as last_val
FROM VALUES
  ('A', 10),
  ('A', 20),
  ('B', 30),
  ('B', 40)
AS t(category, value)
GROUP BY category;
+----------+-----------+----------+
| category | first_val | last_val |
+----------+-----------+----------+
| A        | 10        | 20       |
| B        | 30        | 40       |
+----------+-----------+----------+
```

6. Use FILTER clause to conditionally retrieve the first value

```sql
SELECT first_value(col) FILTER (WHERE col > 5)
FROM VALUES (3), (10), (7), (12) AS tab(col);
+-------------------------------------------+
| first_value(col) FILTER (WHERE (col > 5)) |
+-------------------------------------------+
| 10                                        |
+-------------------------------------------+
```
