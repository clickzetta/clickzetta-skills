# Incremental Patterns In Depth

## Principles for Choosing the Incremental Column

| Column Type | Use Case | Notes |
|---|---|---|
| `updated_at` | Has an update timestamp; data can be modified | Most accurate; recommended as first choice |
| `dt` | Has a business date partition; processed daily | Use with insert_overwrite |
| `created_at` | Append-only; data is never modified | Use with append strategy |
| None | Small table; full rebuild is simpler | Switch to table materialization instead |

## append Strategy In Depth

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

select
    event_id,
    user_id,
    event_type,
    created_at
from {{ source('raw', 'events') }}

{% if is_incremental() %}
where created_at >= (select max(created_at) from {{ this }})
{% endif %}
```

**Behavior**:
- Only INSERTs new rows; does not update or delete existing data
- Suitable for: logs, tracking events, immutable append-only data
- Note: re-runs may produce duplicate rows; ensure upstream data is not delivered more than once

## merge Strategy In Depth

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id'    -- single-column primary key
    -- unique_key=['order_id', 'dt']  -- composite primary key
) }}

select
    order_id,
    customer_id,
    amount,
    status,
    updated_at
from {{ source('raw', 'orders') }}

{% if is_incremental() %}
-- >= rather than >: prevents updates within the same second from being missed (timestamp precision issue)
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}

-- If upstream data has late arrivals, a lookback window is safer:
-- where updated_at >= (select max(updated_at) from {{ this }}) - interval 3 days
```

**Behavior**:
- Matches unique_key → UPDATE existing row
- No match → INSERT new row
- Suitable for: order status changes, user profile updates

## insert_overwrite Strategy In Depth

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'        -- overwrite by dt partition
) }}

select
    dt,
    region,
    count(*) as order_count,
    sum(amount) as revenue
from {{ source('raw', 'orders') }}
where status = 'completed'
group by dt, region
-- No is_incremental() filter needed
-- Each run overwrites the current day's partition
```

**Behavior**:
- Deletes all data in the matching partition from the target table
- Re-inserts the newly computed data
- Suitable for: daily summary tables, date-partitioned aggregations

## delete+insert Strategy In Depth

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_id'
) }}

select ...
{% if is_incremental() %}
where dt >= current_date() - interval 3 days  -- 3-day lookback to prevent missing rows
{% endif %}
```

**Behavior**:
- First DELETEs rows matching the unique_key
- Then INSERTs new data
- Suitable for: tables without a primary key that still need replacement, or cases requiring backfill corrections to historical data

## on_schema_change Configuration

```sql
{{ config(
    materialized='incremental',
    on_schema_change='append_new_columns'  -- automatically sync new columns when the source table adds columns
    -- on_schema_change='sync_all_columns'  -- sync all column changes (including dropped columns)
    -- on_schema_change='ignore'            -- ignore schema changes (default)
) }}
```

## Incremental Model Debugging Tips

```bash
# Force a full rebuild (wipe and rebuild from scratch)
dbt run --full-refresh --select fct_orders

# Run a single model only
dbt run --select fct_orders

# View the compiled SQL without executing it
dbt compile --select fct_orders
cat target/compiled/.../fct_orders.sql
```
