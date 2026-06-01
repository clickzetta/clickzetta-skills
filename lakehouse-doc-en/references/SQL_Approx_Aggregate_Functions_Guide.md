# Approximate Aggregate Functions Guide

> **Scenario**: When running TopN analysis, percentile statistics, or data distribution visualization on massive datasets (hundreds of millions of rows or more), exact computation can cause OOM errors or extremely slow queries. Approximate aggregate functions trade a tiny loss in precision for significant performance gains.
>
> **Core functions**: `approx_top_k` (approximate TopN statistics), `approx_histogram` (data distribution histogram), `approx_percentile` (approximate percentiles).

---

## Quick Reference

| Function | Purpose | Use Case | Precision |
|---|---|---|---|
| `approx_top_k(col, k, error)` | Approximate Top K elements with frequencies | Log TopN errors, popular products, high-frequency search terms | Controllable (error parameter) |
| `approx_histogram(col, buckets)` | Data distribution histogram | Response time distribution, spending distribution, outlier detection | Bucket approximation |
| `approx_percentile(col, p)` | Approximate percentiles (P50/P90/P99) | Performance monitoring SLA, latency analysis, long-tail detection | Approximate |

---

## Prerequisites

All examples in this guide use the following test data:

```sql
-- Service performance log table
CREATE TABLE service_logs (
  server_id BIGINT,
  response_time INT,        -- response time (milliseconds)
  log_level VARCHAR,        -- log level: error, warn, info, debug
  endpoint VARCHAR          -- API endpoint
);

-- Sample data
INSERT INTO service_logs VALUES
  (1, 100, 'info', '/api/users'), (1, 150, 'info', '/api/users'),
  (1, 200, 'warn', '/api/orders'), (1, 250, 'info', '/api/users'),
  (1, 300, 'error', '/api/payments'), (1, 350, 'info', '/api/users'),
  (1, 400, 'warn', '/api/orders'), (1, 450, 'info', '/api/users'),
  (1, 500, 'error', '/api/payments'), (1, 120, 'info', '/api/users'),
  (1, 180, 'warn', '/api/orders'), (1, 220, 'info', '/api/users'),
  (1, 280, 'error', '/api/payments'), (1, 320, 'info', '/api/users'),
  (1, 380, 'warn', '/api/orders'), (1, 420, 'info', '/api/users'),
  (1, 480, 'error', '/api/payments'), (1, 550, 'info', '/api/users'),
  (1, 90, 'debug', '/api/health'), (1, 600, 'error', '/api/payments'),
  (2, 80, 'info', '/api/users'), (2, 120, 'info', '/api/users'),
  (2, 200, 'warn', '/api/orders'), (2, 300, 'error', '/api/payments'),
  (2, 150, 'info', '/api/users'), (2, 250, 'warn', '/api/orders'),
  (2, 350, 'info', '/api/users'), (2, 100, 'debug', '/api/health'),
  (2, 180, 'info', '/api/users'), (2, 400, 'error', '/api/payments');
```

---

## Scenario 1: Approximate TopN Statistics (approx_top_k)

### Problem

Find the N most frequent log levels or API endpoints from a large volume of logs.

### SQL Implementation

```sql
SELECT 
  server_id,
  approx_top_k(log_level, 3, 100) AS top_levels,
  approx_top_k(endpoint, 3, 100) AS top_endpoints
FROM service_logs
GROUP BY server_id;
```

**Output**:

| server_id | top_levels | top_endpoints |
|-----------|------------|---------------|
| 1 | error=5:warn=4:info=9 | /api/users=9:/api/orders=4:/api/payments=5 |
| 2 | info=5:warn=2:error=2 | /api/users=5:/api/orders=3:/api/payments=2 |

> **Output format**: `value=count:value=count:...`, sorted by frequency in descending order.

### Parameter Reference

| Parameter | Type | Description |
|---|---|---|
| `col` | Any comparable type | The column to analyze |
| `k` | INT | Number of top elements to return |
| `error` | INT | Precision control (0–100); higher values are more accurate but use more memory |

### Effect of the error Parameter

```sql
-- Differences are minor on small datasets; significant on datasets of tens of millions of rows or more
SELECT 
  approx_top_k(log_level, 3, 10) AS low_accuracy,
  approx_top_k(log_level, 3, 100) AS high_accuracy
FROM service_logs;
```

| low_accuracy | high_accuracy |
|--------------|---------------|
| info=14:error=7:warn=6 | info=14:error=7:warn=6 |

> **Recommendation**: Use `100` (highest precision) in production; use `50` for exploratory analysis to save memory.

---

## Scenario 2: Data Distribution Histogram (approx_histogram)

### Problem

Understand the distribution of response times and identify whether there are long tails or outliers.

### SQL Implementation

```sql
SELECT approx_histogram(response_time, 5) AS histogram
FROM service_logs;
```

**Output**:

| histogram |
|-----------|
| 80=80=2:80=208=10:208=336=7:336=464=6:464=600=5 |

> **Output format**: `lower=upper=count:lower=upper=count:...`, showing the start value, end value, and count for each bucket.

### Reading the Output

| Bucket Range | Count | Percentage |
|---|---|---|
| 80–80 | 2 | 6.7% |
| 80–208 | 10 | 33.3% |
| 208–336 | 7 | 23.3% |
| 336–464 | 6 | 20.0% |
| 464–600 | 5 | 16.7% |

### View Distribution by Server

```sql
SELECT 
  server_id,
  approx_histogram(response_time, 4) AS histogram
FROM service_logs
GROUP BY server_id;
```

---

## Scenario 3: Approximate Percentiles (approx_percentile)

### Problem

Calculate P50 (median), P90, and P99 response times for SLA monitoring.

### SQL Implementation

```sql
SELECT 
  approx_percentile(response_time, 0.5) AS p50,
  approx_percentile(response_time, 0.9) AS p90,
  approx_percentile(response_time, 0.99) AS p99
FROM service_logs;
```

**Output**:

| p50 | p90 | p99 |
|-----|-----|-----|
| 307.5 | 525 | 600 |

### Calculate Multiple Percentiles at Once

```sql
SELECT 
  approx_percentile(response_time, ARRAY[0.5, 0.9, 0.95, 0.99]) AS percentiles
FROM service_logs;
```

**Output**:

| percentiles |
|-------------|
| 307.5:525:550:600 |

> **Output format**: Colon-separated percentile values, in the same order as the input array.

### Calculate SLA by Endpoint

```sql
SELECT 
  endpoint,
  COUNT(*) AS request_count,
  approx_percentile(response_time, 0.5) AS p50,
  approx_percentile(response_time, 0.9) AS p90,
  approx_percentile(response_time, 0.99) AS p99
FROM service_logs
GROUP BY endpoint
ORDER BY p90 DESC;
```

**Output**:

| endpoint | request_count | p50 | p90 | p99 |
|----------|---------------|-----|-----|-----|
| /api/payments | 7 | 400 | 600 | 600 |
| /api/orders | 6 | 250 | 450 | 450 |
| /api/users | 14 | 180 | 420 | 550 |
| /api/health | 2 | 90 | 100 | 100 |

---

## Scenario 4: Approximate vs. Exact Values

### Problem

Verify whether the precision of approximate functions meets business requirements.

### SQL Implementation

```sql
SELECT 
  -- Exact values
  percentile(response_time, 0.5) AS exact_p50,
  percentile(response_time, 0.9) AS exact_p90,
  -- Approximate values
  approx_percentile(response_time, 0.5) AS approx_p50,
  approx_percentile(response_time, 0.9) AS approx_p90,
  -- Error
  ROUND(ABS(percentile(response_time, 0.5) - approx_percentile(response_time, 0.5)), 1) AS p50_error,
  ROUND(ABS(percentile(response_time, 0.9) - approx_percentile(response_time, 0.9)), 1) AS p90_error
FROM service_logs;
```

**Output**:

| exact_p50 | exact_p90 | approx_p50 | approx_p90 | p50_error | p90_error |
|-----------|-----------|------------|------------|-----------|-----------|
| 310 | 505.0 | 307.5 | 525 | 2.5 | 20.0 |

> ⚠️ **Note**: Errors are more noticeable on small datasets (30 rows); on large datasets (millions of rows or more), the error is typically less than 1%.

---

## Scenario 5: End-to-End Example — Service Performance Monitoring Dashboard

### Problem

Build a service performance monitoring query that includes:
- Request volume per server
- Top 3 error types
- P50/P90/P99 response times
- Response time distribution

### SQL Implementation

```sql
SELECT 
  server_id,
  COUNT(*) AS total_requests,
  -- Top 3 log levels
  approx_top_k(log_level, 3, 100) AS top_levels,
  -- Percentiles
  approx_percentile(response_time, 0.5) AS p50,
  approx_percentile(response_time, 0.9) AS p90,
  approx_percentile(response_time, 0.99) AS p99,
  -- Distribution (3 buckets)
  approx_histogram(response_time, 3) AS distribution
FROM service_logs
GROUP BY server_id;
```

**Output**:

| server_id | total_requests | top_levels | p50 | p90 | p99 | distribution |
|-----------|----------------|------------|-----|-----|-----|--------------|
| 1 | 20 | info=9:error=5:warn=4 | 290 | 525 | 600 | 90=90=1:90=330=12:330=600=7 |
| 2 | 10 | info=5:warn=2:error=2 | 180 | 400 | 400 | 80=80=1:80=253=6:253=400=3 |

---

## Common Issues

### 1. Return value format of `approx_top_k`

```sql
-- The return value is a formatted string, not JSON or an array
-- If you need structured data, parse it with string functions
SELECT approx_top_k(level, 3, 100) AS result FROM logs;
-- Output: error=5:warn=2:info=2
```

### 2. Choosing the number of buckets for `approx_histogram`

```sql
-- Too few buckets: distribution is too coarse
approx_histogram(response_time, 2)  -- only 2 buckets

-- Too many buckets: approximation quality degrades and output string becomes very long
approx_histogram(response_time, 100)  -- may exceed display limits

-- Recommended: 5–10 buckets
approx_histogram(response_time, 5)
```

### 3. `approx_percentile` does not support the FILTER clause

```sql
-- Wrong: approx_percentile does not support FILTER
approx_percentile(response_time, 0.9) FILTER (WHERE server_id = 1)

-- Correct: use CASE WHEN to filter
approx_percentile(CASE WHEN server_id = 1 THEN response_time END, 0.9)
```

### 4. NULL handling

```sql
-- NULL values are ignored and do not affect the result
SELECT approx_percentile(response_time, 0.5) FROM (
  SELECT NULL AS response_time UNION ALL SELECT 100 UNION ALL SELECT 200
);
-- Output: 150 (calculated from 100 and 200)
```

### 5. Performance advantage on large datasets

| Data Volume | `percentile` Time | `approx_percentile` Time | Memory Ratio |
|---|---|---|---|
| 1 million rows | ~5s | ~1s | 1:5 |
| 100 million rows | ~60s | ~3s | 1:20 |
| 1 billion rows | OOM | ~15s | N/A : manageable |

> **Recommendation**: Use exact functions for fewer than 100,000 rows; use approximate functions for more than 1 million rows.

---

## Performance Optimization Tips

| Scenario | Optimization Strategy |
|---|---|
| Multiple percentile calculations | Use `ARRAY[0.5, 0.9, 0.99]` to compute all at once and avoid multiple scans |
| TopN + percentile combination | Place them in the same `SELECT` to share the aggregation phase |
| Time-window analysis | Use `DATE_TRUNC` for grouping to avoid full table scans |
| Approximate functions + GROUP BY | Filter before aggregating to reduce input data volume |

```sql
-- Recommended: compute multiple percentiles in one pass
SELECT 
  endpoint,
  approx_percentile(response_time, ARRAY[0.5, 0.9, 0.99]) AS percentiles
FROM service_logs
WHERE response_time > 0  -- filter first
GROUP BY endpoint;

-- Not recommended: multiple scans for each percentile
SELECT 
  endpoint,
  approx_percentile(response_time, 0.5) AS p50,
  approx_percentile(response_time, 0.9) AS p90  -- additional scan
FROM service_logs
GROUP BY endpoint;
```

---

## Related Documentation

* [Aggregate Functions Reference](agg_function.md)
* [approx_top_k](sql_functions/aggregate_functions/approx_top_k.md)
* [approx_histogram](sql_functions/aggregate_functions/approx_histogram.md)
* [approx_percentile](sql_functions/aggregate_functions/approx_percentile.md)
* [Data Sampling and Exploration](sql_sampling_guide.md)
