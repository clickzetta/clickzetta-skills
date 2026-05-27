# Lakehouse Data Comparison and Merging Guide (Set Operations)

## Overview

In data analysis, it is often necessary to merge, compare, or find differences between multiple query results. Singdata Lakehouse provides complete set operation support, including `UNION` (merge), `INTERSECT` (intersection), and `EXCEPT` (difference). This guide categorizes usage by business scenario to help you quickly master efficient data comparison and merging methods.

### Quick Navigation

* [Merge Data](#merge-data) -- Use UNION ALL to merge multiple query results
* [Deduplicated Merge](#deduplicated-merge) -- Use UNION to merge and remove duplicate rows
* [Find Common Data](#find-common-data) -- Use INTERSECT to find the intersection
* [Find Different Data](#find-different-data) -- Use EXCEPT to find the difference
* [Multi-Table Comparison](#multi-table-comparison) -- Combine set operations for complex comparisons

***

## SQL Commands Covered

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `UNION ALL` | Merge result sets (preserve duplicates) | Quickly merge multiple tables or partition data |
| `UNION` | Merge result sets (deduplicate) | Need unique records after merging |
| `INTERSECT` | Return the intersection of two result sets | Find common users, common orders, etc. |
| `EXCEPT` | Return data in first result set but not in second | Find new, churned, or different data |

***

## Prerequisites

The following examples use two simulated sales tables `sales_2023` and `sales_2024`:

```sql
-- Create 2023 sales table
CREATE TABLE IF NOT EXISTS sales_2023 (
    customer_id INT,
    product STRING,
    amount DOUBLE
);

-- Create 2024 sales table
CREATE TABLE IF NOT EXISTS sales_2024 (
    customer_id INT,
    product STRING,
    amount DOUBLE
);

-- Insert 2023 data
INSERT INTO sales_2023 VALUES
(1, 'Phone', 5000),
(2, 'Laptop', 8000),
(3, 'Tablet', 3000);

-- Insert 2024 data
INSERT INTO sales_2024 VALUES
(2, 'Laptop', 8000),
(3, 'Tablet', 3000),
(4, 'Watch', 2000);
```

***

## Merge Data

Use `UNION ALL` to merge multiple query results into one result set, preserving all rows (including duplicates). Best performance.

```sql
-- Merge two years of sales data
SELECT customer_id, product, amount FROM sales_2023
UNION ALL
SELECT customer_id, product, amount FROM sales_2024
ORDER BY customer_id;
```

**Result**:

| customer_id | product | amount |
|-------------|---------|--------|
| 1 | Phone | 5000 |
| 2 | Laptop | 8000 |
| 2 | Laptop | 8000 |
| 3 | Tablet | 3000 |
| 3 | Tablet | 3000 |
| 4 | Watch | 2000 |

> **Tip**: `UNION ALL` does not deduplicate and performs better than `UNION`. If data is known to be duplicate-free or deduplication is not needed, prefer `UNION ALL`.

***

## Deduplicated Merge

Use `UNION` to merge result sets and automatically remove duplicate rows.

```sql
-- Merge two years of sales data and deduplicate
SELECT customer_id, product, amount FROM sales_2023
UNION
SELECT customer_id, product, amount FROM sales_2024
ORDER BY customer_id;
```

**Result**:

| customer_id | product | amount |
|-------------|---------|--------|
| 1 | Phone | 5000 |
| 2 | Laptop | 8000 |
| 3 | Tablet | 3000 |
| 4 | Watch | 2000 |

***

## Find Common Data

Use `INTERSECT` to return records that exist in both result sets (intersection).

```sql
-- Find customers and products present in both years
SELECT customer_id, product, amount FROM sales_2023
INTERSECT
SELECT customer_id, product, amount FROM sales_2024
ORDER BY customer_id;
```

**Result**:

| customer_id | product | amount |
|-------------|---------|--------|
| 2 | Laptop | 8000 |
| 3 | Tablet | 3000 |

***

## Find Different Data

Use `EXCEPT` to return records present in the first result set but not in the second (difference).

```sql
-- Find customers in 2023 but not in 2024 (churned customers)
SELECT customer_id, product FROM sales_2023
EXCEPT
SELECT customer_id, product FROM sales_2024
ORDER BY customer_id;
```

**Result**:

| customer_id | product |
|-------------|---------|
| 1 | Phone |

```sql
-- Find newly added customers in 2024
SELECT customer_id, product FROM sales_2024
EXCEPT
SELECT customer_id, product FROM sales_2023
ORDER BY customer_id;
```

**Result**:

| customer_id | product |
|-------------|---------|
| 4 | Watch |

***

## Multi-Table Comparison

Combine set operations for more complex data comparisons.

```sql
-- Find customers appearing in only one year (symmetric difference)
(SELECT customer_id FROM sales_2023
 EXCEPT
 SELECT customer_id FROM sales_2024)
UNION ALL
(SELECT customer_id FROM sales_2024
 EXCEPT
 SELECT customer_id FROM sales_2023)
ORDER BY customer_id;
```

**Result**:

| customer_id |
|-------------|
| 1 |
| 4 |

***

## Clean Up Test Data

After completing set operation verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS sales_2023;
DROP TABLE IF EXISTS sales_2024;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Column Count and Type Matching**: Set operations require both queries to have the same number of columns, with compatible data types for corresponding columns.
2. **Column Names from First Query**: The result set's column names use those from the first `SELECT`.
3. **ORDER BY Position**: `ORDER BY` can only be placed after the last query and applies to the entire result set.
4. **Performance Differences**: `UNION ALL` has the best performance (no deduplication). `UNION` and `INTERSECT` require deduplication. `EXCEPT` requires hash matching. For large data volumes, prefer `UNION ALL` + post-processing.

***

## Related Documentation

* [Set Operations](set-operations.md)
* [SELECT Basic Syntax](query-syntax.md)
