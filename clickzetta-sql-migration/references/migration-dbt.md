# dbt Migration Guide — Databricks / Snowflake / BigQuery → ClickZetta

> Covers migrating an existing dbt project to ClickZetta Lakehouse using `dbt-clickzetta`.
> Based on 3 verified migration projects: dbt-databricks blueprint (30 models, 36 tests, **28/28 ✅**),
> Snowflake TPC-H (bronze/silver/gold + CDC + Dynamic Tables + Python),
> BigQuery retail (Airflow+Cosmos+Soda → Studio Tasks).
> For SQL syntax differences within dbt models, use the `clickzetta-sql-migration` skill which covers Databricks, Snowflake, and function-level migration guides.

## Table of Contents

| Section | Content | Line |
|---------|---------|:----:|
| [1](#1-adapter--setup) | Adapter & setup (`dbt-clickzetta`) | L28 |
| [2](#2-profilesyml) | `profiles.yml` — 1-line change per target | L52 |
| [3](#3-dbt_projectyml) | `dbt_project.yml` — profile name only | L87 |
| [4](#4-source-platform-changes) | Source-platform SQL changes | L103 |
| [5](#5-dynamic-tables--incremental) | Dynamic Tables & incremental strategies | L227 |
| [6](#6-streams--cdc-macros) | Table Streams & CDC macros | L282 |
| [7](#7-python-models) | Python models (dbt-clickzetta >= 1.7.10) | L317 |
| [8](#8-seeds) | Seeds | L341 |
| [9](#9-packages--macros) | Packages & macro compatibility | L367 |
| [10](#10-snowflake-specific) | Snowflake → ClickZetta reference | L438 |
| [11](#11-bigquery-specific) | BigQuery → ClickZetta reference | L492 |
| [12](#12-studio-pipeline) | Integration with Studio pipeline | L528 |

---

## 1. Adapter & Setup

### Install

```bash
pip install "dbt-clickzetta>=1.7.10"
# Python models:               pip install "dbt-clickzetta[python]>=1.7.10"
# Databricks catalog federation: pip install "dbt-clickzetta[databricks]>=1.7.10"
```

### Verified Environment

| Component | Version | Verified |
|-----------|---------|:---:|
| `dbt-clickzetta` | 1.7.13 (dev) / 1.7.10 (PyPI latest) | ✅ blueprint, TPCH, retail |
| `dbt-core` | 1.8+ | ✅ |
| Python | >= 3.9 | ✅ |
| PyPI package | `dbt-clickzetta` (pip install) | ✅ published by `clickzetta` |
| Source | `github.com/clickzetta/dbt-clickzetta` | ✅ private repo |

### Supported Materializations (all verified)

| Materialization | dbt-clickzetta | Verified |
|---|---|---|
| `table` | `CREATE OR REPLACE TABLE` | ✅ blueprint 30/30 |
| `view` | `CREATE OR REPLACE VIEW` | ✅ |
| `incremental` | `MERGE INTO` (default strategy) or `INSERT OVERWRITE` | ✅ blueprint, retail |
| `dynamic_table` | `CREATE OR REPLACE DYNAMIC TABLE ... REFRESH INTERVAL ...` | ✅ TPCH silver/gold |
| `snapshot` | `MERGE INTO` with `dbt_scd_id` / `dbt_updated_at` | ✅ TPCH dim_customer_changes |
| `seed` | `CREATE TABLE ... AS (CSV data)` via Volume + COPY INTO | ✅ blueprint 9 seeds, retail, TPCH |
| `python` | Python model (dbt-clickzetta >= 1.7.10, requires `[python]` extra) | ✅ TPCH customer_clustering |

---

## 2. profiles.yml

The **only required change** in profiles.yml is the `type` field and connection parameters. Everything else stays the same.

### Before → After (single line per target)

```yaml
# Databricks (before)
dbt_project:
  target: dev
  outputs:
    dev:
      type: databricks                        # ← change this line
      catalog: dbt_blueprint                  # ← replaced by instance
      schema: default
      host: dbc-xxx.cloud.databricks.com      # ← replaced by service
      http_path: /sql/1.0/warehouses/xxx      # ← removed
      token: "{{ env_var('DBT_TOKEN') }}"     # ← replaced by username+password

# Snowflake (before)
dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake                         # ← change this line
      account: xxx.us-east-1                  # ← replaced by service
      database: MY_DB                         # ← replaced by instance
      schema: public
      warehouse: COMPUTE_WH                   # ← replaced by vcluster
      role: TRANSFORMER                       # ← removed (workspace RBAC)

# ClickZetta (after)
dbt_project:
  target: dev
  outputs:
    dev:
      type: clickzetta
      service: cn-shanghai-alicloud.api.clickzetta.com   # cloud region API endpoint
      instance: f8866243                                 # instance name
      workspace: quick_start                             # workspace name
      schema: dbt_blueprint_dev
      vcluster: default                                  # compute cluster
      username: "{{ env_var('CZ_USERNAME') }}"
      password: "{{ env_var('CZ_PASSWORD') }}"
      threads: 4
```

### Full Field Mapping

| Databricks | Snowflake | BigQuery | **ClickZetta** |
|---|---|---|---|
| `type: databricks` | `type: snowflake` | `type: bigquery` | `type: clickzetta` |
| `catalog` | `database` | `project` | `workspace` |
| — | — | — | `instance` ✅ (required, unique to ClickZetta) |
| `host` | `account` | — | `service` |
| `http_path` | `warehouse` | `priority` | `vcluster` |
| `token` | `user`+`password`+`role` | `method`+`keyfile` | `username`+`password` |
| — | `role` | — | (managed via workspace RBAC) |
| `schema` | `schema` | `dataset` | `schema` |
| `threads` | `threads` | `threads` | `threads` ✅ (same) |

### VCluster Selection (TPCH verified)

| VCluster | Type | Use case |
|----------|------|---------|
| `default` | General-purpose | dbt development, all models |
| `my_ap_vc` | Analytical, larger size | Dynamic Table refresh, heavy aggregations |

```bash
# Check available VClusters before setting profiles.yml
cz-cli sql --sync "SHOW VCLUSTERS" --profile <name>
```

---

## 3. dbt_project.yml

**Only the profile name changes.** All model configs, hooks, and project structure stay the same.

```yaml
# dbt_project.yml — only one line changes
name: my_project
version: "1.0"
profile: dbt_blueprint     # ← update to match profiles.yml target name (was databricks/snowflake profile)
```

**No config removal needed.** `tblproperties` / `file_format` / `copy_grants` / `secure` / `transient` / `location_root` are silently ignored by dbt-clickzetta if they appear in model-level configs — `dbt run` succeeds without errors.

---

## 4. Source-Platform SQL Changes

### 4.1 Databricks → ClickZetta

Based on dbt-databricks blueprint: **30 models, 36 tests, 28/28 e2e ✅**. Only 3 types of SQL changes were needed across all 30 models:

**1. Cast syntax** (9 staging models — the most common fix):

```sql
-- ❌ Databricks
col :: type

-- ✅ ClickZetta
CAST(col AS type)
```

**2. Function names** (1 model):

| Databricks | ClickZetta |
|---|---|
| `getdate()` | `current_date()` |

**3. DATEDIFF macro rewrite** (1 macro — Databricks-specific 3-arg pattern):

```sql
-- ❌ Databricks custom macro: DATEDIFF(year, start, end) + DATEADD logic for age calculation
-- ✅ ClickZetta: YEAR(e) - YEAR(s) - CASE WHEN MONTH(e) < MONTH(s) ... style calculation
```

**What stayed the same** (verified, no changes):
- All CTE patterns, window functions, LEAD/LAG
- `ROWNUMBER() OVER (PARTITION BY ... ORDER BY ...)`
- SCD Type 2 logic (both timestamp and check strategies)
- All JOINs, filters, aggregations, `QUALIFY`
- `dbt_utils.generate_surrogate_key()` ✅
- `dbt_date` package ✅
- `SELECT * EXCEPT (col)` ✅ (both Databricks and ClickZetta support this)
- All 36 dbt tests (unique, not_null, relationships, accepted_values)
- Data contracts (model contracts)

### 4.2 Snowflake → ClickZetta

Based on TPCH migration: bronze/silver/gold layers with CDC streams, Dynamic Tables, and a Python model.

**Common function replacements** (verified):

| Snowflake | ClickZetta | Where |
|---|---|---|
| `sysdate()` | `current_timestamp()` | dim_orders |
| `IFF(cond, a, b)` | `IF(cond, a, b)` | general |
| `CHARINDEX(sub, str)` | `INSTR(str, sub)` ⚠️ reversed args | general |
| `to_char(date, 'YYYYMMDD')::number(8,0)` | `cast(date_format(date, 'yyyyMMdd') as int)` | dim_calendar_day |
| `last_day(date, 'YEAR')` / `last_day(date, 'WEEK')` | Manual: `date(concat(year, '-12-31'))` / `dateadd(day, 6, week_start)` | dim_calendar_day |
| `table(generator(rowcount => N))` | `explode(sequence(0, N-1))` | dim_calendar_day |
| `extract(dayofweek from ...)` | `dayofweek(...)` | order_facts_dynamic |
| `hash(col1, col2, ...)` | Not supported — use `hash_combine(crc32(col1), crc32(col2), ...)` | MACRO ONLY |
| `sequence_get_nextval()` macro | `row_number() over (order by ...)` | gold models |
| `object_construct('k', v)` | `named_struct('k', v)` | general |
| `parse_json(str)` | `parse_json(str)` ✅ Same | general |
| `coalesce(a, b)` | `coalesce(a, b)` ✅ Same | general |

**Unsupported configs — silently ignored (remove for clarity)**:

| Snowflake config | Action |
|---|---|
| `transient=false` | Remove (ClickZetta has no transient tables) |
| `merge_exclude_columns=[...]` | Remove (MERGE handles all columns) |
| `indexes: [{type: 'hash'}]` | Remove (use bloomfilter index if needed) |
| `on_configuration_change='apply'` | Remove (use `ALTER DYNAMIC TABLE`) |
| `target_lag='DOWNSTREAM'` | Replace with explicit `refresh_interval` |

### 4.3 BigQuery → ClickZetta

Based on BigQuery retail: Airflow+Cosmos+Soda → Studio Tasks + dbt-clickzetta. **7 models, 5 needed zero changes.**

**Platform-specific differences** (2 models changed):

| BigQuery | ClickZetta | File |
|---|---|---|
| `FORMAT_TIMESTAMP(...)` + `CAST(col AS STRING)` + `CAST(... AS datetime)` | `REGEXP_REPLACE` + `TO_TIMESTAMP` (parse M/D/YY H:MM manually) | dim_datetime |
| `EXTRACT(DAYOFWEEK FROM TIMESTAMP(col))` | `DAYOFWEEK(ts)` | dim_datetime |
| `CAST(InvoiceDate AS STRING)` | No CAST needed — seed already defined as varchar | fct_invoices |
| `database: 'project-id'` in sources.yml | `schema: retail_raw` | sources.yml |

**No changes** (5 of 7 models):
- `dim_customer.sql` — standard SQL
- `dim_product.sql` — standard SQL
- `fct_invoices.sql` — except one CAST removal
- `report_*.sql` (3 files) — all standard SQL, zero changes
- `dbt_utils.generate_surrogate_key` — cross-platform ✅

---

## 5. Dynamic Tables & Incremental

### dynamic_table Materialization

Verified in TPCH silver/gold: ClickZetta natively supports Dynamic Tables as a dbt materialization.

```sql
-- models/silver/order_facts_dynamic.sql
{{
    config(
        materialized='dynamic_table',
        refresh_interval='1 hour',
        refresh_vc='default'
    )
}}

SELECT ...
FROM {{ ref('bronze_orders') }}
```

| Snowflake Dynamic Table | ClickZetta Dynamic Table | Notes |
|---|---|---|
| `snowflake_warehouse=target.warehouse` | `refresh_vc='default'` | Different config key |
| `target_lag='1 hour'` | `refresh_interval='1 hour'` | Same value, different key |
| `target_lag='DOWNSTREAM'` | Not supported — use explicit `refresh_interval` | |
| `on_configuration_change='apply'` | Not supported — use `ALTER DYNAMIC TABLE` | Manual schema evolution |
| `REFRESH_MODE = 'FULL'` | Same ✅ | |

### incremental Strategy (+ Studio)

For models deployed as Studio scheduled tasks (via `clickzetta-dbt-studio-pipeline`):

| dbt Pattern | Studio Behavior |
|---|---|
| Model has `{% if is_incremental() %} WHERE updated_at > ...` | Upload compiled SQL as-is; configure upstream sync as dependency |
| Model uses `insert_overwrite` + `partition_by` (Type 2 in pipeline skill) | Inject scheduling parameters like `${bizdate}` |

> ⚠️ **`${bizdate}` only resolves during scheduled runs** — not on manual `cz-cli task execute`. Test with hardcoded dates first.

### MERGE — Supported, No WHEN NOT MATCHED BY SOURCE

```sql
-- ✅ Supported
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- ❌ Not supported
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

If a dbt model relies on `WHEN NOT MATCHED BY SOURCE`, rewrite as a two-step operation or use `INSERT OVERWRITE` with partition_by for the target partition.

---

## 6. Table Streams & CDC Macros

### Snowflake `get_stream()` → ClickZetta `get_table_stream()`

Verified in TPCH: Snowflake's built-in `get_stream()` macro is replaced by a custom macro.

```sql
-- Macro: macros/get_table_stream.sql
-- Snowflake: {{ get_stream(ref('dim_customers')) }}
-- ClickZetta: {{ get_table_stream(ref('dim_customers')) }}

-- The custom macro generates:
CREATE TABLE STREAM {{ relation }}_stream ON TABLE {{ relation }}
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

### Stream Metadata Fields

| Snowflake | ClickZetta | Notes |
|---|---|---|
| `METADATA$ACTION` | `__change_type` | ⚠️ **backtick-quote required**: `` `__change_type` `` |
| `METADATA$ISUPDATE` | `__change_type = 'UPDATE_BEFORE'` | Different semantics |
| `METADATA$ROW_ID` | `__commit_version` | |
| `SHOW_INITIAL_ROWS = TRUE` (post_hook) | `WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')` | Different syntax |
| `TABLE_STREAM_MODE = 'ALL'` | Not supported | Use `'STANDARD'` or `'APPEND_ONLY'` |

> ⚠️ `__change_type`, `__commit_timestamp`, `__commit_version` are **reserved column names** in ClickZetta. If your model produces these as output column names, use different aliases (e.g., `cdc_change_type`, `cdc_commit_ts`). When reading FROM a stream, backtick-quote them.

### SELECT * FROM Stream (with metadata exclusion)

```sql
-- Snowflake
SELECT * FROM {{ get_stream(ref('dim_customers')) }}
WHERE metadata$action = 'DELETE'

-- ClickZetta (dbt-clickzetta >= 1.6.5)
SELECT * EXCEPT(__change_type, __commit_timestamp, __commit_version)
FROM {{ get_table_stream(ref('dim_customers')) }}
WHERE `__change_type` = 'DELETE'
```

---

## 7. Python Models

Supported since dbt-clickzetta **1.7.10** (`pip install "dbt-clickzetta[python]"`).

### Snowpark Python → dbt-clickzetta Python

Verified in TPCH `customer_clustering.py`:

```python
# ❌ Snowpark Python model
import snowflake.snowpark as snowpark
def model(dbt, session: snowpark.Session):
    df = dbt.ref('dim_customers').to_pandas()
    # ... scikit-learn clustering ...
    return df

# ✅ dbt-clickzetta Python model
def model(dbt, session):
    df = dbt.ref('dim_customers').to_pandas()
    # ⚠️ ZettaPark .to_pandas() returns lowercase column names
    df.columns = df.columns.str.upper()
    # ... scikit-learn clustering ...
    return df
```

Key differences:

| Snowpark | dbt-clickzetta Python |
|---|---|
| `packages=['snowflake-snowpark-python', 'joblib']` | `packages=['scikit-learn', 'pandas', 'numpy']` (pre-installed by dbt-clickzetta) |
| `session.sproc.register(...)` | Not supported — remove stored procedure logic; Python model runs directly |
| `.to_pandas()` column case | **UPPERCASE** ← Snowpark | **lowercase** ← ZettaPark |
| `session.table(...)` equivalent | Not available — use `dbt.ref()` / `dbt.source()` | |

---

## 8. Seeds

Seeds use ClickZetta Volume + COPY INTO internally — same `dbt seed` command. Verified in all 3 projects.

```bash
# Works exactly the same
dbt seed
```

Key differences from other platforms:

| Platform | Seed behavior | ClickZetta |
|---|---|---|
| Databricks | `CREATE TABLE ... USING DELTA` | `CREATE TABLE` via Volume + COPY INTO CSV |
| Snowflake | `CREATE TABLE` via PUT + COPY INTO | `CREATE TABLE` via Volume + COPY INTO CSV ✅ Same |
| BigQuery | Auto-schema from CSV header | Same ✅ |

**`float8` type in seeds** (discovered during TPCH validation):
- Snowflake seeds with `float8` columns failed on dbt-clickzetta < 1.6.2
- **Fixed in dbt-clickzetta 1.6.2**: `float8` now automatically maps to `double`
- Still recommended: use explicit `column_types` in `dbt_project.yml` for seeds to avoid type inference overhead:

```yaml
# dbt_project.yml
seeds:
  my_project:
    raw_orders:
      +column_types:
        amount: double
        quantity: int
```

### Airflow → Studio: Eliminated Seed Upload Steps

In BigQuery retail, GCS upload + BigQuery load steps (7 Airflow tasks) are replaced by a single `dbt seed`:

```
Airflow: correct_csv → upload_retail_to_gcs → upload_country_to_gcs → create_dataset → retail_to_raw → country_to_raw
Studio:  seed_raw_data (dbt seed — one task)
```

---

## 9. Packages & Macro Compatibility

### `dbt_utils` — Verified

The only dbt_utils macro used and verified in the blueprint project is `generate_surrogate_key`. Other macros listed below have NOT been tested:

| `dbt_utils` macro | Status | Notes |
|---|---|---|
| `generate_surrogate_key` | ✅ Verified in blueprint | Used in staging + intermediate + marts models (30/30 dbt run, 36/36 dbt test) |
| `date_spine` | ❌ | Uses `WITH RECURSIVE` (not supported in ClickZetta). Pre-build date dimension table instead. |
| `star`, `union_relations`, `get_column_values`, `group_by`, `deduplicate`, `pivot` | Not tested | These macros were in the dbt_utils package but were NOT used by any blueprint model or test. Their compatibility with dbt-clickzetta adapter has not been verified. |

### `dbt_date` — Verified

Used in blueprint — zero issues.

### Custom Macros — `hash()` Required Rewrite

`hash()` is not supported in ClickZetta (discovered during TPCH validation):

```sql
-- ❌ Snowflake / Databricks
hash(col1, col2, col3)

-- ✅ ClickZetta replacement
hash_combine(crc32(col1), crc32(col2), crc32(col3))
-- ⚠️ hash_combine() requires bigint args; use crc32() to convert varchar to bigint
-- ⚠️ hash_combine_commutative() also exists for order-independent hashing
```

### `generate_schema_name.sql` — Target Name Changes

If your dbt project has a custom schema macro that checks `target.name`, update the target name:

```sql
-- Databricks (before)
{% if target.name in ["prod", "databricks_cluster"] %}

-- ClickZetta (after)
{% if target.name in ["prod", "clickzetta_prod"] %}
```

---

## 10. Snowflake → ClickZetta Reference

Complete diff from TPCH migration. Apply these changes to Snowflake dbt projects.

### Function Replacements

| Snowflake | ClickZetta |
|---|---|
| `sysdate()` | `current_timestamp()` |
| `IFF(cond, a, b)` | `IF(cond, a, b)` |
| `CHARINDEX(sub, str)` | `INSTR(str, sub)` ⚠️ args reversed |
| `to_char(d, 'YYYYMMDD')::number(8,0)` | `cast(date_format(d, 'yyyyMMdd') as int)` |
| `last_day(d, 'YEAR')` | `date(concat(year(d), '-12-31'))` |
| `last_day(d, 'WEEK')` | `dateadd(day, 6, week_start)` |
| `table(generator(rowcount => N))` | `explode(sequence(0, N-1))` |
| `extract(dayofweek from ...)` | `dayofweek(...)` |
| `hash(col1, col2, ...)` | `hash_combine(crc32(col1), crc32(col2), ...)` |
| `sequence_get_nextval()` macro | `row_number() over (order by ...)` |
| `object_construct('k', v)` | `named_struct('k', v)` |
| `null::timestamp_ntz` | `null` (no timestamp_ntz type) |

### Config Replacements

| Snowflake config | ClickZetta |
|---|---|
| `snowflake_warehouse=target.warehouse` | `refresh_vc='default'` |
| `target_lag='1 hour'` | `refresh_interval='1 hour'` |
| `target_lag='DOWNSTREAM'` | Not supported — use explicit interval |
| `on_configuration_change='apply'` | Not supported — `ALTER DYNAMIC TABLE` |
| `transient=false` | Remove |
| `merge_exclude_columns=[...]` | Remove |
| `indexes: [{type: 'hash'}]` | Remove |
| `post_hook: CREATE STREAM ... SHOW_INITIAL_ROWS = TRUE` | `post_hook: CREATE TABLE STREAM ... TABLE_STREAM_MODE = 'STANDARD'` |

### Stream / CDC

| Snowflake | ClickZetta |
|---|---|
| `METADATA$ACTION` | `` `__change_type` `` (backtick required) |
| `METADATA$ISUPDATE` | `` `__change_type` = 'UPDATE_BEFORE' `` |
| `METADATA$ROW_ID` | `__commit_version` |
| `TABLE_STREAM_MODE = 'ALL'` | Not supported |
| `get_stream(ref(...))` macro | `get_table_stream(ref(...))` custom macro |

### Float Types (verified)

| Snowflake | ClickZetta (dbt-clickzetta >= 1.6.2) |
|---|---|
| `float8` in seeds | Automatically maps to `double` ✅ |
| Explicit `column_types` | Still recommended for performance |

---

## 11. BigQuery → ClickZetta Reference

Complete diff from BigQuery retail migration.

### Function Replacements

| BigQuery | ClickZetta | File |
|---|---|---|
| `FORMAT_TIMESTAMP(...)` | `REGEXP_REPLACE` + `TO_TIMESTAMP` for non-standard formats | dim_datetime |
| `CAST(col AS STRING)` | No CAST if col is already varchar | fct_invoices |
| `CAST(str AS datetime)` | `TO_TIMESTAMP(str)` (ClickZetta has no `datetime` type) | dim_datetime |
| `EXTRACT(DAYOFWEEK FROM TIMESTAMP(col))` | `DAYOFWEEK(ts)` | dim_datetime |
| `EXTRACT(YEAR/MONTH/DAY FROM ts)` | `DATE_FORMAT(ts, 'yyyy'/'MM'/'dd')` | dim_datetime |
| `SUBSTR(date_part, N, M)` (extract from string) | `DATE_FORMAT(ts, 'yyyy'/'MM'/'dd'/'HH'/'mm')` | dim_datetime |

### Configuration Replacements

| BigQuery | ClickZetta |
|---|---|
| `type: bigquery` | `type: clickzetta` |
| `method: service-account` + `keyfile` | `username` + `password` |
| `project: 'project-id'` | `workspace` + `instance` |
| `dataset: retail` | `schema: retail` |
| `database: 'project-id'` (in sources.yml) | `schema: retail_raw` |
| `CAST(col AS datetime)` | No datetime type — use `TIMESTAMP` |

### Airflow / Cosmos → Studio Tasks

BigQuery retail's Airflow DAG (11 steps: GCS upload + BigQuery load + Cosmos + Soda) maps to Studio:

| Airflow | Studio |
|---|---|
| `correct_csv_format` + `upload_to_gcs` (×2) + `create_dataset` + `load_to_raw` (×2) | `dbt seed` (one task) |
| `transform` (Cosmos DbtTaskGroup, 4 models) | `dbt run --select transform` (one task) |
| `check_load` + `check_transform` + `check_report` (Soda) | `dbt test` (one task) |
| `report` (Cosmos DbtTaskGroup, 3 models) | `dbt run --select report` (one task) |

Dependency chain: `seed → dbt run transform → dbt test → dbt run report`

### Soda → dbt test

```yaml
# Soda (before) — checks/sources/raw.yml
checks for retail_raw:
  - row_count > 0
  - schema:
      when required:
        - InvoiceNo
        - StockCode
        - Quantity
        - InvoiceDate

# dbt (after) — models/schema.yml
models:
  - name: retail_raw
    tests:
      - dbt_utils.expression_is_true:
          expression: "InvoiceNo IS NOT NULL AND Quantity IS NOT NULL"
```

---

## 12. Studio Pipeline

After the dbt project builds successfully on ClickZetta, `clickzetta-dbt-studio-pipeline` deploys models as Studio tasks:

```bash
dbt run && dbt test       # Verify on ClickZetta
dbt compile               # Generate manifest.json
# → hand off to clickzetta-dbt-studio-pipeline
```

### Materialization → Studio Task Mapping

| dbt materialization | Studio task type | State | Scheduling |
|---|---|---|---|
| `view` | SQL (DDL) | DRAFT | None |
| `table` | SQL (DDL) | DRAFT | None |
| `incremental` | SQL | PUBLISHED | Cron + scheduling params |
| `dynamic_table` | SQL (DDL) | DRAFT | None (auto-refresh) |
| `python` | PYTHON | DRAFT | None (dbt-run managed) |
| `snapshot` | — | Not uploaded | Managed by dbt |
| `seed` | SQL | PUBLISHED | Once, or cron for refresh |

### BigQuery Retail: Full Airflow → Studio Mapping

```
Studio Tasks for retail_pipeline:
  seed_raw_data         (dbt seed, once)
       ↓
  dbt_run_transform     (dbt run --select transform, depends on seed)
       ↓
  dbt_test_transform    (dbt test --select transform, depends on run)
       ↓
  dbt_run_report         (dbt run --select report, depends on test)
       ↓
  dbt_test_report        (dbt test --select report, depends on run)
```

### Migration Checklist

- [ ] `pip install "dbt-clickzetta>=1.7.10"` (add `[python]` or `[databricks]` extras if needed)
- [ ] `profiles.yml`: `type` → `clickzetta`, replace `catalog/host/http_path` or `account/database/warehouse` or `project/method/keyfile` with `instance/workspace/service/vcluster/username/password`
- [ ] `dbt_project.yml`: update `profile:` field only (match profiles.yml target name)
- [ ] Run `dbt deps` — verify packages install successfully
- [ ] Run `dbt seed` — verify seed data loads correctly (use `column_types` for `float8`)
- [ ] Run `dbt run` on a subset first: `dbt run --select tag:smoke_test` or `dbt run --select staging`
- [ ] Fix SQL issues: `col :: type` → `CAST(col AS type)` (Databricks), function name replacements (Snowflake/BigQuery per §10-11), `hash()` → `hash_combine(crc32(...))`, stream macros
- [ ] Remove unsupported configs: `transient`, `merge_exclude_columns`, `indexes`, `on_configuration_change`, `target_lag='DOWNSTREAM'`
- [ ] Run `dbt test` — verify all data quality checks pass
- [ ] Full `dbt run` — verify all models build
- [ ] Run `dbt compile` — generate `manifest.json`
- [ ] Route to `clickzetta-dbt-studio-pipeline` for Studio deployment

### Related Skills

| Scenario | Skill |
|----------|-------|
| dbt project setup (greenfield) | `clickzetta-dbt-project-setup` |
| dbt data modeling (greenfield) | `clickzetta-dbt-modeling` |
| Deploy dbt models as Studio tasks | `clickzetta-dbt-studio-pipeline` |
| Raw SQL migration (Databricks → ClickZetta) | `clickzetta-sql-migration` |
| Raw SQL migration (Snowflake → ClickZetta) | `clickzetta-sql-migration` |
| Function mapping (Snowflake/Spark/Databricks → ClickZetta) | `clickzetta-sql-migration` |
