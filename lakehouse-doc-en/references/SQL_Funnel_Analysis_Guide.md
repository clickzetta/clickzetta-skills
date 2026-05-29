# Lakehouse Funnel Analysis and User Behavior Analysis Guide

## Overview

Funnel analysis and user behavior analysis are the most common data analysis needs in e-commerce, SaaS, and mobile app scenarios. They are used to measure user drop-off rates from registration through final conversion at each step, as well as user activity frequency, retention rates, and behavior paths. Singdata Lakehouse provides comprehensive window function, aggregate function, and time function support to efficiently perform these analyses. This guide categorizes usage by business scenario to help you quickly master the core SQL patterns for funnel analysis.

### Quick Navigation

* [Basic Funnel Conversion Rate](#scenario-1-basic-funnel-conversion-rate) -- Use COUNT DISTINCT + CASE WHEN to count users and conversion rates at each step
* [Ordered Funnel](#scenario-2-ordered-funnel) -- Require steps to occur in chronological order, filtering out-of-order behavior
* [User First/Last Behavior](#scenario-3-user-firstlast-behavior) -- Use MIN/MAX to find first purchase time and last activity time
* [User Retention Analysis](#scenario-4-user-retention-analysis) -- Count whether users have behavior on day 1/7 after registration
* [Session Segmentation](#scenario-5-session-segmentation) -- Treat intervals over 30 minutes between events as new sessions
* [Behavior Path Concatenation](#scenario-6-behavior-path-concatenation) -- Use COLLECT_LIST or GROUP_CONCAT to generate behavior sequences

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `COUNT(DISTINCT ...)` | Count distinct users | Funnel step user counts |
| `MAX(CASE WHEN ...)` | Determine if a user completed a step | Funnel tagging, retention tagging |
| `MIN()` / `MAX()` | Get earliest/latest time | First behavior, last activity |
| `LAG()` | Access previous row data | Ordered funnel, session segmentation |
| `UNIX_TIMESTAMP()` | Convert timestamp to seconds | Compute event interval seconds |
| `DATEDIFF()` | Compute date difference | Retention day count calculation |
| `SUM() OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` | Cumulative sum | Session ID generation |
| `GROUP_CONCAT(... ORDER BY ... SEPARATOR ...)` | Ordered string concatenation | Behavior path string |
| `COLLECT_LIST(... ORDER BY ...)` | Ordered array collection | Behavior path array |

***

## Prerequisites

The following examples use a simulated user behavior event table `doc_funnel_events`, covering four steps: register, browse, add_cart, pay:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS doc_funnel_events (
    event_id   INT,
    user_id    INT,
    step_name  STRING,
    event_time TIMESTAMP
);

-- Insert test data (7 users, some did not complete the full funnel)
INSERT INTO doc_funnel_events VALUES
(1,  101, 'register', CAST('2024-01-01 08:00:00' AS TIMESTAMP)),
(2,  101, 'browse',   CAST('2024-01-01 08:05:00' AS TIMESTAMP)),
(3,  101, 'add_cart', CAST('2024-01-01 08:10:00' AS TIMESTAMP)),
(4,  101, 'pay',      CAST('2024-01-01 08:20:00' AS TIMESTAMP)),
(5,  102, 'register', CAST('2024-01-02 09:00:00' AS TIMESTAMP)),
(6,  102, 'browse',   CAST('2024-01-02 09:10:00' AS TIMESTAMP)),
(7,  102, 'add_cart', CAST('2024-01-02 09:20:00' AS TIMESTAMP)),
(8,  103, 'register', CAST('2024-01-03 10:00:00' AS TIMESTAMP)),
(9,  103, 'browse',   CAST('2024-01-03 10:15:00' AS TIMESTAMP)),
(10, 104, 'register', CAST('2024-01-04 11:00:00' AS TIMESTAMP)),
(11, 104, 'browse',   CAST('2024-01-04 11:30:00' AS TIMESTAMP)),
(12, 104, 'add_cart', CAST('2024-01-04 12:00:00' AS TIMESTAMP)),
(13, 104, 'pay',      CAST('2024-01-04 12:30:00' AS TIMESTAMP)),
(14, 105, 'register', CAST('2024-01-05 14:00:00' AS TIMESTAMP)),
(15, 106, 'register', CAST('2024-01-06 15:00:00' AS TIMESTAMP)),
(16, 106, 'browse',   CAST('2024-01-06 15:10:00' AS TIMESTAMP)),
(17, 107, 'register', CAST('2024-01-07 16:00:00' AS TIMESTAMP)),
(18, 107, 'browse',   CAST('2024-01-07 16:20:00' AS TIMESTAMP)),
(19, 107, 'add_cart', CAST('2024-01-07 17:00:00' AS TIMESTAMP)),
(20, 107, 'pay',      CAST('2024-01-07 17:30:00' AS TIMESTAMP)),
-- Behaviors on subsequent dates (for retention and session analysis)
(21, 101, 'browse',   CAST('2024-01-02 10:00:00' AS TIMESTAMP)),
(22, 101, 'pay',      CAST('2024-01-08 11:00:00' AS TIMESTAMP)),
(23, 102, 'browse',   CAST('2024-01-03 09:00:00' AS TIMESTAMP)),
(24, 104, 'browse',   CAST('2024-01-05 14:00:00' AS TIMESTAMP)),
(25, 104, 'pay',      CAST('2024-01-11 15:00:00' AS TIMESTAMP)),
(26, 107, 'browse',   CAST('2024-01-08 10:00:00' AS TIMESTAMP));
```

> ⚠️ **Note**: `TIMESTAMP` literals do not support direct string values; use `CAST('...' AS TIMESTAMP)` for explicit conversion.

***

## Scenario 1: Basic Funnel Conversion Rate

Count users at each step -- register, browse, add_cart, pay -- and compute conversion rates between adjacent steps.

```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN step_name = 'register'  THEN 1 ELSE 0 END) AS has_register,
        MAX(CASE WHEN step_name = 'browse'    THEN 1 ELSE 0 END) AS has_browse,
        MAX(CASE WHEN step_name = 'add_cart'  THEN 1 ELSE 0 END) AS has_add_cart,
        MAX(CASE WHEN step_name = 'pay'       THEN 1 ELSE 0 END) AS has_pay
    FROM doc_funnel_events
    GROUP BY user_id
)
SELECT
    COUNT(*)                                                          AS total_users,
    SUM(has_register)                                                 AS step1_register,
    SUM(has_browse)                                                   AS step2_browse,
    SUM(has_add_cart)                                                 AS step3_add_cart,
    SUM(has_pay)                                                      AS step4_pay,
    ROUND(SUM(has_browse)   * 100.0 / SUM(has_register),  1)         AS browse_rate,
    ROUND(SUM(has_add_cart) * 100.0 / SUM(has_browse),    1)         AS add_cart_rate,
    ROUND(SUM(has_pay)      * 100.0 / SUM(has_add_cart),  1)         AS pay_rate
FROM funnel;
```

**Execution Result**:

| total_users | step1_register | step2_browse | step3_add_cart | step4_pay | browse_rate | add_cart_rate | pay_rate |
|-------------|----------------|--------------|----------------|-----------|-------------|---------------|----------|
| 7 | 7 | 6 | 4 | 3 | 85.7 | 66.7 | 75.0 |

> **Explanation**: `MAX(CASE WHEN ...)` tags each user (0/1), then `SUM` aggregates, which is the standard pattern for funnel analysis. Conversion rate denominators use the user count from the previous step, reflecting gradual drop-off.

***

## Scenario 2: Ordered Funnel

The basic funnel only checks whether a user reached a step, not the order. An ordered funnel requires steps to occur in chronological order, filtering out abnormal behavior such as adding to cart before registering.

```sql
WITH step_times AS (
    -- Get each user's earliest time for each step
    SELECT
        user_id,
        MAX(CASE WHEN step_name = 'register'  THEN event_time END) AS t_register,
        MAX(CASE WHEN step_name = 'browse'    THEN event_time END) AS t_browse,
        MAX(CASE WHEN step_name = 'add_cart'  THEN event_time END) AS t_add_cart,
        MAX(CASE WHEN step_name = 'pay'       THEN event_time END) AS t_pay
    FROM doc_funnel_events
    GROUP BY user_id
),
ordered_funnel AS (
    SELECT
        user_id,
        CASE WHEN t_register IS NOT NULL                THEN 1 ELSE 0 END AS s1,
        CASE WHEN t_browse   > t_register               THEN 1 ELSE 0 END AS s2,
        CASE WHEN t_add_cart > t_browse                 THEN 1 ELSE 0 END AS s3,
        CASE WHEN t_pay      > t_add_cart               THEN 1 ELSE 0 END AS s4
    FROM step_times
)
SELECT
    COUNT(*)    AS total,
    SUM(s1)     AS step1_register,
    SUM(s2)     AS step2_browse,
    SUM(s3)     AS step3_add_cart,
    SUM(s4)     AS step4_pay
FROM ordered_funnel;
```

**Execution Result**:

| total | step1_register | step2_browse | step3_add_cart | step4_pay |
|-------|----------------|--------------|----------------|-----------|
| 7 | 7 | 6 | 4 | 3 |

To view each user's ordered funnel details:

```sql
WITH step_times AS (
    SELECT
        user_id,
        MAX(CASE WHEN step_name = 'register'  THEN event_time END) AS t_register,
        MAX(CASE WHEN step_name = 'browse'    THEN event_time END) AS t_browse,
        MAX(CASE WHEN step_name = 'add_cart'  THEN event_time END) AS t_add_cart,
        MAX(CASE WHEN step_name = 'pay'       THEN event_time END) AS t_pay
    FROM doc_funnel_events
    GROUP BY user_id
)
SELECT
    user_id,
    t_register IS NOT NULL  AS did_register,
    t_browse   > t_register AS did_browse_after,
    t_add_cart > t_browse   AS did_add_cart_after,
    t_pay      > t_add_cart AS did_pay_after
FROM step_times
ORDER BY user_id;
```

**Execution Result**:

| user_id | did_register | did_browse_after | did_add_cart_after | did_pay_after |
|---------|--------------|------------------|--------------------|---------------|
| 101 | true | true | true | true |
| 102 | true | true | true | NULL |
| 103 | true | true | NULL | NULL |
| 104 | true | true | true | true |
| 105 | true | NULL | NULL | NULL |
| 106 | true | true | NULL | NULL |
| 107 | true | true | true | true |

> **Explanation**: When a step's timestamp is `NULL` (user did not reach that step), comparison expressions return `NULL` rather than `false`, displayed as `NULL` in results. To uniformly display `NULL` as `false`, use `COALESCE(t_browse > t_register, false)`.

***

## Scenario 3: User First/Last Behavior

Use `MIN` and `MAX` to find each user's first registration time, first purchase time, and last activity time.

```sql
SELECT
    user_id,
    MIN(event_time)                                              AS first_event_time,
    MAX(event_time)                                              AS last_event_time,
    MIN(CASE WHEN step_name = 'pay' THEN event_time END)         AS first_pay_time,
    MAX(CASE WHEN step_name = 'pay' THEN event_time END)         AS last_pay_time
FROM doc_funnel_events
GROUP BY user_id
ORDER BY user_id;
```

**Execution Result**:

| user_id | first_event_time | last_event_time | first_pay_time | last_pay_time |
|---------|-----------------|-----------------|----------------|---------------|
| 101 | 2024-01-01T00:00:00.000Z | 2024-01-08T03:00:00.000Z | 2024-01-01T00:20:00.000Z | 2024-01-08T03:00:00.000Z |
| 102 | 2024-01-02T01:00:00.000Z | 2024-01-03T01:00:00.000Z | NULL | NULL |
| 103 | 2024-01-03T02:00:00.000Z | 2024-01-03T02:15:00.000Z | NULL | NULL |
| 104 | 2024-01-04T03:00:00.000Z | 2024-01-11T07:00:00.000Z | 2024-01-04T04:30:00.000Z | 2024-01-11T07:00:00.000Z |
| 105 | 2024-01-05T06:00:00.000Z | 2024-01-05T06:00:00.000Z | NULL | NULL |
| 106 | 2024-01-06T07:00:00.000Z | 2024-01-06T07:10:00.000Z | NULL | NULL |
| 107 | 2024-01-07T08:00:00.000Z | 2024-01-08T02:00:00.000Z | 2024-01-07T09:30:00.000Z | 2024-01-07T09:30:00.000Z |

> **Explanation**: `MIN(CASE WHEN step_name = 'pay' THEN event_time END)` takes the minimum only for `pay` rows; users without purchases return `NULL`. Timestamps are stored in UTC; use `DATE_FORMAT(event_time, 'yyyy-MM-dd HH:mm:ss')` to convert to local time strings for display.

***

## Scenario 4: User Retention Analysis

Count whether each user had behavior on day 1 and day 7 after registration, and summarize retention rates.

```sql
WITH first_register AS (
    -- Each user's registration date
    SELECT
        user_id,
        MIN(event_time) AS register_time
    FROM doc_funnel_events
    WHERE step_name = 'register'
    GROUP BY user_id
),
activity AS (
    -- Each user's daily activity records (deduplicated)
    SELECT DISTINCT
        user_id,
        CAST(DATE_FORMAT(event_time, 'yyyy-MM-dd') AS DATE) AS active_day
    FROM doc_funnel_events
),
retention AS (
    SELECT
        r.user_id,
        DATE_FORMAT(r.register_time, 'yyyy-MM-dd') AS register_day,
        MAX(CASE WHEN DATEDIFF(a.active_day,
            CAST(DATE_FORMAT(r.register_time, 'yyyy-MM-dd') AS DATE)) = 1
            THEN 1 ELSE 0 END)                             AS day1_retained,
        MAX(CASE WHEN DATEDIFF(a.active_day,
            CAST(DATE_FORMAT(r.register_time, 'yyyy-MM-dd') AS DATE)) = 7
            THEN 1 ELSE 0 END)                             AS day7_retained
    FROM first_register r
    LEFT JOIN activity a ON r.user_id = a.user_id
    GROUP BY r.user_id, r.register_time
)
SELECT
    COUNT(*)                                              AS total_users,
    SUM(day1_retained)                                    AS day1_count,
    SUM(day7_retained)                                    AS day7_count,
    ROUND(SUM(day1_retained) * 100.0 / COUNT(*), 1)       AS day1_rate,
    ROUND(SUM(day7_retained) * 100.0 / COUNT(*), 1)       AS day7_rate
FROM retention;
```

**Execution Result**:

| total_users | day1_count | day7_count | day1_rate | day7_rate |
|-------------|------------|------------|-----------|-----------|
| 7 | 4 | 2 | 57.1 | 28.6 |

To view each user's retention details:

```sql
WITH first_register AS (
    SELECT user_id, MIN(event_time) AS register_time
    FROM doc_funnel_events
    WHERE step_name = 'register'
    GROUP BY user_id
),
activity AS (
    SELECT DISTINCT user_id,
        CAST(DATE_FORMAT(event_time, 'yyyy-MM-dd') AS DATE) AS active_day
    FROM doc_funnel_events
)
SELECT
    r.user_id,
    DATE_FORMAT(r.register_time, 'yyyy-MM-dd')             AS register_day,
    MAX(CASE WHEN DATEDIFF(a.active_day,
        CAST(DATE_FORMAT(r.register_time, 'yyyy-MM-dd') AS DATE)) = 1
        THEN 1 ELSE 0 END)                                 AS day1_retained,
    MAX(CASE WHEN DATEDIFF(a.active_day,
        CAST(DATE_FORMAT(r.register_time, 'yyyy-MM-dd') AS DATE)) = 7
        THEN 1 ELSE 0 END)                                 AS day7_retained
FROM first_register r
LEFT JOIN activity a ON r.user_id = a.user_id
GROUP BY r.user_id, r.register_time
ORDER BY r.user_id;
```

**Execution Result**:

| user_id | register_day | day1_retained | day7_retained |
|---------|--------------|---------------|---------------|
| 101 | 2024-01-01 | 1 | 1 |
| 102 | 2024-01-02 | 1 | 0 |
| 103 | 2024-01-03 | 0 | 0 |
| 104 | 2024-01-04 | 1 | 1 |
| 105 | 2024-01-05 | 0 | 0 |
| 106 | 2024-01-06 | 0 | 0 |
| 107 | 2024-01-07 | 1 | 0 |

> **Explanation**: `DATEDIFF(active_day, register_day) = 1` means the user was active exactly on day 1 after registration. `LEFT JOIN` preserves users without subsequent behavior; `MAX(CASE WHEN ...)` returns 0 when there are no matching rows.

***

## Scenario 5: Session Segmentation

Segment a user's event stream into sessions based on time intervals: intervals over 30 minutes (1800 seconds) between events mark the start of a new session.

```sql
WITH with_prev AS (
    SELECT
        user_id,
        step_name,
        event_time,
        LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_time
    FROM doc_funnel_events
),
with_session AS (
    SELECT
        user_id,
        step_name,
        event_time,
        -- Mark as new session on first event or when interval exceeds 30 minutes
        SUM(CASE
            WHEN prev_time IS NULL
              OR (UNIX_TIMESTAMP(event_time) - UNIX_TIMESTAMP(prev_time)) > 1800
            THEN 1 ELSE 0
        END) OVER (
            PARTITION BY user_id
            ORDER BY event_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_id
    FROM with_prev
)
SELECT
    user_id,
    session_id,
    COUNT(*)                                                AS event_count,
    MIN(DATE_FORMAT(event_time, 'yyyy-MM-dd HH:mm:ss'))     AS session_start,
    MAX(DATE_FORMAT(event_time, 'yyyy-MM-dd HH:mm:ss'))     AS session_end
FROM with_session
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

**Execution Result**:

| user_id | session_id | event_count | session_start | session_end |
|---------|------------|-------------|---------------|-------------|
| 101 | 1 | 4 | 2024-01-01 08:00:00 | 2024-01-01 08:20:00 |
| 101 | 2 | 1 | 2024-01-02 10:00:00 | 2024-01-02 10:00:00 |
| 101 | 3 | 1 | 2024-01-08 11:00:00 | 2024-01-08 11:00:00 |
| 102 | 1 | 3 | 2024-01-02 09:00:00 | 2024-01-02 09:20:00 |
| 102 | 2 | 1 | 2024-01-03 09:00:00 | 2024-01-03 09:00:00 |
| 103 | 1 | 2 | 2024-01-03 10:00:00 | 2024-01-03 10:15:00 |
| 104 | 1 | 4 | 2024-01-04 11:00:00 | 2024-01-04 12:30:00 |
| 104 | 2 | 1 | 2024-01-05 14:00:00 | 2024-01-05 14:00:00 |
| 104 | 3 | 1 | 2024-01-11 15:00:00 | 2024-01-11 15:00:00 |
| 105 | 1 | 1 | 2024-01-05 14:00:00 | 2024-01-05 14:00:00 |
| 106 | 1 | 2 | 2024-01-06 15:00:00 | 2024-01-06 15:10:00 |
| 107 | 1 | 2 | 2024-01-07 16:00:00 | 2024-01-07 16:20:00 |
| 107 | 2 | 2 | 2024-01-07 17:00:00 | 2024-01-07 17:30:00 |
| 107 | 3 | 1 | 2024-01-08 10:00:00 | 2024-01-08 10:00:00 |

> **Explanation**: User 107 had a 40-minute gap between 16:20 and 17:00, exceeding the 30-minute threshold, so add_cart and pay are assigned to session 2. `UNIX_TIMESTAMP` converts timestamps to seconds for interval calculations.

***

## Scenario 6: Behavior Path Concatenation

Concatenate each user's behavior steps in chronological order into strings or arrays for path analysis and pattern mining.

**Method 1: Use `GROUP_CONCAT` to generate string paths**

```sql
SELECT
    user_id,
    GROUP_CONCAT(step_name ORDER BY event_time SEPARATOR ' -> ') AS behavior_path
FROM doc_funnel_events
GROUP BY user_id
ORDER BY user_id;
```

**Execution Result**:

| user_id | behavior_path |
|---------|---------------|
| 101 | register -> browse -> add_cart -> pay -> browse -> pay |
| 102 | register -> browse -> add_cart -> browse |
| 103 | register -> browse |
| 104 | register -> browse -> add_cart -> pay -> browse -> pay |
| 105 | register |
| 106 | register -> browse |
| 107 | register -> browse -> add_cart -> pay -> browse |

**Method 2: Use `COLLECT_LIST` to generate array paths**

```sql
SELECT
    user_id,
    COLLECT_LIST(step_name ORDER BY event_time) AS step_list,
    SIZE(COLLECT_LIST(step_name ORDER BY event_time)) AS step_count
FROM doc_funnel_events
GROUP BY user_id
ORDER BY user_id;
```

**Execution Result**:

| user_id | step_list | step_count |
|---------|-----------|------------|
| 101 | ["register","browse","add_cart","pay","browse","pay"] | 6 |
| 102 | ["register","browse","add_cart","browse"] | 4 |
| 103 | ["register","browse"] | 2 |
| 104 | ["register","browse","add_cart","pay","browse","pay"] | 6 |
| 105 | ["register"] | 1 |
| 106 | ["register","browse"] | 2 |
| 107 | ["register","browse","add_cart","pay","browse"] | 5 |

> **Explanation**: `GROUP_CONCAT` is suitable for generating readable path strings; `COLLECT_LIST` is suitable for subsequent programmatic processing with functions like `ARRAY_CONTAINS`. Both support `ORDER BY` inside the aggregate function without relying on subquery sorting.

***

## Clean Up Test Data

After completing funnel analysis verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS doc_funnel_events;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Funnel Step Deduplication**: `MAX(CASE WHEN step_name = 'pay' THEN 1 ELSE 0 END)` only tags whether a user reached the step, unaffected by repeated events. To count the number of times, use `COUNT(CASE WHEN step_name = 'pay' THEN 1 END)` instead.
2. **Ordered Funnel NULL Propagation**: When a step's timestamp is `NULL`, `t_add_cart > t_browse` returns `NULL` rather than `false`. In `SUM`, `NULL` is ignored (equivalent to 0), so summary results are unaffected.
3. **UNIX_TIMESTAMP Precision**: `UNIX_TIMESTAMP` returns second-level integers, suitable for minute-level intervals. For millisecond precision, use `UNIX_MILLIS(event_time)` with a threshold of `1800000`.
4. **DATEDIFF Parameter Order**: `DATEDIFF(end_date, start_date)` returns the number of days as `end_date - start_date`.
5. **GROUP_CONCAT Default Length Limit**: `GROUP_CONCAT` has a maximum string length; very long paths may be truncated. For complete paths, prefer `COLLECT_LIST`.
6. **Window Function Execution Order**: Window functions execute after `WHERE` and `GROUP BY`; window function results cannot be used directly in `WHERE`. Use `QUALIFY` or subqueries for filtering.

***

## Related Documentation

* [Window Functions](WINDOWFUNCTION.md)
* [Date and Time Functions](datetime_patterns.md)
* [QUALIFY Clause](sql-qualify.md)
* [GROUP BY Clause](groupby.md)
