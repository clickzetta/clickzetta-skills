### BIT_XOR 
```sql
bit_xor([distinct] expr)
```
####  Description

The BIT\_XOR function is used to calculate the bitwise XOR result of a set of integer data. Bitwise XOR operation compares the corresponding bits of two binary numbers; if the two bits are the same, the result is 0, and if they are different, the result is 1.

#### Parameter Description

* expr: Integer type expression, which can be of type tinyint, smallint, int, or bigint.
* distinct (optional): When using the distinct keyword, the function will calculate the bitwise XOR result of the deduplicated set.

#### Return Result

* The return value type is consistent with the parameter type.
* If the parameters contain null values, the null values do not participate in the calculation.

#### Usage Example

1. Calculate the bitwise XOR result of a set of integers:

<Notes>
</Notes>

#### Permalink
```sql
SELECT bit_xor(col) FROM VALUES (3), (5), (7) AS tab(col);
+--------------+
| bit_xor(col) |
+--------------+
| 1            |
+--------------+
```
2. Calculate the bitwise XOR result of the deduplicated integer set:
```sql
SELECT bit_xor(DISTINCT col) FROM VALUES (3), (3), (5), (7), (null) AS tab(col);
+-----------------------+
| bit_xor(DISTINCT col) |
+-----------------------+
| 1                     |
+-----------------------+
```
3. Calculate the bitwise XOR result in the actual data table:
```sql
CREATE TABLE example_table (id INT);
INSERT INTO example_table VALUES (3), (5), (7);
SELECT bit_xor(id) FROM example_table;
+-------------+
| bit_xor(id) |
+-------------+
| 1           |
+-------------+
```
4. Calculate the bitwise XOR result of an integer set containing null values:
```sql
INSERT INTO example_table VALUES (null), (8);
SELECT bit_xor(id) FROM example_table;
+-------------+
| bit_xor(id) |
+-------------+
| 9           |
+-------------+
```