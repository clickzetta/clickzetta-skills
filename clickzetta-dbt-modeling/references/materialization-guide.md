# Materialization Selection Guide

## Inference Criteria

When inferring the materialization type, consider the following four dimensions:

| Dimension | How to Obtain | Key Signals |
|---|---|---|
| Table name | Read directly | `orders/events/logs` → fact-type; `customers/products/dim_` → dimension-type; `summary/daily/agg_` → aggregate-type |
| Columns | `table describe` | Has `updated_at` → merge incremental; has `dt/date` → insert_overwrite; has `created_at` but no `updated_at` → append; has primary key column → merge/delete+insert |
| Row count | `SELECT COUNT(*)` | < 1M → prefer table; > 10M → must use incremental |
| Data growth history | `SHOW TABLE HISTORY` or query new rows added in the last 7 days | Steady daily growth → incremental; very little or no growth → table; growth with backfill modifications → merge instead of append |

**Growth history decision logic**:
- Last 7 days: > 10K new rows per day → likely needs incremental, avoid costly full rebuilds
- Last 7 days: historical rows modified (updated_at changing) → needs merge, cannot use append
- Last 7 days: only inserts, no modifications → can use append, simpler and more efficient
- Small data volume but daily modifications → still use table (full rebuild is simpler than merge, and small size has no performance impact)

## Decision Tree

```
Combine table name + columns + row count + growth history:
├── Row count < 1M, or very slow growth (< 10K new rows/day)
│   ├── Historical rows changing (updated_at is changing) → table (full rebuild, simple and reliable)
│   └── No changes or append-only → table
├── Row count > 1M, or steady daily growth
│   ├── Has unique primary key + historical rows modified (updated_at changing) → incremental + merge
│   ├── Has date partition column (dt/date) + daily recompute → incremental + insert_overwrite
│   ├── No primary key but has partition, needs replacement → incremental + delete+insert
│   └── Append-only, no modifications (logs/events) → incremental + append
├── Aggregate / summary model (DWS/ADS layer: customer stats, daily revenue, product performance, etc.)
│   ├── No strict scheduling time window needed → dynamic_table (preferred — auto-refresh, no Studio task needed)
│   └── Must run at a specific time (e.g. after upstream sync completes) → incremental + insert_overwrite
├── Columns have SCD characteristics (name/city/status and other changing dimension attributes)
│   └── → snapshot (SCD Type 2)
├── Pre-computed query acceleration (read-only, high-frequency queries)
│   └── → dynamic_table (preferred, auto-refresh, no scheduling needed; materialized_view not recommended)
├── Zero-copy clone or Time Travel snapshot
│   └── → clone (source points to original table, at_timestamp specifies the point in time)
└── Intermediate computation, no materialization needed
    └── → ephemeral
```

**When to choose dynamic_table for aggregation models**:
- Customer stats, product performance, store rankings, daily/weekly summaries — these are all good candidates
- dynamic_table auto-refreshes when upstream data changes, no cron needed
- Only use incremental/table for aggregation when: (1) the aggregation window is time-bounded (e.g. "yesterday only"), or (2) the model must run after a specific upstream task completes

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
