# Statistical Analysis Functions Reference for Data Science

---

## Approximate Aggregate Functions (Efficient for Large Tables)

### approx_count_distinct — Approximate Distinct Count

```sql
-- Uses HyperLogLog algorithm, ~2% error, 10x+ faster than COUNT(DISTINCT)
SELECT approx_count_distinct(user_id) AS approx_uv
FROM my_schema.events;

-- Daily active users (DAU)
SELECT
    DATE(event_time) AS dt,
    approx_count_distinct(user_id) AS dau
FROM my_schema.events
GROUP BY 1
ORDER BY 1;
```

### approx_percentile — Approximate Percentiles

```sql
-- Median, quartiles, P95, P99
SELECT
    approx_percentile(amount, 0.25) AS p25,
    approx_percentile(amount, 0.50) AS median,
    approx_percentile(amount, 0.75) AS p75,
    approx_percentile(amount, 0.95) AS p95,
    approx_percentile(amount, 0.99) AS p99
FROM my_schema.orders;

-- Grouped percentiles
SELECT
    category,
    approx_percentile(price, 0.5) AS median_price
FROM my_schema.products
GROUP BY category;
```

### approx_histogram — Approximate Histogram

```sql
-- Returns a struct array: [{min, max, count}, ...]
SELECT approx_histogram(amount, 10) AS hist
FROM my_schema.orders;

-- Parse histogram (expand to rows)
SELECT
    bucket.min AS bucket_min,
    bucket.max AS bucket_max,
    bucket.count AS bucket_count
FROM (
    SELECT EXPLODE(approx_histogram(amount, 10)) AS bucket
    FROM my_schema.orders
);
```

### approx_top_k — Approximate Top-K High-Frequency Values

```sql
-- Find the top 10 most frequent cities
SELECT approx_top_k(city, 10) AS top_cities
FROM my_schema.orders;

-- Returns a struct array: [{value, count}, ...]
-- Expand to rows (fields are value and count)
SELECT item.value AS city, item.count AS cnt
FROM (
    SELECT EXPLODE(approx_top_k(city, 10)) AS item
    FROM my_schema.orders
)
ORDER BY cnt DESC;
```

---

## Exact Statistical Functions

### percentile / median

```sql
-- Exact median (use for small tables; use approx_percentile for large tables)
SELECT
    percentile(amount, 0.5)  AS exact_median,
    median(amount)           AS median_alias  -- equivalent
FROM my_schema.orders;

-- Multiple percentiles
SELECT percentile(amount, ARRAY(0.25, 0.5, 0.75, 0.9, 0.99))
FROM my_schema.orders;
```

---

## TABLESAMPLE Sampling

```sql
-- ROW mode: exact row-level sampling (good for ML training sets, <10M rows)
SELECT * FROM my_schema.events TABLESAMPLE ROW (10);      -- exact 10%
SELECT * FROM my_schema.events TABLESAMPLE ROW (5 ROWS);  -- exact 5 rows

-- SYSTEM mode: file-level sampling (good for large table quick preview, >10M rows)
SELECT * FROM my_schema.events TABLESAMPLE SYSTEM (0.1) LIMIT 50000;  -- ~0.1%

-- Stratified sampling (proportional by category)
SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY RAND()) AS rn,
           COUNT(*) OVER (PARTITION BY category) AS cat_total
    FROM my_schema.products
)
WHERE rn <= CEIL(cat_total * 0.1);  -- 10% per category
```

| Use Case | Recommended Mode | Notes |
|---|---|---|
| Quick data preview | SYSTEM | Very fast, good for >1M rows |
| ML training set | ROW | Exact random, ensures representativeness |
| Data quality spot check | SYSTEM | Fast sampling for validation |
| Statistical analysis | ROW | Exact probability sampling |

> ⚠️ **Note**: TABLESAMPLE on small tables (<tens of thousands of rows) may return all data — percentage sampling is not precise. Use `LIMIT` directly for small tables.

---

## Window Functions (Time Series / Ranking Features)

```sql
-- 7-day moving average
SELECT
    dt,
    revenue,
    AVG(revenue) OVER (
        ORDER BY dt
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS revenue_7d_ma
FROM daily_stats;

-- Month-over-month growth rate
SELECT
    dt,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY dt)  AS prev_revenue,
    ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY dt))
          / NULLIF(LAG(revenue, 1) OVER (ORDER BY dt), 0), 2) AS mom_growth_pct
FROM daily_stats;

-- User behavior ranking (RFM analysis)
SELECT
    user_id,
    total_amount,
    NTILE(5) OVER (ORDER BY total_amount DESC)  AS monetary_quintile,
    NTILE(5) OVER (ORDER BY order_cnt DESC)     AS frequency_quintile,
    NTILE(5) OVER (ORDER BY last_order_date DESC) AS recency_quintile
FROM user_rfm;

-- Deduplication keeping latest (common in data cleaning)
SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY user_id
               ORDER BY update_time DESC
           ) AS rn
    FROM my_schema.users_raw
) WHERE rn = 1;
```

---

## Data Quality Check Template

```sql
-- Output all key quality metrics in one query
SELECT
    COUNT(*)                                                    AS total_rows,
    COUNT(DISTINCT user_id)                                     AS unique_users,
    -- Null rates
    ROUND(100.0 * COUNT(*) FILTER (WHERE user_id IS NULL)
          / COUNT(*), 2)                                        AS user_id_null_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE amount IS NULL)
          / COUNT(*), 2)                                        AS amount_null_pct,
    -- Anomalies
    SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END)                AS negative_amount_cnt,
    SUM(CASE WHEN amount > 1000000 THEN 1 ELSE 0 END)          AS extreme_amount_cnt,
    -- Time range
    MIN(order_date)                                             AS earliest_date,
    MAX(order_date)                                             AS latest_date,
    -- Distribution
    approx_percentile(amount, 0.5)                             AS median_amount,
    approx_percentile(amount, 0.99)                            AS p99_amount
FROM my_schema.orders;
```
