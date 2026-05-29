### APPROX\_PERCENTILE

#### Description

The `APPROX_PERCENTILE` function is used to calculate and return the approximate percentile of values in a specified column. This function accepts two parameters: the first parameter is the name of the column for which the percentile is to be calculated, and the second parameter is a floating-point number representing the desired percentile. When the data is sorted in ascending order, this function returns the value corresponding to the specified percentage.

#### Parameter Description

1. `col`: The name of the column for which the percentile is to be calculated. This column should contain numeric data types such as tinyint, smallint, int, bigint, float, double, or decimal.
2. `percentage`: A constant of type double representing the desired percentile. This value should be in the range \[0.0, 1.0].

#### Return Result

The function returns a value of type double. If the `DISTINCT` keyword is specified, the calculation will be based on the deduplicated dataset. Note that null values will not be included in the calculation.

#### Usage Example

1. Calculate the median (50th percentile) in a dataset:
```sql
SELECT approx_percentile(col, 0.5) FROM VALUES (0), (6), (6), (7), (9), (10) AS tab(col);
+-------------------------------+
| approx_percentile(col, 0.5BD) |
+-------------------------------+
| 6.25                          |
+-------------------------------+
```
2. Calculate the median (50th percentile) of the deduplicated dataset:
```sql
SELECT approx_percentile(DISTINCT col, 0.5) FROM VALUES (0), (6), (6), (7), (9), (10) AS tab(col);
+----------------------------------------+
| approx_percentile(DISTINCT col, 0.5BD) |
+----------------------------------------+
| 7.0                                    |
+----------------------------------------+
```
3. Calculate the 25th percentile of the dataset:
```sql
SELECT approx_percentile(col, 0.25) FROM VALUES (0), (6), (6), (7), (9), (10) AS tab(col);
+--------------------------------+
| approx_percentile(col, 0.25BD) |
+--------------------------------+
| 6.0                            |
+--------------------------------+
```
4. Calculate the 75th percentile of the dataset:
```sql
SELECT approx_percentile(col, 0.75) FROM VALUES (0), (6), (6), (7), (9), (10) AS tab(col);
+--------------------------------+
| approx_percentile(col, 0.75BD) |
+--------------------------------+
| 9.0                            |
+--------------------------------+
```
### Summary

The `APPROX_PERCENTILE` function provides users with a quick way to calculate approximate percentiles of a dataset. By adjusting the `percentage` parameter, users can easily obtain values for different percentiles, thereby better analyzing and understanding the data. When using this function, please ensure that the data types match and that the `percentage` parameter value is within the valid range.