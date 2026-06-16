# Real-Time Sales Dashboard: Building a Multi-Layer Incremental Data Warehouse with Dynamic Tables

## Business Context

E-commerce operations teams face a common challenge every day: during a promotion, GMV and rankings across categories are changing in real time, but the data dashboard only refreshes the next day. Missing real-time data means missing the window to adjust campaign strategy — a category is already selling out, but the decisions to restock and boost spend have to wait until tomorrow.

The traditional solution is to write a scheduled SQL job that recalculates everything from scratch every minute. This approach has two problems:

- **Wasted computation**: Every run scans all historical orders. The larger the data, the slower it gets, and cost grows linearly with data volume.
- **Operational burden**: You have to manage scheduling yourself, handle task failure retries, and ensure idempotency.

![](/.topwrite/assets/29-realtime-sales-dashboard.svg)

The value of Dynamic Tables is this: you write SQL with full-scan semantics, and the system automatically identifies new data and only computes the changed portion — it never recomputes history. If data volume grows 10x, the cost of incremental computation stays the same.

## Use Cases

| Scenario | Description |
|----------|-------------|
| Real-time sales leaderboard | Category/product/store GMV rankings, updated by the minute |
| Promotion monitoring | Track SKU sales and inventory consumption in real time during campaigns |
| Automated daily operations report | Daily GMV, order count, and average order value summarized automatically — no manual queries needed |
| Multi-layer data warehouse maintenance | Full-chain incremental refresh across ODS → DWD → ADS, replacing scheduled full-scan jobs |

## SQL Commands Involved

| Command | Purpose |
|---------|---------|
| `CREATE DYNAMIC TABLE` | Define a table that refreshes automatically |
| `REFRESH INTERVAL` | Set the data update frequency |
| `SHOW DYNAMIC TABLE REFRESH HISTORY` | View refresh status and duration for each layer |
| `DROP DYNAMIC TABLE` | Clean up resources |

## Data Architecture

A three-layer Dynamic Table pipeline, each layer refreshing every 1 minute:

```
External data source (MySQL / Kafka / object storage / ...)
              │  real-time writes
              ▼
doc_orders          doc_products
    └──────────────────┘
              │  JOIN
              ▼
   doc_dwd_order_detail     ← DWD: enriched orders (adds category, brand)
              │
              ▼
   doc_ads_category_gmv     ← ADS: category GMV summary + average price
              │
              ▼
   doc_ads_category_rank    ← ADS: real-time category leaderboard
```

**How data is written to the base tables in real time**

This guide uses `INSERT INTO` to simulate data writes so you can reproduce the example quickly in a test environment. In production, order data typically comes from a business database or message queue. Singdata Lakehouse provides several ways to continuously write to the base tables:

| Data source | Recommended approach | Reference |
|-------------|---------------------|-----------|
| MySQL / PostgreSQL / Oracle and other relational databases | Studio real-time sync task (CDC) | [Real-time sync task](realtime_sync.md) |
| Multiple business tables in one migration | Studio multi-table real-time sync | [Multi-table real-time sync task](multitable_realtime_sync.md) |
| Kafka message queue | Pipe continuous ingestion | [Continuous ingestion via read_kafka function](pipe-kafka.md) |
| Object storage (OSS / COS / S3) files | Pipe continuous ingestion | [Continuous ingestion from object storage with Pipe](pipe-storage-object.md) |
| Offline batch sync (T+1 or hourly) | Studio offline sync task | [Offline sync task](batch_sync.md) |

Once new data is written to the base tables, the Dynamic Table pipeline automatically detects it at the next refresh cycle and computes incrementally — no additional configuration needed.

## Prerequisites

### Create the source tables

```sql
CREATE TABLE IF NOT EXISTS doc_orders (
    order_id   STRING,
    user_id    STRING,
    product_id STRING,
    quantity   INT,
    unit_price DECIMAL(10,2),
    amount     DECIMAL(10,2),
    order_time TIMESTAMP,
    status     STRING
);

CREATE TABLE IF NOT EXISTS doc_products (
    product_id   STRING,
    product_name STRING,
    category     STRING,
    brand        STRING
);
```

### Insert initial data

```sql
INSERT INTO doc_products VALUES
  ('P001', 'Wireless Bluetooth Earbuds', 'Electronics', 'SoundMax'),
  ('P002', 'Mechanical Keyboard',        'Computer Peripherals', 'KeyPro'),
  ('P003', 'Running Shoes',              'Sports & Outdoors', 'SpeedRun'),
  ('P004', 'Yoga Mat',                   'Sports & Outdoors', 'FlexFit'),
  ('P005', 'Insulated Tumbler',          'Home & Living', 'ThermoKeep'),
  ('P006', 'USB-C Charger',              'Electronics', 'ChargeFast'),
  ('P007', 'Laptop Stand',               'Computer Peripherals', 'DeskPro'),
  ('P008', 'Jump Rope',                  'Sports & Outdoors', 'JumpFit');

INSERT INTO doc_orders VALUES
  ('O001','U101','P001',2,299.00,598.00, CAST('2026-05-28 16:00:00' AS TIMESTAMP),'completed'),
  ('O002','U102','P002',1,459.00,459.00, CAST('2026-05-28 16:05:00' AS TIMESTAMP),'completed'),
  ('O003','U103','P003',1,389.00,389.00, CAST('2026-05-28 16:10:00' AS TIMESTAMP),'completed'),
  ('O004','U104','P001',1,299.00,299.00, CAST('2026-05-28 16:15:00' AS TIMESTAMP),'completed'),
  ('O005','U105','P004',2,128.00,256.00, CAST('2026-05-28 16:20:00' AS TIMESTAMP),'completed'),
  ('O006','U106','P005',3, 89.00,267.00, CAST('2026-05-28 16:25:00' AS TIMESTAMP),'completed'),
  ('O007','U107','P006',2,129.00,258.00, CAST('2026-05-28 16:30:00' AS TIMESTAMP),'completed'),
  ('O008','U108','P003',2,389.00,778.00, CAST('2026-05-28 16:35:00' AS TIMESTAMP),'completed'),
  ('O009','U109','P007',1,199.00,199.00, CAST('2026-05-28 16:40:00' AS TIMESTAMP),'completed'),
  ('O010','U110','P008',3, 49.00,147.00, CAST('2026-05-28 16:45:00' AS TIMESTAMP),'completed');
```

> ⚠️ **Note**: TIMESTAMP columns must be inserted using `CAST('...' AS TIMESTAMP)`. String literals cannot be written directly.

## Scenario 1: Create the Three-Layer Dynamic Tables

### Layer 1 (DWD): Enrich Orders

Join the orders table with the products table to add category and brand information, keeping only completed orders.

```sql
CREATE OR REPLACE DYNAMIC TABLE doc_dwd_order_detail
REFRESH INTERVAL '1' MINUTE VCLUSTER DEFAULT
AS
SELECT
    o.order_id,
    o.user_id,
    o.product_id,
    p.product_name,
    p.category,
    p.brand,
    o.quantity,
    o.unit_price,
    o.amount,
    o.order_time,
    o.status
FROM doc_orders o
JOIN doc_products p ON o.product_id = p.product_id
WHERE o.status = 'completed';
```

### Layer 2 (ADS): Category GMV Summary

Aggregate by category to compute order count, total quantity, GMV, and average price.

```sql
CREATE OR REPLACE DYNAMIC TABLE doc_ads_category_gmv
REFRESH INTERVAL '1' MINUTE VCLUSTER DEFAULT
AS
SELECT
    category,
    COUNT(DISTINCT order_id)                              AS order_cnt,
    SUM(quantity)                                         AS total_qty,
    SUM(amount)                                           AS gmv,
    CAST(SUM(amount) / SUM(quantity) AS DECIMAL(10,2))   AS avg_price
FROM doc_dwd_order_detail
GROUP BY category;
```

> ⚠️ **Note**: Average price must be computed with `CAST(SUM(amount) / SUM(quantity) AS DECIMAL(10,2))` to explicitly specify precision. Using `ROUND(SUM(amount)/SUM(quantity), 2)` directly will trigger an optimizer type inference error.

### Layer 3 (ADS): Category Leaderboard

Compute real-time rankings based on the GMV summary table.

```sql
CREATE OR REPLACE DYNAMIC TABLE doc_ads_category_rank
REFRESH INTERVAL '1' MINUTE VCLUSTER DEFAULT
AS
SELECT
    RANK() OVER (ORDER BY gmv DESC) AS gmv_rank,
    category,
    order_cnt,
    total_qty,
    gmv,
    avg_price
FROM doc_ads_category_gmv;
```

> ⚠️ **Note**: A Dynamic Table will not have data immediately after creation. The first refresh is triggered within about 1 minute of creation. In practice, the DWD layer and the GMV layer refresh in the same batch, while the rank layer detects the change in the next cycle, resulting in an end-to-end latency of about 1–2 minutes.

### Verify Initial Results

Wait about 2 minutes, then query the leaderboard:

```sql
SELECT * FROM doc_ads_category_rank ORDER BY gmv_rank;
```

```
+--------+---------------------+-----------+-----------+---------+-----------+
|gmv_rank|category             |order_cnt  |total_qty  |gmv      |avg_price  |
+--------+---------------------+-----------+-----------+---------+-----------+
|       1|Sports & Outdoors    |          4|          8|  1570.00|     196.25|
|       2|Electronics          |          3|          5|  1155.00|     231.00|
|       3|Computer Peripherals |          2|          2|   658.00|     329.00|
|       4|Home & Living        |          1|          3|   267.00|      89.00|
+--------+---------------------+-----------+-----------+---------+-----------+
```

Sports & Outdoors ranks first with 1570 in GMV, from 4 orders across running shoes (2 orders), yoga mat (1 order), and jump rope (1 order), with an average price of 196.25.

## Scenario 2: New Orders Written, Rankings Update Automatically

Simulate the next batch of orders coming in — Electronics and Computer Peripherals each have new orders:

```sql
INSERT INTO doc_orders VALUES
  ('O011','U111','P005',2, 89.00,178.00, CAST('2026-05-28 17:00:00' AS TIMESTAMP),'completed'),
  ('O012','U112','P006',3,129.00,387.00, CAST('2026-05-28 17:02:00' AS TIMESTAMP),'completed'),
  ('O013','U113','P001',1,299.00,299.00, CAST('2026-05-28 17:05:00' AS TIMESTAMP),'completed'),
  ('O014','U114','P004',1,128.00,128.00, CAST('2026-05-28 17:08:00' AS TIMESTAMP),'completed'),
  ('O015','U115','P002',2,459.00,918.00, CAST('2026-05-28 17:10:00' AS TIMESTAMP),'completed');
```

Wait about 2 minutes, then query the leaderboard again:

```sql
SELECT * FROM doc_ads_category_rank ORDER BY gmv_rank;
```

```
+--------+---------------------+-----------+-----------+---------+-----------+
|gmv_rank|category             |order_cnt  |total_qty  |gmv      |avg_price  |
+--------+---------------------+-----------+-----------+---------+-----------+
|       1|Electronics          |          5|          9|  1841.00|     204.56|
|       2|Sports & Outdoors    |          5|          9|  1698.00|     188.67|
|       3|Computer Peripherals |          3|          4|  1576.00|     394.00|
|       4|Home & Living        |          2|          5|   445.00|      89.00|
+--------+---------------------+-----------+-----------+---------+-----------+
```

Electronics added an insulated tumbler (178), USB-C charger (387), and wireless earbuds (299) for a total of 686 in new GMV, rising from 1155 to 1841 and overtaking Sports & Outdoors to claim first place. The ranking change is computed automatically by the system — no manual intervention required.

## Scenario 3: Modify a Dynamic Table Definition

When business requirements change, you can update the SQL logic with `CREATE OR REPLACE DYNAMIC TABLE`. Existing data will not be lost.

**Changes suitable for OR REPLACE**: modifying WHERE filter conditions, adding pass-through columns (columns that come directly from upstream without any computation).

**Changes that require DROP + recreate**: modifying column types, modifying aggregation logic (e.g., adding a computed column like `avg_price`).

> ⚠️ **Note**: OR REPLACE does not allow changing the type of an existing column — it will raise `NotAllowed: cannot replace <col> from type X to Y`. To change a column type, you must DROP and recreate the table.

After OR REPLACE, if no new data has been written upstream, the system will not recompute existing rows — the new column values will remain null until the next refresh is triggered by new data.

## View Refresh Status

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'doc_ads_category_rank' LIMIT 5;
```

Example output from a real run:

| state | refresh_mode | start_time | rows_inserted | Meaning |
|-------|-------------|------------|---------------|---------|
| SUCCEED | INCREMENTAL | 18:11:48 | 4 | Normal incremental refresh, 4 rows written |
| SUCCEED | NO_DATA | 18:12:48 | — | No new data upstream, computation skipped |
| FAILED | FULL | 18:09:41 | — | Full refresh failed, see error_message |

Key field descriptions:

| Field | Meaning |
|-------|---------|
| `state` | `SUCCEED` success / `FAILED` failure |
| `refresh_mode` | `INCREMENTAL` incremental / `FULL` full scan / `NO_DATA` no new data, skipped |
| `refresh_trigger` | `SYSTEM_SCHEDULED` automatic / `MANUAL` manually triggered |
| `start_time` / `end_time` | Refresh start and end time |
| `stats` | `rows_inserted` / `rows_deleted` — rows written and deleted in this refresh |
| `error_message` | Error details when state is FAILED |

## Behavior When an Upstream Table Is Dropped

When an upstream Dynamic Table is dropped, downstream Dynamic Tables will not error out or cascade-delete. Their refresh state changes to `NO_DATA` and the objects continue to exist.

```sql
-- Drop the DWD layer
DROP DYNAMIC TABLE IF EXISTS doc_dwd_order_detail;

-- The GMV layer still exists, but refreshes become NO_DATA
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'doc_ads_category_gmv' LIMIT 3;
-- state: SUCCEED, refresh_mode: NO_DATA
```

This means: if you accidentally drop an upstream Dynamic Table, downstream data will not disappear. Once the upstream is recreated, the downstream will automatically resume incremental computation at the next refresh cycle.

## Clean Up Resources

```sql
DROP DYNAMIC TABLE IF EXISTS doc_ads_category_rank;
DROP DYNAMIC TABLE IF EXISTS doc_ads_category_gmv;
DROP DYNAMIC TABLE IF EXISTS doc_dwd_order_detail;
DROP TABLE IF EXISTS doc_orders;
DROP TABLE IF EXISTS doc_products;
```

> 💡 **Tip**: The DROP order does not affect the outcome — any order will succeed.

## Key Takeaways

- **Write full-scan SQL, let the system handle incremental computation**: The SQL for all three Dynamic Table layers is plain SELECT — no incremental logic needed. The system automatically identifies new data and only computes the changed portion.
- **Changes propagate through the pipeline automatically**: New data in the source table → DWD layer refreshes → ADS summary layer refreshes → leaderboard updates. The entire pipeline requires no manual triggering.
- **End-to-end latency is about 1–2 minutes**: In practice, the DWD and GMV layers refresh in the same batch, and the rank layer detects the change in the next cycle, giving an end-to-end latency of about 1–2 minutes when the refresh interval is set to 1 minute.
- **OR REPLACE has limitations**: Column types cannot be changed, and modifying aggregation logic requires DROP + recreate. After OR REPLACE, if no new data arrives upstream, new column values will be null until the next refresh.

## Related Documentation

- [Dynamic Table Overview](dynamic-table.md)
- [CREATE DYNAMIC TABLE](create-dynamic-table.md)
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md)
- [SHOW DYNAMIC TABLE REFRESH HISTORY](refresh-history.md)
