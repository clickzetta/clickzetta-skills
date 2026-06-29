# Lakehouse Time Series Analysis Guide

## Overview

Time series analysis is a core scenario in data analysis, widely applied to business trend monitoring, user behavior analysis, and operational metric computation. Singdata Lakehouse provides complete time function and window function support, including time truncation, date formatting, rolling window aggregation, and date series generation. This guide categorizes usage by business scenario to help you quickly master efficient time series analysis methods.

### Quick Navigation

* [Aggregate by Time Granularity](#scenario-1-aggregate-by-time-granularity) -- Use DATE_FORMAT / DATE_TRUNC to summarize by month, week, or day
* [Rolling Window Calculation](#scenario-2-rolling-window-calculation) -- Use RANGE BETWEEN INTERVAL to compute 7-day rolling averages
* [Year-over-Year / Month-over-Month Calculation](#scenario-3-yoymom-calculation) -- Use LAG to compute monthly growth rate
* [Time Interval Calculation](#scenario-4-time-interval-calculation) -- Use DATEDIFF + LAG to compute event interval days
* [Fill Missing Dates with Zero](#scenario-5-fill-missing-dates-with-zero) -- Use SEQUENCE + EXPLODE to fill dates with no data
* [Active Users in Last N Days](#scenario-6-active-users-in-last-n-days) -- Use INTERVAL to filter recently active users

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `DATE_FORMAT()` | Format timestamp as string | Group by month/day, display |
| `DATE_TRUNC()` | Truncate to specified time granularity | Aggregate by week/month/year |
| `DATEDIFF()` | Calculate day difference between two dates | Event interval, retention analysis |
| `LAG()` / `LEAD()` | Access previous/next row data | MoM, YoY calculation |
| `AVG() OVER (RANGE BETWEEN INTERVAL ...)` | Time-range-based rolling aggregation | 7-day/30-day rolling average |
| `SEQUENCE()` + `EXPLODE()` | Generate continuous date series and expand to rows | Date padding, calendar table |
| `INTERVAL` | Time offset | Date arithmetic, range filter |
| `COALESCE()` | Null value replacement | Zero-fill, default value fill |

***

## Prerequisites

The following examples use a simulated user event table `doc_ts_events`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS doc_ts_events (
    event_id   INT,
    user_id    INT,
    event_type STRING,
    amount     DOUBLE,
    event_time TIMESTAMP
);

-- Insert test data (covering Jan 2024 through Mar 2024)
INSERT INTO doc_ts_events VALUES
(1,  101, 'purchase', 120.50, CAST('2024-01-05 10:00:00' AS TIMESTAMP)),
(2,  102, 'purchase',  85.00, CAST('2024-01-10 14:30:00' AS TIMESTAMP)),
(3,  101, 'refund',    30.00, CAST('2024-01-15 09:00:00' AS TIMESTAMP)),
(4,  103, 'purchase', 200.00, CAST('2024-01-20 16:00:00' AS TIMESTAMP)),
(5,  102, 'purchase',  55.00, CAST('2024-01-25 11:00:00' AS TIMESTAMP)),
(6,  101, 'purchase', 300.00, CAST('2024-02-03 10:00:00' AS TIMESTAMP)),
(7,  104, 'purchase', 150.00, CAST('2024-02-08 13:00:00' AS TIMESTAMP)),
(8,  103, 'refund',    50.00, CAST('2024-02-14 15:00:00' AS TIMESTAMP)),
(9,  102, 'purchase',  90.00, CAST('2024-02-18 09:30:00' AS TIMESTAMP)),
(10, 101, 'purchase',  75.00, CAST('2024-02-22 17:00:00' AS TIMESTAMP)),
(11, 104, 'purchase', 220.00, CAST('2024-03-01 10:00:00' AS TIMESTAMP)),
(12, 103, 'purchase', 180.00, CAST('2024-03-07 14:00:00' AS TIMESTAMP)),
(13, 101, 'refund',    25.00, CAST('2024-03-12 11:00:00' AS TIMESTAMP)),
(14, 102, 'purchase', 130.00, CAST('2024-03-18 16:00:00' AS TIMESTAMP)),
(15, 104, 'purchase',  95.00, CAST('2024-03-25 12:00:00' AS TIMESTAMP));
```

> ⚠️ **Note**: `TIMESTAMP` literals do not support direct string values; use `CAST('...' AS TIMESTAMP)` for explicit conversion.

***

## Scenario 1: Aggregate by Time Granularity

Count the number of events and total amount by month and event type -- the most common time series aggregation requirement.

```sql
-- Aggregate by month and event type
SELECT
    DATE_FORMAT(event_time, 'yyyy-MM') AS month,
    event_type,
    COUNT(*)                           AS event_count,
    ROUND(SUM(amount), 2)              AS total_amount
FROM doc_ts_events
GROUP BY DATE_FORMAT(event_time, 'yyyy-MM'), event_type
ORDER BY month, event_type;
```

**Execution Result**:

| month   | event_type | event_count | total_amount |
|---------|------------|-------------|--------------|
| 2024-01 | purchase | 4 | 460.5 |
| 2024-01 | refund | 1 | 30 |
| 2024-02 | purchase | 4 | 615 |
| 2024-02 | refund | 1 | 50 |
| 2024-03 | purchase | 4 | 625 |
| 2024-03 | refund | 1 | 25 |

To aggregate by week, use `DATE_TRUNC('week', ...)` to truncate to Monday:

```sql
-- Aggregate by natural week (week_start is the Monday of each week)
SELECT
    DATE_FORMAT(DATE_TRUNC('week', event_time), 'yyyy-MM-dd') AS week_start,
    COUNT(*)                                                   AS event_count,
    ROUND(SUM(amount), 2)                                      AS weekly_amount
FROM doc_ts_events
WHERE event_type = 'purchase'
GROUP BY DATE_TRUNC('week', event_time)
ORDER BY week_start;
```

**Execution Result (first 5 rows)**:

| week_start | event_count | weekly_amount |
|------------|-------------|---------------|
| 2024-01-01 | 1 | 120.5 |
| 2024-01-08 | 1 | 85 |
| 2024-01-15 | 1 | 200 |
| 2024-01-22 | 1 | 55 |
| 2024-01-29 | 1 | 300 |

***

## Scenario 2: Rolling Window Calculation

Compute a 7-day rolling average of amounts for each trading day to smooth short-term fluctuations and observe trends.

`RANGE BETWEEN INTERVAL N DAY PRECEDING AND CURRENT ROW` defines the window based on time range (not row count), correctly handling non-consecutive dates.

```sql
WITH daily_sales AS (
    SELECT
        CAST(DATE_FORMAT(event_time, 'yyyy-MM-dd') AS DATE) AS sale_day,
        ROUND(SUM(amount), 2)                               AS daily_amount
    FROM doc_ts_events
    WHERE event_type = 'purchase'
    GROUP BY DATE_FORMAT(event_time, 'yyyy-MM-dd')
)
SELECT
    sale_day,
    daily_amount,
    ROUND(
        AVG(daily_amount) OVER (
            ORDER BY sale_day
            RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW
        ), 2
    ) AS rolling_7d_avg
FROM daily_sales
ORDER BY sale_day;
```

**Execution Result**:

| sale_day   | daily_amount | rolling_7d_avg |
|------------|-------------|----------------|
| 2024-01-05 | 120.5 | 120.5 |
| 2024-01-10 | 85    | 102.75 |
| 2024-01-20 | 200   | 200 |
| 2024-01-25 | 55    | 127.5 |
| 2024-02-03 | 300   | 300 |
| 2024-02-08 | 150   | 225 |
| 2024-02-18 | 90    | 90 |
| 2024-02-22 | 75    | 82.5 |
| 2024-03-01 | 220   | 220 |
| 2024-03-07 | 180   | 200 |
| 2024-03-18 | 130   | 130 |
| 2024-03-25 | 95    | 95 |

> **Explanation**: `RANGE BETWEEN INTERVAL 6 DAY PRECEDING` means the time range of 6 days before the current row's date (7 days total). If two records are more than 6 days apart, they are not in the same window, e.g., 2024-01-10 and 2024-01-20 are 10 days apart, so the rolling average for 2024-01-20 only includes itself.

***

## Scenario 3: YoY/MoM Calculation

Use `LAG()` to get the previous period's data and compute the month-over-month growth rate.

```sql
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(event_time, 'yyyy-MM') AS month,
        ROUND(SUM(amount), 2)              AS monthly_amount
    FROM doc_ts_events
    WHERE event_type = 'purchase'
    GROUP BY DATE_FORMAT(event_time, 'yyyy-MM')
)
SELECT
    month,
    monthly_amount,
    LAG(monthly_amount, 1) OVER (ORDER BY month)                AS prev_month_amount,
    ROUND(
        (monthly_amount - LAG(monthly_amount, 1) OVER (ORDER BY month))
        / LAG(monthly_amount, 1) OVER (ORDER BY month) * 100,
        2
    )                                                           AS mom_growth_pct
FROM monthly_sales
ORDER BY month;
```

**Execution Result**:

| month   | monthly_amount | prev_month_amount | mom_growth_pct |
|---------|---------------|-------------------|----------------|
| 2024-01 | 460.5 | NULL | NULL |
| 2024-02 | 615   | 460.5 | 33.55 |
| 2024-03 | 625   | 615   | 1.63 |

> **Explanation**: The first row has no prior period data, so `LAG` returns `NULL` and the growth rate is also `NULL`. Use `COALESCE(mom_growth_pct, 0)` to display as 0 if needed.

***

## Scenario 4: Time Interval Calculation

Compute the number of days between consecutive events for each user, used to analyze activity frequency and purchase cycles.

```sql
SELECT
    user_id,
    event_type,
    DATE_FORMAT(event_time, 'yyyy-MM-dd')                           AS event_day,
    LAG(DATE_FORMAT(event_time, 'yyyy-MM-dd'), 1)
        OVER (PARTITION BY user_id ORDER BY event_time)             AS prev_event_day,
    DATEDIFF(
        DATE_FORMAT(event_time, 'yyyy-MM-dd'),
        LAG(DATE_FORMAT(event_time, 'yyyy-MM-dd'), 1)
            OVER (PARTITION BY user_id ORDER BY event_time)
    )                                                               AS days_since_last
FROM doc_ts_events
ORDER BY user_id, event_time;
```

**Execution Result**:

| user_id | event_type | event_day  | prev_event_day | days_since_last |
|---------|------------|------------|----------------|-----------------|
| 101 | purchase | 2024-01-05 | NULL | NULL |
| 101 | refund   | 2024-01-15 | 2024-01-05 | 10 |
| 101 | purchase | 2024-02-03 | 2024-01-15 | 19 |
| 101 | purchase | 2024-02-22 | 2024-02-03 | 19 |
| 101 | refund   | 2024-03-12 | 2024-02-22 | 19 |
| 102 | purchase | 2024-01-10 | NULL | NULL |
| 102 | purchase | 2024-01-25 | 2024-01-10 | 15 |
| 102 | purchase | 2024-02-18 | 2024-01-25 | 24 |
| 102 | purchase | 2024-03-18 | 2024-02-18 | 29 |
| 103 | purchase | 2024-01-20 | NULL | NULL |
| 103 | refund   | 2024-02-14 | 2024-01-20 | 25 |
| 103 | purchase | 2024-03-07 | 2024-02-14 | 22 |
| 104 | purchase | 2024-02-08 | NULL | NULL |
| 104 | purchase | 2024-03-01 | 2024-02-08 | 22 |
| 104 | purchase | 2024-03-25 | 2024-03-01 | 24 |

***

## Scenario 5: Fill Missing Dates with Zero

When some dates have no data, direct `GROUP BY` skips those dates, causing gaps in line charts. Use `SEQUENCE` + `EXPLODE` to generate a complete date series, then `LEFT JOIN` actual data and use `COALESCE` to fill NULLs with zero.

```sql
WITH date_spine AS (
    -- Generate continuous dates from 2024-01-01 to 2024-03-31
    SELECT EXPLODE(
        SEQUENCE(
            CAST('2024-01-01' AS DATE),
            CAST('2024-03-31' AS DATE),
            INTERVAL 1 DAY
        )
    ) AS cal_day
),
daily_sales AS (
    SELECT
        CAST(DATE_FORMAT(event_time, 'yyyy-MM-dd') AS DATE) AS sale_day,
        ROUND(SUM(amount), 2)                               AS daily_amount
    FROM doc_ts_events
    WHERE event_type = 'purchase'
    GROUP BY DATE_FORMAT(event_time, 'yyyy-MM-dd')
)
SELECT
    d.cal_day,
    COALESCE(s.daily_amount, 0) AS daily_amount
FROM date_spine d
LEFT JOIN daily_sales s ON d.cal_day = s.sale_day
ORDER BY d.cal_day
LIMIT 10;
```

**Execution Result (first 10 rows)**:

| cal_day    | daily_amount |
|------------|-------------|
| 2024-01-01 | 0 |
| 2024-01-02 | 0 |
| 2024-01-03 | 0 |
| 2024-01-04 | 0 |
| 2024-01-05 | 120.5 |
| 2024-01-06 | 0 |
| 2024-01-07 | 0 |
| 2024-01-08 | 0 |
| 2024-01-09 | 0 |
| 2024-01-10 | 85 |

> **Explanation**: `SEQUENCE(start, end, INTERVAL 1 DAY)` generates a date array, and `EXPLODE` expands the array into rows. Dates without data are preserved via `LEFT JOIN`, and `COALESCE` replaces `NULL` with `0`.

***

## Scenario 6: Active Users in Last N Days

Filter users who had at least 2 purchases in the last 90 days, and count their purchase frequency and last active date.

```sql
SELECT
    user_id,
    COUNT(*)                                   AS purchase_count,
    MAX(DATE_FORMAT(event_time, 'yyyy-MM-dd')) AS last_active_day
FROM doc_ts_events
WHERE event_type = 'purchase'
  AND event_time >= CAST('2024-03-31' AS TIMESTAMP) - INTERVAL 90 DAY
GROUP BY user_id
HAVING COUNT(*) >= 2
ORDER BY last_active_day DESC;
```

**Execution Result**:

| user_id | purchase_count | last_active_day |
|---------|---------------|-----------------|
| 104 | 3 | 2024-03-25 |
| 102 | 4 | 2024-03-18 |
| 103 | 2 | 2024-03-07 |
| 101 | 3 | 2024-02-22 |

> **Explanation**: `CAST('2024-03-31' AS TIMESTAMP) - INTERVAL 90 DAY` computes the timestamp 90 days ago. In production environments, replace the fixed date with `CURRENT_TIMESTAMP()` to dynamically compute the 90-day lookback.

***

## Clean Up Test Data

After completing time series analysis verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS doc_ts_events;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Timezone Handling**: `TIMESTAMP` type stores UTC time. `DATE_FORMAT` and `DATE_TRUNC` parse in the session timezone (default UTC+8). When inserting data, use `CAST('yyyy-MM-dd HH:mm:ss' AS TIMESTAMP)` to explicitly specify time literals and avoid implicit conversion failures.
2. **RANGE vs ROWS**: `ROWS BETWEEN N PRECEDING` defines the window by row count, while `RANGE BETWEEN INTERVAL N DAY PRECEDING` defines it by time range. Results differ when dates are non-consecutive; time series analysis typically uses `RANGE`.
3. **DATE_FORMAT Format Strings**: Lakehouse uses Java-style format strings: `yyyy` for four-digit year, `MM` for month, `dd` for date, `HH` for 24-hour hour. Format letters are case-sensitive.
4. **DATEDIFF Parameter Order**: `DATEDIFF(end_date, start_date)` returns the number of days as `end_date - start_date`.
5. **Window Function Execution Order**: Window functions execute after `WHERE` and `GROUP BY`; window function results cannot be used directly in `WHERE`. Use `QUALIFY` or subqueries for filtering.
6. **SEQUENCE with Large Date Ranges**: `SEQUENCE` generates an array, and `EXPLODE` expands it to rows. When generating large date ranges (e.g., multiple years), be mindful of the impact on query performance.

***

## Related Documentation

* [Window Functions](windowfunction.md)
* [Date and Time Functions](sql_functions/scalar_functions/datetime_functions/datetime_patterns.md)
* [QUALIFY Clause](sql-qualify.md)
* [GROUP BY Clause](groupby.md)
