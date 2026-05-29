### ROW_NUMBER

#### Description

The `ROW_NUMBER()` function is used to calculate the row number of the current row within its partition, starting from 1, and ordered by the specified `ORDER BY` clause. This function is very useful when processing data, especially when you need to assign a unique sequence number to each row in the result set.

#### Syntax
```sql
ROW_NUMBER() OVER (
  [PARTITION BY partition_expression, ...]
  ORDER BY sort_expression [ASC | DESC]
)
```
#### Parameter Description

* `partition_expression`: An expression used to define partitions, there can be multiple, used to divide the result set into multiple partitions.
* `sort_expression`: An expression used to specify sorting, it can be a column name or an expression, used to sort rows within each partition.
* `ASC` | `DESC`: Optional parameters used to specify the sorting direction, default is `ASC`.

#### Return Result

* The return value type is `bigint`.
* The returned row numbers are continuous and non-repetitive.

#### Usage Example

1. Basic usage:
   ```sql

     SELECT name, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num 
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
   +-----------+--------+---------+
   |   name    | salary | row_num |
   +-----------+--------+---------+
   | Jeff      | 35000  | 1       |
   | Alex      | 32000  | 2       |
   | Frank     | 30000  | 3       |
   | Jane      | 29000  | 4       |
   | Paul      | 29000  | 5       |
   | Eric      | 28000  | 6       |
   | Tom       | 23000  | 7       |
   | Charles   | 23000  | 8       |
   | Charles F | 23000  | 9       |
   | NotNull   | 23000  | 10      |
   | Felix     | 21000  | 11      |
   | null      | null   | 12      |
   +-----------+--------+---------+
   ```
2. Using Partitions:
   ```sql
   SELECT name,dep_no, salary, RANK() OVER (PARTITION BY dep_no ) AS row_num 
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
   +-----------+--------+--------+---------+
   |   name    | dep_no | salary | row_num |
   +-----------+--------+--------+---------+
   | Jane      | 3      | 29000  | 1       |
   | Jeff      | 3      | 35000  | 1       |
   | Eric      | 1      | 28000  | 1       |
   | Alex      | 1      | 32000  | 1       |
   | Frank     | 1      | 30000  | 1       |
   | Felix     | 2      | 21000  | 1       |
   | Tom       | 2      | 23000  | 1       |
   | Paul      | 2      | 29000  | 1       |
   | Charles   | 2      | 23000  | 1       |
   | Charles F | 2      | 23000  | 1       |
   | null      | 4      | null   | 1       |
   | NotNull   | 4      | 23000  | 1       |
   +-----------+--------+--------+---------+
   ```
3. Multi-column Sorting: 
   ```sql
   SELECT name,dep_no, salary, ROW_NUMBER() OVER (PARTITION BY dep_no ORDER BY salary DESC,name ASC) AS row_num 
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
   +-----------+--------+--------+---------+
   |   name    | dep_no | salary | row_num |
   +-----------+--------+--------+---------+
   | Jeff      | 3      | 35000  | 1       |
   | Jane      | 3      | 29000  | 2       |
   | Alex      | 1      | 32000  | 1       |
   | Frank     | 1      | 30000  | 2       |
   | Eric      | 1      | 28000  | 3       |
   | Paul      | 2      | 29000  | 1       |
   | Charles   | 2      | 23000  | 2       |
   | Charles F | 2      | 23000  | 3       |
   | Tom       | 2      | 23000  | 4       |
   | Felix     | 2      | 21000  | 5       |
   | NotNull   | 4      | 23000  | 1       |
   | null      | 4      | null   | 2       |
   +-----------+--------+--------+---------+
   ```
#### Notes

* The `ROW_NUMBER()` function is independent for each partition, meaning each partition will have its own sequence of row numbers.
* When using the `ROW_NUMBER()` function, ensure that the columns in the `ORDER BY` clause are unique to avoid generating non-continuous row numbers.
* When the columns in the `ORDER BY` clause have the same values, the `ROW_NUMBER()` function will, by default, generate non-continuous row numbers. If continuous row numbers are needed, consider using the `DENSE_RANK()` function.