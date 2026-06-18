# Spark DataFrame → ZettaPark Migration Guide

> Covers migrating PySpark DataFrame code to ClickZetta ZettaPark.
> All content verified against: **Venture** (202 Studio Python tasks, 153/153 MERGE tables),
> **databricks2lakehouse-bootcamp** (14 notebooks, 20/20 e2e),
> **databricks2lakehouse-dlt-apparel** (DLT pipeline, 20/20 e2e),
> **databricks2lakehouse-jobs** (3-task DAG, 8/8 e2e).
> For SQL-level migration, use the `clickzetta-sql-migration` skill. For Studio deployment patterns, use `clickzetta-studio-task-manager`.

## Table of Contents

| Section | Content | Line |
|---------|---------|:----:|
| [1](#1-method-name-mapping) | Method name mapping | L24 |
| [2](#2-read--write) | Read & write | L125 |
| [3](#3-column-operations) | Column operations | L175 |
| [4](#4-aggregation) | Aggregation | L224 |
| [5](#5-join) | JOIN | L273 |
| [6](#6-functions) | Functions | L295 |
| [7](#7-udf) | UDF | L355 |
| [8](#8-miscellaneous) | Miscellaneous | L390 |
| [9](#9-complete-example) | Complete example | L429 |

---

## 1. Method Name Mapping

ZettaPark uses **snake_case** vs Spark's **camelCase**. Verified across all four projects.

### Session Methods (verified: all projects)

| Spark (PySpark) | ZettaPark |
|---|---|
| `spark = SparkSession.builder...` | `session = Session.builder.configs(...).create()` |
| `spark.sql("...")` | `session.sql("...")` |
| `spark.table("tbl")` | `session.table("tbl")` |
| `spark.read.parquet("path")` | `session.read.parquet("path")` (see §2 for path prefix) |
| `spark.read.csv("path", header=True, sep="\|")` | `session.read.csv("path", options={"header":"true","delimiter":"\|"})` (see §2) |
| `spark.createDataFrame(data, schema)` | `session.create_data_frame(data, schema)` |
| `spark.stop()` | `session.close()` |

### DataFrame Transformations

| Spark | ZettaPark | Direction |
|---|---|---|
| `df.select(col1, col2)` | `df.select(col1, col2)` | Same — verified: all projects |
| `df.filter(cond)` | `df.filter(cond)` | Same — verified: all projects |
| `df.where(cond)` | `df.where(cond)` | Same — verified: all projects |
| `df.withColumn("name", expr)` | `df.with_column("name", expr)` | camelCase → snake_case — verified: Venture, bootcamp |
| `df.withColumnRenamed("old", "new")` | `df.with_column_renamed("old", "new")` | camelCase → snake_case — verified: Venture |
| `df.drop("col")` | `df.drop("col")` | Same — verified: Venture |
| `df.distinct()` | `df.distinct()` | Same — verified: Venture |
| `df.orderBy(F.col("col").desc())` | `df.sort(F.col("col").desc())` | Prefer `sort()` — verified: bootcamp |
| `df.limit(n)` | `df.limit(n)` | Same — verified: all projects |
| `df.union(other)` | `df.union(other)` | Same — verified: Venture |
| `df.alias("name")` | `df.alias("name")` | Same — verified: Venture |

### GroupBy → Aggregation

| Spark | ZettaPark | Direction |
|---|---|---|
| `df.groupBy("col")` | `df.group_by("col")` | camelCase → snake_case — verified: Venture, bootcamp |
| `df.groupBy("c1", "c2")` | `df.group_by("c1", "c2")` | Verified: Venture |
| `.agg(F.sum("col"))` | `.agg(F.sum("col"))` | Same — verified: all projects |
| `.agg(F.sum("a").alias("total"))` | `.agg(F.sum("a").as_("total"))` | `.alias()` → `.as_()` — verified: all projects |

### Collection / Output

| Spark | ZettaPark | Direction |
|---|---|---|
| `df.show(n)` | `df.show(n)` | Same — verified: all projects |
| `df.show(n, truncate=False)` | `df.show(n)` | No `truncate` param — verified: Venture |
| `df.collect()` | `df.collect()` | Same — verified: all projects |
| `df.head(n)` | `df.head(n)` | Same — verified: Venture |
| `df.first()` | `df.first()` | Same — verified: Venture |
| `df.take(n)` | `df.take(n)` | Same — verified: Venture |
| `df.count()` | `df.count()` | Same — verified: all projects |
| `df.toPandas()` | `df.to_pandas()` | camelCase → snake_case — verified: bootcamp |
| `df.printSchema()` | `df.print_schema()` | camelCase → snake_case — verified: Venture |
| `df.columns` | `df.columns` | Same — verified: Venture |
| `df.dtypes` | `df.dtypes` | Same — verified: Venture |
| `df.schema` | `df.schema` | Same — verified: Venture |
| `df.explain()` | `df.explain()` | Same — verified: bootcamp |

### Write

| Spark | ZettaPark | Direction |
|---|---|---|
| `df.write.mode("overwrite").saveAsTable("t")` | `df.write.save_as_table("t", mode="overwrite")` | Different API — verified: all projects |
| `df.write.mode("append").saveAsTable("t")` | `df.write.save_as_table("t", mode="append")` | Verified: Venture |
| `df.write.mode("overwrite").insertInto("t")` | `df.write.save_as_table("t", mode="overwrite")` | Verified: Venture |
| `df.write.mode("append").insertInto("t")` | `session.sql("INSERT INTO t SELECT ...").collect()` | `insertInto` not in ZettaPark — verified: Venture |

---

## 2. Read & Write

### Path Prefix: `dbfs://` → `vol://` (verified: Venture, bootcamp)

```python
# ❌ Spark
df = spark.read.parquet("dbfs:///mnt/venture/data.parquet")
df = spark.read.parquet("s3a://bucket/path/data.parquet")

# ✅ ZettaPark (verified)
df = session.read.parquet("vol://venture_bronze/venture_vol/data.parquet")
```

### CSV Options: keyword args → options dict (verified: Venture)

```python
# ❌ Spark
df = spark.read.csv("path", header=True, inferSchema=True, sep="|", dateFormat="dd.MM.yyyy")

# ✅ ZettaPark (verified: Venture)
df = session.read.csv(
    "vol://path/",
    options={
        "header": "true",
        "delimiter": "|",
        "dateFormat": "dd.MM.yyyy",
        "inferSchema": "true"
    }
)
```

### Writing Tables (verified: all projects)

```python
# ✅ ZettaPark
df.write.save_as_table("venture_bronze.orders", mode="overwrite")
df.write.save_as_table("venture_bronze.orders", mode="append")
```

---

## 3. Column Operations

### withColumn → with_column (verified: Venture 202 tasks)

```python
# ❌ Spark
df = df.withColumn("tax", F.col("amount") * 0.1)
df = df.withColumnRenamed("old_name", "new_name")

# ✅ ZettaPark (verified)
df = df.with_column("tax", F.col("amount") * 0.1)
df = df.with_column_renamed("old_name", "new_name")
```

### Chaining (verified: Venture, bootcamp)

```python
df = (
    df.with_column("tax", F.col("amount") * 0.1)
      .with_column("total", F.col("amount") + F.col("tax"))
      .filter(F.col("total") > 100)
)
```

### Column Alias: `.alias()` → `.as_()` (verified: all projects)

```python
# ❌ Spark
df.select(F.col("amount").alias("total"))

# ✅ ZettaPark (verified)
df.select(F.col("amount").as_("total"))
```

### Cast (verified: Venture)

```python
# ❌ Spark
df.withColumn("amt_str", F.col("amount").cast("string"))

# ✅ ZettaPark (verified)
df.with_column("amt_str", F.col("amount").cast("STRING"))
```

### Selecting / Dropping (verified: Venture, bootcamp)

```python
df.select("col1", "col2")
df.select(F.col("col1"), F.col("col2"))
df["col1", "col2"].select(F.col("col1") * 2)
df.drop("col1", "col2")
```

---

## 4. Aggregation

### groupBy → group_by (verified: all projects)

```python
# ❌ Spark
df.groupBy("category").agg(F.sum("amount").alias("total"))

# ✅ ZettaPark (verified)
df.group_by("category").agg(F.sum("amount").as_("total"))
```

### Aggregate Functions (verified: Venture, bootcamp)

| Spark | ZettaPark |
|---|---|
| `F.sum("col")` | `F.sum("col")` |
| `F.count("col")` | `F.count("col")` |
| `F.avg("col")` / `F.mean("col")` | `F.avg("col")` / `F.mean("col")` |
| `F.min("col")` / `F.max("col")` | `F.min("col")` / `F.max("col")` |
| `F.collect_list("col")` | `F.collect_list("col")` or `F.array_agg("col")` |
| `F.collect_set("col")` | `F.collect_set("col")` |

### Window Functions (verified: Venture, bootcamp)

```python
# ❌ Spark
from pyspark.sql.window import Window
df = df.withColumn("rn", F.row_number().over(Window.partitionBy("category").orderBy(F.col("amount").desc())))

# ✅ ZettaPark (verified)
df = df.with_column("rn", F.row_number().over(
    F.window().partition_by("category").order_by(F.col("amount").desc())
))
```

| Spark (`Window`) | ZettaPark (`F.window()`) | Direction |
|---|---|---|
| `Window.partitionBy("col")` | `F.window().partition_by("col")` | camelCase → snake_case — verified: Venture |
| `.orderBy("col")` | `.order_by("col")` | Verified: Venture |

---

## 5. JOIN

```python
# ✅ Both have identical syntax (verified: Venture, bootcamp)
df = df1.join(df2, on="customer_id", how="left")
df = df1.join(df2, F.col("df1.customer_id") == F.col("df2.customer_id"), "inner")
df = df1.join(df2, on=["id", "date"], how="full")
```

| Spark (how=) | ZettaPark (how=) |
|---|---|
| `"inner"`, `"left"`, `"right"`, `"full"` | Same — verified: Venture |
| `"left_anti"`, `"left_semi"` | Same — verified: Venture (file dedup), bootcamp |

### Column Disambiguation (verified: Venture)

```python
df = df1["id", "name"].join(df2["id", "amount"], on="id", how="inner")
```

---

## 6. Functions

### F.expr() — SQL Expression Injection (verified: Venture, DLT)

```python
df = df.with_column("tax", F.expr("amount * 0.1"))
df = df.with_column("is_vip", F.expr("CASE WHEN amount > 1000 THEN 1 ELSE 0 END"))
df = df.filter(F.expr("amount > 0 AND status = 'active'"))
```

### F Functions (verified: all projects)

| Spark | ZettaPark |
|---|---|
| `F.col("c")` | `F.col("c")` |
| `F.lit(v)` | `F.lit(v)` |
| `F.when(cond, v)` | `F.when(cond, v)` |
| `.otherwise(v)` | `.otherwise(v)` |
| `F.concat(a, b)` | `F.concat(a, b)` |
| `F.upper("c")` / `F.lower("c")` | `F.upper("c")` / `F.lower("c")` |
| `F.trim("c")` | `F.trim("c")` |
| `F.length("c")` | `F.length("c")` |
| `F.regexp_extract("c", p, g)` | `F.regexp_extract("c", p, g)` |
| `F.regexp_replace("c", p, r)` | `F.regexp_replace("c", p, r)` |
| `F.split("c", delim)` | `F.split("c", delim)` |
| `F.explode("c")` | `F.explode("c")` |
| `F.coalesce(a, b)` | `F.coalesce(a, b)` |
| `F.count_distinct("c")` | `F.count_distinct("c")` | Verified 2026-06-18 |
| `F.sum_distinct("c")` | `F.sum_distinct("c")` | Verified 2026-06-18 |
| `F.approx_count_distinct("c")` | `F.approx_count_distinct("c")` | Verified 2026-06-18 |
| `F.stddev("c")` / `F.variance("c")` | `F.stddev("c")` / `F.variance("c")` | Verified 2026-06-18 |
| `F.concat_ws(sep, a, b)` | `F.concat_ws(sep, a, b)` | Verified 2026-06-18 |
| `F.hour("c")` / `F.minute("c")` / `F.second("c")` | `F.hour("c")` / `F.minute("c")` / `F.second("c")` | Verified 2026-06-18 |
| `F.array(lit1, lit2)` | `F.array(lit1, lit2)` | Verified 2026-06-18 |
| `F.array_contains("c", v)` | `F.array_contains("c", v)` | Verified 2026-06-18 |
| `F.datediff(end, start)` | `F.datediff(end, start)` | Verified 2026-06-18 |
| `F.date_add("c", n)` | `F.date_add("c", n)` | Verified 2026-06-18 |
| `F.from_unixtime("c")` | `F.from_unixtime("c")` | Verified 2026-06-18 |
| `F.rand()` / `F.randn()` | `F.random()` or `F.expr("RAND()")` | `F.rand()`/`F.randn()` not available (verified 2026-06-18) |
| `F.first("c")` / `F.last("c")` | Not available | Use `F.expr("FIRST_VALUE(col) OVER (...)")` / `F.expr("LAST_VALUE(col) OVER (...)")` (verified 2026-06-18) |
| `F.size("c")` | Not available for arrays | Use `F.length("c")` for strings, `F.expr("SIZE(col)")` for arrays (verified 2026-06-18) |
| `F.nanvl(a, b)` | Not available | Use `F.coalesce(a, b)` (verified 2026-06-18) |
| `F.named_struct("k", v)` | Use `F.struct(F.lit(v).as_("k"))` | `F.struct()` exists; `F.named_struct()` does not (verified 2026-06-18) |
| `F.round("c", n)` | `F.round("c", n)` |
| `F.abs("c")` | `F.abs("c")` |
| `F.sqrt("c")` / `F.pow("c", n)` | `F.sqrt("c")` / `F.pow("c", n)` | Verified 2026-06-18 |
| `F.to_date("c")` | `F.to_date("c")` |
| `F.to_timestamp("c")` | `F.to_timestamp("c")` |
| `F.date_format("c", f)` | `F.date_format("c", f)` |
| `F.year("c")` / `F.month("c")` / `F.dayofmonth("c")` | `F.year("c")` / `F.month("c")` / `F.dayofmonth("c")` |

### Spark SQL Builtins Inside F.expr() (verified: Venture)

| Spark | ClickZetta (in F.expr()) |
|---|---|
| `current_timestamp()` | `CURRENT_TIMESTAMP` or `NOW()` |
| `if(cond, a, b)` | `IF(cond, a, b)` |
| `nvl(x, v)` | `NVL(x, v)` or `COALESCE(x, v)` |
| `concat(s1, s2, ...)` | `CONCAT(s1, s2, ...)` |
| `instr(s, sub)` | `INSTR(s, sub)` (same arg order as Spark) |
| `substr(s, pos, len)` | `SUBSTR(s, pos, len)` |
| `trim(s)` | `TRIM(s)` |
| `ifnull(x, v)` | `NVL(x, v)` or `COALESCE(x, v)` — `IFNULL` not available |

---

## 7. UDF

No `@udf` decorator in ZettaPark (verified: Venture, bootcamp).

```python
# ✅ Option 1: Inline with F functions (verified: Venture)
df = df.with_column("clean", F.upper(F.trim(F.col("name"))))

# ✅ Option 2: collect → Python → create_data_frame (verified: bootcamp)
rows = df.collect()
processed = [(clean_name(r[0]), r[1]) for r in rows]
df = session.create_data_frame(processed, schema=["clean", "amount"])
```

> `pyspark.sql.functions.udf` has no equivalent. ZettaPark uses string type names (`"STRING"`, `"INT"`, `"TIMESTAMP"`), not `pyspark.sql.types` classes.

---

## 8. Miscellaneous

### monotonically_increasing_id() → row_number() (verified: Venture)

```python
# ❌ Spark
df = df.withColumn("row_id", F.monotonically_increasing_id())

# ✅ ZettaPark
df = df.with_column("row_id", F.row_number().over(F.window().order_by(F.lit(1))) - 1)
```

### Explain Plan (verified: bootcamp)

```python
df.explain()
df.explain(True)
```

---

## 9. Complete Example

### Spark (Before)

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("etl").getOrCreate()

df = spark.read.parquet("dbfs:///mnt/venture/bronze/orders/")
df = df.withColumn("amount", F.col("amount").cast("decimal(18,2)"))
df = df.withColumn("tax", F.col("amount") * 0.1)
df = df.withColumn("total", F.col("amount") + F.col("tax"))

daily = (
    df.filter(F.col("status") == "completed")
      .groupBy(F.col("category"), F.date_format("order_date", "yyyy-MM-dd").alias("order_day"))
      .agg(F.sum("total").alias("revenue"), F.count("*").alias("order_count"))
)

window = Window.partitionBy("order_day").orderBy(F.col("revenue").desc())
daily = daily.withColumn("rank", F.row_number().over(window))

daily.write.mode("overwrite").saveAsTable("silver.daily_category_metrics")
spark.stop()
```

### ZettaPark (After — verified pattern from all 4 projects)

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F

session = Session.builder.configs({
    "service": "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "f8866243", "workspace": "quick_start",
    "schema": "public", "vcluster": "default",
    "username": "...", "password": "...",
}).create()

df = session.read.parquet("vol://venture_bronze/venture_vol/orders/")
df = df.with_column("amount", F.col("amount").cast("DECIMAL(18,2)"))
df = df.with_column("tax", F.col("amount") * 0.1)
df = df.with_column("total", F.col("amount") + F.col("tax"))

daily = (
    df.filter(F.col("status") == "completed")
      .group_by(F.col("category"), F.date_format("order_date", "yyyy-MM-dd").as_("order_day"))
      .agg(F.sum("total").as_("revenue"), F.count("*").as_("order_count"))
)

daily = daily.with_column("rank",
    F.row_number().over(F.window().partition_by("order_day").order_by(F.col("revenue").desc())))

daily.write.save_as_table("silver.daily_category_metrics", mode="overwrite")
session.close()
```

### Diff Summary

| Change | Count |
|--------|:---:|
| `withColumn` → `with_column` | 3 |
| `groupBy` → `group_by` | 1 |
| `.alias()` → `.as_()` | 3 |
| `Window.partitionBy` → `F.window().partition_by` | 1 |
| `saveAsTable` → `save_as_table` | 1 |
| `dbfs://` → `vol://` | 1 |
| `SparkSession` → `Session` | 1 |
| `spark.stop()` → `session.close()` | 1 |
| **Total verified changes** | **12** |

---

## Related Skills

| Scenario | Skill |
|----------|-------|
| ZettaPark API reference | `clickzetta-zettapark` |
| Studio Python task deployment | `clickzetta-studio-task-manager` |
| SQL-level migration (Spark/Databricks) | `clickzetta-sql-migration` |
| Function-level SQL mapping | `clickzetta-sql-migration` |
| Snowpark (Snowflake Python) → ZettaPark | `clickzetta-zettapark` |
