### MIN 
```sql
MIN(expr) OVER ([PARTITION BY clause] [ORDER BY clause] [FRAME clause])
```
####  Description

The MIN function is used to calculate and return the minimum value of a specified expression (expr) within a window. This function is commonly used in data analysis and processing to quickly obtain the minimum data within a specific group.

#### Parameter Description

* `expr`: The expression for which the minimum value needs to be calculated. It can be a comparable type such as numeric, string, or time.

#### Return Result

* The return type is the same as the type of the input `expr` parameter.

####  Example

**Example 1: Simple Usage**
```sql

SELECT name, dep_no, salary, MIN(salary) OVER (PARTITION BY dep_no) AS min_salary
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
+-----------+--------+--------+------------+
|   name    | dep_no | salary | min_salary |
+-----------+--------+--------+------------+
| Jane      | 3      | 29000  | 29000      |
| Jeff      | 3      | 35000  | 29000      |
| Eric      | 1      | 28000  | 28000      |
| Alex      | 1      | 32000  | 28000      |
| Frank     | 1      | 30000  | 28000      |
| Felix     | 2      | 21000  | 21000      |
| Tom       | 2      | 23000  | 21000      |
| Paul      | 2      | 29000  | 21000      |
| Charles   | 2      | 23000  | 21000      |
| Charles F | 2      | 23000  | 21000      |
| null      | 4      | null   | 23000      |
| NotNull   | 4      | 23000  | 23000      |
+-----------+--------+--------+------------+
```
The above SQL query will return the employee name, department number, salary, and the minimum salary of each department.

**Example 2: Combining with ORDER BY Clause**
```sql
SELECT name, dep_no, salary, MIN(salary) OVER (PARTITION BY dep_no ORDER BY salary) AS min_salary
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
+-----------+--------+--------+------------+
|   name    | dep_no | salary | min_salary |
+-----------+--------+--------+------------+
| Jane      | 3      | 29000  | 29000      |
| Jeff      | 3      | 35000  | 29000      |
| Eric      | 1      | 28000  | 28000      |
| Frank     | 1      | 30000  | 28000      |
| Alex      | 1      | 32000  | 28000      |
| Felix     | 2      | 21000  | 21000      |
| Tom       | 2      | 23000  | 21000      |
| Charles   | 2      | 23000  | 21000      |
| Charles F | 2      | 23000  | 21000      |
| Paul      | 2      | 29000  | 21000      |
| null      | 4      | null   | null       |
| NotNull   | 4      | 23000  | 23000      |
+-----------+--------+--------+------------+
```
This example will sort by the salary of each department and return the minimum salary for each department.

**Example 3: Using window functions to calculate cumulative minimum values**
```sql
SELECT name, dep_no, salary,
       MIN(salary) OVER (PARTITION BY dep_no ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_min_salary
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
+-----------+--------+--------+----------------+
|   name    | dep_no | salary | cum_min_salary |
+-----------+--------+--------+----------------+
| Jane      | 3      | 29000  | 29000          |
| Jeff      | 3      | 35000  | 29000          |
| Eric      | 1      | 28000  | 28000          |
| Frank     | 1      | 30000  | 28000          |
| Alex      | 1      | 32000  | 28000          |
| Felix     | 2      | 21000  | 21000          |
| Tom       | 2      | 23000  | 21000          |
| Charles   | 2      | 23000  | 21000          |
| Charles F | 2      | 23000  | 21000          |
| Paul      | 2      | 29000  | 21000          |
| null      | 4      | null   | null           |
| NotNull   | 4      | 23000  | 23000          |
+-----------+--------+--------+----------------+
```
In this example, we will calculate the cumulative minimum salary for each department, which is the minimum salary from each employee up to the current employee.

^
^