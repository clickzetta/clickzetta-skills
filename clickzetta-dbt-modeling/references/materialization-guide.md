# Materialization Selection Guide

## Core Principle: Dynamic Table as the Default for Declarative SQL Pipelines

Dynamic tables are the **recommended approach for new multi-table SQL pipelines** — you write a SELECT statement, the system handles refresh timing, dependency ordering, and incremental processing automatically. This mirrors Snowflake's design philosophy and applies equally to ClickZetta Lakehouse.

**Use dynamic_table by default** for any model that:
- Is defined purely as a SELECT (no DML needed on the output)
- Reads from upstream tables and transforms/joins/aggregates them
- Does not need to run at a specific clock time (e.g. "after the sync task at 02:00")

**Use incremental or table** only when:
- The output table needs DML (INSERT/UPDATE/DELETE) — e.g. merge by primary key for order status updates
- The model must be triggered by an external event (upstream task completion, not just data change)
- The aggregation is time-windowed and must only include "yesterday's data" (not all history)

## Inference Criteria

When inferring the materialization type, consider the following four dimensions:

| Dimension | How to Obtain | Key Signals |
|---|---|---|
| Table name | Read directly | `orders/events/logs` → fact-type; `customers/products/dim_` → dimension-type; `summary/daily/agg_` → aggregate-type |
| Columns | `table describe` | Has `updated_at` → check if rows are modified (merge needed) or append-only; has `dt/date` → time-windowed aggregation; has primary key → merge/delete+insert |
| Row count | `SELECT COUNT(*)` | < 1M → prefer dynamic_table or table; > 10M with DML needs → incremental |
| Data growth history | `SHOW TABLE HISTORY` or query new rows added in the last 7 days | Rows modified (updated_at changing) → needs merge (incremental); only inserts → dynamic_table or append |

## Decision Tree

```
Does the output table need DML (merge/update/delete by primary key)?
├── YES → incremental (dynamic_table is read-only, cannot do merge)
│   ├── Has unique primary key + rows modified → incremental + merge
│   ├── Has date partition + daily recompute → incremental + insert_overwrite
│   ├── No primary key but has partition → incremental + delete+insert
│   └── Append-only, no modifications → incremental + append
│
└── NO (pure SELECT, no DML needed) → prefer dynamic_table
    ├── ODS / staging layer (rename, cast, filter from raw)
    │   └── → dynamic_table with TARGET_LAG = DOWNSTREAM
    │         (refreshes only when downstream needs it, zero scheduling overhead)
    ├── DWD dimension tables (customers, products, stores — small, JOIN + clean)
    │   └── → dynamic_table (auto-refreshes when source changes)
    ├── DWD fact tables — append-only (events, logs, no status updates)
    │   └── → dynamic_table (append-only facts work well as dynamic tables)
    ├── DWS / ADS aggregation (customer stats, daily revenue, product performance)
    │   ├── No strict time window → dynamic_table (most common case)
    │   └── Must include only "yesterday" data → incremental + insert_overwrite
    │         (dynamic_table would include all history, not just yesterday)
    └── Single-table query acceleration (no joins)
        └── → materialized_view (query optimizer rewrites automatically; dynamic_table not needed)
```

**Special case — DWD fact tables with status updates** (e.g. orders: pending → completed):
- If `updated_at` exists and rows are modified → **incremental + merge** (dynamic_table cannot merge)
- If rows are append-only (events, logs) → **dynamic_table**

**TARGET_LAG = DOWNSTREAM pattern** for intermediate tables:
```sql
{{ config(
    materialized='dynamic_table',
    target_lag='DOWNSTREAM',   -- only refresh when downstream tables need it
    refresh_vc='default_ap'
) }}
```
Use this for ODS/staging layers — they don't need their own refresh schedule, they just need to be ready when DWS/ADS tables refresh.

**When NOT to use dynamic_table** (Snowflake/ClickZetta official guidance):
- Output needs DML (INSERT/UPDATE/DELETE/TRUNCATE) → use incremental
- Must run after a specific upstream task completes (not just when data changes) → use incremental + Studio scheduling
- Simple single-table query with no joins → use materialized_view (more efficient)
- SCD Type 2 (need to track historical versions of dimension rows) → use snapshot

## Configuration Templates by Type

### table
```sql
{{ config(materialized='table') }}
select ...
```

### incremental + merge
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id'
) }}
select ...
{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

### incremental + insert_overwrite
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'
) }}
select ...
-- No is_incremental() filter needed; overwrites the entire partition each run
```

### dynamic_table
```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 minutes',
    refresh_vc='default_ap'
) }}
select
    customer_id,
    count(*) as order_count,
    sum(amount) as total_amount
from {{ ref('fct_orders') }}
group by customer_id
```

### snapshot (timestamp strategy)
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

### snapshot (check strategy)
```sql
{% snapshot customers_snapshot %}
{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',
    check_cols=['name', 'email', 'city']
) }}
select * from {{ source('raw', 'customers') }}
{% endsnapshot %}
```

### materialized_view (not recommended)
```sql
{{ config(materialized='materialized_view') }}
select ...
```
> **Not recommended.** Prefer `dynamic_table` for the same use case — dynamic tables have explicit refresh intervals and VCluster configuration, making behavior more predictable and easier to monitor. Only consider `materialized_view` when there is a specific reason.

### clone
```sql
{{ config(
    materialized='clone',
    source='my_schema.fct_orders',
    at_timestamp='2024-01-01 00:00:00'  -- optional, Time Travel to a specific point in time
) }}
```
> Zero-copy clone, no data is copied. Suitable for creating test replicas or Time Travel snapshots.

### partition + index
```sql
{{ config(
    materialized='table',
    partition_by='dt',
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},
        {'type': 'inverted', 'columns': ['status']}
    ]
) }}
```

### VCluster isolation (large models use large clusters)
```sql
{{ config(
    materialized='table',
    vcluster='large_ap'
) }}
```

## Index Strategy

Indexes are created automatically at table creation time — no extra steps needed. Selection principles:

| Index Type | Suitable Queries | Typical Columns |
|---|---|---|
| `bloomfilter` | Equality queries (`WHERE order_id = 'xxx'`, `JOIN ON id`) | Primary keys, foreign keys, high-cardinality ID columns |
| `inverted` | Full-text search (`match_all`, `match_any`), low-cardinality enum filtering | status, region, category and other enum columns |

```sql
{{ config(
    materialized='table',
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},    -- primary key equality queries
        {'type': 'bloomfilter', 'columns': ['customer_id']}, -- foreign key JOIN acceleration
        {'type': 'inverted',    'columns': ['status']}       -- enum filtering
    ]
) }}
```

**When to add indexes**:
- Fact table primary key and foreign key columns: add bloomfilter by default
- Enum columns that frequently appear in WHERE conditions: add inverted
- Small tables (< 1M rows): no index needed, full table scan is faster

## Partition Strategy

Partitioning lets queries scan only relevant partitions, significantly reducing IO. Suitable for large tables with a clear date dimension:

```sql
{{ config(
    materialized='table',
    partition_by='dt'    -- partition by dt column; queries automatically prune partitions
) }}
select
    order_id,
    customer_id,
    amount,
    dt
from {{ ref('stg_orders') }}
```

**Partition + incremental combination** (the most common pattern for large tables):
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'    -- overwrites the current day's partition each run; no is_incremental() filter needed
) }}
```

**When to use partitioning**:
- Table has a `dt` / `date` column and queries frequently filter by date
- Row count > 5M, or > 100K new rows added per day
- Not suitable for: dimension tables without a date column, small tables

## Dynamic Table Configuration Details

```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 minutes',  -- refresh interval: '1 minutes' / '5 minutes' / '1 hours' etc.
    refresh_vc='default_ap'        -- VCluster used for refresh; recommended to separate from query VCluster
) }}
select
    customer_id,
    count(order_id)  as order_count,
    sum(amount)      as total_amount,
    max(updated_at)  as last_order_time
from {{ ref('stg_orders') }}
group by customer_id
```

**Choosing refresh_interval**:
- `1 minutes`: near-real-time scenarios; VCluster consumes resources continuously, higher cost
- `5 minutes`: a reasonable default for most near-real-time scenarios
- `1 hours`: aggregate metrics where freshness requirements are low

**refresh_vc recommendation**: Use a dedicated small VCluster for refresh to avoid competing with the query VCluster for resources. If no dedicated VCluster is available, use `default_ap`.
