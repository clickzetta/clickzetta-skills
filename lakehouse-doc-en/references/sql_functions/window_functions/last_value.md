### LAST_VALUE 

####  Description
When the sort key is the same, the `LAST_VALUE` function is used to return the value of a certain expression in the last row within the specified window. This function is very useful in data analysis and processing, especially when you need to get the last non-null value within a group or the entire dataset.

#### Parameter Description
- `expr`: An expression of any type, whose value will be returned.
- `ignoreNull` (optional): A boolean constant, with a default value of `false`. When set to `true`, the function will ignore null values (`NULL`) within the window and return the last non-null value.

#### Return Result
The return type is the same as the type of the `expr` parameter.

1. Basic usage:

   ```sql

   SELECT name, salary, LAST_VALUE(salary) OVER (PARTITION BY salary ) as min_salary
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
   +-----------+--------+------------+
   |   name    | salary | min_salary |
   +-----------+--------+------------+
   | null      | null   | null       |
   | Eric      | 28000  | 28000      |
   | Jeff      | 35000  | 35000      |
   | Frank     | 30000  | 30000      |
   | Felix     | 21000  | 21000      |
   | Tom       | 23000  | 23000      |
   | Charles   | 23000  | 23000      |
   | Charles F | 23000  | 23000      |
   | NotNull   | 23000  | 23000      |
   | Jane      | 29000  | 29000      |
   | Paul      | 29000  | 29000      |
   | Alex      | 32000  | 32000      |
   +-----------+--------+------------+
   ```

2. Ignore NULL values: In this example, we will ignore employees with NULL salaries.

   ```sql
   SELECT name, salary, LAST_VALUE(salary,true) OVER (PARTITION BY salary ) as min_salary
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
   +-----------+--------+------------+
   |   name    | salary | min_salary |
   +-----------+--------+------------+
   | null      | null   | null       |
   | Eric      | 28000  | 28000      |
   | Jeff      | 35000  | 35000      |
   | Frank     | 30000  | 30000      |
   | Felix     | 21000  | 21000      |
   | Tom       | 23000  | 23000      |
   | Charles   | 23000  | 23000      |
   | Charles F | 23000  | 23000      |
   | NotNull   | 23000  | 23000      |
   | Jane      | 29000  | 29000      |
   | Paul      | 29000  | 29000      |
   | Alex      | 32000  | 32000      |
   +-----------+--------+------------+
   ```
3. Using in conjunction with ORDER BY:
   ```sql
   SELECT name, salary, LAST_VALUE(salary) OVER (PARTITION BY dep_no ORDER BY dep_no DESC) as min_salary
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
   +-----------+--------+------------+
   |   name    | salary | min_salary |
   +-----------+--------+------------+
   | Jane      | 29000  | 35000      |
   | Jeff      | 35000  | 35000      |
   | Eric      | 28000  | 30000      |
   | Alex      | 32000  | 30000      |
   | Frank     | 30000  | 30000      |
   | Felix     | 21000  | 23000      |
   | Tom       | 23000  | 23000      |
   | Paul      | 29000  | 23000      |
   | Charles   | 23000  | 23000      |
   | Charles F | 23000  | 23000      |
   | null      | null   | 23000      |
   | NotNull   | 23000  | 23000      |
   +-----------+--------+------------+
   ```

4. Using Window Functions:When you need to apply the LAST function to the entire dataset, you can use the ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING clause.

   ```sql
   SELECT name, salary, LAST_VALUE(salary, true) OVER (ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as global_min_salary
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
   +-----------+--------+-------------------+
   |   name    | salary | global_min_salary |
   +-----------+--------+-------------------+
   | null      | null   | 35000             |
   | Felix     | 21000  | 35000             |
   | Tom       | 23000  | 35000             |
   | Charles   | 23000  | 35000             |
   | Charles F | 23000  | 35000             |
   | NotNull   | 23000  | 35000             |
   | Eric      | 28000  | 35000             |
   | Jane      | 29000  | 35000             |
   | Paul      | 29000  | 35000             |
   | Frank     | 30000  | 35000             |
   | Alex      | 32000  | 35000             |
   | Jeff      | 35000  | 35000             |
   +-----------+--------+-------------------+
   ```