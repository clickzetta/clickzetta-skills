# Lakehouse Data Pivot and Row-Column Transposition Guide

## Overview

Data pivoting and row-column transposition are common requirements in data analysis, used to reshape detail data into wide-table or long-table formats suitable for reporting or further analysis. Singdata Lakehouse supports complete row-column transposition capabilities through standard SQL syntax such as `CASE WHEN`, `UNION ALL`, and `LATERAL VIEW EXPLODE`. This guide categorizes usage by business scenario to help you quickly master data pivot and row-column transposition methods.

### Quick Navigation

* [Row to Column (PIVOT)](#scenario-1-row-to-column-pivot) -- Use CASE WHEN + GROUP BY to expand row data into columns
* [Column to Row (UNPIVOT)](#scenario-2-column-to-row-unpivot) -- Use UNION ALL to merge multiple columns into multiple rows
* [Cross-Tabulation Statistics](#scenario-3-cross-tabulation-statistics) -- Two-dimensional cross-summary matrix
* [Multi-Value Column Expansion](#scenario-4-multi-value-column-expansion) -- Use LATERAL VIEW EXPLODE + SPLIT to expand comma-separated values
* [Post-Aggregation Transposition](#scenario-5-post-aggregation-transposition) -- First GROUP BY aggregate, then transpose to wide table with CASE WHEN

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `CASE WHEN ... END` | Conditional expression | Row to column, cross-tabulation |
| `GROUP BY` | Group aggregation | Summary statistics |
| `UNION ALL` | Merge multiple query results | Column to row |
| `LATERAL VIEW EXPLODE()` | Expand arrays into multiple rows | Multi-value column expansion |
| `SPLIT()` | Split string into array by delimiter | Comma-separated value handling |
| `WITH ... AS (CTE)` | Common Table Expression | Step-by-step aggregation then transposition |
| `SUM() / COUNT()` | Aggregate functions | Pivot calculations |

***

## Prerequisites

The following examples use a simulated sales detail table `doc_pivot_sales`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS doc_pivot_sales (
    sale_id INT,
    region  STRING,
    month   STRING,
    product STRING,
    amount  DOUBLE
);

-- Insert test data (covering East/South/North regions, Jan-Mar 2024, two products, 18 rows total)
INSERT INTO doc_pivot_sales VALUES
(1,  'East', '2024-01', 'ProductA', 1200.00),
(2,  'East', '2024-01', 'ProductB',  800.00),
(3,  'East', '2024-02', 'ProductA', 1500.00),
(4,  'East', '2024-02', 'ProductB',  950.00),
(5,  'East', '2024-03', 'ProductA', 1800.00),
(6,  'East', '2024-03', 'ProductB', 1100.00),
(7,  'South', '2024-01', 'ProductA',  900.00),
(8,  'South', '2024-01', 'ProductB',  600.00),
(9,  'South', '2024-02', 'ProductA', 1100.00),
(10, 'South', '2024-02', 'ProductB',  750.00),
(11, 'South', '2024-03', 'ProductA', 1300.00),
(12, 'South', '2024-03', 'ProductB',  880.00),
(13, 'North', '2024-01', 'ProductA',  700.00),
(14, 'North', '2024-01', 'ProductB',  500.00),
(15, 'North', '2024-02', 'ProductA',  850.00),
(16, 'North', '2024-02', 'ProductB',  620.00),
(17, 'North', '2024-03', 'ProductA', 1000.00),
(18, 'North', '2024-03', 'ProductB',  750.00);
```

***

## Scenario 1: Row to Column (PIVOT)

Convert detail data with months as row dimensions into a wide-table format with one column per month, making it easy to compare sales across months.

```sql
-- Summarize monthly sales by region, turning month rows into columns
SELECT
    region,
    SUM(CASE WHEN month = '2024-01' THEN amount ELSE 0 END) AS jan_amount,
    SUM(CASE WHEN month = '2024-02' THEN amount ELSE 0 END) AS feb_amount,
    SUM(CASE WHEN month = '2024-03' THEN amount ELSE 0 END) AS mar_amount
FROM doc_pivot_sales
GROUP BY region
ORDER BY region;
```

**Execution Result**:

| region | jan_amount | feb_amount | mar_amount |
|--------|-----------|-----------|-----------|
| East   | 2000 | 2450 | 2900 |
| North  | 1200 | 1470 | 1750 |
| South  | 1500 | 1850 | 2180 |

> **Explanation**: `CASE WHEN month = '2024-01' THEN amount ELSE 0 END` checks the month for each row; only matching rows contribute their amount, others contribute 0. `SUM` aggregates all rows for the same region, leaving one row per region with month information now as columns.

***

## Scenario 2: Column to Row (UNPIVOT)

Convert multiple quarter columns (`q1_amount`, `q2_amount`, `q3_amount`, `q4_amount`) in a wide table into a long-table format with `quarter` + `amount` columns, easier for unified processing or line chart plotting.

First, create wide-table sample data:

```sql
-- Create wide table (one row per region, four quarter columns)
CREATE TABLE IF NOT EXISTS doc_pivot_wide (
    region    STRING,
    q1_amount DOUBLE,
    q2_amount DOUBLE,
    q3_amount DOUBLE,
    q4_amount DOUBLE
);

INSERT INTO doc_pivot_wide VALUES
('East',  2000, 2450, 2900, 3100),
('South', 1500, 1850, 2180, 2400),
('North', 1200, 1470, 1750, 1900);
```

Use `UNION ALL` to expand four columns into multiple rows:

```sql
-- Column to row: merge q1~q4 columns into quarter + amount columns
SELECT region, 'Q1' AS quarter, q1_amount AS amount FROM doc_pivot_wide
UNION ALL
SELECT region, 'Q2',            q2_amount             FROM doc_pivot_wide
UNION ALL
SELECT region, 'Q3',            q3_amount             FROM doc_pivot_wide
UNION ALL
SELECT region, 'Q4',            q4_amount             FROM doc_pivot_wide
ORDER BY region, quarter;
```

**Execution Result**:

| region | quarter | amount |
|--------|---------|--------|
| East   | Q1 | 2000 |
| East   | Q2 | 2450 |
| East   | Q3 | 2900 |
| East   | Q4 | 3100 |
| North  | Q1 | 1200 |
| North  | Q2 | 1470 |
| North  | Q3 | 1750 |
| North  | Q4 | 1900 |
| South  | Q1 | 1500 |
| South  | Q2 | 1850 |
| South  | Q3 | 2180 |
| South  | Q4 | 2400 |

> **Explanation**: Each `SELECT` clause corresponds to one column, and `UNION ALL` vertically concatenates the results. More columns mean more `UNION ALL` clauses, but the logic is clear and easy to maintain.

***

## Scenario 3: Cross-Tabulation Statistics

Summarize sales for each month by region, forming a month x region two-dimensional matrix suitable for cross-tab reports.

```sql
-- Month x Region cross-tab: one row per month, one column per region
SELECT
    month,
    SUM(CASE WHEN region = 'East'  THEN amount ELSE 0 END) AS east_amount,
    SUM(CASE WHEN region = 'South' THEN amount ELSE 0 END) AS south_amount,
    SUM(CASE WHEN region = 'North' THEN amount ELSE 0 END) AS north_amount,
    SUM(amount)                                             AS total_amount
FROM doc_pivot_sales
GROUP BY month
ORDER BY month;
```

**Execution Result**:

| month   | east_amount | south_amount | north_amount | total_amount |
|---------|------------|-------------|-------------|-------------|
| 2024-01 | 2000 | 1500 | 1200 | 4700 |
| 2024-02 | 2450 | 1850 | 1470 | 5770 |
| 2024-03 | 2900 | 2180 | 1750 | 6830 |

You can also create a region x product cross-tab showing sales for both products per region with totals:

```sql
-- Region x Product cross-tab: one row per region, one column per product
SELECT
    region,
    SUM(CASE WHEN product = 'ProductA' THEN amount ELSE 0 END) AS product_a_total,
    SUM(CASE WHEN product = 'ProductB' THEN amount ELSE 0 END) AS product_b_total,
    SUM(amount)                                                AS grand_total
FROM doc_pivot_sales
GROUP BY region
ORDER BY region;
```

**Execution Result**:

| region | product_a_total | product_b_total | grand_total |
|--------|----------------|----------------|------------|
| East   | 4500 | 2850 | 7350 |
| North  | 2550 | 1870 | 4420 |
| South  | 3300 | 2230 | 5530 |

> **Explanation**: Cross-tabulation is essentially an extension of row-to-column transposition, where columns are constructed by enumerating dimension values in `CASE WHEN`. When dimension values are numerous, first run `SELECT DISTINCT` to discover all values, then dynamically construct the SQL.

***

## Scenario 4: Multi-Value Column Expansion

When a column stores multiple comma-separated values (e.g., tags, product lists), expand each value into an independent row for statistical analysis.

First, create a sample table with multi-value columns:

```sql
-- Create order tags table (tags column stores comma-separated product tags)
CREATE TABLE IF NOT EXISTS doc_pivot_tags (
    order_id INT,
    region   STRING,
    tags     STRING
);

INSERT INTO doc_pivot_tags VALUES
(1, 'East',  'ProductA,ProductB'),
(2, 'South', 'ProductA'),
(3, 'North', 'ProductB,ProductC'),
(4, 'East',  'ProductA,ProductC'),
(5, 'South', 'ProductB,ProductC');
```

Use `LATERAL VIEW EXPLODE` with `SPLIT` to expand the multi-value column:

```sql
-- Split the tags column by comma, expanding each tag into an independent row
SELECT
    order_id,
    region,
    tag
FROM doc_pivot_tags
LATERAL VIEW EXPLODE(SPLIT(tags, ',')) t AS tag
ORDER BY order_id, tag;
```

**Execution Result**:

| order_id | region | tag    |
|----------|--------|--------|
| 1 | East   | ProductA |
| 1 | East   | ProductB |
| 2 | South  | ProductA |
| 3 | North  | ProductB |
| 3 | North  | ProductC |
| 4 | East   | ProductA |
| 4 | East   | ProductC |
| 5 | South  | ProductB |
| 5 | South  | ProductC |

After expansion, you can directly perform aggregate statistics, e.g., counting how many orders each product appears in:

```sql
-- After expansion, count orders per product
SELECT
    tag        AS product,
    COUNT(*)   AS order_count
FROM doc_pivot_tags
LATERAL VIEW EXPLODE(SPLIT(tags, ',')) t AS tag
GROUP BY tag
ORDER BY tag;
```

**Execution Result**:

| product  | order_count |
|----------|------------|
| ProductA | 3 |
| ProductB | 3 |
| ProductC | 3 |

> **Explanation**: `SPLIT(tags, ',')` splits the string into an array by comma, `EXPLODE` expands the array into rows, and `LATERAL VIEW` associates the expanded results with other columns from the original table. The number of rows after expansion equals the total number of tags across all rows.

***

## Scenario 5: Post-Aggregation Transposition

First group and aggregate by region and month, then transpose the aggregated results into a wide-table format with a total column. This two-step approach keeps SQL clear when aggregation logic is complex.

```sql
-- Step 1: Aggregate by region and month; Step 2: Transpose month columns to wide table
WITH monthly_summary AS (
    SELECT
        region,
        month,
        SUM(amount) AS total_amount
    FROM doc_pivot_sales
    GROUP BY region, month
)
SELECT
    region,
    ROUND(SUM(CASE WHEN month = '2024-01' THEN total_amount ELSE 0 END), 2) AS m1,
    ROUND(SUM(CASE WHEN month = '2024-02' THEN total_amount ELSE 0 END), 2) AS m2,
    ROUND(SUM(CASE WHEN month = '2024-03' THEN total_amount ELSE 0 END), 2) AS m3,
    ROUND(SUM(total_amount), 2)                                              AS total
FROM monthly_summary
GROUP BY region
ORDER BY region;
```

**Execution Result**:

| region | m1   | m2   | m3   | total |
|--------|------|------|------|-------|
| East   | 2000 | 2450 | 2900 | 7350 |
| North  | 1200 | 1470 | 1750 | 4420 |
| South  | 1500 | 1850 | 2180 | 5530 |

> **Explanation**: CTE (`WITH ... AS`) separates the aggregation logic from the transposition logic, making the SQL more readable. The outer query only needs to apply `CASE WHEN` transposition to the CTE result without repeating aggregation conditions.

***

## Clean Up Test Data

After completing data pivot verification, it is recommended to clean up test tables:

```sql
DROP TABLE IF EXISTS doc_pivot_sales;
DROP TABLE IF EXISTS doc_pivot_wide;
DROP TABLE IF EXISTS doc_pivot_tags;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Column Values Must Be Enumerated in Advance**: `CASE WHEN` row-to-column transposition requires knowing all column values when writing the SQL (e.g., months, regions). If column values change dynamically, construct SQL dynamically at the application layer, or first use `GROUP_CONCAT` to discover all values and then build the query.
2. **ELSE 0 vs ELSE NULL**: With `CASE WHEN ... ELSE 0 END` paired with `SUM`, non-matching rows contribute 0 and the result contains no NULLs. With `ELSE NULL`, `SUM` ignores NULLs (same result), but `AVG` would differ due to different denominators -- choose based on business semantics.
3. **UNION ALL Column Count and Types Must Match**: When doing column-to-row, each `SELECT` clause must have the same number of columns and corresponding data types, otherwise an error occurs.
4. **LATERAL VIEW and WHERE Execution Order**: `LATERAL VIEW` executes at the `FROM` stage, `WHERE` filters after it. To filter original rows before expansion, put conditions in a subquery. To filter expanded results, put conditions in the outer `WHERE`.
5. **SPLIT Results May Contain Empty Strings**: If the original data has trailing commas (e.g., `"ProductA,"`), `SPLIT` produces empty string elements. Filter them with `WHERE tag != ''` after expansion.
6. **Performance Considerations**: More `CASE WHEN` expressions in row-to-column means more column scans, impacting wide-table performance. When columns exceed 50, consider using `MAP_AGG` or application-layer processing.

***

## Related Documentation

* [GROUP BY Clause](groupby.md)
* [LATERAL VIEW](LATERALVIEW.md)
* [Window Functions](WINDOWFUNCTION.md)
* [String Functions](string_function.md)
