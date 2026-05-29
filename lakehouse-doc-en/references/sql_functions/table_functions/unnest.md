## Description
`UNNEST` is a function used to expand arrays or nested data structures. It is commonly used to convert array-type columns into multiple rows of data for row-level analysis.

## **Syntax**
```sql
SELECT [column_name] FROM UNNEST(array_expression) [AS alias(column_name)];
SELECT [column_name] FROM table_name, UNNEST(array_column) [AS alias(column_name)]; -- Implicit JOIN
```
## **Parameters**
`array_expression`: The array or nested data structure to expand (such as multi-dimensional arrays, structs).
`alias(column_name)`: Optional, specifies an alias and column name for the expanded column.
`LEFT JOIN`: Optional, retains all rows from the left table even if the right table (`UNNEST` result) has no matching data.
## **Examples**
1. **Basic array expansion**
Expands a one-dimensional array into multiple rows, with each row corresponding to one element in the array.
**Example:**
```sql
-- Input: array(1,2,3)
SELECT * FROM UNNEST(array(1,2,3));
-- Output:
-- 1
-- 2
-- 3
```
 2. **Multi-array column expansion**
Supports expanding multiple arrays simultaneously, aligned by row. If array lengths are inconsistent, missing values are filled with `NULL`.
**Example:**
```sql
-- Input: array(1,2,3), array('ab','cd')
SELECT * FROM UNNEST(array(1,2,3), array('ab','cd'));
-- Output:
-- 1    ab
-- 2    cd
-- 3    NULL
```
3. **Nested array expansion**
Supports expanding multi-dimensional arrays (recursive expansion), producing flattened results.
**Example:**
```sql
-- Input: array(array(1,2,3), array(4,5,6))
SELECT * FROM UNNEST(array(array(1,2,3), array(4,5,6)));
-- Output:
-- 1
-- 2
-- 3
-- 4
-- 5
-- 6
```

4. **Combined use with JOIN**
Can be associated with other tables using `JOIN` or `CROSS JOIN` to expand array columns.
**Example:**
```sql
-- Input: Table t contains column k and array column a
WITH t AS (SELECT * FROM VALUES (1, array(1,2,3)), (2, array(4,5)) AS t(k, a))
SELECT * FROM t, UNNEST(a);
-- Output:
-- 1    [1,2,3]    1
-- 1    [1,2,3]    2
-- 1    [1,2,3]    3
-- 2    [4,5]      4
-- 2    [4,5]      5
```

 5. **Handling NULL and empty arrays**
- If the array is `NULL`, the expansion produces no results.
- If the array is empty (`[]`), the expansion also produces no results.
**Example:**
```sql
-- Input: Array column contains NULL or empty values
CREATE VIEW student_score AS
SELECT id, scores FROM VALUES
(1, [80,85,87]),
(2, [77, NULL, 89]),
(3, NULL),
(4, []) AS students(id, scores);

SELECT id, scores, score FROM student_score, UNNEST(scores) AS t(score);
-- Output:
-- 1    [80,85,87]    80
-- 1    [80,85,87]    85
-- 1    [80,85,87]    87
-- 2    [77,null,89]  77
-- 2    [77,null,89]  NULL
-- 2    [77,null,89]  89
```
6. **Filtering expanded results**
```sql
-- Keep only even elements
WITH t AS (SELECT * FROM VALUES (1, array(1,2,3)), (2, array(4,5)) AS t(k, a))
SELECT * FROM t LEFT JOIN UNNEST(a) u(e) WHERE u.e % 2 = 0;
-- Output:
-- 1    [1,2,3]    2
-- 2    [4,5]      4
```


## **Notes**
1. **Parameter type restrictions**
   `UNNEST` only accepts arrays or nested structures as input. Passing a non-array type will result in an error.
   ```sql
   -- Error example: Input is an integer
   SELECT * FROM UNNEST(1); -- Error: expect array type
   ```
