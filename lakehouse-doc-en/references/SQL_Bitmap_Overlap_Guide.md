# Group Bitmap User Overlap Analysis: Practical Guide

> **Scenario**: Achieve **sub-second** funnel conversion calculation, retention analysis, multi-dimensional audience segmentation, and A/B test audience isolation checks on massive user datasets (hundreds of millions of records).
>
> **Core technique**: Use Bitmap bitwise operations (AND/OR/XOR) to replace traditional `JOIN` or `COUNT DISTINCT`, reducing computational complexity from O(N) to O(1) — a performance improvement of over 100x.

---

## Why Choose Bitmap?

| Analysis scenario | Traditional SQL approach | Bitmap approach | Performance comparison (100M users) |
|---|---|---|---|
| **Funnel conversion** | Multi-table `JOIN` + `COUNT DISTINCT` | `bitmap_and` + `bitmap_cardinality` | Traditional: ~30s / Bitmap: <0.1s |
| **Retention analysis** | Self-join + date filter | Generate Bitmap per day, bitwise AND | Traditional: ~15s / Bitmap: <0.1s |
| **Multi-dimensional segmentation** | Dynamic `WHERE` condition aggregation | Pre-compute tag Bitmaps, real-time bitwise ops | Traditional: ~5s / Bitmap: <0.05s |
| **A/B test isolation** | `INTERSECT` or `IN` subquery | `bitmap_and` to check if cardinality is 0 | Traditional: ~2s / Bitmap: <0.01s |

---

## Core Function Reference

| Function | Purpose | Return type | Use case |
|---|---|---|---|
| `group_bitmap_state` | Generate a user Bitmap object | BITMAP | Pre-compute user sets by tag/channel/step |
| `bitmap_and` | Compute intersection | BITMAP | Funnel conversion, retained users, audience intersection |
| `bitmap_or` | Compute union | BITMAP | Total reach, audience merge |
| `bitmap_xor` | Compute symmetric difference | BITMAP | New users, churned users, A/B isolation check |
| `bitmap_cardinality` | Count elements in a Bitmap | BIGINT | Get final unique user count (UV) |

---

## Prerequisites

```sql
-- User behavior event log table
CREATE TABLE user_events (
  user_id BIGINT,
  event_name VARCHAR(50),
  event_date DATE,
  channel VARCHAR(20)
);

-- Sample funnel data: view -> cart -> pay
INSERT INTO user_events VALUES
  (1, 'view', CAST('2026-05-01' AS DATE), 'app'), (1, 'cart', CAST('2026-05-01' AS DATE), 'app'), (1, 'pay', CAST('2026-05-01' AS DATE), 'app'),
  (2, 'view', CAST('2026-05-01' AS DATE), 'app'), (2, 'cart', CAST('2026-05-01' AS DATE), 'app'),
  (3, 'view', CAST('2026-05-01' AS DATE), 'app'),
  (4, 'view', CAST('2026-05-01' AS DATE), 'web'), (4, 'cart', CAST('2026-05-01' AS DATE), 'web'), (4, 'pay', CAST('2026-05-01' AS DATE), 'web'),
  (5, 'view', CAST('2026-05-02' AS DATE), 'app'), (5, 'cart', CAST('2026-05-02' AS DATE), 'app'),
  (1, 'view', CAST('2026-05-02' AS DATE), 'app'), (1, 'pay', CAST('2026-05-02' AS DATE), 'app');
```

---

## Scenario 1: Funnel Conversion Analysis (Sub-second)

### Problem

Calculate the conversion rate for "view -> cart -> pay". Traditional SQL requires multiple `JOIN`s, which easily times out on large datasets.

### Bitmap Implementation

```sql
WITH funnel_steps AS (
  SELECT
    -- Generate a Bitmap for each funnel step
    group_bitmap_state(CASE WHEN event_name = 'view' THEN user_id END) AS step_view,
    group_bitmap_state(CASE WHEN event_name = 'cart' THEN user_id END) AS step_cart,
    group_bitmap_state(CASE WHEN event_name = 'pay'  THEN user_id END) AS step_pay
  FROM user_events
  WHERE event_date = CAST('2026-05-01' AS DATE)
)
SELECT
  bitmap_cardinality(step_view) AS view_uv,
  bitmap_cardinality(step_cart) AS cart_uv,
  bitmap_cardinality(step_pay)  AS pay_uv,
  -- Conversion rate: current step count / previous step count
  ROUND(bitmap_cardinality(step_cart) * 100.0 / bitmap_cardinality(step_view), 2) AS view_to_cart_rate,
  ROUND(bitmap_cardinality(step_pay)  * 100.0 / bitmap_cardinality(step_cart), 2) AS cart_to_pay_rate
FROM funnel_steps;
```

**Output**:

| view_uv | cart_uv | pay_uv | view_to_cart_rate | cart_to_pay_rate |
|---------|---------|--------|-------------------|------------------|
| 4 | 3 | 2 | 75.00 | 66.67 |

> **Advantage**: Regardless of whether the data volume is 1 million or 1 billion, bitwise operation time is nearly constant and always completes in milliseconds.

---

## Scenario 2: Retained User Analysis (N-day Retention)

### Problem

Calculate how many users active on May 1 were also active on May 2 and May 3.

### Bitmap Implementation

```sql
WITH daily_users AS (
  -- Aggregate by day to generate Bitmaps
  SELECT event_date, group_bitmap_state(user_id) AS daily_bm
  FROM user_events
  GROUP BY event_date
),
base_day AS (
  SELECT daily_bm AS base_bm FROM daily_users WHERE event_date = CAST('2026-05-01' AS DATE)
)
SELECT
  d.event_date,
  bitmap_cardinality(d.daily_bm) AS daily_uv,
  -- Retention: intersection of the current day's Bitmap with the baseline day's Bitmap
  bitmap_cardinality(bitmap_and(d.daily_bm, b.base_bm)) AS retained_uv,
  ROUND(bitmap_cardinality(bitmap_and(d.daily_bm, b.base_bm)) * 100.0 / bitmap_cardinality(b.base_bm), 2) AS retention_rate
FROM daily_users d
CROSS JOIN base_day b
WHERE d.event_date >= CAST('2026-05-01' AS DATE)
ORDER BY d.event_date;
```

**Output**:

| event_date | daily_uv | retained_uv | retention_rate |
|------------|----------|-------------|----------------|
| 2026-05-01 | 4 | 4 | 100.00 |
| 2026-05-02 | 2 | 1 | 25.00 |

---

## Scenario 3: Real-time Multi-dimensional Audience Segmentation (Ad-Hoc Query)

### Problem

A marketer needs to query in real time: "How many users came from the App channel and made a payment?"

### Bitmap Implementation

**Step 1: Pre-compute tag Bitmaps (Dynamic Table or scheduled job)**

```sql
-- Example: pre-compute Bitmaps by channel and event type
CREATE TABLE tag_bitmaps AS
SELECT
  channel,
  event_name,
  group_bitmap_state(user_id) AS bm
FROM user_events
GROUP BY channel, event_name;
```

**Step 2: Real-time query (millisecond response)**

```sql
-- Query: users from the App channel who also made a payment
-- Logic: (Bitmap of all App users) AND (Bitmap of all paying users)
WITH app_users AS (
  SELECT group_bitmap_state(user_id) AS bm FROM user_events WHERE channel = 'app'
),
pay_users AS (
  SELECT group_bitmap_state(user_id) AS bm FROM user_events WHERE event_name = 'pay'
)
SELECT
  bitmap_cardinality(bitmap_and(a.bm, b.bm)) AS target_uv
FROM app_users a, pay_users b;
```

**Output**:

| target_uv |
|-----------|
| 2         |

> **Advantage**: No need to scan the raw event log table. Bitwise operations run directly on the pre-computed Bitmap table and support any combination of dimensions.

---

## Scenario 4: A/B Test Audience Isolation Check

### Problem

Verify that the control group and treatment group in an A/B test do not share any users (overlap contaminates experiment results).

### Bitmap Implementation

```sql
WITH groups AS (
  SELECT
    group_bitmap_state(CASE WHEN group_name = 'control'   THEN user_id END) AS control_bm,
    group_bitmap_state(CASE WHEN group_name = 'treatment' THEN user_id END) AS treatment_bm
  FROM ab_test_users
)
SELECT
  bitmap_cardinality(bitmap_and(control_bm, treatment_bm)) AS overlap_count,
  CASE
    WHEN bitmap_cardinality(bitmap_and(control_bm, treatment_bm)) > 0 THEN '⚠️ Overlap detected — experiment invalid'
    ELSE '✅ Audiences are isolated — experiment valid'
  END AS check_result
FROM groups;
```

**Output**:

| overlap_count | check_result |
|---------------|--------------|
| 0 | ✅ Audiences are isolated — experiment valid |

---

## Common Issues

### 1. `group_bitmap` vs `group_bitmap_state`

```sql
-- Wrong: group_bitmap returns a cardinality (INT) and cannot be used in bitwise operations
SELECT bitmap_and(group_bitmap(user_id), ...) -- error

-- Correct: use group_bitmap_state to produce a Bitmap object
SELECT bitmap_and(group_bitmap_state(user_id), ...)
```

### 2. Handling negative IDs

```sql
-- Bitmap only supports non-negative integers. If user_id contains negatives or strings, convert first.
-- Wrong: group_bitmap_state(user_id) WHERE user_id = -1
-- Correct: ensure ID >= 0, or use a hash function to convert to a positive integer
SELECT group_bitmap_state(abs(hash(user_id))) FROM users;
```

### 3. Memory limits

```sql
-- A single Bitmap object is usually small in memory (compressed), but in extreme cases
-- (e.g., the full user base) it may consume significant memory.
-- Recommendation: shard Bitmaps by time or business domain to avoid oversized single Bitmaps.
```

---

## Performance Optimization Tips

| Scenario | Optimization strategy |
|---|---|
| **High-frequency queries** | Store Bitmap results in a Dynamic Table with `REFRESH INTERVAL 1 HOUR` for automatic updates |
| **Storage optimization** | Store Bitmap columns using the `BITMAP` type; Singdata Lakehouse automatically applies RoaringBitmap compression |
| **Query acceleration** | Build a Bloom Filter index on Bitmap columns to speed up `bitmap_cardinality` queries |

```sql
-- Recommended architecture: ODS -> DWD (detail) -> DWS (Bitmap aggregation) -> ADS (application queries)
CREATE DYNAMIC TABLE dws_user_bitmaps
REFRESH INTERVAL 1 HOUR
AS
SELECT
  DATE_TRUNC('DAY', event_time) AS event_date,
  channel,
  group_bitmap_state(user_id) AS user_bm
FROM dwd_user_events
GROUP BY 1, 2;
```

---

## Related Documents

* [BITMAP Function Reference](bitmap_function.md)
* [Aggregate Function Reference](agg_function.md)
* [User Behavior Analysis and Precision Marketing: BITMAP Practical Guide](bitmap_uba_guide.md)
* [Retention and Cohort Analysis](SQL_Retention_Cohort_Guide.md)
