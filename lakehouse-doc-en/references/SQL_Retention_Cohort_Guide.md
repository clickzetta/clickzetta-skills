# Retention and Cohort Analysis Guide

> **Scenario**: Calculate user retention rates, perform cohort analysis, track consecutive activity streaks, and identify churned users.
>
> **Core techniques**: `DATEDIFF` to calculate time intervals, `DATE_TRUNC` to group cohorts, window functions to mark consecutive ranges, `CASE` for pivot-style retention matrices.

---

## Quick Reference

| Analysis Type | Business Question | Core Technique | Complexity |
|---|---|---|---|
| Basic retention | How many users return on day N after registration? | `DATEDIFF` + conditional aggregation | ⭐⭐ |
| Cohort matrix | How do retention trends compare across registration months? | `DATE_TRUNC` + pivot | ⭐⭐⭐ |
| Consecutive retention | What is a user's longest consecutive active streak? | `ROW_NUMBER` + difference grouping | ⭐⭐⭐ |
| Churn analysis | Which users have been inactive for N days? | `MAX` + `DATEDIFF` + threshold classification | ⭐⭐ |
| Retention curve | How does retention decay over time? | Weekly/monthly aggregation + line chart data | ⭐⭐ |

---

## Sample Data

All examples in this guide are based on the following user behavior data:

```sql
-- User registration table
CREATE TABLE users (
  user_id BIGINT,
  register_date VARCHAR  -- Use DATE type in production
);

-- User activity log table
CREATE TABLE activity (
  user_id BIGINT,
  activity_date VARCHAR
);
```

The sample data simulates 3 cohorts (5 users registered in January, February, and March respectively), totaling 15 users with activity records spanning 3 months.

---

## 1. Basic Retention: Day-N Retention Rate

### Retention Definition

- **Day 0 retention**: Users active on their registration day (should be 100%).
- **Day N retention**: Number of users still active on day N after registration / total users in the cohort.

### SQL Implementation

```sql
WITH retention_base AS (
  SELECT 
    u.user_id,
    u.register_date,
    a.activity_date,
    DATEDIFF(a.activity_date, u.register_date) AS days_since_register
  FROM users u
  JOIN activity a ON u.user_id = a.user_id
),
cohort_size AS (
  SELECT 
    DATE_TRUNC('MONTH', CAST(register_date AS DATE)) AS cohort_month,
    COUNT(DISTINCT user_id) AS cohort_users
  FROM users
  GROUP BY 1
),
retention_by_day AS (
  SELECT 
    DATE_TRUNC('MONTH', CAST(rb.register_date AS DATE)) AS cohort_month,
    rb.days_since_register,
    COUNT(DISTINCT rb.user_id) AS retained_users
  FROM retention_base rb
  GROUP BY 1, 2
)
SELECT 
  r.cohort_month,
  r.days_since_register,
  r.retained_users,
  c.cohort_users,
  ROUND(r.retained_users * 100.0 / c.cohort_users, 1) AS retention_pct
FROM retention_by_day r
JOIN cohort_size c ON r.cohort_month = c.cohort_month
WHERE r.days_since_register IN (0, 1, 3, 7, 14, 30)
ORDER BY r.cohort_month, r.days_since_register;
```

**Sample output**:

| cohort_month | days_since_register | retained_users | cohort_users | retention_pct |
|--------------|---------------------|----------------|--------------|---------------|
| 2026-01-01   | 0                   | 5              | 5            | 100.0         |
| 2026-01-01   | 1                   | 5              | 5            | 100.0         |
| 2026-01-01   | 3                   | 2              | 5            | 40.0          |
| 2026-01-01   | 7                   | 3              | 5            | 60.0          |
| 2026-02-01   | 0                   | 5              | 5            | 100.0         |
| 2026-02-01   | 7                   | 4              | 5            | 80.0          |

### Key Notes

- `DATEDIFF(end, start)` returns the number of days between two dates.
- `DATE_TRUNC('MONTH', date)` truncates a date to the first day of the month, used for cohort grouping.
- Choose retention day checkpoints based on your business cycle: gaming typically uses day 1/3/7; SaaS typically uses day 7/14/30.

---

## 2. Cohort Retention Matrix (Pivot)

### Use Case

The retention matrix is a common BI report format: rows represent cohorts, columns represent retention days, and cells contain retention rates.

### SQL Implementation

```sql
-- Build a pivot on top of the basic retention query using CASE
SELECT 
  r.cohort_month,
  c.cohort_users,
  MAX(CASE WHEN r.days_since_register = 0 THEN ROUND(r.retained_users * 100.0 / c.cohort_users, 1) END) AS day_0,
  MAX(CASE WHEN r.days_since_register = 1 THEN ROUND(r.retained_users * 100.0 / c.cohort_users, 1) END) AS day_1,
  MAX(CASE WHEN r.days_since_register = 3 THEN ROUND(r.retained_users * 100.0 / c.cohort_users, 1) END) AS day_3,
  MAX(CASE WHEN r.days_since_register = 7 THEN ROUND(r.retained_users * 100.0 / c.cohort_users, 1) END) AS day_7,
  MAX(CASE WHEN r.days_since_register = 14 THEN ROUND(r.retained_users * 100.0 / c.cohort_users, 1) END) AS day_14,
  MAX(CASE WHEN r.days_since_register = 30 THEN ROUND(r.retained_users * 100.0 / c.cohort_users, 1) END) AS day_30
FROM retention_by_day r
JOIN cohort_size c ON r.cohort_month = c.cohort_month
GROUP BY r.cohort_month, c.cohort_users
ORDER BY r.cohort_month;
```

**Sample output**:

| cohort_month | cohort_users | day_0 | day_1 | day_3 | day_7 | day_14 | day_30 |
|--------------|--------------|-------|-------|-------|-------|--------|--------|
| 2026-01-01   | 5            | 100   | 100   | 40    | 60    | NULL   | NULL   |
| 2026-02-01   | 5            | 100   | 100   | 20    | 80    | 20     | NULL   |
| 2026-03-01   | 5            | 100   | 100   | 20    | 60    | 20     | NULL   |

> ⚠️ **Note**: A `NULL` value in `day_30` means the cohort's data does not yet cover 30 days — it is not a calculation error.

### Dynamic Columns

To support additional retention checkpoints (e.g., day 60 or day 90), simply append more `MAX(CASE WHEN ...)` columns to the `SELECT` clause.

---

## 3. Consecutive Retention: Longest Active Streak

### Core Logic

Use the window function `ROW_NUMBER()` to identify consecutive ranges:
- If dates are consecutive, the value of `activity_date - row_number` stays constant.
- Rows sharing the same difference value belong to the same consecutive streak.

### SQL Implementation

```sql
WITH ranked AS (
  SELECT 
    user_id,
    CAST(activity_date AS DATE) AS activity_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) AS rn
  FROM activity
),
grouped AS (
  SELECT 
    user_id,
    activity_date,
    rn,
    -- Core trick: compute days since a fixed baseline, then subtract rn
    DATEDIFF(activity_date, CAST('2000-01-01' AS DATE)) - rn AS grp
  FROM ranked
),
streaks AS (
  SELECT 
    user_id,
    grp,
    MIN(activity_date) AS streak_start,
    MAX(activity_date) AS streak_end,
    COUNT(*) AS streak_length
  FROM grouped
  GROUP BY user_id, grp
),
max_streaks AS (
  SELECT 
    user_id,
    MAX(streak_length) AS max_consecutive_days
  FROM streaks
  GROUP BY user_id
)
SELECT 
  ms.user_id,
  ms.max_consecutive_days,
  s.streak_start,
  s.streak_end
FROM max_streaks ms
JOIN streaks s ON ms.user_id = s.user_id AND ms.max_consecutive_days = s.streak_length
ORDER BY ms.max_consecutive_days DESC, ms.user_id;
```

**Sample output**:

| user_id | max_consecutive_days | streak_start | streak_end |
|---------|----------------------|--------------|------------|
| 1       | 2                    | 2026-01-05   | 2026-01-06 |
| 2       | 2                    | 2026-01-10   | 2026-01-11 |
| ...     | ...                  | ...          | ...        |

### Extension: Users with a Streak of N or More Days

```sql
-- Count users with a streak of at least 3 consecutive days
SELECT COUNT(DISTINCT user_id) AS users_with_3day_streak
FROM streaks
WHERE streak_length >= 3;
```

---

## 4. Churn Analysis: Identifying Inactive Users

### User Status Classification

| Status | Definition | Recommended Action |
|---|---|---|
| active | Active within the last 7 days | Maintain experience |
| warning | Inactive for 7–13 days | Send a reminder |
| at_risk | Inactive for 14–29 days | Offer an incentive |
| churned | Inactive for 30+ days | Run a win-back campaign |

### SQL Implementation

```sql
-- Analysis reference date: 2026-03-25
WITH user_last_active AS (
  SELECT 
    u.user_id,
    u.register_date,
    MAX(a.activity_date) AS last_active_date,
    DATEDIFF(CAST('2026-03-25' AS DATE), CAST(MAX(a.activity_date) AS DATE)) AS days_since_active
  FROM users u
  LEFT JOIN activity a ON u.user_id = a.user_id
  GROUP BY u.user_id, u.register_date
)
SELECT 
  user_id,
  register_date,
  last_active_date,
  days_since_active,
  CASE 
    WHEN days_since_active >= 30 THEN 'churned'
    WHEN days_since_active >= 14 THEN 'at_risk'
    WHEN days_since_active >= 7 THEN 'warning'
    ELSE 'active'
  END AS user_status
FROM user_last_active
ORDER BY days_since_active DESC;
```

**Sample output**:

| user_id | register_date | last_active_date | days_since_active | user_status |
|---------|---------------|------------------|-------------------|-------------|
| 5       | 2026-01-25    | 2026-01-26       | 58                | churned     |
| 4       | 2026-01-20    | 2026-01-27       | 57                | churned     |
| 8       | 2026-02-10    | 2026-02-25       | 28                | at_risk     |
| 12      | 2026-03-05    | 2026-03-20       | 5                 | active      |

### Churn Rate Summary

```sql
SELECT 
  user_status,
  COUNT(*) AS user_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM user_last_active
GROUP BY user_status
ORDER BY user_count DESC;
```

---

## 5. Retention Curve: Weekly Aggregated Retention Trend

### Use Case

Generate line chart data showing how retention decays over time.

### SQL Implementation

```sql
WITH retention_base AS (
  SELECT 
    u.user_id,
    u.register_date,
    a.activity_date,
    DATEDIFF(a.activity_date, u.register_date) AS days_since_register
  FROM users u
  JOIN activity a ON u.user_id = a.user_id
),
cohort_size AS (
  SELECT 
    DATE_TRUNC('MONTH', CAST(register_date AS DATE)) AS cohort_month,
    COUNT(DISTINCT user_id) AS cohort_users
  FROM users
  GROUP BY 1
),
retention_by_week AS (
  SELECT 
    DATE_TRUNC('MONTH', CAST(rb.register_date AS DATE)) AS cohort_month,
    FLOOR(rb.days_since_register / 7.0) AS week_number,
    COUNT(DISTINCT rb.user_id) AS retained_users
  FROM retention_base rb
  GROUP BY 1, 2
)
SELECT 
  r.cohort_month,
  r.week_number,
  r.retained_users,
  c.cohort_users,
  ROUND(r.retained_users * 100.0 / c.cohort_users, 1) AS retention_pct
FROM retention_by_week r
JOIN cohort_size c ON r.cohort_month = c.cohort_month
ORDER BY r.cohort_month, r.week_number;
```

**Sample output**:

| cohort_month | week_number | retained_users | cohort_users | retention_pct |
|--------------|-------------|----------------|--------------|---------------|
| 2026-01-01   | 0           | 5              | 5            | 100.0         |
| 2026-01-01   | 1           | 4              | 5            | 80.0          |
| 2026-01-01   | 2           | 2              | 5            | 40.0          |
| 2026-01-01   | 3           | 2              | 5            | 40.0          |
| 2026-02-01   | 0           | 5              | 5            | 100.0         |
| 2026-02-01   | 1           | 4              | 5            | 80.0          |

### Visualization Tips

- **X-axis**: `week_number`
- **Y-axis**: `retention_pct`
- **Legend**: `cohort_month` (different colors for different registration months)

---

## 6. Advanced: Cohort × Behavioral Attribute Cross-Analysis

### Scenario: Retention Differences by Acquisition Channel

```sql
SELECT 
  u.channel,
  DATE_TRUNC('MONTH', CAST(u.register_date AS DATE)) AS cohort_month,
  COUNT(DISTINCT u.user_id) AS cohort_users,
  COUNT(DISTINCT CASE WHEN DATEDIFF(a.activity_date, u.register_date) = 7 THEN u.user_id END) AS day_7_retained,
  ROUND(
    COUNT(DISTINCT CASE WHEN DATEDIFF(a.activity_date, u.register_date) = 7 THEN u.user_id END) * 100.0 
    / COUNT(DISTINCT u.user_id), 1
  ) AS day_7_retention_pct
FROM users u
LEFT JOIN activity a ON u.user_id = a.user_id
GROUP BY u.channel, DATE_TRUNC('MONTH', CAST(u.register_date AS DATE))
ORDER BY cohort_month, day_7_retention_pct DESC;
```

### Scenario: Cohort LTV (Lifetime Value)

```sql
SELECT 
  DATE_TRUNC('MONTH', CAST(u.register_date AS DATE)) AS cohort_month,
  COUNT(DISTINCT u.user_id) AS cohort_users,
  SUM(o.order_amount) AS total_revenue,
  ROUND(SUM(o.order_amount) / COUNT(DISTINCT u.user_id), 2) AS avg_ltv
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY 1
ORDER BY 1;
```

---

## Common Issues

### 1. `DATEDIFF` Argument Order

```sql
-- Correct: DATEDIFF(end, start)
DATEDIFF('2026-03-25', '2026-01-01')  -- returns 83

-- Wrong: reversed arguments produce a negative number
DATEDIFF('2026-01-01', '2026-03-25')  -- returns -83
```

### 2. `DATE_ADD` Syntax

```sql
-- Correct: DATE_ADD(date, INTERVAL n unit)
DATE_ADD(CAST('2026-01-10' AS DATE), INTERVAL 3 DAY)

-- Wrong: 3-argument form is not supported
DATE_ADD('2026-01-10', 3, 'DAY')  -- syntax error
```

### 3. Baseline Date for Consecutive Streak Calculation

```sql
-- Correct: use a fixed baseline date (e.g., '2000-01-01')
DATEDIFF(activity_date, CAST('2000-01-01' AS DATE)) - rn AS grp

-- Wrong: using a dynamic baseline causes incorrect grouping
DATEDIFF(activity_date, MIN(activity_date)) - rn  -- baseline differs per group
```

### 4. Division by Zero in Retention Rate

```sql
-- Safe: use NULLIF to avoid divide-by-zero errors
ROUND(retained_users * 100.0 / NULLIF(cohort_users, 0), 1)
```

### 5. Cohort Grouping Granularity

```sql
-- Monthly grouping (recommended)
DATE_TRUNC('MONTH', CAST(register_date AS DATE))

-- Weekly grouping
DATE_TRUNC('WEEK', CAST(register_date AS DATE))

-- Daily grouping (not recommended for large datasets)
CAST(register_date AS DATE)
```

---

## Performance Optimization Tips

| Scenario | Strategy |
|---|---|
| Large-scale retention calculation | Deduplicate the activity log by `user_id` first, then JOIN |
| Cohort matrix | Materialize `retention_base` as a Dynamic Table |
| Consecutive activity tracking | Build a Bloom Filter index on `(user_id, activity_date)` in the `activity` table |
| Churn analysis | Parameterize the reference date to avoid hardcoding |

```sql
-- Optimization example: deduplicate before calculating
WITH distinct_activity AS (
  SELECT DISTINCT user_id, CAST(activity_date AS DATE) AS activity_date
  FROM activity
),
retention_base AS (
  SELECT 
    u.user_id,
    u.register_date,
    a.activity_date,
    DATEDIFF(a.activity_date, u.register_date) AS days_since_register
  FROM users u
  JOIN distinct_activity a ON u.user_id = a.user_id
)
-- Remaining logic is unchanged...
```
