### SUM 
```sql
sum(expr) OVER ([partition_clause] [orderby_clause] [frame_clause])
```
####  Description

The SUM function is used to calculate the sum of the specified expression (expr) within a window. This function can sum data by groups or calculate cumulative sums according to specified sorting rules.

#### Parameter Description

* expr: The numeric expression to be summed, which can be of type tinyint, smallint, int, bigint, float, double, or decimal.

#### Return Type

* When expr is of type decimal, the return type is decimal, and the precision may increase accordingly.
* When expr is of integer type, the return type is bigint.
* In other cases, the return type is double.

#### Notes

* During the function calculation, null values will be ignored.

#### Usage Example

**Example 1: Sum by department group**
```sql
SELECT dep_no, salary, sum(salary) OVER (PARTITION BY dep_no) AS total_salary
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
  ('null',4,null),
  ('NotNull',4,23000)
  AS tab(name, dep_no, salary);
+--------+--------+--------------+
| dep_no | salary | total_salary |
+--------+--------+--------------+
| 3      | 29000  | 64000        |
| 3      | 35000  | 64000        |
| 1      | 28000  | 90000        |
| 1      | 32000  | 90000        |
| 1      | 30000  | 90000        |
| 2      | 21000  | 119000       |
| 2      | 23000  | 119000       |
| 2      | 29000  | 119000       |
| 2      | 23000  | 119000       |
| 2      | 23000  | 119000       |
| 4      | null   | 23000        |
| 4      | 23000  | 23000        |
+--------+--------+--------------+
```
The above SQL query will return the total salary of employees in each department.

**Example 2: Combining Sorting and Grouping for Sum**
```sql
SELECT dep_no, salary, sum(salary) OVER (PARTITION BY dep_no ORDER BY salary DESC) AS rank_by_salary
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
  ('null',4,null),
  ('NotNull',4,23000)
  AS tab(name, dep_no, salary);
+--------+--------+----------------+
| dep_no | salary | rank_by_salary |
+--------+--------+----------------+
| 3      | 35000  | 35000          |
| 3      | 29000  | 64000          |
| 1      | 32000  | 32000          |
| 1      | 30000  | 62000          |
| 1      | 28000  | 90000          |
| 2      | 29000  | 29000          |
| 2      | 23000  | 98000          |
| 2      | 23000  | 98000          |
| 2      | 23000  | 98000          |
| 2      | 21000  | 119000         |
| 4      | 23000  | 23000          |
| 4      | null   | 23000          |
+--------+--------+----------------+
```
This query will sort the employees' salaries in each department in descending order and calculate the cumulative salary ranking for each employee within their department.

#### Summary

The SUM function is a very useful aggregate function in SQL, which can be flexibly applied to various data analysis scenarios, such as calculating group totals, cumulative sums, etc. By combining the features of window functions, its application scope can be further expanded, providing powerful data computation capabilities for data analysts and database developers.