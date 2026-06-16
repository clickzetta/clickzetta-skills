# Zettapark DataFrame API Guide

Zettapark is the Python DataFrame API for Singdata Lakehouse, providing a pandas/PySpark-like interface. The Python code you write is translated into SQL and executed distributedly in Lakehouse — no manual SQL required.

**This guide covers**: Creating DataFrames → Basic transformations → Aggregations → Joins → Set operations → Null handling → Window functions → Reading and writing tables → Views and Dynamic Tables.

> 💡 **When to use what**:
> - Need DataFrame operations (pandas/PySpark-like) → Use Zettapark (this guide)
> - Need standard SQL execution or script automation → Use [Python Connector](python_reference/connector.md)
> - Need high-speed bulk writes (millions of rows) → Use [BulkLoad](java_reference/bulkload.md)

---

## Installation

```bash
pip install clickzetta_zettapark_python
```

---

## Create a Session

```python
from clickzetta.zettapark.session import Session

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

Close when done:

```python
session.close()
```

---

## Create a DataFrame

### From Python Data

```python
from clickzetta.zettapark.session import Session

data = [(1, "Alice", 1000.0), (2, "Bob", 2000.0), (3, "Carol", 500.0)]
df = session.create_dataframe(data, schema=["id", "name", "amount"])
df.show()
```

```Plain
+---+-----+------+
| id| name|amount|
+---+-----+------+
|  1|Alice|  1000|
|  2|  Bob|  2000|
|  3|Carol|   500|
+---+-----+------+
```

### From an Existing Table

Create the table and insert data first:

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id BIGINT, user_id BIGINT, product STRING,
        amount DECIMAL(10,2), status STRING, order_date STRING
    )
""").collect()
session.sql("""
    INSERT INTO orders VALUES
    (1001,101,'iPhone',7999.00,'paid','2024-01-15'),
    (1002,102,'MacBook',14999.00,'paid','2024-01-15'),
    (1003,101,'AirPods',1799.00,'pending','2024-01-16')
""").collect()
```

Then read with `session.table()`:

```python
df = session.table("orders")
df.show()
```

### Execute SQL and Return a DataFrame

```python
df = session.sql("SELECT * FROM orders WHERE status = 'paid'")
df.show()
```

---

## Basic Transformations

```python
from clickzetta.zettapark import functions as F

data = [(1,"A",100.0),(2,"A",200.0),(3,"B",300.0),(4,"B",150.0)]
df = session.create_dataframe(data, schema=["id","category","amount"])
```

filter — filter rows

```python
df.filter(F.col("amount") > 150).show()
```

select — select columns

```python
df.select("category", "amount").show()
```

sort — sort rows

```python
df.sort("amount", ascending=False).show()
```

with\_column — add or replace a column

```python
df.with_column("amount_tax", F.col("amount") * 1.13).show()
```

with\_column\_renamed — rename a column

```python
df.with_column_renamed("amount", "price").show()
```

drop — drop a column

```python
df.drop("id").show()
```

limit

```python
df.limit(2).show()
```

---

## Aggregations

group\_by + agg

```python
result = df.group_by("category").agg(
    F.sum("amount").alias("total"),
    F.count("id").alias("cnt"),
    F.avg("amount").alias("avg_amount"),
    F.max("amount").alias("max_amount"),
    F.min("amount").alias("min_amount")
)
result.show()
```

```Plain
+--------+-----+---+----------+---------+---------+
|category|total|cnt|avg_amount|max_amount|min_amount|
+--------+-----+---+----------+---------+---------+
|       A|  300|  2|       150|      200|      100|
|       B|  450|  2|       225|      300|      150|
+--------+-----+---+----------+---------+---------+
```

---

## Joins

```python
users  = session.create_dataframe([(1,"Alice"),(2,"Bob"),(3,"Carol")], schema=["id","name"])
orders = session.create_dataframe([(1,500.0),(1,300.0),(2,800.0)],    schema=["user_id","amount"])
```

inner join (default)

```python
users.join(orders, users["id"] == orders["user_id"]).show()
```

left join

```python
users.join(orders, users["id"] == orders["user_id"], "left").show()
```

```Plain
+---+-----+-------+------+
| id| name|user_id|amount|
+---+-----+-------+------+
|  1|Alice|      1|   300|
|  1|Alice|      1|   500|
|  2|  Bob|      2|   800|
|  3|Carol|   NULL|  NULL|
+---+-----+-------+------+
```

cross join

```python
users.cross_join(orders).show()
```

---

## Set Operations

```python
df1 = session.create_dataframe([(1,"A"),(2,"B"),(3,"C")], schema=["id","val"])
df2 = session.create_dataframe([(2,"B"),(3,"C"),(4,"D")], schema=["id","val"])

df1.union_all(df2).show()   # union (keep duplicates)
df1.intersect(df2).show()   # intersection
df1.except_(df2).show()     # difference (in df1 but not df2)
```

---

## Null Handling

```python
data = [(1,"Alice",100.0),(2,None,200.0),(3,"Carol",None)]
df = session.create_dataframe(data, schema=["id","name","amount"])
```

Drop rows containing NULL

```python
df.dropna().show()
```

```Plain
+---+-----+------+
| id| name|amount|
+---+-----+------+
|  1|Alice|   100|
+---+-----+------+
```

Fill NULL values

```python
df.fillna({"name": "Unknown", "amount": 0.0}).show()
```

```Plain
+---+-------+------+
| id|   name|amount|
+---+-------+------+
|  1|  Alice|   100|
|  2|Unknown|   200|
|  3|  Carol|     0|
+---+-------+------+
```

---

## Window Functions

```python
from clickzetta.zettapark.window import Window

data = [(1,"A",100),(2,"A",200),(3,"B",300),(4,"B",150),(5,"A",50)]
df = session.create_dataframe(data, schema=["id","category","amount"])
```

Rank within group

```python
w_rank = Window.partition_by("category").order_by(F.col("amount").desc())
```

Running sum within group

```python
w_sum = Window.partition_by("category").order_by("amount")

result = df \
    .with_column("rank",          F.rank().over(w_rank)) \
    .with_column("running_total", F.sum("amount").over(w_sum))

result.show()
```

```Plain
+---+--------+------+----+-------------+
| id|category|amount|rank|running_total|
+---+--------+------+----+-------------+
|  5|       A|    50|   3|           50|
|  1|       A|   100|   2|          150|
|  2|       A|   200|   1|          350|
|  4|       B|   150|   2|          150|
|  3|       B|   300|   1|          450|
+---+--------+------+----+-------------+
```

---

## Reading and Writing Tables

### Write to a Table

```python
df = session.create_dataframe([(1,"Alice",100.0),(2,"Bob",200.0)], schema=["id","name","amount"])
```

Overwrite (creates the table if it doesn't exist)

```python
df.write.save_as_table("my_table", mode="overwrite")
```

Append

```python
df.write.save_as_table("my_table", mode="append")
```

### Read from a Table

```python
df = session.table("my_table")
df.show()
```

### Convert to pandas DataFrame

```python
pdf = df.to_pandas()
print(type(pdf))   # <class 'pandas.core.frame.DataFrame'>
print(pdf.head())
```

---

## Views and Dynamic Tables

### Temporary View (valid within the session)

```python
df.filter(F.col("amount") > 100).create_or_replace_temp_view("high_value_orders")
```

Query the temporary view with SQL

```python
session.sql("SELECT * FROM high_value_orders").show()
```

### Persistent View

```python
df.filter(F.col("amount") > 100).create_or_replace_view("v_high_value_orders")
```

### Dynamic Table (auto incremental refresh)

Define transformation logic on a source table; the system auto-refreshes incrementally

```python
source_df = session.table("raw_orders").filter(F.col("status") == "paid")

source_df.create_or_replace_dynamic_table(
    "paid_orders_summary",
    lag="1 minute",       # refresh interval
    warehouse="default"   # compute cluster to use
)
```

See [Dynamic Table Documentation](dynamic-table.md) for details.

---

## Inspect Generated SQL

Use `explain()` to view the SQL generated by DataFrame operations — useful for debugging and performance analysis:

```python
df.filter(F.col("amount") > 150) \
  .group_by("category") \
  .agg(F.sum("amount").alias("total")) \
  .explain()
```

Output:

```Plain
SELECT `category`, sum(`amount`) AS `total`
FROM ( SELECT ... WHERE (`amount` > CAST(150 AS bigint)))
GROUP BY `category`
```

---

## Related Documentation

| Document | Description |
|------|------|
| [Zettapark Quick Start](zettapark-quick-start.md) | Installation and basic examples |
| [Python Connector SDK](python_reference/connector.md) | Standard SQL execution interface |
| [Dynamic Table](dynamic-table.md) | Auto-incrementally refreshed data pipelines |
| [BulkLoad Batch Import](java_reference/bulkload.md) | High-speed writes for millions of rows |
