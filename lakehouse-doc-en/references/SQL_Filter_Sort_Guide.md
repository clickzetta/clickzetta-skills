# Lakehouse Basic Data Filtering and Sorting Guide

## Overview

Data querying is the first step in data analysis. Singdata Lakehouse provides complete SQL filtering and sorting capabilities, supporting everything from simple conditional filtering to complex expression combinations. This guide categorizes usage by common business scenarios to help you quickly master efficient data exploration methods.

### Quick Navigation

* [Basic Column Selection](#basic-column-selection) -- Use SELECT to specify return columns
* [Conditional Filtering](#conditional-filtering) -- Use WHERE to filter data
* [Result Sorting](#result-sorting) -- Use ORDER BY for sorting
* [Limit Returned Rows](#limit-returned-rows) -- Use LIMIT to control result set size
* [Exclude Specific Columns](#exclude-specific-columns) -- Use EXCEPT to quickly exclude sensitive fields

***

## SQL Commands Covered

| Command/Clause | Purpose | Applicable Scenario |
|-----------|------|----------|
| `SELECT` | Specify returned columns | Column pruning, reduce data transfer |
| `SELECT * EXCEPT(...)` | Exclude specified columns | Quickly exclude sensitive fields |
| `WHERE` | Row-level filtering | Filter data by condition |
| `ORDER BY` | Result sorting | Sort by single or multiple columns |
| `LIMIT` | Limit returned rows | Data exploration, paginated queries |

***

## Prerequisites

The following examples use a simulated employee table `employees`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT,
    emp_name STRING,
    dept STRING,
    salary DOUBLE,
    hire_date DATE
);

-- Insert test data
INSERT INTO employees VALUES
(1, 'Alice', 'Engineering', 12000, '2020-03-15'),
(2, 'Bob', 'Engineering', 9500, '2021-07-01'),
(3, 'Carol', 'Marketing', 8500, '2019-11-20'),
(4, 'David', 'Marketing', 7800, '2022-01-10'),
(5, 'Eve', 'HR', 6000, '2023-05-05');
```

***

## Basic Column Selection

Explicitly specify the needed columns when querying to avoid returning unnecessary data. In columnar storage, this can significantly improve query performance.

```sql
-- Query only name and department
SELECT emp_name, dept
FROM employees;
```

**Result**:

| emp_name | dept |
|----------|------|
| Alice | Engineering |
| Bob | Engineering |
| Carol | Marketing |
| David | Marketing |
| Eve | HR |

> **Note**: Avoid using `SELECT *`. Explicitly specifying column names enables column pruning optimization and reduces I/O.

***

## Conditional Filtering

Use the `WHERE` clause to filter data by condition. Lakehouse supports a rich set of comparison and logical operators.

### Scenario 1: Numeric Range Filtering

```sql
-- Query employees with salary greater than 8000
SELECT emp_name, dept, salary
FROM employees
WHERE salary > 8000;
```

### Scenario 2: Multiple Condition Combinations

```sql
-- Query Engineering department employees with salary above 10000
SELECT emp_name, dept, salary
FROM employees
WHERE dept = 'Engineering' AND salary > 10000;
```

### Scenario 3: IN and BETWEEN

```sql
-- Query employees in Marketing or HR departments
SELECT emp_name, dept
FROM employees
WHERE dept IN ('Marketing', 'HR');

-- Query employees hired between 2020 and 2022
SELECT emp_name, hire_date
FROM employees
WHERE hire_date BETWEEN '2020-01-01' AND '2022-12-31';
```

### Scenario 4: Fuzzy Matching

```sql
-- Query employees whose names start with 'A'
SELECT emp_name
FROM employees
WHERE emp_name LIKE 'A%';
```

***

## Result Sorting

Use `ORDER BY` to sort query results, supporting ascending (ASC, default) and descending (DESC) order.

```sql
-- Sort by salary in descending order
SELECT emp_name, dept, salary
FROM employees
ORDER BY salary DESC;

-- Multi-column sort: first by department ascending, then by salary descending
SELECT emp_name, dept, salary
FROM employees
ORDER BY dept ASC, salary DESC;
```

**Result** (multi-column sort):

| emp_name | dept | salary |
|----------|------|--------|
| Alice | Engineering | 12000 |
| Bob | Engineering | 9500 |
| Eve | HR | 6000 |
| Carol | Marketing | 8500 |
| David | Marketing | 7800 |

***

## Limit Returned Rows

Use `LIMIT` to control the number of returned rows, commonly used for data exploration and paginated queries.

```sql
-- View only the top 3 records
SELECT emp_name, dept, salary
FROM employees
ORDER BY salary DESC
LIMIT 3;
```

**Result**:

| emp_name | dept | salary |
|----------|------|--------|
| Alice | Engineering | 12000 |
| Bob | Engineering | 9500 |
| Carol | Marketing | 8500 |

> **Tip**: In the Lakehouse Studio Web UI, query results are limited to 10000 rows by default. Using `LIMIT` can speed up the return of small batches of data.

***

## Exclude Specific Columns

Use the `EXCEPT` clause to quickly exclude unneeded columns, especially useful for wide table queries.

```sql
-- Query all columns except emp_id
SELECT * EXCEPT(emp_id)
FROM employees;
```

**Result**:

| emp_name | dept | salary | hire_date |
|----------|------|--------|-----------|
| Alice | Engineering | 12000 | 2020-03-15 |
| Bob | Engineering | 9500 | 2021-07-01 |
| Carol | Marketing | 8500 | 2019-11-20 |
| David | Marketing | 7800 | 2022-01-10 |
| Eve | HR | 6000 | 2023-05-05 |

***

## Clean Up Test Data

After completing query verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS employees;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Column Pruning Optimization**: Explicitly specify `SELECT` column names and avoid `SELECT *` to significantly reduce I/O and network transfer.
2. **Partition Pruning**: If the table is partitioned, filter directly on the partition column in `WHERE` to skip irrelevant partitions.
3. **Sorting Performance**: `ORDER BY` triggers a full sort; for large data volumes, use it with `LIMIT`.
4. **NULL Value Sorting**: `ORDER BY` places `NULL` values last (ascending) or first (descending) by default; use `NULLS FIRST/LAST` to control.

***

## Related Documentation

* [SELECT Basic Syntax](query-syntax.md)
* [Window Functions](WINDOWFUNCTION.md)
* [QUALIFY Clause](sql-qualify.md)
