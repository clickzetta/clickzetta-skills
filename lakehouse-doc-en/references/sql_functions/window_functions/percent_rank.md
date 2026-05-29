### PERCENT_RANK

#### Description

The `PERCENT_RANK` function is used to calculate the percentage rank of a specified row within its partition. This function sorts the data according to the sorting order specified by the `ORDER BY` clause and calculates the rank of each row within each partition. The return value is of type `double`, ranging from \[0.0, 1.0]. The specific calculation formula is `(current row rank - 1) / (total number of rows in the partition - 1)`. When there is only one row in the partition, the return value is 0.

#### Syntax
```sql
PERCENT_RANK() OVER (
    [PARTITION BY partition_expression, ...]
    [ORDER BY sort_expression [ASC | DESC], ...]
)
```
* `PARTITION BY` clause (optional): Specifies the expression(s) used for partitioning, multiple expressions can be used. If this clause is omitted, the entire result set will be used as a single partition.
* `ORDER BY` clause: Specifies the expression(s) used for sorting, multiple expressions can be used, and the sorting direction (ascending ASC or descending DESC) can be specified.

#### Example

The following example demonstrates how to use the `PERCENT_RANK` function to calculate the salary rank percentage of employees in different departments.
```sql
SELECT    name, dep_no,salary,
PERCENT_RANK() OVER (PARTITION BY dep_no ORDER BY  salary DESC) AS PERCENT_RANK
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
+-----------+--------+--------+--------------+
|   name    | dep_no | salary | PERCENT_RANK |
+-----------+--------+--------+--------------+
| Jeff      | 3      | 35000  | 0.0          |
| Jane      | 3      | 29000  | 1.0          |
| Alex      | 1      | 32000  | 0.0          |
| Frank     | 1      | 30000  | 0.5          |
| Eric      | 1      | 28000  | 1.0          |
| Paul      | 2      | 29000  | 0.0          |
| Tom       | 2      | 23000  | 0.25         |
| Charles   | 2      | 23000  | 0.25         |
| Charles F | 2      | 23000  | 0.25         |
| Felix     | 2      | 21000  | 1.0          |
| NotNull   | 4      | 23000  | 0.0          |
| null      | 4      | null   | 1.0          |
+-----------+--------+--------+--------------+
```