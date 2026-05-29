# FIRST 
```
FIRST(expr[, ignoreNull]) OVER ([partition_clause] [orderby_clause] [frame_clause])
```
####  Description

When the sort keys are the same, the FIRST function is used to return the value of the first row within the specified window. When there are non-null values within the window, the first non-null value will be returned. If all values within the window are null and the ignoreNull parameter is set to true, the first null value will be returned. This function is non-deterministic.

#### Parameter Description

* **expr**: An expression of any type.
* **ignoreNull**: Optional parameter, boolean type, default value is false. When set to true, if all values within the window are null, the first null value will be returned.

#### Return Type

The return type is the same as the input expr type.

#### Usage Example

**Example 1: Basic Usage**
```sql

SELECT dep_no, salary, FIRST(salary,true) OVER (PARTITION BY dep_no) AS first_salary
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000),
  ('Charles F', 2, 23000),
  (null,4,null)
AS tab(name, dep_no, salary);
+--------+--------+--------------+
| dep_no | salary | first_salary |
+--------+--------+--------------+
| 3      | 29000  | 29000        |
| 3      | 35000  | 29000        |
| 1      | 28000  | 28000        |
| 1      | 32000  | 28000        |
| 1      | 30000  | 28000        |
| 2      | 21000  | 21000        |
| 2      | 23000  | 21000        |
| 2      | 29000  | 21000        |
| 2      | 23000  | 21000        |
| 2      | 23000  | 21000        |
| 4      | null   | null         |
+--------+--------+--------------+
```
**Example 2: Ignore null values**
```sql
SELECT dep_no, salary, FIRST(salary, true) OVER (PARTITION BY dep_no) AS first_non_null_salary
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000),
  ('Charles F', 2, 23000),
  (null,4,null)
AS tab(name, dep_no, salary);
+--------+--------+-----------------------+
| dep_no | salary | first_non_null_salary |
+--------+--------+-----------------------+
| 3      | 29000  | 29000                 |
| 3      | 35000  | 29000                 |
| 1      | 28000  | 28000                 |
| 1      | 32000  | 28000                 |
| 1      | 30000  | 28000                 |
| 2      | 21000  | 21000                 |
| 2      | 23000  | 21000                 |
| 2      | 29000  | 21000                 |
| 2      | 23000  | 21000                 |
| 2      | 23000  | 21000                 |
| 4      | null   | null                  |
+--------+--------+-----------------------+
```
**Example 3: Combining Sorting and Window Functions**
```sql
SELECT dep_no, salary, FIRST(salary, true) OVER (PARTITION BY dep_no ORDER BY salary DESC) AS highest_salary_in_department
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000),
  ('Charles F', 2, 23000),
  (null,4,null)
AS tab(name, dep_no, salary);
+--------+--------+------------------------------+
| dep_no | salary | highest_salary_in_department |
+--------+--------+------------------------------+
| 3      | 35000  | 35000                        |
| 3      | 29000  | 35000                        |
| 1      | 32000  | 32000                        |
| 1      | 30000  | 32000                        |
| 1      | 28000  | 32000                        |
| 2      | 29000  | 29000                        |
| 2      | 23000  | 29000                        |
| 2      | 23000  | 29000                        |
| 2      | 23000  | 29000                        |
| 2      | 21000  | 29000                        |
| 4      | null   | null                         |
+--------+--------+------------------------------+
```
**Example 4: Using the ROWS BETWEEN Clause**
```sql
SELECT dep_no, salary, FIRST(salary, true) OVER (PARTITION BY dep_no ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS highest_salary_in_department
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000),
  ('Charles F', 2, 23000),
  (null,4,null)
AS tab(name, dep_no, salary);
+--------+--------+------------------------------+
| dep_no | salary | highest_salary_in_department |
+--------+--------+------------------------------+
| 3      | 29000  | 29000                        |
| 3      | 35000  | 29000                        |
| 1      | 28000  | 28000                        |
| 1      | 30000  | 28000                        |
| 1      | 32000  | 28000                        |
| 2      | 21000  | 21000                        |
| 2      | 23000  | 21000                        |
| 2      | 23000  | 21000                        |
| 2      | 23000  | 21000                        |
| 2      | 29000  | 21000                        |
| 4      | null   | null                         |
+--------+--------+------------------------------+
```
