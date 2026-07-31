# SUM0

#### Introduction

`SUM0` sums a set of numeric values. Its only difference from `SUM` is that when all values in a group are `NULL`, `SUM0` returns `0` instead of `NULL`. This is useful when the outer query performs numeric calculations directly and you want to avoid handling `NULL` separately.

#### Syntax

```sql
SUM0([DISTINCT] expr) [FILTER (WHERE condition)]
```

#### Parameters

* `expr`: A numeric expression.

#### Return Value

* The return type matches the type of `expr` (integer or floating-point).
* `NULL` values are ignored during computation and treated as `0`.
* When all values in a group are `NULL` (or the group is empty), returns `0` instead of `NULL`.

#### Examples

1. Basic usage (with `NULL` values — `NULL` counts as 0):

```sql
SELECT SUM0(v) FROM (VALUES (1),(2),(NULL)) t(v);
+---------+
| sum0(v) |
+---------+
| 3       |
+---------+
```

2. Difference between `SUM` and `SUM0` when a group is all `NULL`:

```sql
SELECT SUM(v), SUM0(v) FROM (VALUES (NULL),(NULL)) t(v);
+--------+---------+
| sum(v) | sum0(v) |
+--------+---------+
| NULL   | 0       |
+--------+---------+
```

3. Combined with GROUP BY — `SUM0` returns 0 for a group that is entirely `NULL`:

```sql
SELECT
    category,
    SUM(amount)  AS total_sum,
    SUM0(amount) AS total_sum0
FROM (VALUES
    ('A', 10),
    ('A', NULL),
    ('B', NULL),
    ('B', NULL)
) t(category, amount)
GROUP BY category;
+----------+-----------+------------+
| category | total_sum | total_sum0 |
+----------+-----------+------------+
| A        | 10        | 10         |
| B        | NULL      | 0          |
+----------+-----------+------------+
```

4. Use DISTINCT to sum deduplicated values:

```sql
SELECT SUM0(DISTINCT v) FROM (VALUES (2),(2),(3),(NULL)) t(v);
+------------------+
| sum0(DISTINCT v) |
+------------------+
| 5                |
+------------------+
```

5. Use a FILTER clause for conditional summation:

```sql
SELECT SUM0(v) FILTER (WHERE v > 1) FROM (VALUES (1),(2),(3),(NULL)) t(v);
+------------------------------------+
| sum0(v) FILTER (WHERE (v > 1))     |
+------------------------------------+
| 5                                  |
+------------------------------------+
```
