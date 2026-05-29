### MAX Function
```
max([distinct] expr)
```
#### Function Description
The MAX function is used to find the maximum value from a set of data. This function is applicable to various data types, including numeric, temporal, and string types.

#### Parameter Description
* `expr` (required): Comparable types, including numeric types (such as tinyint, smallint, int, bigint, float, double, decimal) and temporal types (such as date, timestamp) as well as string types (such as char, varchar, string, binary).

#### Return Results
* The return type is the same as the input parameter type.
* If the `distinct` keyword is set, the maximum value in the deduplicated set is calculated, but it does not affect the result.
* `null` values are not included in the calculation.

#### Usage Example
1. Find the maximum value of a numeric column:
```sql
SELECT max(col) FROM VALUES (10), (50), (20), (null) AS tab(col);
```
Results:
```
50
```
2. Find the maximum value of a time-type column:
```sql
SELECT max(col) FROM VALUES ('2021-01-01'), ('2021-12-31'), ('2021-06-15') AS tab(col);
```
Results:
```
2021-12-31
```
3. Find the maximum value of a string column:
```sql
SELECT max(col) FROM VALUES ('apple'), ('banana'), ('cherry') AS tab(col);
```
Results:
```
cherry
```
4. Use the `distinct` keyword to find the maximum value of a numeric column (no effect on the result):
```sql
SELECT max(distinct col) FROM VALUES (10), (50), (20), (null), (50) AS tab(col);
```
Results:
```
50
```
#### Precautions
* When using the MAX function, please ensure that the input parameter types are correct, otherwise it may cause the function to fail or return unexpected results.
* When you need to find the maximum value of multiple fields, you can call the MAX function multiple times, as shown below:
```sql
SELECT max(col1), max(col2) FROM VALUES (10, 'apple'), (20, 'banana'), (30, 'cherry') AS tab(col1, col2);
```
Results:
```
50, cherry
```