### MAX 
```
max([distinct] expr)
```
####  Description

The MAX function is used to find the maximum value from a set of data. This function is applicable to various data types, including numeric, temporal, and string types.

#### Parameter Description

* `expr`: Comparable data types, supported types include:
  * Numeric types: tinyint, smallint, int, bigint, float, double, and decimal;
  * Temporal types: date and timestamp;
  * String types: char, varchar, string, and binary.
* `distinct`: Optional parameter, used to specify whether to remove duplicate values. If distinct is set, the maximum value from the deduplicated set is returned. Note that for numeric data, distinct does not affect the result.

#### Return Value

* The return type is the same as the input parameter `expr`.
* If the input parameter contains null values, these values will not be included in the calculation.
* Setting the distinct parameter does not affect the result for numeric data.

#### Usage Example

1. Find the maximum value of numeric data:
```sql
SELECT max(col) FROM VALUES (10), (50), (20), (null) AS tab(col);
+------------+
| `max`(col) |
+------------+
| 50         |
+------------+
```

1. Find the maximum value of time-based data:
```sql
SELECT max(col) FROM VALUES ('2023-01-01'), ('2022-12-31'), ('2023-02-01') AS tab(col);
+------------+
| `max`(col) |
+------------+
| 2023-02-01 |
+------------+
```
2. Find the maximum value of string type data:
```sql
SELECT max(col) FROM VALUES ('apple'), ('banana'), ('cherry') AS tab(col);
+------------+
| `max`(col) |
+------------+
| cherry     |
+------------+
```
3. Use the distinct parameter to find the maximum value of numeric data (no effect on the result):
```sql
SELECT max(distinct col) FROM VALUES (10), (50), (20), (null), (10) AS tab(col);
+---------------------+
| `max`(DISTINCT col) |
+---------------------+
| 50                  |
+---------------------+
```
4. Use the distinct parameter to find the maximum value of string data:
```sql
SELECT max(distinct col) FROM VALUES ('apple'), ('banana'), ('cherry'), ('apple') AS tab(col);
+---------------------+
| `max`(DISTINCT col) |
+---------------------+
| cherry              |
+---------------------+
```