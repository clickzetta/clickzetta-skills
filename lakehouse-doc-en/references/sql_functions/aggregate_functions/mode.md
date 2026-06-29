# MODE

#### Introduction

The `MODE` function returns the most frequently occurring value (the mode) in a set of data. When multiple values share the same highest frequency, the result is nondeterministic.

#### Syntax

```sql
MODE(expr) [FILTER (WHERE condition)]
```

#### Parameters

* `expr`: An expression of any comparable type.

#### Return Value

* The return type matches the type of `expr`.
* `NULL` values are ignored and do not participate in frequency counting.
* If all values are `NULL`, returns `NULL`.
* When multiple values share the same highest frequency, the result is nondeterministic. Do not rely on a specific return value in examples or business logic.

#### Examples

1. Basic usage — return the most frequently occurring value:

```sql
SELECT MODE(v) FROM (VALUES (1),(2),(2),(3)) t(v);
+---------+
| mode(v) |
+---------+
| 2       |
+---------+
```

2. Combined with GROUP BY to compute the mode per group:

```sql
SELECT dept, MODE(score)
FROM (VALUES ('A', 90), ('A', 90), ('A', 80), ('B', 70), ('B', 70), ('B', 90)) t(dept, score)
GROUP BY dept;
+------+-------------+
| dept | mode(score) |
+------+-------------+
| A    | 90          |
| B    | 70          |
+------+-------------+
```

3. Tie case — nondeterministic result when multiple values share the same frequency:

```sql
-- 1 and 2 each appear twice; which value is returned is nondeterministic
SELECT MODE(v) FROM (VALUES (1),(1),(2),(2)) t(v);
+---------+
| mode(v) |
+---------+
| 1       |
+---------+
```

> ⚠️ **Note**: In a tie, the actual return value may vary with data distribution or execution plan. Do not rely on a specific value in business logic.

4. Use a FILTER clause for conditional mode computation:

```sql
SELECT MODE(v) FILTER (WHERE v > 1) FROM (VALUES (1),(2),(2),(3)) t(v);
+----------------------------------+
| mode(v) FILTER (WHERE (v > 1))   |
+----------------------------------+
| 2                                |
+----------------------------------+
```
