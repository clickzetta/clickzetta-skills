# Snowflake Dynamic Tables Migration in Practice: Bronze–Silver–Gold Pipeline

If you have built a Medallion data pipeline on Snowflake using Dynamic Tables, migrating to Singdata Lakehouse involves mainly 4 syntax differences. The core SQL query logic does not need to change.

This article demonstrates the complete migration process with a real project: migrating a Bronze–Silver–Gold three-layer pipeline based on Snowflake Dynamic Tables to Singdata Lakehouse, using the TPC-H standard dataset available on both platforms. All SQL has been validated with cz-cli.

Full code: [snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables)

---

## Original Project

[snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables) is adapted from [Techy-Malay/snowflake-bsg-dynamic-tables](https://github.com/Techy-Malay/snowflake-bsg-dynamic-tables), demonstrating how to implement a Bronze–Silver–Gold architecture on Snowflake using Dynamic Tables. The project uses the TPC-H ORDERS table as the data source and outputs a daily sales summary after three layers of Dynamic Table processing.

The migrated code is in the `03_lakehouse/` directory; the original Snowflake SQL is preserved in `01_snowflake/` for comparison.

## Conclusion First

**The core SQL query logic does not need to change.** All 4 changes are platform configuration replacements: `TARGET_LAG` → `REFRESH INTERVAL`, `WAREHOUSE` → `VCLUSTER`, `DATA_RETENTION_TIME_IN_DAYS` moved to a separate post-creation statement, and `DOWNSTREAM` cascade refresh replaced with independent per-layer intervals.

| Change | Effort | Notes |
|---|---|---|
| Dynamic Table refresh parameters | Very low | `TARGET_LAG` → `REFRESH INTERVAL`, `WAREHOUSE` → `VCLUSTER` |
| DOWNSTREAM cascade refresh | Low | Singdata Lakehouse has no such concept; each layer sets its own `REFRESH INTERVAL` independently |
| Time Travel retention | Very low | Moved from inline CREATE TABLE option to post-creation `ALTER TABLE SET PROPERTIES` |
| Data source reference | Very low | `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1` → `clickzetta_sample_data.tpch_100g` |

Cleaning, deduplication (QUALIFY), aggregation, date truncation — the core SQL logic syntax is identical and requires no changes.

---

## Technology Stack Comparison

| | Original (Snowflake) | After Migration (Lakehouse) |
|---|---|---|
| Compute resource | `WAREHOUSE = compute_wh` | `VCLUSTER default` |
| Refresh strategy | `TARGET_LAG = '5 minutes'` | `REFRESH INTERVAL '5' MINUTE` |
| Dependency propagation | `TARGET_LAG = 'DOWNSTREAM'` (auto cascade) | No such concept; each layer refreshes independently |
| Manual refresh | `ALTER DYNAMIC TABLE ... REFRESH` | `REFRESH DYNAMIC TABLE ...` |
| Time Travel retention | `DATA_RETENTION_TIME_IN_DAYS = 1` (inline CREATE TABLE option) | `ALTER TABLE ... SET PROPERTIES ('data_retention_days' = '1')` (separate post-creation statement) |
| Sample dataset | `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS` (1GB) | `clickzetta_sample_data.tpch_100g.orders` (100GB) |
| Schema reference | `USE SCHEMA` + unqualified name, or fully qualified name | Same; both forms supported |
| Deduplication syntax | `QUALIFY ROW_NUMBER() OVER (...) = 1` | Same syntax, fully supported |
| Date truncation | `DATE_TRUNC('day', ts)` | Same syntax, fully supported |

The main changes are platform configuration — replacing Snowflake Virtual Warehouse with Lakehouse VCluster, and `TARGET_LAG` with `REFRESH INTERVAL`. The core SQL logic for data processing is completely unchanged: cleaning, deduplication, aggregation — these are written identically on Lakehouse as on Snowflake.

---

## Architecture Overview

```
SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS          clickzetta_sample_data.tpch_100g.orders
(Snowflake built-in sample dataset, 1GB)        (Lakehouse shared dataset, 100GB)
              │                                               │
              ▼                                               ▼
         ORDERS_STG                                    orders_stg
    DATA_RETENTION_TIME_IN_DAYS = 1            SET PROPERTIES ('data_retention_days' = '1')
              │                                               │
              ▼  TARGET_LAG = '5 minutes'                     ▼  REFRESH INTERVAL '5' MINUTE
         bronze_orders                                 bronze_orders
    (raw data + ingestion metadata)                (raw data + ingestion metadata)
              │                                               │
              ▼  TARGET_LAG = '5 minutes' + QUALIFY           ▼  REFRESH INTERVAL '5' MINUTE + QUALIFY
         silver_orders                                 silver_orders
    (cleaned, deduplicated, type-normalized)       (cleaned, deduplicated, type-normalized)
              │                                               │
              ▼  TARGET_LAG = '10 minutes'                    ▼  REFRESH INTERVAL '10' MINUTE
         gold_sales_summary                            gold_sales_summary
    (daily sales summary for analytics)            (daily sales summary for analytics)
```

---

![](.topwrite/assets/anim-08-snowflake-dt-migration.svg)

---

## Migration Steps

### Step 1: Replace Sample Dataset Reference

Snowflake's built-in sample data is accessed via the `SNOWFLAKE_SAMPLE_DATA` database; Lakehouse's shared dataset is accessed via `clickzetta_sample_data`.

Snowflake:

```sql
CREATE OR REPLACE TABLE ARCH_BSG_DYNAMIC_TABLES.ORDERS_STG
DATA_RETENTION_TIME_IN_DAYS = 1
AS
SELECT
    O_ORDERKEY   AS order_id,
    O_CUSTKEY    AS customer_id,
    O_ORDERDATE  AS order_ts,
    O_TOTALPRICE AS amount
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS;
```

Lakehouse:

```sql
CREATE SCHEMA IF NOT EXISTS bsg_dynamic_tables;

CREATE OR REPLACE TABLE bsg_dynamic_tables.orders_stg
AS
SELECT
    O_ORDERKEY   AS order_id,
    O_CUSTKEY    AS customer_id,
    O_ORDERDATE  AS order_ts,
    O_TOTALPRICE AS amount
FROM clickzetta_sample_data.tpch_100g.orders;

ALTER TABLE bsg_dynamic_tables.orders_stg
SET PROPERTIES ('data_retention_days' = '1');
```

Two changes:

1. `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1` → `clickzetta_sample_data.tpch_100g` (different dataset name, same column names)
2. `DATA_RETENTION_TIME_IN_DAYS = 1` moved from inline DDL option to a separate post-creation `ALTER TABLE ... SET PROPERTIES`

### Step 2: Replace Dynamic Table Syntax

This is the core part of the migration, involving 3 syntax changes.

**`TARGET_LAG` → `REFRESH INTERVAL`**

Snowflake uses `TARGET_LAG` to declare acceptable data latency (the platform automatically determines refresh frequency); Lakehouse uses `REFRESH INTERVAL` to set a fixed refresh cycle.

Snowflake:

```sql
CREATE OR REPLACE DYNAMIC TABLE bronze_orders
  TARGET_LAG = '5 minutes'
  WAREHOUSE = compute_wh
AS
SELECT ...
```

Lakehouse:

```sql
CREATE OR REPLACE DYNAMIC TABLE bsg_dynamic_tables.bronze_orders
  REFRESH INTERVAL '5' MINUTE
  VCLUSTER default
AS
SELECT ...
```

**`WAREHOUSE` → `VCLUSTER`**

Snowflake Virtual Warehouse corresponds to Lakehouse VCluster. Use your VCluster name (most instances default to `default`).

**Handling `TARGET_LAG = 'DOWNSTREAM'`**

Snowflake supports `TARGET_LAG = 'DOWNSTREAM'`, which lets upstream table refreshes automatically trigger downstream table refreshes in a dependency cascade. Lakehouse does not have this concept — each Dynamic Table refreshes independently according to its own `REFRESH INTERVAL`.

Practical recommendation: set Tier 1 (Bronze/Silver) refresh intervals shorter than Tier 2 (Gold) to approximate cascade behavior. For example, Bronze/Silver at 5 minutes and Gold at 10 minutes ensures Bronze/Silver data is up to date when Gold refreshes.

### Step 3: Replace Manual Refresh Command

Snowflake:

```sql
ALTER DYNAMIC TABLE bronze_orders REFRESH;
```

Lakehouse:

```sql
REFRESH DYNAMIC TABLE bsg_dynamic_tables.bronze_orders;
```

Note that refreshes must be executed manually in dependency order — Lakehouse does not auto-cascade:

```sql
REFRESH DYNAMIC TABLE bsg_dynamic_tables.bronze_orders;
REFRESH DYNAMIC TABLE bsg_dynamic_tables.silver_orders;
REFRESH DYNAMIC TABLE bsg_dynamic_tables.gold_sales_summary;
```

### Step 4: Fully Compatible Parts (No Changes Needed)

The following syntax is identical between Lakehouse and Snowflake:

**`QUALIFY ROW_NUMBER() OVER (...) = 1`** (Silver layer deduplication)

```sql
-- Identical syntax in Snowflake and Lakehouse
FROM bronze_orders
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY ingestion_ts DESC
) = 1;
```

**`DATE_TRUNC('day', ts)`** (Gold layer date aggregation)

```sql
-- Identical syntax in Snowflake and Lakehouse
SELECT
    DATE_TRUNC('day', order_ts) AS order_date,
    COUNT(*)                    AS total_orders,
    SUM(amount)                 AS total_sales
FROM silver_orders
GROUP BY DATE_TRUNC('day', order_ts);
```

**`CAST(order_ts AS TIMESTAMP)`** (Silver layer type conversion)

```sql
-- Identical syntax in Snowflake and Lakehouse
CAST(order_ts AS TIMESTAMP) AS order_ts
```

---

## Validation Results

All SQL has been validated by running on a Lakehouse instance via cz-cli:

| Table | Row Count | Notes |
|----|------|------|
| `orders_stg` | 100,000 | Sampled from 150M-row TPC-H dataset |
| `bronze_orders` | 100,000 | Added `ingestion_ts` and `source_system` columns |
| `silver_orders` | 100,000 | After QUALIFY deduplication (TPC-H source data has no duplicates) |
| `gold_sales_summary` | 103 | 103 distinct order dates, total sales $15 billion |

After running, clean up all Lakehouse objects with:

```bash
cz-cli sql -f 03_lakehouse/06_cleanup.sql --profile <your-profile> --sync --write
```

---

## Migration Conclusion

Snowflake Dynamic Tables and Lakehouse Dynamic Tables have highly compatible SQL query logic. This project validates the following conclusions:

**Fully compatible (no changes needed):**

- `QUALIFY ROW_NUMBER() OVER (...) = 1` deduplication
- `DATE_TRUNC('day', ts)` date truncation
- `CAST(col AS TYPE)` type conversion
- Standard aggregation functions: `COUNT`, `SUM`, `AVG`
- `CURRENT_TIMESTAMP()` system function

**4 changes required:**

| Difference | Snowflake | Lakehouse |
|--------|-----------|-----------|
| Compute resource | `WAREHOUSE = wh_name` | `VCLUSTER vcluster_name` |
| Refresh strategy | `TARGET_LAG = 'N minutes'` | `REFRESH INTERVAL 'N' MINUTE` |
| Dependency cascade | `TARGET_LAG = 'DOWNSTREAM'` | No such concept; each layer sets its own interval |
| Manual refresh | `ALTER DYNAMIC TABLE ... REFRESH` | `REFRESH DYNAMIC TABLE ...` |
| Time Travel retention | `DATA_RETENTION_TIME_IN_DAYS = N` (inline CREATE TABLE option) | `ALTER TABLE ... SET PROPERTIES ('data_retention_days' = 'N')` (separate post-creation statement) |

---

## References

- GitHub project: [snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables)
- Original project: [Techy-Malay/snowflake-bsg-dynamic-tables](https://github.com/Techy-Malay/snowflake-bsg-dynamic-tables)
- [Dynamic Table Overview](dynamic_table_summary.md)
- [CREATE DYNAMIC TABLE](create-dynamic-table.md)
- [Time Travel](timetravel-summary.md)
- [Dynamic Table Development Guide](sql_dynamic_table_guide.md)
