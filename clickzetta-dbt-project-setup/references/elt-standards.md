# ELT Standards Template

## End-to-End Pipeline Architecture

A complete ClickZetta data pipeline has three layers. Each layer has dedicated tools — choose based on the scenario.

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Data Ingestion                                        │
│  External sources → Lakehouse raw schema                        │
│                                                                 │
│  Real-time CDC    Studio sync task (task_type=28/281)           │
│  (seconds)        MySQL/PostgreSQL → Lakehouse via Binlog/WAL   │
│                   Skill: clickzetta-cdc-sync-pipeline           │
│                                                                 │
│  Batch sync       Studio sync task (task_type=10/291)           │
│  (hourly/daily)   Any DB → Lakehouse, cron-scheduled            │
│                   Skill: clickzetta-batch-sync-pipeline         │
│                                                                 │
│  File/stream      SQL Pipe (OSS/S3/COS/Kafka)                   │
│  (continuous)     Auto-ingests new files or messages            │
│                   Skill: clickzetta-oss-ingest-pipeline         │
│                          clickzetta-kafka-ingest-pipeline       │
│                                                                 │
│  One-time import  COPY INTO / file upload                       │
│                   Skill: clickzetta-file-import-pipeline        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ raw schema (ods / bronze / raw)
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Transformation (dbt)                                  │
│  Raw schema → modeled schemas                                   │
│                                                                 │
│  Project setup    profiles.yml + dbt_project.yml                │
│                   Skill: clickzetta-dbt-project-setup           │
│                                                                 │
│  Modeling         sources.yml + model .sql files                │
│                   Dynamic Table (auto-refresh) preferred        │
│                   Incremental (time-window control) when needed │
│                   Skill: clickzetta-dbt-modeling                │
│                                                                 │
│  Layering         Choose one pattern:                           │
│  patterns         • dbt standard: staging → marts               │
│                   • Medallion: bronze → silver → gold           │
│                   • Traditional DW: ODS → DWD → DWS → ADS      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ modeled schemas (marts / gold / ads)
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Publishing & Scheduling (Studio)                      │
│  dbt models → Studio tasks for unified management               │
│                                                                 │
│  Asset mgmt       All models → Studio SQL tasks (DRAFT)         │
│  (all models)     Team can see full pipeline code in Studio     │
│                                                                 │
│  Scheduling       table/incremental/snapshot → PUBLISHED        │
│  (batch models)   Cron + dependencies + bizdate params          │
│                   dynamic_table: skip — self-refreshes          │
│                                                                 │
│                   Skill: clickzetta-dbt-studio-pipeline         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    BI tools / downstream apps
```

### Choosing the ingestion method

| Source | Latency needed | Recommended method |
|---|---|---|
| MySQL / PostgreSQL | Seconds (real-time) | Studio CDC sync (Binlog/WAL) |
| MySQL / PostgreSQL | Hours/days (batch) | Studio batch sync (cron) |
| OSS / S3 / COS files | Minutes (continuous) | SQL Pipe (LIST_PURGE or EVENT mode) |
| Kafka / message queue | Seconds (streaming) | SQL Pipe (READ_KAFKA) |
| Local files / URLs | One-time | COPY INTO |
| Any DB | One-time migration | Studio batch sync (full load) |

### Dynamic Table vs dbt incremental — when to use which

| Scenario | Use | Reason |
|---|---|---|
| Reflect current upstream state | `dynamic_table` | System handles incremental refresh automatically |
| Process only yesterday's data | `incremental` (insert_overwrite) | DT always reflects full current state |
| Run after a specific upstream task | `incremental` | Studio dependency ordering |
| Consume Table Stream (CDC) | `incremental` (merge) | Need to control stream offset advancement |
| SCD Type 2 history | `snapshot` | dbt snapshot handles slowly changing dimensions |

### Scheduling time windows (batch pipeline standard)

```
02:00  Layer 1: Data sync task completes (Studio sync)
02:30  Layer 2a: Raw/staging layer dbt run
03:00  Layer 2b: Core modeling layer dbt run (dwd / silver)
03:30  Layer 2c: Aggregation layer dbt run (dws / gold / marts)
04:00  Layer 3: Data quality checks (DQC)
```

Dynamic Table models do not appear in this schedule — they refresh continuously on their own `refresh_interval`.

---

## Layering Pattern Comparison

| Dimension | dbt standard (staging/marts) | dbt standard + intermediate | Medallion (bronze/silver/gold) | Traditional DW (ODS/DWD/DWS/ADS) |
|---|---|---|---|---|
| Applicable scale | Small to medium projects | Medium projects with complex JOIN logic | Data lakehouse, modern stack | Large data warehouses, traditional teams |
| Team requirements | Familiar with dbt | Familiar with dbt | Familiar with lakehouse concepts | Data warehouse design experience |
| Latency | T+1 or real-time (DT) | T+1 or real-time (DT) | Real-time preferred (silver/gold as DT) | Minute-level (ADS uses DT) |
| Tooling | dbt + Studio | dbt + Studio | dbt + Studio + Dynamic Table | dbt + Studio + Dynamic Table |

**Intermediate layer notes**: When marts models require multi-table JOINs with complex logic, an intermediate layer can be added between staging and marts. Intermediate models:
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
- Use `refresh_interval` to control freshness (e.g. `5 MINUTE`, `30 MINUTE`, `1 HOUR`)

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
