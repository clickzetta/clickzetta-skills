# ELT Standards Template

## Layering Pattern Comparison

| Dimension | Two-layer (staging/marts) | Two-layer + intermediate (staging/intermediate/marts) | Three-layer (ods/dwd/ads) | Four-layer (ods/dwd/dws/ads) |
|---|---|---|---|---|
| Applicable scale | Small to medium projects | Medium projects with complex JOIN logic | Medium to large projects | Large data warehouses |
| Team requirements | Familiarity with dbt is sufficient | Familiarity with dbt is sufficient | Requires data warehouse design experience | Requires a dedicated data team |
| Latency | T+1 (daily batch) | T+1 (daily batch) | Minute-level (ADS uses DT) | Minute-level |
| Tooling | dbt + Studio | dbt + Studio | dbt + Studio + Dynamic Table | dbt + Studio + Dynamic Table |

**Intermediate layer notes**: When marts models require multi-table JOINs with complex logic, an intermediate layer can be added between staging and marts to handle JOINs and data shaping, preventing marts models from becoming too bloated. Intermediate models:
- Naming convention: `int_{entity}__{verb}.sql` (double underscore separates entity and action, e.g. `int_orders__joined.sql`)
- Materialization: `ephemeral` or `view`, not exposed to BI tools
- Not mandatory — only introduce when JOIN logic in marts spans more than 3 tables

## Naming Conventions

### Schema Naming
```
{prefix}_raw        # Raw data (from sync tasks)
{prefix}_staging    # Staging layer (dbt view)
{prefix}_ods        # Operational data store (dbt table)
{prefix}_dwd        # Detail data warehouse (dbt incremental)
{prefix}_dws        # Summary data warehouse (dbt incremental or Dynamic Table)
{prefix}_ads        # Application data store (Dynamic Table)
{prefix}_marts      # Business marts (used in two-layer pattern)
```

### Table Naming
```
dim_{entity}              # Dimension tables: dim_customers, dim_products
fct_{event}               # Fact tables: fct_orders, fct_pageviews
ods_{source}_{table}      # ODS: ods_mysql_orders, ods_kafka_events
dwd_{domain}_{table}      # DWD: dwd_trade_order_detail
dws_{domain}_{metric}     # DWS: dws_trade_daily_summary
ads_{subject}_{metric}    # ADS: ads_dashboard_gmv
```

### dbt Model File Naming
```
models/
├── staging/
│   ├── stg_{source}_{table}.sql    # stg_orders.sql
│   └── schema.yml
├── marts/
│   ├── dim_{entity}.sql            # dim_customers.sql
│   ├── fct_{event}.sql             # fct_orders.sql
│   └── schema.yml
└── snapshots/
    └── {table}_snapshot.sql        # customers_snapshot.sql
```

## Scheduling Strategy Standards

### What to use Dynamic Table for (preferred default — no Studio task needed)
- ODS/staging layers, dimension tables, fact tables, DWS/ADS aggregations — anything that can be expressed as a SELECT reflecting current upstream state
- The system handles incremental refresh, row updates, and dependency propagation automatically
- Use `refresh_interval` to control freshness (e.g. `5 minutes`, `30 minutes`, `1 hours`)

### What to schedule with dbt + Studio (only when dynamic_table doesn't fit)
- Fully rebuilt dimension tables (`materialized='table'`) — when full rebuild is simpler
- Incremental fact tables (`materialized='incremental'`) — when time-window control is required (yesterday's data only, last hour only)
- Snapshot tables (`materialized='snapshot'`) — SCD Type 2 history tracking

### Scheduling Time Windows (standard)
```
02:00  Data sync task (sync) completes
02:30  staging/ODS layer dbt task
03:00  DWD layer dbt task
03:30  DWS/marts layer dbt task
04:00  Data quality check (DQC)
```

## Incremental Model Standards

### Incremental Field Selection
- Prefer `updated_at` (when an update timestamp is available)
- Fall back to `dt` (when a business date partition is available)
- Last resort: `created_at` (append-only scenarios)

### Incremental Filter Pattern (standard)
```sql
{% if is_incremental() %}
where updated_at >= (select max(updated_at) from {{ this }})
{% endif %}
```

### Partition Incremental Pattern (insert_overwrite)
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by='dt'
) }}
select ...
-- No is_incremental() filter needed — entire partition is overwritten
```

## Data Quality Standards

### Required Tests
```yaml
# schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - not_null
          - unique
      - name: status
        data_tests:
          - accepted_values:
              values: ['completed', 'pending', 'cancelled']
```

### Recommended Singular Tests
- Amount sanity check (must not be negative)
- Key metric range check (daily order count must not be 0)
- Cross-table consistency check (fact table customer_id must exist in the dimension table)
