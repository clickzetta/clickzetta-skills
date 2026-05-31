---
name: clickzetta-zettapark
description: |
  Use the ZettaPark Python library to work with ClickZetta Lakehouse data. ZettaPark provides
  a pandas-like DataFrame API that translates Python operations into SQL for distributed execution
  in Lakehouse — no need to write SQL manually for data transformations.
  Covers Session creation, DataFrame construction and transformation (filter/select/join/groupBy),
  result collection (collect/to_pandas/show), writing tables (save_as_table),
  file operations (PUT/GET), and executing SQL.

  Trigger when the user says: "ZettaPark", "zettapark", "DataFrame API", "Python Lakehouse",
  "save_as_table", "session.table", "session.sql", "collect()", "to_pandas",
  "Python data engineering", "Python write to Lakehouse", "Python read from Lakehouse",
  "clickzetta_zettapark_python", "Python ETL", "Python ML on Lakehouse",
  "feature engineering Python", "Python DataFrame Lakehouse".
  Keywords: ZettaPark, DataFrame, pandas-like, Python, SQL translation, distributed compute
---

# ClickZetta ZettaPark

ZettaPark is ClickZetta Lakehouse's Python DataFrame framework. It translates Python operations into SQL for distributed execution in Lakehouse, giving you a pandas-like development experience without writing SQL manually. Use it when you need Python logic (ML, complex transformations, file processing) that operates on Lakehouse data at scale.

See [references/zettapark-api.md](references/zettapark-api.md) for the complete API reference.

## Installation

> ⚠️ **Python version**: Python 3.12 recommended (minimum 3.10; 3.9 and below not supported)

```bash
# Option 1: venv (built-in, recommended)
python3.12 -m venv .venv
source .venv/bin/activate   # macOS/Linux  |  .venv\Scripts\activate (Windows)
pip install clickzetta_zettapark_python

# Option 2: pyenv (when switching Python versions)
pyenv install 3.12.9 && pyenv local 3.12.9
python -m venv .venv && source .venv/bin/activate
pip install clickzetta_zettapark_python

# Option 3: conda (data science environments)
conda create -n lakehouse python=3.12 -y && conda activate lakehouse
pip install clickzetta_zettapark_python
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

# Verify connection
session.sql("SELECT current_user(), current_workspace()").show()
```

---

## Core Workflow

### Read data

```python
from clickzetta.zettapark import functions as F

# From table
df = session.table("orders")
df = session.table("my_schema.orders")

# From SQL
df = session.sql("SELECT * FROM orders WHERE year = 2024")

# From Python data
df = session.create_dataframe([[1, "Alice", 100.0], [2, "Bob", 200.0]],
                               schema=["id", "name", "amount"])
```

### Transform data

```python
result = (
    session.table("orders")
    .filter(F.col("status") == "completed")
    .select("order_id", "customer_id", "amount")
    .with_column("tax", F.col("amount") * 0.1)
    .sort(F.col("amount").desc())
    .limit(100)
)
```

### Aggregate

```python
summary = (
    session.table("orders")
    .group_by("category")
    .agg(
        F.sum("amount").as_("total"),
        F.count("*").as_("cnt"),
        F.avg("amount").as_("avg_amount"),
    )
)
summary.show()
```

### JOIN

```python
orders = session.table("orders")
customers = session.table("customers")

result = orders.join(
    customers,
    orders["customer_id"] == customers["id"],
    "left"
).select(
    orders["order_id"],
    customers["name"],
    orders["amount"]
)
```

### Write data

```python
# Append to existing table
df.write.save_as_table("result_table", mode="append")

# Overwrite (auto-creates table if not exists)
df.write.save_as_table("result_table", mode="overwrite")
```

### Collect results

```python
# Print preview
df.show(20)

# Collect as Row list
rows = df.collect()
for row in rows:
    print(row["id"], row["name"])

# Convert to Pandas DataFrame (small data only — large results will OOM)
pandas_df = df.to_pandas()

# Get row count
print(df.count())
```

---

## Typical Scenarios

### Scenario 1: ETL data processing

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

### Scenario 2: Feature engineering (machine learning)

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

### Scenario 3: Import from local file

```python
import json
import gzip
from clickzetta.zettapark.session import Session

session = Session.builder.configs(config).create()

data = []
with gzip.open('data.json.gz', 'rt', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            data.append(json.loads(line))

df = session.create_dataframe(data)
df.write.save_as_table("my_table", mode="overwrite")
session.close()
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `collect()` timeout | Data volume too large or cluster too small | Increase `sdk.job.timeout`, or test with `limit()` first |
| `to_pandas()` OOM | Result set too large — all data is pulled to local memory | Aggregate/filter before converting to pandas, or process in batches |
| Column name conflict after JOIN | Both tables have a column with the same name | Use `df_left["col"]` to explicitly specify the source |
| `save_as_table` error | Table already exists with incompatible mode | Use `mode="overwrite"` or `mode="append"` |
