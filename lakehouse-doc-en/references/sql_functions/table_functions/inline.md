### INLINE
```sql
INLINE(expr)
```
####  Description

The INLINE function is used to expand the struct elements in an array into multiple rows of data. The input parameter `expr` is of type `array<struct<T1, T2, ... Tn>>`, and each column after expansion corresponds to a field in the struct element. If column names are not specified, the expanded column names will be the same as the struct field names. The INLINE function can be used directly or in conjunction with LATERAL VIEW for more complex data processing.

#### Parameter Description

* expr: The input array expression, of type `array<struct<T1, T2, ... Tn>>`

#### Return Result

* Return type: The type is inferred based on the input parameter `expr`, resulting in data of type `(T1, T2, ... Tn)`.

#### Usage Example

Example 1: Simple INLINE expansion
```sql
SELECT INLINE(array(struct(1, 'x'), struct(2, 'y')));
+------+------+
| col1 | col2 |
+------+------+
| 1    | x    |
| 2    | y    |
+------+------+
```
Example 2: Using with LATERAL VIEW
```sql
SELECT word, s1, s2 FROM VALUES ('hello') AS vt(word) LATERAL VIEW INLINE(array(struct('a', 0), struct('b', 1))) lv AS s1, s2;
+-------+----+----+
| word  | s1 | s2 |
+-------+----+----+
| hello | a  | 0  |
| hello | b  | 1  |
+-------+----+----+
```
#### Precautions

* When using the INLINE function, please ensure that the input array element type is a struct type.
* When used in conjunction with LATERAL VIEW, be sure to specify an alias for the expanded data for subsequent operations.