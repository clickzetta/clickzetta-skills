# Snowpark → ZettaPark Migration in Practice: Frostbyte Data Engineering Pipeline

If you have built a data engineering pipeline on Snowflake using Snowpark Python, migrating to Singdata Lakehouse involves changes in 3 main areas: data loading (Stage → Volume), stored procedures (replaced by Python scripts), and task scheduling (TASK → cz-cli task). The DataFrame API itself is highly compatible — business logic does not need to be rewritten.

This guide demonstrates the complete process using a real migration project: migrating the official Snowflake Frostbyte Data Engineering Lab (`sfguide-data-engineering-with-snowpark-python`, 150 stars) to Singdata Lakehouse, using the original Frostbyte S3 public dataset as the data source. All code has been validated with actual runs.

Full code on GitHub: [snowflake2lakehouse-data-engineering](https://github.com/clickzetta/snowflake2lakehouse-data-engineering)

---

## Original Project

[snowflake2lakehouse-data-engineering](https://github.com/clickzetta/snowflake2lakehouse-data-engineering) is adapted from [Snowflake-Labs/sfguide-data-engineering-with-snowpark-python](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python) and demonstrates how to build a complete data engineering pipeline on Snowflake using Snowpark Python: loading Frostbyte food truck order data from S3, cleansing it, flattening it with JOINs, merging it incrementally, and ultimately producing daily city-level sales metrics.

The migrated code lives in the `03_lakehouse/` directory. The original Snowflake code is preserved in `01_snowflake/` for comparison.

## Technology Stack Comparison

| | Original (Snowflake) | Migrated (Lakehouse) |
|---|---|---|
| Data loading | S3 External Stage + `COPY INTO` | Volume + `session.file.put()` + `save_as_table()` |
| DataFrame API | `snowflake.snowpark` | `clickzetta.zettapark` (import path; API is identical) |
| Stored procedures | Python Stored Procedure (`CREATE PROCEDURE`) | Plain Python scripts (logic unchanged) |
| Python UDF | Snowpark Python UDF (depends on scipy) | SQL UDF (`RETURN expr` syntax) |
| Stream on View | `CREATE STREAM ON VIEW` | Not supported; materialize the View as a Table first, then create a Stream on the Table |
| Task scheduling | `CREATE TASK ... WHEN SYSTEM$STREAM_HAS_DATA(...)` | `cz-cli task create/deploy/execute` |
| Compute resource | `WAREHOUSE = HOL_WH` | `VCLUSTER default` |

The core DataFrame operations (`with_column`, `join`, `group_by`, `agg`, `merge`, Window functions) are fully identical between ZettaPark and Snowpark — not a single line of business logic needs to change.

---

![](.topwrite/assets/anim-09-snowpark-migration.svg)

---

## Architecture Overview

```
S3 (sfquickstarts bucket)                    Volume (frostbyte_raw_pos.frostbyte_vol)
  pos/order_header/year=2021/                  pos/order_header/
  pos/order_detail/year=2021/                  pos/order_detail/
  pos/menu/ · pos/truck/ · ...                 pos/menu/ · pos/truck/ · ...
  customer/customer_loyalty/                   customer/customer_loyalty/
         │                                              │
         │  COPY INTO (Snowflake)                       │  session.file.put() + save_as_table()
         ▼                                              ▼
  RAW_POS / RAW_CUSTOMER schemas              frostbyte_raw_pos / frostbyte_raw_customer
         │                                              │
         │  Snowpark DataFrame join                     │  ZettaPark DataFrame join (identical)
         ▼                                              ▼
  POS_FLATTENED_V (View)                      pos_flattened_v (View, SQL CREATE VIEW)
  + Stream ON VIEW                            + pos_flattened_v_table (materialized)
                                              + Stream ON TABLE (WITH PROPERTIES)
         │                                              │
         │  Python Stored Procedure                     │  Python Script (06_orders_update.py)
         ▼                                              ▼
  HARMONIZED.ORDERS                           frostbyte_harmonized.orders
         │                                              │
         │  Python Stored Procedure                     │  Python Script (07_daily_city_metrics.py)
         ▼                                              ▼
  ANALYTICS.DAILY_CITY_METRICS                frostbyte_analytics.daily_city_metrics
         │                                              │
         │  CREATE TASK ... AFTER ...                   │  cz-cli task create/deploy/execute
         ▼                                              ▼
  Task Orchestration (Snowsight)              Studio Task (cz-cli)
```

---

## Quick Start

```bash
git clone https://github.com/clickzetta/snowflake2lakehouse-data-engineering.git
cd snowflake2lakehouse-data-engineering/03_lakehouse

cp .env.example .env
# Fill in the connection details in .env

pip install clickzetta_zettapark_python python-dotenv

# Download Frostbyte data (public S3, no AWS account required)
aws s3 sync s3://sfquickstarts/data-engineering-with-snowpark-python/ ./datasets/ \
  --no-sign-request \
  --exclude "pos/order_header/*" --exclude "pos/order_detail/*"
# Take one year=2021 file each for order_header and order_detail (about 90 MB)
aws s3 cp s3://sfquickstarts/data-engineering-with-snowpark-python/pos/order_header/year=2021/data_01a91b48-0605-6a9c-0000-711101079122_005_4_0.snappy.parquet \
  ./datasets/pos/order_header/ --no-sign-request
aws s3 cp s3://sfquickstarts/data-engineering-with-snowpark-python/pos/order_detail/year=2021/data_01a91b50-0605-721e-0000-71110107a166_008_0_0.snappy.parquet \
  ./datasets/pos/order_detail/ --no-sign-request

# Run the full pipeline end-to-end and validate (24 data checks)
python e2e.py --teardown

# Or run step by step:
python setup.py                          # Create schemas/volume, upload data, register cz-cli profile
python steps/02_load_raw.py              # Load raw data into Lakehouse
python steps/04_create_pos_view.py       # Create View + Table Stream
cz-cli sql -f steps/05_udf.sql --profile frostbyte --sync --write  # Create SQL UDF
python steps/06_orders_update.py         # Merge order data
python steps/07_daily_city_metrics.py    # Compute daily city metrics
export $(grep -v '^#' .env | xargs) && bash steps/08_orchestrate_tasks.sh  # Deploy scheduled tasks

# Clean up all objects (Studio task + SQL objects + Volume)
bash steps/11_teardown.sh
```

---

## Migration Steps

### Step 1: Data Loading (Stage → Volume)

This is the first difference in the migration and the most straightforward.

Snowflake uses an External Stage pointing to S3 and loads data with `COPY INTO`:

```sql
CREATE STAGE FROSTBYTE_RAW_STAGE
    URL = 's3://sfquickstarts/data-engineering-with-snowpark-python/';

COPY INTO RAW_POS.ORDER_HEADER
FROM @FROSTBYTE_RAW_STAGE/pos/order_header/
FILE_FORMAT = (FORMAT_NAME = PARQUET_FORMAT)
MATCH_BY_COLUMN_NAME = CASE_SENSITIVE;
```

Lakehouse uses a Volume as managed storage. Files are uploaded via ZettaPark and then loaded with `save_as_table`:

```python
# Upload to Volume (replaces S3 Stage)
session.file.put(str(local_file), "vol://frostbyte_raw_pos.frostbyte_vol/pos/order_header/",
                 auto_compress=False, overwrite=True)

# Read from Volume and write to table (replaces COPY INTO)
df = session.read.option("compression", "snappy").parquet(
    "vol://frostbyte_raw_pos.frostbyte_vol/pos/order_header/"
)
df.write.save_as_table("frostbyte_raw_pos.order_header", mode="overwrite")
```

> ⚠️ **Note**: A Volume must be created under an existing schema. `setup.py` first creates the `frostbyte_raw_pos` schema via `cz-cli`, then creates the Volume, so the Volume can be placed under `frostbyte_raw_pos` rather than `public`. The ZettaPark session connects using the `public` schema (which always exists), but `session.file.put()` can write to a Volume under any existing schema.

### Step 2: DataFrame API (Almost No Changes Needed)

The Snowpark and ZettaPark DataFrame APIs are highly compatible. Only the import paths need to change:

```python
# Snowflake
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.window import Window

# Lakehouse (only change the imports; everything else stays the same)
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F
from clickzetta.zettapark.window import Window
```

The following operations are written identically on both platforms:

```python
# JOIN to flatten multiple tables
final = order_detail.join(order_header, "order_id") \
                    .join(menu, "menu_item_id") \
                    .join(truck, "truck_id")

# Incremental merge (MERGE INTO)
target.merge(
    source,
    target["order_detail_id"] == source["order_detail_id"],
    [F.when_matched().update(updates),
     F.when_not_matched().insert(updates)]
)

# Window functions
window = Window.partition_by("city").order_by(F.col("date").desc())
df.with_column("rank", F.row_number().over(window))
```

### Step 3: Handling Stream on View

Snowflake supports creating a Stream directly on a View:

```sql
CREATE STREAM HARMONIZED.POS_FLATTENED_V_STREAM
ON VIEW HARMONIZED.POS_FLATTENED_V;
```

Lakehouse Table Streams only support `ON TABLE` — `ON VIEW` is not supported. The solution is to first materialize the View as a Table, then create a Stream on the Table:

```python
# 1. Create the View (using SQL to ensure persistence)
session.sql("""
    CREATE OR REPLACE VIEW frostbyte_harmonized.pos_flattened_v AS
    SELECT od.order_detail_id, oh.order_ts, m.truck_brand_name, ...
    FROM frostbyte_raw_pos.order_detail od
    JOIN frostbyte_raw_pos.order_header oh ON od.order_id = oh.order_id
    ...
""").collect()

# 2. Materialize as a Table (Stream can only be created on a Table)
session.sql("""
    CREATE TABLE IF NOT EXISTS frostbyte_harmonized.pos_flattened_v_table
    AS SELECT * FROM frostbyte_harmonized.pos_flattened_v
""").collect()

# 3. Create a Stream on the Table (TABLE_STREAM_MODE must be specified)
session.sql("""
    CREATE TABLE STREAM IF NOT EXISTS frostbyte_harmonized.pos_flattened_v_stream
    ON TABLE frostbyte_harmonized.pos_flattened_v_table
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')
""").collect()
```

> ⚠️ **Note**: Lakehouse `CREATE TABLE STREAM` requires `WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')`. Omitting it will cause a syntax error.

When consuming from a Stream, Lakehouse Table Streams append metadata columns (`__change_type`, `__commit_version`, etc.) alongside the data columns. When inserting, you must explicitly specify column names to exclude these metadata columns:

```python
# When consuming data from a stream, use SQL INSERT with explicit column names
session.sql("""
    INSERT INTO frostbyte_harmonized.orders
    SELECT
        order_detail_id, order_id, truck_id, ...,
        CURRENT_TIMESTAMP() AS meta_updated_at
    FROM frostbyte_harmonized.pos_flattened_v_stream
""").collect()
```

### Step 4: Stored Procedures → Python Scripts

Snowflake Python Stored Procedures encapsulate business logic inside the database and are triggered via `CALL`:

```sql
CREATE OR REPLACE PROCEDURE HARMONIZED.ORDERS_UPDATE_SP()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'main'
AS $$
def main(session):
    # business logic
    ...
$$;

CALL HARMONIZED.ORDERS_UPDATE_SP();
```

Lakehouse does not support stored procedures, but the logic can be converted directly to a plain Python script:

```python
# 06_orders_update.py — identical logic to the stored procedure, just a different execution model
from clickzetta.zettapark.session import Session

def merge_order_updates(session):
    # The business logic from the original stored procedure, unchanged
    ...

if __name__ == "__main__":
    session = create_session()
    merge_order_updates(session)
```

### Step 5: Python UDF → SQL UDF

Snowflake Python UDFs can use third-party packages (such as scipy):

```python
# Snowflake Python UDF
from scipy.constants import convert_temperature

def main(temp_f: float) -> float:
    return convert_temperature(float(temp_f), 'F', 'C')
```

Lakehouse Python UDFs require configuring an External Function service (cloud function deployment). For simple mathematical calculations, a SQL UDF is much simpler:

```sql
-- Lakehouse SQL UDF
-- Note: use RETURN expr syntax (not AS $$ ... $$), and use DOUBLE type (to avoid DECIMAL precision overflow)
CREATE OR REPLACE FUNCTION frostbyte_analytics.fahrenheit_to_celsius_udf(temp_f DOUBLE)
RETURNS DOUBLE
RETURN (temp_f - 32.0) * 5.0 / 9.0;
```

### Step 6: Task Scheduling (TASK → cz-cli task)

Snowflake Tasks can monitor Stream data changes and trigger automatically:

```sql
CREATE OR REPLACE TASK ORDERS_UPDATE_TASK
WAREHOUSE = HOL_WH
WHEN SYSTEM$STREAM_HAS_DATA('POS_FLATTENED_V_STREAM')
AS CALL HARMONIZED.ORDERS_UPDATE_SP();

ALTER TASK DAILY_CITY_METRICS_UPDATE_TASK RESUME;
EXECUTE TASK ORDERS_UPDATE_TASK;
```

Lakehouse uses `cz-cli task` to create scheduled tasks, with the script content embedded directly in the task:

```bash
# Create the task
cz-cli task create orders_update_task --type PYTHON --profile frostbyte

# Save the script content (connection info is embedded; Studio tasks run in an isolated environment)
cz-cli task save-content orders_update_task \
  --content "$(cat orders_script.py)" --profile frostbyte

# Set a cron schedule (replaces SYSTEM$STREAM_HAS_DATA trigger)
cz-cli task save-cron orders_update_task \
  --cron "*/5 * * * *" --profile frostbyte

# Deploy and execute once immediately
cz-cli task deploy orders_update_task -y --profile frostbyte
cz-cli task execute orders_update_task --profile frostbyte
```

> ⚠️ **Note**: Studio tasks run in an isolated environment and cannot read local `.env` files. Connection information must be embedded in the script, or expanded in the shell via `export $(grep -v '^#' .env | xargs)` before being passed in via a heredoc.

---

## Validation Results

All code was validated end-to-end with `python e2e.py`. All 24/24 data checks passed:

| Layer | Table | Row count | Check |
|-------|-------|-----------|-------|
| Raw | `order_header` | 7,336,341 | Row count matches |
| Raw | `order_detail` | 6,230,167 | Row count matches |
| Raw | `customer_loyalty` | 222,540 | Row count matches |
| Raw | `menu / truck / location / ...` | 100 / 450 / 13,093 / ... | Row count matches |
| Harmonized | `pos_flattened_v` | 378,941 | Row count, 15 brands, 58 menu items |
| Harmonized | `orders` | 378,941 | Row count, no null primary keys, top brand Freezing Point |
| Harmonized | `orders` | — | Total revenue $5,547,817.75, date range 2021-01-01 ~ 2022-01-01 |
| Analytics | `daily_city_metrics` | 247 | Row count, top city New York City |
| UDF | `fahrenheit_to_celsius_udf` | — | 212°F = 100°C ✓ |
| UDF | `inch_to_millimeter_udf` | — | 1 inch = 25.4mm ✓ |

---

## Migration Conclusions

ZettaPark and Snowpark's DataFrame APIs are highly compatible. This project validates the following conclusions:

**Fully compatible (no changes needed):**

- DataFrame chaining: `with_column`, `join`, `group_by`, `agg`, `filter`, `select`
- Function library: `F.when().otherwise()`, `F.current_timestamp()`, `F.row_number()`, `F.sum()`, `F.coalesce()`
- Window functions: `Window.partition_by().order_by()`, behavior is fully identical
- `target.merge()` MERGE INTO semantics
- SQL UDF syntax (`RETURN expr`)
- Table Stream (`ON TABLE`)

**4 differences that require handling:**

| Difference | Snowflake | Lakehouse |
|------------|-----------|-----------|
| Data loading | S3 Stage + `COPY INTO` | Volume + `session.file.put()` + `save_as_table()` |
| Stream on View | `CREATE STREAM ON VIEW` | Not supported; materialize View as Table, then create Stream |
| Python UDF | Snowpark Python UDF (third-party packages) | SQL UDF (`RETURN expr`, `DOUBLE` type) |
| Stored procedure + Task | `CREATE PROCEDURE` + `CREATE TASK` | Python script + `cz-cli task` |

---

## References

- GitHub project: [snowflake2lakehouse-data-engineering](https://github.com/clickzetta/snowflake2lakehouse-data-engineering)
- Original project: [Snowflake-Labs/sfguide-data-engineering-with-snowpark-python](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python)
- [Volume Usage Guide](volume-guide.md)
- [Table Stream](table_stream.md)
- [CREATE SQL FUNCTION](create-sql-function.md)
- [ZettaPark DataFrame API Guide](zettapark-dataframe-guide.md)
- [Snowflake Dynamic Tables Migration Guide](snowflake-dynamic-tables-to-lakehouse.md)
