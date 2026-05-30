# Materialization Selection Guide

## Core Principle: Two Paradigms of Incremental Computation

There are two fundamentally different ways to keep a table up to date:

**Declarative (dynamic_table)**: You declare *what the table should contain* as a SELECT statement. The system automatically detects upstream changes and incrementally recomputes the result — inserts, updates, and deletes in the source are all reflected automatically. You never write incremental filter logic. The system handles it.

**Imperative (incremental)**: You write *how to process each batch* — which rows to pick up (`WHERE updated_at >= ...`), how to merge them (`merge`/`insert_overwrite`/`append`). You control the logic; the system just executes it on schedule.

**The key question is not "does it need DML" — dynamic_table handles row-level changes automatically through declarative incremental refresh. The key question is: do you need to control the time window of data being processed?**

- **No time window control needed** → `dynamic_table` (system keeps it fresh automatically)
- **Must process only a specific window** (e.g. "yesterday's data only", "last hour only") → `incremental`
- **Must run after a specific upstream task** (not just when data changes) → `incremental` + Studio scheduling

## Decision Tree

```
Can this model be fully expressed as a SELECT that should always reflect
the current state of its upstream tables?
│
├── YES → dynamic_table (declarative incremental, system handles everything)
│   │
│   ├── ODS / staging (rename, cast, filter from raw)
│   │   └── refresh_interval='5 minutes' or longer — low-frequency source can use longer intervals
│   │
│   ├── DWD dimension tables (customers, products, stores)
│   │   └── refresh_interval='5 minutes' or longer — auto-tracks source changes
│   │
│   ├── DWD fact tables (orders, events — including those with status updates)
│   │   └── dynamic_table handles row updates automatically; no merge logic needed
│   │
│   ├── DWS / ADS aggregation (customer stats, daily revenue, product performance)
│   │   └── dynamic_table — aggregates stay current as upstream facts change
│   │
│   └── Single-table query acceleration (no joins, no transforms)
│       └── materialized_view is more efficient (query optimizer rewrites automatically)
│
└── NO → incremental or table
    │
    ├── Must process only a specific time window
    │   ├── Daily partition recompute (dt field) → incremental + insert_overwrite
    │   └── Hourly window (start_time / end_time) → incremental + insert_overwrite
    │
    ├── Must run after a specific upstream Studio task completes
    │   └── incremental + Studio scheduling + dependency config
    │
    ├── SCD Type 2 (track historical versions of dimension rows)
    │   └── snapshot
    │
    └── Small table, simplest possible rebuild
        └── table (full rebuild each run)
```

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
    refresh_interval='5 minutes',  -- '1 minutes' / '5 minutes' / '1 hours'
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
    refresh_interval='5 minutes',  -- use longer interval for low-frequency sources
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
| `1 minutes` | Near-real-time, latency-sensitive | High — VCluster runs continuously |
| `5 minutes` | Most scenarios, good default | Moderate |
| `30 minutes` | Dimension tables, low-freshness aggregates | Low |
| `1 hours` | Very low-freshness, batch-style aggregates | Minimal |

Note: `DOWNSTREAM` is a Snowflake-specific syntax and is **not supported in ClickZetta**. Use a fixed interval instead.

**refresh_vc**: Use `default`, or a dedicated small VCluster to avoid competing with query workloads.
