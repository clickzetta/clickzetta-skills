### MIN Function
```
min([distinct] expr)
```
#### Function Description
The MIN function is used to find and return the minimum value from a set of data. This function supports multiple data types as input, including numeric types and time types.

#### Parameter Description
* `expr`: Comparable data types, including numeric types (such as tinyint, smallint, int, bigint, float, double, and decimal) as well as time types (such as date and timestamp) and string types (such as char, varchar, and string) and binary.

#### Return Results
* The return value type is the same as the input parameter type.
* If the `distinct` keyword is set, it indicates calculating the minimum value from the deduplicated set, but it has no effect on the result.
* `null` values do not participate in the calculation of the minimum value.

#### Usage Example
1. Get the minimum value from numeric types:
```sql
SELECT min(col) FROM VALUES (10), (50), (20), (null) AS tab(col);
```
Results:
```
10
```
2. Get the minimum value from the time type:
```sql
SELECT min(col) FROM VALUES ('2023-01-01'), ('2022-12-31'), ('2023-02-01') AS tab(col);
```
Results:
```
2022-12-31
```
3. Get the minimum value from a string type:
```sql
SELECT min(col) FROM VALUES ('apple'), ('banana'), ('cherry') AS tab(col);
```
Results:
```
apple
```
4. Using the `distinct` keyword to get the minimum value:
```sql
SELECT min(distinct col) FROM VALUES (10), (50), (20), (10), (null) AS tab(col);
```
Results:
```
10
```
#### Notes
* When all input values are `null`, the MIN function returns `null`.
* The `distinct` keyword has no effect on the result in this scenario because the MIN function itself does not calculate the same value multiple times.