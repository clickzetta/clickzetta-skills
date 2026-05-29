# Sessionization Guide

> **Scenario**: Split a continuous stream of user behavior events into discrete sessions, then compute session duration, page views, bounce rate, conversion rate, and user paths.
>
> **Core techniques**: `LAG` to retrieve the previous event time, `TIMESTAMPDIFF` to calculate intervals, `SUM` to accumulate flags and generate session IDs, `GROUP_CONCAT` to build visit paths.

---

## Quick Reference

| Analysis Type | Business Question | Core Technique | Complexity |
|---|---|---|---|
| Session splitting | How do you group continuous events into discrete sessions? | `LAG` + `TIMESTAMPDIFF` + `SUM` | ⭐⭐⭐ |
| Session aggregation | What are the average session duration and page views? | `MIN/MAX` + `COUNT` + `GROUP BY` | ⭐⭐ |
| Bounce rate | How many users left after viewing only one page? | `CASE WHEN COUNT = 1` | ⭐⭐ |
| Path analysis | Which pages did users visit within a session? | `GROUP_CONCAT` + `ORDER BY` | ⭐⭐ |
| Conversion analysis | How many sessions completed a target action? | `MAX(CASE WHEN event_type = ...)` | ⭐⭐ |

---

## Sample Data

All examples in this guide are based on the following user behavior event stream:

```sql
-- User behavior events table
CREATE TABLE user_events (
  user_id BIGINT,
  event_time TIMESTAMP_LTZ,
  page VARCHAR,
  event_type VARCHAR  -- view, add_to_cart, complete, etc.
);
```

The sample data simulates 3 users with 18 events total, covering 5 sessions (including bounce sessions and conversion sessions).

---

## 1. Session Splitting (Core)

### Session Definition

- **Session timeout**: If a user is inactive for **30 minutes**, the next activity starts a new session.
- **Session ID**: Increments from 1 within each user partition.

### Four-Step Splitting Method

```sql
WITH events AS (
  SELECT user_id, CAST(event_time AS TIMESTAMP_LTZ) AS event_time, page, event_type
  FROM user_events
),
-- Step 1: Retrieve the previous event time
with_prev AS (
  SELECT 
    user_id,
    event_time,
    page,
    event_type,
    LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_event_time
  FROM events
),
-- Step 2: Calculate the time gap and flag new session starts
with_gap AS (
  SELECT 
    *,
    CASE 
      WHEN prev_event_time IS NULL THEN 1  -- First event, new session
      WHEN TIMESTAMPDIFF(MINUTE, prev_event_time, event_time) > 30 THEN 1  -- Timeout, new session
      ELSE 0
    END AS is_new_session
  FROM with_prev
),
-- Step 3: Accumulate flags to generate session IDs
with_session AS (
  SELECT 
    *,
    SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
  FROM with_gap
)
SELECT user_id, session_id, event_time, page, event_type
FROM with_session
ORDER BY user_id, session_id, event_time;
```

**Sample output**:

| user_id | session_id | event_time          | page           | event_type  |
|---------|------------|---------------------|----------------|-------------|
| 1       | 1          | 2026-03-01 10:00:00 | home           | view        |
| 1       | 1          | 2026-03-01 10:05:00 | products       | view        |
| 1       | 1          | 2026-03-01 10:15:00 | product_detail | view        |
| 1       | 2          | 2026-03-01 14:00:00 | home           | view        |
| 1       | 2          | 2026-03-01 14:10:00 | cart           | view        |
| 2       | 1          | 2026-03-01 09:00:00 | landing        | view        |
| 2       | 2          | 2026-03-01 11:00:00 | home           | view        |

### Key Notes

- `TIMESTAMPDIFF(MINUTE, start, end)` returns the difference in minutes between two timestamps.
- `DATEDIFF` on `TIMESTAMP_LTZ` columns returns the difference in days (not minutes) by default — always use `TIMESTAMPDIFF` for sub-day precision.
- The session timeout threshold can be adjusted to fit your business: 30 minutes is common for e-commerce; 15 minutes works well for content platforms.

---

## 2. Session Aggregation Metrics

### SQL Implementation

```sql
-- Aggregate on top of the session-splitting result
SELECT 
  user_id,
  session_id,
  MIN(event_time) AS session_start,
  MAX(event_time) AS session_end,
  TIMESTAMPDIFF(MINUTE, MIN(event_time), MAX(event_time)) AS session_duration_min,
  COUNT(*) AS page_views,
  COUNT(DISTINCT page) AS unique_pages,
  -- Bounce session: only 1 page view
  CASE WHEN COUNT(*) = 1 THEN 1 ELSE 0 END AS is_bounce,
  -- Conversion session: contains a target event
  MAX(CASE WHEN event_type IN ('add_to_cart', 'complete') THEN 1 ELSE 0 END) AS is_converted
FROM with_session
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

**Sample output**:

| user_id | session_id | session_start       | session_end         | duration_min | page_views | is_bounce | is_converted |
|---------|------------|---------------------|---------------------|--------------|------------|-----------|--------------|
| 1       | 1          | 2026-03-01 10:00:00 | 2026-03-01 10:15:00 | 15           | 3          | 0         | 0            |
| 1       | 2          | 2026-03-01 14:00:00 | 2026-03-01 14:10:00 | 10           | 2          | 0         | 0            |
| 2       | 1          | 2026-03-01 09:00:00 | 2026-03-01 09:00:00 | 0            | 1          | 1         | 0            |
| 2       | 2          | 2026-03-01 11:00:00 | 2026-03-01 11:12:00 | 12           | 5          | 0         | 1            |
| 3       | 1          | 2026-03-01 08:00:00 | 2026-03-01 08:30:00 | 30           | 7          | 0         | 1            |

---

## 3. Overall Session Statistics

### SQL Implementation

```sql
SELECT 
  COUNT(*) AS total_sessions,
  COUNT(DISTINCT user_id) AS unique_users,
  ROUND(AVG(page_views), 1) AS avg_pages_per_session,
  ROUND(AVG(session_duration_min), 1) AS avg_duration_min,
  ROUND(SUM(CASE WHEN page_views = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS bounce_rate_pct,
  ROUND(SUM(is_converted) * 100.0 / COUNT(*), 1) AS conversion_rate_pct
FROM session_agg;
```

**Sample output**:

| total_sessions | unique_users | avg_pages | avg_duration_min | bounce_rate | conversion_rate |
|----------------|--------------|-----------|------------------|-------------|-----------------|
| 5              | 3            | 3.6       | 13.4             | 20.0        | 40.0            |

---

## 4. User Path Analysis

### SQL Implementation

```sql
SELECT 
  user_id,
  session_id,
  GROUP_CONCAT(page ORDER BY event_time SEPARATOR ' → ') AS page_path,
  COUNT(*) AS path_length
FROM with_session
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

**Sample output**:

| user_id | session_id | page_path                                                    | path_length |
|---------|------------|--------------------------------------------------------------|-------------|
| 1       | 1          | home → products → product_detail                             | 3           |
| 1       | 2          | home → cart                                                  | 2           |
| 2       | 1          | landing                                                      | 1           |
| 2       | 2          | home → products → product_detail → cart → checkout           | 5           |
| 3       | 1          | home → products → product_detail → reviews → cart → checkout | 7           |

### Top Path Patterns

```sql
-- Find the 5 most common paths
SELECT 
  page_path,
  COUNT(*) AS session_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM (
  SELECT 
    user_id,
    session_id,
    GROUP_CONCAT(page ORDER BY event_time SEPARATOR ' → ') AS page_path
  FROM with_session
  GROUP BY user_id, session_id
)
GROUP BY page_path
ORDER BY session_count DESC
LIMIT 5;
```

---

## 5. Session Quality Segmentation

### Segmentation Criteria

| Tier | Page Views | Duration | Definition |
|---|---|---|---|
| Bounce | 1 | 0 min | Left after viewing a single page |
| Shallow | 2–3 | < 5 min | Quick browse |
| Medium | 4–6 | 5–15 min | Moderate engagement |
| Deep | 7+ | > 15 min | High engagement |

### SQL Implementation

```sql
SELECT 
  user_id,
  session_id,
  page_views,
  session_duration_min,
  CASE 
    WHEN page_views = 1 THEN 'bounce'
    WHEN page_views <= 3 AND session_duration_min < 5 THEN 'shallow'
    WHEN page_views <= 6 AND session_duration_min < 15 THEN 'medium'
    ELSE 'deep'
  END AS session_quality
FROM session_agg
ORDER BY user_id, session_id;
```

### Quality Distribution

```sql
SELECT 
  session_quality,
  COUNT(*) AS session_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM (
  SELECT 
    CASE 
      WHEN page_views = 1 THEN 'bounce'
      WHEN page_views <= 3 AND session_duration_min < 5 THEN 'shallow'
      WHEN page_views <= 6 AND session_duration_min < 15 THEN 'medium'
      ELSE 'deep'
    END AS session_quality
  FROM session_agg
)
GROUP BY session_quality
ORDER BY session_count DESC;
```

---

## 6. Advanced Scenarios

### Scenario 1: Session Quality by Traffic Source

```sql
SELECT 
  u.traffic_source,
  COUNT(DISTINCT s.session_id) AS sessions,
  ROUND(AVG(s.page_views), 1) AS avg_pages,
  ROUND(SUM(CASE WHEN s.page_views = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS bounce_rate
FROM session_agg s
JOIN users u ON s.user_id = u.user_id
GROUP BY u.traffic_source
ORDER BY bounce_rate;
```

### Scenario 2: Step Numbering Within a Session

```sql
-- Label each event's position within its session (step 1, step 2, ...)
SELECT 
  user_id,
  session_id,
  event_time,
  page,
  ROW_NUMBER() OVER (PARTITION BY user_id, session_id ORDER BY event_time) AS step_number,
  CASE 
    WHEN event_type = 'complete' THEN 'conversion'
    WHEN event_type = 'add_to_cart' THEN 'intent'
    ELSE 'browse'
  END AS event_category
FROM with_session
ORDER BY user_id, session_id, step_number;
```

### Scenario 3: Cross-Session User Behavior Analysis

> The following query builds on the `with_session` CTE result from Section 1.

```sql
-- Calculate total sessions and average gap between sessions per user
WITH session_times AS (
  SELECT 
    user_id,
    session_id,
    MIN(event_time) AS session_start
  FROM with_session
  GROUP BY user_id, session_id
),
session_gaps AS (
  SELECT 
    user_id,
    session_id,
    session_start,
    LAG(session_start) OVER (PARTITION BY user_id ORDER BY session_start) AS prev_session_start,
    TIMESTAMPDIFF(HOUR, LAG(session_start) OVER (PARTITION BY user_id ORDER BY session_start), session_start) AS hours_between_sessions
  FROM session_times
)
SELECT 
  user_id,
  COUNT(*) AS total_sessions,
  ROUND(AVG(hours_between_sessions), 1) AS avg_hours_between_sessions
FROM session_gaps
WHERE hours_between_sessions IS NOT NULL
GROUP BY user_id;
```

---

## Common Issues

### 1. `DATEDIFF` vs `TIMESTAMPDIFF`

```sql
-- Wrong: DATEDIFF on TIMESTAMP_LTZ returns the difference in days (events minutes apart show 0)
DATEDIFF(event_time, prev_event_time)  -- returns 0

-- Correct: use TIMESTAMPDIFF with an explicit unit
TIMESTAMPDIFF(MINUTE, prev_event_time, event_time)  -- returns 5
TIMESTAMPDIFF(SECOND, prev_event_time, event_time)  -- returns 300
TIMESTAMPDIFF(HOUR, prev_event_time, event_time)    -- returns 0
```

### 2. Choosing a Session Timeout Threshold

| Business Type | Recommended Threshold | Reason |
|---|---|---|
| E-commerce | 30 minutes | Users may leave to compare prices |
| Content / News | 15 minutes | Users leave after finishing an article |
| SaaS tools | 60 minutes | Users may work for extended periods |
| Gaming | 10 minutes | High activity frequency, short gaps |

### 3. Session Duration for Single-Page Sessions

```sql
-- Bounce sessions have session_start = session_end, so duration is 0.
-- This is correct. Do not use the gap between adjacent events as session duration.
-- Always use MIN/MAX of event_time within the session.
TIMESTAMPDIFF(MINUTE, MIN(event_time), MAX(event_time))  -- correct
```

### 4. `GROUP_CONCAT` Ordering

```sql
-- Wrong: without ORDER BY, path order is non-deterministic
GROUP_CONCAT(page SEPARATOR ' → ')

-- Correct: order by event_time to guarantee path sequence
GROUP_CONCAT(page ORDER BY event_time SEPARATOR ' → ')
```

### 5. Performance at Scale

```sql
-- Optimization: filter by date partition first, then split sessions
WITH filtered_events AS (
  SELECT * FROM user_events
  WHERE event_time >= '2026-03-01' AND event_time < '2026-03-02'
),
-- Remaining session-splitting logic is unchanged...
```

---

## Performance Optimization Tips

| Scenario | Strategy |
|---|---|
| Large-scale session splitting | Process day by day to avoid full-table window computations |
| High-frequency queries | Materialize session aggregation results as a Dynamic Table |
| Path analysis | Build a Bloom Filter index on `(user_id, event_time)` |
| Cross-midnight sessions | Use `DATE_TRUNC('DAY', event_time)` as an additional partition key |

```sql
-- Recommended: encapsulate session-splitting logic in a Dynamic Table
CREATE DYNAMIC TABLE dws_user_sessions
REFRESH INTERVAL 1 HOUR
AS
WITH with_prev AS (...),
     with_gap AS (...),
     with_session AS (...)
SELECT user_id, session_id, event_time, page, event_type
FROM with_session;
```
