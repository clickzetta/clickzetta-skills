# ZettaPark API Quick Reference

> Source: https://www.yunqi.tech/documents/ZettaparkQuickStart

## Table of Contents
- [Installation & Session](#installation)
- [Build DataFrame](#build-dataframe)
- [Transformations](#dataframe-transformations)
- [Aggregation](#aggregation)
- [JOIN](#join)
- [Execute & Collect](#execute-and-collect-results)
- [Write Data](#write-data)
- [Execute SQL](#execute-sql)
- [File Operations](#file-operations-volume)
- [Functions Reference](#common-functions-quick-reference)
- [Worked Examples](#worked-examples)

## Installation

```bash
pip install clickzetta_zettapark_python -U
```

---

## Create Session

```python
from clickzetta.zettapark.session import Session

connection_parameters = {
    "username": "your_username",
    "password": "your_password",
    "service": "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance_id",
    "workspace": "your_workspace",
    "schema": "public",
    "vcluster": "default",
}

session = Session.builder.configs(connection_parameters).create()
```

With hints (timeout, query_tag, etc.):

```python
connection_parameters = {
    "username": "your_username",
    "password": "your_password",
    "service": "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance_id",
    "workspace": "your_workspace",
    "schema": "public",
    "vcluster": "default",
    "hints": {
        "sdk.job.timeout": 300,
        "query_tag": "my_zettapark_app",
    }
}

session = Session.builder.configs(connection_parameters).create()
```

From JSON config file:

```python
import json
with open('config.json', 'r') as f:
    config = json.load(f)
session = Session.builder.configs(config).create()
```

Verify connection:

```python
session.sql("SELECT current_user(), current_workspace(), current_vcluster()").show()
```

Close session:

```python
session.close()
```

---

## Build DataFrame

```python
# From table
df = session.table("my_schema.my_table")

# From SQL
df = session.sql("SELECT * FROM orders WHERE year = 2024")

# From Python data
df = session.create_dataframe([1, 2, 3, 4]).to_df("id")
df = session.create_dataframe([[1, "Alice"], [2, "Bob"]], schema=["id", "name"])

# From Row objects
from clickzetta.zettapark import Row
df = session.create_dataframe([Row(id=1, name="Alice"), Row(id=2, name="Bob")])

# With explicit schema
from clickzetta.zettapark.types import IntegerType, StringType, StructType, StructField
schema = StructType([StructField("id", IntegerType()), StructField("name", StringType())])
df = session.create_dataframe([[1, "Alice"], [2, "Bob"]], schema)

# Range sequence
df = session.range(1, 10, 2).to_df("n")  # 1,3,5,7,9
```

---

## DataFrame Transformations

```python
from clickzetta.zettapark import functions as F

# Filter rows
df.filter(F.col("age") > 18)
df.filter(F.col("status") == "active")
df.where(F.col("amount") > 1000)

# Select columns
df.select("id", "name", "amount")
df.select(F.col("id"), F.col("name").as_("user_name"))

# Add / modify columns
df.with_column("total", F.col("price") * F.col("qty"))
df.with_column("upper_name", F.upper(F.col("name")))

# Rename columns
df.rename(F.col("old_name"), "new_name")

# Sort
df.sort(F.col("amount").desc())
df.order_by(F.col("created_at").asc())

# Deduplicate
df.distinct()
df.drop_duplicates(["user_id"])

# Limit rows
df.limit(100)

# Drop columns
df.drop("unnecessary_col")
```

---

## Aggregation

```python
from clickzetta.zettapark import functions as F

# Group by aggregation
df.group_by("category").agg(
    F.sum("amount").as_("total_amount"),
    F.count("*").as_("order_count"),
    F.avg("price").as_("avg_price"),
    F.max("amount").as_("max_amount"),
    F.min("amount").as_("min_amount"),
)

# Global aggregation
df.agg(F.count("*"), F.sum("amount"))
```

---

## JOIN

```python
# Inner join
df_orders.join(df_customers, df_orders["customer_id"] == df_customers["id"])

# Left join
df_orders.join(df_customers, df_orders["customer_id"] == df_customers["id"], "left")

# Select columns after join (avoid column name conflicts)
result = df_orders.join(df_customers, df_orders["customer_id"] == df_customers["id"]) \
    .select(df_orders["order_id"], df_customers["name"], df_orders["amount"])
```

---

## Execute and Collect Results

```python
# Print first N rows (triggers execution)
df.show()
df.show(20)

# Collect all results as Row list
rows = df.collect()
for row in rows:
    print(row["id"], row["name"])

# Convert to Pandas DataFrame
pandas_df = df.to_pandas()

# Get row count
count = df.count()

# Get column names
print(df.columns)

# View schema
df.schema.print_tree()
```

---

## Write Data

```python
# Append to existing table
df.write.save_as_table("my_table", mode="append")

# Overwrite (recreates table)
df.write.save_as_table("my_table", mode="overwrite")

# Write to table in specific schema
df.write.save_as_table("my_schema.my_table", mode="append")
```

---

## Execute SQL

```python
# Execute DDL/DML
session.sql("CREATE TABLE IF NOT EXISTS t (id INT, name STRING)").collect()
session.sql("INSERT INTO t VALUES (1, 'Alice')").collect()

# Execute query and get DataFrame
df = session.sql("SELECT * FROM orders WHERE amount > 1000")
df.show()

# Switch schema
session.use_schema("my_schema")
```

---

## File Operations (Volume)

```python
# Upload file to User Volume
session.file.put("/local/path/data.csv", "volume:user://~/data/")

# Download file
session.file.get("volume:user://~/data/data.csv", "/local/output/")

# List User Volume files
session.sql("LIST USER VOLUME").show()
session.sql("SHOW USER VOLUME DIRECTORY").show()
```

---

## Common Functions Quick Reference

```python
from clickzetta.zettapark import functions as F

# String
F.upper(col), F.lower(col), F.concat(col1, col2)
F.substring(col, 1, 3), F.trim(col), F.length(col)

# Numeric
F.abs(col), F.round(col, 2), F.floor(col), F.ceil(col)
F.sqrt(col), F.pow(col, 2)

# Date/time
F.current_date(), F.current_timestamp()
F.year(col), F.month(col), F.day(col)
F.date_add(col, 7), F.datediff(col1, col2)

# Conditional
F.when(F.col("status") == "A", "Active").otherwise("Inactive")
F.coalesce(col1, col2)  # first non-null value
F.isnull(col), F.isnotnull(col)

# Aggregation
F.count("*"), F.sum(col), F.avg(col), F.max(col), F.min(col)
F.count_distinct(col)

# Type casting
F.col("amount").cast(IntegerType())
```

---

## Worked Examples

### ETL data processing

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F

session = Session.builder.configs(config).create()

raw = session.table("bronze.raw_orders")

cleaned = (
    raw
    .filter(F.isnotnull(F.col("order_id")))
    .filter(F.col("amount") > 0)
    .with_column("order_date", F.col("created_at").cast("DATE"))
    .with_column("year_month", F.date_format(F.col("order_date"), "yyyy-MM"))
    .select("order_id", "customer_id", "amount", "order_date", "year_month")
)

cleaned.write.save_as_table("silver.orders_cleaned", mode="overwrite")
session.close()
```

### Feature engineering (machine learning)

```python
from clickzetta.zettapark import functions as F

customer = session.table("clickzetta_sample_data.tpch_100g.customer")
orders = session.table("clickzetta_sample_data.tpch_100g.orders")

customer_features = (
    orders
    .group_by("o_custkey")
    .agg(
        F.sum("o_totalprice").as_("total_spend"),
        F.count("*").as_("order_count"),
        F.avg("o_totalprice").as_("avg_order_value"),
        F.max("o_orderdate").as_("last_order_date"),
    )
    .join(customer, orders["o_custkey"] == customer["c_custkey"])
    .select("c_custkey", "c_name", "total_spend", "order_count", "avg_order_value")
)

customer_features.write.save_as_table("ml_features.customer_features", mode="overwrite")
```

### Import from local file

```python
import json, gzip
from clickzetta.zettapark.session import Session

session = Session.builder.configs(config).create()

data = []
with gzip.open('data.json.gz', 'rt', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            data.append(json.loads(line))

session.create_dataframe(data).write.save_as_table("my_table", mode="overwrite")
session.close()
```
