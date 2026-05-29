# Data Discovery, Quality Assessment, Cleaning, and EDA Examples

## Data Discovery

```python
from src.config import get_session
session = get_session()

session.sql("SHOW SCHEMAS").show()
session.sql("SHOW TABLES IN my_schema").show()
session.sql("DESC EXTENDED my_schema.orders").show()
session.sql("""
    SELECT table_name, row_count,
           ROUND(bytes/1024.0/1024/1024, 2) AS size_gb
    FROM information_schema.tables
    WHERE table_schema = 'my_schema'
    ORDER BY bytes DESC
""").show()
```

---

## Data Quality Assessment

```sql
-- Basic statistics
SELECT
    COUNT(*)                                                          AS total_rows,
    COUNT(DISTINCT user_id)                                           AS unique_users,
    MIN(event_time) AS earliest, MAX(event_time) AS latest,
    ROUND(100.0 * SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS user_id_null_pct,
    ROUND(100.0 * SUM(CASE WHEN amount  IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS amount_null_pct
FROM my_schema.orders;

-- Duplicate primary key check
SELECT order_id, COUNT(*) AS cnt
FROM my_schema.orders GROUP BY order_id HAVING cnt > 1 LIMIT 10;

-- Numeric distribution (efficient for large tables)
SELECT
    approx_percentile(amount, 0.25) AS p25,
    approx_percentile(amount, 0.50) AS median,
    approx_percentile(amount, 0.75) AS p75,
    approx_percentile(amount, 0.99) AS p99,
    MIN(amount) AS min_val, MAX(amount) AS max_val
FROM my_schema.orders;

-- Top-K high-frequency values
SELECT approx_top_k(status, 10) AS top_statuses FROM my_schema.orders;

-- Approximate distinct count
SELECT approx_count_distinct(user_id) AS approx_uv FROM my_schema.events;
```

---

## Data Cleaning

```sql
-- Deduplication (keep the latest record)
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY update_time DESC) AS rn
    FROM my_schema.orders_raw
) WHERE rn = 1;

-- Null handling + type casting
SELECT
    order_id, user_id,
    COALESCE(amount, 0.0)       AS amount,
    COALESCE(status, 'UNKNOWN') AS status,
    CAST(order_date AS DATE)    AS order_date
FROM my_schema.orders_raw
WHERE user_id IS NOT NULL;

-- Multi-table integration
SELECT o.order_id, o.user_id, o.amount, o.order_date,
       u.age_group, u.city, p.category, p.brand
FROM my_schema.orders o
LEFT JOIN my_schema.users    u ON o.user_id    = u.user_id
LEFT JOIN my_schema.products p ON o.product_id = p.product_id;
```

---

## EDA

```python
# Sampling strategies
df_quick = session.sql("""
    SELECT * FROM my_schema.events TABLESAMPLE SYSTEM (0.1) LIMIT 50000
""").to_pandas()  # SYSTEM: file-level, very fast, good for >1M row previews

df_ml = session.sql("""
    SELECT * FROM my_schema.events TABLESAMPLE ROW (10)
""").to_pandas()  # ROW: exact row-level, good for ML training sets

# Time series analysis
session.sql("""
    SELECT
        DATE_TRUNC('day', order_time)  AS dt,
        COUNT(*)                       AS daily_orders,
        SUM(amount)                    AS daily_revenue,
        AVG(SUM(amount)) OVER (
            ORDER BY DATE_TRUNC('day', order_time)
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )                              AS revenue_7d_ma
    FROM my_schema.orders
    GROUP BY 1 ORDER BY 1
""").to_pandas().plot(x='dt', y=['daily_revenue', 'revenue_7d_ma'])
```
