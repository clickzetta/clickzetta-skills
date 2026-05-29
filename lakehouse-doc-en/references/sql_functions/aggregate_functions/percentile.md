### PERCENTILE
```sql
percentile([distinct] col, percentage[, frequency])
```
####  Description

The percentile function `PERCENTILE` is used to calculate the percentile of numerical data in a specified column. When the data is sorted in ascending order, this function returns the value at the specified percentage position.

#### Parameter Description

* `col`: The column for which the percentile is to be calculated. The data type should be numerical, including tinyint, smallint, int, bigint, float, double, and decimal.
* `percentage`: The percentile to be calculated, with a data type of double constant. The value range should be between 0.0 and 1.0.
* `frequency` (optional): Indicates the number of times each data row is counted in the calculation. The data type should be a positive integer.

#### Return Result

This function returns a double type value representing the calculated percentile.

If the `distinct` keyword is used in the function, it indicates the calculation of the percentile for the deduplicated set. Note that `null` values are not included in the calculation.

#### Usage Example

The following is an example of using the `PERCENTILE` function:

1. Calculate the 30th percentile of a non-deduplicated dataset:
```sql
SELECT percentile(col, 0.3) FROM VALUES (0), (10), (10), (null) AS tab(col);
+------------------------+
| percentile(col, 0.3BD) |
+------------------------+
| 6.0                    |
+------------------------+
```
2. Calculate the 30th percentile of the deduplicated dataset:
```sql
SELECT percentile(DISTINCT col, 0.3) FROM VALUES (0), (10), (10), (null) AS tab(col);
+---------------------------------+
| percentile(DISTINCT col, 0.3BD) |
+---------------------------------+
| 3.0                             |
+---------------------------------+
```
3. Calculate the 30th percentile of each data row being counted twice in the dataset:
```sql
SELECT percentile(col, 0.3, freq) FROM VALUES (0, 1), (10, 2) AS tab(col, freq);
+------------------------------+
| percentile(col, 0.3BD, freq) |
+------------------------------+
| 6.0                          |
+------------------------------+
```