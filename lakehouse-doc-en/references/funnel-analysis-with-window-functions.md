# User Behavior Funnel Analysis: Tracking Conversions from Impression to Order

## Business Background

After a promotion goes live, the operations team's biggest concern is usually not "how much did we sell" but "where are we losing users." 100 users saw a product, but only 3 placed an order — was the click-through rate too low, did users abandon after adding to cart, or was there a problem on the checkout page?

Funnel analysis breaks user behavior into an ordered sequence of steps (impression → click → add-to-cart → order), counts the number of users and conversion rate at each step, and pinpoints the stage with the highest drop-off.

Typical use cases:

- **Post-promotion review**: After a campaign ends, compare funnel differences across products to identify underperforming SKUs
- **Page optimization decisions**: High click-through but low add-to-cart rate suggests the product detail page lacks persuasiveness; high add-to-cart but low order rate suggests friction in the checkout flow
- **Real-time monitoring**: During an active campaign, refresh funnel data every minute and intervene immediately when anomalies are detected

## Use Cases

| Scenario | Description |
|------|------|
| E-commerce promotion funnel | Impression → click → add-to-cart → order; identify the step with the highest drop-off |
| Registration conversion funnel | Visit landing page → fill form → verify phone → complete registration |
| Content consumption funnel | Push impression → open → finish reading → share |
| A/B test comparison | Compare conversion differences between test and control groups at each step |

## SQL Commands Involved

| Command / Function | Purpose |
|------------|------|
| `COUNT(DISTINCT user_id)` | Count deduplicated users (UV) per step |
| `LAG()` | Retrieve the UV of the previous step to calculate step-over-step conversion rate |
| `FIRST_VALUE()` | Retrieve the UV of the first funnel step to calculate overall conversion rate |
| `PARTITION BY` | Group by dimensions such as product or time period to compute independent funnels |
| `CREATE DYNAMIC TABLE` | Wrap the funnel query into an auto-refreshing real-time dashboard |

## Data Architecture

```
External data sources (tracking SDK / log system / Kafka / ...)
              │  real-time writes
              ▼
doc_user_events (user behavior events table)
              │
              │  window function aggregation
              ▼
doc_ads_funnel_overview (Dynamic Table, auto-refreshes every 1 minute)
              │
              ▼
BI dashboard / operations screen
```

**How event data is written in real time**

This guide uses `INSERT INTO` to simulate user behavior events so you can quickly reproduce the examples in a test environment. In production, user behavior data typically comes from client-side tracking or server-side logs. Singdata Lakehouse provides multiple ways to continuously ingest this data:

| Data source | Recommended method | Description | Reference |
|---------|---------|------|---------|
| Kafka message queue (real-time tracking events) | Pipe continuous ingestion | Suitable when a client SDK sends events to Kafka; millisecond-level latency | [Continuous ingestion with the read_kafka function](pipe-kafka.md) |
| Object storage (log files on disk) | Pipe continuous ingestion | Suitable when server-side logs are periodically written to OSS / COS / S3 | [Continuous ingestion from object storage with Pipe](pipe-storage-object.md) |
| Business databases (orders, click records) | Studio real-time sync task (CDC) | Captures source database binlog and syncs to Lakehouse with millisecond-level latency | [Real-time sync task](realtime_sync.md) |

After new events are written to the base table, the Dynamic Table automatically detects them and performs an incremental computation in the next refresh cycle — no manual trigger needed.

## Prerequisites

### Create the User Behavior Events Table

```sql
CREATE TABLE IF NOT EXISTS doc_user_events (
    event_id   STRING,
    user_id    STRING,
    session_id STRING,
    event_type STRING,
    product_id STRING,
    event_time TIMESTAMP
);
```

`event_type` takes the values `expose` (impression), `click`, `cart` (add-to-cart), and `order`, representing the four funnel steps.

### Insert Test Event Data

```sql
INSERT INTO doc_user_events VALUES
  ('E001','U101','S001','expose','P001', CAST('2026-05-28 10:00:00' AS TIMESTAMP)),
  ('E002','U101','S001','click', 'P001', CAST('2026-05-28 10:01:00' AS TIMESTAMP)),
  ('E003','U101','S001','cart',  'P001', CAST('2026-05-28 10:03:00' AS TIMESTAMP)),
  ('E004','U101','S001','order', 'P001', CAST('2026-05-28 10:05:00' AS TIMESTAMP)),
  ('E005','U102','S002','expose','P001', CAST('2026-05-28 10:10:00' AS TIMESTAMP)),
  ('E006','U102','S002','click', 'P001', CAST('2026-05-28 10:11:00' AS TIMESTAMP)),
  ('E007','U102','S002','cart',  'P001', CAST('2026-05-28 10:15:00' AS TIMESTAMP)),
  ('E008','U103','S003','expose','P002', CAST('2026-05-28 10:20:00' AS TIMESTAMP)),
  ('E009','U103','S003','click', 'P002', CAST('2026-05-28 10:21:00' AS TIMESTAMP)),
  ('E010','U104','S004','expose','P001', CAST('2026-05-28 10:30:00' AS TIMESTAMP)),
  ('E011','U105','S005','expose','P002', CAST('2026-05-28 10:35:00' AS TIMESTAMP)),
  ('E012','U105','S005','click', 'P002', CAST('2026-05-28 10:36:00' AS TIMESTAMP)),
  ('E013','U105','S005','order', 'P002', CAST('2026-05-28 10:40:00' AS TIMESTAMP)),
  ('E014','U106','S006','expose','P003', CAST('2026-05-28 11:00:00' AS TIMESTAMP)),
  ('E015','U106','S006','click', 'P003', CAST('2026-05-28 11:02:00' AS TIMESTAMP)),
  ('E016','U106','S006','cart',  'P003', CAST('2026-05-28 11:05:00' AS TIMESTAMP)),
  ('E017','U106','S006','order', 'P003', CAST('2026-05-28 11:08:00' AS TIMESTAMP)),
  ('E018','U107','S007','expose','P003', CAST('2026-05-28 11:10:00' AS TIMESTAMP)),
  ('E019','U108','S008','expose','P001', CAST('2026-05-28 11:15:00' AS TIMESTAMP)),
  ('E020','U108','S008','click', 'P001', CAST('2026-05-28 11:16:00' AS TIMESTAMP));
```

## Scenario 1: Overall Funnel Conversion Rate

Count the UV at each step across all users, and calculate the step-over-step conversion rate (each step relative to the previous) and the overall conversion rate (each step relative to impressions).

```sql
WITH funnel AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) AS uv,
        CASE event_type
            WHEN 'expose' THEN 1
            WHEN 'click'  THEN 2
            WHEN 'cart'   THEN 3
            WHEN 'order'  THEN 4
        END AS step
    FROM doc_user_events
    GROUP BY event_type
)
SELECT
    step,
    event_type,
    uv,
    LAG(uv) OVER (ORDER BY step)                                     AS prev_uv,
    CAST(uv * 100.0 / LAG(uv) OVER (ORDER BY step) AS DECIMAL(5,1)) AS step_cvr,
    CAST(uv * 100.0 / FIRST_VALUE(uv) OVER (ORDER BY step) AS DECIMAL(5,1)) AS total_cvr
FROM funnel
ORDER BY step;
```

```
+----+----------+--+-------+---------+---------+
|step|event_type|uv|prev_uv|step_cvr |total_cvr|
+----+----------+--+-------+---------+---------+
|1   |expose    |8 |NULL   |NULL     |100.0    |
|2   |click     |6 |8      |75.0     |75.0     |
|3   |cart      |3 |6      |50.0     |37.5     |
|4   |order     |3 |3      |100.0    |37.5     |
+----+----------+--+-------+---------+---------+
```

Result interpretation:

- Impression → click: 75% of users clicked on the product — a normal click-through rate
- Click → add-to-cart: Only 50% of users added to cart, making this the step with the highest drop-off — the product detail page may lack persuasiveness
- Add-to-cart → order: 100% of users who added to cart completed the order — no friction in the checkout flow
- Overall conversion rate: 3 out of 8 users who saw the impression placed an order, for an overall conversion rate of 37.5%

`LAG(uv) OVER (ORDER BY step)` retrieves the UV from the previous step. The first step (expose) has no previous step, so `prev_uv` and `step_cvr` are NULL — this is expected.

## Scenario 2: Per-Product Funnel Comparison

Identify conversion differences across products to locate underperforming SKUs.

```sql
WITH funnel AS (
    SELECT
        product_id,
        event_type,
        COUNT(DISTINCT user_id) AS uv,
        CASE event_type
            WHEN 'expose' THEN 1
            WHEN 'click'  THEN 2
            WHEN 'cart'   THEN 3
            WHEN 'order'  THEN 4
        END AS step
    FROM doc_user_events
    GROUP BY product_id, event_type
)
SELECT
    product_id,
    step,
    event_type,
    uv,
    CAST(uv * 100.0 / FIRST_VALUE(uv) OVER (PARTITION BY product_id ORDER BY step) AS DECIMAL(5,1)) AS total_cvr
FROM funnel
ORDER BY product_id, step;
```

```
+----------+----+----------+--+---------+
|product_id|step|event_type|uv|total_cvr|
+----------+----+----------+--+---------+
|P001      |1   |expose    |4 |100.0    |
|P001      |2   |click     |3 |75.0     |
|P001      |3   |cart      |2 |50.0     |
|P001      |4   |order     |1 |25.0     |
|P002      |1   |expose    |2 |100.0    |
|P002      |2   |click     |2 |100.0    |
|P002      |4   |order     |1 |50.0     |
|P003      |1   |expose    |2 |100.0    |
|P003      |2   |click     |1 |50.0     |
|P003      |3   |cart      |1 |50.0     |
|P003      |4   |order     |1 |50.0     |
+----------+----+----------+--+---------+
```

Result interpretation:

- **P001**: Click-through rate 75%, but only 25% overall conversion from add-to-cart to order — significant drop-off after adding to cart
- **P002**: Click-through rate 100%, and no add-to-cart step (users went directly from click to order) — this is normal and indicates a shorter purchase decision path for this product, or that the add-to-cart event was not covered by tracking
- **P003**: Click-through rate of only 50%, the lowest among the three products — the product detail page needs to be more compelling

`PARTITION BY product_id` lets each product independently compute `FIRST_VALUE` (its own impression UV), so conversion rates do not interfere with each other.

## Scenario 3: Building a Real-Time Funnel Dashboard with Dynamic Table

Wrap the overall funnel query into a Dynamic Table that auto-refreshes every minute, so the operations dashboard can query the result table directly.

```sql
CREATE OR REPLACE DYNAMIC TABLE doc_ads_funnel_overview
REFRESH INTERVAL '1' MINUTE VCLUSTER default
AS
WITH funnel AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) AS uv,
        CASE event_type
            WHEN 'expose' THEN 1
            WHEN 'click'  THEN 2
            WHEN 'cart'   THEN 3
            WHEN 'order'  THEN 4
        END AS step
    FROM doc_user_events
    GROUP BY event_type
)
SELECT
    step,
    event_type,
    uv,
    CAST(uv * 100.0 / FIRST_VALUE(uv) OVER (ORDER BY step) AS DECIMAL(5,1)) AS total_cvr
FROM funnel;
```

Wait about 1 minute, then query:

```sql
SELECT * FROM doc_ads_funnel_overview ORDER BY step;
```

```
+----+----------+--+---------+
|step|event_type|uv|total_cvr|
+----+----------+--+---------+
|1   |expose    |8 |100.0    |
|2   |click     |6 |75.0     |
|3   |cart      |3 |37.5     |
|4   |order     |3 |37.5     |
+----+----------+--+---------+
```

After new events are written, the Dynamic Table automatically updates in the next refresh cycle. Simulate a new batch of user behavior:

```sql
INSERT INTO doc_user_events VALUES
  ('E021','U109','S009','expose','P001', CAST('2026-05-28 12:00:00' AS TIMESTAMP)),
  ('E022','U109','S009','click', 'P001', CAST('2026-05-28 12:01:00' AS TIMESTAMP)),
  ('E023','U109','S009','cart',  'P001', CAST('2026-05-28 12:03:00' AS TIMESTAMP)),
  ('E024','U109','S009','order', 'P001', CAST('2026-05-28 12:05:00' AS TIMESTAMP)),
  ('E025','U110','S010','expose','P002', CAST('2026-05-28 12:10:00' AS TIMESTAMP)),
  ('E026','U110','S010','click', 'P002', CAST('2026-05-28 12:11:00' AS TIMESTAMP));
```

Wait about 1 minute — the funnel updates automatically:

```
+----+----------+--+---------+
|step|event_type|uv|total_cvr|
+----+----------+--+---------+
|1   |expose    |10|100.0    |
|2   |click     |8 |80.0     |
|3   |cart      |4 |40.0     |
|4   |order     |4 |40.0     |
+----+----------+--+---------+
```

Impression UV increased from 8 to 10, click-through rate rose from 75% to 80%, and overall conversion rate improved from 37.5% to 40% — the new batch of users converted at a higher rate.

## Scenario 4: Comparing Funnels by Time Period

Compare conversion differences between morning and afternoon to assess user quality across time slots.

```sql
WITH funnel AS (
    SELECT
        CASE WHEN HOUR(event_time) < 12 THEN 'Morning (10-12)' ELSE 'Afternoon (12+)' END AS time_slot,
        event_type,
        COUNT(DISTINCT user_id) AS uv,
        CASE event_type
            WHEN 'expose' THEN 1
            WHEN 'click'  THEN 2
            WHEN 'cart'   THEN 3
            WHEN 'order'  THEN 4
        END AS step
    FROM doc_user_events
    GROUP BY time_slot, event_type
)
SELECT
    time_slot,
    step,
    event_type,
    uv,
    CAST(uv * 100.0 / FIRST_VALUE(uv) OVER (PARTITION BY time_slot ORDER BY step) AS DECIMAL(5,1)) AS total_cvr
FROM funnel
ORDER BY time_slot, step;
```

```
+-----------------+----+----------+--+---------+
|time_slot        |step|event_type|uv|total_cvr|
+-----------------+----+----------+--+---------+
|Morning (10-12)  |1   |expose    |8 |100.0    |
|Morning (10-12)  |2   |click     |6 |75.0     |
|Morning (10-12)  |3   |cart      |3 |37.5     |
|Morning (10-12)  |4   |order     |3 |37.5     |
|Afternoon (12+)  |1   |expose    |2 |100.0    |
|Afternoon (12+)  |2   |click     |2 |100.0    |
|Afternoon (12+)  |3   |cart      |1 |50.0     |
|Afternoon (12+)  |4   |order     |1 |50.0     |
+-----------------+----+----------+--+---------+
```

Result interpretation: The afternoon time slot has a higher click-through rate (100%) and overall conversion rate (50%) than the morning (75% / 37.5%), indicating that afternoon users have stronger purchase intent. Consider increasing push volume during afternoon hours.

`PARTITION BY time_slot` lets each time period independently compute its conversion rate. `FIRST_VALUE(uv) OVER (PARTITION BY time_slot ORDER BY step)` uses each time period's own impression UV as the denominator.

## Clean Up Resources

```sql
DROP DYNAMIC TABLE IF EXISTS doc_ads_funnel_overview;
DROP TABLE IF EXISTS doc_user_events;
```

## Key Takeaways

- **`COUNT(DISTINCT user_id)` is the foundation of funnel analysis**: Count deduplicated users (UV) at each step — multiple actions by the same user at the same step count only once
- **`FIRST_VALUE` computes overall conversion rate; `LAG` computes step-over-step conversion rate**: Used together, they show both per-step drop-off and cumulative conversion from impression to the current step
- **`PARTITION BY` supports multi-dimensional funnels**: Group by product, time period, channel, or other dimensions — each group computes its own conversion rate independently
- **Missing steps are normal**: Some users may skip a step (e.g., going directly from click to order). The corresponding row simply won't appear in the results, which does not affect the calculation of other steps
- **Dynamic Table enables real-time funnels**: Wrap the funnel SQL in a Dynamic Table, and it automatically refreshes incrementally as new events arrive — no scheduled jobs needed

## Related Documentation

- [Window Functions](windowfunction.md)
- [LAG](sql_functions/window_functions/lag.md)
- [FIRST_VALUE](sql_functions/window_functions/first_value.md)
- [Create Dynamic Table](create-dynamic-table.md)
