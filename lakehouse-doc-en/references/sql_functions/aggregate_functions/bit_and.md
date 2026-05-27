### BIT\_AND 
```sql
bit_and([distinct] expr)
```
####  Description

The BIT\_AND function is used to calculate the bitwise AND result of a specified expression within a set of data. This function operates on integer types of data, including tinyint, smallint, int, and bigint types. By using the BIT\_AND function, you can perform bitwise operations on data to achieve precise control and processing of the data.

#### Parameter Description

* expr (required): An integer type expression, including tinyint, smallint, int, and bigint types.
* distinct (optional): When set to distinct, the function will calculate the bitwise AND result of the deduplicated set.

#### Return Result

* The return value type is consistent with the parameter type.
* If distinct is set, the bitwise AND result of the deduplicated set is returned.
* Null values are not included in the calculation.

#### Usage Example

1. Calculate the bitwise AND result of a set of data (distinct not set):
```sql
SELECT bit_and(col) FROM VALUES (3), (5), (7) AS tab(col);
+--------------+
| bit_and(col) |
+--------------+
| 1            |
+--------------+
```
2. Calculate the bitwise AND result of a set of data (set distinct and include duplicates):
```sql
SELECT bit_and(DISTINCT col) FROM VALUES (3), (3), (5), (7), (null) AS tab(col);
+-----------------------+
| bit_and(DISTINCT col) |
+-----------------------+
| 1                     |
+-----------------------+
```

3. Calculate the bitwise AND result of a set of data (including null values):

```sql
SELECT bit_and(col) FROM VALUES (3), (null), (5), (7) AS tab(col);
+--------------+
| bit_and(col) |
+--------------+
| 1            |
+--------------+
```
4. Calculate the bitwise AND result of different integer types:
```sql
SELECT bit_and(tinyint_col)col1, bit_and(smallint_col)col2, bit_and(int_col)col3, bit_and(bigint_col) col4
FROM VALUES (11, 22, 33, 44) AS t(tinyint_col, smallint_col, int_col, bigint_col);
+------+------+------+------+
| col1 | col2 | col3 | col4 |
+------+------+------+------+
| 11   | 22   | 33   | 44   |
+------+------+------+------+
```