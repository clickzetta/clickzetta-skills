### COUNT 

#### Description

The COUNT function is used to calculate the number of data rows within a window. This function has two forms: `count(*)` and `count(expr1[,expr2...])`. `count(*)` calculates the number of all rows within the window, including rows containing NULL values; `count(expr1[,expr2...])` calculates the number of non-NULL expressions within the window.

#### Syntax
```sql
count(*) over ([partition_clause] [orderby_clause] [frame_clause])
count(expr1[,expr2...]) over ([partition_clause] [orderby_clause] [frame_clause])
```
#### Parameters

* `exprN`: Any type, used to calculate the number of non-NULL values.

#### Return Results

* The return value type is bigint.
* When using `count(*)`, NULL values are also counted as one row.
* When using `count(expr1[,expr2...])`, if any column has a NULL value, that row will be ignored.
#### Example
Example 1: Calculate the number of people in each department
```sql
SELECT dep_no,name, count(*) OVER (PARTITION BY dep_no)
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000)
AS tab(name, dep_no, salary);
+--------+---------+---------------------------------------+
| dep_no |  name   | `count`(*) OVER (PARTITION BY dep_no) |
+--------+---------+---------------------------------------+
| 3      | Jane    | 2                                     |
| 3      | Jeff    | 2                                     |
| 1      | Eric    | 3                                     |
| 1      | Alex    | 3                                     |
| 1      | Frank   | 3                                     |
| 2      | Felix   | 4                                     |
| 2      | Tom     | 4                                     |
| 2      | Paul    | 4                                     |
| 2      | Charles | 4                                     |
+--------+---------+---------------------------------------+
```
In this example, we group employees by department and count the number of people in each department.

Example 2: Calculate the cumulative number of people in each department sorted by salary in ascending order
```sql
SELECT dep_no,name, count(*) OVER (PARTITION BY dep_no ORDER BY salary)
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000)
AS tab(name, dep_no, salary);
+--------+---------+-----------------------------------------------------------+
| dep_no |  name   | `count`(*) OVER (PARTITION BY dep_no ORDER BY salary ASC) |
+--------+---------+-----------------------------------------------------------+
| 3      | Jane    | 1                                                         |
| 3      | Jeff    | 2                                                         |
| 1      | Eric    | 1                                                         |
| 1      | Frank   | 2                                                         |
| 1      | Alex    | 3                                                         |
| 2      | Felix   | 1                                                         |
| 2      | Tom     | 3                                                         |
| 2      | Charles | 3                                                         |
| 2      | Paul    | 4                                                         |
+--------+---------+-----------------------------------------------------------+
```
In this example, we group employees by department and sort them in ascending order by salary