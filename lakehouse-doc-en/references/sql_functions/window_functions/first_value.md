### FIRST_VALUE 

#### Description

When the sort keys are the same, the FIRST\_VALUE function is used to return the value of the first row within the window. This function can group and sort data to find the desired value within a specific data range. By using the optional ignoreNull parameter, you can specify whether the function should ignore NULL values during calculation. This function is non-deterministic.

#### Syntax
```sql
FIRST_VALUE(expr[, ignoreNull]) OVER ([PARTITION BY partition_clause] [ORDER BY order_by_clause] [frame_clause])
```
#### Parameters

* expr: An expression of any type.
* ignoreNull (optional): A boolean constant, default value is false. When set to true, the function will return the first non-NULL value within the window.

#### Return Result

The return type is the same as the type of the expr parameter.

#### Example

1. Basic usage:
```sql
SELECT dep_no, salary, FIRST_VALUE(salary) OVER (PARTITION BY dep_no) AS first_salary
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
+--------+--------+-----------------------+
| dep_no | salary | first_non_null_salary |
+--------+--------+-----------------------+
| 3      | 29000  | 29000                 |
| 3      | 35000  | 29000                 |
| 1      | 28000  | 28000                 |
| 1      | 32000  | 28000                 |
| 1      | 30000  | 28000                 |
| 2      | 21000  | 21000                 |
| 2      | 23000  | 21000                 |
| 2      | 29000  | 21000                 |
| 2      | 23000  | 21000                 |
| 2      | 23000  | 21000                 |
| 4      | null   | null                  |
| 4      | 23000  | null                  |
+--------+--------+-----------------------+
```

2. Ignore NULL values:

```sql
SELECT dep_no, salary, FIRST_VALUE(salary, true) OVER (PARTITION BY dep_no) AS first_non_null_salary
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
+--------+--------+-----------------------+
| dep_no | salary | first_non_null_salary |
+--------+--------+-----------------------+
| 3      | 29000  | 29000                 |
| 3      | 35000  | 29000                 |
| 1      | 28000  | 28000                 |
| 1      | 32000  | 28000                 |
| 1      | 30000  | 28000                 |
| 2      | 21000  | 21000                 |
| 2      | 23000  | 21000                 |
| 2      | 29000  | 21000                 |
| 2      | 23000  | 21000                 |
| 2      | 23000  | 21000                 |
| 4      | null   | 23000                 |
| 4      | 23000  | 23000                 |
+--------+--------+-----------------------+
```

3. Combining with the ORDER BY clause:

```sql

SELECT dep_no, salary, FIRST_VALUE(salary, true) OVER (PARTITION BY dep_no ORDER BY salary) AS first_salary_by_salary
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
+--------+--------+------------------------+
| dep_no | salary | first_salary_by_salary |
+--------+--------+------------------------+
| 3      | 29000  | 29000                  |
| 3      | 35000  | 29000                  |
| 1      | 28000  | 28000                  |
| 1      | 30000  | 28000                  |
| 1      | 32000  | 28000                  |
| 2      | 21000  | 21000                  |
| 2      | 23000  | 21000                  |
| 2      | 23000  | 21000                  |
| 2      | 23000  | 21000                  |
| 2      | 29000  | 21000                  |
| 4      | null   | null                   |
| 4      | 23000  | 23000                  |
+--------+--------+------------------------+
```