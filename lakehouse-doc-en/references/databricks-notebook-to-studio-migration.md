# Databricks Notebook → Lakehouse Migration Guide: Retail Data Medallion Pipeline

If your data engineering pipeline runs on Databricks Notebooks, the migration effort to Singdata Lakehouse Studio is lower than you might expect. Databricks' PySpark DataFrame API — `select`, `filter`, `join`, `withColumn`, `when`, Window functions — has identical syntax in ZettaPark. Changes are limited to just 5 mechanical substitutions: import paths, session acquisition method, table path prefix, one API casing difference, and replacing `dbutils.notebook.run()` with Studio task dependencies.

This article validates this with a real project: a Databricks-based retail data Medallion pipeline (Bronze → Silver → Gold three-layer architecture, 14 Notebooks, 81 code cells) fully migrated to Singdata Lakehouse, offering three migration options, all 20 automated validations passing.

Full code on GitHub: [databricks2lakehouse-bootcamp](https://github.com/clickzetta/databricks2lakehouse-bootcamp)

---

## Source Project

[databricks2lakehouse-bootcamp](https://github.com/clickzetta/databricks2lakehouse-bootcamp) is forked from [DataWithBaraa/databricks_bootcamp_2026](https://github.com/DataWithBaraa/databricks_bootcamp_2026) (⭐335). The original tech stack is Databricks + PySpark + Delta Lake + Unity Catalog. The project implements a complete retail data warehouse from dual-source CRM/ERP ingestion to a star schema, covering 18,484 customers, 397 products, and 60,398 sales records, with complete data cleansing, type conversion, code mapping, and dimensional modeling.

Migrated code is in the `03_lakehouse/` directory, comparable file-by-file with `01_source/`.

## Conclusion First

You don't need to rewrite any business logic, or retrain your team. All 5 changes are mechanical substitutions.

| Change | Effort | Notes |
|--------|--------|------|
| Import path replacement | Very low | `pyspark.sql` → `clickzetta.zettapark`, global search-replace |
| Session acquisition method | Very low | `spark` (global injection) → Studio tasks use `clickzetta_dbutils`, local use `Session.builder.configs({})` |
| Table path prefix | Very low | `workspace.bronze.X` → `bronze.X`, remove catalog prefix |
| StructField casing | Very low | `field.dataType` → `field.datatype` (ZettaPark API difference) |
| Orchestration method | Low | `dbutils.notebook.run(nb)` → Studio task dependencies (DAG) |

`select`, `filter`, `join`, `withColumn`, `when`, `coalesce`, `trim`, `regexp_replace`, `to_date`, `cast`, `isNotNull`, Window functions, `ROW_NUMBER()` — these core data engineering operations have identical syntax and require no changes.

---

## Tech Stack Comparison

| | Databricks Notebook | Lakehouse Studio Task |
|---|---|---|
| Compute engine | Apache Spark (Databricks) | Singdata Lakehouse |
| DataFrame API | PySpark (`pyspark.sql`) | ZettaPark (`clickzetta.zettapark`) |
| Session acquisition | `spark` (Databricks global injection) | `clickzetta_dbutils.get_active_lakehouse_engine()` |
| Table naming | `workspace.bronze.crm_cust_info` (3-level) | `bronze.crm_cust_info` (2-level) |
| File path | `/Volumes/workspace/bronze/raw_sources/...` | `vol://bronze.raw_sources/...` |
| StructField | `field.dataType` | `field.datatype` |
| SQL execution | `spark.sql(q)` executes immediately | `session.sql(q).collect()` triggers execution |
| Notebook chaining | `dbutils.notebook.run(nb, timeout_seconds=0)` | Studio task dependencies (`--deps` parameter) |
| Scheduling orchestration | Databricks Jobs | Studio task DAG |

---

![](.topwrite/assets/anim-28-databricks-notebook-migration.svg)

---

## Project Background

Data comes from a bicycle retailer's dual-source CRM + ERP system, including 6 CSV files:

| Data Source | Table Name | Row Count | Notes |
|--------|------|------|------|
| CRM | `crm_cust_info` | 18,494 | Customer info (includes dirty data and inconsistent casing) |
| CRM | `crm_prd_info` | 397 | Product info (includes category ID encoded in product key) |
| CRM | `crm_sales_details` | 60,398 | Sales transactions (includes yyyyMMdd format dates) |
| ERP | `erp_cust_az12` | 18,484 | Customer master data (includes NAS prefix, future dates) |
| ERP | `erp_loc_a101` | 18,484 | Customer addresses (includes hyphens and country code abbreviations) |
| ERP | `erp_px_cat_g1v2` | 37 | Product categories (includes YES/NO maintenance flags) |

Medallion architecture in three layers:

- **Bronze**: Raw CSV → 6 Delta tables (no transformation)
- **Silver**: Cleansing + normalization → 6 wide tables (trim, type conversion, enum mapping, column renaming)
- **Gold**: Star schema → dim_customers + dim_products + fact_sales

The original project has 14 Databricks Notebooks (81 code cells), chained via `dbutils.notebook.run()`.

---

## Migration Steps

### Step 1: Replace Import Paths

Mechanical global replacement, no logic changes:

```python
# Databricks
import pyspark.sql.functions as F
from pyspark.sql.types import StringType, DateType
from pyspark.sql.functions import trim, col, length
from pyspark.sql.window import Window

# ZettaPark (package name only)
from clickzetta.zettapark import functions as F
from clickzetta.zettapark.types import StringType, DateType
from clickzetta.zettapark.functions import trim, col, length
from clickzetta.zettapark.window import Window
```

### Step 2: Replace Session Acquisition Method

Databricks injects `spark` into every Notebook without requiring explicit creation. Studio tasks obtain it via `clickzetta_dbutils`, also without needing to manage passwords or connection parameters:

```python
# Databricks: spark is globally available, use directly
df = spark.table("workspace.bronze.crm_cust_info")

# Studio task: platform-injected, get session via clickzetta_dbutils
from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from urllib.parse import urlparse, parse_qs

engine = get_active_lakehouse_engine(schema="quick_start")
url_str = str(engine.url)
parsed = urlparse(url_str.replace('clickzetta://', 'https://'))
params = parse_qs(parsed.query)
parts = parsed.hostname.split('.', 1)

session = Session.builder.configs({
    "service":     parts[1],
    "instance":    parts[0],
    "magic_token": params['magic_token'][0],
    "workspace":   parsed.path.lstrip('/'),
    "schema":      params.get('schema', ['quick_start'])[0],
    "vcluster":    params.get('virtualcluster', ['DEFAULT'])[0],
}).getOrCreate()

# After this, session usage is identical to spark
df = session.table("bronze.crm_cust_info")
```

> 💡 **Note**: For local development and debugging, explicitly pass credentials with `Session.builder.configs({"instance":..., "password":..., ...}).create()`, without relying on `clickzetta_dbutils`. DataFrame code is identical after either acquisition method.

### Step 3: Remove Catalog Prefix from Table Paths

Unity Catalog uses three-level naming (catalog.schema.table). Lakehouse only requires two levels within a single workspace:

```python
# Databricks (Unity Catalog three-level)
df = spark.table("workspace.bronze.crm_cust_info")
df.write.mode("overwrite").format("delta").saveAsTable("workspace.silver.crm_customers")

# ZettaPark (two-level, remove catalog prefix)
df = session.table("bronze.crm_cust_info")
df.write.mode("overwrite").saveAsTable("silver.crm_customers")  # .format("delta") not needed either
```

### Step 4: Fix StructField Casing

This is an API difference discovered in testing, affecting all code that iterates field types with `df.schema.fields`:

```python
# Databricks / PySpark
for field in df.schema.fields:
    if isinstance(field.dataType, StringType):  # uppercase T
        df = df.withColumn(field.name, trim(col(field.name)))

# ZettaPark (datatype all lowercase)
for field in df.schema.fields:
    if isinstance(field.datatype, StringType):  # lowercase t
        df = df.withColumn(field.name, trim(col(field.name)))
```

### Step 5: Replace dbutils.notebook.run() with Studio Task Dependencies

The original project chains 14 Notebooks via `dbutils.notebook.run()`, which maps directly to Studio task DAG:

```python
# Databricks: orchestration notebook
notebooks = [
    "./silver_crm_cust_info",
    "./silver_crm_prd_info",
    "./silver_crm_sales_details",
    "./silver_erp_cust_az12",
    "./silver_erp_loc_a101",
    "./silver_erp_px_cat_g1v2"
]
for nb in notebooks:
    dbutils.notebook.run(nb, timeout_seconds=0)
```

```bash
# Studio: set task dependencies with cz-cli, one-time configuration, platform handles scheduling
cz-cli task save-config bootcamp/silver_crm_cust_info \
    --deps bootcamp/bronze_ingestion --profile aws_singapore_prod

cz-cli task save-config bootcamp/gold_dim_customers \
    --deps bootcamp/silver_crm_cust_info,bootcamp/silver_erp_cust_az12,bootcamp/silver_erp_loc_a101 \
    --profile aws_singapore_prod
```

Execute DAG (equivalent to the original orchestration notebook's chained calls):

```bash
cz-cli task execute bootcamp/init_lakehouse --profile aws_singapore_prod
# → automatically triggers bronze → silver (parallel) → gold (in dependency order)
```

---

## Studio Task DAG After Migration

The original Databricks project used 2 orchestration notebooks chained in series. After migration, the Studio platform automatically manages dependencies and parallelism:

```
init_lakehouse (SQL task)
└── bronze_ingestion (Python task)
    ├── silver_crm_cust_info      ← parallel execution
    ├── silver_crm_prd_info       ← parallel execution
    ├── silver_crm_sales_details  ← parallel execution
    ├── silver_erp_cust_az12      ← parallel execution
    ├── silver_erp_loc_a101       ← parallel execution
    └── silver_erp_px_cat_g1v2    ← parallel execution
        ├── gold_dim_customers  ← depends on silver_crm_cust_info + erp_cust + erp_loc
        ├── gold_dim_products   ← depends on silver_crm_prd_info + erp_px_cat
        └── gold_fact_sales     ← depends on dim_customers + dim_products + silver_crm_sales
```

The original Databricks ran 6 silver notebooks sequentially; Studio runs 6 silver tasks in parallel — same logic, shorter overall runtime.

---

## Fully Compatible Parts

The following code has identical syntax on both sides, validated by testing — no changes needed:

```python
# String cleansing
for field in df.schema.fields:
    if isinstance(field.datatype, StringType):
        df = df.withColumn(field.name, trim(col(field.name)))

# Enum mapping (conditional replacement)
df = df.withColumn("cst_marital_status",
    F.when(F.upper(F.col("cst_marital_status")) == "S", "Single")
     .when(F.upper(F.col("cst_marital_status")) == "M", "Married")
     .otherwise("n/a"))

# Composite string parsing (extract category ID from product key)
df = df.withColumn("cat_id", F.regexp_replace(F.substring(col("prd_key"), 1, 5), "-", "_"))
df = df.withColumn("prd_key", F.substring(col("prd_key"), 7, F.length(col("prd_key"))))

# Date format conversion (yyyyMMdd integer → DATE)
df = df.withColumn("sls_order_dt",
    F.when(
        (col("sls_order_dt") == 0) | (length(col("sls_order_dt")) != 8), None
    ).otherwise(F.to_date(col("sls_order_dt").cast("string"), "yyyyMMdd")))

# Conditional price fix (derive from sales/quantity when quantity != 0)
df = df.withColumn("sls_price",
    F.when(
        (col("sls_price").isNull()) | (col("sls_price") <= 0),
        F.when(col("sls_quantity") != 0, col("sls_sales") / col("sls_quantity")).otherwise(None)
    ).otherwise(col("sls_price")))

# Prefix cleansing (remove invalid NAS prefix)
df = df.withColumn("cid",
    F.when(col("cid").startswith("NAS"), F.substring(col("cid"), 4, F.length(col("cid"))))
     .otherwise(col("cid")))

# Future date filtering (dirty data cleansing)
df = df.withColumn("bdate",
    F.when(col("bdate") > F.current_date(), None).otherwise(col("bdate")))

# Multi-table LEFT JOIN + ROW_NUMBER for dimension table
df = session.sql("""
SELECT
    ROW_NUMBER() OVER (ORDER BY ci.customer_id) AS customer_key,
    ci.customer_id, ci.customer_number, ci.first_name, ci.last_name,
    COALESCE(la.country, 'n/a') AS country, ci.marital_status,
    CASE WHEN ci.gender <> 'n/a' THEN ci.gender ELSE COALESCE(ca.gender, 'n/a') END AS gender,
    ca.birth_date, ci.created_date
FROM silver.crm_customers ci
LEFT JOIN silver.erp_customer_location la ON ci.customer_number = la.customer_number
LEFT JOIN silver.erp_customers ca ON ci.customer_number = ca.customer_number
""")
```

---

## E2E Validation Results

Tested on AWS Singapore instance (`aws_singapore_prod`), 20/20 all passed:

| Check | Expected | Result |
|--------|--------|------|
| bronze.crm_cust_info | 18,494 | ✅ |
| bronze.crm_prd_info | 397 | ✅ |
| bronze.crm_sales_details | 60,398 | ✅ |
| bronze.erp_cust_az12 | 18,484 | ✅ |
| bronze.erp_loc_a101 | 18,484 | ✅ |
| bronze.erp_px_cat_g1v2 | 37 | ✅ |
| silver.crm_customers | 18,490 | ✅ |
| silver.crm_products | 397 | ✅ |
| silver.crm_sales | 60,398 | ✅ |
| silver.erp_customers | 18,484 | ✅ |
| silver.erp_customer_location | 18,484 | ✅ |
| silver.erp_product_category | 37 | ✅ |
| gold.dim_customers | 18,490 | ✅ |
| gold.dim_products | 397 | ✅ |
| gold.fact_sales | 89,833 | ✅ |
| Total sales amount | 43,538,800 | ✅ |
| Rows with negative sales | 5 (raw data) | ✅ |
| Distinct customer count | 18,484 | ✅ |
| Distinct product SKUs | 295 | ✅ |
| Rows with null order date | 24 (raw data format issue) | ✅ |

> Bronze 18,494 → Silver 18,490: 4 records with NULL customer_id were filtered during Silver cleansing, consistent with original Databricks behavior.

---

## Three Migration Options Compared

This project provides three options suited to different team backgrounds and deployment needs:

| Option | File Location | Session Method | Change Volume | Use Case |
|------|----------|-------------|--------|----------|
| **A. ZettaPark Local** | `03_lakehouse/{bronze,silver,gold}/` | `Session.builder.configs({}).create()` | ~5% | Local development, CI/CD debugging |
| **B. Pure SQL** | `03_lakehouse/sql/` | Not needed | Full rewrite (logic unchanged) | SQL-first teams, Studio SQL tasks |
| **C. Studio Task** | `03_lakehouse/tasks/` | `clickzetta_dbutils` | ~5% | **Production deployment (recommended)** |

All three options produce identical results — row counts, metrics, and data are consistent. Option C is the recommended path for production, directly mapping to the Databricks Notebook + Jobs architecture.

## Notes

- **`field.datatype` casing**: ZettaPark's `StructField` property is `datatype` (all lowercase); PySpark uses `dataType` (camelCase). This is the only non-mechanical API difference. Search for all uses of `schema.fields` and update individually.
- **`clickzetta_dbutils` template for Studio tasks**: The `get_active_lakehouse_engine()` call returns the current task's connection info; parse the URL to build the Session. This template code is fixed and can be extracted to a shared module for reuse.
- **Volume path format**: Databricks `/Volumes/catalog/schema/volume/path` → ZettaPark `vol://schema.volume/path`, note the removal of the catalog level.
- **`.format("delta")` not needed**: ZettaPark's `saveAsTable()` writes in Lakehouse native format by default; no explicit format specification required.
- **Silver row count difference (18,494 → 18,490)**: The CRM source data contains 4 records with NULL customer_id, filtered during Silver cleansing. This is expected behavior.

## Related Documentation

### ZettaPark DataFrame API

- [ZettaPark Quick Start](zettapark-quick-start.md): Session creation, DataFrame basics
- [ZettaPark DataFrame API Guide](zettapark-dataframe-guide.md): Full reference for select, filter, join, withColumn, etc.
- [ZettaPark Common Functions Reference](zettapark-functions-guide.md): Usage of trim, when, regexp_replace, Window, etc.
- [ZettaPark Data Engineering in Practice](zettapark-etl-guide.md): Complete ETL pipeline examples

### Studio Tasks and Orchestration

- [Lakehouse Studio Introduction](lakehouse-studio-concept.md): Studio platform concepts and architecture
- [Task Development and Scheduling](task-develop.md): Creating, developing, and scheduling Studio tasks
- [Task Scheduling Dependencies](task_scheduling_dependency.md): `--deps` parameter for configuring task DAG
- [Python Task](python-task.md): Creating and running Python tasks in Studio
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md): Managing Studio tasks via cz-cli command line

### Other Migration Guides

- [PySpark → ZettaPark Migration Guide (Formula 1)](pyspark-to-zettapark-migration-f1.md): PySpark DataFrame API query-by-query migration
- [Snowpark → ZettaPark Migration Guide](snowflake-snowpark-to-zettapark-migration.md): Snowflake Python DataFrame migration
- [Spark Migration Guide](spark-migration-guide.md): Spark ecosystem migration overview and common issues
- [SQL Compatibility Reference](migration-sql-compatibility.md): Cross-platform SQL syntax differences
