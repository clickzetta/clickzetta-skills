### DENSE_RANK 

#### Description

The `DENSE_RANK` function is a window function used to calculate the continuous rank of the current row within a specified partition, starting from 1. When the values in the `ORDER BY` clause are the same, the `DENSE_RANK` function generates the same rank, but the rank numbers do not skip.

#### Syntax
```sql
DENSE_RANK() OVER ([PARTITION_clause] [ORDER_BY_clause])
```
#### Parameter Description

* `PARTITION_clause` (optional): Specifies the clause for partitioning, used to divide the dataset into different partitions. If no partition is specified, the ranking is applied to the entire dataset.
* `ORDER_BY_clause`: Specifies the columns or expressions used for sorting the data.

#### Return Type

The return value type is `bigint`.

#### Usage Example

1. Basic Usage
```sql

SELECT 
       name,
       salary,
       dense_rank() OVER (PARTITION BY dep_no ORDER BY salary DESC) AS salary_rank
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
  ('null',4,null)
AS tab(name, dep_no, salary);
+-----------+--------+-------------+
|   name    | salary | salary_rank |
+-----------+--------+-------------+
| Jeff      | 35000  | 1           |
| Jane      | 29000  | 2           |
| Alex      | 32000  | 1           |
| Frank     | 30000  | 2           |
| Eric      | 28000  | 3           |
| Paul      | 29000  | 1           |
| Tom       | 23000  | 2           |
| Charles   | 23000  | 2           |
| Charles F | 23000  | 2           |
| Felix     | 21000  | 3           |
| null      | null   | 1           |
+-----------+--------+-------------+
```
In this example, we partition employees by department ID and sort by salary in descending order, calculating each employee's salary rank within their department.

2. No partition ranking
```sql
SELECT 
       name,
       salary,
       dense_rank() OVER ( ORDER BY salary DESC) AS salary_rank
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
  ('null',4,null)
AS tab(name, dep_no, salary);
+---------+--------+-------------+
|  name   | salary | salary_rank |
+---------+--------+-------------+
| Jeff    | 35000  | 1           |
| Alex    | 32000  | 2           |
| Frank   | 30000  | 3           |
| Jane    | 29000  | 4           |
| Paul    | 29000  | 4           |
| Eric    | 28000  | 5           |
| Tom     | 23000  | 6           |
| Charles | 23000  | 6           |
| Felix   | 21000  | 7           |
| null    | null   | 8           |
+---------+--------+-------------+
```
In this example, we did not specify a partition, so the inventory ranking will be calculated for the entire product dataset, sorted in ascending order by inventory quantity.

3. Multi-column Sorting
```sql
SELECT student_id,
       student_name,
       exam_score,
       dense_rank() OVER (PARTITION BY exam_subject ORDER BY exam_score DESC, student_name ASC) AS score_rank
FROM exam_results;
```
In this example, we first partition by exam subjects, then sort by exam scores in descending order. If the scores are the same, then sort by student names in ascending order to calculate each student's ranking in each subject exam.

#### Notes

* When the values in the `ORDER BY` clause are the same, the `DENSE_RANK` function does not generate skipped rankings; the rankings will repeat.
* Compared to the `RANK()` function, the `DENSE_RANK()` function provides more compact rankings when dealing with the same values, whereas the `RANK()` function will produce discontinuous rankings.
* When using the `DENSE_RANK()` function, ensure that the `ORDER BY` clause correctly reflects the way you want to sort the data.