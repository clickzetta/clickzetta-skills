# Lakehouse Data Grouping and Aggregation Guide

## Overview

Data grouping and aggregation is a core operation in data analysis, used to group data by dimensions and compute statistical metrics. Singdata Lakehouse provides comprehensive aggregate function support, including basic aggregation, conditional aggregation, and approximate aggregation. This guide categorizes usage by business scenario to help you quickly master efficient data aggregation methods.

### Quick Navigation

* [Basic Grouping and Aggregation](#basic-grouping-and-aggregation) -- Use GROUP BY to compute departmental statistics
* [Filter Aggregation Results](#filter-aggregation-results) -- Use HAVING to filter groups
* [Conditional Aggregation](#conditional-aggregation) -- Use CASE WHEN + aggregate functions for conditional statistics
* [Distinct Count](#distinct-count) -- Use COUNT(DISTINCT) to count unique values
* [Approximate Aggregation](#approximate-aggregation) -- Use APPROX_COUNT_DISTINCT to accelerate large-volume statistics

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `GROUP BY` | Group by column | Dimensional aggregation analysis |
| `COUNT(*)` / `COUNT(col)` | Count | Count rows or non-null values |
| `SUM()` / `AVG()` / `MIN()` / `MAX()` | Numeric aggregation | Sum, average, min/max |
| `HAVING` | Filter grouped results | Substitute for WHERE on aggregated data |
| `COUNT(DISTINCT col)` | Distinct count | Count unique values |
| `APPROX_COUNT_DISTINCT()` | Approximate distinct count | Fast estimation for large data volumes |

***

## Prerequisites

The following examples use a simulated sales table `sales`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT,
    region STRING,
    product STRING,
    amount DOUBLE,
    quantity INT,
    sale_date DATE
);

-- Insert test data
INSERT INTO sales VALUES
(1, 'East', 'Phone', 5000, 10, '2024-06-01'),
(2, 'East', 'Laptop', 8000, 5, '2024-06-01'),
(3, 'West', 'Phone', 4500, 9, '2024-06-02'),
(4, 'West', 'Tablet', 3000, 8, '2024-06-02'),
(5, 'East', 'Phone', 5000, 10, '2024-06-03'),
(6, 'South', 'Laptop', 8000, 5, '2024-06-03'),
(7, 'South', 'Tablet', 3000, 8, '2024-06-04');
```

***

## Basic Grouping and Aggregation

Group by dimension and compute aggregate metrics -- the most common data analysis operation.

```sql
-- Compute sales and order count by region
SELECT 
    region,
    COUNT(*) as order_count,
    SUM(amount) as total_sales,
    AVG(amount) as avg_sales
FROM sales
GROUP BY region
ORDER BY total_sales DESC;
```

**Result**:

| region | order_count | total_sales | avg_sales |
|--------|-------------|-------------|-----------|
| East | 3 | 18000 | 6000 |
| West | 2 | 7500 | 3750 |
| South | 2 | 11000 | 5500 |

> ⚠️ **Note**: Columns in `SELECT` that are not wrapped in aggregate functions must be included in `GROUP BY`.

***

## Filter Aggregation Results

Use the `HAVING` clause to filter results after grouping, replacing aggregate conditions that cannot be used in `WHERE`.

```sql
-- Query regions with total sales greater than 10000
SELECT 
    region,
    SUM(amount) as total_sales
FROM sales
GROUP BY region
HAVING SUM(amount) > 10000
ORDER BY total_sales DESC;
```

**Result**:

| region | total_sales |
|--------|-------------|
| East | 18000 |
| South | 11000 |

### Difference Between WHERE and HAVING

* `WHERE` filters rows before grouping and cannot use aggregate functions.
* `HAVING` filters groups after grouping and can use aggregate functions.

```sql
-- Correct: filter date first, then group
SELECT region, SUM(amount) as total_sales
FROM sales
WHERE sale_date >= '2024-06-02'
GROUP BY region
HAVING SUM(amount) > 5000;
```

***

## Conditional Aggregation

Use `CASE WHEN` with aggregate functions to implement conditional statistics, avoiding multiple table scans.

```sql
-- Compute sales for each product type by region
SELECT 
    region,
    SUM(CASE WHEN product = 'Phone' THEN amount ELSE 0 END) as phone_sales,
    SUM(CASE WHEN product = 'Laptop' THEN amount ELSE 0 END) as laptop_sales,
    SUM(CASE WHEN product = 'Tablet' THEN amount ELSE 0 END) as tablet_sales,
    SUM(amount) as total_sales
FROM sales
GROUP BY region
ORDER BY region;
```

**Result**:

| region | phone_sales | laptop_sales | tablet_sales | total_sales |
|--------|-------------|--------------|--------------|-------------|
| East | 10000 | 8000 | 0 | 18000 |
| South | 0 | 8000 | 3000 | 11000 |
| West | 4500 | 0 | 3000 | 7500 |

> 💡 **Tip**: Conditional aggregation is more efficient than multiple `SELECT` + `UNION` queries and is recommended for row-to-column transposition scenarios.

***

## Distinct Count

Use `COUNT(DISTINCT col)` to count unique values.

```sql
-- Count distinct product types sold in each region
SELECT 
    region,
    COUNT(DISTINCT product) as unique_products,
    SUM(quantity) as total_quantity
FROM sales
GROUP BY region
ORDER BY unique_products DESC;
```

**Result**:

| region | unique_products | total_quantity |
|--------|-----------------|----------------|
| East | 2 | 25 |
| South | 2 | 13 |
| West | 2 | 17 |

***

## Approximate Aggregation

When data volumes are very large, exact distinct counts can be slow. Lakehouse provides approximate aggregate functions that significantly improve performance within an acceptable error range.

```sql
-- Use approximate distinct count (suitable for tens of millions of rows and above)
SELECT 
    region,
    APPROX_COUNT_DISTINCT(product) as approx_unique_products,
    COUNT(DISTINCT product) as exact_unique_products
FROM sales
GROUP BY region;
```

**Result**:

| region | approx_unique_products | exact_unique_products |
|--------|------------------------|-----------------------|
| East | 2 | 2 |
| South | 2 | 2 |
| West | 2 | 2 |

> 💡 **Tip**: `APPROX_COUNT_DISTINCT` is based on the HyperLogLog algorithm, with typical error within 1%-2%, suitable for fast estimation on large data volumes.

***

## Clean Up Test Data

After completing aggregation verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS sales;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **GROUP BY Position**: Column positions can be used in `GROUP BY` (e.g., `GROUP BY 1`), but using column names is recommended for readability.
2. **NULL Value Handling**: `COUNT(col)` does not count NULL values; `COUNT(*)` counts all rows. `GROUP BY` groups NULL values into one group.
3. **Performance Optimization**: Filter with `WHERE` before `GROUP BY` to significantly reduce aggregation computation.
4. **Approximate Function Applicability**: When data exceeds millions of rows and precision requirements are moderate, prefer the `APPROX_*` function family.

***

## Related Documentation

* [SELECT Basic Syntax](query-syntax.md)
* [GROUP BY Clause](groupby.md)
* [Aggregate Functions](agg_function.md)
