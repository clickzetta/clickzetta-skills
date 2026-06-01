# DBT Advanced Features in Practice

> The code in this article comes from [clickzetta/dbt-clickzetta](https://github.com/clickzetta/dbt-clickzetta) (`examples/` directory). All examples have been verified through actual execution.

---

## Indexes

Singdata Lakehouse supports three index types, declared in the `config` block of a dbt model and automatically created after the table is built:

| Index Type | Use Cases | Example Query |
|---|---|---|
| `bloomfilter` | Equality queries (`WHERE col = 'xxx'`) | `WHERE order_id = 'abc123'` |
| `inverted` | Full-text search (`match_all`, `match_any` functions) | `WHERE match_all(status, 'completed')` |
| `vector` | Vector similarity search | `ORDER BY cosine_distance(embedding, [...])` |

**Why do you need indexes?**

Singdata Lakehouse stores data as Parquet files on object storage. Without an index, `WHERE order_id = 'abc123'` requires scanning all rows in all files. A Bloomfilter index maintains a compact probabilistic data structure on each file. At query time, the index is checked first — if it says "this value definitely does not exist in this file," the entire file is skipped, dramatically reducing I/O.

An inverted index is designed for full-text search scenarios. It tokenizes text and builds a word-to-row mapping, so `match_all(col, 'keyword')` can directly locate rows containing the keyword without scanning the entire table.

A vector index is for AI scenarios, supporting approximate nearest neighbor (ANN) search on high-dimensional vectors — orders of magnitude faster than brute-force distance computation across all vectors.

### Bloomfilter + Inverted Index

```sql
{{ config(
    materialized='table',
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},
        {'type': 'bloomfilter', 'columns': ['customer_id']},
        {'type': 'inverted',    'columns': ['status']}
    ]
) }}

select
    order_id,
    customer_id,
    amount,
    status,
    region,
    dt
from {{ ref('stg_orders') }}
```

Each index is a dictionary: `type` specifies the type, `columns` specifies the columns (currently each index supports only a single column). dbt automatically executes `CREATE INDEX` statements after `CREATE TABLE` completes — no manual operation needed.

### Vector Index

```sql
{{ config(
    materialized='table',
    indexes=[
        {
            'type': 'vector',
            'columns': ['embedding'],
            'distance_function': 'cosine_distance',
            'scalar_type': 'f32'
        }
    ]
) }}

select id, embedding
from {{ ref('vector_source') }}
```

A vector index requires additional parameters: `distance_function` (supports `cosine_distance`, `l2_distance`, `dot_product`, etc.) and `scalar_type` (`f32`, `f16`, `b1`).

---

## Clone (Zero-Copy Clone)

Clone is Singdata Lakehouse's zero-copy cloning capability — cloning a table requires no data copying, only metadata copying, making it extremely fast and consuming no additional storage.

**Why zero-copy?**

Singdata Lakehouse uses a storage-compute separation architecture. Data is stored as Parquet files on object storage (OSS/S3/COS), and table metadata (which files belong to this table) is stored in the metadata service. A Clone operation simply creates a new "pointer" at the metadata layer pointing to the same batch of Parquet files — no data files need to be copied. The cloned table and the source table share the underlying files until one of them performs a write operation, at which point new files are created (Copy-on-Write).

This means cloning a 1 TB table takes the same time as cloning a 1 KB table — both are millisecond-level.

### Basic Clone

```sql
{{ config(
    materialized='clone',
    source=target.database ~ '.' ~ target.schema ~ '.fct_orders_partitioned'
) }}
```

`source` specifies the table to clone. `target.database ~ '.' ~ target.schema` is Jinja concatenation of the current connection's database and schema.

**Typical use**: CI/CD environment isolation — quickly clone a production table in a test environment, delete it after testing, without affecting production data.

### Time Travel Clone

Clone to a historical point in time, for recovering from accidental data operations or comparing historical versions:

```sql
{{ config(
    materialized='clone',
    source=target.database ~ '.' ~ target.schema ~ '.fct_orders_partitioned',
    at_timestamp="current_timestamp() - interval 1 hours"
) }}
```

A few notes (from comments in [dbt-clickzetta examples](https://github.com/clickzetta/dbt-clickzetta)):
- The time point must be within the `data_retention_days` retention period (up to 90 days)
- The source table must have existed at that time point
- Timestamps use the server timezone (usually UTC+8)

Common time expressions:
```sql
current_timestamp() - interval 1 hours   -- 1 hour ago
current_timestamp() - interval 1 days    -- 1 day ago
'2024-01-05 15:00:00'                    -- fixed point in time
date_sub(current_date(), 1)              -- yesterday
```

---

## Materialized View

A materialized view pre-computes and physically stores query results, suitable for accelerating high-frequency fixed aggregation queries. The difference from Dynamic Table: materialized views require manual refresh, while Dynamic Tables refresh automatically on a schedule.

```sql
{{ config(materialized='materialized_view') }}

select
    region,
    dt,
    count(order_id)  as order_count,
    sum(amount)      as revenue
from {{ ref('stg_orders') }}
where status = 'completed'
group by region, dt
```

**Selection guidance**:
- Need automatic continuous refresh → use Dynamic Table
- Fixed query pattern, can accept manual refresh → use materialized view
- No physical storage needed, only logical encapsulation → use a regular view

---

## VCluster per-model

Singdata Lakehouse supports assigning a compute cluster to individual models, enabling resource isolation between different types of models:

```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='1 HOUR',
    refresh_vc='default_ap'    -- dynamic_table specific: specifies the cluster for refresh jobs
) }}

select ...
from {{ ref('stg_orders') }}
```

You can also configure by directory in bulk in `dbt_project.yml` (`vcluster` is the general execution cluster; `refresh_vc` is the Dynamic Table-specific refresh cluster):

```yaml
models:
  my_project:
    marts:
      +vcluster: default_ap   # aggregation query models use the analytics cluster
    staging:
      +vcluster: default      # ETL write models use the general-purpose cluster
```

**Cluster type selection**:

| Scenario | Recommended Cluster Type | Reason |
|---|---|---|
| incremental writes, seed | General-purpose (`DEFAULT`) | Supports automatic small file merging, suitable for frequent writes |
| Large-scale aggregation queries, Dynamic Table refresh | Analytics (`DEFAULT_AP`) | Optimized for large-scale scans and aggregations |
| Data sync, CDC | Sync (`PORTAL_SYNC_VC`) | Designed specifically for data integration scenarios |

---

## Grants

dbt supports automatically granting permissions after a model runs, allowing specified roles to query the table:

```sql
{{ config(
    materialized='table',
    grants={
        'select': [var('grant_role', 'workspace_analyst')]
    }
) }}

select
    region,
    count(order_id)  as order_count,
    sum(amount)      as revenue
from {{ ref('stg_orders') }}
where status = 'completed'
group by region
```

`var('grant_role', 'workspace_analyst')` uses a dbt variable, defaulting to granting access to the `workspace_analyst` role. This can be overridden at runtime:

```bash
dbt run --vars '{"grant_role": "my_role"}' --select regional_revenue_with_grants
```

> ⚠️ **Note**: The role names in `grants` must be roles that already exist in the workspace, otherwise `dbt run` will report an error.

---

## Combined Usage Example

The following is a model that combines multiple advanced features:

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_id',
    vcluster='default',       -- ETL writes use the general-purpose cluster
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},
        {'type': 'bloomfilter', 'columns': ['customer_id']},
        {'type': 'inverted',    'columns': ['status']}
    ],
    grants={
        'select': ['workspace_analyst']
    }
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
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

This model:
- Uses the `delete+insert` strategy for incremental updates, running on the general-purpose cluster (`default`)
- Automatically creates bloomfilter and inverted indexes after the table is built
- Automatically grants access to the `workspace_analyst` role after running

---

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [DBT Incremental Processing in Practice](dbt-incremental.md)
- [Index Overview](index-overview.md)
- [Dynamic Table](dynamic-table.md)
- [dbt-clickzetta GitHub](https://github.com/clickzetta/dbt-clickzetta)
