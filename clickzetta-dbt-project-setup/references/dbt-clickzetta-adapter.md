# dbt-clickzetta Adapter Capability Reference

## Supported Materialization Types

| Type | Use Case | Key Configuration |
|---|---|---|
| `table` | Dimension tables, small tables, full rebuild | No special config |
| `view` | Lightweight staging layer, no data storage | No special config |
| `incremental` | Fact tables, large tables, incremental updates | `unique_key`, `incremental_strategy` |
| `snapshot` | Slowly changing dimensions (SCD Type 2) | `unique_key`, `strategy`, `updated_at` |
| `dynamic_table` | Real-time aggregation, auto-refresh, pre-computed query acceleration (preferred over materialized_view) | `refresh_interval`, `refresh_vc` |
| `materialized_view` | Not recommended — use dynamic_table instead for the same use case | No special config |
| `clone` | Zero-copy clone, Time Travel | `source`, `at_timestamp` |
| `ephemeral` | Intermediate computation, not materialized | No special config |

## Incremental Strategies (incremental_strategy)

| Strategy | Use Case | Required Parameters |
|---|---|---|
| `merge` (default) | Has primary key, needs to update historical records | `unique_key` |
| `append` | Append-only, log-type data | None |
| `insert_overwrite` | Full partition overwrite, daily recalculated summaries | `partition_by` |
| `delete+insert` | Partition replacement without primary key | `unique_key` |

## Advanced Features

### Indexes
```sql
{{ config(
    materialized='table',
    indexes=[
        {'type': 'bloomfilter', 'columns': ['order_id']},
        {'type': 'inverted', 'columns': ['status'], 'analyzer': 'unicode'},
        {'type': 'vector', 'columns': ['embedding'], 'distance_function': 'cosine_distance'}
    ]
) }}
```

### VCluster Isolation
```sql
{{ config(materialized='table', vcluster='large_ap') }}
```

### Permission Grants
```sql
{{ config(
    materialized='table',
    grants={'select': ['workspace_analyst']}
) }}
```

### Table Stream as Source
```yaml
# sources.yml
sources:
  - name: streams
    database: "{{ target.database }}"
    schema: "{{ target.schema }}"
    tables:
      - name: orders_stream
```
System columns: `__change_type`, `__commit_version`, `__commit_timestamp`
Use `SELECT * EXCEPT(__change_type, ...)` to filter out system columns when querying.

## Standard Test Command Sequence

```bash
# Full test workflow (all must pass before release)
dbt seed --profiles-dir . --full-refresh   # Load test data
dbt run --profiles-dir .                   # Build all models
dbt snapshot --profiles-dir .              # Build snapshots
dbt test --profiles-dir .                  # Run all tests
```

## Useful run-operations

```bash
# Merge small files
dbt run-operation optimize_table --args '{relation: schema.table}'

# View recoverable deleted objects
dbt run-operation show_tables_history --args '{schema: my_schema}'

# Restore accidentally deleted objects
dbt run-operation undrop --args '{relation: schema.table}'

# Manually refresh a dynamic table
dbt run-operation refresh_dynamic_table --args '{model_name: my_dt}'
```

## Connection Parameters

| Parameter | Description | Example |
|---|---|---|
| `service` | API endpoint | `cn-shanghai-alicloud.api.clickzetta.com` |
| `instance` | Instance ID | `f8866243` |
| `workspace` | Workspace (= dbt database) | `quick_start` |
| `schema` | Default write schema | `my_marts` |
| `vcluster` | Compute cluster | `default_ap` |

> `workspace` maps to dbt's `database`, and `{{ this }}` renders as `workspace.schema.table`
