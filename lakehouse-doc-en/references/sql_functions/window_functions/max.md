### MAX 
```sql
max(expr) OVER ([partition_clause] [orderby_clause] [frame_clause])
```
####  Description

The MAX function is used to calculate and return the maximum value of a specified expression (expr) within a window range. This function is commonly used in data analysis and statistics to quickly obtain the maximum value of a certain group or overall data.

#### Parameter Description

* **expr**: The expression for which the maximum value needs to be calculated. It can be a numeric type, string type, time type, or other comparable types.

#### Return Result

The return type is the same as the type of the input expression.

####  Example

**Example 1: Simple Usage**
```sql
SELECT name, dep_no, salary, MAX(salary) OVER () AS max_salary FROM VALUES
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
|   name    | dep_no | salary | max_salary |
+-----------+--------+--------+------------+
| Eric      | 1      | 28000  | 35000      |
| Alex      | 1      | 32000  | 35000      |
| Felix     | 2      | 21000  | 35000      |
| Frank     | 1      | 30000  | 35000      |
| Tom       | 2      | 23000  | 35000      |
| Jane      | 3      | 29000  | 35000      |
| Jeff      | 3      | 35000  | 35000      |
| Paul      | 2      | 29000  | 35000      |
| Charles   | 2      | 23000  | 35000      |
| Charles F | 2      | 23000  | 35000      |
| null      | 4      | null   | 35000      |
| NotNull   | 4      | 23000  | 35000      |
+-----------+--------+--------+------------+
```
The above SQL statement will return the maximum salary of all employees in the employees table.

**Example 2: Group by Department**
```sql
SELECT dep_no, salary, MAX(salary) OVER (PARTITION BY dep_no) AS max_salary_by_department FROM VALUES
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
+--------+--------+--------------------------+
| dep_no | salary | max_salary_by_department |
+--------+--------+--------------------------+
| 3      | 29000  | 35000                    |
| 3      | 35000  | 35000                    |
| 1      | 28000  | 32000                    |
| 1      | 32000  | 32000                    |
| 1      | 30000  | 32000                    |
| 2      | 21000  | 29000                    |
| 2      | 23000  | 29000                    |
| 2      | 29000  | 29000                    |
| 2      | 23000  | 29000                    |
| 2      | 23000  | 29000                    |
| 4      | null   | 23000                    |
| 4      | 23000  | 23000                    |
+--------+--------+--------------------------+
```
This statement will return the highest salary of employees in each department.

**Example 3: Combining Sorting**
```sql
SELECT name, salary, MAX(salary) OVER (ORDER BY salary DESC) AS max_salary_after FROM VALUES
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
+-----------+--------+------------------+
|   name    | salary | max_salary_after |
+-----------+--------+------------------+
| Jeff      | 35000  | 35000            |
| Alex      | 32000  | 35000            |
| Frank     | 30000  | 35000            |
| Jane      | 29000  | 35000            |
| Paul      | 29000  | 35000            |
| Eric      | 28000  | 35000            |
| Tom       | 23000  | 35000            |
| Charles   | 23000  | 35000            |
| Charles F | 23000  | 35000            |
| NotNull   | 23000  | 35000            |
| Felix     | 21000  | 35000            |
| null      | null   | 35000            |
+-----------+--------+------------------+
```
In this example, we will sort employees in descending order by salary and get the maximum salary value after each employee.

**Example 4: Using Window Functions**

```sql
SELECT name, dep_no, salary,
 MAX(salary) OVER (PARTITION BY dep_no ORDER BY salary DESC ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS top_two_salary
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
|   name    | dep_no | salary | top_two_salary |
+-----------+--------+--------+----------------+
| Jeff      | 3      | 35000  | 35000          |
| Jane      | 3      | 29000  | 35000          |
| Alex      | 1      | 32000  | 32000          |
| Frank     | 1      | 30000  | 32000          |
| Eric      | 1      | 28000  | 30000          |
| Paul      | 2      | 29000  | 29000          |
| Tom       | 2      | 23000  | 29000          |
| Charles   | 2      | 23000  | 23000          |
| Charles F | 2      | 23000  | 23000          |
| Felix     | 2      | 21000  | 23000          |
| NotNull   | 4      | 23000  | 23000          |
| null      | 4      | null   | 23000          |
+-----------+--------+--------+----------------+
```
