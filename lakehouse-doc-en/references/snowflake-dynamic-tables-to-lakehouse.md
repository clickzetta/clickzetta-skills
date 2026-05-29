# Migrating Snowflake Dynamic Tables to Lakehouse: Bronze–Silver–Gold Three-Layer Pipeline

If you have built a Medallion data pipeline on Snowflake using Dynamic Tables, migrating to Singdata Lakehouse involves changes in 4 syntax areas. The core SQL query logic does not need to change.

This guide walks through a complete migration using a real project: moving a Bronze–Silver–Gold three-layer pipeline built on Snowflake Dynamic Tables to Singdata Lakehouse, using the TPC-H standard dataset available on both platforms. All SQL has been validated with cz-cli against a live instance.

Full code on GitHub: [snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables)

---

## Original Project

[snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables) is adapted from [Techy-Malay/snowflake-bsg-dynamic-tables](https://github.com/Techy-Malay/snowflake-bsg-dynamic-tables) and demonstrates how to implement a Bronze–Silver–Gold three-layer architecture on Snowflake using Dynamic Tables. The project uses the TPC-H ORDERS table as its data source and produces a daily sales summary after three layers of Dynamic Table processing.

The migrated code lives in the `03_lakehouse/` directory. The original Snowflake SQL is preserved in `01_snowflake/` for comparison.

## Technology Stack Comparison

| | Original (Snowflake) | Migrated (Lakehouse) |
|---|---|---|
| Compute resource | `WAREHOUSE = compute_wh` | `VCLUSTER default` |
| Refresh strategy | `TARGET_LAG = '5 minutes'` | `REFRESH INTERVAL '5' MINUTE` |
| Dependency propagation | `TARGET_LAG = 'DOWNSTREAM'` (automatic cascade) | No equivalent; each layer refreshes independently |
| Manual refresh | `ALTER DYNAMIC TABLE ... REFRESH` | `REFRESH DYNAMIC TABLE ...` |
| Time Travel retention | `DATA_RETENTION_TIME_IN_DAYS = 1` (inline CREATE TABLE option) | `ALTER TABLE ... SET PROPERTIES ('data_retention_days' = '1')` (separate statement after table creation) |
| Sample dataset | `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS` (1 GB) | `clickzetta_sample_data.tpch_100g.orders` (100 GB) |
| Schema reference | `USE SCHEMA` + unqualified name, or fully qualified name | Same; both styles are supported |
| Deduplication syntax | `QUALIFY ROW_NUMBER() OVER (...) = 1` | Same syntax, fully supported |
| Date truncation | `DATE_TRUNC('day', ts)` | Same syntax, fully supported |

What changes is primarily platform configuration — swapping Snowflake Virtual Warehouse for Lakehouse VCluster, and `TARGET_LAG` for `REFRESH INTERVAL`. The core SQL data processing logic is completely unchanged: cleansing, deduplication, and aggregation are written identically on Lakehouse.

---

## Architecture Overview

```
SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS          clickzetta_sample_data.tpch_100g.orders
(Snowflake built-in sample dataset, 1 GB)       (Lakehouse shared dataset, 100 GB)
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
    (cleansed, deduplicated, type-normalized)      (cleansed, deduplicated, type-normalized)
              │                                               │
              ▼  TARGET_LAG = '10 minutes'                    ▼  REFRESH INTERVAL '10' MINUTE
         gold_sales_summary                            gold_sales_summary
    (daily sales summary, analytics-ready)         (daily sales summary, analytics-ready)
```

---

![](.topwrite/assets/anim-08-snowflake-dt-migration.svg)

---

## Migration Steps

### Step 1: Replace the sample dataset reference

Snowflake's built-in sample data is accessed via the `SNOWFLAKE_SAMPLE_DATA` database. Lakehouse's shared dataset is accessed via `clickzetta_sample_data`.

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

1. `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1` → `clickzetta_sample_data.tpch_100g` (different dataset name; column names are the same)
2. `DATA_RETENTION_TIME_IN_DAYS = 1` moves from an inline DDL option to a separate `ALTER TABLE ... SET PROPERTIES` statement after table creation

### Step 2: Replace Dynamic Table syntax

This is the core of the migration and involves 3 syntax changes.

**`TARGET_LAG` → `REFRESH INTERVAL`**

Snowflake uses `TARGET_LAG` to declare the acceptable data lag (the platform decides the refresh frequency automatically). Lakehouse uses `REFRESH INTERVAL` to set a fixed refresh cycle.

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

Snowflake supports `TARGET_LAG = 'DOWNSTREAM'`, which causes an upstream table's refresh to automatically trigger downstream table refreshes, forming a dependency cascade. Lakehouse does not have this concept — each Dynamic Table refreshes independently on its own `REFRESH INTERVAL`.

Practical recommendation: set Tier 1 (Bronze/Silver) refresh intervals shorter than Tier 2 (Gold) to approximate the cascade effect. For example, set Bronze/Silver to 5 minutes and Gold to 10 minutes — by the time Gold refreshes, Bronze/Silver will already have the latest data.

### Step 3: Replace the manual refresh command

Snowflake:

```sql
ALTER DYNAMIC TABLE bronze_orders REFRESH;
```

Lakehouse:

```sql
REFRESH DYNAMIC TABLE bsg_dynamic_tables.bronze_orders;
```

Note that refreshes must be executed manually in dependency order — Lakehouse does not cascade automatically:

```sql
REFRESH DYNAMIC TABLE bsg_dynamic_tables.bronze_orders;
REFRESH DYNAMIC TABLE bsg_dynamic_tables.silver_orders;
REFRESH DYNAMIC TABLE bsg_dynamic_tables.gold_sales_summary;
```

### Step 4: Fully compatible parts (no changes needed)

The following syntax is identical between Lakehouse and Snowflake:

**`QUALIFY ROW_NUMBER() OVER (...) = 1`** (Silver layer deduplication)

```sql
-- Identical syntax in both Snowflake and Lakehouse
FROM bronze_orders
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY ingestion_ts DESC
) = 1;
```

**`DATE_TRUNC('day', ts)`** (Gold layer date aggregation)

```sql
-- Identical syntax in both Snowflake and Lakehouse
SELECT
    DATE_TRUNC('day', order_ts) AS order_date,
    COUNT(*)                    AS total_orders,
    SUM(amount)                 AS total_sales
FROM silver_orders
GROUP BY DATE_TRUNC('day', order_ts);
```

**`CAST(order_ts AS TIMESTAMP)`** (Silver layer type conversion)

```sql
-- Identical syntax in both Snowflake and Lakehouse
CAST(order_ts AS TIMESTAMP) AS order_ts
```

---

## Validation Results

All SQL was validated by running it against a Lakehouse instance with cz-cli:

| Table | Row count | Notes |
|-------|-----------|-------|
| `orders_stg` | 100,000 | Sampled from the 150M-row TPC-H dataset |
| `bronze_orders` | 100,000 | Two columns added: `ingestion_ts`, `source_system` |
| `silver_orders` | 100,000 | After QUALIFY deduplication (TPC-H source data has no duplicates) |
| `gold_sales_summary` | 103 | 103 distinct order dates, total sales $15 billion |

After the run, clean up all Lakehouse objects with:

```bash
cz-cli sql -f 03_lakehouse/06_cleanup.sql --profile <your-profile> --sync --write
```

---

## Migration Conclusions

The SQL query logic of Snowflake Dynamic Tables and Lakehouse Dynamic Tables is highly compatible. This project validates the following conclusions:

**Fully compatible (no changes needed):**

- `QUALIFY ROW_NUMBER() OVER (...) = 1` deduplication
- `DATE_TRUNC('day', ts)` date truncation
- `CAST(col AS TYPE)` type conversion
- Standard aggregate functions: `COUNT`, `SUM`, `AVG`
- `CURRENT_TIMESTAMP()` system function

**4 areas that require changes:**

| Difference | Snowflake | Lakehouse |
|------------|-----------|-----------|
| Compute resource | `WAREHOUSE = wh_name` | `VCLUSTER vcluster_name` |
| Refresh strategy | `TARGET_LAG = 'N minutes'` | `REFRESH INTERVAL 'N' MINUTE` |
| Dependency cascade | `TARGET_LAG = 'DOWNSTREAM'` | No equivalent; each layer sets its own interval |
| Manual refresh | `ALTER DYNAMIC TABLE ... REFRESH` | `REFRESH DYNAMIC TABLE ...` |
| Time Travel retention | `DATA_RETENTION_TIME_IN_DAYS = N` (inline CREATE TABLE option) | `ALTER TABLE ... SET PROPERTIES ('data_retention_days' = 'N')` (separate statement after table creation) |

---

## References

- GitHub project: [snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables)
- Original project: [Techy-Malay/snowflake-bsg-dynamic-tables](https://github.com/Techy-Malay/snowflake-bsg-dynamic-tables)
- [Dynamic Table Overview](dynamic_table_summary.md)
- [CREATE DYNAMIC TABLE](create-dynamic-table.md)
- [Time Travel](timetravel.md)
- [Dynamic Table Development Guide](SQL_Dynamic_Table_Guide.md)
