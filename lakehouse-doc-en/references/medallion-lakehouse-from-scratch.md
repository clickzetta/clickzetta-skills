# Building a Medallion Lakehouse from Scratch on Singdata Lakehouse

If you've worked with the Medallion architecture on Databricks, migrating to Singdata Lakehouse is mostly an environment configuration exercise — the modeling logic and code stay the same. Bronze ingestion, Silver cleansing, Gold dimensional modeling — all of that thinking and code carries over directly to ZettaPark.

This article walks through a complete three-layer modeling process using a real migration project: moving a Medallion architecture example built on the Apache Spark stack (Databricks + PySpark) to Singdata Lakehouse. After 22 automated validation checks, 20/22 passed (the 2 warnings stem from source data quality issues, not from the migration itself).

Full code on GitHub: [spark2lakehouse-medallion](https://github.com/clickzetta/spark2lakehouse-medallion)

---

## The Original Project

[spark2lakehouse-medallion](https://github.com/clickzetta/spark2lakehouse-medallion) is adapted from [DataWithBaraa/databricks_bootcamp_2026](https://github.com/DataWithBaraa/databricks_bootcamp_2026). It demonstrates how to use the Medallion architecture on Databricks to integrate data from two systems — CRM and ERP — and produce a dimensional model ready for BI analysis. The project includes 6 source tables (3 from CRM + 3 from ERP), which are processed through three layers to produce 2 dimension tables (`dim_customers`, `dim_products`) and 1 fact table (`fact_sales`).

The migrated code lives in the `03_lakehouse/` directory. The original Databricks Notebooks are preserved in `01_spark/` for side-by-side comparison.

## Technology Stack Comparison

| | Original | After Migration |
|---|---|---|
| Compute engine | Apache Spark (Databricks) | Singdata Lakehouse |
| DataFrame API | PySpark (`pyspark.sql`) | ZettaPark (`clickzetta.zettapark`) |
| Development environment | Databricks Notebook | Jupyter Notebook (local) |
| Storage format | Delta Lake | Lakehouse native tables |
| File storage | DBFS / ADLS | Volume (`vol://schema.vol/...`) |
| Session management | `spark` (globally injected) | `Session.builder.configs({}).create()` |
| Method naming | `withColumn` / `withColumnRenamed` | `with_column` / `with_column_renamed` |
| Write method | `df.write.mode("overwrite").saveAsTable(t)` | `df.write.save_as_table(t, mode="overwrite")` |
| Layer isolation | Delta databases | Separate schemas (bronze / silver / gold) |

The main changes are in the runtime environment — switching from Databricks Notebook to local Jupyter, and from DBFS to Volume. The core data processing and modeling logic is completely unchanged: cleansing, deduplication, multi-source JOINs, Window functions, dimensional modeling — all of these work the same way in ZettaPark as in PySpark. Business logic (`F.when().otherwise()`, `Window.partition_by().order_by()`, `df.join()`, `df.filter()`) is fully compatible — not a single line needs to change.

This project achieves roughly 90% code compatibility. Changes are concentrated in four areas: import paths, Session creation, method naming, and write syntax — all mechanical substitutions. If the original project doesn't rely on Databricks' globally injected `spark` (i.e., it runs with local PySpark), compatibility can approach 100%. Projects that use Python UDFs or `df.write.partitionBy()` will see somewhat lower compatibility.

---

![](.topwrite/assets/anim-06-medallion-pipeline.svg)

---

## Architecture Overview

The Medallion architecture divides data processing into three layers, each with a clear responsibility boundary:

```
Data sources (CSV)
    ↓  session.read.csv("vol://...")
Bronze layer (schema: bronze)
    Raw data, no transformations — format normalization only
    ↓  with_column / filter / drop_duplicates
Silver layer (schema: silver)
    Cleansing, deduplication, standardization, multi-source integration
    ↓  join + row_number().over(window)
Gold layer (schema: gold)
    Dimensional modeling, dim/fact tables, ready for analytics
```

The three layers map to three separate schemas — physically isolated, with no cross-layer interference. Each layer only reads from the layer above it.

---

## The Medallion Data Model

The Medallion architecture (also called the multi-hop architecture) is the dominant data organization pattern for lakehouse scenarios. Popularized by Databricks, it has become an industry standard.

Traditional data warehouses mix raw and processed data together, making it hard to trace issues or rerun pipelines. The core idea of Medallion is **layered isolation**: raw data is always preserved in the Bronze layer, each layer does exactly one thing, and if something goes wrong you can rerun from the previous layer without affecting anything else.

This pattern is especially well-suited for multi-source integration scenarios — data quality varies across systems, Bronze captures everything as-is, Silver handles cleansing and standardization, and Gold focuses on business-oriented modeling. Responsibilities are clear and layers don't interfere with each other.

### Layer Responsibilities

| Layer | Alias | Responsibility | Data State |
|----|------|------|---------|
| Bronze | Raw layer | Ingest as-is, no transformations | Raw data, may contain dirty records, duplicates, inconsistent formats |
| Silver | Cleansed layer | Deduplication, cleansing, standardization, multi-source integration | Clean, trustworthy, business-semantic |
| Gold | Serving layer | Dimensional modeling for analytics and BI | Aggregated wide tables, star schema |

The benefit of physical isolation across layers: if any layer has a problem, you can rerun it from the layer above — no need to re-download raw data, and no impact on other layers.

### Star Schema

The Gold layer typically uses a **star schema**: one fact table at the center, surrounded by dimension tables.

```
              dim_customers
                    │
dim_products ── fact_sales
```

**Fact tables** store business events (orders, transactions). Each row is one event and contains measures (amounts, quantities) plus foreign keys pointing to dimension tables. **Dimension tables** store attributes of business entities (customer info, product info) and are joined to the fact table via foreign keys.

This project's Gold layer follows exactly this structure: `fact_sales` links to `dim_customers` and `dim_products` via `customer_key` and `product_key`.

### Why Surrogate Keys?

Dimension table primary keys come in two flavors: natural keys (from the source system, e.g., `customer_id = "C001"`) and surrogate keys (integers generated internally by the warehouse, e.g., `customer_key = 1`).

Reasons to use surrogate keys:

- **Performance**: integer JOINs are faster than string JOINs
- **Stability**: source system IDs can change due to business events (mergers, renumbering); surrogate keys are unaffected
- **Cross-source integration**: the same entity from multiple source systems can map to a single surrogate key

This project generates surrogate keys using `F.row_number().over(Window.order_by("customer_id"))` — simple and effective.

---

## Environment Initialization

Before running any notebook, create the schemas and Volume, then upload the CSV files. This only needs to be done once.

```python
# init_lakehouse.ipynb
from clickzetta.zettapark.session import Session
import os
from dotenv import load_dotenv

load_dotenv()
session = Session.builder.configs({
    "username":  os.environ["CLICKZETTA_USERNAME"],
    "password":  os.environ["CLICKZETTA_PASSWORD"],
    "service":   os.environ["CLICKZETTA_SERVICE"],
    "instance":  os.environ["CLICKZETTA_INSTANCE"],
    "workspace": os.environ["CLICKZETTA_WORKSPACE"],
    "schema":    os.environ["CLICKZETTA_SCHEMA"],
    "vcluster":  os.environ["CLICKZETTA_VCLUSTER"],
}).create()

# Create the three-layer schemas
for schema in ["bronze", "silver", "gold"]:
    session.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}").collect()

# Create Volume (to store raw CSVs)
vol_schema = os.environ["CLICKZETTA_SCHEMA"]
vol_name   = os.environ.get("CLICKZETTA_VOLUME", "medallion_vol")
session.sql(f"CREATE VOLUME IF NOT EXISTS {vol_schema}.{vol_name}").collect()

# Upload local CSVs to Volume
import pathlib
datasets_dir = pathlib.Path("../datasets")
vol_base = f"vol://{vol_schema}.{vol_name}"

for csv_file in datasets_dir.rglob("*.csv"):
    relative = csv_file.relative_to(datasets_dir)
    dest = f"{vol_base}/{relative}"
    session.file.put(str(csv_file), dest, auto_compress=False, overwrite=True)
    print(f"  {relative} → {dest}")
```

`.env` configuration:

```
CLICKZETTA_USERNAME=your_username
CLICKZETTA_PASSWORD=your_password
CLICKZETTA_SERVICE=cn-shanghai-alicloud.api.singdata.com
CLICKZETTA_INSTANCE=your_instance_id
CLICKZETTA_WORKSPACE=your_workspace
CLICKZETTA_SCHEMA=public
CLICKZETTA_VCLUSTER=default_ap
CLICKZETTA_VOLUME=medallion_vol
```

---

## Bronze Layer: Raw Data Ingestion

The Bronze layer principle is **no business transformations** — just read the CSVs and write them as tables. The benefit: if something goes wrong downstream, you can rerun from Bronze without re-downloading the raw data.

```python
# 03_lakehouse/01_bronze/bronze.ipynb

VOL_SCHEMA = os.environ.get("CLICKZETTA_SCHEMA", "public")
VOLUME     = os.environ.get("CLICKZETTA_VOLUME", "medallion_vol")

INGESTION_CONFIG = [
    {"path": f"vol://{VOL_SCHEMA}.{VOLUME}/source_crm/cust_info.csv",     "table": "bronze.crm_cust_info"},
    {"path": f"vol://{VOL_SCHEMA}.{VOLUME}/source_crm/prd_info.csv",      "table": "bronze.crm_prd_info"},
    {"path": f"vol://{VOL_SCHEMA}.{VOLUME}/source_crm/sales_details.csv", "table": "bronze.crm_sales_details"},
    {"path": f"vol://{VOL_SCHEMA}.{VOLUME}/source_erp/CUST_AZ12.csv",     "table": "bronze.erp_cust_az12"},
    {"path": f"vol://{VOL_SCHEMA}.{VOLUME}/source_erp/LOC_A101.csv",      "table": "bronze.erp_loc_a101"},
    {"path": f"vol://{VOL_SCHEMA}.{VOLUME}/source_erp/PX_CAT_G1V2.csv",  "table": "bronze.erp_px_cat_g1v2"},
]

for item in INGESTION_CONFIG:
    print(f"Ingesting → {item['table']}")
    df = session.read.option("header", "true").csv(item["path"])
    df.write.save_as_table(item["table"], mode="overwrite")
    print("  OK")
```

6 tables, 6 config entries, handled uniformly. `mode="overwrite"` ensures idempotency — rerunning won't produce duplicate data.

---

## Silver Layer: Cleansing and Standardization

The Silver layer does three things: **remove nulls, standardize enum values, rename columns**. Each source table has its own notebook with independent, self-contained logic.

### Customer Info Cleansing (crm_cust_info → silver.crm_customers)

```python
# 03_lakehouse/02_silver/crm/silver_crm_cust_info.ipynb

from clickzetta.zettapark.types import StringType
from clickzetta.zettapark import functions as F

df = session.table("bronze.crm_cust_info")

# 1. Trim leading/trailing whitespace from all string columns
for field in df.schema.fields:
    if isinstance(field.datatype, StringType):
        df = df.with_column(field.name, F.trim(F.col(field.name)))

# 2. Standardize enum values
df = (
    df
    .with_column(
        "cst_marital_status",
        F.when(F.upper(F.col("cst_marital_status")) == "S", "Single")
         .when(F.upper(F.col("cst_marital_status")) == "M", "Married")
         .otherwise("n/a")
    )
    .with_column(
        "cst_gndr",
        F.when(F.upper(F.col("cst_gndr")) == "F", "Female")
         .when(F.upper(F.col("cst_gndr")) == "M", "Male")
         .otherwise("n/a")
    )
)

# 3. Filter out rows with null primary keys
df = df.filter(F.col("cst_id").is_not_null())

# 4. Rename columns (apply business semantics)
RENAME_MAP = {
    "cst_id":             "customer_id",
    "cst_key":            "customer_number",
    "cst_firstname":      "first_name",
    "cst_lastname":       "last_name",
    "cst_marital_status": "marital_status",
    "cst_gndr":           "gender",
    "cst_create_date":    "created_date",
}
for old, new in RENAME_MAP.items():
    df = df.with_column_renamed(old, new)

df.write.save_as_table("silver.crm_customers", mode="overwrite")
```

Note that `with_column_renamed` follows ZettaPark's snake_case naming convention, corresponding to PySpark's `withColumnRenamed` — the behavior is identical.

### Deduplication: Keep the Latest Record by Priority

When source data contains duplicate IDs, a simple `drop_duplicates` isn't enough — you need to decide which record to keep based on business rules. Here, `row_number()` ranks records by creation date descending, keeping only the most recent:

```python
# 03_lakehouse/02_silver/crm/silver_crm_prd_info.ipynb

from clickzetta.zettapark.window import Window

# Partition by prd_id, keep the row with the latest prd_start_dt
window = Window.partition_by("prd_id").order_by(F.col("prd_start_dt").desc())
df = (
    df
    .with_column("_row_num", F.row_number().over(window))
    .filter(F.col("_row_num") == 1)
    .select([c for c in df.columns])  # drop the helper column
)
```

This pattern is common in multi-source integration: the same product may exist in both CRM and ERP, with one system treated as authoritative and the other as supplementary.

### Silver Layer Orchestration

6 notebooks run in dependency order:

```python
# 03_lakehouse/02_silver/silver_orchestration.ipynb

import subprocess, sys

NOTEBOOKS = [
    "crm/silver_crm_cust_info.ipynb",
    "crm/silver_crm_prd_info.ipynb",
    "crm/silver_crm_sales_details.ipynb",
    "erp/silver_erp_cust_az12.ipynb",
    "erp/silver_erp_loc_a101.ipynb",
    "erp/silver_erp_px_cat_g1v2.ipynb",
]

for nb in NOTEBOOKS:
    print(f"Running {nb}...")
    result = subprocess.run(
        ["jupyter", "nbconvert", "--to", "notebook", "--execute", nb,
         "--output", nb, "--ExecutePreprocessor.timeout=300"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"FAILED: {nb}")
        print(result.stderr)
        sys.exit(1)
    print(f"  OK")
```

---

## Gold Layer: Dimensional Modeling

The Gold layer's core work is **multi-source integration** and **surrogate key generation**.

### Customer Dimension Table (dim_customers)

CRM customer info is the primary source; ERP customer info and location data serve as supplements, integrated via LEFT JOIN:

```python
# 03_lakehouse/03_gold/gold_dim_customers.ipynb

from clickzetta.zettapark.window import Window

ci = session.table("silver.crm_customers")    # CRM customers (primary)
ca = session.table("silver.erp_customers")    # ERP customers (supplement: gender, birthdate)
la = session.table("silver.erp_customer_location")  # ERP location (supplement: country)

joined = (
    ci.join(ca, ci["customer_number"] == ca["customer_number"], "left")
      .join(la, ci["customer_number"] == la["customer_number"], "left")
)

# After a multi-table JOIN, always specify the source DataFrame for each column
# to avoid ambiguity with identically named columns
df = joined.select(
    ci["customer_id"].alias("customer_id"),
    ci["customer_number"].alias("customer_number"),
    ci["first_name"].alias("first_name"),
    ci["last_name"].alias("last_name"),
    la["country"].alias("country"),
    ci["marital_status"].alias("marital_status"),
    # gender: prefer CRM; fall back to ERP when CRM is n/a
    F.when(ci["gender"] != "n/a", ci["gender"])
     .otherwise(F.coalesce(ca["gender"], F.lit("n/a"))).alias("gender"),
    ca["birth_date"].alias("birthdate"),
    ci["created_date"].alias("create_date"),
)

# Generate surrogate key (globally unique integer primary key)
w = Window.order_by(F.col("customer_id"))
df = df.with_column("customer_key", F.row_number().over(w))

# Reorder columns, surrogate key first
df = df.select(
    "customer_key", "customer_id", "customer_number",
    "first_name", "last_name", "country",
    "marital_status", "gender", "birthdate", "create_date",
)

df.write.save_as_table("gold.dim_customers", mode="overwrite")
```

**Why surrogate keys?**

`customer_id` is the natural key from the source system. It may be inconsistent across systems and can change over time due to business events. `customer_key` is the warehouse's internal integer primary key — stable, unique, and used as the foreign key in fact tables, independent of source system ID formats.

### Sales Fact Table (fact_sales)

The fact table joins to dimension tables via surrogate keys and stores no redundant business attributes:

```python
# 03_lakehouse/03_gold/gold_fact_sales.ipynb

sd = session.table("silver.crm_sales")
dp = session.table("gold.dim_products")
dc = session.table("gold.dim_customers")

# Join to dimension tables using surrogate keys
joined = (
    sd.join(dp, sd["sls_prd_key"] == dp["product_number"], "left")
      .join(dc, sd["sls_cust_id"] == dc["customer_id"], "left")
)

df = joined.select(
    sd["sls_ord_num"].alias("order_number"),
    dp["product_key"].alias("product_key"),       # surrogate key
    dc["customer_key"].alias("customer_key"),      # surrogate key
    sd["sls_order_dt"].alias("order_date"),
    sd["sls_ship_dt"].alias("ship_date"),
    sd["sls_due_dt"].alias("due_date"),
    sd["sls_sales"].alias("sales_amount"),
    sd["sls_quantity"].alias("quantity"),
    sd["sls_price"].alias("unit_price"),
)

df.write.save_as_table("gold.fact_sales", mode="overwrite")
```

---

## Data Quality Validation

After the pipeline runs, `04_validate.ipynb` performs 22 automated checks. The validation logic uses ZettaPark queries directly, with no external framework required:

```python
# 04_validate.ipynb (excerpt)

def check(label, condition_sql, expect_zero=True):
    """Run a SQL query and check whether the result meets expectations."""
    result = session.sql(condition_sql).collect()[0][0]
    passed = (result == 0) if expect_zero else (result > 0)
    status = "✓" if passed else "✗ FAIL"
    print(f"  {status}  {label}: {result}")
    return passed

# Bronze → Silver row count consistency
check(
    "silver.crm_customers row count matches bronze.crm_cust_info (after null filter)",
    """
    SELECT ABS(
        (SELECT COUNT(*) FROM silver.crm_customers) -
        (SELECT COUNT(*) FROM bronze.crm_cust_info WHERE cst_id IS NOT NULL)
    )
    """,
    expect_zero=True
)

# No nulls in key columns
check(
    "dim_customers.customer_key has no nulls",
    "SELECT COUNT(*) FROM gold.dim_customers WHERE customer_key IS NULL",
    expect_zero=True
)

# Surrogate key uniqueness
check(
    "dim_customers.customer_key has no duplicates",
    """
    SELECT COUNT(*) FROM (
        SELECT customer_key, COUNT(*) AS cnt
        FROM gold.dim_customers
        GROUP BY customer_key
        HAVING cnt > 1
    )
    """,
    expect_zero=True
)

# Foreign key integrity
check(
    "All customer_key values in fact_sales resolve to dim_customers",
    """
    SELECT COUNT(*) FROM gold.fact_sales f
    LEFT JOIN gold.dim_customers d ON f.customer_key = d.customer_key
    WHERE d.customer_key IS NULL
    """,
    expect_zero=True
)
```

Actual results: **20/22 passed**. 2 warnings:

- `bronze.crm_cust_info` contains 5 groups of duplicate `customer_id` values (source data quality issue)
- `bronze.crm_sales_details` contains 3 rows with negative sales amounts (returns/reversals — normal business behavior)

Neither issue was introduced by the migration; both exist in the original Databricks project as well.

---

## Key Design Decisions

### Why `mode="overwrite"` instead of MERGE INTO?

This Medallion project has a small data volume (a few thousand rows). Full overwrite is far simpler than incremental MERGE and easier to keep idempotent. MERGE INTO complexity is only worth it when data volumes are large (millions of rows or more) or when you need to preserve historical versions.

Comparison:

| Scenario | Recommended approach | Reason |
|------|---------|------|
| Small data, full refresh | `save_as_table(mode="overwrite")` | Simple, idempotent, no merge key to maintain |
| Large data, incremental updates | MERGE INTO + `merge_delta_data()` | Avoids full table scans, preserves history |
| Historical snapshots needed | Time Travel + INSERT | Natively supported by Lakehouse |

### Why surrogate keys in the Gold layer?

Using natural keys (e.g., `customer_id`) as foreign keys in the fact table creates two problems:

1. Natural keys may be strings, which JOIN more slowly than integers
2. Source system IDs can change (mergers, renumbering), breaking historical data associations

The integer key generated by `row_number().over(Window.order_by("customer_id"))` is stable and unique — the standard approach in dimensional modeling.

### Why must you explicitly specify column sources after a multi-table JOIN?

```python
# This is problematic: joined.select("customer_id", "country", ...)
# because ci, ca, and la all have a customer_number column — ZettaPark doesn't know which to use

# Correct: specify the source DataFrame for every column
df = joined.select(
    ci["customer_id"].alias("customer_id"),
    la["country"].alias("country"),
    # ...
)
```

This isn't a ZettaPark limitation — PySpark requires the same treatment after multi-table JOINs. Explicitly specifying the source is good practice: it improves readability and prevents runtime errors from column name ambiguity.

---

## Full Execution Order

```bash
# 1. Install dependencies
pip install clickzetta_zettapark_python python-dotenv jupyter

# 2. Configure connection
cp .env.sample .env
# Edit .env and fill in your Singdata connection details

# 3. Run notebooks in order
jupyter nbconvert --to notebook --execute 03_lakehouse/init_lakehouse.ipynb --output 03_lakehouse/init_lakehouse.ipynb
jupyter nbconvert --to notebook --execute 03_lakehouse/01_bronze/bronze.ipynb --output 03_lakehouse/01_bronze/bronze.ipynb
jupyter nbconvert --to notebook --execute 03_lakehouse/02_silver/silver_orchestration.ipynb --output 03_lakehouse/02_silver/silver_orchestration.ipynb
jupyter nbconvert --to notebook --execute 03_lakehouse/03_gold/gold_orchestration.ipynb --output 03_lakehouse/03_gold/gold_orchestration.ipynb

# 4. Validate results
jupyter nbconvert --to notebook --execute 04_validate.ipynb --output 04_validate.ipynb
```

---

## Side-by-Side Comparison with PySpark

This project preserves the original Databricks Notebooks in the `01_spark/` directory for file-by-file comparison. There are only 4 core differences:

| Difference | PySpark | ZettaPark |
|--------|---------|-----------|
| Method naming | `withColumn` / `withColumnRenamed` | `with_column` / `with_column_renamed` |
| Session creation | `spark` (globally injected) | `Session.builder.configs({...}).create()` |
| File paths | Local path / DBFS | `vol://schema.vol/path` |
| Write method | `df.write.mode("overwrite").saveAsTable(t)` | `df.write.save_as_table(t, mode="overwrite")` |

Business logic (`F.when().otherwise()`, `Window.partition_by().order_by()`, `df.join()`, `df.filter()`) is **fully compatible — not a single line needs to change**.

---

## Migration Conclusions

ZettaPark is highly compatible with PySpark's DataFrame API. This project validates the following conclusions:

**Fully compatible (no changes needed):**

- DataFrame chaining: `filter`, `select`, `join`, `group_by`, `agg`, `drop_duplicates`
- Function library: `F.when().otherwise()`, `F.trim()`, `F.upper()`, `F.coalesce()`, `F.row_number()`, `F.isnotnull()`
- Window functions: `Window.partition_by().order_by()`, windowed aggregation behavior is identical
- SQL DML: MERGE INTO, INSERT, UPDATE, DELETE

**4 changes required (same as the F1 project):**

| Difference | PySpark | ZettaPark |
|--------|---------|-----------|
| Method naming | `withColumn` / `withColumnRenamed` | `with_column` / `with_column_renamed` |
| Session creation | `spark` (globally injected) | `Session.builder.configs({...}).create()` |
| File paths | Local path / DBFS | `vol://schema.vol/path` |
| Write method | `df.write.mode("overwrite").saveAsTable(t)` | `df.write.save_as_table(t, mode="overwrite")` |

With 20/22 validations passing (the 2 warnings are source data quality issues, not migration artifacts), this project demonstrates that ZettaPark can fully handle PySpark-based Medallion data engineering workloads.

---

## References

- GitHub project: [spark2lakehouse-medallion](https://github.com/clickzetta/spark2lakehouse-medallion)
- Original project: [DataWithBaraa/databricks_bootcamp_2026](https://github.com/DataWithBaraa/databricks_bootcamp_2026)
- PySpark migration in practice (more details on pitfalls): [PySpark → ZettaPark Migration in Practice: F1 Racing Data Engineering Project](pyspark-to-zettapark-migration-f1.md)
- ZettaPark API reference: [ZettaPark DataFrame API Guide](zettapark-dataframe-guide.md)
- Spark SQL syntax migration: [Spark SQL Syntax Migration Guide](migration-spark-sql.md)
- Volume usage guide: [Volume Usage Guide](zettapark-volume-guide.md)
- Data type compatibility: [Data Type Compatibility Reference](migration-sql-compatibility.md)
- Custom functions: [SQL Function](create-sql-function.md) · [External Function](create_external_function.md)
- Spark Connector: [Using Spark Connector](spark-connector-use.md)
