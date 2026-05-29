# MaxCompute → Lakehouse Migration in Practice: E-Commerce Data Engineering Project

If your data engineering project runs on MaxCompute + DataWorks, migrating to Singdata Lakehouse involves two main areas of work: **SQL syntax adaptation** and **task orchestration replacement**. The differences between MaxCompute SQL and Lakehouse SQL are fewer than you might expect — most standard SQL (JOIN, window functions, CTE, aggregation) is identical. What needs changing is mainly 6 MaxCompute-specific syntax patterns, plus migrating DataWorks task nodes to Studio tasks.

This article validates that claim with a real project: a complete migration of an e-commerce data engineering project from MaxCompute + DataWorks to Singdata Lakehouse, covering ODS/DWD/ADS three layers, 8 source tables, and 5 ETL tasks — all passing full end-to-end validation.

> Full code: [clickzetta/maxcompute2lakehouse-ecommerce](https://github.com/clickzetta/maxcompute2lakehouse-ecommerce)

## Source Project

- **Source**: [rcdelacruz/dataworks-maxcompute-practice](https://github.com/rcdelacruz/dataworks-maxcompute-practice)
- **Dataset**: E-commerce scenario, 8 tables (customers / products / orders / order_items / web_sessions / page_views / user_events / suppliers)
- **Task orchestration**: DataWorks `daily_etl_workflow.json`, 5 nodes, triggered daily at 02:00
- **UDFs**: Python text analysis (sentiment analysis, keyword extraction) + Java string processing

## Technology Stack Comparison

| Dimension | MaxCompute + DataWorks | Singdata Lakehouse |
|---|---|---|
| Compute engine | MaxCompute (ODPS) | Lakehouse SQL Engine |
| Task orchestration | DataWorks Workflow JSON (descriptive config; the original project did not implement API automation — tasks must be created manually in the console) | Studio tasks + **cz-cli** (fully command-line; `setup.py` automatically creates tasks, configures dependencies, and deploys in one step) |
| Object storage | OSS (LOAD DATA INPATH) | Volume (COPY INTO FROM VOLUME) |
| UDF | Inline Python/Java (executed within the engine) | External Function (cloud function service) |
| Data retention | `LIFECYCLE 365` (auto-deletes data, no upper limit) | `TBLPROPERTIES ('data_retention_days' = '7')` (Time Travel history retention, max 90 days; physical data deletion requires manual or scheduled tasks) |
| Partitioning | PARTITIONED BY (ds STRING) | Same |
| Parameter variables | `${bizdate}` | Can be used directly in Studio task SQL; use f-string interpolation when executing via Python/cz-cli directly |

![](.topwrite/assets/31-maxcompute-migration.svg)

## Conclusion First

- **SQL changes**: 6 syntax replacements; all other standard SQL requires zero changes
- **Task orchestration**: 5 DataWorks nodes → 5 Studio tasks, dependency relationships fully preserved; the original Workflow JSON was only descriptive config without DataWorks API automation, requiring manual console operations; after migration, fully automated via `cz-cli` with `setup.py` completing everything in one step
- **Data validation**: ODS 8 tables / DWD 3 summary tables / ADS 3 analytics tables — all passing
- **UDFs**: Zero code logic changes; deployment method changed from "within the engine" to "cloud function service"

## Project Background

The source project is a standard e-commerce data engineering practice with a three-layer data architecture:

- **ODS layer**: 8 raw tables, loading CSV data from OSS
- **DWD layer**: Daily sales summary, customer segmentation, product performance analysis
- **ADS layer**: Web traffic analysis, incremental change detection, data quality monitoring

The DataWorks Workflow defines the dependency relationships for 5 task nodes:

```
data_quality_check
    ├── customer_segmentation
    ├── product_performance_etl
    └── web_analytics_etl
            └── daily_sales_summary (depends on the previous two)
```

## Migration Steps

### Step 1: Set Up Repo and Connection Configuration

Fork the source repo to the `clickzetta/` organization and reorganize the directory structure:

```bash
gh repo fork rcdelacruz/dataworks-maxcompute-practice \
  --org clickzetta \
  --fork-name maxcompute2lakehouse-ecommerce
gh repo clone clickzetta/maxcompute2lakehouse-ecommerce
```

Original code goes into `01_source/`, migrated code into `03_lakehouse/`:

```
maxcompute2lakehouse-ecommerce/
├── 01_source/          # Original MaxCompute code (preserved as-is)
├── 02_migration/       # Syntax difference notes, task mapping docs
├── 03_lakehouse/       # Migrated code
│   ├── sql/            # Lakehouse SQL
│   ├── tasks/          # Studio task list
│   ├── udf/            # External Function code
│   ├── setup.py        # One-step initialization
│   └── e2e.py          # End-to-end validation
└── data/               # 8 CSV sample files
```

Configure the connection (`.env`):

```bash
cp .env.example .env
# Fill in CLICKZETTA_SERVICE / INSTANCE / WORKSPACE / USERNAME / PASSWORD
```

Initialize the environment (create profile, create tables, upload data, create Studio tasks):

```bash
pip install -r requirements.txt
python 03_lakehouse/setup.py
```

`setup.py` automatically completes 6 steps: create cz-cli profile → create Schema → create Volume and upload CSV → create tables → COPY INTO to load data → create Studio tasks (with dependency configuration and cron scheduling).

### Step 2: SQL Syntax Adaptation (6 Changes)

The differences between MaxCompute and Lakehouse SQL are limited to the following 6 areas. All other standard SQL syntax is identical.

**1. LIFECYCLE → TBLPROPERTIES data_retention_days**

MaxCompute uses `LIFECYCLE` to control automatic data deletion (no upper limit). Lakehouse uses `data_retention_days` to control the Time Travel history retention period (max 90 days). The semantics differ — `data_retention_days` does not automatically delete current data; it only affects the time window for historical version lookback:

```sql
-- MaxCompute (auto-deletes expired data)
CREATE TABLE orders (...) LIFECYCLE 365;

-- Lakehouse (sets Time Travel retention period, max 90 days)
CREATE TABLE orders (...);
ALTER TABLE orders SET PROPERTIES ('data_retention_days' = '7');

-- Or specify directly at table creation
CREATE TABLE orders (...)
TBLPROPERTIES ('data_retention_days' = '7');
```

> ⚠️ **Note**: If you previously relied on `LIFECYCLE` to automatically clean up historical partition data, you will need to replace that with a scheduled Studio task running `ALTER TABLE ... DROP PARTITION` after migration.

**2. DATETIME → STRING (ODS layer)**

MaxCompute's `DATETIME` type cannot be implicitly converted from a CSV string during `COPY INTO`. In the ODS layer, use `STRING` to receive raw values, then `CAST` during DWD layer transformation:

```sql
-- MaxCompute ODS
order_date DATETIME

-- Lakehouse ODS (receives raw CSV string)
order_date STRING

-- Lakehouse DWD (explicit CAST during transformation)
CAST(order_date AS TIMESTAMP)
```

**3. LOAD DATA INPATH → COPY INTO FROM VOLUME**

MaxCompute loads data from OSS using `LOAD DATA INPATH`. Lakehouse uses `COPY INTO FROM VOLUME` with a different syntax structure:

```sql
-- MaxCompute
LOAD DATA INPATH 'oss://bucket/data/customers.csv' INTO TABLE customers;

-- Lakehouse
COPY INTO ecommerce.customers
FROM VOLUME ecommerce.ecommerce_vol
USING CSV
OPTIONS ('header' = 'true')
FILES ('raw/customers.csv');
```

> ⚠️ **Note**: Lakehouse `COPY INTO` does not support the `FILE_FORMAT = (TYPE = 'CSV' ...)` syntax. You must use the `USING CSV OPTIONS(...)` form.

**4. ${bizdate} Parameter Variables**

`${bizdate}` can be used directly in Studio task SQL and will be substituted by the scheduling system at runtime, consistent with DataWorks behavior. When executing SQL directly via Python code or cz-cli, `${bizdate}` will not be substituted (returns an empty string) — use f-string interpolation instead:

```python
# Can be kept as-is in Studio task SQL (substituted at scheduled runtime)
INSERT OVERWRITE TABLE daily_sales PARTITION (ds = '${bizdate}') ...

# When executing directly via Python / cz-cli, pass via f-string
bizdate = "20240115"
session.sql(f"""
    INSERT OVERWRITE TABLE ecommerce_dwd.daily_sales
    PARTITION (ds = '{bizdate}')
    SELECT ...
""").collect()
```

**5. GETDATE() → CURRENT_TIMESTAMP()**

```sql
-- MaxCompute
GETDATE()

-- Lakehouse
CURRENT_TIMESTAMP()
```

**6. RLIKE → REGEXP, CAST AS STRING → CAST AS VARCHAR**

```sql
-- MaxCompute
email RLIKE '^[A-Za-z0-9+_.-]+@...$'
CAST(count AS STRING)

-- Lakehouse
email REGEXP '^[A-Za-z0-9+_.-]+@...$'
CAST(count AS VARCHAR)
```

**Fully compatible, zero changes required:**

- `JOIN` (INNER / LEFT / RIGHT / FULL OUTER / SELF)
- Window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, `SUM OVER`, `AVG OVER`)
- CTE (`WITH ... AS (...)`)
- `CASE WHEN`, `COALESCE`, `NULLIF`
- `DATE_FORMAT`, `DATEDIFF`, `YEAR`, `MONTH`, `DAYOFWEEK`
- `CONCAT`, `UPPER`, `LOWER`, `LIKE`
- `PARTITIONED BY (ds STRING)` partition syntax
- `INSERT OVERWRITE TABLE ... PARTITION (...)`
- `UNION ALL`, `HAVING`, `LIMIT`, `OFFSET`

### Step 3: Data Loading

`setup.py` uploads the 8 CSV files from the `data/` directory to a Volume, then loads them using `COPY INTO`:

```python
# Upload to Volume
session.file.put(str(csv_file), f"vol://ecommerce.ecommerce_vol/raw/")

# Load (in SQL file)
COPY INTO ecommerce.orders PARTITION (ds = '20240115')
FROM VOLUME ecommerce.ecommerce_vol
USING CSV OPTIONS ('header' = 'true')
FILES ('raw/orders.csv');
```

Actual load results:

| Table | Row Count |
|---|---|
| customers | 10 |
| products | 10 |
| orders | 10 |
| order_items | 30 |
| web_sessions | 20 |
| page_views | 30 |
| user_events | 30 |
| suppliers | 9 |

### Step 4: Migrate DataWorks Workflow → Studio Tasks

The original project's `daily_etl_workflow.json` is a descriptive configuration file. DataWorks provides an API for task automation, but the original project did not implement it — in practice, you had to log into the console and manually create each node, configure dependencies, and set up scheduling.

After migration, step 6 of `setup.py` completes everything automatically via `cz-cli task`: creating tasks, writing SQL content, configuring dependencies, setting cron schedules, and deploying — no manual operations required.

For manual operations or to understand the underlying commands, the core steps are:

```bash
# Create task (--profile ensures consistent context)
cz-cli task create data_quality_check --type SQL \
  --folder ecommerce_etl --profile ecommerce_dev

# Write SQL content
cz-cli task save-content data_quality_check \
  --file 03_lakehouse/sql/06_data_quality.sql \
  --profile ecommerce_dev

# Configure dependencies (dep-tasks requires a JSON array of taskId + taskName; get taskId via cz-cli task list)
cz-cli task save-config customer_segmentation \
  --deps replace \
  --dep-tasks '[{"taskId":10353489,"taskName":"data_quality_check"}]' \
  --profile ecommerce_dev

# Configure cron schedule (daily at 02:00)
cz-cli task save-cron data_quality_check \
  --cron "0 2 * * *" --profile ecommerce_dev

# Deploy
cz-cli task deploy data_quality_check --profile ecommerce_dev
```

DataWorks → Studio task mapping:

| DataWorks Node | Studio Task | Dependencies |
|---|---|---|
| data_quality_check | data_quality_check | None (entry point) |
| customer_segmentation | customer_segmentation | data_quality_check |
| product_performance | product_performance_etl | data_quality_check |
| web_analytics_summary | web_analytics_etl | data_quality_check |
| daily_sales_summary | daily_sales_summary | customer_segmentation + product_performance_etl |

### Step 5: UDF Migration

MaxCompute UDFs execute directly within the engine. Lakehouse UDFs must be deployed to a cloud function service (Alibaba Cloud FC / Tencent Cloud SCF). Code logic requires zero changes — only adapt to the Lakehouse External Function specification:

```python
# MaxCompute (inherits com.aliyun.odps.udf.UDF)
from odps.udf import annotate
@annotate("string->string")
class Upper(BaseUDTF):
    def evaluate(self, arg):
        return arg.upper()

# Lakehouse (adapt to cz.udf, everything else unchanged)
try:
    from cz.udf import annotate
except ImportError:
    annotate = lambda _: lambda cls: cls  # local development placeholder

@annotate("string->string")
class Upper(object):
    def evaluate(self, arg):
        return arg.upper() if arg else None
```

Register the function:

```sql
CREATE EXTERNAL FUNCTION IF NOT EXISTS ecommerce.text_sentiment(text STRING)
    RETURNS STRING
    AS 'text_analytics.TextSentiment'
    USING FILE = 'volume:user://~/text_analytics.zip'
    CONNECTION = ecommerce_fc_conn
    WITH PROPERTIES ('remote.udf.api' = 'python3.mc.v0');
```

> ⚠️ **Note**: `CREATE EXTERNAL FUNCTION` does not support `OR REPLACE` — use `IF NOT EXISTS` only. When calling the function, you must include the full schema prefix: `ecommerce.text_sentiment(...)`.

## Pitfalls Encountered

### Pitfall 1: COPY INTO Syntax Differs from Snowflake

The first attempt used Snowflake-style `FILE_FORMAT = (TYPE = 'CSV' ...)` syntax, resulting in `CZLH-60001 parser return null`. The correct Lakehouse syntax is `USING CSV OPTIONS(...)`:

```sql
-- Error (Snowflake style)
COPY INTO ecommerce.customers
FROM VOLUME ecommerce_vol
FILES = ('raw/customers.csv')
FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 1);

-- Correct
COPY INTO ecommerce.customers
FROM VOLUME ecommerce_vol
USING CSV OPTIONS ('header' = 'true')
FILES ('raw/customers.csv');
```

### Pitfall 2: ODS Layer Date Columns Cannot Use TIMESTAMP

`COPY INTO` does not support implicit conversion from CSV strings to `TIMESTAMP`, resulting in `CZLH-42000 implicit cast not allowed`. ODS layer date columns must use `STRING`, with `CAST` applied in the DWD layer:

```sql
-- ODS table created with TIMESTAMP, COPY INTO fails
order_date TIMESTAMP

-- ODS uses STRING, CAST during DWD transformation
order_date STRING  -- ODS layer
CAST(order_date AS TIMESTAMP)  -- used in DWD layer
```

### Pitfall 3: Comma in CSV Field Causes Column Count Overflow

Row 30 of `user_events.csv` had an `event_data` field value of `products:PROD006,PROD007` — containing a comma but not quoted — causing `COPY INTO` to report `Expected 9 columns, got 10`. Lakehouse's `on_error='continue'` option fails before the Arrow parsing layer and cannot skip the row.

Fix: repair the source data in Python by merging the extra columns back into the last column:

```python
import csv
rows = list(csv.reader(open('user_events.csv')))
header_len = len(rows[0])
fixed = [r[:header_len-1] + [','.join(r[header_len-1:])]
         if len(r) > header_len else r for r in rows]
csv.writer(open('user_events.csv', 'w')).writerows(fixed)
```

### Pitfall 4: cz-cli task save-config --deps Parameter Meaning

`--deps` does not accept a task name — it controls the dependency operation mode (`keep` / `replace` / `clear`). The actual upstream tasks are passed via `--dep-tasks` as a JSON array:

```bash
# Wrong (--deps does not accept task names)
cz-cli task save-config customer_segmentation \
  --deps data_quality_check

# Correct
cz-cli task save-config customer_segmentation \
  --deps replace \
  --dep-tasks '[{"taskId":10353489,"taskName":"data_quality_check"}]'
```

## End-to-End Validation

Run `python 03_lakehouse/e2e.py --reset` for full validation:

```
=== Data Summary ===

ecommerce (ODS):
  customers                  10 rows
  products                   10 rows
  orders                     10 rows
  order_items                30 rows
  web_sessions               20 rows
  page_views                 30 rows
  user_events                30 rows
  suppliers                   9 rows

ecommerce_dwd (DWD):
  daily_sales_summary         4 rows
  customer_segments          10 rows
  product_performance        10 rows

ecommerce_ads (ADS):
  web_analytics_summary       1 row
  customer_changes            0 rows
  data_quality_metrics        3 rows
  dq_rules                    6 rows
  dq_assessment               6 rows
  data_profile                3 rows

=== Data Validation ===

[Row Count Assertions]
  PASS  ecommerce.customers  (10)
  PASS  ecommerce.orders  (10)
  ...(all 17 tables passed)

[ODS Integrity]
  PASS  customers.customer_id no NULLs  (0)
  PASS  orders.total_amount all > 0  (0)
  PASS  order_items.order_id all exist in orders  (0)
  ...

[DWD Business Assertions]
  PASS  customer_segments covers all customers  (10)
  PASS  customer_segments contains 3 segments  (3)
  ...

[ADS Business Assertions]
  PASS  dq_assessment at least 1 PASS  (6 records)
  PASS  data_profile covers 3 tables  (3)
  ...

  Validation result: 26/26 passed  All passed

=== Studio Task Validation ===
  data_quality_check             triggered successfully
  customer_segmentation          triggered successfully
  product_performance_etl        triggered successfully
  web_analytics_etl              triggered successfully
  daily_sales_summary            triggered successfully
```

## Full Syntax Reference

| Scenario | MaxCompute | Lakehouse |
|---|---|---|
| Data retention | `LIFECYCLE 365` | `TBLPROPERTIES ('data_retention_days' = 'N')` (max 90 days, controls Time Travel retention period) |
| Date/time type | `DATETIME` | `TIMESTAMP` (use `STRING` in ODS layer) |
| Current time | `GETDATE()` | `CURRENT_TIMESTAMP()` |
| Partition write | `INSERT OVERWRITE TABLE t PARTITION (ds='${bizdate}')` | `${bizdate}` can be kept in Studio task SQL; use f-string when executing directly via Python |
| Parameter variables | `${bizdate}` | Supported in Studio task SQL; use f-string when executing directly via Python/cz-cli |
| Data loading | `LOAD DATA INPATH 'oss://...'` | `COPY INTO ... FROM VOLUME ... USING CSV OPTIONS(...)` |
| Regex matching | `col RLIKE 'pattern'` | `col REGEXP 'pattern'` |
| Cast to string | `CAST(x AS STRING)` | `CAST(x AS VARCHAR)` |
| UDF registration | `CREATE FUNCTION f AS 'Class' USING 'file.py'` | `CREATE EXTERNAL FUNCTION f ... CONNECTION = conn` |
| Task orchestration | DataWorks Workflow JSON | Studio tasks + `cz-cli task` |
| Task dependency config | Workflow JSON `dependencies` field | `cz-cli task save-config --deps replace --dep-tasks '[...]'` |

## Related Documentation

- [ZettaPark Python SDK Guide](zettapark-guide.md)
- [COPY INTO Syntax Reference](copy-into.md)
- [Studio Task Management](studio-task.md)
- [cz-cli Task Management Command Reference](cz-cli-task.md)
- [External Function Deployment Guide](external-function.md)
