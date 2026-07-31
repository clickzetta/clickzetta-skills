# Build a Retail Chain Store Operations Data Warehouse

Integrate POS transaction data and inventory data from 100 chain stores nationwide to build a store operations analysis and SKU turnover data warehouse. This guide uses the [Retail Data Warehouse 12-Table Dataset](https://www.kaggle.com/datasets/datarspectrum/retail-data-warehouse-12-table-1m-rows-dataset) to walk through the complete pipeline from ODS raw POS transactions to ADS fast/slow-moving SKU analysis and store rankings, covering six core capabilities: MySQL CDC multi-table full-database mirror, Dynamic Table incremental aggregation, static partitioning by store_id, Bloomfilter Index, External Schema (Hive), and Time Travel for month-end reconciliation.

![](/.topwrite/assets/anim-20-retail-chain-pos.svg)

---

## Overview

Core challenges in a chain retail data warehouse:

| Problem | Singdata Solution |
|---|---|
| POS systems across different regional stores use separate databases and sharded tables that need to be unified | MySQL CDC multi-table full-database mirror — merge shards and write to a single ODS layer |
| ODS → DWD → DWS → ADS multi-layer aggregation is error-prone to schedule manually | Dynamic Table cascading refresh with declarative SQL; the system automatically maintains the dependency chain |
| Single-store historical order queries are slow and full cross-partition scans are costly | `PARTITIONED BY (store_id)` + `SESSION_CONFIGS` parameterized partitions for per-store refreshes |
| `product_id` in order items is a high-cardinality column with frequent point queries | Bloomfilter Index — skip non-matching data blocks in milliseconds |
| Years of existing historical data remains in Hive clusters and you don't want to migrate it | External Schema (Hive) — query external historical tables directly in SQL without migration |
| Month-end reconciliation requires comparing historical sales snapshots with current system data | Time Travel — `TIMESTAMP AS OF` to rewind to any historical version |

---

## SQL Commands Used

| Command / Feature | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create ODS layer raw POS transaction tables and dimension tables | Regular tables, used as upstream sources for Dynamic Tables |
| `CREATE BLOOMFILTER INDEX` | Create a Bloomfilter index on the `product_id` column | Suitable for point query filtering on high-cardinality columns |
| `CREATE DYNAMIC TABLE` | Create DWD / DWS / ADS incremental computation tables | Declarative SQL; the system handles incremental refresh |
| `PARTITIONED BY` + `SESSION_CONFIGS` | Refresh the DWS layer by store ID with static partitions | Parameterized partitions for precise per-store historical backfill |
| `REFRESH DYNAMIC TABLE ... PARTITION` | Refresh a specified store partition in DWS | Studio Task schedules by store + date granularity |
| `CREATE EXTERNAL SCHEMA` | Mount Hive historical order data | Two-level naming for queries; no data migration needed |
| `DESC HISTORY` | View table historical version list | Returns timestamp, row count change per version |
| `SELECT ... TIMESTAMP AS OF` | Month-end reconciliation: rewind to a historical snapshot | Locates order totals and revenue at any point in time |

---

## Prerequisites

All examples run under the `best_practice_retail_pos` schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_retail_pos;
```

Download the dataset and extract it locally:

```bash
kaggle datasets download -d datarspectrum/retail-data-warehouse-12-table-1m-rows-dataset \
    --unzip -p /tmp/retail_pos/
```

After extraction you get 12 CSV files: `stores.csv` (100 rows), `orders.csv` (300K rows), `order_items.csv` (600K rows), `products.csv` (10K rows), etc. This guide uses 100 stores, 100 orders, and 200 order items as the demo dataset.

---

## ODS (Raw Data Layer): Multi-Store POS Raw Data

The ODS layer directly receives raw data from each regional POS system, distributed by natural business keys when creating tables, with no aggregation transformations.

### MySQL CDC Ingestion

In production, each regional POS system is typically an independent MySQL instance. Binlog changes are synced in real time to the ODS layer via CDC through Studio's **multi-table real-time sync** task (task_type=281).

> ⚠️ **Note**: MySQL CDC connections do not use `CREATE STORAGE CONNECTION`. The Lakehouse `STORAGE CONNECTION` only supports object storage (OSS/HDFS, etc.) and Kafka types — MySQL is not supported. Configure MySQL data sources under Studio's **Data Source Management**, and create CDC tasks through the multi-table real-time sync feature.

**Source MySQL Preparation**

Confirm the following parameters are correctly configured on the source MySQL:

| Parameter | Required Value | Query Method |
|------|--------|---------|
| `log_bin` | ON | `SHOW GLOBAL VARIABLES LIKE 'log_bin'` |
| `binlog_format` | ROW | `SHOW GLOBAL VARIABLES LIKE 'binlog_format'` |
| `binlog_row_image` | FULL | `SHOW GLOBAL VARIABLES LIKE 'binlog_row_image'` |

The sync account needs the following permissions:

```sql
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc_user'@'%';
```

**Studio Multi-Table Real-Time Sync Configuration Steps**

1. Add MySQL data sources in Studio's **Data Source Management** (one data source per regional database, e.g., `ds_mysql_pos_north`, `ds_mysql_pos_south`)
2. Create a new task in Studio **Development → Multi-Table Real-Time Sync**, select the sync mode:
   - **Full-database mirror**: syncs at database granularity, auto-adapts to new tables — suitable for initial full-database ingestion
   - **Multi-table mirror**: syncs selected tables — suitable when only some tables are needed
3. Configure the source data source; select the target workspace and schema (`best_practice_retail_pos`)
4. Set `sync_mode` to **full + incremental**: on first run it pulls all historical data then switches to CDC
5. Submit the task and manually start it in Studio

After starting, the task goes through: initialization → full sync → incremental CDC. The end-to-end latency in the CDC phase is seconds. Multiple regional databases can have separate tasks, all writing to tables in the same target schema.

> 💡 **Tip**: If MySQL CDC is not configured yet, you can write sample data directly with `INSERT INTO`. The downstream Dynamic Table and query logic will be identical. The table and data examples below use the INSERT approach for demonstration.

### Create Tables

**Store master data table (partitioned table)**

```sql
CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_stores (
    store_id INT,
    city     STRING
);
```

**Product dimension tables**

```sql
CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_categories (
    category_id   INT,
    category_name STRING
);

CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_products (
    product_id  INT,
    category_id INT,
    supplier_id INT,
    price       DOUBLE
);

CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_promotions (
    promotion_id INT,
    discount     INT    -- discount percentage; e.g., 24 means a 24% discount (pay 76%)
);
```

**Customer and order tables**

```sql
CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_customers (
    customer_id INT,
    city        STRING,
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_orders (
    order_id     INT,
    customer_id  INT,
    store_id     INT,
    order_date   DATE,
    promotion_id INT
)
PARTITIONED BY (store_id);

CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_order_items (
    order_item_id INT,
    order_id      INT,
    product_id    INT,
    qty           INT,
    price         DOUBLE
);
```

**Payment and return tables**

```sql
CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_payments (
    payment_id INT,
    order_id   INT,
    amount     DOUBLE
);

CREATE TABLE IF NOT EXISTS best_practice_retail_pos.doc_ods_returns (
    return_id     INT,
    order_item_id INT,
    refund        DOUBLE
);
```

### Load Data

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). If you prefer not to use the command line, you can run the SQL in **Singdata Studio → Development → SQL Editor** and configure / trigger scheduling tasks on the **Studio → Tasks** page.

Import Kaggle CSV files via cz-cli (replace with PIPE automatic ingestion in actual projects).

**Import from a local CSV file (recommended)**

Save each table's data as a CSV file and bulk-import via User Volume:

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/stores.csv' TO USER VOLUME FILE 'stores.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_retail_pos.doc_ods_stores
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('stores.csv');
```

Repeat the above steps for the remaining tables (`doc_ods_orders`, `doc_ods_order_items`, `doc_ods_products`, `doc_ods_customers`, `doc_ods_payments`, `doc_ods_returns`, etc.), uploading each corresponding CSV file and running COPY INTO.

You can also insert a small batch of test data inline (no CSV file required):

```sql
-- Example: insert store master data (100 stores)
INSERT INTO best_practice_retail_pos.doc_ods_stores VALUES
(1,'Pune'),(2,'Pune'),(3,'Delhi'),(4,'Mumbai'),(5,'Mumbai'),
-- ... 100 rows total
(100,'Delhi');

-- Insert orders (100) and order items (200)
INSERT INTO best_practice_retail_pos.doc_ods_orders VALUES
(1,45,33,CAST('2021-08-26' AS DATE),24),
(2,10,81,CAST('2022-03-19' AS DATE),3),
-- ...
(100,31,63,CAST('2022-03-30' AS DATE),33);
```

Verify ODS row counts:

```sql
SELECT
    (SELECT COUNT(*) FROM best_practice_retail_pos.doc_ods_stores)      AS stores,
    (SELECT COUNT(*) FROM best_practice_retail_pos.doc_ods_orders)      AS orders,
    (SELECT COUNT(*) FROM best_practice_retail_pos.doc_ods_order_items) AS items,
    (SELECT COUNT(*) FROM best_practice_retail_pos.doc_ods_products)    AS products,
    (SELECT COUNT(*) FROM best_practice_retail_pos.doc_ods_payments)    AS payments,
    (SELECT COUNT(*) FROM best_practice_retail_pos.doc_ods_returns)     AS returns;
```

```
stores | orders | items | products | payments | returns
-------+--------+-------+----------+----------+--------
100    | 100    | 200   | 100      | 100      | 20
```

### Create Bloomfilter Index

Filtering order items by `product_id` is a high-frequency operation (SKU sales rankings, fast/slow-moving analysis). With `product_id` cardinality in the range of the product count, a Bloomfilter Index is a good fit:

```sql
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_product_id
ON TABLE doc_ods_order_items (product_id);
```

> ⚠️ **Note**: `CREATE BLOOMFILTER INDEX` requires the same Schema context as the target table. Run `USE SCHEMA` first or use the `-s` parameter; otherwise you see an "index and table must in the same schema" error.

### External Schema: Access Hive Historical Data

When historical archive data remains in a Hive cluster, use External Schema to query it directly without migration:

```sql
-- Step 1: Create a Catalog Connection pointing to the Hive Metastore
CREATE CATALOG CONNECTION IF NOT EXISTS conn_hive_pos
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://hive-metastore:9083'
    STORAGE_CONNECTION = 'conn_oss_archive';

-- Step 2: Mount the Hive database as an External Schema
CREATE EXTERNAL SCHEMA IF NOT EXISTS pos_hive_archive
    CONNECTION conn_hive_pos
    OPTIONS (SCHEMA = 'pos_archive_db');

-- Step 3: Query historical archived orders directly (two-level naming, like local tables)
SELECT order_id, store_id, order_date, total_amount
FROM pos_hive_archive.historical_orders
WHERE store_id = 33
  AND order_date >= CAST('2019-01-01' AS DATE)
ORDER BY order_date DESC
LIMIT 5;
```

> ⚠️ **Note**: Tables under External Schema support **SELECT queries only** — INSERT / UPDATE / DELETE are not supported. To backfill historical data into a Lakehouse local table, run `INSERT INTO best_practice_retail_pos.doc_ods_orders SELECT ... FROM pos_hive_archive.historical_orders`.

---

## DWD (Detail Data Layer): Standardized Sales Detail

The DWD layer joins multiple ODS fact tables with dimension tables, derives discounted amounts and return flags, and creates a complete view for each transaction.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_retail_pos.doc_dwd_sales_detail
AS
SELECT
    oi.order_item_id,
    o.order_id,
    o.store_id,
    s.city                                              AS store_city,
    o.order_date,
    o.customer_id,
    c.city                                              AS customer_city,
    oi.product_id,
    p.category_id,
    cat.category_name,
    p.price                                             AS list_price,
    oi.qty,
    oi.price                                            AS unit_price,
    CAST(oi.qty * oi.price AS DOUBLE)                  AS gross_amount,
    COALESCE(pr.discount, 0)                            AS discount_pct,
    ROUND(oi.qty * oi.price * (1.0 - COALESCE(pr.discount, 0) / 100.0), 2) AS net_amount,
    CASE WHEN r.return_id IS NOT NULL THEN 1 ELSE 0 END AS is_returned,
    COALESCE(r.refund, 0)                               AS refund_amount
FROM best_practice_retail_pos.doc_ods_order_items oi
JOIN best_practice_retail_pos.doc_ods_orders      o   ON oi.order_id    = o.order_id
JOIN best_practice_retail_pos.doc_ods_stores      s   ON o.store_id     = s.store_id
JOIN best_practice_retail_pos.doc_ods_customers   c   ON o.customer_id  = c.customer_id
JOIN best_practice_retail_pos.doc_ods_products    p   ON oi.product_id  = p.product_id
JOIN best_practice_retail_pos.doc_ods_categories  cat ON p.category_id  = cat.category_id
LEFT JOIN best_practice_retail_pos.doc_ods_promotions pr ON o.promotion_id = pr.promotion_id
LEFT JOIN best_practice_retail_pos.doc_ods_returns    r  ON oi.order_item_id = r.order_item_id;
```

> ⚠️ **Note**: `CREATE DYNAMIC TABLE` DDL does not include `REFRESH INTERVAL`. Refresh scheduling is managed through Studio Tasks (see below), which lets you attach data quality checks and alert rules to the same task.

Trigger the initial refresh manually:

```sql
REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_dwd_sales_detail;
```

Verify results:

```sql
SELECT COUNT(*) AS dwd_rows FROM best_practice_retail_pos.doc_dwd_sales_detail;
```

```
dwd_rows
--------
200
```

View the first few rows to verify `net_amount` discount calculation is correct:

```sql
SELECT order_item_id, store_id, store_city, order_date,
       product_id, category_name, qty, unit_price,
       gross_amount, discount_pct, net_amount, is_returned
FROM best_practice_retail_pos.doc_dwd_sales_detail
ORDER BY order_item_id
LIMIT 5;
```

```
order_item_id | store_id | store_city | order_date | product_id | category_name | qty | unit_price | gross_amount | discount_pct | net_amount | is_returned
--------------+----------+------------+------------+------------+---------------+-----+------------+--------------+--------------+------------+-------------
1             | 33       | Delhi      | 2021-08-26 | 72         | Cat_12        | 3   | 176        | 528          | 5            | 501.6      | 0
2             | 33       | Delhi      | 2021-08-26 | 10         | Cat_29        | 2   | 316        | 632          | 5            | 600.4      | 0
3             | 81       | Mumbai     | 2022-03-19 | 45         | Cat_16        | 1   | 1345       | 1345         | 27           | 981.85     | 0
4             | 17       | Delhi      | 2021-01-21 | 23         | Cat_15        | 4   | 2116       | 8464         | 34           | 5586.24    | 0
5             | 85       | Hyderabad  | 2021-01-16 | 87         | Cat_24        | 2   | 4567       | 9134         | 22           | 7124.52    | 0
```

**Result interpretation**: Row 4 (product 23, promotion discount 34%) has `net_amount` (5586.24) = `8464 × (1 - 0.34)` — the discount calculation is correct. Row 3 has `is_returned = 0`, indicating no return for that order item; the LEFT JOIN on `doc_ods_returns` returned NULL which the `CASE WHEN` converted to 0.

---

## DWS (Summary Data Layer): Daily Store Sales Summary

The DWS layer summarizes DWD detail at store + transaction date granularity, supporting daily reports, weekly trends, and period-over-period analysis.

### Store Daily Summary Dynamic Table

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_retail_pos.doc_dws_store_daily_sales
AS
SELECT
    store_id,
    store_city,
    order_date,
    COUNT(DISTINCT order_id)     AS order_count,
    COUNT(order_item_id)         AS item_count,
    SUM(qty)                     AS total_qty,
    ROUND(SUM(gross_amount), 2)  AS gross_revenue,
    ROUND(SUM(net_amount), 2)    AS net_revenue,
    ROUND(AVG(discount_pct), 2)  AS avg_discount_pct,
    SUM(is_returned)             AS return_count,
    ROUND(SUM(refund_amount), 2) AS total_refund,
    COUNT(DISTINCT product_id)   AS sku_count
FROM best_practice_retail_pos.doc_dwd_sales_detail
GROUP BY store_id, store_city, order_date;
```

```sql
REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_dws_store_daily_sales;

SELECT store_id, store_city, order_date, order_count, total_qty,
       gross_revenue, net_revenue, avg_discount_pct, return_count, sku_count
FROM best_practice_retail_pos.doc_dws_store_daily_sales
ORDER BY net_revenue DESC
LIMIT 8;
```

```
store_id | store_city | order_date | order_count | total_qty | gross_revenue | net_revenue | avg_discount_pct | return_count | sku_count
---------+------------+------------+-------------+-----------+---------------+-------------+------------------+--------------+----------
17       | Delhi      | 2021-12-09 | 1           | 6         | 25089         | 22830.99    | 9                | 0            | 2
24       | Pune       | 2021-08-05 | 1           | 6         | 22694         | 21105.42    | 7                | 0            | 2
68       | Pune       | 2022-01-14 | 1           | 5         | 21725         | 20638.75    | 5                | 0            | 2
54       | Bangalore  | 2021-04-26 | 1           | 7         | 21983         | 19564.87    | 11               | 0            | 2
43       | Bangalore  | 2022-08-17 | 1           | 5         | 20948         | 18853.2     | 10               | 0            | 2
1        | Pune       | 2023-11-27 | 1           | 6         | 22167         | 18398.61    | 17               | 0            | 2
99       | Bangalore  | 2022-02-04 | 1           | 5         | 18178         | 17087.32    | 6                | 0            | 2
55       | Hyderabad  | 2022-11-06 | 1           | 9         | 31919         | 16934.26    | 25.5             | 0            | 2
```

**Result interpretation**: Delhi store 17 (2021-12-09) tops the single-day net revenue at ¥22,831 with a discount rate of only 9%, indicating this store maintains low promotional intensity around holidays but achieves a high average order value. Hyderabad store 55 (discount rate 25.5%) has higher transaction volume (qty=9) but net revenue is compressed by discounts.

### Refresh by Store Static Partition

When you need to precisely backfill data for a specific store and month, use `PARTITIONED BY (store_id)` + `SESSION_CONFIGS` parameterized partitions:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_retail_pos.doc_dws_store_date_partition (
    store_id, order_date, order_count, item_count, total_qty, net_revenue
)
PARTITIONED BY (store_id)
AS
SELECT
    store_id,
    order_date,
    COUNT(DISTINCT order_id)   AS order_count,
    COUNT(order_item_id)       AS item_count,
    SUM(qty)                   AS total_qty,
    ROUND(SUM(net_amount), 2)  AS net_revenue
FROM best_practice_retail_pos.doc_dwd_sales_detail
WHERE store_id = CAST(SESSION_CONFIGS()['dt.args.store_id'] AS INT)
GROUP BY store_id, order_date;
```

> ⚠️ **Note**: Partitioned Dynamic Tables must explicitly declare `PARTITIONED BY`; automatic partition inference cannot be relied on. `SESSION_CONFIGS()['dt.args.xxx']` returns a STRING type and must be `CAST` to the target type (INT / DATE, etc.) before matching the partition column; otherwise you get a type incompatibility error during refresh.

Refresh the partition data for store 33:

```sql
SET dt.args.store_id = 33;
REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_dws_store_date_partition
    PARTITION (store_id = 33);
```

```sql
SELECT * FROM best_practice_retail_pos.doc_dws_store_date_partition
WHERE store_id = 33;
```

```
store_id | order_date | order_count | item_count | total_qty | net_revenue
---------+------------+-------------+------------+-----------+------------
33       | 2021-08-26 | 1           | 3          | 6         | 5335.2
```

Each refresh only updates the specified store partition without affecting other stores — suitable for parallel multi-store backfill scenarios.

### Configure Studio Refresh Tasks

DWD and DWS layer refresh is scheduled through Studio Tasks — do not set `REFRESH INTERVAL` in the DDL:

```bash
# Create DWD refresh task
cz-cli task create refresh_dwd_sales_detail --type SQL -p skill_test
# Example return: {"data":{"id":10353698,...}}

# Save SQL content
cz-cli task save-content 10353698 \
    --content "REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_dwd_sales_detail;" \
    -p skill_test

# Set schedule: run daily at 01:30
cz-cli task save-cron 10353698 --cron "0 30 1 * * ?" -p skill_test

# Create DWS refresh task (same steps)
cz-cli task create refresh_dws_store_daily --type SQL -p skill_test
# task id: 10354652
cz-cli task save-content 10354652 \
    --content "REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_dws_store_daily_sales;" \
    -p skill_test
cz-cli task save-cron 10354652 --cron "0 30 1 * * ?" -p skill_test
```

> 💡 **Tip**: Studio Task supports configuring data quality checks (e.g., `net_revenue > 0`) and alert notifications on the same task. If `doc_dws_store_daily_sales` has zero rows after a DWD refresh on a given day, set an alert on the task to trigger a notification.

---

## ADS (Application Data Layer): Fast/Slow-Moving SKU Analysis and Store Rankings

### SKU Sales Velocity Analysis

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_retail_pos.doc_ads_sku_velocity
AS
SELECT
    product_id,
    category_id,
    category_name,
    SUM(qty)                                                   AS total_sold_qty,
    COUNT(DISTINCT order_id)                                   AS order_count,
    ROUND(SUM(net_amount), 2)                                  AS total_net_revenue,
    COUNT(DISTINCT store_id)                                   AS store_coverage,
    SUM(is_returned)                                           AS return_count,
    ROUND(SUM(is_returned) * 100.0 / NULLIF(COUNT(*), 0), 2) AS return_rate_pct,
    CASE
        WHEN SUM(qty) >= 10 THEN 'fast_moving'
        WHEN SUM(qty) >= 5  THEN 'normal'
        ELSE 'slow_moving'
    END                                                        AS velocity_label,
    ROUND(SUM(net_amount) / NULLIF(COUNT(DISTINCT store_id), 0), 2) AS revenue_per_store
FROM best_practice_retail_pos.doc_dwd_sales_detail
GROUP BY product_id, category_id, category_name;
```

```sql
REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_ads_sku_velocity;

-- View SKU count and revenue distribution by velocity tier
SELECT velocity_label, COUNT(*) AS sku_count,
       ROUND(SUM(total_net_revenue), 2) AS label_revenue
FROM best_practice_retail_pos.doc_ads_sku_velocity
GROUP BY velocity_label
ORDER BY label_revenue DESC;
```

```
velocity_label | sku_count | label_revenue
---------------+-----------+--------------
normal         | 37        | 520537.33
slow_moving    | 61        | 392062.88
```

**Result interpretation**: Of 100 SKUs, 37 are normal-moving (qty 5–9) and 61 are slow-moving (qty < 5). Slow-moving SKUs contributed ¥392,062 in net revenue — about 43% of total. This shows that high-priced slow-moving items still contribute meaningful revenue. Procurement decisions should consider both `total_net_revenue` and `total_sold_qty`, not just sales volume.

View the top 10 fastest-moving SKUs:

```sql
SELECT product_id, category_name, total_sold_qty, order_count,
       total_net_revenue, store_coverage, velocity_label
FROM best_practice_retail_pos.doc_ads_sku_velocity
ORDER BY total_sold_qty DESC
LIMIT 10;
```

```
product_id | category_name | total_sold_qty | order_count | total_net_revenue | store_coverage | velocity_label
-----------+---------------+----------------+-------------+-------------------+----------------+---------------
60         | Cat_30        | 9              | 3           | 7922.28           | 3              | normal
12         | Cat_14        | 9              | 3           | 27547.1           | 3              | normal
37         | Cat_24        | 8              | 3           | 12089             | 3              | normal
87         | Cat_24        | 8              | 4           | 31740.65          | 4              | normal
23         | Cat_15        | 8              | 3           | 10833.92          | 3              | normal
65         | Cat_11        | 7              | 2           | 16566.66          | 2              | normal
56         | Cat_2         | 7              | 3           | 23981.55          | 3              | normal
30         | Cat_4         | 7              | 2           | 11288.1           | 2              | normal
55         | Cat_13        | 7              | 3           | 20519.61          | 3              | normal
14         | Cat_10        | 7              | 3           | 15307.11          | 3              | normal
```

View the slowest-moving SKUs (priority candidates for clearance):

```sql
SELECT product_id, category_name, total_sold_qty, total_net_revenue,
       store_coverage, return_rate_pct, velocity_label
FROM best_practice_retail_pos.doc_ads_sku_velocity
WHERE velocity_label = 'slow_moving'
ORDER BY total_sold_qty ASC, total_net_revenue ASC
LIMIT 8;
```

```
product_id | category_name | total_sold_qty | total_net_revenue | store_coverage | return_rate_pct | velocity_label
-----------+---------------+----------------+-------------------+----------------+-----------------+---------------
54         | Cat_20        | 1              | 2360.82           | 1              | 0.00            | slow_moving
66         | Cat_22        | 1              | 2599.1            | 1              | 0.00            | slow_moving
2          | Cat_18        | 1              | 2835.88           | 1              | 0.00            | slow_moving
20         | Cat_27        | 2              | 954.8             | 2              | 0.00            | slow_moving
89         | Cat_29        | 2              | 2218.36           | 1              | 0.00            | slow_moving
49         | Cat_18        | 2              | 2468.82           | 1              | 0.00            | slow_moving
70         | Cat_3         | 2              | 2620.8            | 2              | 0.00            | slow_moving
98         | Cat_3         | 2              | 2649.92           | 2              | 0.00            | slow_moving
```

**Result interpretation**: Product 20 (Cat_27) sold only 2 units at about ¥477 each — a typical low-price, low-sales double-slow item and a priority candidate for promotional clearance. Products 54 / 66 / 2 each completed only 1 sale in 1 store; consider removing them from shelves or redistributing to high-traffic stores for a trial.

### Store Revenue Rankings

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_retail_pos.doc_ads_store_ranking
AS
SELECT
    store_id,
    store_city,
    SUM(order_count)                AS total_orders,
    SUM(item_count)                 AS total_items,
    SUM(total_qty)                  AS total_qty,
    ROUND(SUM(gross_revenue), 2)    AS gross_revenue,
    ROUND(SUM(net_revenue), 2)      AS net_revenue,
    ROUND(AVG(avg_discount_pct), 2) AS avg_discount_pct,
    SUM(return_count)               AS total_returns,
    ROUND(SUM(return_count) * 100.0 / NULLIF(SUM(item_count), 0), 2) AS return_rate_pct,
    RANK() OVER (ORDER BY SUM(net_revenue) DESC) AS revenue_rank
FROM best_practice_retail_pos.doc_dws_store_daily_sales
GROUP BY store_id, store_city;
```

```sql
REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_ads_store_ranking;

SELECT store_id, store_city, total_orders, total_qty,
       gross_revenue, net_revenue, avg_discount_pct,
       total_returns, return_rate_pct, revenue_rank
FROM best_practice_retail_pos.doc_ads_store_ranking
ORDER BY revenue_rank
LIMIT 10;
```

```
store_id | store_city | total_orders | total_qty | gross_revenue | net_revenue | avg_discount_pct | total_returns | return_rate_pct | revenue_rank
---------+------------+--------------+-----------+---------------+-------------+------------------+---------------+-----------------+-------------
85       | Hyderabad  | 3            | 11        | 41227         | 31331.48    | 24.33            | 1             | 16.67           | 1
17       | Delhi      | 2            | 11        | 37009         | 30698.19    | 21.5             | 0             | 0.00            | 2
54       | Bangalore  | 2            | 12        | 30081         | 25719.35    | 17.5             | 0             | 0.00            | 3
55       | Hyderabad  | 2            | 9         | 31919         | 24637.9     | 25.5             | 0             | 0.00            | 4
87       | Delhi      | 2            | 12        | 36889         | 24199.49    | 34               | 1             | 25.00           | 5
81       | Mumbai     | 2            | 9         | 29513         | 21114.41    | 28               | 0             | 0.00            | 6
24       | Pune       | 1            | 6         | 22694         | 21105.42    | 7                | 0             | 0.00            | 7
68       | Pune       | 1            | 5         | 21725         | 20638.75    | 5                | 0             | 0.00            | 8
11       | Delhi      | 2            | 10        | 22606         | 19327.32    | 18               | 0             | 0.00            | 9
43       | Bangalore  | 1            | 5         | 20948         | 18853.2     | 10               | 0             | 0.00            | 10
```

**Result interpretation**:
- Hyderabad store 85 (rank 1) has net revenue of ¥31,331, but `avg_discount_pct = 24.33` (high discount rate) with a return rate of 16.67%. High revenue has quality concerns — review the high-return SKU mix.
- Delhi store 17 (rank 2) has a discount rate of only 21.5% and a return rate of 0% — a genuinely high-quality store, suitable as an operational benchmark to learn from.
- Delhi store 87 (rank 5) has a 34% discount rate and 25% return rate. High-promotion-driven high revenue is unsustainable; gradually adjusting the promotional strategy is advisable.

Configure ADS layer refresh tasks:

```bash
cz-cli task create refresh_ads_sku_velocity --type SQL -p skill_test
# task id: 10353699
cz-cli task save-content 10353699 \
    --content "REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_ads_sku_velocity;" \
    -p skill_test
cz-cli task save-cron 10353699 --cron "0 0 2 * * ?" -p skill_test

cz-cli task create refresh_ads_store_ranking --type SQL -p skill_test
# task id: 10354653
cz-cli task save-content 10354653 \
    --content "REFRESH DYNAMIC TABLE best_practice_retail_pos.doc_ads_store_ranking;" \
    -p skill_test
cz-cli task save-cron 10354653 --cron "0 0 2 * * ?" -p skill_test
```

Full scheduling chain: `refresh_dwd_sales_detail` (01:30) → `refresh_dws_store_daily` (01:30, depends on the previous) → `refresh_ads_*` (02:00).

---

## Time Travel: Month-End Reconciliation

During month-end financial reconciliation, you need to rewind to the order snapshot at the month-end cutoff time and compare with current data to detect orders entered after the cutoff.

```sql
-- View historical versions of the ODS orders table
DESC HISTORY best_practice_retail_pos.doc_ods_orders;
```

```
version | time                        | total_rows | operation   | stats
--------+-----------------------------+------------+-------------+----------------------------
4       | 2026-06-06T14:41:30.348     | 100        | INSERT_INTO | rows_inserted: 40
3       | 2026-06-06T14:41:15.488     | 60         | INSERT_INTO | rows_inserted: 30
2       | 2026-06-06T14:41:02.329     | 30         | INSERT_INTO | rows_inserted: 30
1       | 2026-06-06T14:38:18.807     | 0          | CREATE      | —
```

> **Scenario: month-end financial reconciliation** — assume the month-end cutoff is at version 3 (60 orders), but the system now has 100 orders. We need to identify the 40 orders entered after the cutoff:
>

```sql
-- Rewind to the store revenue snapshot at the month-end cutoff time
SELECT
    snap.order_date,
    snap.store_id,
    COUNT(*)          AS orders_in_snapshot,
    SUM(p.amount)     AS snapshot_revenue
FROM best_practice_retail_pos.doc_ods_orders TIMESTAMP AS OF '2026-06-06 14:41:15.488' snap
JOIN best_practice_retail_pos.doc_ods_payments p ON snap.order_id = p.order_id
GROUP BY snap.order_date, snap.store_id
ORDER BY snapshot_revenue DESC
LIMIT 5;
```

```
order_date | store_id | orders_in_snapshot | snapshot_revenue
-----------+----------+--------------------+-----------------
2021-04-26 | 54       | 1                  | 13688
2022-03-08 | 87       | 1                  | 12036
2023-11-15 | 100      | 1                  | 11156
2020-11-14 | 57       | 1                  | 9702
2023-11-27 | 1        | 1                  | 9465
```

```sql
-- Find orders entered after the month-end cutoff (present in current DB but absent from historical snapshot)
SELECT o_cur.order_id, o_cur.store_id, o_cur.order_date
FROM best_practice_retail_pos.doc_ods_orders o_cur
LEFT JOIN (
    SELECT order_id
    FROM best_practice_retail_pos.doc_ods_orders
    TIMESTAMP AS OF '2026-06-06 14:41:15.488'
) snap ON o_cur.order_id = snap.order_id
WHERE snap.order_id IS NULL
ORDER BY o_cur.order_id
LIMIT 10;
```

```
order_id | store_id | order_date
---------+----------+-----------
61       | 46       | 2022-04-07
62       | 89       | 2023-09-22
63       | 13       | 2021-05-16
64       | 71       | 2022-12-30
65       | 38       | 2023-04-14
66       | 92       | 2021-06-28
67       | 27       | 2022-01-12
68       | 50       | 2023-05-27
69       | 65       | 2021-07-11
70       | 3        | 2022-02-25
```

**Result interpretation**: `order_id` 61–100, totaling 40 orders, were entered after the month-end cutoff. Submit these order IDs to finance for review to decide whether to include them in the current month's accounting or roll them over to the next month — this is the core value of Time Travel in month-end reconciliation scenarios.

> 💡 **Tip**: `TIMESTAMP AS OF` accepts literal constants (e.g., `'2026-06-06 14:41:15.488'`) — **expressions** like `NOW() - INTERVAL 30 DAY` are **not supported**. If you need relative time, first compute the specific timestamp with `SELECT CURRENT_TIMESTAMP() - INTERVAL 30 DAYS`, then use it in the query.

---

## Data Warehouse Object Summary

All objects in the `best_practice_retail_pos` schema:

```sql
SHOW TABLES IN best_practice_retail_pos;
```

```
schema_name              | table_name                      | is_dynamic
-------------------------+---------------------------------+-----------
best_practice_retail_pos | doc_ods_stores                  | false
best_practice_retail_pos | doc_ods_categories              | false
best_practice_retail_pos | doc_ods_products                | false
best_practice_retail_pos | doc_ods_promotions              | false
best_practice_retail_pos | doc_ods_customers               | false
best_practice_retail_pos | doc_ods_orders                  | false
best_practice_retail_pos | doc_ods_order_items             | false
best_practice_retail_pos | doc_ods_payments                | false
best_practice_retail_pos | doc_ods_returns                 | false
best_practice_retail_pos | doc_dwd_sales_detail            | true
best_practice_retail_pos | doc_dws_store_daily_sales       | true
best_practice_retail_pos | doc_dws_store_date_partition    | true
best_practice_retail_pos | doc_ads_sku_velocity            | true
best_practice_retail_pos | doc_ads_store_ranking           | true
```

---

## Notes

- **Bloomfilter Index does not automatically apply to existing data**: `CREATE BLOOMFILTER INDEX` only speeds up data written after the index is created. For existing data, you need to either rebuild the table or accept that Bloomfilter acceleration will not apply to existing rows.

- **Partitioned Dynamic Tables must explicitly declare `PARTITIONED BY`**: Automatic system inference of partition columns cannot be relied on. `SESSION_CONFIGS()['dt.args.xxx']` returns STRING and must be `CAST` to the target type before matching the partition column; otherwise you get a type incompatibility error during refresh.

- **`REFRESH DYNAMIC TABLE` does not use `REFRESH INTERVAL`**: All Dynamic Table periodic refresh is managed through Studio Tasks. Studio Tasks support attaching data quality rules and alerts to the same task. Setting `REFRESH INTERVAL` in the DDL bypasses this management mechanism.

- **Time Travel `TIMESTAMP AS OF` only accepts constants**: Expressions like `NOW() - INTERVAL N DAY` at runtime are not supported. Pre-compute the target timestamp before calling. `DESC HISTORY` returns UTC time; add 8 hours to convert to local time (UTC+8).

- **External Schema is read-only**: External tables under `pos_hive_archive` do not support INSERT / UPDATE / DELETE. To import historical data into a Lakehouse local table, explicitly migrate it with `INSERT INTO ... SELECT ... FROM pos_hive_archive.xxx`.

- **ODS layer `doc_ods_orders` uses `PARTITIONED BY (store_id, order_date)`**: If the upstream CDC uses `INSERT OVERWRITE` (rather than `INSERT INTO`), Dynamic Tables will fall back to a full refresh. Using append-only writes (`INSERT INTO` only) preserves Dynamic Table's incremental refresh capability.

---

## Related Documentation

- [Create Dynamic Table](create-dynamic-table.md) — syntax reference and incremental refresh mechanism
- [Dynamic Table Parameterized Partition Definition](dynamic-table-parameters.md) — `PARTITIONED BY` + `SESSION_CONFIGS` full syntax
- [Create Index](create-index.md) — Bloomfilter / Inverted / Vector index syntax
- [External Catalog and External Schema](external_catalog_schema.md) — federated query entry point, Hive mounting
- [Continuous Kafka Data Ingestion with PIPE](pipe-kafka.md) — full Kafka PIPE parameter reference
- [Medallion Architecture: Pure SQL Dynamic Table Approach](lakehouse-medallion-sql-dt-guide.md) — large-scale three-layer data warehouse reference