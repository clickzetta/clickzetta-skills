### MEDIAN Function

```
median(expr)
```

#### Description

The `MEDIAN` function computes the median of a numeric column. The median is the middle value when the data is sorted in order. This function is equivalent to `percentile(expr, 0.5)`, i.e., computing the 50th percentile.

#### Parameters

* `expr`: A numeric expression, which can be of integer, floating-point, or `DECIMAL` type.

#### Return Type

* Returns a `DOUBLE` value.
* Returns the median of the dataset.

#### Notes

* If the input is an empty set, returns `NULL`.
* For an even number of values, returns the average of the two middle values.
* For an odd number of values, returns the exact middle value.
* `NULL` values are automatically ignored and excluded from computation.
* `MEDIAN` does not support the `FILTER` clause. For conditional filtering, use a `WHERE` clause at the outer level or switch to `percentile(expr, 0.5) FILTER (...)`.

#### Examples

1. Basic usage: compute the median

```sql
SELECT median(col) FROM VALUES (0), (10) AS tab(col);
+--------------+
| median(col)  |
+--------------+
| 5.0          |
+--------------+
```

2. Median of an even number of values (average of the two middle values)

```sql
SELECT median(value) FROM VALUES (1), (2), (3), (4) AS t(value);
+----------------+
| median(value)  |
+----------------+
| 2.5            |
+----------------+
```

3. Median of an odd number of values

```sql
SELECT median(value) FROM VALUES (1), (2), (3), (4), (5) AS t(value);
+----------------+
| median(value)  |
+----------------+
| 3.0            |
+----------------+
```

4. Compute the median by group

```sql
SELECT c, median(col)
FROM VALUES ('a', 1), ('a', 2), ('a', 3), ('b', 10), ('b', 20), ('b', 30) AS tab(c, col)
GROUP BY c;
+---+-------------+
| c | median(col) |
+---+-------------+
| a | 2.0         |
| b | 20.0        |
+---+-------------+
```
