# DBT ClickZetta Adapter Usage Guide

> 💡 **If you are using dbt to perform data transformation and modeling on Singdata Lakehouse**, Singdata Studio provides native development, orchestration, and operations capabilities — no need to maintain a separate dbt project:
>
> **Step 1: Develop transformation logic in Studio SQL tasks**
>
> [Studio SQL tasks](../task-develop.md) are Singdata's native data modeling approach, supporting SQL authoring and scheduled execution in an IDE. Choose the appropriate object type based on your transformation scenario:
>
> | Scenario | Object Type | Description |
> |------|---------|------|
> | Transformation logic requiring automatic incremental refresh | [Dynamic Table](../dynamic-table.md) | Declaratively define transformation SQL; the system automatically computes incrementally without manual scheduling logic |
> | Accelerating high-frequency fixed aggregation queries | [Materialized View](../materializedview.md) | Pre-computed results stored physically; BI queries hit directly |
> | Standard SQL ETL logic | Regular table + INSERT/MERGE | Standard SQL writes with flexible execution control |
>
> **Step 2: Orchestrate multiple SQL tasks into a workflow**
>
> Multiple SQL tasks can be combined into a [workflow (DAG)](../composite_task.md), defining dependencies between tasks for unified scheduling.
>
> **Step 3: Scheduling, monitoring, and operations**
>
> Studio has a built-in scheduling system supporting cron triggers, task dependencies, failure alerts, run log viewing, and failure reruns. See [Using Studio In Depth](../studio_manual.md).
>
> If you have an existing dbt project to migrate, or your team prefers the dbt development workflow, continue reading the integration guide below.

---

## Installation

Requires Python 3.10+ (3.12 recommended) and dbt-core 1.8+.

```bash
pip install "dbt-clickzetta>=1.7.8"
```

## Connection Configuration

Configure connection details in `profiles.yml`:

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: clickzetta
      service: cn-shanghai-alicloud.api.clickzetta.com
      instance: your_instance
      workspace: your_workspace
      username: your_username
      password: your_password
      schema: your_schema
      vcluster: default
```

| Parameter | Required | Description |
|------|------|------|
| `type` | Yes | Fixed as `clickzetta` |
| `service` | Yes | API address, e.g., `cn-shanghai-alicloud.api.clickzetta.com` |
| `instance` | Yes | Instance name |
| `workspace` | Yes | Workspace name |
| `username` | Yes | Username |
| `password` | Yes | Password |
| `schema` | Yes | Default schema name |
| `vcluster` | Yes | Compute cluster name, e.g., `default` |
| `connect_retries` | No | Connection retry count, default 3 |

Verify the connection:

```bash
dbt debug
```

---

## Supported Features

| Feature | Support |
|------|---------|
| `table` materialization | ✅ |
| `view` materialization | ✅ |
| `incremental` materialization | ✅ |
| `ephemeral` materialization | ✅ |
| `snapshot` (SCD Type 2) | ✅ |
| `dynamic_table` materialization | ✅ |
| `materialized_view` materialization | ✅ |
| `dbt test` (generic + singular) | ✅ |
| `dbt seed` | ✅ |
| `dbt docs generate` | ✅ (includes row count, size, last modified time) |
| `dbt source freshness` | ✅ |
| `persist_docs` (relation + columns) | ✅ |
| Partitioned tables | ✅ |
| Bucketed tables | ✅ |
| Python models | ❌ Not supported; SQL models only |
| `on_schema_change` | ✅ (append_new_columns, sync_all_columns) |
| `grants` | ✅ |
| `clone` materialization | ✅ (zero-copy clone + Time Travel clone) |
| Indexes (Bloomfilter / Inverted / Vector) | ✅ (auto-created via `indexes` config) |
| Table Stream as source | ✅ (declared in `sources.yml`, referenced via `source()`) |
| VCluster per-model | ✅ (via `vcluster` config) |

---

## Incremental Strategies

Four incremental strategies are supported:

| Strategy | Description |
|------|------|
| `merge` (default) | MERGE INTO, requires `unique_key` |
| `append` | INSERT INTO, no deduplication |
| `insert_overwrite` | INSERT OVERWRITE, dynamic partition mode |
| `delete+insert` | Delete matching rows by `unique_key` first, then insert (`unique_key` required) |

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='id'
) }}

select * from {{ ref('stg_orders') }}
{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}
```

---

## Dynamic Table

Dynamic Table automatically refreshes incrementally at `refresh_interval` without external scheduling:

```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 MINUTE',
    refresh_vc='default'
) }}

select
    customer_id,
    count(order_id)  as order_count,
    sum(amount)      as total_amount
from {{ ref('stg_orders') }}
group by customer_id
```

Manually trigger an immediate refresh:

```bash
dbt run-operation refresh_dynamic_table --args '{model_name: my_dynamic_table}'
```

---

## Indexes

Indexes are automatically created when building tables. Three types are supported: Bloomfilter (equality queries), Inverted (full-text search), and Vector (similarity search):

```sql
{{ config(
    materialized='table',
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},
        {'type': 'inverted',    'columns': ['status'], 'analyzer': 'unicode'},
        {'type': 'vector',      'columns': ['embedding'],
         'distance_function': 'cosine_distance', 'scalar_type': 'f32'}
    ]
) }}
```

---

## VCluster per-model

Specify a compute cluster for individual models to isolate resources between large and small models:

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_id',
    vcluster='large_ap'
) }}
```

You can also configure by directory in `dbt_project.yml`:

```yaml
models:
  my_project:
    marts:
      +vcluster: large_ap
    staging:
      +vcluster: default_ap
```

---

## Table Stream as Source

Declare a Table Stream in `sources.yml` and reference it with `source()` in models to consume CDC change data:

```yaml
sources:
  - name: my_streams
    schema: my_schema
    tables:
      - name: orders_stream
```

```sql
{{ config(materialized='incremental', incremental_strategy='append') }}

select
    `__change_type`      as cdc_change_type,
    `__commit_timestamp` as cdc_commit_ts,
    order_id, customer_id, amount
from {{ source('my_streams', 'orders_stream') }}
```

> ⚠️ **Note**: `__change_type`, `__commit_timestamp`, and `__commit_version` are Table Stream system columns and must be wrapped in backticks when referenced. When consuming, it is recommended to use `SELECT * EXCEPT(__change_type, __commit_timestamp, __commit_version)` to filter out system columns.

---

## Clone

Zero-copy clone, suitable for CI/CD environment isolation or quickly creating test copies:

```sql
{{ config(
    materialized='clone',
    source='my_schema.fct_orders'
) }}
```

Time Travel clone (restore to a historical point in time):

```sql
{{ config(
    materialized='clone',
    source='my_schema.fct_orders',
    at_timestamp="current_timestamp() - interval 1 hours"
) }}
```

---

## Snapshot (SCD Type 2)

Implements SCD Type 2 via MERGE INTO, without requiring Delta/Iceberg:

```sql
{% snapshot orders_snapshot %}
{{ config(
    target_schema='snapshots',
    unique_key='order_id',
    strategy='timestamp',
    updated_at='updated_at'
) }}
select * from {{ source('raw', 'orders') }}
{% endsnapshot %}
```

---

## Utility Macros

Call built-in macros via `dbt run-operation`:

```bash
# Compact small files (use after high-frequency incremental writes)
dbt run-operation optimize_table --args '{relation: my_schema.my_table}'
dbt run-operation optimize_table --args '{relation: my_schema.my_table, where: "dt >= current_date() - interval 7 days"}'

# Switch the current session's VCluster
dbt run-operation use_vcluster --args '{vcluster: large_ap}'

# View recoverable deleted objects
dbt run-operation show_tables_history --args '{schema: my_schema}'

# Recover a deleted object (table / dynamic_table / materialized_view / stream)
dbt run-operation undrop --args '{relation: my_schema.my_table}'

# Drop an object
dbt run-operation drop_object --args '{relation: my_schema.my_table, type: table}'

# Manually refresh a Dynamic Table
dbt run-operation refresh_dynamic_table --args '{model_name: my_dynamic_table}'
```

---

## Related Documentation

- [dbt Quick Start (Jaffle Shop)](dbt-jaffle-shop-quickstart.md)
- [dbt Development in Practice (Table Stream + Dynamic Table)](../use-dbt-dev.md)
- [dbt Snowflake Migration Guide](../dbt-snowflake-to-clickzetta-migration.md)
- [Dynamic Table](../dynamic-table.md)
- [Table Stream](../table_stream.md)
- [dbt-clickzetta GitHub](https://github.com/clickzetta/dbt-clickzetta)
