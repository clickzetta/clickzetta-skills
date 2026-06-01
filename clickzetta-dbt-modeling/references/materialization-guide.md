# Materialization Selection Guide

## Core Principle

`dynamic_table` is the default for most models. It uses declarative incremental refresh — the system detects upstream changes and only recomputes what changed. No upstream change = no computation, no cost. It handles T+1 batch, large tables, near-real-time, and most aggregation patterns equally well.

Use a different mechanism only when `dynamic_table` has a **fundamental limitation** for your use case.

## When dynamic_table Cannot Do the Job

### 1. SCD Type 2 — historical version tracking → `snapshot`

Dynamic table always reflects the **current state** of upstream data. When a source row changes, the dynamic table updates in place — the old value is gone. If you need to track "what was the customer's city last month", dynamic_table cannot help.

`snapshot` is the only mechanism that preserves historical versions with `dbt_valid_from` / `dbt_valid_to` timestamps.

```sql
{% snapshot customers_snapshot %}
{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',
    check_cols=['city', 'status']
) }}
select * from {{ source('raw', 'customers') }}
{% endsnapshot %}
```

### 2. Time-windowed processing → `incremental + insert_overwrite`

Dynamic table always reflects the full current state — it cannot produce a view that contains "only yesterday's data". If your downstream model needs to process a specific time window (e.g. daily partition recompute, hourly aggregation), use `incremental + insert_overwrite` with Studio scheduling to inject the time parameter.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt',
    on_schema_change='append_new_columns'
) }}
select dt, region, count(*) as order_count, sum(amount) as revenue
from {{ source('raw', 'orders') }}
where status = 'completed'
group by dt, region
-- Studio injects: WHERE dt = '${bizdate}' at scheduling time
```

### 3. Studio dependency ordering → `incremental + merge/insert_overwrite`

Dynamic table refreshes when upstream data changes, not when a specific upstream task completes. If your model must run **after** a specific Studio task (e.g. after a data sync task finishes loading), use `incremental` with Studio dependency config.

### 4. Change-type routing (INSERT vs DELETE vs UPDATE) → Table Stream + `incremental`

Dynamic table reflects the current state — it cannot distinguish "this row was deleted" from "this row never existed". If you need to route changes by type (e.g. apply inserts to one table, route deletes to an audit log), use a Table Stream as source.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id',
    on_schema_change='append_new_columns'
) }}
select order_id, customer_id, amount, status
from {{ source('raw', 'orders_stream') }}
where __change_type in ('INSERT', 'UPDATE_AFTER')
-- Stream offset advances when this MERGE completes
```

### 5. Append-only guarantee → `incremental + append`

Dynamic table can delete rows if upstream rows are deleted. If you need a table that only ever grows (e.g. an audit log, an event ledger that must never lose records), use `incremental + append`.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}
select event_id, user_id, event_type, created_at
from {{ source('raw', 'events') }}
{% if is_incremental() %}
where created_at >= (select max(created_at) from {{ this }})
{% endif %}
```

### 6. Partition-level backfill / correction → `incremental + delete+insert`

When you need to reprocess and replace a specific partition (e.g. correct yesterday's data after a source fix), `delete+insert` gives explicit control: delete the matching rows, then insert the corrected data.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_id'   -- required: used as DELETE condition
) }}
select ...
{% if is_incremental() %}
where dt >= current_date() - interval 3 days
{% endif %}
```

### 7. Small static reference table → `table`

For lookup/config tables that rarely change and are small enough for full rebuild, `table` is simpler and more predictable than managing a dynamic_table.

## Decision Tree

```
Does dynamic_table have a fundamental limitation for this model?
│
├── Need to preserve historical versions of rows (SCD Type 2)
│   └── snapshot
│
├── Need to process only a specific time window (yesterday, last hour)
│   or must run after a specific upstream Studio task
│   ├── Has date partition → incremental + insert_overwrite
│   └── Has update timestamp → incremental + merge
│
├── Need to route changes by type (INSERT vs DELETE vs UPDATE)
│   └── Table Stream as source + incremental
│
├── Need append-only guarantee (records must never be deleted)
│   └── incremental + append
│
├── Need partition-level backfill / correction
│   └── incremental + delete+insert
│
├── Small static reference table
│   └── table (full rebuild)
│
└── None of the above
    └── dynamic_table (default — handles everything else)
        ├── ODS/staging: refresh_interval='5 MINUTE' or longer
        ├── Dimension tables: refresh_interval='30 MINUTE' or longer
        ├── Fact tables / DWS aggregations: refresh_interval='5 MINUTE'
        └── ADS report tables: refresh_interval='5 MINUTE' or longer
```

## Table Stream Setup

Before using a Table Stream as a dbt source, it must be created (via pre_hook or manually):

```sql
-- Enable change tracking on the source table
ALTER TABLE {schema}.orders SET PROPERTIES ('change_tracking' = 'true');

-- Create the stream (TABLE_STREAM_MODE is required)
CREATE TABLE STREAM {schema}.orders_stream
  ON TABLE {schema}.orders
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

Define it as a dbt source:
```yaml
sources:
  - name: raw
    schema: "{{ target.schema }}"
    tables:
      - name: orders_stream
```

**Key behavior**: SELECT does not advance the stream offset — only DML (INSERT/MERGE) does. Each `dbt run` that executes the MERGE advances the offset, so the next run sees only new changes.


## Studio Scheduling and Dynamic Tables

**Dynamic table with `refresh_interval`**: auto-refreshes on schedule, **no Studio task needed**.
The system manages the refresh independently. Creating a Studio task for it would be redundant.

**Dynamic table with manual refresh** (if `refresh_interval` is disabled or set to manual):
A Studio SQL task can trigger `REFRESH DYNAMIC TABLE {table}` on a schedule.
Use this when you want the refresh to be part of a dependency chain in Studio.

```sql
-- Studio task SQL for manual dynamic table refresh
REFRESH DYNAMIC TABLE {workspace}.{schema}.{model};
```

## Configuration Templates

### dynamic_table — auto-refresh (most common)
```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 MINUTE',  -- '1 MINUTE' / '5 MINUTE' / '1 HOUR'
    refresh_vc='default'
) }}
select
    customer_id,
    count(order_id)  as order_count,
    sum(amount)      as total_amount,
    max(updated_at)  as last_order_time
from {{ ref('stg_orders') }}
group by customer_id
```

### dynamic_table — ODS/staging layer
```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 MINUTE',  -- use longer interval for low-frequency sources
    refresh_vc='default'           -- Note: DOWNSTREAM is not supported in ClickZetta
) }}
select
    order_id,
    customer_id,
    amount,
    status,
    updated_at
from {{ source('raw', 'orders') }}
where order_id is not null
```

### incremental + insert_overwrite (time-windowed daily batch)
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'
) }}
select
    dt,
    region,
    count(*) as order_count,
    sum(amount) as revenue
from {{ source('raw', 'orders') }}
where status = 'completed'
group by dt, region
-- No is_incremental() filter needed; overwrites the current partition each run
```

### incremental + merge (when you need explicit merge control)
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id'
) }}
select ...
{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }}) - interval 3 days
{% endif %}
```
Use this when: you need a lookback window, or the merge logic is more complex than what dynamic_table's automatic incremental can express.

### table (small tables, simplest rebuild)
```sql
{{ config(materialized='table') }}
select ...
```

### snapshot (SCD Type 2)
```sql
{% snapshot customers_snapshot %}
{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='timestamp',
    updated_at='updated_at'
) }}
select * from {{ source('raw', 'customers') }}
{% endsnapshot %}
```

### materialized_view (not recommended)
```sql
{{ config(materialized='materialized_view') }}
select ...
```
> **Not recommended.** Use `dynamic_table` instead — it has explicit refresh configuration and is easier to monitor. Only use `materialized_view` for simple single-table query acceleration where the query optimizer can rewrite automatically.

### clone
```sql
{{ config(
    materialized='clone',
    source='my_schema.fct_orders',
    at_timestamp='2024-01-01 00:00:00'  -- optional, Time Travel to a specific point
) }}
```

## Index Strategy

Indexes are created automatically at table creation time. Selection principles:

| Index Type | Suitable Queries | Typical Columns |
|---|---|---|
| `bloomfilter` | Equality queries (`WHERE order_id = 'xxx'`, `JOIN ON id`) | Primary keys, foreign keys, high-cardinality ID columns |
| `inverted` | Full-text search (`match_all`, `match_any`), low-cardinality enum filtering | status, region, category |

```sql
{{ config(
    materialized='table',
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},
        {'type': 'bloomfilter', 'columns': ['customer_id']},
        {'type': 'inverted',    'columns': ['status']}
    ]
) }}
```

**When to add indexes**: fact table primary/foreign keys → bloomfilter; enum columns in WHERE → inverted; small tables (< 1M rows) → skip.

## Partition Strategy

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'
) }}
```

**When to use**: table has `dt`/`date` column, queries filter by date, row count > 5M or > 100K new rows/day. Not suitable for dimension tables or small tables.

## refresh_interval Selection

| Interval | Use Case | Cost |
|---|---|---|
| `1 MINUTE` | Near-real-time, latency-sensitive | High — VCluster runs continuously |
| `5 MINUTE` | Most scenarios, good default | Moderate |
| `30 MINUTE` | Dimension tables, low-freshness aggregates | Low |
| `1 HOUR` | Very low-freshness, batch-style aggregates | Minimal |

Note: `DOWNSTREAM` is a Snowflake-specific syntax and is **not supported in ClickZetta**. Use a fixed interval instead.

**refresh_vc**: Use `default`, or a dedicated small VCluster to avoid competing with query workloads.
