## Description

The `PERCENTILE_APPROX` function calculates the approximate percentile of a numeric column. Compared to the exact `PERCENTILE` function, `PERCENTILE_APPROX` offers better performance on large datasets and is suitable for scenarios where high precision is not required.

## Syntax

```SQL
PERCENTILE_APPROX(value_expr, percentile)
```

## Parameters

* **value_expr**: The numeric column or expression for which to calculate the percentile. Supports numeric types.
* **percentile**: The desired percentile, either a `DOUBLE` constant in the range 0 to 1, or an array of percentiles (`ARRAY<DOUBLE>`). When an array is passed, the function returns multiple percentile results at once.

## Return Results

* When a single percentile is passed, returns a `DOUBLE` approximation.
* When an array is passed, returns an `ARRAY<DOUBLE>`, where each element corresponds to the percentile at the same position in the input array.
* `NULL` values are excluded from the calculation.

## Examples

1. Calculate a single percentile (50th percentile, i.e., median):

```SQL
SELECT percentile_approx(col, 0.5) FROM VALUES (0), (1), (2), (10) AS tab(col);
+-----------------------------+
| percentile_approx(col, 0.5) |
+-----------------------------+
| 1                         |
+-----------------------------+
```

2. Calculate multiple percentiles at once:

```SQL
SELECT percentile_approx(col, array(0.5, 0.4, 0.1)) AS res
FROM VALUES (0), (1), (2), (10) AS tab(col);
+---------------+
|      res      |
+---------------+
| [1,1.1,0] |
+---------------+
```

3. Calculate the median by group:

```SQL
SELECT c, percentile_approx(col, 0.5)
FROM VALUES ('a', 1), ('a', 2), ('a', 3), ('b', 10), ('b', 20), ('b', 30) AS tab(c, col)
GROUP BY c;
+---+-----------------------------+
| c | percentile_approx(col, 0.5) |
+---+-----------------------------+
| a | 2                         |
| b | 20                        |
+---+-----------------------------+
```

4. Calculate the 25th and 75th percentiles (quartiles):

```SQL
SELECT percentile_approx(col, array(0.25, 0.75))
FROM VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10) AS tab(col);
+------------------------------------------+
| percentile_approx(col, array(0.25, 0.75)) |
+------------------------------------------+
| [3, 8]                                   |
+------------------------------------------+
```
