---
name: clickzetta-zettapark
description: |
  Use the ZettaPark Python library to work with ClickZetta Lakehouse data through a pandas-like DataFrame API that translates Python transformations into distributed SQL — no manual SQL needed.
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

See [references/zettapark-api.md](references/zettapark-api.md) for the complete API reference, all transformation methods, and worked examples (ETL, feature engineering, file import).

## Installation

> ⚠️ **Python version**: Python 3.12 recommended (minimum 3.10; 3.9 and below not supported)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install clickzetta_zettapark_python
```

## Create Session

```python
from clickzetta.zettapark.session import Session

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service": "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance_id",
    "workspace": "your_workspace",
    "schema": "public",
    "vcluster": "default",
}).create()

session.sql("SELECT current_user(), current_workspace()").show()
```

## Core Pattern

```python
from clickzetta.zettapark import functions as F

# Read → Transform → Write
result = (
    session.table("bronze.raw_orders")
    .filter(F.col("amount") > 0)
    .with_column("tax", F.col("amount") * 0.1)
    .group_by("category")
    .agg(F.sum("amount").as_("total"))
)

result.write.save_as_table("silver.orders_summary", mode="overwrite")
session.close()
```

Key methods: `filter` / `select` / `with_column` / `join` / `group_by` / `agg` / `sort` / `limit`

Collect results: `show()` (preview) · `collect()` (Row list) · `to_pandas()` (small data only) · `count()`

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `collect()` timeout | Data too large or cluster too small | Increase `hints.sdk.job.timeout`, or test with `limit()` first |
| `to_pandas()` OOM | All data pulled to local memory | Aggregate/filter before converting, or process in batches |
| Column name conflict after JOIN | Both tables have same-named column | Use `df_left["col"]` to specify source explicitly |
| `save_as_table` error | Table exists with incompatible mode | Use `mode="overwrite"` or `mode="append"` |
