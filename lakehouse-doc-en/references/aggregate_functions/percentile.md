### PERCENTILE Percentile Function
```sql
PERCENTILE([DISTINCT] col, percentage[, frequency])
```
#### Function Description
The percentile function `PERCENTILE` is used to calculate the percentile of numerical data in a specified column. Given a percentage value, this function will return the value corresponding to that percentage position after the dataset is sorted in ascending order.

#### Parameter Description
- `col`: The numeric column for which the percentile is to be calculated. It can be of type `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, or `DECIMAL`.
- `percentage`: The percentile to be calculated, which should be a constant of type `DOUBLE`, with a value range within `[0.0, 1.0]`.
- `frequency` (optional): The weight of each data row in the calculation, which is a positive integer. By default, the weight of each data row is 1.

#### Return Result
The function returns a value of type `DOUBLE`. If the `DISTINCT` keyword is specified, the calculation is based on the deduplicated dataset. `NULL` values are not included in the calculation.

#### Usage Example

**Example 1: Calculating Basic Percentile**

<Notes>
```sql
SELECT PERCENTILE(col, 0.3) FROM VALUES (0), (10), (20), (null) AS tab(col);
```
Results:
```
6.5
```
**Example 2: Calculate Weighted Percentile**
```sql
SELECT PERCENTILE(col, 0.3, freq) FROM VALUES (0, 1), (10, 2), (20, 3) AS tab(col, freq);
```
Results:
```
7.333...
```
**Example 3: Calculate the Percentile after Deduplication**
```sql
SELECT PERCENTILE(DISTINCT col, 0.3) FROM VALUES (0), (10), (10), (null) AS tab(col);
```
Results:
```
3.0
```
#### Notes
- Ensure the value of the `percentage` parameter is within the valid range, otherwise it may lead to inaccurate calculation results.
- When `percentage` is 0, the function returns the minimum value in the dataset; when `percentage` is 1, it returns the maximum value.
- When using the `DISTINCT` keyword, ensure you understand the impact of deduplication on the results.
- When using the `frequency` parameter, ensure its value is a positive integer, otherwise it may lead to inaccurate calculation results or function execution failure.