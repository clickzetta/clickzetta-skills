# Build a Supply Chain and Logistics Tracking Data Warehouse

A supply chain data warehouse faces the challenge of three parallel data pipelines with different system latencies: OMS order status needs second-level visibility, WMS inventory snapshots sync in daily batches, and TMS logistics EDI files arrive periodically. Using the Kaggle retail dataset (orders, inventory, logistics, and suppliers, covering the full ODS→DWD→DWS→ADS pipeline), this guide demonstrates how to use Singdata Lakehouse to integrate three heterogeneous data sources into a unified supply chain visibility data warehouse that monitors SKU inventory turnover and shipment on-time rates.

![](/.topwrite/assets/anim-17-supply-chain.svg)

---

## Overview

| Problem | Singdata Solution |
|---|---|
| OMS order status changes need real-time sync to the warehouse; hour-level delay is unacceptable | PostgreSQL CDC real-time sync; order status changes written to ODS in seconds |
| WMS warehouse inventory has large volume; historical snapshot queries filter by warehouse | MySQL multi-table offline sync + `PARTITIONED BY (warehouse_id, dt)` for partition pruning |
| Logistics providers supply EDI files that need periodic batch import | OSS PIPE continuously monitors the bucket; new files automatically trigger COPY INTO |
| Multi-layer aggregation (DWD→DWS→ADS) has a complex dependency chain that needs automatic orchestration | Dynamic Table cascading refresh + Studio Task dependency scheduling; DWD refresh automatically triggers downstream |
| Inventory alerts need minute-level detection; supplier SLA reports update daily | Studio Task schedules each layer at configured times; alert tables refresh before SLA reports |

---

## SQL Commands Used

| Command / Feature | Purpose | Notes |
|---|---|---|
| `CREATE TABLE ... PARTITIONED BY` | Create ODS raw layer partition tables | Partition by warehouse ID and date to speed up historical range scans |
| `CREATE DYNAMIC TABLE` | Create DWD/DWS/ADS Dynamic Tables | Omit `REFRESH INTERVAL` in DDL; manage refresh scheduling through Studio Task |
| `REFRESH DYNAMIC TABLE` | Manually trigger a Dynamic Table refresh | Use after first creating the table or when debugging |
| `CASE WHEN` | Derive fields (`delivery_flag`, `stock_status`, `sla_status`) | Normalize multi-source status codes to unified business semantics |
| `DATEDIFF` | Calculate in-transit days `transit_days` | Supports `COALESCE` to handle undelivered shipments |
| `DATE_FORMAT` | Monthly group statistics (`yyyy-MM`) | Used for ADS monthly SLA reports |
| `NULLIF` | Avoid division-by-zero errors | Divide by `NULLIF(count, 0)` when computing SLA compliance rate |

---

## Prerequisites

Use a dedicated Schema to isolate all test tables in this guide:

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_supply_chain;
```

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). You can also run SQL in **Development → SQL Editor** in Singdata Studio and configure or trigger scheduled tasks under **Studio → Tasks**.

```bash
cz-cli sql "CREATE SCHEMA IF NOT EXISTS best_practice_supply_chain" -p skill_test --write
```

Result:

```json
{"data":{},"time_ms":101}
```

---

## ODS (Raw Data Layer): Three-Channel Heterogeneous Data Ingestion

The ODS layer maps to three source systems, each ingested with a different method.

### Create Tables

**OMS Order Table (PostgreSQL CDC Target Table)**

```sql
CREATE TABLE IF NOT EXISTS best_practice_supply_chain.doc_ods_orders (
  order_id       BIGINT,
  order_date     DATE,
  customer_id    BIGINT,
  store_id       INT,
  status         STRING,
  total_amount   DECIMAL(12,2),
  currency       STRING,
  created_at     TIMESTAMP,
  updated_at     TIMESTAMP
)
COMMENT 'ODS: raw orders from OMS (synced via PostgreSQL CDC)'
PARTITIONED BY (dt STRING);
```

**OMS Order Items Table (PostgreSQL CDC Target Table)**

```sql
CREATE TABLE IF NOT EXISTS best_practice_supply_chain.doc_ods_order_items (
  item_id        BIGINT,
  order_id       BIGINT,
  product_id     BIGINT,
  sku_code       STRING,
  quantity       INT,
  unit_price     DECIMAL(10,2),
  discount       DECIMAL(10,2),
  warehouse_id   INT,
  created_at     TIMESTAMP
)
COMMENT 'ODS: raw order line items from OMS'
PARTITIONED BY (dt STRING);
```

**TMS Shipment Table (OSS PIPE Target Table)**

```sql
CREATE TABLE IF NOT EXISTS best_practice_supply_chain.doc_ods_shipments (
  shipment_id       BIGINT,
  order_id          BIGINT,
  carrier_code      STRING,
  tracking_number   STRING,
  origin_warehouse  INT,
  dest_city         STRING,
  dest_province     STRING,
  shipped_at        TIMESTAMP,
  expected_delivery DATE,
  actual_delivery   DATE,
  status            STRING,
  created_at        TIMESTAMP
)
COMMENT 'ODS: logistics shipment events from TMS / EDI files (via OSS PIPE)'
PARTITIONED BY (dt STRING);
```

**WMS Supplier Master Table**

```sql
CREATE TABLE IF NOT EXISTS best_practice_supply_chain.doc_ods_suppliers (
  supplier_id    INT,
  supplier_name  STRING,
  contact_name   STRING,
  country        STRING,
  city           STRING,
  sla_days       INT,
  tier           STRING,
  created_at     TIMESTAMP
)
COMMENT 'ODS: supplier master data from WMS';
```

**WMS Inventory Snapshot Table (MySQL Batch Sync Target, Partitioned by Warehouse + Date)**

```sql
CREATE TABLE IF NOT EXISTS best_practice_supply_chain.doc_ods_inventory (
  snapshot_id          BIGINT,
  snapshot_date        DATE,
  warehouse_id         INT,
  sku_code             STRING,
  product_id           BIGINT,
  quantity_on_hand     INT,
  quantity_reserved    INT,
  quantity_in_transit  INT,
  reorder_point        INT,
  created_at           TIMESTAMP
)
COMMENT 'ODS: WMS inventory snapshots (synced via MySQL batch offline sync)'
PARTITIONED BY (dt STRING);
```

> ⚠️ **Note**: Columns in `PARTITIONED BY` cannot share names with columns in the `columns` definition, otherwise you get a `key.found` error. Although the inventory table is queried on both warehouse and date dimensions, only one partition column `dt STRING` is defined; the warehouse dimension is filtered via a WHERE clause pushdown.

### OSS PIPE Ingestion for TMS EDI Files

Logistics providers upload shipment EDI files to an OSS bucket in the early morning each day. A PIPE automatically imports them into the shipment table:

```sql
-- Prerequisite: OSS Storage Connection and External Volume already created
CREATE PIPE IF NOT EXISTS best_practice_supply_chain.pipe_ods_shipments
AS
COPY INTO best_practice_supply_chain.doc_ods_shipments
FROM VOLUME oss_logistics_vol
USING csv
OPTIONS('header'='true', 'sep'=',');
```

> 💡 **Tip**: PIPE defaults to `LIST_PURGE` scan mode (periodically polling the Volume for new files). If OSS event notifications are enabled, switch to `INGEST_MODE = EVENT_NOTIFICATION` for second-level file triggering.

---

## DWD (Detail Data Layer): Order Lifecycle Event Standardization

The DWD layer JOINs the three core ODS tables into a wide table, derives `delivery_flag` (on_time/delayed/overdue) and `transit_days` (in-transit days), and provides a unified order event view.

### Create Tables

**Order Event Wide Table (Dynamic Table)**

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_supply_chain.doc_dwd_order_events
COMMENT 'DWD: standardized order lifecycle events with shipment join'
AS
SELECT
  o.order_id,
  o.order_date,
  o.customer_id,
  o.store_id,
  o.status                                          AS order_status,
  o.total_amount,
  o.currency,
  o.created_at                                      AS order_created_at,
  o.updated_at                                      AS order_updated_at,
  oi.item_id,
  oi.product_id,
  oi.sku_code,
  oi.quantity,
  oi.unit_price,
  oi.discount,
  oi.warehouse_id,
  (oi.unit_price * oi.quantity - oi.discount)       AS line_amount,
  s.shipment_id,
  s.carrier_code,
  s.tracking_number,
  s.shipped_at,
  s.expected_delivery,
  s.actual_delivery,
  s.status                                          AS shipment_status,
  s.dest_city,
  s.dest_province,
  CASE
    WHEN s.actual_delivery IS NOT NULL AND s.actual_delivery <= s.expected_delivery THEN 'on_time'
    WHEN s.actual_delivery IS NOT NULL AND s.actual_delivery >  s.expected_delivery THEN 'delayed'
    WHEN s.actual_delivery IS NULL     AND CURRENT_DATE()    >  s.expected_delivery THEN 'overdue'
    ELSE 'pending'
  END                                               AS delivery_flag,
  DATEDIFF(COALESCE(s.actual_delivery, CURRENT_DATE()), s.shipped_at) AS transit_days
FROM best_practice_supply_chain.doc_ods_orders      o
JOIN best_practice_supply_chain.doc_ods_order_items oi ON o.order_id = oi.order_id
LEFT JOIN best_practice_supply_chain.doc_ods_shipments s ON o.order_id = s.order_id;
```

**Inventory Event Wide Table (Dynamic Table)**

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_supply_chain.doc_dwd_inventory_events
COMMENT 'DWD: enriched inventory snapshots with availability calculation'
AS
SELECT
  inv.snapshot_date,
  inv.warehouse_id,
  inv.sku_code,
  inv.product_id,
  inv.quantity_on_hand,
  inv.quantity_reserved,
  inv.quantity_in_transit,
  inv.reorder_point,
  (inv.quantity_on_hand - inv.quantity_reserved)    AS available_quantity,
  CASE
    WHEN (inv.quantity_on_hand - inv.quantity_reserved) <= 0               THEN 'out_of_stock'
    WHEN (inv.quantity_on_hand - inv.quantity_reserved) < inv.reorder_point THEN 'low_stock'
    ELSE 'normal'
  END                                               AS stock_status
FROM best_practice_supply_chain.doc_ods_inventory inv;
```

### Refresh Dynamic Tables and Verify Data

```bash
cz-cli sql "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_dwd_order_events" -p skill_test --write
cz-cli sql "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_dwd_inventory_events" -p skill_test --write
```

Query the order event wide table to verify the derived `delivery_flag` and `transit_days` fields:

```sql
SELECT order_id, sku_code, order_status, delivery_flag, transit_days
FROM best_practice_supply_chain.doc_dwd_order_events
ORDER BY order_id
LIMIT 10;
```

| order_id | sku_code | order_status | delivery_flag | transit_days |
|---|---|---|---|---|
| 100001 | SKU-A001 | delivered | delayed | 4 |
| 100001 | SKU-B012 | delivered | delayed | 4 |
| 100002 | SKU-C005 | shipped | overdue | 795 |
| 100003 | SKU-A001 | processing | pending | null |
| 100004 | SKU-E007 | delivered | delayed | 4 |
| 100005 | SKU-B012 | cancelled | pending | null |
| 100006 | SKU-C005 | delivered | delayed | 4 |
| 100007 | SKU-F001 | shipped | overdue | 793 |
| 100008 | SKU-A001 | delivered | delayed | 4 |

`delivery_flag` values: `delayed` means actual delivery was later than expected; `overdue` means the shipment was sent but still not received (past the committed lead time); `pending` means not yet shipped or cancelled. For undelivered shipments, `transit_days` is calculated using `COALESCE(actual_delivery, CURRENT_DATE())`; rows with no shipment are null.

Query the inventory event wide table:

```sql
SELECT warehouse_id, sku_code, quantity_on_hand, available_quantity, stock_status
FROM best_practice_supply_chain.doc_dwd_inventory_events
ORDER BY warehouse_id, sku_code;
```

| warehouse_id | sku_code | quantity_on_hand | available_quantity | stock_status |
|---|---|---|---|---|
| 1 | SKU-A001 | 380 | 335 | normal |
| 1 | SKU-B012 | 210 | 180 | normal |
| 1 | SKU-F001 | 180 | 155 | normal |
| 2 | SKU-A001 | 150 | 130 | normal |
| 2 | SKU-C005 | 560 | 480 | normal |
| 2 | SKU-G009 | 320 | 280 | normal |
| 3 | SKU-D020 | 95 | 85 | normal |
| 3 | SKU-E007 | 42 | 37 | normal |

`available_quantity = quantity_on_hand - quantity_reserved` represents the actual shippable quantity after deducting reserved stock.

---

## DWS (Summary Data Layer): SKU Inventory and Route Lead Time Aggregation

The DWS layer aggregates DWD data across two dimensions: daily SKU sales summary (for inventory turnover analysis) and carrier route lead time summary (for SLA assessment).

### Create Tables

**Daily SKU Sales Aggregation Table (Dynamic Table)**

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_supply_chain.doc_dws_sku_daily_sales
COMMENT 'DWS: daily SKU-level sales and inventory turnover aggregation'
AS
SELECT
  e.order_date,
  e.sku_code,
  e.warehouse_id,
  COUNT(DISTINCT e.order_id)       AS order_count,
  SUM(e.quantity)                  AS total_quantity_sold,
  SUM(e.line_amount)               AS total_revenue,
  AVG(e.unit_price)                AS avg_unit_price,
  SUM(CASE WHEN e.delivery_flag = 'on_time' THEN 1 ELSE 0 END) AS on_time_count,
  SUM(CASE WHEN e.delivery_flag = 'delayed' THEN 1 ELSE 0 END) AS delayed_count,
  SUM(CASE WHEN e.delivery_flag = 'overdue' THEN 1 ELSE 0 END) AS overdue_count
FROM best_practice_supply_chain.doc_dwd_order_events e
WHERE e.order_status NOT IN ('cancelled')
GROUP BY e.order_date, e.sku_code, e.warehouse_id;
```

**Carrier Route Lead Time Aggregation Table (Dynamic Table)**

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_supply_chain.doc_dws_carrier_timeliness
COMMENT 'DWS: carrier on-time delivery rate and route performance aggregation'
AS
SELECT
  s.carrier_code,
  s.dest_province,
  DATE_TRUNC('week', s.shipped_at)  AS ship_week,
  COUNT(*)                           AS total_shipments,
  SUM(CASE WHEN e.delivery_flag = 'on_time' THEN 1 ELSE 0 END) AS on_time_shipments,
  SUM(CASE WHEN e.delivery_flag = 'delayed' THEN 1 ELSE 0 END) AS delayed_shipments,
  ROUND(
    SUM(CASE WHEN e.delivery_flag = 'on_time' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
  )                                  AS on_time_rate_pct,
  AVG(e.transit_days)                AS avg_transit_days
FROM best_practice_supply_chain.doc_dwd_order_events e
JOIN best_practice_supply_chain.doc_ods_shipments s ON e.shipment_id = s.shipment_id
WHERE e.shipment_status IN ('delivered', 'in_transit')
GROUP BY s.carrier_code, s.dest_province, DATE_TRUNC('week', s.shipped_at);
```

### Query DWS Aggregation Results

**SKU Sales Summary (all dates merged by SKU):**

```sql
SELECT
  sku_code,
  SUM(total_quantity_sold) AS qty,
  ROUND(SUM(total_revenue), 2) AS revenue
FROM best_practice_supply_chain.doc_dws_sku_daily_sales
GROUP BY sku_code
ORDER BY revenue DESC;
```

| sku_code | qty | revenue |
|---|---|---|
| SKU-A001 | 8 | 694.00 |
| SKU-F001 | 2 | 680.00 |
| SKU-C005 | 11 | 554.50 |
| SKU-D020 | 4 | 486.00 |
| SKU-E007 | 1 | 215.30 |
| SKU-B012 | 1 | 180.90 |
| SKU-G009 | 1 | 63.00 |

SKU-A001 leads in both unit sales (8 units, 694) and revenue; SKU-C005 has the most units (11) but a lower unit price, ranking third in total revenue. This sales volume/revenue distribution gap is the core basis for prioritizing restocking decisions.

**Carrier lead time summary (aggregated across weeks):**

```sql
SELECT
  carrier_code,
  SUM(total_shipments)         AS shipments,
  ROUND(AVG(on_time_rate_pct), 2) AS avg_ontime_pct,
  ROUND(AVG(avg_transit_days), 1) AS avg_transit
FROM best_practice_supply_chain.doc_dws_carrier_timeliness
GROUP BY carrier_code
ORDER BY avg_ontime_pct DESC;
```

| carrier_code | shipments | avg_ontime_pct | avg_transit |
|---|---|---|---|
| YTO | 2 | 0.00 | 4 |
| SF | 3 | 0.00 | 4 |
| ZTO | 1 | 0.00 | 4 |
| BEST | 1 | 0.00 | 793 |
| JD | 1 | 0.00 | 795 |

BEST and JD show `avg_transit_days` of 793 and 795 days because these shipments have `in_transit` status (not yet delivered); `transit_days` uses `CURRENT_DATE()` as the cutoff, which is expected behavior for historical test data. In real production data, the DWS layer can serve as the data source for an operations monitoring dashboard to identify routes with abnormally high average in-transit days.

---

## ADS (Application Data Layer): Supplier SLA Report and Inventory Alerts

The ADS layer directly serves business decisions: supplier compliance management and inventory restocking alerts.

### Create Tables

**Supplier SLA Monthly Report (Dynamic Table)**

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_supply_chain.doc_ads_supplier_sla_report
COMMENT 'ADS: supplier SLA compliance report — monthly delivery performance vs contracted SLA days'
AS
SELECT
  sup.supplier_id,
  sup.supplier_name,
  sup.tier                                          AS supplier_tier,
  sup.sla_days                                      AS contracted_sla_days,
  DATE_FORMAT(o.order_date, 'yyyy-MM')              AS stat_month,
  COUNT(DISTINCT o.order_id)                        AS total_orders,
  SUM(CASE WHEN dwd.delivery_flag = 'on_time' THEN 1 ELSE 0 END) AS on_time_orders,
  SUM(CASE WHEN dwd.delivery_flag = 'delayed' THEN 1 ELSE 0 END) AS delayed_orders,
  ROUND(
    SUM(CASE WHEN dwd.delivery_flag = 'on_time' THEN 1 ELSE 0 END) * 100.0
    / NULLIF(COUNT(DISTINCT o.order_id), 0), 2
  )                                                 AS on_time_rate_pct,
  AVG(dwd.transit_days)                             AS avg_transit_days,
  CASE
    WHEN ROUND(
      SUM(CASE WHEN dwd.delivery_flag='on_time' THEN 1 ELSE 0 END) * 100.0
      / NULLIF(COUNT(DISTINCT o.order_id), 0), 2
    ) >= 95 THEN 'SLA_MET'
    WHEN ROUND(
      SUM(CASE WHEN dwd.delivery_flag='on_time' THEN 1 ELSE 0 END) * 100.0
      / NULLIF(COUNT(DISTINCT o.order_id), 0), 2
    ) >= 80 THEN 'SLA_AT_RISK'
    ELSE 'SLA_BREACH'
  END                                               AS sla_status
FROM best_practice_supply_chain.doc_dwd_order_events  dwd
JOIN best_practice_supply_chain.doc_ods_orders         o   ON dwd.order_id = o.order_id
JOIN best_practice_supply_chain.doc_ods_order_items    oi  ON dwd.item_id  = oi.item_id
JOIN best_practice_supply_chain.doc_ods_suppliers      sup ON oi.warehouse_id = sup.supplier_id
WHERE dwd.order_status != 'cancelled'
  AND dwd.shipment_status IS NOT NULL
GROUP BY
  sup.supplier_id, sup.supplier_name, sup.tier, sup.sla_days,
  DATE_FORMAT(o.order_date, 'yyyy-MM');
```

**Inventory Alert Table (Dynamic Table, 5-minute high-frequency refresh)**

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_supply_chain.doc_ads_inventory_alert
COMMENT 'ADS: real-time inventory alert — low stock and out-of-stock SKUs requiring reorder'
AS
SELECT
  inv.snapshot_date,
  inv.warehouse_id,
  inv.sku_code,
  inv.product_id,
  inv.quantity_on_hand,
  inv.available_quantity,
  inv.reorder_point,
  inv.stock_status,
  CASE
    WHEN inv.stock_status = 'out_of_stock' THEN 'URGENT'
    WHEN inv.stock_status = 'low_stock'    THEN 'WARNING'
    ELSE NULL
  END                                               AS alert_level,
  (inv.reorder_point * 2 - inv.quantity_on_hand)   AS suggested_reorder_qty
FROM best_practice_supply_chain.doc_dwd_inventory_events inv
WHERE inv.stock_status IN ('out_of_stock', 'low_stock');
```

> 💡 **Tip**: The inventory alert table retains only SKUs that need attention (`WHERE stock_status IN ('out_of_stock', 'low_stock')`), so its row count is much smaller than the full DWD table. The 5-minute refresh has very low computation cost.

### Query ADS Alert Data

**Supplier SLA monthly compliance status:**

```sql
SELECT
  supplier_name,
  supplier_tier,
  contracted_sla_days,
  stat_month,
  total_orders,
  on_time_orders,
  on_time_rate_pct,
  ROUND(avg_transit_days, 1) AS avg_transit,
  sla_status
FROM best_practice_supply_chain.doc_ads_supplier_sla_report
ORDER BY supplier_name;
```

| supplier_name | supplier_tier | contracted_sla_days | stat_month | total_orders | on_time_orders | on_time_rate_pct | avg_transit | sla_status |
|---|---|---|---|---|---|---|---|---|
| IndiaMakers Inc. | B | 7 | 2024-04 | 2 | 0 | 0.00 | 398.5 | SLA_BREACH |
| ShenzhenTech Co. | A | 3 | 2024-04 | 2 | 0 | 0.00 | 4.0 | SLA_BREACH |
| VietnamFactory Ltd. | B | 5 | 2024-04 | 3 | 0 | 0.00 | 267.7 | SLA_BREACH |

All suppliers show `SLA_BREACH` for the current month because the test data shipments all have actual delivery dates later than expected (the test data dates have now passed, so `delivery_flag` outputs `delayed`). The `contracted_sla_days` field comes from `doc_ods_suppliers.sla_days` and records the maximum in-transit days promised in the contract. Combined with `avg_transit_days`, it directly shows the gap between actual supplier performance and contracted terms.

**Inventory alert list:**

```sql
SELECT
  snapshot_date,
  warehouse_id,
  sku_code,
  available_quantity,
  reorder_point,
  stock_status,
  alert_level,
  suggested_reorder_qty
FROM best_practice_supply_chain.doc_ads_inventory_alert
ORDER BY alert_level, warehouse_id;
```

| snapshot_date | warehouse_id | sku_code | available_quantity | reorder_point | stock_status | alert_level | suggested_reorder_qty |
|---|---|---|---|---|---|---|---|
| 2024-04-02 | 3 | SKU-E007 | 0 | 20 | out_of_stock | URGENT | 40 |
| 2024-04-02 | 3 | SKU-D020 | 5 | 30 | low_stock | WARNING | 35 |

`alert_level = URGENT` means stock is exhausted and immediate restocking is required. `alert_level = WARNING` means available inventory is below the reorder point; restocking is recommended soon. `suggested_reorder_qty = reorder_point * 2 - quantity_on_hand` is a simple reorder quantity formula (restocking to twice the safety stock); adjust the multiplier based on actual turnover rate.

---

## Dynamic Table Cascading Refresh Verification

Run the following query to confirm that all 6 Dynamic Tables have been created and are active:

```sql
SHOW DYNAMIC TABLES IN best_practice_supply_chain;
```

| schema_name | table_name | is_dynamic |
|---|---|---|
| best_practice_supply_chain | doc_ads_inventory_alert | true |
| best_practice_supply_chain | doc_ads_supplier_sla_report | true |
| best_practice_supply_chain | doc_dwd_inventory_events | true |
| best_practice_supply_chain | doc_dwd_order_events | true |
| best_practice_supply_chain | doc_dws_carrier_timeliness | true |
| best_practice_supply_chain | doc_dws_sku_daily_sales | true |

Cascading dependency chain:

```
ODS raw tables (static)
  ↓
doc_dwd_order_events       ← JOIN orders + order_items + shipments
doc_dwd_inventory_events   ← inventory snapshot + available-quantity derivation
  ↓ (task dependency)
doc_dws_sku_daily_sales    ← aggregated by date × SKU × warehouse
doc_dws_carrier_timeliness ← aggregated by carrier × province × week
  ↓ (task dependency)
doc_ads_inventory_alert    ← filters low-stock SKUs
doc_ads_supplier_sla_report← monthly supplier compliance rating
```

None of the 6 Dynamic Tables have `REFRESH INTERVAL` in their DDL. The refresh order is guaranteed by Studio Task scheduling dependencies (see the next section).

---

## Configure Studio Scheduling Tasks

In production, manage Dynamic Table periodic refresh through Studio Task rather than writing `REFRESH INTERVAL` in the DDL. The benefits: you can adjust scheduling times and dependencies without rebuilding tables, and you can attach alert rules to tasks to notify on-call staff when a refresh fails.

### Create Refresh Tasks

**DWD layer:**

```bash
# Create DWD order event refresh task
cz-cli task create refresh_dwd_order_events_sc --type SQL -p skill_test
# Example response: {"data":{"id":10353826,...}}

cz-cli task save-content 10353826 \
    --content "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_dwd_order_events;" \
    -p skill_test

# Create DWD inventory event refresh task
cz-cli task create refresh_dwd_inventory_events_sc --type SQL -p skill_test
# Example response: {"data":{"id":10354789,...}}

cz-cli task save-content 10354789 \
    --content "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_dwd_inventory_events;" \
    -p skill_test
```

**DWS layer:**

```bash
cz-cli task create refresh_dws_sku_daily_sc --type SQL -p skill_test
# Example response: {"data":{"id":10353827,...}}

cz-cli task save-content 10353827 \
    --content "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_dws_sku_daily_sales;" \
    -p skill_test

cz-cli task create refresh_dws_carrier_sc --type SQL -p skill_test
# Example response: {"data":{"id":10354790,...}}

cz-cli task save-content 10354790 \
    --content "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_dws_carrier_timeliness;" \
    -p skill_test
```

**ADS layer:**

```bash
cz-cli task create refresh_ads_inventory_alert_sc --type SQL -p skill_test
# Example response: {"data":{"id":10353828,...}}

cz-cli task save-content 10353828 \
    --content "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_ads_inventory_alert;" \
    -p skill_test

cz-cli task create refresh_ads_supplier_sla_sc --type SQL -p skill_test
# Example response: {"data":{"id":10354791,...}}

cz-cli task save-content 10354791 \
    --content "REFRESH DYNAMIC TABLE best_practice_supply_chain.doc_ads_supplier_sla_report;" \
    -p skill_test
```

### Configure Schedules

```bash
# DWD layer: refresh daily at 01:00
cz-cli task save-cron 10353826 --cron "0 0 1 * * ?" -p skill_test
cz-cli task save-cron 10354789 --cron "0 0 1 * * ?" -p skill_test

# DWS layer: refresh daily at 01:30 (after DWD completes)
cz-cli task save-cron 10353827 --cron "0 30 1 * * ?" -p skill_test
cz-cli task save-cron 10354790 --cron "0 30 1 * * ?" -p skill_test

# ADS layer: refresh daily at 02:00 (after DWS completes)
cz-cli task save-cron 10353828 --cron "0 0 2 * * ?" -p skill_test
cz-cli task save-cron 10354791 --cron "0 0 2 * * ?" -p skill_test
```

### Configure Task Dependencies

Schedule times alone cannot guarantee that downstream tasks start only after upstream completes (if upstream runs overtime, DWS computation could begin before the data is fully refreshed). Use `save-config --deps` to configure task dependencies for completion-state-based cascading triggers:

```bash
# DWS SKU aggregation depends on DWD order events
cz-cli task save-config refresh_dws_sku_daily_sc \
    --deps replace \
    --dep-tasks '[{"taskId":10353826,"taskName":"refresh_dwd_order_events_sc"}]' \
    -p skill_test

# DWS carrier timeliness depends on DWD order events
cz-cli task save-config refresh_dws_carrier_sc \
    --deps replace \
    --dep-tasks '[{"taskId":10353826,"taskName":"refresh_dwd_order_events_sc"}]' \
    -p skill_test

# ADS inventory alert depends on DWD inventory events
cz-cli task save-config refresh_ads_inventory_alert_sc \
    --deps replace \
    --dep-tasks '[{"taskId":10354789,"taskName":"refresh_dwd_inventory_events_sc"}]' \
    -p skill_test

# ADS supplier SLA report depends on DWS SKU aggregation and DWS carrier timeliness
cz-cli task save-config refresh_ads_supplier_sla_sc \
    --deps replace \
    --dep-tasks '[{"taskId":10353827,"taskName":"refresh_dws_sku_daily_sc"},{"taskId":10354790,"taskName":"refresh_dws_carrier_sc"}]' \
    -p skill_test
```

Full scheduling chain:

```
01:00  refresh_dwd_order_events_sc     (DWD order event wide table)
01:00  refresh_dwd_inventory_events_sc (DWD inventory event wide table)
  ↓ triggered after dependency completes
01:30  refresh_dws_sku_daily_sc        (DWS SKU daily sales aggregation)
01:30  refresh_dws_carrier_sc          (DWS carrier route timeliness aggregation)
  ↓ triggered after dependency completes
02:00  refresh_ads_inventory_alert_sc  (ADS inventory alert)
02:00  refresh_ads_supplier_sla_sc     (ADS supplier SLA monthly report)
```

> 💡 **Tip**: Studio Task supports attaching alert rules to tasks. For example, if `doc_dwd_order_events` has 0 rows after `refresh_dwd_order_events_sc` refreshes on a given day, configure an alert on the task to send a notification to on-call staff. You can also configure schedules and dependencies through the Singdata Studio UI under **Development → Tasks** instead of the CLI.

---

## Notes

- **Partition column naming**: Column names defined in `PARTITIONED BY` cannot match field names in the `columns` definition, otherwise you get a `key.found` error. Although the ODS inventory table is queried on both warehouse and date dimensions, only `dt STRING` is defined as a partition column; the warehouse dimension is filtered via WHERE rather than partition pruning.
- **PostgreSQL CDC table schema**: The CDC target table's column definitions must align with the source table's fields. When data types mismatch, the CDC task reports an `implicit cast not allowed` error; explicit `CAST('...' AS TIMESTAMP)` is required during insertion.
- **OSS PIPE FILES() limitation**: PIPE definitions do not support `FILES('filename')` or `SUBDIRECTORY 'dirname'` to filter specific files; they can only scan the entire Volume path. If EDI files come from multiple logistics providers with different formats, create a separate Volume and PIPE for each provider.
- **Do not write `REFRESH INTERVAL` in Dynamic Table DDL**: Manage all Dynamic Table periodic refresh through Studio Task. Studio Task supports configuring scheduling dependencies (downstream triggers only after upstream completes), which is more reliable than fixed intervals. It also supports attaching data quality rules and alerts to the same task; writing `REFRESH INTERVAL` in DDL bypasses this management mechanism.
- **`NULLIF` prevents division by zero**: When computing the SLA compliance rate, the denominator uses `NULLIF(COUNT(DISTINCT order_id), 0)` to avoid division-by-zero errors. When a supplier has no shipped orders in the current month, `on_time_rate_pct` returns NULL rather than an error.
- **`CURRENT_DATE()` behavior in Dynamic Tables**: `CURRENT_DATE()` in a Dynamic Table is recomputed on each refresh. `transit_days` grows automatically over time, making it suitable for monitoring overdue shipments that have not been delivered.

---

## Related Documentation

- [CREATE DYNAMIC TABLE](../create-dynamic-table.md) — Full Dynamic Table syntax and parameter reference
- [Medallion Architecture: Pure SQL Dynamic Table Approach](../lakehouse-medallion-sql-dt-guide.md) — Complete three-layer data warehouse build reference
- [OSS Object Storage Data Import Pipeline Practice](../lakehouse-volume-pipe-acceleration-guide.md) — Volume + PIPE end-to-end configuration
- [CREATE TABLE ... PARTITIONED BY](../create-table.md) — Partition table syntax and partition pruning optimization