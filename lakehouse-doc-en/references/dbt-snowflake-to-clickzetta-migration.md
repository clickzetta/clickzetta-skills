# DBT Snowflake Migration in Practice: TPC-H Data Warehouse Pipeline

If you have built a data warehouse pipeline with dbt on Snowflake, the core migration effort to Singdata Lakehouse is concentrated in 6 platform-specific features. Standard SQL models require zero changes.

This article demonstrates the complete migration process using a real migration project: migrating [sfc-gh-dflippo/snowflake-dbt-demo](https://github.com/sfc-gh-dflippo/snowflake-dbt-demo) (a dbt demo project maintained by a Snowflake official engineer) to Singdata Lakehouse. The data source uses the TPC-H standard dataset shared by both platforms. All models have been verified through actual execution — 24/24 passing.

Full code on GitHub: [clickzetta/snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt)

---

## Original Project

[sfc-gh-dflippo/snowflake-dbt-demo](https://github.com/sfc-gh-dflippo/snowflake-dbt-demo) is a dbt feature demonstration project maintained by a Snowflake official engineer. The business scenario is TPC-H customer order analysis: starting from raw order data, processing through Bronze (cleaning) → Silver (aggregation, segmentation) → Gold (dimension tables, metrics) layers, ultimately producing customer value segmentation, order fact tables, calendar dimensions, and other analytical models.

The project covers most of dbt's advanced features on Snowflake: Dynamic Tables, Streams (CDC), Sequences, Python models, Incremental strategies, etc. — making it an ideal subject for validating migration completeness.

The migrated code is in the `03_lakehouse/` directory. The original Snowflake code is preserved in `01_snowflake/` for comparison. Migration notes are in `02_migration/MIGRATION_NOTES.md`.

---

## Conclusion First

**Your dbt project can be migrated; business logic does not need to be rewritten.** This migration made 6 changes, all of which are platform configuration and function name replacements — not a single change touched the data processing logic itself. If your project only uses standard SQL (no Dynamic Tables, Streams, or Sequences), changing `profiles.yml` is all you need.

| Change | Effort | Description |
|---|---|---|
| `profiles.yml` connection config | Very low | Field-by-field replacement, done in 5 minutes |
| Dynamic Table parameter names | Very low | `target_lag` → `refresh_interval`, `snowflake_warehouse` → `refresh_vc` |
| CDC Stream column names | Low | `METADATA$ACTION` → `` `__change_type` ``; use `SELECT * EXCEPT(...)` when consuming |
| Surrogate key | Low | `SEQUENCE .nextval` → `IDENTITY` column or `row_number() over (...)`, note semantic differences (see Step 4) |
| Multi-column hash | Low | `hash()` → `hash_combine(crc32(col), ...)`; requires understanding the Singdata Lakehouse function system |
| Calendar table row generation | Low | `table(generator(...))` → `explode(sequence(...))`, a one-line replacement |

Snowflake-specific configs (`transient`, `merge_exclude_columns`, `copy_grants`) can be deleted directly — Singdata Lakehouse does not support them and does not need them.

---

## Technology Stack Comparison

| | Original Project (Snowflake) | After Migration (Lakehouse) |
|---|---|---|
| dbt adapter | `dbt-snowflake` | `dbt-clickzetta >= 1.7.10` (Python models require `dbt-clickzetta[python] >= 1.7.10`) |
| Compute resource config | `snowflake_warehouse: target.warehouse` | `refresh_vc: default` |
| Dynamic Table refresh schedule | `target_lag: '1 hour'` | `refresh_interval: '1 HOUR'` |
| Config change strategy | `on_configuration_change: apply` | Not supported; use `ALTER DYNAMIC TABLE` |
| Stream change type column | `METADATA$ACTION` | `` `__change_type` `` |
| Stream consumption mode | `SELECT *` | `SELECT * EXCEPT(__change_type, __commit_timestamp, __commit_version)` |
| Surrogate key | `SEQUENCE .nextval` | `IDENTITY` column (at table creation) or `row_number() over (...)` |
| Multi-column hash | `hash(col1, col2, ...)` | `hash_combine(crc32(col1), crc32(col2), ...)` |
| Row generation | `table(generator(rowcount => N))` | `explode(sequence(0, N-1))` |
| Sampling | `sample (10)` | `TABLESAMPLE SYSTEM(10)` |
| Data source | `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1` | `clickzetta_sample_data.tpch_100g` |
| FX rate data | Cybersyn Marketplace (Snowflake-exclusive) | Mock seed CSV (2020–2024, 5 currencies) |

Standard SQL operations — SELECT, JOIN, GROUP BY, window functions, CTE, QUALIFY — have identical syntax and require no changes.

---

## Prerequisites

Requires Python 3.10+ (3.12 recommended) and dbt-clickzetta >= 1.7.10.

```bash
git clone https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt.git
cd snowflake-dbt2lakehouse-dbt

python3 -m venv .venv
source .venv/bin/activate
pip install "dbt-clickzetta[python]>=1.7.10"   # [python] enables Python model support
```

Copy the connection config template and fill in your connection information:

```bash
cp 03_lakehouse/profiles.yml.example ~/.dbt/profiles.yml
```

Key field differences in `profiles.yml`: `account` → `service` (API address), `warehouse` → `vcluster` (compute cluster name). For full field descriptions, see the [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md).

Verify the connection:

```bash
cd 03_lakehouse
dbt debug
```

**Quick validation mode**: TPC-H SF100 data is large (30 million customers, 150 million orders). A full first run takes about 10 minutes. To quickly validate migration correctness, use the `sample_limit` variable to limit the staging layer data volume:

```bash
# Sample 10,000 rows, about 1 minute
bash run.sh --limit 10000

# Full run
bash run.sh --full
```

Or use dbt directly:

```bash
dbt build --vars '{"sample_limit": 10000}'   # sample mode, ~1 minute
dbt build                                     # full mode, ~10 minutes
```

---

## Migration Steps

### Step 1: Data Source Replacement

The original project depends on two Snowflake-exclusive data sources:

**TPC-H data**: `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1` → `clickzetta_sample_data.tpch_100g`

Singdata Lakehouse has a built-in shared dataset — no import needed. Just modify the `schema` in `_sources.yml`:

```yaml
- name: TPC_H
  schema: TPCH_SF1
  database: SNOWFLAKE_SAMPLE_DATA
```

Change to (requires dbt-clickzetta >= 1.7.8):

```yaml
- name: TPC_H
  database: clickzetta_sample_data
  schema: tpch_100g
```

**Cybersyn FX rate data**: Exclusive to Snowflake Marketplace; Singdata Lakehouse has no equivalent data source. The project already provides a mock seed replacement (2020–2024, USD base, 5 currencies, 9,135 rows):

```bash
dbt seed
```

---

### Step 2: Dynamic Table Parameters

Only two parameter names need to be replaced:

```sql
{{ config(
    materialized='dynamic_table',
    snowflake_warehouse=target.warehouse,
    target_lag='1 hour',
    on_configuration_change='apply'
) }}
```

Change to:

```sql
{{ config(
    materialized='dynamic_table',
    refresh_vc='default',
    refresh_interval='1 HOUR'
) }}
```

`on_configuration_change='apply'` can be deleted directly — Singdata Lakehouse does not support it. To modify Dynamic Table configuration, use `ALTER DYNAMIC TABLE` manually.

The original project also has a `target_lag='DOWNSTREAM'` (downstream-triggered refresh). Singdata Lakehouse does not have this concept; change it to an explicit `refresh_interval`:

```sql
{{ config(materialized='dynamic_table', target_lag='DOWNSTREAM') }}
```

Change to:

```sql
{{ config(materialized='dynamic_table', refresh_vc='default', refresh_interval='1 HOUR') }}
```

---

### Step 3: CDC Stream

Snowflake Streams and Singdata Lakehouse Table Streams share the same concept, but differ in creation syntax and system column names:

| | Snowflake Stream | Singdata Lakehouse Table Stream |
|---|---|---|
| Creation syntax | `CREATE STREAM ... ON TABLE t SHOW_INITIAL_ROWS = TRUE` | `CREATE TABLE STREAM ... ON TABLE t WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')` |
| Change type column | `METADATA$ACTION` (INSERT / DELETE) | `` `__change_type` `` (INSERT / UPDATE_BEFORE / UPDATE_AFTER / DELETE) |
| Is UPDATE | `METADATA$ISUPDATE` (boolean) | Determined by `__change_type = 'UPDATE_BEFORE'` |
| Row identifier | `METADATA$ROW_ID` | `__commit_version` |
| Commit time | No direct equivalent | `__commit_timestamp` |

**Recommended pattern for consuming a Stream**: Use `SELECT * EXCEPT(...)` to filter system columns without hardcoding business column names:

```sql
select
    row_number() over (order by `__commit_timestamp`, customer_key) as log_id,
    * except (`__change_type`, `__commit_timestamp`, `__commit_version`),
    `__change_type`      as cdc_change_type,
    `__commit_timestamp` as cdc_commit_ts,
    `__commit_version`   as cdc_version,
    case when `__change_type` = 'DELETE' then 'Y' else 'N' end as delete_flag
from {{ get_table_stream(ref('dim_customers')) }} as d
```

> ⚠️ **Note**: System column names like `__change_type` must be referenced with backticks. Using `SELECT *` without `EXCEPT` will cause a reserved name conflict error.

**Macro to create a Table Stream** (replacing Snowflake's `get_stream()` macro; full code in `03_lakehouse/macros/get_table_stream.sql`):

```sql
{%- macro get_table_stream(table, stream_name=( (this.alias or this.name) ~ "_ts" )) -%}
    {%- set stream_full = this.schema ~ "." ~ stream_name -%}
    {% if execute and flags.WHICH in ('run', 'build') %}
        {%- set stream_create_statement -%}
        create table stream if not exists {{ stream_full }}
        on table {{ table }}
        with properties ('TABLE_STREAM_MODE' = 'STANDARD')
        {%- endset -%}
        {%- do run_query(stream_create_statement) -%}
    {%- endif -%}
    {{ return(stream_full) }}
{%- endmacro -%}
```

---

### Step 4: Surrogate Key

Snowflake uses `SEQUENCE` objects to generate auto-increment surrogate keys. Singdata Lakehouse supports `IDENTITY` auto-increment columns, which are semantically closer:

```sql
{{ sequence_get_nextval() }} as customer_surrogate_key
```

In Singdata Lakehouse, add `identity` directly to the column definition when creating the table:

```sql
id bigint identity
```

However, dbt incremental models cannot directly declare `identity` columns in `config`. You need to create the table via `pre_hook` or use `row_number()` as an alternative. This project uses the `row_number()` approach:

```sql
row_number() over (order by s.customer_key) as customer_surrogate_key
```

> ⚠️ **Note the semantic difference**: `SEQUENCE` and `IDENTITY` are both globally auto-incrementing — the same record always gets the same surrogate key across incremental runs. `row_number()` is computed based on the current query result set; on a full rebuild, row numbers are recomputed, and the same record may get a different value. Therefore, when using `row_number()`, `unique_key` cannot be the surrogate key — it must be changed to the business primary key:

```sql
{{ config(
    materialized='incremental',
    unique_key='integration_id'
) }}
```

Other Snowflake-specific configs that need to be deleted (Singdata Lakehouse does not support them and does not need them):

```sql
transient=false
merge_exclude_columns=[...]
```

---

### Step 5: Multi-Column Hash

Snowflake's `hash()` accepts multiple columns of any type. Singdata Lakehouse uses `hash_combine(crc32(col), ...)` as a replacement:

```sql
hash(c.customer_name, c.customer_address, c.nation_key, ...) as cdc_hash_key
```

Change to:

```sql
hash_combine(
    crc32(coalesce(c.customer_name, '')),
    crc32(coalesce(c.customer_address, '')),
    crc32(coalesce(cast(c.nation_key as varchar), '')),
    ...
) as cdc_hash_key
```

`hash_combine_commutative()` only accepts `bigint` parameters. varchar columns need to be converted to integers using `crc32()` first before combining.

---

### Step 6: Calendar Table Row Generation

Snowflake's `table(generator(rowcount => N))` generates a sequence of N rows. Singdata Lakehouse uses `explode(sequence(0, N-1))` as a replacement:

```sql
select row_number() over (order by seq4()) as day_seq
from table(generator(rowcount => 50 * 365))
```

Change to:

```sql
select date_add(date('1992-01-01'), pos) as day_dt, pos + 1 as day_seq
from (select explode(sequence(0, 50 * 365 - 1)) as pos) t
```

Two date functions also need adjustment: `to_char(date, 'YYYYMMDD')::number(8,0)` changes to `cast(date_format(date, 'yyyyMMdd') as int)`; `last_day(date, 'YEAR')` changes to `date(concat(extract(year from date), '-12-31'))`.

---

### Step 7: Python Model

The original project's `async_bulk_operations.py` deeply depends on Snowflake Stored Procedures (`session.sproc.register`), which Singdata Lakehouse does not support. This model needs to be skipped or redesigned.

The K-means clustering logic in `customer_clustering.py` has been successfully migrated — dbt-clickzetta 1.7.10+ supports Python models, executed via ZettaPark.

**Installation**:
```bash
pip install "dbt-clickzetta[python]>=1.7.10"
```

**Migration key points**:

| Snowflake | Singdata Lakehouse |
|---|---|
| `import snowflake.snowpark as snowpark` | Standard Python; ZettaPark session is compatible |
| `session.sproc.register(...)` | Not supported — remove parallel stored procedure logic |
| `packages=['snowflake-snowpark-python', 'joblib']` | `packages=['scikit-learn', 'pandas', 'numpy']` (auto-installed) |
| `dbt.ref(...).to_pandas()` returns uppercase column names | ZettaPark returns lowercase column names; add `df.columns = df.columns.str.upper()` |

**Usage** (`models/silver/run/customer_clustering.py`):

```python
def model(dbt, session):
    dbt.config(
        materialized="table",
        packages=["scikit-learn", "pandas", "numpy"],  # auto-installed
    )
    customer_df = dbt.ref("customer_segments").to_pandas()
    customer_df.columns = customer_df.columns.str.upper()  # normalize column names
    # ... sklearn KMeans logic ...
    return session.createDataFrame(customer_df)
```

Packages declared in `dbt.config(packages=[...])` are automatically `pip install`ed before the model runs, supported in both local and Studio environments.

---

## End-to-End Verification

`e2e.py` runs 12 automated checks on the migration results, covering the full chain from seed to gold layer:

```bash
python3 e2e.py
```

Actual run results:

```
Done. PASS=27 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=27

  ✓ PASS  fx_rates row count: 9135 rows
  ✓ PASS  stg_customers: 15 million rows (SF100 after dedup)
  ✓ PASS  stg_orders: 150 million rows
  ✓ PASS  stg_orders_incremental: has data
  ✓ PASS  customer_segments: 5 segments (PREMIUM/HIGH_VALUE/STANDARD/BASIC/LOW_VALUE)
  ✓ PASS  fx_rates intermediate: 9135 rows
  ✓ PASS  dim_customers: 30 million rows
  ✓ PASS  dim_orders: has data
  ✓ PASS  dim_calendar_day: 18250 rows (50 years)
  ✓ PASS  customer_insights: no null classifications
  ✓ PASS  customer_cdc_stream: has data
  ✓ PASS  DIM_CUSTOMER_CHANGES: has data

=== Result: 12/12 checks passed ===
```

**12/12 checks passed**.

### Expected Run Time

The first run takes approximately **9-10 minutes** (default minimum-size VCluster). Dynamic Tables require a full refresh on first creation (about 4 minutes) — this is normal behavior, not a hang. Subsequent incremental refreshes take only a few seconds.

---

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [dbt Development in Practice (Table Stream + Dynamic Table)](use-dbt-dev.md)
- [Dynamic Table](dynamic-table.md)
- [Table Stream](table_stream.md)
