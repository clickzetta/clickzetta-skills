### RANK 

#### Description

The `RANK()` function is used to calculate the rank of the current row within a specified partition. The ranking starts from 1 and is sorted based on the values in the `ORDER BY` clause. If there are identical sorting values, the `RANK()` function assigns the same rank to these rows and skips the next rank.

#### Syntax
```sql
RANK() OVER ([PARTITION BY column_name | column_name, ...] [ORDER BY column_name [ASC|DESC], ...])
```
#### Parameter Description

* `PARTITION BY`: Optional parameter used to partition the data. You can specify one or more column names to partition the data.
* `ORDER BY`: Optional parameter used to specify the columns and the sorting order (ascending or descending).

#### Return Value

* The return value type is bigint.
* The return value may be non-continuous and may have duplicates. If there are identical `ORDER BY` values, the result is the same, representing the rank of the first `ORDER BY` row.

#### Example

1. Basic Usage
   We can use the `RANK()` function to calculate the salary rank of each employee.
   ```sql
   SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS rank 
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
   +-----------+--------+------+
   |   name    | salary | rank |
   +-----------+--------+------+
   | Jeff      | 35000  | 1    |
   | Alex      | 32000  | 2    |
   | Frank     | 30000  | 3    |
   | Jane      | 29000  | 4    |
   | Paul      | 29000  | 4    |
   | Eric      | 28000  | 6    |
   | Tom       | 23000  | 7    |
   | Charles   | 23000  | 7    |
   | Charles F | 23000  | 7    |
   | NotNull   | 23000  | 7    |
   | Felix     | 21000  | 11   |
   | null      | null   | 12   |
   +-----------+--------+------+
   ```
2. Partition Usage
   If we want to calculate salary rankings based on employee grades, we can use the `PARTITION BY` clause.
   ```sql
     SELECT name,dep_no, salary, RANK() OVER (PARTITION BY dep_no ORDER BY salary DESC) AS rank 
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
   +-----------+--------+--------+------+
   |   name    | dep_no | salary | rank |
   +-----------+--------+--------+------+
   | Jeff      | 3      | 35000  | 1    |
   | Jane      | 3      | 29000  | 2    |
   | Alex      | 1      | 32000  | 1    |
   | Frank     | 1      | 30000  | 2    |
   | Eric      | 1      | 28000  | 3    |
   | Paul      | 2      | 29000  | 1    |
   | Tom       | 2      | 23000  | 2    |
   | Charles   | 2      | 23000  | 2    |
   | Charles F | 2      | 23000  | 2    |
   | Felix     | 2      | 21000  | 5    |
   | NotNull   | 4      | 23000  | 1    |
   | null      | 4      | null   | 2    |
   +-----------+--------+--------+------+
   ```
3. Multi-column Sorting
   If we need to sort based on two or more columns, we can specify these columns in the `ORDER BY` clause.
   ```sql
   SELECT name,dep_no, salary, RANK() OVER (PARTITION BY dep_no ORDER BY salary DESC,name ASC) AS rank 
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
   +-----------+--------+--------+------+
   |   name    | dep_no | salary | rank |
   +-----------+--------+--------+------+
   | Jeff      | 3      | 35000  | 1    |
   | Jane      | 3      | 29000  | 2    |
   | Alex      | 1      | 32000  | 1    |
   | Frank     | 1      | 30000  | 2    |
   | Eric      | 1      | 28000  | 3    |
   | Paul      | 2      | 29000  | 1    |
   | Charles   | 2      | 23000  | 2    |
   | Charles F | 2      | 23000  | 3    |
   | Tom       | 2      | 23000  | 4    |
   | Felix     | 2      | 21000  | 5    |
   | NotNull   | 4      | 23000  | 1    |
   | null      | 4      | null   | 2    |
   +-----------+--------+--------+------+
   ```
#### Notes

* The `RANK()` function may produce non-continuous rankings in the presence of identical sort values.
* When using the `RANK()` function, ensure that the columns in the `ORDER BY` clause match the columns you wish to rank by.