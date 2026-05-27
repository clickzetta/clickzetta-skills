# Zettapark Data Engineering Practice

This guide demonstrates Zettapark usage in a complete data engineering workflow through an order analytics scenario.

---

## Setup

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F
from clickzetta.zettapark.window import Window

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.singdata.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "default"
}).create()
```

---

## Prerequisites

All examples in this guide use the following two tables. Run this setup before proceeding:

```python
# Create tables
session.sql("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id   BIGINT,
        user_id    BIGINT,
        product    STRING,
        amount     DECIMAL(10, 2),
        status     STRING,
        order_date STRING
    )
""").collect()

session.sql("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT,
        name    STRING,
        city    STRING,
        level   STRING
    )
""").collect()

# Insert test data
session.sql("""
    INSERT INTO orders VALUES
    (1001, 101, 'iPhone',  7999.00, 'paid',      '2024-01-15'),
    (1002, 102, 'MacBook', 14999.00, 'paid',      '2024-01-15'),
    (1003, 101, 'AirPods', 1799.00, 'pending',   '2024-01-16'),
    (1004, 103, 'iPad',    8999.00, 'paid',      '2024-01-16'),
    (1005, 102, 'Watch',   3299.00, 'cancelled', '2024-01-17'),
    (1006, 101, 'MacBook', 14999.00, 'paid',      '2024-01-17')
""").collect()

session.sql("""
    INSERT INTO users VALUES
    (101, 'Alice', 'Beijing',   'gold'),
    (102, 'Bob',   'Shanghai',  'silver'),
    (103, 'Carol', 'Guangzhou', 'bronze')
""").collect()
```

> 💡 `order_date` uses STRING type to store date strings; use `F.to_date()` to convert at query time. This is because Lakehouse has limited implicit type conversion for DATE columns — STRING is more flexible.

---

## Scenario 1: Multi-Table Join + Aggregation + Write Results

Join the orders and users tables, compute per-user spending summaries, and write to a result table.

```python
orders = session.table("orders")   # order_id, user_id, product, amount, status, order_date
users  = session.table("users")    # user_id, name, city, level

# Note: when joining tables with a shared column name (user_id),
# rename it before joining to avoid ambiguity
paid = orders.filter(F.col("status") == "paid") \
    .select(
        F.col("order_id"),
        orders["user_id"].alias("o_user_id"),  # rename to avoid post-join ambiguity
        F.col("amount"),
        F.col("order_date")
    )

result = paid.join(users, paid["o_user_id"] == users["user_id"]) \
    .group_by("user_id", "name", "city", "level") \
    .agg(
        F.count(F.col("order_id")).alias("order_count"),
        F.sum(F.col("amount")).alias("total_amount"),
        F.max(F.col("order_date")).alias("last_order_date")
    ) \
    .sort(F.col("total_amount").desc())

result.show()
# +-------+-----+---------+------+-----------+------------+---------------+
# |user_id| name|     city| level|order_count|total_amount|last_order_date|
# +-------+-----+---------+------+-----------+------------+---------------+
# |    101|Alice|  Beijing|  gold|          2|    22998.00|     2024-01-17|
# |    102|  Bob| Shanghai|silver|          1|    14999.00|     2024-01-15|
# |    103|Carol|Guangzhou|bronze|          1|     8999.00|     2024-01-16|
# +-------+-----+---------+------+-----------+------------+---------------+

# Write to result table
result.write.save_as_table("user_order_summary", mode="overwrite")
```

> ⚠️ **Join column ambiguity**: When two tables share a column name, `group_by` or `select` after the join will raise `cannot resolve column`. Fix: rename the shared column in one table using `.alias()` before joining.

---

## Scenario 2: Window Functions — Ranking and Running Totals

```python
summary = session.table("user_order_summary")

# Rank by spending amount descending
w_rank = Window.order_by(F.col("total_amount").desc())

# Running total by city
w_city = Window.partition_by("city").order_by(F.col("total_amount").desc())

result = summary \
    .with_column("rank",           F.rank().over(w_rank)) \
    .with_column("city_rank",      F.rank().over(w_city)) \
    .with_column("running_total",  F.sum("total_amount").over(w_city))

result.show()
# +-------+-----+------+-----------+------------+----+---------+-------------+
# |user_id| name| level|order_count|total_amount|rank|city_rank|running_total|
# +-------+-----+------+-----------+------------+----+---------+-------------+
# |    101|Alice|  gold|          2|    22998.00|   1|        1|     22998.00|
# |    102|  Bob|silver|          1|    14999.00|   2|        1|     14999.00|
# |    103|Carol|bronze|          1|     8999.00|   3|        1|      8999.00|
# +-------+-----+------+-----------+------------+----+---------+-------------+
```

---

## Scenario 3: Create a View for BI

```python
# Create a paid orders view with year/month dimensions for BI analysis
orders.filter(F.col("status") == "paid") \
    .select(
        F.col("order_id"),
        F.col("user_id"),
        F.col("product"),
        F.col("amount"),
        F.col("order_date"),
        F.year(F.to_date(F.col("order_date"))).alias("year"),
        F.month(F.to_date(F.col("order_date"))).alias("month"),
    ).create_or_replace_view("v_paid_orders")

# BI tools can query the view directly
session.table("v_paid_orders").show()
```

---

## Scenario 4: Incremental Processing

Process only new data after a given point in time — suitable for scheduled incremental ETL:

```python
# Process only new orders from 2024-01-16 onwards
cutoff = "2024-01-16"
new_orders = orders.filter(F.col("order_date") >= cutoff)

print(f"New orders: {new_orders.count()}")
new_orders.show()

# Append new paid orders to the archive table
new_orders.filter(F.col("status") == "paid") \
    .write.save_as_table("paid_orders_archive", mode="append")
```

---

## Scenario 5: Data Quality Checks

Check data quality before writing:

```python
# Check for NULL values
null_counts = orders.select(
    F.count(F.lit(1)).alias("total"),
    F.sum(F.iff(F.is_null(F.col("amount")), F.lit(1), F.lit(0))).alias("null_amount"),
    F.sum(F.iff(F.is_null(F.col("user_id")), F.lit(1), F.lit(0))).alias("null_user_id"),
)
null_counts.show()

# Check status distribution
orders.group_by("status").agg(
    F.count(F.lit(1)).alias("cnt")
).sort("cnt", ascending=False).show()

# Check for anomalous amounts (negative or excessively large)
anomalies = orders.filter(
    (F.col("amount") <= 0) | (F.col("amount") > 100000)
)
print(f"Anomalous orders: {anomalies.count()}")
```

---

## Scenario 6: Mixing with SQL

Complex logic can be executed directly with `session.sql()`. The result is still a DataFrame and can continue to be chained:

```python
# Execute a complex query with SQL, return a DataFrame for further processing
df = session.sql("""
    SELECT
        user_id,
        DATE_TRUNC('month', TO_DATE(order_date)) AS month,
        SUM(amount) AS monthly_amount
    FROM orders
    WHERE status = 'paid'
    GROUP BY user_id, DATE_TRUNC('month', TO_DATE(order_date))
""")

# Continue processing with the DataFrame API
w = Window.partition_by("user_id").order_by("month")
df.with_column("cumulative", F.sum("monthly_amount").over(w)).show()
```

---

## Notes

**DATE column writes**: When using `session.sql()` INSERT, strings cannot be implicitly converted to DATE type. Recommended approaches:
- Define date columns as `STRING` type when creating tables; use `F.to_date()` to convert at query time
- Or use explicit `CAST`: `INSERT INTO t VALUES (CAST('2024-01-15' AS DATE))`

**Join column ambiguity**: After joining two tables with shared column names, `group_by` will raise an error. Fix: rename the shared column in one table using `.alias()` before joining.

**Lazy evaluation in chained operations**: Zettapark DataFrames are lazy — they only execute when an action is called, such as `show()`, `collect()`, `count()`, or `write.save_as_table()`.

---

## Related Documentation

| Document | Description |
|------|------|
| [Zettapark DataFrame API Guide](zettapark-dataframe-guide.md) | Complete DataFrame operations reference |
| [Zettapark Functions Reference](zettapark-functions-guide.md) | String, numeric, date, and conditional functions |
| [Dynamic Table](../dynamic-table.md) | Create auto-incrementally refreshed data pipelines with Zettapark |
| [Python Connector SDK](../python_reference/connector.md) | Standard SQL execution interface |
