# ZettaPark Python SDK

ZettaPark is the Python DataFrame API for Singdata Lakehouse — you write data processing logic in a pandas-like syntax, and ZettaPark automatically translates it into SQL for distributed execution on Lakehouse, with no need to write SQL by hand.

![](/.topwrite/assets/27-zettapark-overview.svg)

**When to use ZettaPark**: Ideal for scenarios where you have existing Python/PySpark data processing code and want to migrate to Lakehouse, or when you prefer using Python control flow (loops, conditionals) to dynamically build queries.

| Need | Recommended Tool |
|------|---------|
| DataFrame operations, pandas/PySpark-style | ZettaPark (this section) |
| Execute fixed SQL, script automation | [Python Connector](../python_reference/connector.md) |
| High-speed bulk writes (millions of rows) | [BulkLoad](../java_reference/bulkload.md) |
| ML feature engineering + model training | ZettaPark + Python ML libraries |

## Core Mechanism

ZettaPark uses a **lazy execution** model: calling methods like `filter()`, `select()`, and `groupBy()` only builds an execution plan — nothing runs immediately. Only when you call `collect()`, `show()`, `to_pandas()`, or `save_as_table()` does the entire plan get translated into a single SQL statement and sent to Lakehouse for execution.

The following three steps only build the plan and produce no network requests:

```python
df = session.table("orders")
df_filtered = df.filter(F.col("amount") > 100)
df_grouped = df_filtered.groupBy("region").agg(F.sum("amount").alias("total"))
```

Calling `collect()` triggers execution — the entire chain is translated into a single SQL statement sent to Lakehouse:

```python
result = df_grouped.collect()
```

This means complex multi-step transformations produce only one network round-trip, with computation running distributed on the Lakehouse cluster — not limited by local memory.

## This Section

| Document | Content |
|------|------|
| [Quick Start](zettapark-quick-start.md) | Installation, establishing a session, your first DataFrame |
| [DataFrame API Guide](zettapark-dataframe-guide.md) | filter / select / join / groupBy / window functions / reading and writing tables |
| [Functions Reference](zettapark-functions-guide.md) | Quick reference for the `functions` module |
| [Data Engineering in Practice](zettapark-etl-guide.md) | Complete ETL workflow example |
| [Volume and File Operations](zettapark-volume-guide.md) | PUT / GET files, object storage integration |
| [Consuming Table Streams](zettapark-stream-guide.md) | Incremental data processing |
| [Creating Dynamic Tables](zettapark-dynamic-table-guide.md) | Define auto-refreshing computed tables with Python |
| [Feature Engineering](zettapark-feature-engineering.md) | Machine learning feature processing |
| [Credit Scoring in Practice](credit-scoring-with-zettapark.md) | End-to-end case: ZettaPark + Python ML libraries |
