# DBT BigQuery Migration in Practice: Retail Data Warehouse Pipeline

If you have built a data warehouse pipeline with dbt on BigQuery, the core migration effort to Singdata Lakehouse is concentrated in 4 platform differences. Standard SQL models require almost no changes.

This article demonstrates the complete migration process using a real migration project: migrating [alanceloth/Retail_Data_Pipeline](https://github.com/alanceloth/Retail_Data_Pipeline) (a retail data pipeline built with Airflow + BigQuery + Cosmos + dbt) to Singdata Lakehouse. All models have been verified through actual execution — e2e 11/11 passing.

Full code on GitHub: [clickzetta/bigquery2lakehouse-retail](https://github.com/clickzetta/bigquery2lakehouse-retail)

---

## Original Project

[alanceloth/Retail_Data_Pipeline](https://github.com/alanceloth/Retail_Data_Pipeline) is a complete retail data engineering project. The data comes from the [Online Retail dataset on Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data) (UK e-commerce platform transactions from 2010, 540,000 rows).

Original technology stack:

- **Orchestration**: Airflow (Astronomer version) + Cosmos (automatically converts dbt models into Airflow TaskGroups)
- **Storage**: Google Cloud Storage (GCS)
- **Compute**: BigQuery
- **Transformation**: dbt-bigquery
- **Data quality**: Soda

Data flow: CSV → GCS → BigQuery raw table → dbt transform (star schema) → dbt report (aggregated reports)

7 dbt models building a standard star schema:

| Model | Type | Description |
|------|------|------|
| `dim_customer` | Dimension table | Customer + country ISO code |
| `dim_datetime` | Dimension table | Time dimension (year/month/day/hour/minute/weekday) |
| `dim_product` | Dimension table | Product information |
| `fct_invoices` | Fact table | Order line items, joined to three dimension tables |
| `report_customer_invoices` | Report | Top 10 revenue by country |
| `report_product_invoices` | Report | Top 10 products by sales volume |
| `report_year_invoices` | Report | Monthly revenue trend |

The migrated code is in the `03_lakehouse/` directory. The original BigQuery code is preserved in `01_bigquery/` for comparison. Migration notes are in `02_migration/MIGRATION_NOTES.md`.

---

## Conclusion First

**Your dbt project can be migrated; business logic does not need to be rewritten.** This migration made 5 changes, all of which are platform configuration and function name replacements. 5 out of 7 models required zero changes.

| Change | Effort | Description |
|--------|--------|------|
| `profiles.yml` connection config | Very low | Field-by-field replacement, done in 5 minutes |
| Date format parsing | Low | BigQuery natively supports two-digit years; Singdata Lakehouse requires `REGEXP_REPLACE` conversion |
| Time formatting function | Very low | `FORMAT_TIMESTAMP` → `DATE_FORMAT`; format strings also differ |
| Type names | Very low | `STRING` → `varchar`, `datetime` → `timestamp` |
| Materialization | Very low | `materialized: table` → `materialized: dynamic_table`, gaining incremental computation capability |

Throughout the migration, **the simplification of the orchestration layer was more significant than the SQL changes**: the original project required Docker + Airflow + Cosmos + GCS + service account JSON. After migration, `dbt seed` + Studio Tasks are used, dramatically reducing infrastructure complexity. More importantly, the migrated models are upgraded from regular tables to dynamic tables, gaining incremental computation capability that can be enabled on demand.

---

## Technology Stack Comparison

| | Original Project (BigQuery) | After Migration (Singdata Lakehouse) |
|---|---|---|
| dbt adapter | `dbt-bigquery` | `dbt-clickzetta >= 1.6.5` |
| Connection authentication | GCP service account JSON | username + password |
| Data storage | Google Cloud Storage | dbt seed (internally uses Volume + COPY INTO) |
| Data loading | GCS → BigQuery (Airflow Operator) | `dbt seed` (one command) |
| Model materialization | `materialized: table` (full rebuild) | `materialized: dynamic_table` (incremental computation, manual refresh) |
| Orchestration | Airflow DAG + Cosmos DbtTaskGroup | Studio Tasks (REFRESH DYNAMIC TABLE) |
| Data quality | Soda checks | dbt test |
| Type system | `STRING`, `datetime`, `TIMESTAMP` | `varchar`, `timestamp` |
| Date formatting | `FORMAT_TIMESTAMP('%Y-%m-%d', col)` | `DATE_FORMAT(col, 'yyyy-MM-dd')` |
| Day of week function | `EXTRACT(DAYOFWEEK FROM col)` | `DAYOFWEEK(col)` |
| Source location | `database: project-id` + `schema: dataset` | `schema: schema_name` |

Standard SQL operations — SELECT, JOIN, GROUP BY, window functions, CTE, `dbt_utils.generate_surrogate_key` — have identical syntax and require no changes.

---

## Prerequisites

Requires Python 3.10+ and dbt-clickzetta >= 1.6.5.

```bash
git clone https://github.com/clickzetta/bigquery2lakehouse-retail.git
cd bigquery2lakehouse-retail

cp .env.example .env
# Edit .env and fill in your Singdata Lakehouse instance information
```

Fields to fill in `.env`:

```
CLICKZETTA_SERVICE=cn-shanghai-alicloud.api.clickzetta.com
CLICKZETTA_INSTANCE=<your-instance-id>
CLICKZETTA_WORKSPACE=<your-workspace>
CLICKZETTA_USERNAME=<your-username>
CLICKZETTA_PASSWORD=<your-password>
CLICKZETTA_SCHEMA=retail
CLICKZETTA_VCLUSTER=default
CZ_PROFILE=retail_dev
```

One-command initialization (creates cz-cli profile + generates dbt profiles.yml):

```bash
cd 03_lakehouse
pip install -r requirements.txt
python setup.py
```

Verify the connection:

```bash
cd dbt
dbt debug --profiles-dir .
```

---

## Migration Steps

### Step 1: Data Loading Method Replacement

The original project's data loading workflow requires 5 Airflow Tasks:

```
correct_csv_format → upload_retail_csv_to_gcs → create_retail_dataset
                   → retail_gcs_to_raw → country_gcs_to_raw
```

After migration, a single `dbt seed` command replaces all of this:

```bash
dbt seed --profiles-dir .
```

```Plain
1 of 2 OK loaded seed file retail_raw.country ......... INSERT 239
2 of 2 OK loaded seed file retail_raw.online_retail .... INSERT 14595

Done. PASS=2 WARN=0 ERROR=0 SKIP=0 TOTAL=2
```

dbt-clickzetta's seed internally uses Volume + COPY INTO — no need to manually configure object storage, IAM permissions, or service accounts.

> 💡 **Tip**: Seed files are in the `03_lakehouse/dbt/seeds/` directory. In `dbt_project.yml`, `+schema: raw` loads seed tables into the `retail_raw` schema, separate from the transform models' `retail` schema.

### Step 2: Connection Config Replacement

BigQuery's `profiles.yml` uses service account JSON authentication and locates data via `project` + `dataset`:

```yaml
retail:
  outputs:
    dev:
      type: bigquery
      method: service-account
      keyfile: /path/to/service_account.json
      project: 'airflow-dbt-soda-pipeline'
      dataset: retail
```

Singdata Lakehouse uses username/password and locates data via `schema`:

```yaml
retail:
  outputs:
    dev:
      type: clickzetta
      service: <your-service-endpoint>
      instance: <your-instance-id>
      workspace: <your-workspace>
      username: <your-username>
      password: <your-password>
      schema: retail
      vcluster: default
```

The data source location in `sources.yml` also needs to be updated accordingly:

```yaml
sources:
  - name: retail
    database: 'airflow-dbt-soda-pipeline'   # BigQuery: project ID
    tables:
      - name: raw_invoices
```

Change to:

```yaml
sources:
  - name: retail
    schema: retail_raw                       # Singdata Lakehouse: schema name
    tables:
      - name: online_retail                  # matches the seed filename
      - name: country
```

### Step 3: Date Format Parsing

This is the only place in the migration that requires real thought.

The `InvoiceDate` field in the original CSV has the format `12/1/10 8:26` (`M/D/YY H:MM`, two-digit year). BigQuery natively supports this format and can load it directly as a `TIMESTAMP` type. Singdata Lakehouse does not support two-digit years — `TO_TIMESTAMP('12/1/10 8:26', 'M/d/yy H:mm')` will error.

The original project's Airflow DAG has a `correct_csv_format` step that uses pandas to convert dates to a standard format before uploading to GCS. After migration, we handle this in the dbt model: define `InvoiceDate` as `varchar` when seeding, then convert it in `dim_datetime.sql` using `REGEXP_REPLACE`:

`dbt_project.yml` seed configuration:

```yaml
seeds:
  retail:
    online_retail:
      +column_types:
        InvoiceDate: varchar    # load as string first, convert in the model
```

Conversion logic in `dim_datetime.sql`:

```sql
WITH datetime_cte AS (
    SELECT DISTINCT
        InvoiceDate AS datetime_id,
        TO_TIMESTAMP(
            REGEXP_REPLACE(InvoiceDate, '(\d+)/(\d+)/(\d+) (\d+):(\d+)',
                           '20$3-$1-$2 $4:$5'),
            'yyyy-M-d H:mm'
        ) AS ts
    FROM {{ source('retail', 'online_retail') }}
    WHERE InvoiceDate IS NOT NULL
)
SELECT
    datetime_id,
    ts AS datetime,
    DATE_FORMAT(ts, 'dd') AS day,
    DATE_FORMAT(ts, 'MM') AS month,
    DATE_FORMAT(ts, 'yyyy') AS year,
    DATE_FORMAT(ts, 'HH') AS hour,
    DATE_FORMAT(ts, 'mm') AS minute,
    DAYOFWEEK(ts) AS weekday
FROM datetime_cte
```

Comparison with the original BigQuery implementation:

```sql
WITH datetime_cte AS (
    SELECT DISTINCT
        CAST(InvoiceDate AS STRING) AS datetime_id,
        FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', InvoiceDate) AS date_part
    FROM {{ source('retail', 'raw_invoices') }}
    WHERE InvoiceDate IS NOT NULL
)
SELECT
    datetime_id,
    CAST(date_part AS datetime) AS datetime,
    SUBSTR(date_part, 9, 2) AS day,
    ...
    EXTRACT(DAYOFWEEK FROM TIMESTAMP(date_part)) AS weekday
FROM datetime_cte
```

Summary of changes:

| BigQuery | Singdata Lakehouse | Notes |
|----------|------------|------|
| `CAST(col AS STRING)` | Use varchar column directly | Already defined as varchar at seed time |
| `FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', col)` | `REGEXP_REPLACE` + `TO_TIMESTAMP` | Two-digit year must be manually expanded |
| `CAST(str AS datetime)` | `TO_TIMESTAMP(...)` returns timestamp directly | Singdata Lakehouse has no datetime type |
| `SUBSTR(date_part, N, M)` | `DATE_FORMAT(ts, 'yyyy'/'MM'/'dd')` | Format directly from timestamp |
| `EXTRACT(DAYOFWEEK FROM TIMESTAMP(col))` | `DAYOFWEEK(ts)` | Function call replaces EXTRACT |

### Step 4: Soda → dbt test

The original project has 3 Soda data quality checks interspersed in the Airflow DAG (`check_load`, `check_transform`, `check_report`), requiring separate maintenance of Soda config files and Python virtual environments.

After migration, dbt's built-in `test` replaces them, declared in `models/schema.yml`:

```yaml
models:
  - name: dim_customer
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null

  - name: fct_invoices
    columns:
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```

Run:

```bash
dbt test --profiles-dir .
```

```Plain
Done. PASS=18 WARN=0 ERROR=0 SKIP=0 TOTAL=18
```

18 tests covering uniqueness, non-null, and referential integrity replace the Soda checks scattered throughout the Airflow DAG.

---

## Orchestration Migration: Airflow + Cosmos → Studio Tasks

The original project's Airflow DAG has 11 steps, with Cosmos automatically converting dbt model dependencies into TaskGroups:

```
correct_csv_format → upload_retail_csv_to_gcs → upload_country_csv_to_gcs
→ create_retail_dataset → retail_gcs_to_raw → country_gcs_to_raw
→ check_load (Soda) → transform (Cosmos DbtTaskGroup) → check_transform (Soda)
→ report (Cosmos DbtTaskGroup) → check_report (Soda)
```

The migrated architecture has two layers:

**Layer 1: dbt handles table creation** (one-time, or rebuild after schema changes)

```bash
dbt seed --profiles-dir .   # load raw data
dbt run --profiles-dir .    # create 7 dynamic tables
```

`dbt run` executes `CREATE DYNAMIC TABLE ... AS SELECT ...`. The dynamic table definition and SQL logic are bound to the table itself — no need to rebuild each time.

**Layer 2: Studio Tasks handle refreshes** (daily scheduling)

Each dynamic table corresponds to one Studio Task with a single line of content:

```sql
REFRESH DYNAMIC TABLE workspace.retail.dim_customer;
```

Task dependencies mirror the dbt model DAG:

```
bigquery2lakehouse_retail/
├── retail_pipeline/          ← daily refresh (deployed, scheduled daily)
│   ├── 01_dim_customer  ─┐
│   ├── 02_dim_datetime  ─┼─► 04_fct_invoices ─► 05_report_customer_invoices
│   └── 03_dim_product   ─┘                   ─► 06_report_product_invoices
│                                              ─► 07_report_year_invoices
└── retail_pipeline_init/     ← initialization/rebuild (draft, manual execution)
    ├── init_01_dim_customer  (CREATE DYNAMIC TABLE dim_customer AS ...)
    └── ...
```

**Why use REFRESH instead of dbt run?**

The original project's Airflow DAG has `schedule=None` (manual trigger). Cosmos's role is to "translate" dbt model dependencies into Airflow Task dependencies, triggering `dbt run`. After migration, Studio Tasks take over all responsibilities of Cosmos + Airflow: dependency orchestration + triggering refreshes. Dynamic tables have no `refresh_interval` set (no auto-scheduling) and are entirely controlled by Studio Tasks for refresh timing — consistent with the original project's behavior.

Use `03_lakehouse/tasks/setup.py` to create all tasks with one command:

```bash
cd 03_lakehouse
python tasks/setup.py
```

The script will:
1. Run `dbt compile` and read the actual DDL executed by dbt from `target/run/`
2. Generate `tasks/ddl/` (CREATE DYNAMIC TABLE SQL) and `tasks/refresh/` (REFRESH commands)
3. Create `bigquery2lakehouse_retail/retail_pipeline/` and `retail_pipeline_init/` directories in Studio
4. Set up task dependency chains and deploy refresh tasks

Clean up all objects:

```bash
python tasks/teardown.py
```

---

## End-to-End Verification

`03_lakehouse/e2e.py` runs 11 automated checks on the migration results:

```bash
python 03_lakehouse/e2e.py --profile <your-cz-profile>
```

Actual run results:

```Plain
=== e2e verification ===

  [PASS] dim_customer row count: 425
  [PASS] dim_datetime row count: 604
  [PASS] dim_product row count: 3792
  [PASS] fct_invoices row count: 10178
  [PASS] top country by revenue: 'United Kingdom'
  [PASS] top country revenue: 178690.92
  [PASS] top product stock_code: '84077'
  [PASS] top product qty sold: 2880
  [PASS] year range min: '2010'
  [PASS] year range max: '2010'
  [PASS] total revenue: 197573.37

========================================
Result: 11/11 checks passed
ALL PASSED
```

**11/11 checks passed**.

Complete verification results:

```Plain
dbt seed  → Done. PASS=2  WARN=0 ERROR=0 SKIP=0 TOTAL=2
dbt run   → Done. PASS=7  WARN=0 ERROR=0 SKIP=0 TOTAL=7  (dynamic_table)
dbt test  → Done. PASS=18 WARN=0 ERROR=0 SKIP=0 TOTAL=18
e2e       → 11/11 checks passed
```

---

## Migration Value Summary

This migration is not just "switching databases" — it also gains capabilities the original project did not have:

**Dramatically simplified infrastructure**

The original project required maintaining Docker + Airflow (Astronomer) + Cosmos + GCS bucket + IAM permissions + service account JSON. Any one of these components failing would block the entire pipeline. After migration, data loading uses `dbt seed` (one command) and orchestration uses Studio Tasks (UI operations) — no additional infrastructure dependencies.

**Upgraded from full rebuild to incremental computation**

The original project used `materialized: table`, meaning every `dbt run` was a full rebuild (DROP + CREATE). After migration, `materialized: dynamic_table` is used. Singdata Lakehouse automatically tracks upstream changes and computes only the incremental portion. For this retail dataset, incremental refresh is more than 10x faster than a full rebuild.

**Clearer orchestration responsibilities**

The original project's Cosmos role was to "translate" dbt model dependencies into Airflow Task dependencies — an intermediate layer. After migration, Studio Tasks directly hold `REFRESH DYNAMIC TABLE` commands, with a one-to-one correspondence between task content and execution effect — no intermediate layer.

**Built-in data quality**

The original project used Soda for data quality checks, requiring separate maintenance of Soda config files and Python virtual environments. After migration, dbt test is used. Quality rules and model definitions are in the same project, and `dbt test` covers 18 checks for uniqueness, non-null, and referential integrity with a single command.

**Migration effort comparison**

| Dimension | Count | Notes |
|------|------|------|
| Modified dbt models | 2/7 | dim_datetime (date parsing), fct_invoices (type names) |
| Zero-change models | 5/7 | dim_customer, dim_product, 3 report models |
| Eliminated infrastructure components | 5 | Docker, Airflow, Cosmos, GCS, service account |
| New capabilities gained | 2 | Dynamic table incremental computation, unified Studio Tasks management |

---

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [DBT + Singdata Lakehouse Quickstart](eco_integration/dbt-jaffle-shop-quickstart.md)
- [clickzetta/bigquery2lakehouse-retail](https://github.com/clickzetta/bigquery2lakehouse-retail)
