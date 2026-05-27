### Overview of Window Functions

Window functions are a powerful analytical tool in SQL that allow you to perform calculations over a set of related rows, rather than just a single row. Window functions create a "window" to view the current row and its context rows, enabling complex data analysis tasks.

#### Syntax
```sql
function_name([expr [, ...]]) OVER ( [window_definition] )
```
* `function_name`: Built-in window functions, such as `SUM`, `COUNT`, etc.
* `expr`: Function parameters, determined based on actual data.
* `window_definition`: Window definition, used to specify how to apply the window function on the dataset.

#### Window Definition
```sql
[PARTITION BY expression [, ...]]
[ORDER BY expression [ASC|DESC]] [, ...]
[FRAME frame_clause]
```
* `PARTITION BY` clause: Optional, used to divide the dataset into different partitions.
* `ORDER BY` clause: Optional, used to specify the sorting method of data within each window. It is recommended to use unique columns or column combinations to reduce randomness.
* `FRAME` clause: Optional, used to determine the boundaries of the window. Detailed description is as follows.

#### FRAME clause
```sql
{ROWS|RANGE} BETWEEN frame_start AND frame_end
```
`FRAME` clause defines a closed interval to determine the data boundaries. `ROWS` and `RANGE` are two types of boundary types.

* `ROWS` type: Determines the boundary by row number.
* `RANGE` type: When `ORDER BY` is specified, the boundary is determined by the size relationship of the column values. When `ORDER BY` is not specified, all rows are considered to have the same value.

`frame_start` and `frame_end` represent the start and end boundaries of the window. `frame_start` is required, `frame_end` is optional, and the default value is `CURRENT ROW`. The specific options are as follows:

- `UNBOUNDED PRECEDING`: Indicates the start of the partition or result set.
- `OFFSET PRECEDING`: Indicates an offset relative to the current row.
- `CURRENT ROW`: Indicates only the current row.
- `OFFSET FOLLOWING`: Indicates an offset after the current row.
- `UNBOUNDED FOLLOWING`: Indicates the end of the partition or result set.

When the `FRAME` clause is not explicitly set, the default `FRAME` clause is:
```sql
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```
#### Usage Example
```sql
SELECT
  name,
  dep_no,
  salary,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) rows_up_uf,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) range_up_uf,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) rows_up_cr,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) range_up_cr,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) rows_cr_uf,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) range_cr_uf,
  COUNT(salary) OVER (PARTITION BY dep_no ORDER BY salary ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) rows_1p_1f
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Lily', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000)
  AS tab(name, dep_no, salary);
```
#### Window Function Classification

Window functions can be classified into the following three categories based on their behavior:

1. Ranking Functions (`ranking_function`): Used to calculate rankings, must specify `ORDER BY`, and cannot specify the `FRAME` clause. For example:
   - `ROW_NUMBER`
   - `RANK`
   - `DENSE_RANK`
   - `PERCENT_RANK`
   - `NTILE`
2. Analytic Functions (`analytic_function`): Used to perform more complex analytical calculations. For example:
   - `CUME_DIST`
   - `