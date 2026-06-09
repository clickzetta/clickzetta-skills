# dbt-databricks → dbt-clickzetta Migration in Practice: Financial Payment Data Pipeline

If your data pipeline is built with dbt + Databricks SQL, migrating to Singdata Lakehouse is far less work than you might expect — as little as changing one line in `profiles.yml`. All core dbt capabilities — CTE models, window functions, SCD Type 2 logic, data quality tests, unit tests, and data contracts — are fully compatible with Lakehouse and require zero changes.

This article validates that claim with a real project: a financial payment data pipeline built on dbt-databricks (staging → intermediate → marts → semantic, 30 models, 36 tests) was fully migrated to dbt-clickzetta and verified with `dbt seed 9/9 + dbt run 30/30 + dbt test 36/36` — all passing.

Full code on GitHub: [dbt-databricks2lakehouse-blueprint](https://github.com/clickzetta/dbt-databricks2lakehouse-blueprint)

---

## Original Project

[dbt-databricks2lakehouse-blueprint](https://github.com/clickzetta/dbt-databricks2lakehouse-blueprint) is forked from [Alex-Teodosiu/dbt-blueprint](https://github.com/Alex-Teodosiu/dbt-blueprint) (⭐72). The original stack is dbt-databricks + Databricks SQL Warehouse. The project simulates a P2P/P2B (peer-to-peer / peer-to-business) payment platform data engineering pipeline, covering five data domains — users, merchants, accounts, bank cards, and transactions — and implements the complete chain from raw events → cleansing → SCD Type 2 dimension tables → fact tables → semantic layer.

The migrated code is in the `03_lakehouse/` directory and can be compared file-by-file with `01_source/dbt_blueprint/`.

## Conclusion First

**The adapter is dbt's database dialect layer** — switching adapters means switching the database; the dbt models themselves do not need to change. Changes are concentrated in `profiles.yml` (connection configuration) and a handful of Databricks-specific syntax items.

| Change | Files | Effort | Notes |
|--------|-------|--------|-------|
| Adapter switch | 1 (`profiles.yml`) | Minimal | `type: databricks` → `type: clickzetta`, different connection params |
| Project profile name | 1 (`dbt_project.yml`) | Minimal | `connection_databricks` → `dbt_blueprint` |
| `getdate()` | 1 | Minimal | → `current_date()` |
| Macro target name | 1 | Minimal | `databricks_cluster` → `clickzetta_prod` |

**Parts that need no changes**: all CTE model logic, window functions (LEAD/LAG/ROW_NUMBER), SCD Type 2 logic, `dbt_utils.generate_surrogate_key()`, data quality tests, unit tests, data contracts, `SELECT * EXCEPT (col)`, `col :: type` cast syntax, `DATEDIFF(year, start, end)` — all natively supported by Lakehouse.

---

## Technology Stack Comparison

| | dbt-databricks (original) | dbt-clickzetta (migrated) |
|---|---|---|
| dbt adapter | `dbt-databricks` | `dbt-clickzetta` |
| Compute engine | Databricks SQL Warehouse | Singdata Lakehouse |
| Connection method | `host` + `http_path` + `token` | `instance` + `workspace` + `service` + `username` + `password` |
| Target catalog | `catalog: dbt_blueprint` | Not needed (workspace is the catalog) |
| SQL dialect | Databricks SQL | Lakehouse SQL (ANSI-compatible) |
| `:: cast` | Supported | **Supported** (same on both sides, no change needed) |
| `SELECT * EXCEPT` | Supported | **Supported** (same on both sides, no change needed) |
| `DATEDIFF(year, s, e)` | Supported | **Supported** (three-argument form compatible) |
| `getdate()` | Supported | Not supported → use `current_date()` |
| Model logic (CTE/Window/JOIN) | — | **Fully identical** |

---

![](.topwrite/assets/anim-29-dbt-databricks-migration.svg)

---

## Project Background

The data comes from a simulated P2P/P2B payment platform and contains 9 raw event tables:

| Domain | Table | Rows | Description |
|--------|-------|------|-------------|
| Users | `user_events` | 196 | User registration/status change events (SCD2 source) |
| Merchants | `merchant_events` | 30 | Merchant registration/status changes |
| Merchants | `industry_codes` | 30 | Industry code reference table |
| Accounts | `account_events` | 80 | Bank account opening/change events |
| Bank cards | `card_events` | 60 | Card activation/status changes |
| Transactions | `raw_p2p_captured_events` | 150 | Successful P2P transactions |
| Transactions | `raw_p2p_failed_events` | 50 | Failed P2P transactions |
| Transactions | `raw_p2b_captured_events` | 80 | Successful P2B transactions |
| Transactions | `raw_p2b_failed_events` | 30 | Failed P2B transactions |

dbt four-layer architecture:

```
staging   → intermediate → marts         → semantic
(view)       (table)         (table)        (table)
raw events   SCD2 logic      dim + fact     enriched
```

---

## Migration Steps

### Step 1: Switch the Adapter (Core Change)

The original `profiles.yml` uses `type: databricks`. The migration only requires switching to `type: clickzetta`, replacing Databricks connection params `host/http_path/token` with Lakehouse params `instance/workspace/service`:

```yaml
# Original (dbt-databricks)
connection_databricks:
  target: dev_local
  outputs:
    dev_local:
      type: databricks
      catalog: dbt_blueprint
      schema: default
      host: dbc-a505ff10-0af5.cloud.databricks.com
      http_path: /sql/1.0/warehouses/4fa4ca06332da87f
      token: "{{ env_var('BLUEPRINT_DATABRICKS_TOKEN') }}"
      threads: 1
```

```yaml
# Migrated (dbt-clickzetta)
dbt_blueprint:
  target: dev
  outputs:
    dev:
      type: clickzetta
      instance: "{{ env_var('CZ_INSTANCE') }}"
      workspace: "{{ env_var('CZ_WORKSPACE') }}"
      schema: "{{ env_var('CZ_SCHEMA', 'dbt_blueprint_dev') }}"
      vcluster: "{{ env_var('CZ_VCLUSTER', 'DEFAULT') }}"
      username: "{{ env_var('CZ_USERNAME') }}"
      password: "{{ env_var('CZ_PASSWORD') }}"
      service: "{{ env_var('CZ_SERVICE') }}"
      threads: 4
```

Also update the `profile` name in `dbt_project.yml`:

```yaml
# Original
profile: 'connection_databricks'

# Migrated
profile: 'dbt_blueprint'
```

### Step 2: Replace `getdate()`

`getdate()` is a SQL Server/Databricks function. Lakehouse uses `current_date()`:

```sql
-- Original (int_users.sql)
{{ calculate_age('date_of_birth', 'getdate()') }} as age

-- Migrated
{{ calculate_age('date_of_birth', 'current_date()') }} as age
```

> 💡 **Tip**: The `:: cast` syntax and the three-argument `DATEDIFF(year, start, end)` form are both **natively supported** in Lakehouse — no changes needed.

### Step 3: Update the Target Name in the `generate_schema_name` Macro

The original macro uses `databricks_cluster` as the prod environment name. Change it to `clickzetta_prod`:

```sql
-- Original
{%- if target.name in ["prod", "databricks_cluster"] -%}

-- Migrated
{%- if target.name in ["prod", "clickzetta_prod"] -%}
```

---

## Fully Compatible Parts (No Changes Needed)

The following patterns are written identically on both sides and have been tested end-to-end:

```sql
-- :: cast type conversion — supported on both sides
userId       :: string    as user_id,
eventTime    :: timestamp as event_time,
amount       :: double    as transaction_amount

-- SCD Type 2 window logic
, users_scd2 as (
    select
        user_id, status, event_time as from_event_timestamp,
        lead(event_time) over w as to_event_timestamp
    from users
    window w as (partition by user_id order by event_time)
)

-- DATEDIFF three-argument form — supported on both sides
DATEDIFF(year, date_of_birth, current_date())

-- Surrogate key (dbt_utils)
{{ dbt_utils.generate_surrogate_key(['user_id', 'from_event_timestamp', 'status']) }}

-- SELECT * EXCEPT — supported on both sides
select * except (age)
from users
where age >= 18

-- Data contracts (model contracts)
config:
  contract:
    enforced: true
columns:
  - name: transaction_uid
    data_type: string
    data_tests:
      - not_null
      - unique

-- Unit tests
unit_tests:
  - name: test__int_users__scd_logic
    model: int_users
    given:
      - input: ref('stg_user_events')
        rows: [...]
    expect:
      rows: [...]
```

---

## dbt Test Results

Tested on the AWS Singapore instance (`aws_singapore_prod`), 36/36 all passing:

```
dbt seed:  9/9  PASS  (196 users, 310 transactions, 80 accounts, 60 cards...)
dbt run:  30/30 PASS  (9 views + 21 tables)
dbt test: 36/36 PASS  (21 data tests + 15 unit tests)
```

Data quality tests include: not_null/unique constraints on source tables, marts-layer data contracts (`contract: enforced: true`), and column type validation on fact_transaction. Unit tests cover SCD2 logic (`int_users__scd_logic`), transaction aggregation (`int_transactions__union_all`), and the age calculation macro (`calculate_age__valid_ages`).

---

## Notes

- **`getdate()` vs `current_date()`**: Databricks' `getdate()` returns the current timestamp. Lakehouse uses `current_date()` (date) or `current_timestamp()` (timestamp) as replacements. The `col :: type` cast syntax and the three-argument `DATEDIFF(year, s, e)` form are both **natively supported** in Lakehouse — no changes needed.
- **Catalog hierarchy**: Databricks uses three-part naming (`catalog.schema.table`). In dbt with Lakehouse, only `schema.table` is used; the adapter handles the rest automatically. No manual changes to table references in models are needed.
- **Seeds replacing the ingestion layer**: The original project relies on ingestion tables in the Databricks workspace. After migrating to Lakehouse, seeds CSVs are used as replacements. In production, these can be replaced with Studio data integration or CDC tasks.

## Related Documentation

### dbt Development Guides

- [dbt Quick Start](use-dbt-dev.md): dbt-clickzetta adapter installation and configuration
- [dbt Incremental Models](dbt-incremental.md): Incremental strategy configuration and unique_key options
- [dbt Data Quality Checks](dbt-data-quality.md): Data tests, contract validation, and custom tests
- [dbt Advanced Features](dbt-advanced-features.md): Macros, snapshots, semantic layer, and more

### Other Migration Case Studies

- [Databricks Notebook → Lakehouse Migration (Retail Medallion Pipeline)](databricks-notebook-to-studio-migration.md): PySpark Notebook → ZettaPark/Studio tasks
- [dbt BigQuery Migration: Retail Data Warehouse Pipeline](dbt-bigquery-to-clickzetta-migration.md): BigQuery → Lakehouse adapter migration
- [dbt Snowflake Migration: TPC-H Data Warehouse Pipeline](dbt-snowflake-to-clickzetta-migration.md): Snowflake → Lakehouse adapter migration
