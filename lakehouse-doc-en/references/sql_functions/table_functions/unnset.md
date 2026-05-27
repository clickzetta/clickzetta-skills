## Description
`UNNEST` is a function used to expand arrays or nested data structures, commonly used to convert array-type columns into multiple rows of data for row-level analysis.

## **Syntax**
```sql
SELECT [column_name] FROM UNNEST(array_expression) [AS alias(column_name)];
SELECT [column_name] FROM table_name, UNNEST(array_column) [AS alias(column_name)]; -- Implicit JOIN
```
## **Parameter Description**
`Array Expression`  : The array or nested data structure (such as multidimensional arrays, structs) that needs to be expanded.
`Alias (Column Name)`: Optional, specify an alias and column name for the expanded columns.
`LEFT JOIN` : Optional, retain all rows of the left table even if there is no matching data in the right table (UNNEST result).
## ** Example**
1. **Basic Array Expansion**
Expand a one-dimensional array into multiple rows, with each row corresponding to an element in the array.
**Example:**
```sql
-- Input: array(1,2,3)
SELECT * FROM UNNEST(array(1,2,3)); 
-- Output:
-- 1
-- 2
-- 3
```
2. **Multiple Array Expansion**
Supports expanding multiple arrays simultaneously, aligned by rows. If the array lengths are inconsistent, missing values are filled with `NULL`.  
**Example:**
```sql
-- Input: array(1,2,3), array('ab','cd')
SELECT * FROM UNNEST(array(1,2,3), array('ab','cd'));
-- Output:
-- 1    ab
-- 2    cd
-- 3    NULL
```
3. **Nested Array Expansion**
Supports expanding multidimensional arrays (recursive expansion) to generate flattened results.  
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
4. **Using with JOIN**
Can be associated with other tables through `JOIN` or `CROSS JOIN` to expand array columns.  
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
5. **Handling NULL and Empty Arrays**
- If the array is `NULL`, there will be no result after expansion.  
- If the array is empty (`[]`), there will also be no result after expansion.  
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
6. ：**Filter Expansion Results**
```sql
-- Only keep even elements
WITH t AS (SELECT * FROM VALUES (1, array(1,2,3)), (2, array(4,5)) AS t(k, a))
SELECT * FROM t LEFT JOIN UNNEST(a) u(e) WHERE u.e % 2 = 0;
-- Output:
-- 1    [1,2,3]    2
-- 2    [4,5]      4
```
## **Precautions**
1. **Parameter Type Restrictions**  
   `UNNEST` only accepts arrays or nested structures as input, passing non-array types will result in an error.
```sql
-- Error example: input is an integer
SELECT * FROM UNNEST(1); -- Error: expect array type
```