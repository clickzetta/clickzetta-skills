# Cumulative Calculation and Running Totals

## Overview

Cumulative calculation (Running Total / Cumulative Aggregation) is a high-frequency requirement in data analysis: calculating cumulative sales up to a point in time, computing rolling N-day averages, tracking how much a metric has changed from its starting point. Singdata Lakehouse implements these calculations through window function `ORDER BY` clauses and frame specifications (`ROWS BETWEEN`) without requiring self-joins or subqueries.

### SQL Syntax Covered

| Syntax | Purpose |
|------|------|
| `SUM(...) OVER (ORDER BY ...)` | Cumulative sum (default frame: from first row to current row) |
| `ROWS BETWEEN N PRECEDING AND CURRENT ROW` | Rolling N-row window |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | From partition start to current row |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | Entire partition |
| `FIRST_VALUE / LAST_VALUE` | Get first/last row value in window |
| `LAG(col, n)` | Get value of n rows before, used for period-over-period calculation |

---

## Prerequisite Data

The following examples use two test tables:

```SQL
-- Daily sales details table
CREATE TABLE IF NOT EXISTS doc_running_sales (
  sale_date DATE,
  region    VARCHAR(20),
  amount    DECIMAL(10,2)
);

INSERT INTO doc_running_sales VALUES
  (CAST('2024-01-01' AS DATE), 'East', 1200.00),
  (CAST('2024-01-02' AS DATE), 'East',  850.00),
  (CAST('2024-01-03' AS DATE), 'East', 1500.00),
  (CAST('2024-01-04' AS DATE), 'East',  600.00),
  (CAST('2024-01-05' AS DATE), 'East', 2100.00),
  (CAST('2024-01-01' AS DATE), 'West',  900.00),
  (CAST('2024-01-02' AS DATE), 'West', 1100.00),
  (CAST('2024-01-03' AS DATE), 'West',  750.00),
  (CAST('2024-01-04' AS DATE), 'West', 1300.00),
  (CAST('2024-01-05' AS DATE), 'West',  980.00);

-- Monthly revenue table
CREATE TABLE IF NOT EXISTS doc_running_monthly (
  month_date DATE,
  category   VARCHAR(20),
  revenue    DECIMAL(12,2)
);

INSERT INTO doc_running_monthly VALUES
  (CAST('2024-01-01' AS DATE), 'Apparel',   50000.00),
  (CAST('2024-02-01' AS DATE), 'Apparel',   45000.00),
  (CAST('2024-03-01' AS DATE), 'Apparel',   62000.00),
  (CAST('2024-04-01' AS DATE), 'Apparel',   58000.00),
  (CAST('2024-01-01' AS DATE), 'Electronics', 120000.00),
  (CAST('2024-02-01' AS DATE), 'Electronics', 135000.00),
  (CAST('2024-03-01' AS DATE), 'Electronics',  98000.00),
  (CAST('2024-04-01' AS DATE), 'Electronics', 145000.00);
```

---

## Scenario 1: Cumulative Sum by Partition

Calculate the cumulative daily sales for each region.

```SQL
SELECT
  sale_date,
  region,
  amount,
  SUM(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
  ) AS running_total
FROM doc_running_sales
ORDER BY region, sale_date;
```

Result:

| sale_date  | region | amount  | running_total |
|------------|--------|---------|---------------|
| 2024-01-01 | East   | 1200.00 | 1200.00       |
| 2024-01-02 | East   | 850.00  | 2050.00       |
| 2024-01-03 | East   | 1500.00 | 3550.00       |
| 2024-01-04 | East   | 600.00  | 4150.00       |
| 2024-01-05 | East   | 2100.00 | 6250.00       |
| 2024-01-01 | West   | 900.00  | 900.00        |
| 2024-01-02 | West   | 1100.00 | 2000.00       |
| 2024-01-03 | West   | 750.00  | 2750.00       |
| 2024-01-04 | West   | 1300.00 | 4050.00       |
| 2024-01-05 | West   | 980.00  | 5030.00       |

> Without `ROWS BETWEEN`, the default frame for `ORDER BY` is `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, i.e., from the partition start to the current row.

---

## Scenario 2: Cumulative Proportion of Total (YTD Progress)

Calculate each category's monthly YTD revenue and its proportion of total annual revenue.

```SQL
SELECT
  month_date,
  category,
  revenue,
  SUM(revenue) OVER (
    PARTITION BY category
    ORDER BY month_date
  )                                                          AS ytd_revenue,
  SUM(revenue) OVER (PARTITION BY category)                 AS annual_total,
  ROUND(
    SUM(revenue) OVER (PARTITION BY category ORDER BY month_date)
    / SUM(revenue) OVER (PARTITION BY category) * 100,
    2
  )                                                          AS ytd_pct
FROM doc_running_monthly
ORDER BY category, month_date;
```

Result:

| month_date | category     | revenue   | ytd_revenue | annual_total | ytd_pct |
|------------|--------------|-----------|-------------|--------------|---------|
| 2024-01-01 | Apparel      | 50000.00  | 50000.00    | 215000.00    | 23.26   |
| 2024-02-01 | Apparel      | 45000.00  | 95000.00    | 215000.00    | 44.19   |
| 2024-03-01 | Apparel      | 62000.00  | 157000.00   | 215000.00    | 73.02   |
| 2024-04-01 | Apparel      | 58000.00  | 215000.00   | 215000.00    | 100.00  |
| 2024-01-01 | Electronics  | 120000.00 | 120000.00   | 498000.00    | 24.10   |
| 2024-02-01 | Electronics  | 135000.00 | 255000.00   | 498000.00    | 51.20   |
| 2024-03-01 | Electronics  | 98000.00  | 353000.00   | 498000.00    | 70.88   |
| 2024-04-01 | Electronics  | 145000.00 | 498000.00   | 498000.00    | 100.00  |

---

## Scenario 3: Rolling N-Row Window (Moving Average)

Calculate a 3-day moving average of sales for each region.

```SQL
SELECT
  sale_date,
  region,
  amount,
  AVG(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS moving_avg_3day
FROM doc_running_sales
ORDER BY region, sale_date;
```

Result:

| sale_date  | region | amount  | moving_avg_3day |
|------------|--------|---------|-----------------|
| 2024-01-01 | East   | 1200.00 | 1200.000000     |
| 2024-01-02 | East   | 850.00  | 1025.000000     |
| 2024-01-03 | East   | 1500.00 | 1183.333333     |
| 2024-01-04 | East   | 600.00  | 983.333333      |
| 2024-01-05 | East   | 2100.00 | 1400.000000     |

> `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` means the current row and the preceding 2 rows, for a total of 3 rows. At the partition boundary where there are fewer than 3 rows, the average uses only the available rows.

---

## Scenario 4: Aggregate First, Then Roll (Two-Level Window)

First aggregate total daily sales across all regions, then calculate a 7-day rolling sum.

```SQL
SELECT
  sale_date,
  SUM(amount)                                                    AS daily_total,
  SUM(SUM(amount)) OVER (
    ORDER BY sale_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  )                                                              AS rolling_7day_sum,
  AVG(SUM(amount)) OVER (
    ORDER BY sale_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  )                                                              AS rolling_7day_avg
FROM doc_running_sales
GROUP BY sale_date
ORDER BY sale_date;
```

Result:

| sale_date  | daily_total | rolling_7day_sum | rolling_7day_avg |
|------------|-------------|------------------|------------------|
| 2024-01-01 | 2100.00     | 2100.00          | 2100.000000      |
| 2024-01-02 | 1950.00     | 4050.00          | 2025.000000      |
| 2024-01-03 | 2250.00     | 6300.00          | 2100.000000      |
| 2024-01-04 | 1900.00     | 8200.00          | 2050.000000      |
| 2024-01-05 | 3080.00     | 11280.00         | 2256.000000      |

> When applying window functions over aggregated results, the window function parameter must be an aggregate expression (`SUM(SUM(amount))`), not a plain column name.

---

## Scenario 5: Cumulative Maximum / Minimum

Track the historical highest and lowest single-day sales for each region.

```SQL
SELECT
  sale_date,
  region,
  amount,
  MAX(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_max,
  MIN(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_min
FROM doc_running_sales
ORDER BY region, sale_date;
```

Result (East region only):

| sale_date  | region | amount  | running_max | running_min |
|------------|--------|---------|-------------|-------------|
| 2024-01-01 | East   | 1200.00 | 1200.00     | 1200.00     |
| 2024-01-02 | East   | 850.00  | 1200.00     | 850.00      |
| 2024-01-03 | East   | 1500.00 | 1500.00     | 850.00      |
| 2024-01-04 | East   | 600.00  | 1500.00     | 600.00      |
| 2024-01-05 | East   | 2100.00 | 2100.00     | 600.00      |

---

## Scenario 6: Period-over-Period Change (MoM / DoD)

Calculate the month-over-month change amount and change rate for each category.

```SQL
SELECT
  month_date,
  category,
  revenue,
  LAG(revenue, 1) OVER (
    PARTITION BY category
    ORDER BY month_date
  )                                                              AS prev_month,
  revenue - LAG(revenue, 1) OVER (
    PARTITION BY category
    ORDER BY month_date
  )                                                              AS mom_change,
  ROUND(
    (revenue - LAG(revenue, 1) OVER (PARTITION BY category ORDER BY month_date))
    / LAG(revenue, 1) OVER (PARTITION BY category ORDER BY month_date) * 100,
    2
  )                                                              AS mom_pct
FROM doc_running_monthly
ORDER BY category, month_date;
```

Result (Apparel category):

| month_date | category | revenue  | prev_month | mom_change | mom_pct |
|------------|----------|----------|------------|------------|---------|
| 2024-01-01 | Apparel  | 50000.00 | NULL       | NULL       | NULL    |
| 2024-02-01 | Apparel  | 45000.00 | 50000.00   | -5000.00   | -10.00  |
| 2024-03-01 | Apparel  | 62000.00 | 45000.00   | 17000.00   | 37.78   |
| 2024-04-01 | Apparel  | 58000.00 | 62000.00   | -4000.00   | -6.45   |

> The first row has no prior period data, so `LAG` returns NULL and the period-over-period calculation also yields NULL. Use `COALESCE(LAG(...), 0)` to replace with 0 if needed.

---

## Scenario 7: Change from Starting Point (FIRST_VALUE)

Calculate each region's daily sales change relative to the first day, and the final day's sales.

```SQL
SELECT
  sale_date,
  region,
  amount,
  FIRST_VALUE(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
  )                                                              AS first_day_amount,
  LAST_VALUE(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )                                                              AS last_day_amount,
  amount - FIRST_VALUE(amount) OVER (
    PARTITION BY region
    ORDER BY sale_date
  )                                                              AS change_from_start
FROM doc_running_sales
ORDER BY region, sale_date;
```

Result (East region only):

| sale_date  | region | amount  | first_day_amount | last_day_amount | change_from_start |
|------------|--------|---------|------------------|-----------------|-------------------|
| 2024-01-01 | East   | 1200.00 | 1200.00          | 2100.00         | 0.00              |
| 2024-01-02 | East   | 850.00  | 1200.00          | 2100.00         | -350.00           |
| 2024-01-03 | East   | 1500.00 | 1200.00          | 2100.00         | 300.00            |
| 2024-01-04 | East   | 600.00  | 1200.00          | 2100.00         | -600.00           |
| 2024-01-05 | East   | 2100.00 | 1200.00          | 2100.00         | 900.00            |

> `LAST_VALUE`'s default frame only goes up to the current row. You must explicitly specify `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` to get the value from the partition's last row.

---

## Important Notes

- **Frame Specification Defaults**: When `ORDER BY` is present, the default frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` (value-range based). For date columns with duplicate dates, `RANGE` and `ROWS` may produce different results. Use explicit `ROWS BETWEEN` when precise control is needed.
- **Two-Level Windows**: When applying window functions over `GROUP BY` aggregated results, the window function argument must wrap the aggregate function (e.g., `SUM(SUM(col))`), otherwise an error will occur.
- **LAST_VALUE Trap**: Without `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`, `LAST_VALUE` only returns the current row's value (because the default frame stops at the current row).
- **NULL Handling**: `LAG` / `LEAD` return NULL at boundaries. Use `COALESCE(LAG(col, 1), 0)` to substitute default values.
