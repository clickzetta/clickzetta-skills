# Lakehouse SQL Query Statements

## Description

Lakehouse supports data queries using standard SQL SELECT statements. This document provides a detailed introduction to the basic syntax of query statements, parameter descriptions, and usage examples to help you perform data queries more efficiently.

## Syntax

```SQL
[WITH cte [, ...] ]
SELECT 
[ hints ] 
[ ALL | DISTINCT ]
select_expr [, (except_expr)] ...
FROM table_reference
[WHERE where_condition ] 
[GROUP BY [GROUPING SETS | ROLLUP | CUBE] {col_name | expr | position}]
    [ HAVING having_condition ]
[ WINDOW window_name AS (window_spec) [, ...] ]
[ QUALIFY qualify_condition ]
[ ORDER BY order_condition [ ASC | DESC ] [ NULLS { FIRST | LAST } ] ]
[ LIMIT  <number> [OFFSET <number>]
| OFFSET <number> [LIMIT <number>]
| LIMIT  <offset>, <number>
]
```

## Parameter Description

**1. WITH cte** (Optional)
[Common Table Expression](with.md), used to define a temporary result set in the query.

**2. ALL | DISTINCT** (Optional): Filters the result set. `all` returns all rows; `distinct` filters out duplicate rows. Default is `all`.

```
--Indicates not to deduplicate cp_start_date_sk
SELECT ALL cp_start_date_sk FROM catalog_page;
--Indicates to deduplicate cp_start_date_sk
SELECT DISTINCT cp_start_date_sk FROM catalog_page;
```

**3. HINTS** (Optional): Help the Lakehouse optimizer make better planning decisions. Currently supports [map join](mapjoin.md) as shown in the following example:

```SQL
SELECT /*+ MAPJOIN (t2) */ * FROM table1 t1
JOIN table2 t2
ON (t1.emp_id = t2.emp_id);
```

**4. select\_expr** (Required)
Specify the columns to query, supporting column names, column expressions, etc. For example: col1\_name, col2\_name, column expression, ...

**1) Exclude Columns** (Optional)
Optional. The `except_expr` format is `except(col1_name, col2_name, ...)`. When you want to read most of the columns in the table while excluding a few columns, you can use the `SELECT * except(col1_name, col2_name, ...) from ...;` statement, which means that the specified columns (col1, col2) will be excluded when reading the table data.

Example command is as follows.

```SQL
--Table structure is as follows
DESC students;
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| name        | string    |         |
| class       | string    |         |
+-------------+-----------+---------+
--Exclude the class column
SELECT * EXCEPT(class) FROM students LIMIT 1;
+-------+
| name  |
+-------+
| Alice |
+-------+
```

**2) where\_condition** (Optional)
Filter conditions used to screen data that meets specified criteria. Supports relational operators, like, rlike, in, not in, between…and, etc.

* Use with relational operators to filter data that meets specified criteria. Relational operators include:

  * `>`、`<`、`=`、`>=`、`<=`、`<>`
  * `like`、`rlike`
  * `in`、`not in`
  * `between…and`

**5. GROUP BY expression** (Optional)

Typically, group by is used in conjunction with aggregate functions to group data based on specified ordinary columns, partition columns, or regular expressions. `Grouping Sets`, `Rollup`, `Cube` are extensions of group by. For details, refer to [GROUPING SET](groupby.md). The usage rules for group by are as follows:

* The group by operation has a higher priority than the select operation, so the values of group by are the column names of the select input table or expressions composed of columns from the input table. Note that:

  * When the value of group by is a regular expression, the complete expression of the column must be used.
  * Columns that do not use aggregate functions in the select statement must appear in the group by.

**6. having\_condition** (Optional)
Typically, the `having` clause is used with aggregate functions to achieve filtering.

**7. WINDOW** (Optional)
The `WINDOW` clause is used to define named window specifications that can be shared across multiple window functions in the SELECT list. This avoids repeating the same `PARTITION BY` and `ORDER BY` clauses.

```sql
SELECT
  name,
  department,
  salary,
  SUM(salary) OVER w AS dept_total,
  RANK() OVER w AS rk
FROM employees
WINDOW w AS (PARTITION BY department ORDER BY salary DESC);
```

Multiple named windows can be separated by commas:

```sql
SELECT
  name,
  SUM(salary) OVER w1 AS dept_total,
  RANK() OVER w2 AS global_rk
FROM employees
WINDOW
  w1 AS (PARTITION BY department),
  w2 AS (ORDER BY salary DESC);
```

**8. QUALIFY qualify\_condition** (Optional)
The `QUALIFY` clause is used to filter the results of window function calculations, similar to how `HAVING` filters aggregate function results. `QUALIFY` executes after window function calculations are complete and can directly reference window function expressions or aliases defined in the SELECT list. This avoids the need to use subqueries to filter window function results. For more information, refer to [QUALIFY](sql-qualify.md).

```sql
-- Get the employee with the highest salary in each department
SELECT name, department, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rk
FROM employees
QUALIFY rk = 1;
```

**9. order\_condition** (Optional)
Globally sort all data by specified columns, expressions, or ordinal positions in the SELECT list (ordinal, starting from 1). For example, `ORDER BY 1` sorts by the first column, and `ORDER BY 2 DESC` sorts by the second column in descending order. The default is ascending order; use the `desc` keyword for descending order. By default, ascending order places `NULL` values at the beginning, while descending order places `NULL` at the end. Order by is a time-consuming and resource-intensive operation because all data needs to be sent to one node for sorting, which requires more memory compared to operations without sorting.

You can explicitly control the sort position of NULL values using `NULLS FIRST` or `NULLS LAST`:

```SQL
SELECT * FROM orders ORDER BY amount ASC NULLS LAST;   -- NULL sorted last
SELECT * FROM orders ORDER BY amount DESC NULLS FIRST; -- NULL sorted first
```

| Syntax | NULL Position |
|------|---------|
| `ORDER BY col ASC` (default) | NULL first |
| `ORDER BY col DESC` (default) | NULL last |
| `ORDER BY col NULLS FIRST` | NULL first (regardless of sort direction) |
| `ORDER BY col NULLS LAST` | NULL last (regardless of sort direction) |

**10. LIMIT ... OFFSET** (Optional)

* LIMIT \<number> indicates that the query result only returns the first \<number> records, where \<number> is a positive integer. This syntax can be used for pagination or to limit the amount of data queried. Supports the LIMIT m,n syntax. **Using limit offset only makes sense when combined with order by, otherwise the data may be inconsistent each time it is executed.**
* OFFSET \<number> indicates that the query result skips the first \<number> records and then returns the remaining records, where \<number> is a positive integer. This syntax can be used to specify the starting position of the query. The OFFSET keyword can also be replaced with a comma.
* LIMIT and OFFSET can be used simultaneously or individually. The following syntaxes are supported:
  * `LIMIT 10` — returns the first 10 rows
  * `LIMIT 10 OFFSET 20` — skips the first 20 rows, returns the next 10
  * `OFFSET 20 LIMIT 10` — same as above; OFFSET can also be written before LIMIT
  * `OFFSET 20` — skips the first 20 rows only, returns all remaining records (no limit on return count)
  * `LIMIT 20, 10` — skips the first 20 rows, returns the next 10 (comma syntax)
* When the OFFSET value is 0, it is equivalent to not using OFFSET.
* Large OFFSET values may cause performance degradation because the skipped rows still need to be computed on the server side.

## Query Historical Version Data

In addition to the standard `SELECT` options, Lakehouse also supports users accessing historical data at any point within a defined time period, including changed or deleted data. Supports querying tables, dynamic tables, and materialized views.
**Note**: The historical query of objects depends on the data retention period. The current version has a default data retention period of 1 day. You can adjust the retention period by executing the [ALTER command](timetravel.md). Note that modifying the retention period may increase storage costs. For specific usage, refer to [TIME TRAVEL](timetravel.md).

```sql
SELECT 
    table_identifier TIMESTAMP AS OF timestamp_expression
```

By using the TIMESTAMP AS OF clause, users can specify a specific point in time to query the exact position in the table's history within the retention period or the data just before the specified point. The timestamp_expression is a parameter that returns a timestamp type expression, such as:

* `'2023-11-07 14:49:18'`, a string that can be cast to a timestamp.
* `CAST('2023-11-07 14:49:18' AS TIMESTAMP)`.
* `CURRENT_TIMESTAMP() - INTERVAL 12 HOURS`. The version from 12 hours ago.
* Any expression that is itself a timestamp type or can be cast to a timestamp.
  Usage example

```
SELECT * FROM events TIMESTAMP AS OF TIMESTAMP'2024-10-18 22:15:12.013'
```

## Syntactic Sugar: Trailing Commas

In SQL statements, using Trailing Commas can make the statements easier to read and edit. Even if there is an extra comma after the last value or parameter, it will not cause an error. For example:

```SQL
SELECT    client_ip,
          client_identity,
          userid,
          user_agent,
          log_time
          -- status_code 
FROM      server_logs;
```

## Notes

* It is recommended that you limit the size of the submitted query text (i.e., SQL statements) to 5MB per statement. SQL texts larger than 5MB cannot be submitted. If you have SQL texts exceeding 5MB, please submit a ticket for resolution.

### Examples

1. **Basic Query**
   ```SQL
   -- Query the names and classes of all students
   SELECT name, class FROM students;
   ```

2. **Using the WITH Clause (Common Table Expressions)**
   ```SQL
   WITH ranked_students AS (
     SELECT name, class, RANK() OVER (ORDER BY score DESC) as rank
     FROM students
   )
   SELECT * FROM ranked_students WHERE rank <= 10;
   ```

3. **Deduplication Query**
   ```SQL
   -- Query different class names
   SELECT DISTINCT class FROM students;
   ```

4. **Use HINTS to Optimize Queries**
   ```SQL
   SELECT /*+ MAPJOIN(t2) */ * FROM students t1
   JOIN classes t2 ON t1.class_id = t2.id;
   ```

5. **Conditional Filtering**
   ```SQL
   -- Query the names of students older than 20 years
   SELECT name FROM students WHERE age > 20;
   ```

6. **GROUP BY and Aggregate Functions**
   ```SQL
   -- Group by class and query the average score of each class
   SELECT class, AVG(score) FROM students GROUP BY class;
   ```

7. **Using the HAVING Clause**
   ```SQL
   -- Query classes with an average score greater than 60
   SELECT class, AVG(score) as avg_score FROM students GROUP BY class HAVING avg_score > 60;
   ```

8. **ORDER BY and LIMIT**
   ```SQL
   -- Query the top 5 students with scores in descending order
   SELECT name, score FROM students ORDER BY score DESC LIMIT 5;
   ```

9. **Query Historical Version Data**
   ```SQL
   -- Query the student table data at the timestamp 2024-10-18 22:15:12.013
   SELECT * FROM students TIMESTAMP AS OF TIMESTAMP'2024-10-18 22:15:12.013';
   ```

10. Join Example
    Refer to [Join](join.md) for related usage

## Best Practices

1. **Utilize Partition and Bucket Filtering**
   * Whenever possible, use the partition and bucket of Lakehouse as data filtering conditions to reduce the data scanning range.

2. **Use Index Fields**
   * Fully utilize the index fields of Lakehouse as data filtering conditions to accelerate query speed. Refer to [Index](lakehouse-index-best-practice.md).

3. **Use Aggregation Reasonably**
   * Aggregation operations should be used when the data volume is large to reduce data transmission and improve query efficiency.

4. **Use ORDER BY and LIMIT for Pagination**
   * When pagination queries are needed, using the combination of ORDER BY and LIMIT can effectively retrieve data for specific pages.

5. **Pay Attention to Data Type Matching**
   * When using UNION or JOIN, ensure that the columns being joined have the same data type.

6. **Avoid Large Query Texts**
   * Limit the query text size to within 5MB to avoid submission failures.

7. **Use HAVING Clause to Filter Aggregated Results**
   * The HAVING clause should be used after the aggregation function to filter the aggregated result set.

8. **Use WITH Clause to Simplify Complex Queries**
   * Common Table Expressions (WITH clause) can simplify complex queries, making them easier to understand and maintain.

9. **Pay Attention to Query Costs**
   * Modifying the data retention period may increase storage costs. Set the data retention period reasonably to balance query needs and costs.
