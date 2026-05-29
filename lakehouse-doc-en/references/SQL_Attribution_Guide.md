# Attribution Modeling Guide

> **Scenario**: Allocate conversion value fairly across marketing channel touchpoints to evaluate the true contribution of each channel.
>
> **Core techniques**: `ROW_NUMBER` to label touchpoint order, `TIMESTAMPDIFF` to calculate time decay, `CASE` to implement multi-model weight assignment, window functions for normalization.

---

## Quick Reference

| Attribution Model | Weight Distribution | Best For | Complexity |
|---|---|---|---|
| First-Touch | 100% to the first touchpoint | Brand awareness, new user acquisition | ⭐⭐ |
| Last-Touch | 100% to the last touchpoint | Performance ads, conversion optimization | ⭐⭐ |
| Linear | Equal share across all touchpoints | Fair evaluation, initial analysis | ⭐⭐ |
| Time-Decay | Higher weight for touchpoints closer to conversion | Short decision cycles, promotion-driven | ⭐⭐⭐ |
| U-Shape (Position) | First 40% + Last 40% + Middle split evenly | Full-funnel evaluation, standard reporting | ⭐⭐⭐ |

---

## Sample Data

All examples in this guide are based on the following user touchpoint paths:

```sql
-- Marketing touchpoints table
CREATE TABLE marketing_touchpoints (
  user_id BIGINT,
  event_time TIMESTAMP_LTZ,
  channel VARCHAR,       -- organic_search, paid_ads, social_media, email, direct
  event_type VARCHAR     -- view, click, purchase
);

-- Conversion value table (sourced from the order system in production)
CREATE TABLE conversions (
  user_id BIGINT,
  conversion_value DECIMAL(10,2)
);

-- The Time-Decay model also requires a conversion timestamp.
-- Add a conversion_time column to the conversions table,
-- or retrieve it by joining the orders table in the query.
```

Sample touchpoint paths for 4 users:

| User | Touchpoint Path | Conversion Value |
|---|---|---|
| 1 | organic_search → social_media → paid_ads → purchase | $100 |
| 2 | paid_ads → email → purchase | $200 |
| 3 | social_media → organic_search → social_media → paid_ads → purchase | $150 |
| 4 | email → purchase | $50 |

---

## 1. First-Touch Attribution

### Rule

**100%** of the conversion value is attributed to the **first touchpoint** in the user journey.

### SQL Implementation

```sql
WITH touchpoints_ranked AS (
  SELECT 
    user_id,
    channel,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time) AS touch_order
  FROM marketing_touchpoints
  WHERE event_type != 'purchase'
),
first_channel AS (
  SELECT user_id, channel AS first_touch_channel
  FROM touchpoints_ranked
  WHERE touch_order = 1
)
SELECT 
  fc.first_touch_channel,
  COUNT(*) AS conversions,
  SUM(c.conversion_value) AS total_value,
  ROUND(SUM(c.conversion_value) * 100.0 / (SELECT SUM(conversion_value) FROM conversions), 1) AS value_share_pct
FROM first_channel fc
JOIN conversions c ON fc.user_id = c.user_id
GROUP BY fc.first_touch_channel
ORDER BY total_value DESC;
```

**Sample output**:

| first_touch_channel | conversions | total_value | value_share_pct |
|---|---|---|---|
| paid_ads | 1 | 200 | 40.0 |
| social_media | 1 | 150 | 30.0 |
| organic_search | 1 | 100 | 20.0 |
| email | 1 | 50 | 10.0 |

---

## 2. Last-Touch Attribution

### Rule

**100%** of the conversion value is attributed to the **last touchpoint** before conversion.

### SQL Implementation

```sql
WITH touchpoints_ranked AS (
  SELECT 
    user_id,
    channel,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC) AS touch_order_desc
  FROM marketing_touchpoints
  WHERE event_type != 'purchase'
),
last_channel AS (
  SELECT user_id, channel AS last_touch_channel
  FROM touchpoints_ranked
  WHERE touch_order_desc = 1
)
SELECT 
  lc.last_touch_channel,
  COUNT(*) AS conversions,
  SUM(c.conversion_value) AS total_value,
  ROUND(SUM(c.conversion_value) * 100.0 / (SELECT SUM(conversion_value) FROM conversions), 1) AS value_share_pct
FROM last_channel lc
JOIN conversions c ON lc.user_id = c.user_id
GROUP BY lc.last_touch_channel
ORDER BY total_value DESC;
```

**Sample output**:

| last_touch_channel | conversions | total_value | value_share_pct |
|---|---|---|---|
| paid_ads | 2 | 250 | 50.0 |
| email | 2 | 250 | 50.0 |

---

## 3. Linear Attribution

### Rule

The conversion value is **split equally** across all touchpoints.

### SQL Implementation

```sql
WITH touch_counts AS (
  SELECT user_id, COUNT(*) AS touch_count
  FROM marketing_touchpoints
  WHERE event_type != 'purchase'
  GROUP BY user_id
),
attribution AS (
  SELECT 
    t.user_id,
    t.channel,
    c.conversion_value / tc.touch_count AS attributed_value
  FROM marketing_touchpoints t
  JOIN conversions c ON t.user_id = c.user_id
  JOIN touch_counts tc ON t.user_id = tc.user_id
  WHERE t.event_type != 'purchase'
)
SELECT 
  channel,
  COUNT(*) AS touch_count,
  ROUND(SUM(attributed_value), 2) AS total_attributed_value,
  ROUND(SUM(attributed_value) * 100.0 / (SELECT SUM(conversion_value) FROM conversions), 1) AS value_share_pct
FROM attribution
GROUP BY channel
ORDER BY total_attributed_value DESC;
```

**Sample output**:

| channel | touch_count | total_attributed_value | value_share_pct |
|---|---|---|---|
| paid_ads | 3 | 170.83 | 34.2 |
| email | 2 | 150.00 | 30.0 |
| social_media | 3 | 108.33 | 21.7 |
| organic_search | 2 | 70.83 | 14.2 |

---

## 4. Time-Decay Attribution

### Rule

Touchpoints closer to the conversion receive higher weight, using **exponential decay**:

```
weight = 2^(-hours_to_conversion / half_life_hours)
```

The default half-life is 24 hours (a touchpoint 1 day before conversion receives half the weight of one at conversion time).

### SQL Implementation

```sql
WITH conversions AS (
  -- In production, retrieve conversion times from the orders table
  SELECT 1 AS user_id, '2026-03-02 10:30:00' AS conversion_time, 100.0 AS conversion_value UNION ALL
  SELECT 2, '2026-03-02 09:00:00', 200.0 UNION ALL
  SELECT 3, '2026-03-02 14:30:00', 150.0 UNION ALL
  SELECT 4, '2026-03-01 12:30:00', 50.0
),
touch_with_decay AS (
  SELECT 
    t.user_id,
    t.channel,
    c.conversion_value,
    TIMESTAMPDIFF(HOUR, CAST(t.event_time AS TIMESTAMP_LTZ), CAST(c.conversion_time AS TIMESTAMP_LTZ)) AS hours_to_conversion,
    -- Exponential decay weight: 2^(-hours/24), half-life = 24 hours
    POW(2, -TIMESTAMPDIFF(HOUR, CAST(t.event_time AS TIMESTAMP_LTZ), CAST(c.conversion_time AS TIMESTAMP_LTZ)) / 24.0) AS decay_weight
  FROM marketing_touchpoints t
  JOIN conversions c ON t.user_id = c.user_id
  WHERE t.event_type != 'purchase'
),
normalized AS (
  SELECT 
    user_id,
    channel,
    conversion_value,
    decay_weight,
    decay_weight / SUM(decay_weight) OVER (PARTITION BY user_id) AS normalized_weight
  FROM touch_with_decay
)
SELECT 
  channel,
  COUNT(*) AS touch_count,
  ROUND(SUM(conversion_value * normalized_weight), 2) AS total_attributed_value,
  ROUND(SUM(conversion_value * normalized_weight) * 100.0 / (SELECT SUM(conversion_value) FROM conversions), 1) AS value_share_pct
FROM normalized
GROUP BY channel
ORDER BY total_attributed_value DESC;
```

**Sample output**:

| channel | touch_count | total_attributed_value | value_share_pct |
|---|---|---|---|
| paid_ads | 3 | 190.90 | 38.2 |
| email | 2 | 161.50 | 32.3 |
| social_media | 3 | 96.30 | 19.3 |
| organic_search | 2 | 51.29 | 10.3 |

### Choosing a Half-Life

| Business Type | Recommended Half-Life | Reason |
|---|---|---|
| E-commerce promotions | 6–12 hours | Short decision cycle |
| SaaS trials | 24–48 hours | Medium decision cycle |
| B2B sales | 72–168 hours | Long decision cycle |

---

## 5. U-Shape (Position-Based) Attribution

### Rule

| Touchpoint Position | Weight |
|---|---|
| First touchpoint | 40% |
| Last touchpoint | 40% |
| Middle touchpoints | Split the remaining 20% equally |

**Special cases**:
- Single touchpoint: 100%
- Two touchpoints: 50% each

### SQL Implementation

```sql
WITH touchpoints_ranked AS (
  SELECT 
    t.user_id,
    t.channel,
    c.conversion_value,
    ROW_NUMBER() OVER (PARTITION BY t.user_id ORDER BY t.event_time) AS touch_order,
    COUNT(*) OVER (PARTITION BY t.user_id) AS total_touches
  FROM marketing_touchpoints t
  JOIN conversions c ON t.user_id = c.user_id
  WHERE t.event_type != 'purchase'
),
attribution AS (
  SELECT 
    user_id,
    channel,
    conversion_value,
    CASE 
      WHEN total_touches = 1 THEN 1.0
      WHEN total_touches = 2 THEN 0.5
      WHEN touch_order = 1 THEN 0.4
      WHEN touch_order = total_touches THEN 0.4
      ELSE 0.2 / (total_touches - 2)
    END AS weight
  FROM touchpoints_ranked
)
SELECT 
  channel,
  COUNT(*) AS touch_count,
  ROUND(SUM(conversion_value * weight), 2) AS total_attributed_value,
  ROUND(SUM(conversion_value * weight) * 100.0 / (SELECT SUM(conversion_value) FROM conversions), 1) AS value_share_pct
FROM attribution
GROUP BY channel
ORDER BY total_attributed_value DESC;
```

**Sample output**:

| channel | touch_count | total_attributed_value | value_share_pct |
|---|---|---|---|
| paid_ads | 3 | 200.00 | 40.0 |
| email | 2 | 150.00 | 30.0 |
| social_media | 3 | 95.00 | 19.0 |
| organic_search | 2 | 55.00 | 11.0 |

---

## 6. Multi-Model Comparison

### Compare All Models at Once

```sql
-- Combine results from all models for side-by-side comparison
WITH first_touch AS (
  -- First-touch attribution results
  SELECT channel, ROUND(SUM(conversion_value), 2) AS first_touch_value
  FROM (
    SELECT user_id, channel, conversion_value
    FROM touchpoints_ranked tr
    JOIN conversions c ON tr.user_id = c.user_id
    WHERE touch_order = 1
  )
  GROUP BY channel
),
last_touch AS (
  -- Last-touch attribution results
  SELECT channel, ROUND(SUM(conversion_value), 2) AS last_touch_value
  FROM (
    SELECT user_id, channel, conversion_value
    FROM touchpoints_ranked tr
    JOIN conversions c ON tr.user_id = c.user_id
    WHERE touch_order = total_touches
  )
  GROUP BY channel
)
-- Merge for comparison...
```

---

## Common Issues

### 1. Excluding the Conversion Event Itself

```sql
-- Wrong: includes the purchase event as a touchpoint
WHERE event_type IN ('view', 'click', 'purchase')

-- Correct: exclude the conversion event
WHERE event_type != 'purchase'
```

### 2. Division by Zero in U-Shape with 2 Touchpoints

```sql
-- Wrong: when total_touches = 2, 0.2 / (2 - 2) causes a divide-by-zero error
ELSE 0.2 / (total_touches - 2)

-- Correct: handle the 2-touchpoint case separately
WHEN total_touches = 2 THEN 0.5
```

### 3. The `POW` Function for Time Decay

```sql
-- Correct: POW(base, exponent)
POW(2, -hours / 24.0)

-- Note: 24.0 must be a float; integer division truncates to 0
POW(2, -hours / 24)  -- Wrong: hours/24 may evaluate to 0
```

### 4. Single-Touch vs Multi-Touch Users

```sql
-- Recommended: segment users by journey type in your analysis
SELECT 
  CASE WHEN total_touches = 1 THEN 'single_touch'
       WHEN total_touches <= 3 THEN 'multi_touch'
       ELSE 'high_touch'
  END AS journey_type,
  COUNT(*) AS user_count
FROM touchpoints_ranked
GROUP BY 1;
```

### 5. Attribution Lookback Window

```sql
-- Limit attribution to touchpoints within the last 30 days
WHERE TIMESTAMPDIFF(DAY, CAST(t.event_time AS TIMESTAMP_LTZ), CAST(c.conversion_time AS TIMESTAMP_LTZ)) <= 30
```

---

## Model Selection Guide

| Business Goal | Recommended Model | Reason |
|---|---|---|
| Evaluate new user acquisition channels | First-Touch | Reflects a channel's ability to attract new users |
| Optimize the conversion funnel | Last-Touch | Reflects the channel that closes the deal |
| Allocate budget fairly | Linear | Treats all touchpoints equally |
| Short-cycle promotions | Time-Decay | Recent touchpoints have greater influence |
| Full-funnel ROI reporting | U-Shape | Balances first, last, and middle touchpoints |

---

## Performance Optimization Tips

| Scenario | Strategy |
|---|---|
| Large-scale attribution | Partition by conversion date and limit the lookback window |
| Running multiple models in parallel | Materialize touchpoint rankings as a Dynamic Table |
| High-frequency queries | Pre-compute attribution results and refresh daily |

```sql
-- Recommended: materialize touchpoint rankings as a Dynamic Table
CREATE DYNAMIC TABLE dws_touchpoints_ranked
REFRESH INTERVAL 1 HOUR
AS
SELECT 
  t.user_id,
  t.channel,
  t.event_time,
  t.event_type,
  ROW_NUMBER() OVER (PARTITION BY t.user_id ORDER BY t.event_time) AS touch_order,
  COUNT(*) OVER (PARTITION BY t.user_id) AS total_touches
FROM marketing_touchpoints t
WHERE event_type != 'purchase';
```
