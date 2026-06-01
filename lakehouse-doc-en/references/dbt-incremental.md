# DBT Incremental Processing in Practice

> The code in this article comes from two directly runnable projects:
> - [clickzetta/jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta) — coffee shop order dataset
> - [clickzetta/snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt) — TPC-H order data warehouse

---

## What Is Incremental Processing

Tables in a data warehouse are typically updated in one of two ways:

- **Full refresh**: Recompute the entire table from scratch each time. Simple and reliable for small datasets, but costly for large ones — a table with 100 million order rows requires scanning all data on every refresh.
- **Incremental processing**: Process only "new or changed" data and merge the results into the existing table. The first run is a full load; subsequent runs process only the incremental data, which is much faster.

dbt's `incremental` materialization is the implementation of incremental processing. Its core logic is:

```
First run (is_incremental() = false) → CREATE TABLE AS SELECT (full load)
Subsequent runs (is_incremental() = true)  → Query only new data, merge into existing table
```

**How does `is_incremental()` determine "first" vs "subsequent"?**

dbt checks whether the target table already exists before running: if it does not exist, it is the first run; if it exists, it is a subsequent run. This means:
- Manually dropping the table and running again triggers a full rebuild
- `dbt run --full-refresh` forces a full rebuild, ignoring the existing table

**Prerequisites for incremental processing**

Incremental processing requires that source data has a way to identify "what is new or changed." Common identification methods:
- **Timestamps**: Fields like `updated_at`, `created_at` that are automatically updated on each change
- **Auto-increment primary key**: New rows always have a larger ID than existing rows
- **Both combined**: Both a timestamp and a primary key, complementing each other

If source data has delete operations but no `updated_at` field, the incremental model cannot detect deletions. In this case, use a full refresh, or switch to Table Stream to capture DELETE events.

The merge strategy is controlled by `incremental_strategy`. Singdata Lakehouse supports 4 strategies.

---

## 4 Incremental Strategies

### merge (default)

Uses a `MERGE INTO` statement, matching on `unique_key`: matched rows are updated, unmatched rows are inserted. Suitable for scenarios with a primary key that need to handle data updates.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id'
) }}

select
    order_id,
    customer_id,
    amount,
    status,
    updated_at
from {{ ref('stg_orders') }}

{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}
```

`{{ this }}` refers to the table corresponding to the current model. `is_incremental()` returns false on the first run and true on subsequent runs.

**Verified data** (from [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta)): 61,948 order rows; the merge strategy takes approximately 20 seconds on the first run.

---

### append

Only performs `INSERT INTO`, without deduplication. Suitable for log-type data — each record is naturally unique, no updates needed, only appending.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

select
    customer_key,
    customer_name,
    account_balance,
    'INSERT'            as cdc_change_type,
    current_timestamp() as cdc_commit_ts
from {{ source('TPC_H', 'CUSTOMER') }}

{% if is_incremental() %}
    TABLESAMPLE SYSTEM(10)
{% endif %}
```

This is the actual implementation of the `customer_cdc_stream` model in [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt) — simulating a CDC data stream where each incremental run samples 10% of the data and appends it, without deduplication.

---

### delete+insert

Deletes matching rows from the target table by `unique_key` first, then inserts the full result set. Suitable for scenarios that need to replace a batch of data by key — for example, backfilling historical partitions, correcting existing data, or when source data has no reliable `updated_at` field but does have a primary key.

> ⚠️ **`unique_key` is required**: `unique_key` is the condition for DELETE. Not setting it will cause a compilation error. Singdata Lakehouse does not support multi-statement execution; the adapter internally splits DELETE and INSERT into two separate API calls.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_id'
) }}

select
    order_id,
    customer_id,
    amount,
    status,
    region,
    dt,
    updated_at
from {{ ref('stg_orders') }}

{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}
```

This is the actual implementation of `fct_orders_delete_insert` in [dbt-clickzetta examples](https://github.com/clickzetta/dbt-clickzetta).

> 💡 **VCluster selection**: For ETL write models (incremental, seed), it is recommended to use the general-purpose cluster (`DEFAULT`). The general-purpose cluster supports automatic small file merging, which is suitable for frequent write scenarios. The analytics cluster (`DEFAULT_AP`) is optimized for large-scale aggregation queries and is not suitable as a compute resource for ETL writes. For per-model VCluster configuration, see [DBT Advanced Features in Practice](dbt-advanced-features.md).

---

### insert_overwrite

`INSERT OVERWRITE` in dynamic partition mode. Suitable for data organized by partition, where only the target partitions are recomputed each time.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'
) }}

select
    dt,
    region,
    count(order_id)  as order_count,
    sum(amount)      as revenue
from {{ ref('stg_orders') }}
where status = 'completed'

{% if is_incremental() %}
and dt >= (select date_sub(max(dt), 3) from {{ this }})
{% endif %}

group by dt, region
```

On incremental runs, only the partitions for the last 3 days are recomputed; historical partitions are untouched. This is the actual implementation of `daily_revenue` in [dbt-clickzetta examples](https://github.com/clickzetta/dbt-clickzetta).

> 💡 **Tip**: The filter condition uses `(select date_sub(max(dt), 3) from {{ this }})`, which looks back 3 days from the maximum date in the target table's existing data, rather than from `current_date()`. This works correctly for historical data backfills — if the latest data in the target table is 2024-01-10, the incremental run recomputes partitions from 2024-01-07 to 2024-01-10, not from today backward.

---

## Strategy Selection

| Strategy | Use Cases | Notes |
|---|---|---|
| `merge` | Has a primary key, needs to handle updates | Requires `unique_key`; source must not have multiple rows for the same key |
| `append` | Logs, event streams — append only, no updates | No deduplication; repeated runs produce duplicate data |
| `delete+insert` | Large data volume where merge performance is poor; replace by partition | Requires `unique_key`; delete then insert, with a brief data gap in between |
| `insert_overwrite` | Data organized by partition, recompute a few partitions each time | Requires `partition_by`; the entire partition is replaced |

---

## Incremental Filter Patterns

The key to incremental processing is: **how to query only "new or changed" data**. Three common patterns:

**Filter by timestamp** (most common):

```sql
{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}
```

**Filter by primary key watermark** (suitable for auto-increment IDs):

```sql
{% if is_incremental() %}
where order_key > (select coalesce(max(order_key), 0) from {{ this }})
{% endif %}
```

**Both combined** (from actual code in [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt)):

```sql
{% if is_incremental() %}
where o_orderdate >= dateadd(day, -{{ var('prune_days') }}, current_date())
   or o_orderkey > (select coalesce(max(o_orderkey), 0) from {{ this }})
{% endif %}
```

`prune_days` is a variable defined in `dbt_project.yml` (default 2), meaning reprocess data from the last N days while also processing new rows with a primary key larger than the current maximum. The two conditions are connected with `OR` to ensure no new data is missed.

---

## Schema Change Handling

When a source table adds a new column, how does the incremental model handle it? This is controlled by `on_schema_change`:

```sql
{{ config(
    materialized='incremental',
    unique_key='o_orderkey',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
) }}
```

| Value | Behavior |
|---|---|
| `ignore` (default) | Ignore new columns, no error |
| `append_new_columns` | Automatically add new columns to the target table; historical data has NULL for those columns |
| `sync_all_columns` | Sync all column changes (add and remove columns) |
| `fail` | Error immediately when there is a schema change |

`append_new_columns` is recommended for production — it neither errors on new columns nor silently loses new column data.

---

## Complete Example: TPC-H Order Incremental Pipeline

The following is the actual incremental pipeline running in [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt), from Bronze layer ingestion to Gold layer dimension table:

**Bronze layer** (`stg_orders_incremental.sql`):

```sql
{{ config(
    materialized='incremental',
    unique_key='o_orderkey',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
) }}

select
    o_orderkey,
    o_custkey,
    o_orderstatus,
    o_totalprice,
    o_orderdate,
    case
        when o_orderstatus = 'O' then 'OPEN'
        when o_orderstatus = 'F' then 'FULFILLED'
        when o_orderstatus = 'P' then 'PARTIAL'
        else 'UNKNOWN'
    end as order_status_desc,
    current_timestamp() as processed_at
from {{ source('TPC_H', 'ORDERS') }}

{% if is_incremental() %}
where o_orderdate >= dateadd(day, -{{ var('prune_days') }}, current_date())
   or o_orderkey > (select coalesce(max(o_orderkey), 0) from {{ this }})
{% endif %}
```

**Gold layer** (`dim_orders.sql`):

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_key',
    alias='DIM_ORDERS'
) }}

with orders_base as (
    select * from {{ ref('stg_orders_incremental') }}
),

customers as (
    select customer_key, customer_name, nation_key
    from {{ ref('dim_customers') }}
    qualify row_number() over (partition by customer_key order by dbt_updated_ts desc) = 1
),

enriched_orders as (
    select
        o.o_orderkey    as order_key,
        o.o_custkey     as customer_key,
        c.customer_name,
        o.order_status_desc,
        o.o_totalprice  as total_price,
        o.o_orderdate   as order_date,
        o.processed_at  as _loaded_at,
        current_timestamp() as _updated_at
    from orders_base o
    left join customers c on o.o_custkey = c.customer_key
)

select * from enriched_orders

{% if is_incremental() %}
where _loaded_at >= (select max(_loaded_at) from {{ this }})
{% endif %}
```

> ⚠️ **Note**: The Gold layer join with `dim_customers` adds `qualify row_number() = 1` for deduplication. This is because `dim_customers` is an SCD model where the same `customer_key` may have multiple historical versions. Without deduplication, this causes an `EXISTS_NONDETERMINISTIC_ROWS` error.

> ⚠️ **NULL value note**: The incremental filter `where _loaded_at >= (select max(_loaded_at) from {{ this }})` has a potential issue — if the target table exists but `_loaded_at` is entirely NULL (e.g., in a historical data migration scenario), `max(_loaded_at)` returns NULL, and `_loaded_at > NULL` is always false, causing the incremental run to process 0 rows. In this case, use `dbt run --full-refresh` to force a full rebuild.

---

## Comparison of Three Incremental Processing Approaches

The `incremental` materialization described in this article is dbt's standard incremental processing approach, requiring manual `dbt run` to trigger. Singdata Lakehouse also supports two other incremental processing approaches for different scenarios:

| Approach | Trigger Mechanism | Use Cases |
|---|---|---|
| `incremental` materialization (this article) | Manual `dbt run` | Need precise control over run timing; integration with scheduling systems |
| Dynamic Table | System auto-refreshes on `refresh_interval` | Need continuous automatic refresh; don't want to manage scheduling |
| Table Stream + incremental | Consumes CDC change stream; each `dbt run` processes new changes | Track row-level changes (INSERT/UPDATE/DELETE) in source tables |

The three approaches can be combined: use Table Stream to capture source table changes → use `incremental` to consume changes → use Dynamic Table to automatically aggregate results.

See [DBT Real-Time Data Pipeline in Practice](dbt-realtime-pipeline.md) for details.

---

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [DBT Real-Time Data Pipeline in Practice](dbt-realtime-pipeline.md)
- [DBT Advanced Features in Practice](dbt-advanced-features.md)
- [dbt-clickzetta GitHub](https://github.com/clickzetta/dbt-clickzetta)
- [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta)
- [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt)
