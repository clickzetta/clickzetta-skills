# Hive → Lakehouse Migration in Practice: E-commerce User Behavior Data Warehouse

If your data warehouse runs on Hive, migrating to Singdata Lakehouse requires less effort than you might expect. The core Hive SQL syntax — SELECT, JOIN, GROUP BY, window functions, conditional aggregation — runs directly in Lakehouse without modification. Changes are concentrated in 4 areas: storage format declarations, data loading methods, dynamic partition SET statements, and SerDe configuration.

This article validates this with a real project: a complete migration of a Hive 4.0-based e-commerce user behavior data warehouse (ODS → DWD → DWS → ADS four-layer architecture) to Singdata Lakehouse, passing all 10 automated validation checks.

Full code on GitHub: [hive2lakehouse-ecommerce-events](https://github.com/clickzetta/hive2lakehouse-ecommerce-events)

---

## Original Project

The data source is the [Kaggle E-commerce User Behavior Dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop), containing user behavior logs from a cosmetics e-commerce website in October–November 2019. Fields include `event_time`, `event_type` (view/cart/purchase), `product_id`, `category_code`, `brand`, `price`, `user_id`, `user_session`, totaling approximately 6.5 million rows.

The Hive implementation runs in a Docker container (`apache/hive:4.0.1`) with a four-layer architecture:

| Layer | Table | Description |
|----|----|------|
| ODS | `ods_events_raw` | Raw events, partitioned by date, ORC format |
| DWD | `dwd_events_clean` | Cleaned events, bucketed into 8 buckets by user_id, ORC format |
| DWS | `dws_user_behavior` | Daily user behavior summary (view/cart/purchase counts and amounts) |
| ADS | `ads_funnel_daily` | Daily funnel conversion rates (view→cart→purchase) |

The migrated code is in the `03_lakehouse/` directory and can be compared file-by-file with `01_hive/`.

## Conclusion First

Your SQL query logic does not need a single change. The 5 changes are all in CREATE TABLE statements and data loading methods — remove Hive-specific storage configuration, replace LOAD DATA syntax, and the business logic is fully preserved.

| Change | Effort | Description |
|--------|--------|------|
| Remove `STORED AS ORC` / `TBLPROPERTIES` | Very low | Delete directly, no logic changes |
| `LOAD DATA` → `COPY INTO FROM VOLUME` | Low | Different syntax structure, but same logic |
| Remove dynamic partition SET statements | Very low | Delete 3 SET lines directly |
| Remove SerDe configuration | Very low | Delete `ROW FORMAT SERDE` block directly |

SELECT / JOIN / GROUP BY / window functions / conditional aggregation — the core operations of a data warehouse — have identical syntax and require no changes.

---

## Technology Stack Comparison

| | Hive 4.0 | Lakehouse |
|---|---|---|
| Storage format | ORC (requires explicit `STORED AS ORC`) | Native Parquet (no declaration needed) |
| CSV parsing | `ROW FORMAT SERDE 'OpenCSVSerde'` | `COPY INTO ... USING CSV OPTIONS (...)` |
| Bucketing acceleration | `CLUSTERED BY (col) INTO N BUCKETS` | Same syntax, directly compatible |
| Dynamic partitioning | Requires 3 SET statements to enable | Enabled by default, no SET needed |
| Data loading | `LOAD DATA LOCAL INPATH` + staging table | `COPY INTO FROM VOLUME` |
| Runtime environment | Docker container (beeline client) | cz-cli / Python SDK |

---

![](.topwrite/assets/anim-10-hive-migration.svg)

---

## Project Background

![](.topwrite/assets/32-hive-to-lakehouse-ecommerce.svg)

The data architecture has four layers, each corresponding to a schema:

- **ODS** (`ecommerce_ods`): Raw data, partitioned by date, retaining original fields
- **DWD** (`ecommerce_dwd`): Cleansing layer, `event_time` converted to TIMESTAMP, `category_code` split into three levels, dirty data filtered
- **DWS** (`ecommerce_dws`): Daily user behavior summary — view/cart/purchase counts and spending per user per day
- **ADS** (`ecommerce_ads`): Funnel analysis — daily view→cart→purchase conversion rates

Sample data (20 rows) validation results:

| Metric | Value |
|------|----|
| ODS row count | 19 (1 row filtered for column-shift dirty data) |
| DWD row count | 19 |
| DWS user count | 6 |
| View user count | 6 |
| Cart user count | 4 |
| Purchase user count | 3 |
| View→cart conversion rate | 66.67% |
| Cart→purchase conversion rate | 75% |

---

## Migration Steps

### Step 1: Remove Storage Format Declarations

Hive requires every table to declare a storage format. Lakehouse uses native Parquet — just delete the declarations.

```sql
-- Hive
CREATE TABLE dwd_events_clean (...)
PARTITIONED BY (dt STRING)
CLUSTERED BY (user_id) INTO 8 BUCKETS
STORED AS ORC
TBLPROPERTIES ("orc.compress"="SNAPPY");

-- Lakehouse: just delete the last three lines
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
-- so COPY INTO staging first, then INSERT INTO partitioned table
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

Hive dynamic partitioning is disabled by default and requires 3 SET statements to enable. Lakehouse enables it by default — just delete the SET statements.

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

Hive requires SerDe configuration to parse CSV. Lakehouse specifies this in `COPY INTO`'s `OPTIONS` — no format configuration is needed at table creation time.

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
-- Specify format at load time
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

## Notes

### 1. OpenCSVSerde Column Shift

**Symptom**: When CSV has consecutive empty fields (e.g., `brand` is empty, appearing as `,,`), OpenCSVSerde parsing causes subsequent columns to shift left — the value of `price` gets read as `user_id`.

**Example**:
```
2019-10-01,view,28719074,...,apparel.shoes.keds,,35.79,541312140,...
```
`brand` is empty → `price=35.79` is read as `user_id`, producing a dirty data row with `user_id=35`.

**Handling**: Filter abnormal user_ids when INSERT INTO ODS:
```sql
WHERE CAST(user_id AS BIGINT) > 100000
```

**Lakehouse impact**: `COPY INTO` uses `ON_ERROR=CONTINUE` to skip malformed rows; the same filter is applied during INSERT.

### 2. Hive 4.0 Bucketed Table GROUP BY Returns Empty

**Symptom**: Under Hive 4.0 + Tez engine, `GROUP BY` queries on `CLUSTERED BY` bucketed ORC tables return empty results, but `COUNT(*)` returns the correct row count via metadata stats.

**Root cause**: `CombineHiveInputFormat` (default) has a bug in the execution plan for bucketed ORC tables.

**Temporary fix**:
```sql
SET hive.input.format=org.apache.hadoop.hive.ql.io.HiveInputFormat;
```

**Lakehouse impact**: This issue does not exist. Lakehouse also supports `CLUSTERED BY ... INTO N BUCKETS` bucketing, but GROUP BY works correctly without this bug.

### 3. COPY INTO Does Not Support Column Reference Syntax

**Symptom**: Lakehouse `COPY INTO` does not support `$1`, `$2` column references:
```sql
-- Error: Syntax error at or near '$'
COPY INTO t FROM (SELECT $1, $2 FROM VOLUME ...)
```

**Correct approach**: Use `FROM VOLUME ... USING CSV OPTIONS (...) FILES (...)` syntax, mapping columns directly by order. When computed columns are needed (e.g., extracting `dt`), first COPY INTO an unpartitioned staging table, then INSERT INTO the target table.

### 4. Dynamic Partition Default Behavior Differences

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
| View→cart conversion rate | 0.6667 | ✓ |
| Cart→purchase conversion rate | 0.75 | ✓ |
| Top spending user ID | 526595547 | ✓ |
| Top spending amount | 1422.0 | ✓ |

Actual run result: **10/10 passed**.

---

## Full Compatibility Reference

| Category | Hive Syntax | Lakehouse | Compatibility |
|------|-----------|-----------|--------|
| Partitioned table | `PARTITIONED BY (dt STRING)` | Same | ✅ Fully compatible |
| Dynamic partition write | `INSERT OVERWRITE ... PARTITION (dt)` | Same | ✅ Fully compatible |
| REGEXP_REPLACE | `REGEXP_REPLACE(col, pattern, replace)` | Same | ✅ Fully compatible |
| SPLIT | `SPLIT(col, '\\.')` | Same | ✅ Fully compatible |
| SIZE | `SIZE(SPLIT(...))` | Same | ✅ Fully compatible |
| SUBSTR | `SUBSTR(col, 1, 10)` | Same | ✅ Fully compatible |
| CAST | `CAST(col AS TIMESTAMP)` | Same | ✅ Fully compatible |
| NULLIF | `NULLIF(expr, 0)` | Same | ✅ Fully compatible |
| Conditional aggregation | `SUM(CASE WHEN ... END)` | Same | ✅ Fully compatible |
| COUNT DISTINCT | `COUNT(DISTINCT CASE WHEN ...)` | Same | ✅ Fully compatible |
| Window functions | `RANK() OVER (ORDER BY ...)` | Same | ✅ Fully compatible |
| STORED AS ORC | `STORED AS ORC` | Not needed | ✅ Delete it |
| CLUSTERED BY | `CLUSTERED BY (col) INTO N BUCKETS` | Same syntax | ✅ Fully compatible |
| OpenCSVSerde | `ROW FORMAT SERDE 'OpenCSVSerde'` | Not needed | ✅ Delete, use COPY INTO instead |
| LOAD DATA | `LOAD DATA LOCAL INPATH` | Not supported | ⚠️ Use COPY INTO FROM VOLUME |
| Dynamic partition SET | `SET hive.exec.dynamic.partition=true` | Not needed | ✅ Delete it |

---

## Migration Conclusion

**The effort for migrating a Hive data warehouse to Lakehouse is mainly in DDL and loading statements, not in business logic.** In this project, the ETL transformation SQL (REGEXP_REPLACE, SPLIT, conditional aggregation) and analytical queries (window functions, funnel calculations) are all reused directly. Changes are concentrated in 4 known difference points, all of which are mechanical replacements.

### SQL-Level Benefits

- The GROUP BY bug on bucketed ORC tables disappears naturally
- No need to maintain SerDe configuration and TBLPROPERTIES
- Dynamic partitioning is enabled by default, no SET statements needed
- COPY INTO is cleaner than LOAD DATA + staging table

### Deployment Model Benefits

Migrating from a self-managed Docker Hive cluster to Singdata Lakehouse SaaS brings benefits beyond SQL simplification:

| | Hive (self-managed Docker) | Lakehouse (SaaS) |
|---|---|---|
| Cluster operations | Must maintain Docker containers, JVM parameters, YARN queues | No operations needed, fully managed |
| Compute resources | Fixed resources, wasted during idle periods | Elastic scaling, billed per query |
| Storage format | ORC files require periodic compaction | Native Parquet, automatically managed |
| Tuning cost | Must tune Hive parameters, Tez configuration, bucketing strategy | Focus on SQL logic, no low-level tuning |
| Version upgrades | Manual Hive and Hadoop dependency upgrades | Platform auto-upgrades |

After migration, data engineers can shift their focus from "keeping Hive running" to "making data valuable."

---

## References

- GitHub: [hive2lakehouse-ecommerce-events](https://github.com/clickzetta/hive2lakehouse-ecommerce-events)
- [Hive ↔ Lakehouse Syntax Mapping](https://github.com/clickzetta/hive2lakehouse-ecommerce-events/blob/main/02_migration/02_syntax_mapping.md)
- [COPY INTO Syntax Reference](copy-into-table.md)
- [CREATE INDEX Syntax Reference](create-inverted-index.md)
