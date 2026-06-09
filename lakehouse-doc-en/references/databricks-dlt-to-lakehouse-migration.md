# Databricks DLT → Lakehouse Migration Guide: Apparel Retail Streaming Pipeline

If your data pipeline runs on Databricks Delta Live Tables, the core migration effort to Singdata Lakehouse is lower than you might expect — **most PySpark DataFrame code can be reused directly**. DLT uses decorators (`@dlt.table`, `@dlt.expect_or_drop`) to wrap Python functions into pipeline nodes. ZettaPark removes the decorators and replaces them with `df.write.saveAsTable()` — business logic is unchanged, line for line.

This article validates this with a real project: a Databricks DLT-based apparel retail streaming pipeline (Bronze ingestion → Silver SCD2 cleansing → Gold aggregation analytics) fully migrated to Singdata Lakehouse, passing all 16 automated validations.

Full code on GitHub: [databricks2lakehouse-dlt-apparel](https://github.com/clickzetta/databricks2lakehouse-dlt-apparel)

---

## Source Project

[databricks2lakehouse-dlt-apparel](https://github.com/clickzetta/databricks2lakehouse-dlt-apparel) is forked from [jrlasak/databricks_apparel_streaming](https://github.com/jrlasak/databricks_apparel_streaming) (⭐45). The original tech stack is Databricks DLT + Auto Loader + Delta Lake. The project implements a complete data pipeline for an apparel retailer across 4 dimensions (customers, products, stores, transactions), covering streaming ingestion, SCD Type 2 history tracking, data quality constraints, and Gold layer aggregation analytics.

Migrated code is in the `03_lakehouse/` directory, with three available approaches that can be compared file-by-file with `01_source/dlt/`.

## Conclusion First

**Option C (Dynamic Table) is the closest equivalent for DLT pipelines** — declarative definition + automatic scheduled refresh, consistent with DLT's "define and execute" philosophy. If the existing team is comfortable with PySpark DataFrame, Option A (ZettaPark) requires only 5 mechanical substitutions with all business logic fully preserved.

| Option | Files | DLT Equivalent | Characteristics |
|------|------|---------|------|
| **A. ZettaPark Python** | `03_lakehouse/*.py` | `@dlt.table` → `df.write.saveAsTable()` | Minimal code changes, retains PySpark skills |
| **B. Pure SQL** | `03_lakehouse/sql/` | SQL equivalent implementation | SQL-first teams |
| **C. Dynamic Table (GIC)** | `03_lakehouse/dynamic_tables/` | **Native equivalent of @dlt.table** | Declarative + auto-refresh, closest to DLT semantics |

**Option A change list** (ZettaPark main path):

| Change | Effort | Notes |
|--------|--------|------|
| `import dlt` / `from pyspark...` | Very low | `from clickzetta.zettapark import functions as F`, replace package name |
| `spark` global | Very low | `session = Session.builder.configs({}).create()` |
| `@dlt.table(name=X)` | Very low | Add `df.write.mode("overwrite").saveAsTable(X)` as last line of function |
| `@dlt.expect_or_drop("msg","cond")` | Very low | `df.filter(F.col(...)...)`, semantically equivalent |
| `dlt.read_stream("LIVE.X")` / `dlt.read("LIVE.X")` | Very low | `session.table("X")`, same as PySpark |
| `dlt.create_auto_cdc_flow(scd_type=2)` | Low | `F.lead().over(Window.partitionBy(key).orderBy(seq))`, ZettaPark Window is identical to PySpark |
| `F.window("event_time","1 day")` | Very low | `F.to_date(F.col("event_time"))`, ZettaPark has no F.window |
| Auto Loader → | Low | `session.read.csv("vol://...")` batch; use Pipe for streaming in production |

JOIN logic, aggregation functions (`F.sum/count/avg`), `F.when/coalesce/lead/lag`, `Window` — all require no changes, fully consistent with PySpark API.

---

## Tech Stack Comparison

| | Databricks DLT | ZettaPark (after migration) |
|---|---|---|
| Pipeline definition | Python decorator `@dlt.table` | `df.write.mode("overwrite").saveAsTable(X)` |
| Data quality constraints | `@dlt.expect_or_drop("msg","cond")` | `df.filter(condition)` (same semantics) |
| Streaming read | `dlt.read_stream("LIVE.X")` | `session.table("X")` (DT auto-incremental) |
| Static read | `dlt.read("LIVE.X")` | `session.table("X")` |
| SCD Type 2 | `dlt.create_auto_cdc_flow(stored_as_scd_type=2)` | `F.lead().over(Window.partitionBy(key).orderBy(seq))` |
| Time window aggregation | `F.window("event_time","1 day")` | `F.to_date(F.col("event_time"))` |
| File ingestion | Auto Loader (`cloudFiles`) | `session.read.csv("vol://...")` / Pipe (streaming) |
| DataFrame API | PySpark | **Fully consistent** (F.col/when/lead/Window etc.) |

---

![](.topwrite/assets/anim-30-databricks-dlt-migration.svg)

---

## Project Background

Apparel retailer with 4 data streams + Bronze/Silver/Gold three-layer architecture:

| Data Domain | Raw Events | Row Count | Notes |
|--------|---------|------|------|
| Customers | `raw_customers` | 150 | Includes SCD2 update records (30 historical) |
| Products | `raw_products` | 50 | Includes category/brand/size/color |
| Stores | `raw_stores` | 5 | 5 stores |
| Transactions | `raw_sales` | 500 | Includes discount, tax, payment method |

DLT pipeline file structure:

```
01_bronze.py   — Auto Loader streaming ingestion → 4 Bronze tables
02A_silver.py  — @dlt.view + @dlt.expect_or_drop (data quality filtering)
02B_silver.py  — dlt.create_auto_cdc_flow (SCD Type 2 dimension tables)
02C_silver.py  — Sales transaction cleansing
03_gold.py     — 4 Gold aggregation tables
```

---

## Migration Steps

### Step 1: `@dlt.table` / Auto Loader → ZettaPark

DLT uses decorators to declare tables + `spark.readStream` for streaming ingestion. ZettaPark uses `session.read.csv("vol://...")` to load files, with `df.write.saveAsTable()` replacing decorators:

```python
# Databricks DLT (01_source/dlt/01_bronze.py)
@dlt.table(name="bronze_sales")
def bronze_sales():
    return spark.readStream.format("cloudFiles").option("cloudFiles.format","csv").load(VOL_PATH)
```

```python
# ZettaPark (03_lakehouse/01_bronze.py) — minimal rewrite
from clickzetta.zettapark import Session               # ← import pyspark → clickzetta.zettapark
session = Session.builder.configs({...}).create()      # ← spark global injection → explicit creation

df = session.read.option("header","true").csv("vol://apparel_bronze.raw_data/sales.csv")
#   readStream.format("cloudFiles")... → session.read.csv("vol://...")
df.write.mode("overwrite").saveAsTable("apparel_bronze.raw_sales")
#   @dlt.table(name=X) → df.write.saveAsTable(X) (last line of function body)
```

> 💡 **Note**: Auto Loader continuously monitors new files (streaming). The Lakehouse equivalent is **Pipe** (automatically ingests after configuration). Use Pipe instead of COPY INTO in production environments.

### Step 2: `@dlt.expect_or_drop` → `df.filter()`

DLT data quality constraints translate directly to ZettaPark `.filter()` — semantically equivalent, API consistent:

```python
# Databricks DLT (02A_silver.py)
@dlt.view(name="customers_cleaned_stream")
@dlt.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL")
@dlt.expect("realistic_age", "age >= 18 AND age <= 100")
def customers_cleaned_stream():
    return dlt.read_stream(f"LIVE.{BRONZE_CUSTOMERS}")
```

```python
# ZettaPark (03_lakehouse/02B_silver.py)
customers = session.table("apparel_bronze.raw_customers")  # dlt.read_stream → session.table()
customers = (customers
    .filter(F.col("customer_id").isNotNull())          # @dlt.expect_or_drop("valid_customer_id",...)
    .filter((F.col("age") >= 18) & (F.col("age") <= 100))  # @dlt.expect("realistic_age",...)
)
```

### Step 3: SCD Type 2 — `dlt.create_auto_cdc_flow` → `LEAD()` Window Function

`create_auto_cdc_flow(stored_as_scd_type=2)` is fundamentally a LEAD window function. ZettaPark implements the equivalent logic directly — `F.lead()` and `Window` APIs are fully consistent between the two:

```python
# Databricks DLT (02B_silver.py)
dlt.create_auto_cdc_flow(
    target=SILVER_CUSTOMERS,
    source=f"live.{CUSTOMERS_CLEANED_STREAM}",
    keys=["customer_id"],
    sequence_by=F.col("last_update_time"),
    stored_as_scd_type=2,
)
```

```python
# ZettaPark (03_lakehouse/02B_silver.py)
from clickzetta.zettapark.window import Window   # ← pyspark.sql.window → clickzetta.zettapark.window

w = Window.partitionBy("customer_id").orderBy("last_update_time")
# F.lead() and Window API are fully consistent, no changes needed
silver_customers = customers.withColumn(
    "__end_at", F.lead("last_update_time").over(w)   # SCD2 end timestamp
).withColumn(
    "__is_current", F.lead("last_update_time").over(w).isNull()
).withColumn(
    "__end_at", F.coalesce(F.col("__end_at"), F.lit("9999-12-31 23:59:59").cast(TimestampType()))
)
silver_customers.write.mode("overwrite").saveAsTable("apparel_silver.silver_customers")
```

**Result**: 150 raw records → 150 rows (including 30 historical) → 120 current snapshot records (`__is_current = TRUE`).

### Step 4: Time Window Aggregation — `F.window()` → `F.to_date()`

`F.window("event_time","1 day")` is not implemented in ZettaPark. Use `F.to_date()` instead (functionally equivalent, results consistent):

```python
# Databricks DLT (03_gold.py)
df.groupBy(F.window("event_time","1 day").alias("sale_window"), "store_id","store_name") \
  .agg(F.round(F.sum("total_amount"),2).alias("total_revenue")) \
  .select(F.col("sale_window.start").cast("date").alias("sale_date"), ...)
```

```python
# ZettaPark (03_lakehouse/03_gold.py)
facts.withColumn("sale_date", F.to_date(F.col("event_time")))   # F.window → F.to_date
     .groupBy("sale_date","store_id","store_name")
     .agg(F.round(F.sum("total_amount"),2).alias("total_revenue"),
          F.count("transaction_id").alias("total_transactions"), ...)
```

> 💡 `F.to_date()` is equivalent to truncating to the day, which produces exactly the same grouping result as `F.window("1 day")`.

---

## Pure SQL Alternative

If the team prefers SQL, `03_lakehouse/sql/` provides equivalent SQL scripts:

```bash
cz-cli sql --file 03_lakehouse/sql/02_silver.sql --profile aws_singapore_prod --sync --write
cz-cli sql --file 03_lakehouse/sql/03_gold.sql   --profile aws_singapore_prod --sync --write
```

| DLT Python | SQL Equivalent |
|---|---|
| `@dlt.expect_or_drop` | `WHERE condition` |
| `create_auto_cdc_flow(scd=2)` | `LEAD() OVER (PARTITION BY key ORDER BY seq)` |
| `F.window("event_time","1 day")` | `DATE_TRUNC('day', event_time)` |

ZettaPark is the recommended primary path (minimal code changes, retains PySpark skills); SQL is suitable for SQL-first teams or rapid validation.

---

## Option C: Dynamic Table (GIC) — Native Equivalent of DLT

Dynamic Table is the most direct equivalent of DLT's `@dlt.table` — declare SQL declaratively, and the platform automatically refreshes on schedule. DLT triggers on new data automatically; Dynamic Table refreshes on a `REFRESH INTERVAL` schedule. Logically equivalent.

```python
# Databricks DLT — declarative pipeline
@dlt.table(name="gold_daily_sales_by_store")
def gold_daily_sales_by_store():
    return df.groupBy(F.window("event_time","1 day"), "store_id","store_name") \
             .agg(F.sum("total_amount").alias("total_revenue"))
```

```sql
-- Lakehouse Dynamic Table — direct equivalent (03_lakehouse/dynamic_tables/gold_dynamic_tables.sql)
CREATE OR REPLACE DYNAMIC TABLE apparel_gold.dt_daily_sales_by_store
REFRESH INTERVAL 10 MINUTE    -- DLT triggers on new data; DT triggers on schedule
VCLUSTER DEFAULT
AS
SELECT CAST(event_time AS DATE) AS sale_date, store_id, store_name,
    ROUND(SUM(total_amount), 2) AS total_revenue, ...
FROM apparel_gold.denormalized_sales_facts
GROUP BY CAST(event_time AS DATE), store_id, store_name;

-- Manual trigger (equivalent to DLT pipeline trigger)
REFRESH DYNAMIC TABLE apparel_gold.dt_daily_sales_by_store;
```

| DLT | Dynamic Table | Notes |
|---|---|---|
| `@dlt.table(name=X)` | `CREATE DYNAMIC TABLE X ... AS SELECT ...` | Direct equivalent |
| Auto-refresh on new data | `REFRESH INTERVAL N MINUTE` | Different scheduling method, semantically equivalent |
| `F.window("1 day")` | `CAST(event_time AS DATE)` | DT uses SQL |
| `create_auto_cdc_flow(scd=2)` | `LEAD() OVER Window` embedded in DT definition | Standard window function |
| DLT pipeline DAG | DT dependencies (downstream DT references upstream DT) | Declarative dependencies |

Tested in AWS Singapore: 4 Dynamic Tables created and refreshed, all passed e2e validation: `dt_customers_current` (150 rows / 120 current), `dt_daily_sales_by_store` (367), `dt_product_performance` (50), `dt_customer_lifetime_value` (96).

## About Pipe (Auto Loader Equivalent)

**Pipe** is the Databricks Auto Loader equivalent — continuously monitors object storage (OSS/S3/COS) for new files, automatically triggering COPY INTO ingestion. Tested in AWS Singapore: after uploading a new CSV to S3, Pipe auto-ingested within 15 seconds.

```sql
-- Step 1: Create External Volume (connected to S3/OSS/COS)
CREATE EXTERNAL VOLUME apparel_bronze.s3_sales_landing
    LOCATION 's3://your-bucket/apparel_landing/'
    USING CONNECTION s3_conn
    DIRECTORY = (enable=true, auto_refresh=true)
    RECURSIVE = true;

-- Step 2: Create table (External Volume does not support inferSchema, explicit definition required)
CREATE TABLE apparel_bronze.raw_sales (
    transaction_id BIGINT, store_id BIGINT, event_time STRING,
    customer_id BIGINT, product_id BIGINT, quantity BIGINT,
    unit_price DOUBLE, total_amount DOUBLE, payment_method STRING,
    discount_applied DOUBLE, tax_amount DOUBLE
);

-- Step 3: Create Pipe
-- DLT: spark.readStream.format("cloudFiles").option("cloudFiles.format","csv").load(PATH)
CREATE OR REPLACE PIPE apparel_bronze.pipe_sales
    VIRTUAL_CLUSTER = 'DEFAULT'
    INGEST_MODE = 'LIST_PURGE'    -- Poll for new files, equivalent to Auto Loader LIST mode
AS COPY INTO apparel_bronze.raw_sales
FROM VOLUME apparel_bronze.s3_sales_landing
USING CSV OPTIONS ('header'='true')
PURGE = TRUE                      -- Delete landing zone files after processing
ON_ERROR = CONTINUE;
```

> 💡 **Pipe vs COPY INTO**: COPY INTO is a one-time batch load; Pipe continuously monitors and auto-triggers when new files arrive — a direct equivalent to Auto Loader. Internal Volumes only support COPY INTO; Pipe requires an External Volume (OSS/S3/COS).

---

## E2E Validation Results

Tested on AWS Singapore instance (`aws_singapore_prod`), **20/20 all passed** (including Dynamic Table validation):

| Check | Expected | Result |
|--------|--------|------|
| bronze.raw_customers | 150 | ✅ |
| bronze.raw_products | 50 | ✅ |
| bronze.raw_stores | 5 | ✅ |
| bronze.raw_sales | 500 | ✅ |
| silver_customers (including history) | 150 | ✅ |
| silver_products | 50 | ✅ |
| silver_stores | 5 | ✅ |
| silver_sales_transactions | 500 | ✅ |
| silver_customers_current | 120 | ✅ |
| silver_products_current | 50 | ✅ |
| silver_stores_current | 5 | ✅ |
| gold.denormalized_sales_facts | 500 | ✅ |
| gold.gold_product_performance | 50 | ✅ |
| Total sales amount | 281,490 | ✅ |
| Customers with purchases | 96 | ✅ |
| SCD2 historical records | 30 | ✅ |
| **dt_customers_current** (Dynamic Table) | 150 | ✅ |
| **dt_daily_sales_by_store** (Dynamic Table) | ≥100 | ✅ 367 |
| **dt_product_performance** (Dynamic Table) | 50 | ✅ |
| **dt_customer_lifetime_value** (Dynamic Table) | 96 | ✅ |
| SCD2 historical records | 30 | ✅ |

---

## Notes

- **Streaming vs batch**: Auto Loader continuously monitors new files; COPY INTO is a one-time batch. Use Lakehouse **Pipe** instead of Auto Loader in production — automatically ingests new files after configuration, no manual triggering required.
- **`@dlt.expect` warn semantics**: `expect` (warn level) in DLT counts but does not drop records. When migrating to SQL, you can choose to not filter (ignore entirely) or add a `WHERE` filter (equivalent to upgrading to `expect_or_drop`). Decide based on business requirements.
- **DT auto-incremental**: Lakehouse Dynamic Tables automatically refresh incrementally after definition (similar to DLT streaming updates), without needing to explicitly write `read_stream`.
- **SCD2 `__is_current` field**: `LEAD()` returning NULL means there is no subsequent version, i.e., this is the current record. `COALESCE(__end_at, '9999-12-31')` is the standard SCD2 convention, with identical behavior on both sides.

## Related Documentation

### Dynamic Table (GIC)

- [Dynamic Table Overview](dynamic-table-overview.md): Declarative incremental computation principles and architecture
- [Dynamic Table SQL Reference](dynamic-table-sql.md): Full CREATE DYNAMIC TABLE syntax
- [Dynamic Table Usage Guide](SQL_DynamicTable_Guide.md): Unified batch-streaming pipeline examples

### Other Migration Guides

- [Databricks Notebook → Lakehouse Migration Guide (Retail Medallion Pipeline)](databricks-notebook-to-studio-migration.md)
- [dbt-databricks → dbt-clickzetta Migration Guide (Financial Payment Pipeline)](dbt-databricks-to-clickzetta-migration.md)
- [Spark Migration Guide](spark-migration-guide.md): Spark ecosystem migration overview
