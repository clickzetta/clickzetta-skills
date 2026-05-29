# Window Function

## Overview

Window Functions are a powerful analytical feature in Singdata Lakehouse SQL that allow you to perform calculations across a set of related rows, rather than just on individual rows. By using the WINDOW clause, you can define one or more named windows and then reference those windows in window functions, avoiding repetitive window specifications and making queries more concise and maintainable.

## Syntax

```sql
WINDOW <window_name> AS (<window_specification>, ...)
```

### Parameter Description

* **window\_name**: The name of the window, which must be a valid identifier and must not conflict with table or column names
* **window\_specification**: The window specification, defining the scope and ordering of the window, consisting of:
  * `PARTITION BY`: Specifies how data is grouped; each group is a partition
  * `ORDER BY`: Specifies how data within each partition is ordered
  * `frame_clause`: Specifies the window frame, limiting the computation range of the window function

### Window Frame Types

1. **ROWS Frame**: Window frame based on row count
2. **RANGE Frame**: Window frame based on value range

## Environment Preparation

### Create Test Table

```sql
CREATE TABLE IF NOT EXISTS sales(
    month INT,
    sales INT,
    profit DOUBLE
);
```

### Insert Test Data

```sql
INSERT INTO sales (month, sales, profit) VALUES
(1, 100, 0.1),
(2, 120, 0.15),
(3, 80, 0.05),
(4, 150, 0.2),
(5, 90, 0.1),
(6, 110, 0.12);
```

## Usage Examples

### Example 1: Moving Window Aggregation - Moving Sum and Moving Average

**Business Scenario**: Calculate the sum and average of sales for the current month and the two preceding months

```sql
SELECT month, sales, 
       SUM(sales) OVER w AS sum_sales, 
       AVG(sales) OVER w AS avg_sales
FROM sales
WINDOW w AS (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW);
```

**Execution Result**:

```
+-------+-------+-----------+--------------------+
| month | sales | sum_sales | avg_sales          |
+-------+-------+-----------+--------------------+
| 1     | 100   | 100       | 100.0              |
| 2     | 120   | 220       | 110.0              |
| 3     | 80    | 300       | 100.0              |
| 4     | 150   | 350       | 116.67             |
| 5     | 90    | 320       | 106.67             |
| 6     | 110   | 350       | 116.67             |
+-------+-------+-----------+--------------------+
```

**Explanation**: Window w defines a sliding window containing the current row and the 2 preceding rows, so each row computes the sum and average of the most recent 3 months of sales.

***

### Example 2: Multi-Window Ranking - Quarterly and Annual Ranking

**Business Scenario**: Simultaneously compute ranking within each quarter and across the full year

```sql
SELECT month, sales, 
       RANK() OVER w1 AS rank_quarter, 
       ROW_NUMBER() OVER w2 AS rank_year
FROM sales
WINDOW w1 AS (PARTITION BY CEIL(month / 3) ORDER BY sales DESC),
       w2 AS (ORDER BY sales DESC);
```

**Execution Result**:

```
+-------+-------+--------------+-----------+
| month | sales | rank_quarter | rank_year |
+-------+-------+--------------+-----------+
| 4     | 150   | 1            | 1         |
| 2     | 120   | 1            | 2         |
| 6     | 110   | 2            | 3         |
| 1     | 100   | 2            | 4         |
| 5     | 90    | 3            | 5         |
| 3     | 80    | 3            | 6         |
+-------+-------+--------------+-----------+
```

**Explanation**:

* The w1 window partitions by quarter (every 3 months), computing sales ranking within each quarter
* The w2 window has no partition, computing sales ranking across the full year
* CEIL(month/3) divides months into Q1 (months 1-3), Q2 (months 4-6), etc.

***

### Example 3: Cumulative Aggregation - Year-to-Date Statistics

**Business Scenario**: Calculate cumulative sales and average profit margin from the beginning of the year to the current month

```sql
SELECT month, sales, profit,
       SUM(sales) OVER w AS cumulative_sales,
       AVG(profit) OVER w AS avg_profit,
       MAX(sales) OVER w AS max_sales,
       MIN(sales) OVER w AS min_sales
FROM sales
WINDOW w AS (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW);
```

**Execution Result**:

```
+-------+-------+--------+------------------+------------+-----------+-----------+
| month | sales | profit | cumulative_sales | avg_profit | max_sales | min_sales |
+-------+-------+--------+------------------+------------+-----------+-----------+
| 1     | 100   | 0.1    | 100              | 0.1        | 100       | 100       |
| 2     | 120   | 0.15   | 220              | 0.125      | 120       | 100       |
| 3     | 80    | 0.05   | 300              | 0.1        | 120       | 80        |
| 4     | 150   | 0.2    | 450              | 0.125      | 150       | 80        |
| 5     | 90    | 0.1    | 540              | 0.12       | 150       | 80        |
| 6     | 110   | 0.12   | 650              | 0.12       | 150       | 80        |
+-------+-------+--------+------------------+------------+-----------+-----------+
```

**Explanation**: `UNBOUNDED PRECEDING` starts from the first row of the partition, and `CURRENT ROW` ends at the current row, achieving cumulative computation.

***

### Example 4: Time Series Analysis - Period-over-Period Comparison

**Business Scenario**: View each month's sales compared to the previous and next month, and the period-over-period change

```sql
SELECT month, sales,
       LAG(sales, 1) OVER w AS prev_sales,
       LEAD(sales, 1) OVER w AS next_sales,
       sales - LAG(sales, 1) OVER w AS sales_change
FROM sales
WINDOW w AS (ORDER BY month);
```

**Execution Result**:

```
+-------+-------+------------+------------+--------------+
| month | sales | prev_sales | next_sales | sales_change |
+-------+-------+------------+------------+--------------+
| 1     | 100   | NULL       | 120        | NULL         |
| 2     | 120   | 100        | 80         | 20           |
| 3     | 80    | 120        | 150        | -40          |
| 4     | 150   | 80         | 90         | 70           |
| 5     | 90    | 150        | 110        | -60          |
| 6     | 110   | 90         | NULL       | 20           |
+-------+-------+------------+------------+--------------+
```

**Explanation**:

* `LAG(sales, 1)`: Gets the sales from the previous row
* `LEAD(sales, 1)`: Gets the sales from the next row
* prev\_sales and next\_sales are NULL for the first and last rows, respectively

***

### Example 5: Comparison of Different Ranking Functions

**Business Scenario**: Understand the differences between various ranking functions

```sql
SELECT month, sales,
       DENSE_RANK() OVER w AS dense_rank,
       RANK() OVER w AS rank,
       ROW_NUMBER() OVER w AS row_num,
       PERCENT_RANK() OVER w AS percent_rank
FROM sales
WINDOW w AS (ORDER BY sales DESC);
```

**Execution Result**:

```
+-------+-------+------------+------+---------+--------------+
| month | sales | dense_rank | rank | row_num | percent_rank |
+-------+-------+------------+------+---------+--------------+
| 4     | 150   | 1          | 1    | 1       | 0.0          |
| 2     | 120   | 2          | 2    | 2       | 0.2          |
| 6     | 110   | 3          | 3    | 3       | 0.4          |
| 1     | 100   | 4          | 4    | 4       | 0.6          |
| 5     | 90    | 5          | 5    | 5       | 0.8          |
| 3     | 80    | 6          | 6    | 6       | 1.0          |
+-------+-------+------------+------+---------+--------------+
```

**Ranking Function Descriptions**:

* `ROW_NUMBER()`: Unique sequential row numbers; rows with the same value do not tie
* `RANK()`: Same value gets the same rank; the next rank skips
* `DENSE_RANK()`: Same value gets the same rank; the next rank is consecutive
* `PERCENT_RANK()`: Returns a percentile rank between 0 and 1

***

### Example 6: Position Functions - Accessing Values at Specific Positions

**Business Scenario**: Get the first, last, and nth values within the window

```sql
SELECT month, sales, profit,
       FIRST_VALUE(sales) OVER w AS first_sales,
       LAST_VALUE(sales) OVER w AS last_sales,
       NTH_VALUE(sales, 2) OVER w AS second_sales
FROM sales
WINDOW w AS (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING);
```

**Execution Result**:

```
+-------+-------+--------+-------------+------------+--------------+
| month | sales | profit | first_sales | last_sales | second_sales |
+-------+-------+--------+-------------+------------+--------------+
| 1     | 100   | 0.1    | 100         | 110        | 120          |
| 2     | 120   | 0.15   | 100         | 110        | 120          |
| 3     | 80    | 0.05   | 100         | 110        | 120          |
| 4     | 150   | 0.2    | 100         | 110        | 120          |
| 5     | 90    | 0.1    | 100         | 110        | 120          |
| 6     | 110   | 0.12   | 100         | 110        | 120          |
+-------+-------+--------+-------------+------------+--------------+
```

**Explanation**:

* `FIRST_VALUE()`: Returns the value of the first row in the window
* `LAST_VALUE()`: Returns the value of the last row in the window (requires UNBOUNDED FOLLOWING to see the actual last row)
* `NTH_VALUE(expr, n)`: Returns the value of the nth row in the window

***

### Example 7: RANGE Window Frame - Value-Range-Based Windows

**Business Scenario**: Find all records within a sales value range of +/-10 and compute statistics

```sql
SELECT month, sales,
       SUM(sales) OVER w AS range_sum,
       COUNT(*) OVER w AS range_count
FROM sales
WINDOW w AS (ORDER BY sales RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING);
```

**Execution Result**:

```
+-------+-------+-----------+-------------+
| month | sales | range_sum | range_count |
+-------+-------+-----------+-------------+
| 3     | 80    | 170       | 2           |
| 5     | 90    | 270       | 3           |
| 1     | 100   | 300       | 3           |
| 6     | 110   | 330       | 3           |
| 2     | 120   | 230       | 2           |
| 4     | 150   | 150       | 1           |
+-------+-------+-----------+-------------+
```

**Explanation**:

* RANGE windows are based on value ranges rather than row counts
* For the row with sales=100, the window includes all rows with sales values in the range [90, 110]
* For the row with sales=150, only itself falls within the range [140, 160]

***

### Example 8: Comprehensive Analysis - Multi-Dimensional Business Reports (Advanced)

**Business Scenario**: Generate a comprehensive analytical report including ranking, cumulative values, period-over-period comparison, and proportions

```sql
SELECT 
    month,
    sales,
    -- Ranking related
    ROW_NUMBER() OVER w1 AS row_num,
    RANK() OVER w1 AS sales_rank,
    -- Cumulative statistics
    SUM(sales) OVER w2 AS ytd_sales,
    AVG(sales) OVER w2 AS ytd_avg,
    -- Period-over-period comparison
    LAG(sales) OVER w1 AS prev_month_sales,
    sales - LAG(sales) OVER w1 AS mom_change,
    -- Proportion analysis
    ROUND(sales * 100.0 / SUM(sales) OVER w3, 2) AS pct_of_total
FROM sales
WINDOW 
    w1 AS (ORDER BY month),
    w2 AS (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
    w3 AS (ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING);
```

**Execution Result**:

```
+-------+-------+---------+------------+-----------+---------+------------------+------------+---------------+
| month | sales | row_num | sales_rank | ytd_sales | ytd_avg | prev_month_sales | mom_change | pct_of_total  |
+-------+-------+---------+------------+-----------+---------+------------------+------------+---------------+
| 1     | 100   | 1       | 1          | 100       | 100.0   | NULL             | NULL       | 15.38         |
| 2     | 120   | 2       | 2          | 220       | 110.0   | 100              | 20         | 18.46         |
| 3     | 80    | 3       | 3          | 300       | 100.0   | 120              | -40        | 12.31         |
| 4     | 150   | 4       | 4          | 450       | 112.5   | 80               | 70         | 23.08         |
| 5     | 90    | 5       | 5          | 540       | 108.0   | 150              | -60        | 13.85         |
| 6     | 110   | 6       | 6          | 650       | 108.33  | 90               | 20         | 16.92         |
+-------+-------+---------+------------+-----------+---------+------------------+------------+---------------+
```

**Explanation**:

* This example uses 3 different window definitions simultaneously
* w1: Ordered by month, used for ranking and period-over-period comparison
* w2: Cumulative window, used for YTD (Year-To-Date) calculations
* w3: Full window, used for computing total sum and calculating proportions
* Demonstrates how to achieve complex multi-dimensional analysis in a single query

***

### Example 9: Data Bucketing - NTILE Function Application

**Business Scenario**: Divide sales data into high, medium, and low tiers based on performance

```sql
SELECT 
    month,
    sales,
    NTILE(3) OVER w AS sales_tier,
    CASE 
        WHEN NTILE(3) OVER w = 1 THEN 'High'
        WHEN NTILE(3) OVER w = 2 THEN 'Medium'  
        ELSE 'Low'
    END AS tier_label
FROM sales
WINDOW w AS (ORDER BY sales DESC);
```

**Execution Result**:

```
+-------+-------+------------+------------+
| month | sales | sales_tier | tier_label |
+-------+-------+------------+------------+
| 4     | 150   | 1          | High       |
| 2     | 120   | 1          | High       |
| 6     | 110   | 2          | Medium     |
| 1     | 100   | 2          | Medium     |
| 5     | 90    | 3          | Low        |
| 3     | 80    | 3          | Low        |
+-------+-------+------------+------------+
```

**Explanation**: `NTILE(n)` divides ordered data into n buckets as evenly as possible, commonly used for tiered analysis, ABC classification, etc.

***

### Example 10: Cumulative Distribution - CUME\_DIST Function Application

**Business Scenario**: Calculate the cumulative distribution percentile of each sales value within the dataset

```sql
SELECT 
    month,
    sales,
    CUME_DIST() OVER w AS cumulative_dist,
    ROUND(CUME_DIST() OVER w * 100, 2) AS percentile
FROM sales
WINDOW w AS (ORDER BY sales);
```

**Execution Result**:

```
+-------+-------+------------------+------------+
| month | sales | cumulative_dist  | percentile |
+-------+-------+------------------+------------+
| 3     | 80    | 0.167            | 16.67      |
| 5     | 90    | 0.333            | 33.33      |
| 1     | 100   | 0.500            | 50.00      |
| 6     | 110   | 0.667            | 66.67      |
| 2     | 120   | 0.833            | 83.33      |
| 4     | 150   | 1.000            | 100.00     |
+-------+-------+------------------+------------+
```

**Explanation**: `CUME_DIST()` returns the ratio of rows with values less than or equal to the current row's value to the total number of rows, indicating the cumulative distribution position of the current value within the dataset.

***

## Window Frame Details

### ROWS vs RANGE

| Frame Type | Description                        | Example                                         |
| ---------- | ---------------------------------- | ----------------------------------------------- |
| ROWS       | Based on physical row count        | `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`      |
| RANGE      | Based on logical value range       | `RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING`   |

### Boundary Keywords

* `UNBOUNDED PRECEDING`: The first row of the partition
* `UNBOUNDED FOLLOWING`: The last row of the partition
* `CURRENT ROW`: The current row
* `n PRECEDING`: The nth row before the current row (for ROWS) or rows with value - n (for RANGE)
* `n FOLLOWING`: The nth row after the current row (for ROWS) or rows with value + n (for RANGE)

***

## Common Window Function Categories

### Aggregate Functions

* `SUM()`, `AVG()`, `COUNT()`, `MAX()`, `MIN()`

### Ranking Functions

* `ROW_NUMBER()`: Unique sequential row numbers
* `RANK()`: Same value gets same rank, with gaps
* `DENSE_RANK()`: Same value gets same rank, without gaps
* `PERCENT_RANK()`: Percentile ranking
* `NTILE(n)`: Divides data into n buckets
* `CUME_DIST()`: Cumulative distribution value

### Value Access Functions

* `LAG()`: Access preceding rows
* `LEAD()`: Access following rows
* `FIRST_VALUE()`: First value in the window
* `LAST_VALUE()`: Last value in the window
* `NTH_VALUE()`: The nth value in the window

***

## Best Practices

### 1. Use the WINDOW Clause to Improve Readability

Not recommended (repeated window definitions):

```sql
SELECT month,
       SUM(sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
       AVG(sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
FROM sales;
```

Recommended (using the WINDOW clause):

```sql
SELECT month,
       SUM(sales) OVER w,
       AVG(sales) OVER w
FROM sales
WINDOW w AS (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW);
```

### 2. Use PARTITION BY Appropriately

For grouped analysis, use PARTITION BY to perform intra-group calculations without breaking the data structure:

```sql
-- Example: Calculate ranking separately by category
SELECT category, month, sales,
       RANK() OVER w AS rank_in_category
FROM sales_by_category
WINDOW w AS (PARTITION BY category ORDER BY sales DESC);
```

**Execution Result**:

```
+-------------+-------+-------+------------------+
| category    | month | sales | rank_in_category |
+-------------+-------+-------+------------------+
| Clothing    | 2     | 600   | 1                |
| Clothing    | 3     | 550   | 2                |
| Clothing    | 1     | 500   | 3                |
| Electronics | 2     | 1200  | 1                |
| Electronics | 1     | 1000  | 2                |
| Electronics | 3     | 900   | 3                |
+-------------+-------+-------+------------------+
```

Explanation: Rankings are computed independently within each category without affecting each other.

### 3. Pay Attention to LAST\_VALUE Window Scope

To get the actual last value, you must use `UNBOUNDED FOLLOWING`:

```sql
WINDOW w AS (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
```

### 4. Specific Considerations

In Lakehouse, it is recommended to add a LIMIT clause at the end of the query to improve performance:

```sql
SELECT ... FROM ... WINDOW ... LIMIT 50;
```

***

## Performance Optimization Suggestions

1. **Index Optimization**: Create appropriate indexes on columns used in ORDER BY and PARTITION BY
2. **Window Scope**: Use smaller window scopes whenever possible to reduce computation
3. **Reuse Window Definitions**: Use the WINDOW clause to avoid redefining identical windows
4. **Partitioning Strategy**: Use PARTITION BY appropriately to reduce the data volume within each window

***

## Frequently Asked Questions

### Q1: Where must the WINDOW clause be placed?

A: The WINDOW clause must be placed after the FROM and WHERE clauses, and before the ORDER BY clause.

### Q2: Can multiple windows be defined in the same query?

A: Yes, use commas to separate multiple window definitions.

### Q3: What is the main difference between ROWS and RANGE?

A: ROWS is based on physical row count, while RANGE is based on logical value range. When there are duplicate values, RANGE will include all rows with the same value.

### Q4: Why doesn't LAST\_VALUE return the expected last value?

A: You need to explicitly specify `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` to include the entire partition.

***

^
