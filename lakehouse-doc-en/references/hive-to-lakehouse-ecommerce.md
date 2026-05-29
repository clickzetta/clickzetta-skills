# Hive → Lakehouse Migration in Practice: E-Commerce User Behavior Data Warehouse

If your data warehouse runs on Hive, migrating to Singdata Lakehouse takes less effort than you might expect. The core Hive SQL syntax — SELECT, JOIN, GROUP BY, window functions, conditional aggregation — runs directly in Lakehouse without any changes. Modifications are limited to 4 areas: storage format declarations, data loading method, dynamic partition SET statements, and SerDe configuration.

This article validates that claim with a real project: a complete migration of a Hive 4.0-based e-commerce user behavior data warehouse (ODS → DWD → DWS → ADS four-layer architecture) to Singdata Lakehouse, verified by 10 automated checks — all passing.

Full code on GitHub: [hive2lakehouse-ecommerce-events](https://github.com/clickzetta/hive2lakehouse-ecommerce-events)

---

## Source Project

The data comes from the [Kaggle E-Commerce User Behavior Dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop), containing user behavior logs from a cosmetics e-commerce site for October–November 2019. Fields include `event_time`, `event_type` (view/cart/purchase), `product_id`, `category_code`, `brand`, `price`, `user_id`, and `user_session` — approximately 6.5 million rows total.

The Hive implementation runs in a Docker container (`apache/hive:4.0.1`) with a four-layer architecture:

| Layer | Table | Description |
|----|----|------|
| ODS | `ods_events_raw` | Raw events, partitioned by date, ORC format |
| DWD | `dwd_events_clean` | Cleaned events, bucketed into 8 buckets by user_id, ORC format |
| DWS | `dws_user_behavior` | Daily user behavior summary (view/cart/purchase counts and amounts) |
| ADS | `ads_funnel_daily` | Daily funnel conversion rates (view→cart→purchase) |

The migrated code lives in the `03_lakehouse/` directory and can be compared file-by-file with `01_hive/`.

## Technology Stack Comparison

| | Hive 4.0 | Lakehouse |
|---|---|---|
| Storage format | ORC (requires explicit `STORED AS ORC`) | Native Parquet (no declaration needed) |
| CSV parsing | `ROW FORMAT SERDE 'OpenCSVSerde'` | `COPY INTO ... USING CSV OPTIONS (...)` |
| Bucketing | `CLUSTERED BY (col) INTO N BUCKETS` | Same syntax, directly compatible |
| Dynamic partitioning | Requires 3 SET statements to enable | Enabled by default, no SET needed |
| Data loading | `LOAD DATA LOCAL INPATH` + staging table | `COPY INTO FROM VOLUME` |
| Runtime environment | Docker container (beeline client) | cz-cli / Python SDK |

---

![](.topwrite/assets/anim-10-hive-migration.svg)

---

## Conclusion First

**Hive SQL DML logic is 100% compatible — changes are limited to 5 DDL and loading statements.**

| Change | Effort | Notes |
|--------|--------|------|
| Remove `STORED AS ORC` / `TBLPROPERTIES` | Very low | Delete directly, no logic changes |
| `LOAD DATA` → `COPY INTO FROM VOLUME` | Low | Different syntax structure, same logic |
| Remove dynamic partition SET statements | Very low | Delete 3 SET lines |
| Remove SerDe configuration | Very low | Delete `ROW FORMAT SERDE` block |

SELECT / JOIN / GROUP BY / window functions / conditional aggregation — the core data warehouse operations — have identical syntax and require no changes.

---

## Project Background

![](.topwrite/assets/32-hive-to-lakehouse-ecommerce.png)

The data architecture has four layers, each corresponding to a Schema:

- **ODS** (`ecommerce_ods`): Raw data, partitioned by date, preserving original fields
- **DWD** (`ecommerce_dwd`): Cleansing layer — `event_time` converted to TIMESTAMP, `category_code` split into three levels, dirty data filtered out
- **DWS** (`ecommerce_dws`): Daily user behavior summary — view/cart/purchase counts and spend per user per day
- **ADS** (`ecommerce_ads`): Funnel analysis — daily view→cart→purchase conversion rates

Sample data (20 rows) validation results:

| Metric | Value |
|------|----|
| ODS row count | 19 (1 row filtered due to column-shift dirty data) |
| DWD row count | 19 |
| DWS user count | 6 |
| view user count | 6 |
| cart user count | 4 |
| purchase user count | 3 |
| view→cart conversion rate | 66.67% |
| cart→purchase conversion rate | 75% |

---

## Migration Steps

### Step 1: Remove Storage Format Declarations

Every Hive table requires a storage format declaration. Lakehouse uses native Parquet — just delete those lines.

```sql
-- Hive
CREATE TABLE dwd_events_clean (...)
PARTITIONED BY (dt STRING)
CLUSTERED BY (user_id) INTO 8 BUCKETS
STORED AS ORC
TBLPROPERTIES ("orc.compress"="SNAPPY");

-- Lakehouse: delete the last three lines
CREATE TABLE dwd_events_clean (...)
PARTITIONED BY (dt STRING);
```

### Step 2: Replace Data Loading Method

Hive uses `LOAD DATA` to load files into an EXTERNAL TABLE. Lakehouse uses `COPY INTO FROM VOLUME`.

```sql
-- Hive: two steps (staging table + INSERT)
LOAD DATA LOCAL INPATH '/tmp/events.csv'
OVERWRITE INTO TABLE ods_events_staging;

INSERT OVERWRITE TABLE ods_events_raw PARTITION (dt)
SELECT ..., SUBSTR(event_time, 1, 10) AS dt
FROM ods_events_staging
WHERE event_type IN ('view', 'cart', 'purchase');

-- Lakehouse: also two steps, but different syntax
-- COPY INTO does not support computed columns (e.g., extracting dt),
-- so COPY INTO a staging table first, then INSERT INTO the partitioned table
COPY INTO ecommerce_ods.ods_events_staging
FROM VOLUME ecommerce_ods.ecommerce_vol
USING CSV
OPTIONS ('header' = 'true', 'nullValue' = '')
FILES ('raw/events_sample.csv')
ON_ERROR = CONTINUE;

INSERT OVERWRITE TABLE ecommerce_ods.ods_events_raw PARTITION (dt)
SELECT ..., SUBSTR(event_time, 1, 10) AS dt
FROM ecommerce_ods.ods_events_staging
WHERE event_type IN ('view', 'cart', 'purchase')
  AND user_id > 100000;
```

### Step 3: Remove Dynamic Partition SET Statements

Hive dynamic partitioning is disabled by default and requires 3 SET statements to enable. Lakehouse enables it by default — just delete those lines.

```sql
-- Hive (required, otherwise errors)
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;
SET hive.enforce.bucketing=true;

INSERT OVERWRITE TABLE dwd_events_clean PARTITION (dt)
SELECT ..., dt FROM ods_events_raw;

-- Lakehouse: write directly, delete all SET statements
INSERT OVERWRITE TABLE ecommerce_dwd.dwd_events_clean PARTITION (dt)
SELECT ..., dt FROM ecommerce_ods.ods_events_raw;
```

### Step 4: Remove SerDe Configuration

Hive requires SerDe configuration to parse CSV. Lakehouse specifies format in `COPY INTO`'s `OPTIONS` — no format configuration needed at table creation time.

```sql
-- Hive: SerDe must be configured at table creation
CREATE EXTERNAL TABLE ods_events_staging (...)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    "separatorChar" = ",",
    "quoteChar"     = "\""
)
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");

-- Lakehouse: table creation only declares columns; format is specified in COPY INTO
CREATE TABLE ecommerce_ods.ods_events_staging (
    event_time STRING, event_type STRING, ...
);
-- Format specified at load time
COPY INTO ecommerce_ods.ods_events_staging
FROM VOLUME ecommerce_ods.ecommerce_vol
USING CSV
OPTIONS ('header' = 'true', 'nullValue' = '')
FILES ('raw/events_sample.csv');
```

---

## Fully Compatible Parts

The following Hive SQL runs directly in Lakehouse without any modification:

**ETL transformation logic** (ODS → DWD):

```sql
-- Identical on both sides, reuse directly
INSERT OVERWRITE TABLE dwd_events_clean PARTITION (dt)
SELECT
    CAST(REGEXP_REPLACE(event_time, ' UTC$', '') AS TIMESTAMP) AS event_ts,
    event_type,
    product_id,
    SPLIT(category_code, '\\.')[0]                              AS category_l1,
    CASE WHEN SIZE(SPLIT(category_code, '\\.')) > 1
         THEN SPLIT(category_code, '\\.')[1] END                AS category_l2,
    brand, price, user_id, user_session, dt
FROM ods_events_raw
WHERE price > 0 OR event_type != 'purchase';
```

**Aggregation logic** (DWD → DWS/ADS):

```sql
-- Identical on both sides, reuse directly
SELECT
    COUNT(DISTINCT CASE WHEN event_type = 'view'     THEN user_id END) AS view_users,
    COUNT(DISTINCT CASE WHEN event_type = 'cart'     THEN user_id END) AS cart_users,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) AS purchase_users,
    ROUND(
        COUNT(DISTINCT CASE WHEN event_type = 'cart' THEN user_id END) * 1.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'view' THEN user_id END), 0),
        4
    ) AS view_to_cart_rate,
    dt
FROM dwd_events_clean
GROUP BY dt;
```

**Window function analysis**:

```sql
-- Identical on both sides, reuse directly
SELECT
    user_id,
    purchase_amt,
    RANK() OVER (ORDER BY purchase_amt DESC) AS spending_rank
FROM dws_user_behavior
WHERE dt = '2019-10-01';
```

---

## 4 Pitfalls Encountered

### Pitfall 1: OpenCSVSerde Column Shift

**Symptom**: When CSV contains consecutive empty fields (e.g., `brand` is empty, producing `,,`), OpenCSVSerde parsing causes subsequent columns to shift left — the value of `price` gets read as `user_id`.

**Example**:
```
2019-10-01,view,28719074,...,apparel.shoes.keds,,35.79,541312140,...
```
`brand` is empty → `price=35.79` is read as `user_id`, producing a dirty row with `user_id=35`.

**Fix**: Filter out abnormal user_id values when inserting into ODS:
```sql
WHERE CAST(user_id AS BIGINT) > 100000
```

**Lakehouse impact**: `COPY INTO` uses `ON_ERROR=CONTINUE` to skip malformed rows; same filter applied during INSERT.

### Pitfall 2: Hive 4.0 Bucketed Table GROUP BY Returns Empty

**Symptom**: Under Hive 4.0 + Tez engine, `GROUP BY` queries on `CLUSTERED BY` bucketed ORC tables return empty results, while `COUNT(*)` returns the correct row count via metadata stats.

**Root cause**: `CombineHiveInputFormat` (default) has a bug in its execution plan for bucketed ORC tables.

**Workaround**:
```sql
SET hive.input.format=org.apache.hadoop.hive.ql.io.HiveInputFormat;
```

**Lakehouse impact**: No such issue. Lakehouse supports `CLUSTERED BY ... INTO N BUCKETS` bucketing with the same syntax, and GROUP BY works correctly.

### Pitfall 3: COPY INTO Does Not Support Column Reference Syntax

**Symptom**: Lakehouse `COPY INTO` does not support `$1`, `$2` column references:
```sql
-- Error: Syntax error at or near '$'
COPY INTO t FROM (SELECT $1, $2 FROM VOLUME ...)
```

**Correct approach**: Use `FROM VOLUME ... USING CSV OPTIONS (...) FILES (...)` syntax, mapping columns by position. When computed columns are needed (e.g., extracting `dt`), first COPY INTO an unpartitioned staging table, then INSERT INTO the target table.

### Pitfall 4: Dynamic Partition Default Behavior Differences

| Behavior | Hive | Lakehouse |
|------|------|-----------|
| Dynamic partition switch | Disabled by default, requires `SET hive.exec.dynamic.partition=true` | Enabled by default |
| Strict mode | Strict by default, requires `SET ... mode=nonstrict` | No such restriction |
| Bucketed writes | Requires `SET hive.enforce.bucketing=true` | Supported by default, no SET needed |

---

## End-to-End Validation

`03_lakehouse/e2e.py` runs 10 automated checks on the migration results:

| Check | Expected | Result |
|--------|--------|------|
| ODS row count | 19 | ✓ |
| DWD row count | 19 | ✓ |
| DWS user count | 6 | ✓ |
| Funnel view_users | 6 | ✓ |
| Funnel cart_users | 4 | ✓ |
| Funnel purchase_users | 3 | ✓ |
| view→cart conversion rate | 0.6667 | ✓ |
| cart→purchase conversion rate | 0.75 | ✓ |
| Top spender user ID | 526595547 | ✓ |
| Top spend amount | 1422.0 | ✓ |

Actual run result: **10/10 passed**.

---

## Full Compatibility Reference

| Category | Hive Syntax | Lakehouse | Compatibility |
|------|-----------|-----------|--------|
| Partitioned table | `PARTITIONED BY (dt STRING)` | Same | Compatible |
| Dynamic partition write | `INSERT OVERWRITE ... PARTITION (dt)` | Same | Compatible |
| REGEXP_REPLACE | `REGEXP_REPLACE(col, pattern, replace)` | Same | Compatible |
| SPLIT | `SPLIT(col, '\\.')` | Same | Compatible |
| SIZE | `SIZE(SPLIT(...))` | Same | Compatible |
| SUBSTR | `SUBSTR(col, 1, 10)` | Same | Compatible |
| CAST | `CAST(col AS TIMESTAMP)` | Same | Compatible |
| NULLIF | `NULLIF(expr, 0)` | Same | Compatible |
| Conditional aggregation | `SUM(CASE WHEN ... END)` | Same | Compatible |
| COUNT DISTINCT | `COUNT(DISTINCT CASE WHEN ...)` | Same | Compatible |
| Window functions | `RANK() OVER (ORDER BY ...)` | Same | Compatible |
| STORED AS ORC | `STORED AS ORC` | Not needed | Delete |
| CLUSTERED BY | `CLUSTERED BY (col) INTO N BUCKETS` | Same syntax | Compatible |
| OpenCSVSerde | `ROW FORMAT SERDE 'OpenCSVSerde'` | Not needed | Delete; use COPY INTO instead |
| LOAD DATA | `LOAD DATA LOCAL INPATH` | Not supported | Use COPY INTO FROM VOLUME |
| Dynamic partition SET | `SET hive.exec.dynamic.partition=true` | Not needed | Delete |

---

## Migration Conclusion

**Migrating a Hive data warehouse to Lakehouse requires effort mainly in DDL and loading statements, not in business logic.** In this project, all ETL transformation SQL (REGEXP_REPLACE, SPLIT, conditional aggregation) and analytical queries (window functions, funnel calculations) were reused directly. Changes were limited to 4 known difference points, all mechanical replacements.

### SQL-Level Benefits

- The GROUP BY bug on bucketed ORC tables disappears naturally
- No need to maintain SerDe configuration and TBLPROPERTIES
- Dynamic partitioning enabled by default, no SET statements needed
- COPY INTO is cleaner than LOAD DATA + staging table

### Deployment Model Benefits

Migrating from a self-managed Docker Hive cluster to Singdata Lakehouse SaaS brings more than just SQL simplification:

| | Hive (Docker self-managed) | Lakehouse (SaaS) |
|---|---|---|
| Cluster operations | Maintain Docker containers, JVM parameters, YARN queues | No ops needed, fully managed |
| Compute resources | Fixed resources, wasted during idle periods | Elastic scaling, billed per query |
| Storage format | ORC files require periodic compaction | Native Parquet, automatically managed |
| Tuning cost | Tune Hive parameters, Tez config, bucketing strategy | Focus on SQL logic, no low-level tuning |
| Version upgrades | Manually upgrade Hive and Hadoop dependencies | Platform upgrades automatically |

After migration, data engineers can shift their focus from "keeping Hive running" to "making data valuable."

---

## References

- GitHub: [hive2lakehouse-ecommerce-events](https://github.com/clickzetta/hive2lakehouse-ecommerce-events)
- [Hive ↔ Lakehouse Syntax Reference](https://github.com/clickzetta/hive2lakehouse-ecommerce-events/blob/main/02_migration/02_syntax_mapping.md)
- [COPY INTO Syntax Reference](copy-into.md)
- [CREATE INDEX Syntax Reference](create-index.md)
