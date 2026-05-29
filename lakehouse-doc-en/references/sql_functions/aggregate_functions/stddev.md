# STDDEV

## Description

The `STDDEV` function computes the sample standard deviation of a set of numeric values. It is a commonly used aggregate function in statistics for measuring data dispersion. This function is a synonym of the `STD` aggregate function, and returns a `DOUBLE` value.

## Syntax

```sql
STDDEV(expr) [FILTER (WHERE condition)]
```

## Parameters

* `expr`: An expression that evaluates to a numeric value. The expression can be a column name, a calculation formula, or any other expression that returns a numeric value.

## Return Value

* Returns a `DOUBLE` value representing the sample standard deviation.
* If `DISTINCT` is specified, the function computes the standard deviation on unique values of `expr` only.
* If the aggregation group contains only one row, the function returns `NULL`.

## Examples

Example 1: Compute the standard deviation of all values

```sql
SELECT STDDEV(col) FROM VALUES (1), (2), (3), (3) AS tab(col);
+--------------------+
|    STDDEV(col)     |
+--------------------+
| 0.9574271077563381 |
+--------------------+
```

Example 2: Compute the standard deviation of unique values

```sql
SELECT STDDEV(DISTINCT col) FROM VALUES (1), (2), (3), (3) AS tab(col);
+----------------------+
| STDDEV(DISTINCT col) |
+----------------------+
| 1.0                  |
+----------------------+
```

Example 3: Use FILTER clause to conditionally compute standard deviation

```sql
SELECT STDDEV(col) FILTER (WHERE col > 1) FROM VALUES (1), (2), (3), (4) AS tab(col);
+----------------------------------------+
| STDDEV(col) FILTER (WHERE (col > 1))   |
+----------------------------------------+
| 1.0                                    |
+----------------------------------------+
```

Example 4: Combine FILTER clause and DISTINCT to compute conditional standard deviation

```sql
SELECT STDDEV(DISTINCT col) FILTER (WHERE col <= 3) FROM VALUES (1), (2), (3), (3), (4) AS tab(col);
+-------------------------------------------------------+
| STDDEV(DISTINCT col) FILTER (WHERE (col <= 3))        |
+-------------------------------------------------------+
| 1.0                                                   |
+-------------------------------------------------------+
```
