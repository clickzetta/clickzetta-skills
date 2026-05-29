# Lakehouse Data Update and Cleanup Guide

## Overview

In data warehouse operations, it is often necessary to correct erroneous data, clean up expired records, or reset table data. Singdata Lakehouse provides three data modification methods: `UPDATE`, `DELETE`, and `TRUNCATE`, each suitable for different scenarios. This guide categorizes usage by business scenario to help you quickly master safe and efficient data update and cleanup methods.

### Quick Navigation

* [Conditional Data Update](#conditional-data-update) -- Use UPDATE to modify specific rows
* [Batch Update](#batch-update) -- Use ORDER BY + LIMIT for batch updates
* [Conditional Data Deletion](#conditional-data-deletion) -- Use DELETE to clean specific rows
* [Truncate Table Data](#truncate-table-data) -- Use TRUNCATE to quickly clear entire table
* [Update Based on Related Table](#update-based-on-related-table) -- Use subqueries or MERGE INTO for updates

***

## SQL Commands Covered

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `UPDATE ... SET ... WHERE` | Update rows by condition | Fix erroneous data, status changes |
| `UPDATE ... ORDER BY ... LIMIT` | Batch update | Safe updates for large data volumes |
| `DELETE FROM ... WHERE` | Delete rows by condition | Clean expired or invalid data |
| `TRUNCATE TABLE` | Clear entire table | Quickly reset table data |

***

## Prerequisites

The following examples use a simulated employee table `employees_update`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS employees_update (
    emp_id INT,
    emp_name STRING,
    dept STRING,
    salary DOUBLE,
    status STRING
);

-- Insert test data
INSERT INTO employees_update VALUES
(1, 'Alice', 'Engineering', 12000, 'active'),
(2, 'Bob', 'Engineering', 9500, 'active'),
(3, 'Carol', 'Marketing', 8500, 'active'),
(4, 'David', 'Marketing', 7800, 'inactive'),
(5, 'Eve', 'HR', 6000, 'active');
```

***

## Conditional Data Update

Use the `UPDATE` statement to modify rows that meet conditions. Always use the `WHERE` clause to limit the update scope.

```sql
-- Give Engineering department employees a 10% raise
UPDATE employees_update 
SET salary = salary * 1.1
WHERE dept = 'Engineering';
```

**Verify Result**:

```sql
SELECT emp_id, emp_name, dept, salary FROM employees_update ORDER BY emp_id;
```

| emp_id | emp_name | dept | salary |
|--------|----------|------|--------|
| 1 | Alice | Engineering | 13200 |
| 2 | Bob | Engineering | 10450 |
| 3 | Carol | Marketing | 8500 |
| 4 | David | Marketing | 7800 |
| 5 | Eve | HR | 6000 |

> ⚠️ **Note**: DOUBLE type calculations may have floating-point precision issues (e.g., 13200.000000000002). Use `ROUND(salary, 2)` for formatting. `UPDATE` without `WHERE` updates all rows in the table; use with caution.

***

## Batch Update

When the number of rows to update is very large, use `ORDER BY + LIMIT` for batch updates to avoid long locks.

```sql
-- Update 2 rows at a time, ordered by emp_id for consistency
UPDATE employees_update 
SET status = 'reviewed'
WHERE status = 'active'
ORDER BY emp_id
LIMIT 2;
```

**Verify Result**:

| emp_id | emp_name | status |
|--------|----------|--------|
| 1 | Alice | reviewed |
| 2 | Bob | reviewed |
| 3 | Carol | active |
| 5 | Eve | active |

> 💡 **Tip**: Repeat this statement in a loop until `affected rows = 0` to complete the full batch update.

***

## Conditional Data Deletion

Use the `DELETE` statement to delete rows that meet conditions. Again, use the `WHERE` clause to limit the deletion scope.

```sql
-- Delete employees with inactive status
DELETE FROM employees_update 
WHERE status = 'inactive';
```

**Verify Result**:

```sql
SELECT * FROM employees_update ORDER BY emp_id;
```

| emp_id | emp_name | dept | salary | status |
|--------|----------|------|--------|--------|
| 1 | Alice | Engineering | 13200 | reviewed |
| 2 | Bob | Engineering | 10450 | reviewed |
| 3 | Carol | Marketing | 8500 | active |
| 5 | Eve | HR | 6000 | active |

***

## Truncate Table Data

Use `TRUNCATE TABLE` to quickly clear all table data while preserving the table structure. More efficient than `DELETE`.

```sql
-- Clear table data
TRUNCATE TABLE employees_update;
```

**Verify Result**:

```sql
SELECT COUNT(*) FROM employees_update;
```

| COUNT(*) |
|----------|
| 0 |

> ⚠️ **Note**:
> * `TRUNCATE` is not rollback-able (not within Time Travel retention), use with caution.
> * `TRUNCATE` does not support `WHERE` conditions; it can only clear the entire table.
> * For conditional clearing, use `DELETE`.

***

## Update Based on Related Table

When updating a table based on data from another table, use subqueries or `MERGE INTO`.

```sql
-- Re-insert data for demonstration
INSERT INTO employees_update VALUES
(1, 'Alice', 'Engineering', 13200, 'reviewed'),
(2, 'Bob', 'Engineering', 10450, 'reviewed');

-- Create salary adjustment table
CREATE TABLE IF NOT EXISTS salary_adjustments (
    emp_id INT,
    adjust_amount DOUBLE
);

INSERT INTO salary_adjustments VALUES
(1, 500),
(2, 300);

-- Use subquery to update salaries
UPDATE employees_update 
SET salary = salary + (
    SELECT adjust_amount 
    FROM salary_adjustments 
    WHERE salary_adjustments.emp_id = employees_update.emp_id
)
WHERE emp_id IN (SELECT emp_id FROM salary_adjustments);
```

**Verify Result**:

| emp_id | emp_name | salary |
|--------|----------|--------|
| 1 | Alice | 13700 |
| 2 | Bob | 10750 |

> 💡 **Tip**: For complex related updates, `MERGE INTO` is recommended for clearer syntax.

***

## Clean Up Test Data

After completing update and cleanup verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS employees_update;
DROP TABLE IF EXISTS salary_adjustments;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **WHERE Clause**: Always use `WHERE` with `UPDATE` and `DELETE` to avoid accidental full-table operations.
2. **Transactionality**: A single `UPDATE` or `DELETE` is an atomic operation -- either all rows succeed or all fail.
3. **TRUNCATE Is Irrecoverable**: `TRUNCATE` operations do not retain historical versions and cannot be recovered through Time Travel.
4. **Dynamic Table Limitation**: Dynamic Tables do not support direct `UPDATE` or `DELETE`; data is refreshed automatically by upstream table changes.
5. **Batch Operations**: For large-volume updates/deletes, use `ORDER BY + LIMIT` to execute in batches to avoid prolonged resource usage.

***

## Related Documentation

* [UPDATE](UPDATE.md)
* [DELETE](DELETE.md)
* [TRUNCATE](TRUNCATE.md)
* [MERGE INTO](MERGE.md)
