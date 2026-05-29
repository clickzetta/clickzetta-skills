### STDDEV\_SAMP Sample Standard Deviation Function
```
stddev_samp([distinct] expr)
```
#### Function Description
The `STDDEV_SAMP` function is used to calculate the sample standard deviation of a set of data, which measures the dispersion of values within the data set. The standard deviation is the square root of the variance and can reflect the fluctuation of the data. In statistics, the sample standard deviation is used to estimate the population standard deviation.

#### Parameter Description
- `expr`: Numeric type fields, including tinyint, smallint, int, bigint, float, double, and decimal types.
- `distinct` (optional): Indicates the calculation of the deduplicated set, default is false, meaning the calculation is performed on all data.

#### Return Result
- Returns a result of type double, representing the value of the sample standard deviation.
- If all input values are null, it returns null.

#### Usage Example

**Example 1: Basic Usage**
The following example calculates the sample standard deviation of a set of values.
```sql
SELECT stddev_samp(col) FROM VALUES (1), (2), (3), (3), (null) AS tab(col);
```
Results:
```
0.9574271077563381
```
**Example 2: Using the DISTINCT Keyword**
The following example calculates the sample standard deviation of a set of values after removing duplicates.
```sql
SELECT stddev_samp(DISTINCT col) FROM VALUES (1), (2), (3), (3), (null) AS tab(col);
```
Results:
```
1.0
```
**Example 3: Using with Other Functions**
The following example demonstrates how to use the `STDDEV_SAMP` function in conjunction with other functions, such as calculating the sample standard deviation of data within a certain range.
```sql
SELECT stddev_samp(col) FROM VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9) AS tab(col)
WHERE col BETWEEN 3 AND 7;
```
Results:
```
2.0615528128088302
```
**Example 4: Handling NULL Values**
The following example demonstrates how the `STDDEV_SAMP` function handles NULL values.
```sql
SELECT stddev_samp(NULLIF(col, 0)) FROM VALUES (1), (2), (null), (4), (null) AS tab(col);
```
Results:
```
1.3416407864998738
```
Through the above examples, you can see the application of the `STDDEV_SAMP` function in different scenarios. In actual use, you can adjust the parameters and conditions as needed to calculate the sample standard deviation that meets your requirements.