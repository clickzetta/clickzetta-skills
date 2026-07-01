# Zettapark Dynamic Table Guide

Dynamic Table is an incremental computation object in Singdata Lakehouse. You define the transformation logic with a DataFrame, and the system automatically detects upstream changes and refreshes the result incrementally — no manual scheduling required. Zettapark creates Dynamic Tables directly from a DataFrame via `create_or_replace_dynamic_table()`.

---

## Prerequisites

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "DEFAULT"
}).create()
```

Create the source table and insert test data:

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT, user_id INT, category STRING,
        amount DECIMAL(10,2), status STRING, order_date STRING
    )
""").collect()

session.sql("""
    INSERT INTO orders VALUES
    (1, 101, 'A', 100.0, 'paid',    '2024-01-15'),
    (2, 102, 'A', 200.0, 'paid',    '2024-01-15'),
    (3, 101, 'B', 300.0, 'pending', '2024-01-16'),
    (4, 103, 'B', 150.0, 'paid',    '2024-01-16')
""").collect()
```

---

## Create a Dynamic Table

### Aggregation Summary

```python
source = session.table("orders")
```

Define the transformation logic:

```python
agg_df = source.group_by("category").agg(
    F.count(F.col("id")).alias("order_count"),
    F.sum(F.col("amount")).alias("total_amount"),
    F.avg(F.col("amount")).alias("avg_amount")
)
```

Create the Dynamic Table with automatic refresh every minute:

```python
agg_df.create_or_replace_dynamic_table(
    "orders_summary",
    lag="1 minute",       # refresh interval
    warehouse="default"   # compute cluster to use
)

session.table("orders_summary").show()
```

```Plain
+--------+-----------+------------+----------+
|category|order_count|total_amount|avg_amount|
+--------+-----------+------------+----------+
|       A|          2|      300.00|    150.00|
|       B|          2|      450.00|    225.00|
+--------+-----------+------------+----------+
```

### Filter + Computed Columns

```python
filtered_df = source \
    .filter(F.col("amount") > 150) \
    .with_column("amount_tax", F.col("amount") * 1.13) \
    .with_column("year", F.year(F.to_date(F.col("order_date"))))

filtered_df.create_or_replace_dynamic_table(
    "orders_filtered",
    lag="5 minutes",
    warehouse="default"
)
```

### Multi-table Join

Create the users table first:

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT, name STRING, city STRING
    )
""").collect()
session.sql("""
    INSERT INTO users VALUES
    (101, 'Alice', 'Beijing'),
    (102, 'Bob',   'Shanghai'),
    (103, 'Carol', 'Guangzhou')
""").collect()
```

```python
orders = session.table("orders")
users  = session.table("users")

paid = orders.filter(F.col("status") == "paid") \
    .select(F.col("id"), orders["user_id"].alias("o_uid"),
            F.col("amount"), F.col("order_date"))
```

Disambiguate duplicate column names before joining:

```python
joined = paid.join(users, paid["o_uid"] == users["user_id"]) \
    .select("user_id", "name", "amount", "order_date")

joined.create_or_replace_dynamic_table(
    "paid_orders_with_user",
    lag="1 minute",
    warehouse="default"
)
```

---

## Manage Dynamic Tables

### Inspect Structure

```python
session.sql("DESC DYNAMIC TABLE orders_summary").collect()
```

### Suspend and Resume

Suspend automatic refresh:

```python
session.sql("ALTER DYNAMIC TABLE orders_summary SUSPEND").collect()
```

Resume automatic refresh:

```python
session.sql("ALTER DYNAMIC TABLE orders_summary RESUME").collect()
```

### Trigger a Manual Refresh

```python
session.sql("ALTER DYNAMIC TABLE orders_summary REFRESH").collect()
```

### Drop

```python
session.sql("DROP DYNAMIC TABLE IF EXISTS orders_summary").collect()
```

---

## Dynamic Table vs. Manual Scheduling

| Aspect | Dynamic Table | Studio SQL Task + Scheduler |
|--------|---------------|-----------------------------|
| Definition | DataFrame API or SQL | SQL script |
| Refresh trigger | System auto-detects upstream changes | Cron schedule or manual trigger |
| Incremental computation | System automatically chooses incremental or full refresh | Incremental logic must be written manually |
| Dependency management | Upstream/downstream dependencies resolved automatically | Task dependencies configured manually |
| Best for | Continuously refreshed aggregations and transformations | Complex business logic requiring precise execution timing |

---

## Notes

- The `lag` parameter accepts formats such as `"1 minute"`, `"5 minutes"`, and `"1 hour"`. The minimum interval is 1 minute.
- A newly created Dynamic Table starts empty and is populated after the first refresh.
- To change a Dynamic Table's definition, use `create_or_replace_dynamic_table` again (this rebuilds the table).
- Upstream tables must have `change_tracking` enabled to support incremental refresh.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Dynamic Table Overview](dynamic-table.md) | Full Dynamic Table concepts and SQL syntax |
| [Zettapark Table Stream Guide](zettapark-stream-guide.md) | Processing CDC incremental changes with Zettapark |
| [Zettapark Data Engineering Guide](zettapark-etl-guide.md) | Multi-table joins, window functions, and more |
