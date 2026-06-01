# Lakehouse Ranking and Percentile Analysis Guide

## Overview

Ranking and percentile analysis are advanced scenarios in data analysis, used to compute the relative position of data within groups, percentile scores, and more. Singdata Lakehouse provides comprehensive window function support, including ranking functions, offset functions, and aggregate window functions. This guide categorizes usage by business scenario to help you quickly master efficient ranking and percentile analysis methods.

### Quick Navigation

* [Basic Ranking](#basic-ranking) -- Use ROW_NUMBER / RANK / DENSE_RANK to compute rankings
* [Percentile Ranking](#percentile-ranking) -- Use PERCENT_RANK to compute relative position
* [Before/After Row Comparison](#beforeafter-row-comparison) -- Use LAG / LEAD for period-over-period comparison
* [Moving Average](#moving-average) -- Use window frames for sliding statistics
* [Quantile Calculation](#quantile-calculation) -- Use PERCENTILE to compute median and quartiles

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `ROW_NUMBER()` | Generate unique row numbers | Deduplication, pagination, Top-N |
| `RANK()` | Ranking (ties skip numbers) | Score ranking, competition ranking |
| `DENSE_RANK()` | Ranking (ties don't skip numbers) | Continuous ranking |
| `PERCENT_RANK()` | Percentile ranking | Relative position analysis |
| `LAG()` / `LEAD()` | Access previous/next row data | Period-over-period, year-over-year |
| `AVG() OVER (... ROWS BETWEEN)` | Moving average | Trend analysis |
| `PERCENTILE()` | Quantile calculation | Median, quartiles |

***

## Prerequisites

The following examples use a simulated employee performance table `performance`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS performance (
    emp_id INT,
    emp_name STRING,
    dept STRING,
    score DOUBLE,
    review_date DATE
);

-- Insert test data
INSERT INTO performance VALUES
(1, 'Alice', 'Engineering', 95, '2024-06-01'),
(2, 'Bob', 'Engineering', 85, '2024-06-01'),
(3, 'Carol', 'Engineering', 95, '2024-06-01'),
(4, 'David', 'Marketing', 88, '2024-06-01'),
(5, 'Eve', 'Marketing', 92, '2024-06-01'),
(6, 'Frank', 'Marketing', 78, '2024-06-01'),
(7, 'Grace', 'HR', 90, '2024-06-01'),
(8, 'Henry', 'HR', 85, '2024-06-01');
```

***

## Basic Ranking

Use ranking functions to compute employee performance rankings within departments. Lakehouse provides three ranking functions with slightly different behaviors.

```sql
-- Comparison of three ranking functions
SELECT 
    emp_name,
    dept,
    score,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY score DESC) as row_num,
    RANK() OVER (PARTITION BY dept ORDER BY score DESC) as rank,
    DENSE_RANK() OVER (PARTITION BY dept ORDER BY score DESC) as dense_rank
FROM performance
ORDER BY dept, row_num;
```

**Result**:

| emp_name | dept | score | row_num | rank | dense_rank |
|----------|------|-------|---------|------|------------|
| Alice | Engineering | 95 | 1 | 1 | 1 |
| Carol | Engineering | 95 | 2 | 1 | 1 |
| Bob | Engineering | 85 | 3 | 3 | 2 |
| Eve | Marketing | 92 | 1 | 1 | 1 |
| David | Marketing | 88 | 2 | 2 | 2 |
| Frank | Marketing | 78 | 3 | 3 | 3 |
| Grace | HR | 90 | 1 | 1 | 1 |
| Henry | HR | 85 | 2 | 2 | 2 |

### Differences Between Ranking Functions

| Function | Tie Handling | Number Continuity |
|------|---------|-----------|
| `ROW_NUMBER()` | Randomly assigns different numbers | Continuous |
| `RANK()` | Same rank for ties, subsequent numbers skip | Discontinuous (1,1,3) |
| `DENSE_RANK()` | Same rank for ties, subsequent numbers are continuous | Continuous (1,1,2) |

***

## Percentile Ranking

Use `PERCENT_RANK()` to compute an employee's relative position within the department (between 0 and 1).

```sql
-- Compute percentile ranking
SELECT 
    emp_name,
    dept,
    score,
    ROUND(PERCENT_RANK() OVER (PARTITION BY dept ORDER BY score DESC), 2) as pct_rank
FROM performance
ORDER BY dept, pct_rank DESC;
```

**Result**:

| emp_name | dept | score | pct_rank |
|----------|------|-------|----------|
| Alice | Engineering | 95 | 0 |
| Carol | Engineering | 95 | 0 |
| Bob | Engineering | 85 | 0.5 |
| Eve | Marketing | 92 | 0 |
| David | Marketing | 88 | 0.5 |
| Frank | Marketing | 78 | 1 |
| Grace | HR | 90 | 0 |
| Henry | HR | 85 | 1 |

> 💡 **Tip**: A smaller `PERCENT_RANK` value indicates a higher ranking (0 is the top rank).

***

## Before/After Row Comparison

Use `LAG()` and `LEAD()` to access the previous or next row's data relative to the current row, commonly used for period-over-period change calculations.

```sql
-- Compute score differences between employees within departments
SELECT 
    emp_name,
    dept,
    score,
    LAG(score, 1) OVER (PARTITION BY dept ORDER BY score DESC) as prev_score,
    score - LAG(score, 1) OVER (PARTITION BY dept ORDER BY score DESC) as diff
FROM performance
ORDER BY dept, score DESC;
```

**Result**:

| emp_name | dept | score | prev_score | diff |
|----------|------|-------|------------|------|
| Alice | Engineering | 95 | NULL | NULL |
| Carol | Engineering | 95 | 95 | 0 |
| Bob | Engineering | 85 | 95 | -10 |
| Eve | Marketing | 92 | NULL | NULL |
| David | Marketing | 88 | 92 | -4 |
| Frank | Marketing | 78 | 88 | -10 |
| Grace | HR | 90 | NULL | NULL |
| Henry | HR | 85 | 90 | -5 |

> ⚠️ **Note**: The first row's `LAG` returns `NULL`, which may display as `nan` for numeric values, but `IS NULL` checks remain valid.

***

## Moving Average

Use window frames (ROWS BETWEEN) to compute sliding window statistics, suitable for trend analysis.

```sql
-- Compute moving average within department ordered by score (current row and two preceding rows)
SELECT 
    emp_name,
    dept,
    score,
    ROUND(AVG(score) OVER (
        PARTITION BY dept 
        ORDER BY score DESC 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) as moving_avg_3
FROM performance
ORDER BY dept, score DESC;
```

**Result**:

| emp_name | dept | score | moving_avg_3 |
|----------|------|-------|--------------|
| Alice | Engineering | 95 | 95 |
| Carol | Engineering | 95 | 95 |
| Bob | Engineering | 85 | 91.7 |
| Eve | Marketing | 92 | 92 |
| David | Marketing | 88 | 90 |
| Frank | Marketing | 78 | 86 |
| Grace | HR | 90 | 90 |
| Henry | HR | 85 | 87.5 |

***

## Quantile Calculation

Use the `PERCENTILE()` function to compute data quantiles such as the median (0.5) and quartiles (0.25, 0.75).

```sql
-- Compute median and quartiles of scores by department
SELECT 
    dept,
    PERCENTILE(score, 0.5) as median,
    PERCENTILE(score, 0.25) as q1,
    PERCENTILE(score, 0.75) as q3,
    MIN(score) as min_score,
    MAX(score) as max_score
FROM performance
GROUP BY dept
ORDER BY dept;
```

**Result**:

| dept | median | q1 | q3 | min_score | max_score |
|------|--------|----|----|-----------|-----------|
| Engineering | 95 | 90 | 95 | 85 | 95 |
| HR | 87.5 | 86.25 | 88.75 | 85 | 90 |
| Marketing | 88 | 83 | 90 | 78 | 92 |

> 💡 **Tip**: The `PERCENTILE` function supports passing an array parameter to compute multiple quantiles at once, e.g., `PERCENTILE(score, ARRAY(0.25, 0.5, 0.75))`.

***

## Clean Up Test Data

After completing ranking analysis verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS performance;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Window Function Execution Order**: Window functions execute after `WHERE` and `GROUP BY`; window function results cannot be used directly in `WHERE`. Use `QUALIFY` or subqueries to filter.
2. **NULL Value Sorting**: `ORDER BY` places `NULL` values last (DESC) or first (ASC) by default; use `NULLS FIRST/LAST` to control.
3. **Performance Optimization**: Choose `PARTITION BY` columns with moderate cardinality to avoid individual partitions becoming too large.
4. **PERCENT_RANK Syntax**: `PERCENT_RANK()` does not accept arguments; write `PERCENT_RANK() OVER (...)` directly.

***

## Related Documentation

* [Window Functions](windowfunction.md)
* [QUALIFY Clause](sql-qualify.md)
* [GROUP BY Clause](groupby.md)
