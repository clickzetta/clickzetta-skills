### APPROX_COUNT_DISTINCT Function
```sql
approx_count_distinct(expr)
```
#### Function Description
The `approx_count_distinct` function uses the hyperloglog algorithm to approximately calculate the number of distinct values in a column. When the cardinality is high, this function can quickly return an approximate result, but please note that the result will have some degree of error.

#### Parameter Description
* `expr`: The column for which the number of distinct values needs to be calculated. It can be of basic data types, including numeric types (integers, decimals), string types, time types, boolean types (true/false), decimal types, and binary types, etc.

#### Return Result
* The return value type is `bigint`, representing the approximately calculated number of distinct values.
* `null` values will not be counted.

#### Usage Example
1. Calculate the number of distinct values in a numeric type column:
```sql
SELECT approx_count_distinct(num_col) FROM VALUES (1), (1), (2), (2), (3), (null) AS t(num_col);
```
Results:
```
3
```
2. Calculate the number of distinct values in a string type column:
```sql
SELECT approx_count_distinct(str_col) FROM VALUES ('apple'), ('banana'), ('apple'), ('orange'), (null) AS t(str_col);
```
Results:
```
3
```
3. Calculate the number of different values in a Boolean type column:
```sql
SELECT approx_count_distinct(bool_col) FROM VALUES (true), (false), (true), (null) AS t(bool_col);
```
Results:
```
2
```
4. Calculate the number of different values in the time type column:
```sql
SELECT approx_count_distinct(time_col) FROM VALUES ('2021-01-01 10:00:00'), ('2021-01-01 11:00:00'), (null), ('2021-01-01 10:00:00') AS t(time_col);
```
Results:
```
2
```
#### Notes
* When the data volume is small, using the `approx_count_distinct` function may not be as efficient as directly calculating the accurate result. It is recommended to use this function when processing large amounts of data.
* Since the `approx_count_distinct` function uses an approximate algorithm, the result may have some errors. Please use it with caution in scenarios where high accuracy is required.