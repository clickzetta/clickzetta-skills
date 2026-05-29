### AVG 
#### Description
The `AVG` function is used to calculate the average value of an expression within a window. This function can be applied to various numeric data types, including `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, and `DECIMAL`. The type of the return result will be converted accordingly based on the input type. Results of the `DECIMAL` type will retain their original precision and scale, while other types will return as `DOUBLE`. It is important to note that `NULL` values will not be included in the average calculation.

#### Syntax
```sql
AVG(expr) OVER ([PARTITION_clause] [ORDER_BY_clause] [FRAME_clause])
```
#### Parameter Description
* `expr`: The numeric expression for which the average value needs to be calculated.
* `PARTITION_clause`: Optional parameter used to partition the data so that the average value is calculated separately within each partition.
* `ORDER_BY_clause`: Optional parameter used to specify the sorting method of records within the window.
* `FRAME_clause`: Optional parameter used to define the specific range of the window.

#### Return Result
The `AVG` function returns a numeric value representing the average value of the data within the window. For `DECIMAL` type, the return result is also of `DECIMAL` type, and its precision and scale may increase. The return result for other types is of `DOUBLE` type.

#### Example
1. Query the average salary (`salary`) of the same department (`dep_no`), partitioned by department without sorting:
```sql
SELECT dep_no, salary, AVG(salary) OVER (PARTITION BY dep_no)
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
```
The result is as follows:
```
dep_no | salary | avg_salary
--------+---------+------------
1       | 28000   | 30000.0
1       | 32000   | 30000.0
1       | 30000   | 30000.0
2       | 21000   | 24000.0
2       | 23000   | 24000.0
2       | 29000   | 24000.0
2       | 23000   | 24000.0
3       | 29000   | 32000.0
3       | 35000   | 32000.0
```
2. Query the cumulative average salary (`salary`) of the same department (`dep_no`), partitioned by department and ordered by salary. Return the average value from the start row to all rows with the same salary as the current row in the current window:
```sql
SELECT dep_no, salary, AVG(salary) OVER (PARTITION BY dep_no ORDER BY salary)
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
```
The result is as follows:
```
dep_no | salary | avg_salary
--------+---------+------------
1       | 28000   | 28000.0
1       | 30000   | 29000.0
1       | 32000   | 30000.0
2       | 21000   | 21000.0
2       | 23000   | 22333.333333333332
2       | 23000   | 22333.333333333332
2       | 29000   | 24000.0
3       | 29000   | 29000.0
3       | 35000   | 32000.0
```
#### Notes
* When there are no non-`NULL` values within the window, the `AVG` function returns `NULL`.
* When using the `AVG` function, ensure that the definitions of partition, sorting, and window range meet expectations.