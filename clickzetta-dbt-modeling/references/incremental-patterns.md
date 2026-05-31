# Incremental Patterns In Depth

## ClickZetta-Specific Behaviors

Before choosing a strategy, understand these ClickZetta-specific behaviors:

- **Default strategy is `merge`** — if `incremental_strategy` is not set, `merge` is used
- **No temporary tables** — the tmp relation is a view (not a temp table); this is transparent to users but means the tmp view must be dropped after each run
- **`delete+insert` requires two API calls** — ClickZetta does not support multi-statement execution; the adapter splits DELETE and INSERT into two separate calls automatically
- **`on_schema_change` defaults to `ignore`** — new upstream columns are silently dropped; always set `on_schema_change='append_new_columns'` explicitly

## Choosing the Incremental Column

| Column Type | Use Case | Recommended Strategy |
|---|---|---|
| `updated_at` | Has an update timestamp; rows can be modified | `merge` |
| `dt` | Has a business date partition; daily batch processing | `insert_overwrite` |
| `created_at` | Append-only; rows are never modified | `append` |
| None | Small table; full rebuild is simpler | Switch to `table` materialization |

## append Strategy

**What it does**: `INSERT INTO target SELECT ... FROM source`. No deduplication, no deletion.

**Use when**: source data is immutable — logs, events, audit records that are never updated or deleted. Each run appends new rows.

**Warning**: re-running without a proper `is_incremental()` filter will insert duplicates.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='append',
    on_schema_change='append_new_columns'
) }}
select event_id, user_id, event_type, created_at
from {{ source('raw', 'events') }}
{% if is_incremental() %}
where created_at >= (select max(created_at) from {{ this }})
{% endif %}
```

## merge Strategy

**What it does**: `MERGE INTO target USING source ON unique_key` — UPDATE matched rows, INSERT unmatched rows.

**Default strategy** — used when `incremental_strategy` is not specified.

**`unique_key` behavior**:
- If `unique_key` is set: proper MERGE with UPDATE + INSERT
- If `unique_key` is NOT set: adapter warns and falls back to append behavior (INSERT only, no UPDATE). This will cause duplicates on re-runs.

**Use when**: source rows can be updated (order status changes, user profile updates).

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id',              -- single key
    -- unique_key=['order_id', 'dt'],   -- composite key also supported
    on_schema_change='append_new_columns'
) }}
select order_id, customer_id, amount, status, updated_at
from {{ source('raw', 'orders') }}
{% if is_incremental() %}
-- >= not >: prevents missing updates within the same second
where updated_at >= (select max(updated_at) from {{ this }})
-- For late-arriving data, use a lookback window:
-- where updated_at >= (select max(updated_at) from {{ this }}) - interval 3 days
{% endif %}
```

**Optional**: control which columns are updated on match:
```sql
{{ config(
    ...
    merge_update_columns=['status', 'amount', 'updated_at'],  -- only update these columns
    -- merge_exclude_columns=['created_at'],                  -- or exclude these from update
) }}
```

## insert_overwrite Strategy

**What it does**: `INSERT OVERWRITE TABLE target PARTITION(...)` — replaces all data in the matching partitions with new data. Uses `partitionOverwriteMode = DYNAMIC`, so only partitions present in the source data are overwritten.

**`partition_by` is required** — without it, insert_overwrite replaces the entire table.

**No `is_incremental()` filter needed** — the partition itself is the filter. Each run overwrites the current partition(s) from scratch.

**Use when**: daily or hourly aggregations with a date partition, where you want to recompute the entire partition each run.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt',
    on_schema_change='append_new_columns'
) }}
select
    dt,
    region,
    count(*) as order_count,
    sum(amount) as revenue
from {{ source('raw', 'orders') }}
where status = 'completed'
group by dt, region
-- No is_incremental() filter here — the partition is the boundary
-- When published to Studio, inject: WHERE dt = '${bizdate}'
```

## delete+insert Strategy

**What it does**: Step 1 — DELETE rows from target where `unique_key` matches source. Step 2 — INSERT all source rows into target.

**`unique_key` is required** — the adapter raises a compiler error if not set. Without it, there is no DELETE condition.

**ClickZetta note**: executed as two separate API calls (DELETE then INSERT) because ClickZetta does not support multi-statement execution. This is handled automatically by the adapter.

**Use when**: you need to replace a set of rows identified by key, but the logic is more complex than what `merge` handles — e.g. backfilling historical partitions, or when the source data does not have a reliable update timestamp.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_id',
    on_schema_change='append_new_columns'
) }}
select order_id, customer_id, amount, status, dt
from {{ source('raw', 'orders') }}
{% if is_incremental() %}
-- Lookback window: reprocess last 3 days to catch late-arriving corrections
where dt >= current_date() - interval 3 days
{% endif %}
```

## on_schema_change Configuration

**Default is `ignore`** — new upstream columns are silently dropped from the incremental result. This is a common source of data loss that is hard to diagnose.

Always set explicitly:

```sql
{{ config(
    materialized='incremental',
    on_schema_change='append_new_columns'  -- add new columns, keep existing data
    -- on_schema_change='sync_all_columns' -- add new + remove dropped columns (data in dropped cols is lost)
    -- on_schema_change='fail'             -- raise an error if schema changes (safe for strict pipelines)
    -- on_schema_change='ignore'           -- default: silently ignore schema changes
) }}
```

**Recommended**: `append_new_columns` for most cases. Use `fail` when schema stability is critical.

## Incremental Model Debugging

```bash
# Force a full rebuild (wipe and rebuild from scratch)
dbt run --full-refresh --select fct_orders

# Run a single model only
dbt run --select fct_orders

# View the compiled SQL without executing
dbt compile --select fct_orders
cat target/compiled/.../fct_orders.sql
```
