# Data Warehouse Modeling Patterns

## Traditional DW Layering (ODS/DWD/DWS/ADS)

### Layer responsibilities

```
ODS (Operational Data Store)
├── Raw ingestion, no business transformation
├── Preserve original field names and types
├── Add metadata fields: dw_insert_time, dw_source
└── Partition by time, support incremental sync

DWD (Data Warehouse Detail)
├── Data cleansing: dedup, NULL handling, format standardization
├── Dimension denormalization: redundant common dimension fields into fact tables
├── Business rules: status code mapping, amount unit normalization
└── Logical primary key (ClickZetta does not enforce constraints)

DWS (Data Warehouse Summary)
├── Light aggregation: daily/weekly/monthly rollups
├── Use Dynamic Table for auto incremental refresh
├── Organized by subject domain: user, product, transaction
└── Not directly exposed to BI (ADS layer wraps it)

ADS (Application Data Store)
├── Wide tables for specific applications/reports
├── Use Dynamic Table or direct query from DWS
└── Business-friendly field naming
```

### Naming conventions

```
Schema: {prefix}_ods / {prefix}_dwd / {prefix}_dws / {prefix}_ads
Tables:
  ODS: ods_{source}_{table}       e.g. ods_mysql_orders
  DWD: dwd_{domain}_{grain}       e.g. dwd_trade_order_detail
  DWS: dws_{domain}_{dim}_{period} e.g. dws_user_order_1d
  ADS: ads_{app}_{metric}         e.g. ads_report_gmv_daily
```

---

## Medallion Architecture (Bronze/Silver/Gold)

### Layer responsibilities

```
Bronze
├── Raw data, zero-transformation principle
├── Supports structured / semi-structured / unstructured
├── Preserve all historical versions (Time Travel)
└── Source markers: source_system, ingestion_time

Silver
├── Trusted data: dedup, cleanse, standardize
├── Cross-source integration: unified field naming and types
├── Business entity identification: user, order, product
└── Directly usable for data science and exploratory analysis

Gold
├── Business-ready data: aggregated metrics, wide tables
├── Use Dynamic Table for auto-refresh
├── Facing BI tools and application systems
└── Semantically clear, business-friendly field naming
```

### Schema naming

```
{prefix}_bronze.{source}_{entity}   e.g. ecommerce_bronze.mysql_orders
{prefix}_silver.{entity}            e.g. ecommerce_silver.orders
{prefix}_gold.{domain}_{metric}     e.g. ecommerce_gold.trade_gmv_daily
```

---

## Dynamic Table vs Materialized View

| Feature | Dynamic Table | Materialized View |
|---|---|---|
| Refresh mechanism | CBO incremental compute, only refreshes changed partitions | Full or manual incremental |
| Scheduling | REFRESH INTERVAL auto-controls | Requires manual scheduling config |
| Time Travel | ✅ Supported | ❌ Not supported |
| Data recovery | ✅ RESTORE TABLE | ❌ Not supported |
| Syntax complexity | Simple, similar to CREATE TABLE | More complex |
| Recommended for | **New projects — always prefer** | Legacy project compatibility |

**Conclusion: Use Dynamic Table for all new projects. Avoid Materialized View.**

---

## DDL Templates

### ODS/Bronze (CDC ingestion example)

```sql
CREATE TABLE IF NOT EXISTS ods.orders (
    order_id       BIGINT,
    user_id        BIGINT,
    amount         DECIMAL(18, 2),
    status         STRING,
    created_at     TIMESTAMP,
    _op            STRING,    -- CDC operation type: I/U/D
    _ts            TIMESTAMP, -- change timestamp
    dw_insert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITIONED BY (days(created_at))
COMMENT 'ODS orders raw table, raw ingestion no transformation';
```

### DWD/Silver

```sql
CREATE TABLE IF NOT EXISTS dwd.fact_orders (
    order_id       BIGINT,
    user_id        BIGINT,
    amount         DECIMAL(18, 2),
    status_code    INT,
    order_date     DATE,
    dw_insert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITIONED BY (days(order_date))
CLUSTERED BY (user_id) INTO 32 BUCKETS
COMMENT 'DWD orders fact table, cleansed and standardized';
```

### DWS/Gold (Dynamic Table — not Materialized View)

```sql
-- First confirm available GP-type VCluster: SHOW VCLUSTERS;
CREATE DYNAMIC TABLE IF NOT EXISTS dws.user_order_daily
  REFRESH INTERVAL 1 HOUR vcluster <gp_vcluster_name>
AS
SELECT
    user_id,
    order_date,
    COUNT(order_id)  AS order_cnt,
    SUM(amount)      AS total_amount,
    AVG(amount)      AS avg_amount
FROM dwd.fact_orders
WHERE status_code = 1
GROUP BY user_id, order_date;

-- Immediately trigger first refresh after creation to reset refresh baseline
REFRESH DYNAMIC TABLE dws.user_order_daily;
```

---

## Scheduling DAG

### Batch scenario (T+1)

```
00_sync (Cron 02:00)
  → 04_transform (Cron 02:30, depends on 00_sync)
    → 05_dqc (optional, depends on 04_transform)

DWS/ADS: Dynamic Table auto-refresh — no Studio task needed
```

### Real-time scenario

```
CDC/Kafka continuous write to Bronze/ODS
  → Silver/DWD (REFRESH INTERVAL 10 MINUTE)
    → Gold/DWS (REFRESH INTERVAL 1 HOUR)
      → ADS (REFRESH INTERVAL 1 HOUR or direct query)
```

### Standard scheduling time windows (batch)

```
02:00  Data sync task completes (Studio sync)
02:30  ODS/staging layer ETL
03:00  DWD/silver layer ETL
03:30  DWS/gold/marts layer (if using incremental, not DT)
04:00  Data quality checks (DQC)
```

---

## Common Modeling Pitfalls

1. **Over-normalization**: DWD layer should not be split too granularly — redundant dimension fields reduce downstream JOINs
2. **Partition granularity too fine**: Hourly partitions create many small files; use daily partitions for batch scenarios
3. **ADS layer running raw SQL**: ADS should use Dynamic Table — don't let BI tools run complex SQL directly
4. **Ignoring data quality at ODS**: Check NULL rates at ingestion time, not after DWS is built
5. **Transforming in Bronze**: Once Bronze is transformed, raw data is lost and traceability breaks
6. **LEFT JOIN filter in WHERE**: `LEFT JOIN ... WHERE right_field = value` degrades to INNER JOIN — filters on right-table fields must go in the `ON` clause
