### MIN 
```
min([distinct] expr)
```
####  Description

The MIN function is used to find the minimum value from a set of data. This function supports various data types, including numeric types (such as tinyint, smallint, int, bigint, float, double, and decimal), time types (such as date and timestamp), string types (such as char, varchar, and string), and binary types.

#### Parameter Description

* `expr`: Comparable data types, including numeric types, time types, and string types.

#### Return Results

* The return value type is the same as the input parameter type.
* If the `distinct` keyword is set, the minimum value in the deduplicated set is calculated, but it has no effect on the result.
* `null` values are not included in the calculation.

#### Usage Example

1. Find the minimum value from a set of numbers:

```sql
SELECT min(col) FROM VALUES (10), (50), (20), (null) AS tab(col);
+------------+
| `min`(col) |
+------------+
| 10         |
+------------+
```
2. Find the minimum value from a set of time-type data:
```sql
SELECT min(col) FROM VALUES ('2023-01-01'), ('2022-12-31'), ('2023-02-01') AS tab(col);
+------------+
| `min`(col) |
+------------+
| 2022-12-31 |
+------------+
```
3. Find the minimum value from a set of string type data:
```sql
SELECT min(col) FROM VALUES ('apple'), ('banana'), ('cherry') AS tab(col);
+------------+
| `min`(col) |
+------------+
| apple      |
+------------+
```
4. Use the `distinct` keyword to find the minimum value from a set of numbers (no effect on the result):
```sql
SELECT min(distinct col) FROM VALUES (10), (50), (20), (null), (10), (20) AS tab(col);
+---------------------+
| `min`(DISTINCT col) |
+---------------------+
| 10                  |
+---------------------+
```
Through the above example, you can see the application of the MIN function in different data types. Please note that `null` values do not affect the calculation of the minimum value.