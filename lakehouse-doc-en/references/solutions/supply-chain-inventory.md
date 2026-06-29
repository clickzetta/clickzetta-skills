# Supply Chain Inventory Optimization
> **Core Capabilities**: Window Functions · Dynamic Table · MERGE INTO · AI_COMPLETE · AI_CLASSIFY  
> **Industries**: Manufacturing · Retail · E-commerce · Medical Devices · FMCG

---

## Business Background

Inventory management in manufacturing spans the entire supply chain: raw material procurement → work-in-progress → finished goods warehouse → regional distribution centers → retail outlets. Every node must balance **stockouts** against **overstocking that ties up capital**.

As global supply chain complexity increases — multi-warehouse layouts, multi-SKU management, seasonal demand fluctuations, unstable supplier lead times — the static safety-stock models that traditional ERP/MRP systems rely on can no longer cope with real-world challenges.

**Core Data Sources**:

```
WMS (Warehouse Management System)  → supply_chain_inventory        Daily inventory snapshots, safety stock thresholds
OMS (Order Management System)      → supply_chain_demand            Historical sales, daily shipment volumes
ERP/MRP                            → supply_chain_inventory fields  Replenishment cycles, BOM materials (static parameters)
Supplier Systems                   → supply_chain_supplier_lead_time Real-time lead times, delay notifications
```

These data sources are scattered across multiple systems and are difficult to aggregate for real-time analysis. Procurement and supply chain teams rely on manual reports and weekly summaries, making it impossible to respond the moment inventory runs critically low.

---

## Industry Pain Points

### 1. Static Safety Stock Cannot Adapt to Demand Fluctuations

Safety stock in traditional MRP systems is a one-time static setting that does not adjust automatically with seasons, promotions, or market changes. **The industry average for inventory days on hand is 60–90 days, with slow-moving inventory tying up roughly 15–20% of working capital**.

### 2. Replenishment Decisions Are Delayed and Rely on Manual Judgment

Buyers managing hundreds of SKUs make replenishment decisions based on experience and Excel. When demand suddenly spikes, by the time reports are generated, meetings held, and purchase orders approved, stockouts may have already lasted several days — with rush shipping fees on top.

### 3. Unbalanced Multi-Warehouse Inventory Makes Transfer Decisions Difficult

It is common for the same SKU to be overstocked at one warehouse while out-of-stock at another. Cross-warehouse transfers involve logistics costs, inventory age prioritization, and in-transit tracking; manual decisions are inefficient, and teams often prefer to reorder rather than transfer.

### 4. Low Demand Forecast Accuracy, Unable to Detect Anomalies

Traditional moving-average methods cannot account for holiday effects, competitor launches, or promotional lifts. Demand anomalies can only be reviewed after the fact.

### 5. Supplier Lead Time Variability Not Incorporated into Replenishment Decisions

The `lead_time_days` field in ERP is a static setting, and supplier delay information cannot be updated automatically. Replenishment plans use "what the lead time should be" rather than "what it actually will be," systematically underestimating stockout risk.

---

## Data Source Details

### WMS — Inventory Snapshots (→ `supply_chain_inventory`)

| Company Size | Typical Products | Recommended Ingestion Method |
|-------------|-----------------|------------------------------|
| Large | SAP EWM, Oracle WMS Cloud, Manhattan WMS | API / CDC real-time push |
| Mid-size | Kuangshi Lanche, Kejie Logistics, Hongjing WMS | Scheduled CSV export → `COPY INTO` |
| Small | Guanyiyun, Wangdiantong | MySQL CDC (see [03-mysql-cdc-sync](../../06-migration-guides/03-mysql-cdc-sync/)) |

ERP replenishment parameters (`lead_time_days`, `reorder_point`) change infrequently (monthly); merge them with the inventory snapshot on write, and recommend a daily full overwrite.

### OMS — Historical Demand (→ `supply_chain_demand`)

| Company Size | Typical Products | Recommended Ingestion Method |
|-------------|-----------------|------------------------------|
| Large manufacturers | SAP SD, Oracle Order Management | BAPI/RFC or DB sync |
| E-commerce / Retail | Wangdiantong, Guanyiyun, Tmall/JD ERP | Platform open API scheduled pull |
| B2B Manufacturing | Kingdee Cloud Xingkong, Yonyou U9 | Custom API or direct DB connection |

When demand data covers fewer than 7 days, `urgency` is automatically set to "Insufficient Data" and no replenishment suggestion is triggered, preventing erroneous actions.

### Supplier Systems — Real-Time Lead Times (→ `supply_chain_supplier_lead_time`)

| Data Source | Ingestion Method |
|-------------|----------------|
| Supplier SRM portal | API / EDI |
| Logistics tracking platform | Cainiao / AfterShip open API |
| Supplier emails / notifications | `AI_EXTRACT` structured parsing, auto-written to lead time table |

```sql
-- Use AI_EXTRACT to automatically extract new lead times from supplier notifications
SELECT AI_EXTRACT(
    'cz_bailian:qwen3.5-plus',
    supplier_notice_text,
    JSON '{"product_id":        "Material number",
           "new_lead_time_days": "New estimated delivery days (integer)",
           "reason":             "Reason for delay"}'
) AS extracted_info
FROM supplier_notices
WHERE notice_date >= CURRENT_DATE - INTERVAL 7 DAY;
```

`supply_chain_replenishment_plan` prioritizes the latest record in this table over the ERP static value. The `lead_time_source` field records the data origin (SRM/EDI/AI_EXTRACT/ERP Static) for full traceability.

---

## Solution Based on Singdata Lakehouse

After multi-system data flows into the Lakehouse, **Dynamic Table incremental computation + window functions for multi-window analysis + real-time supplier lead time integration** form an auto-refreshing replenishment decision system.

### Overall Architecture
![Solution Architecture](/.topwrite/assets/supply-chain-inventory_architecture.svg)

```
[WMS Inventory Snapshot]    [OMS Historical Demand]    [Supplier Real-Time Lead Times]
          │                           │                           │
          ▼                           ▼                           ▼
supply_chain_inventory      supply_chain_demand      supply_chain_supplier_lead_time
(incl. ERP static params)   change_tracking=true      source: SRM/EDI/AI_EXTRACT
          │                           │                           │
          └──────────┬────────────────┘                          │
                     ▼                                           │
  supply_chain_daily_demand_avg (DT, 1h)                        │
  30-day / 7-day average daily demand · anomaly flags           │
                     │                                           │
                     ▼                                           │
  supply_chain_replenishment_plan (DT, 1h) ─────────────────────┘
  dynamic lead_time · urgency · suggested_order
  data-insufficiency guard · replenishment cost estimate
                     │
                     ├──► MERGE INTO supply_chain_replenishment (idempotent archive)
                     ├──► Urgent alerts (Studio Task → DingTalk / WeCom)
                     ├──► Procurement system integration (auto-generate PO)
                     └──► Inventory health dashboard
```

### Core Calculation Logic

```
-- Effective lead time (prefer real-time supplier value, fall back to ERP static)
effective_lead_time = COALESCE(supplier.lead_time_days, erp.lead_time_days)

-- Days of supply
days_of_supply = stock_qty / avg_daily_demand (last 30 days)

-- Urgency classification (with data-quality guard)
  demand_data_days < 7                            → Insufficient Data (no replenishment triggered)
  days_of_supply < effective_lead_time            → Urgent
  days_of_supply < effective_lead_time × 1.5      → Normal
  otherwise                                       → Healthy

-- Suggested order quantity (target: cover lead time + 7-day buffer)
suggested_order = MAX((effective_lead_time + 7) × avg_daily_demand − stock_qty, 0)

-- Demand anomaly detection (7-day vs. 30-day deviation > 30%)
demand_anomaly_flag = |avg_7d - avg_30d| / avg_30d > 0.3
```

---

## Technical Advantages

### 1. Supplier Real-Time Lead Times Dynamically Override ERP Static Values

This is the core differentiator from traditional MRP: `supply_chain_supplier_lead_time` is updated in real time, and `effective_lead_time` in `supply_chain_replenishment_plan` automatically uses the latest value. Supplier delays → the system immediately recalculates urgency, with no manual notification or ERP parameter update required.

### 2. Multi-Window Demand Trend Detection with AI-Powered Anomaly Explanation

```sql
avg_daily_demand  -- 30-day average (baseline)
avg_7d_demand     -- 7-day average (short-term trend)
When demand_anomaly_flag = TRUE, trigger AI_COMPLETE to analyze the cause: promotion / holiday / competitor / seasonal
```

### 3. Insufficient-Data Guard Prevents Large Replenishment Orders Driven by Minimal History

When `demand_data_days < 7`, urgency is set to "Insufficient Data" and no replenishment suggestion is triggered, preventing newly listed SKUs with only 1–2 days of history from generating erroneous high-frequency replenishment orders.

### 4. MERGE INTO Idempotent Archive Enables Historical Replenishment Plan Traceability

Results are automatically archived every hour. Time Travel lets you look back at replenishment recommendations at any point in time, supporting procurement decision post-mortems and accountability reviews.

### 5. Pure SQL, Low Coupling with Existing ERP/WMS

Only periodic data pushes from each system to the Lakehouse are required — no modification to existing systems. Replenishment suggestions are pushed to the procurement system via Studio Task, with a go-live timeline measured in days, not months.

---

## Customer Value

**Supply Chain / Procurement Teams**: Replenishment priorities are visible in real time; urgent SKUs trigger automatic alerts, eliminating reliance on weekly reports to discover stockouts.

**Inventory Management Teams**: `days_of_supply` visualizes health across all warehouses; multi-warehouse comparisons surface transfer opportunities, reducing redundant replenishment costs.

**Finance Teams**: The `est_replenishment_cost` field calculates replenishment amounts in real time to support cash planning, with a target of reducing inventory days on hand from 60–90 days to 30–45 days.

**IT / Digitalization Teams**: No additional Python forecasting service or dedicated inventory system is needed; the Lakehouse integrates everything in one place for unified operations.

---

## Solution Files

| File | Contents |
|------|----------|
| `setup.sql` | Create tables: inventory snapshots, historical demand, **supplier lead times**, replenishment archive |
| `test_data.sql` | Test data: 3 warehouses × 3 SKUs, 14 days of demand history, supplier delay scenarios |
| `pipeline.sql` | Core pipeline: daily demand DT → replenishment plan DT (with supplier lead time integration) → MERGE INTO |
| `teardown.sql` | Clean up all objects (Dynamic Tables before regular tables) |

---

## UAT Validation Results

> Validation date: 2026-06-05 · Environment: UAT · 3 warehouses × 3 SKUs × 14 days of demand history · Includes supplier delay scenarios

**Full Replenishment Plan Output**

| Warehouse | Product | Days of Supply | Effective Lead Time | Lead Time Source | Suggested Order | Est. Cost | Urgency |
|-----------|---------|---------------|---------------------|-----------------|----------------|-----------|---------|
| WH_SH | 27" Monitor | 1.9 days | **18 days** | **AI_EXTRACT** | 37 units | ¥35,150 | **Urgent** |
| WH_SH | Wireless Mouse M100 | 2.2 days | 5 days | SRM | 35 units | ¥875 | **Urgent** |
| WH_BJ | Wireless Mouse M100 | 1.6 days | 6 days | SRM | 108 units | ¥2,700 | **Urgent** |
| WH_BJ | Mechanical Keyboard K200 | 24.0 days | 10 days (+3 delay) | EDI | 0 | — | Healthy |
| WH_GZ | Mechanical Keyboard K200 | 16.7 days | 7 days | EDI | 0 | — | Healthy |
| WH_GZ | 27" Monitor | 22.5 days | 14 days | SRM | 0 | — | Healthy |

**Key Validation Points**

- **Supplier real-time lead time applied** ✅: WH_SH monitor `lead_time_days` extracted by AI_EXTRACT from supplier notification as 18 days (ERP static value: 14 days); the 4-day delay directly causes urgency to be marked "Urgent", suggested order 37 units · ¥35,150
- **COALESCE fallback logic correct** ✅: Real-time supplier values used when available; falls back to ERP static values when no record exists; `lead_time_source` fully records origin (SRM/EDI/AI_EXTRACT/ERP Static)
- **WH_BJ keyboard delayed but not urgent** ✅: Supplier delayed 3 days (EDI, 10 days), but inventory has 24 days of supply, `urgency=Healthy`, confirming that `COALESCE` + urgency calculation correctly distinguishes "delayed but not dangerous" from "delayed and dangerous"
- **MERGE INTO idempotent archive** ✅: 6 records successfully written to `supply_chain_replenishment`
- **Insufficient-data guard not triggered** ✅: All SKUs have ≥ 7 days of demand data; no false "Insufficient Data" flags
- **Demand anomaly detection not triggered** ✅: 7d/30d fluctuations in the 14-day test dataset do not exceed 30% (as designed)

**Supplier Lead Time Impact Analysis**

| Product | Warehouse | ERP Lead Time | Actual Lead Time | Delay Days | Source | Urgency Impact |
|---------|-----------|--------------|-----------------|-----------|--------|---------------|
| 27" Monitor | WH_SH | 14 days | 18 days | **+4** | AI_EXTRACT | Urgent (would be Normal without delay) |
| Mechanical Keyboard K200 | WH_BJ | 7 days | 10 days | **+3** | EDI | No impact (inventory sufficient) |
| Wireless Mouse M100 | WH_BJ | 7 days | 6 days | -1 | SRM | No impact (already Urgent) |

> East China warehouse (WH_SH) is most at risk: 2 SKUs both Urgent, average days of supply only 2.1 days, with the monitor particularly impacted by the supplier delay.

---

```bash
# 1. Create tables
run setup.sql

# 2. Insert test data
run test_data.sql

# 3. Create Dynamic Table pipeline
run pipeline.sql

# 4. Validate
-- Urgent replenishment list
SELECT warehouse_id, product_name, days_of_supply, effective_lead_time,
       lead_time_source, suggested_order, est_replenishment_cost
FROM supply_chain_replenishment_plan WHERE urgency = 'Urgent' ORDER BY days_of_supply;

-- Demand-anomaly SKUs
SELECT warehouse_id, product_name, avg_daily_demand, avg_7d_demand
FROM supply_chain_replenishment_plan WHERE demand_anomaly_flag = TRUE;

# 5. Teardown (optional)
run teardown.sql
```

---

## Core Queries

```sql
-- Urgent replenishment list (with real-time lead time source and replenishment cost)
SELECT warehouse_id, product_name, region,
       current_stock, avg_daily_demand, days_of_supply,
       effective_lead_time, lead_time_source,
       suggested_order, est_replenishment_cost
FROM supply_chain_replenishment_plan
WHERE urgency = 'Urgent'
ORDER BY days_of_supply ASC;

-- Inventory health overview by warehouse
SELECT warehouse_id, region,
       COUNT(*)                                                          AS sku_count,
       SUM(CASE WHEN urgency = 'Urgent'             THEN 1 ELSE 0 END)  AS urgent_count,
       SUM(CASE WHEN urgency = 'Normal'             THEN 1 ELSE 0 END)  AS normal_count,
       SUM(CASE WHEN urgency = 'Healthy'            THEN 1 ELSE 0 END)  AS healthy_count,
       SUM(CASE WHEN urgency = 'Insufficient Data'  THEN 1 ELSE 0 END)  AS data_insufficient,
       ROUND(AVG(days_of_supply), 1)                                     AS avg_days_of_supply
FROM supply_chain_replenishment_plan
GROUP BY warehouse_id, region ORDER BY urgent_count DESC;

-- Supplier delay impact analysis (real-time lead time vs. ERP static value)
SELECT p.product_name, p.warehouse_id,
       i.lead_time_days                 AS erp_lead_time,
       p.effective_lead_time            AS actual_lead_time,
       p.effective_lead_time - i.lead_time_days AS delay_days,
       p.lead_time_source,
       p.urgency
FROM supply_chain_replenishment_plan p
JOIN supply_chain_inventory i
  ON p.warehouse_id = i.warehouse_id AND p.product_id = i.product_id
  AND i.snapshot_date = (SELECT MAX(snapshot_date) FROM supply_chain_inventory)
WHERE p.lead_time_source != 'ERP Static'
ORDER BY delay_days DESC;
```

---

## Notes

**Replenishment Parameters**
- `effective_lead_time` prefers the latest record from `supply_chain_supplier_lead_time`; falls back to ERP static value when no record exists. The `lead_time_source` field labels the origin for auditability.
- The safety-stock buffer days (+7 days) are currently hard-coded; in production, extract this to a parameter table and configure it differently by ABC classification.

**Data Quality**
- When demand data covers fewer than 7 days, urgency is set to "Insufficient Data" and no replenishment suggestion is triggered.
- Inventory snapshots are written once per day; `WHERE snapshot_date = MAX(snapshot_date)` ensures only the latest snapshot is used. When multiple writes occur on the same day, pay attention to timestamp precision.
- `demand_anomaly_flag` requires both 7-day and 30-day data to be non-NULL before it triggers (already guarded); newly listed SKUs with fewer than 30 days of history will not generate false anomaly flags.

**Supplier Lead Times (UAT validated)**
- `supply_chain_supplier_lead_time` retrieves the single latest `effective_date` record per `(warehouse_id, product_id)`; only the most recent value is used when multiple updates exist.
- After AI_EXTRACT parses a supplier notification, the result must be written to `supply_chain_supplier_lead_time` before it takes effect; the Dynamic Table will use the new lead time automatically on the next REFRESH.
- "Delayed but sufficient inventory" and "Delayed and at risk" are correctly distinguished: WH_BJ keyboard delayed 3 days but has 24 days of supply, remaining "Healthy" (UAT validated).

**Dynamic Table**
- Partitioned table PRIMARY KEY must include the partition key (`snapshot_date`, `demand_date`, `effective_date`).
- Dynamic Tables do not support DML; historical data corrections must be made on the source tables.
- Teardown order: DROP Dynamic Tables before regular tables, otherwise dependency errors will occur.

**AI Functions (Extension Layer)**
- Lakehouse currently has no native time-series forecasting function (`SHOW FUNCTIONS LIKE '%FORECAST%'` returns 0 rows, confirmed in UAT).
- `AI_COMPLETE` is suitable for demand anomaly explanation; precise numerical forecasting can be deployed via External Function using Prophet/ARIMA.

---

## Extension Directions

- **Demand anomaly AI explanation**: When `demand_anomaly_flag=TRUE`, trigger `AI_COMPLETE` to analyze the cause (promotion / holiday / competitor / seasonal).
- **ABC inventory classification**: Use `AI_CLASSIFY` to automatically classify SKUs; apply tighter buffer days for Class A, and relax them for Class C.
- **Multi-warehouse transfer optimization**: Suggest transfers from "healthy warehouse → urgent warehouse" for the same SKU, reducing redundant replenishment costs.
- **Integration with defect detection** ([02-defect-detection-ai](../02-defect-detection-ai/)): High-defect-rate batches trigger raw-material stockout risk alerts.
- **SPC statistical process control**: Use Dynamic Table to compute stockout-rate control limits; auto-alert when production line supply is interrupted.

---

## Related Documentation

### AI Functions

| Document | Description |
|----------|-------------|
| [AI Functions Overview](../ai_functions_overview.md) | Overview of AI functions: model selection, invocation methods, billing |
| [AI_EXTRACT](../ai_extract.md) | Structured information extraction function; used here to extract new lead times and delay reasons from supplier notification text |
| [AI_COMPLETE](../ai_complete.md) | General-purpose LLM completion function; used here to explain demand anomaly causes (promotion / holiday / competitor / seasonal) |
| [AI_CLASSIFY](../ai_classify.md) | Classification function; can be extended for automated SKU ABC classification |

### Dynamic Table

| Document | Description |
|----------|-------------|
| [Dynamic Table Overview](../dynamic_table_summary.md) | Core concepts of Dynamic Table, incremental refresh mechanism, and comparison with materialized views |
| [Dynamic Table Development Guide](../sql_dynamic_table_guide.md) | End-to-end example: create, refresh, and view history |
| [CREATE DYNAMIC TABLE](../create-dynamic-table.md) | Syntax reference including `change_tracking`, refresh scheduling, and other parameters |
| [Dynamic Table Refresh Scheduling](../dynamic-table-scheduling.md) | Scheduled refresh configuration for controlling replenishment pipeline frequency |
| [Monitoring Dynamic Tables in Studio](../dynamic_table_using_studio.md) | Visualize Dynamic Table refresh status and pipeline health in Studio |

### Window Functions

| Document | Description |
|----------|-------------|
| [Window Functions Overview](../windowfunction.md) | Window function syntax: OVER / PARTITION BY / ORDER BY / ROWS BETWEEN |
| [Data Transformation with Window Functions](../sql_data_transform_windows.md) | Complete examples of multi-window sliding averages, period-over-period comparisons, and ranking |
| [User Behavior Funnel Analysis: Tracking Conversions from Impression to Order](../funnel-analysis-with-window-functions.md) | Window function practical case; useful as a reference for multi-window calculation patterns |

### MERGE INTO

| Document | Description |
|----------|-------------|
| [MERGE INTO](../merge.md) | Syntax reference including MATCHED/NOT MATCHED branches and idempotent write patterns |
| [Product Dimension History Tracking: SCD Type 2 with MERGE INTO](../scd2-product-dimension-with-merge-into.md) | MERGE INTO idempotent archive practical case, using the same pattern as replenishment plan archiving in this solution |

### Time Travel

| Document | Description |
|----------|-------------|
| [Time Travel Overview](../timetravel-summary.md) | Introduction to the Time Travel mechanism and how to look back at data at any point in time |
| [Data Recovery: Restoring Deleted or Incorrectly Modified Data with Time Travel](../data-recovery-with-time-travel.md) | Time Travel practical case; applicable to replenishment plan history review and decision post-mortems |

### Studio Tasks

| Document | Description |
|----------|-------------|
| [Studio Task Development and Operations](../cz-cli-studio-tasks.md) | Create, deploy, and schedule Studio Tasks for pushing replenishment suggestions to procurement systems on a schedule |
| [Studio Task Development Best Practices](../studio-task-practice.md) | Studio Task development best practices, including scheduled triggers and alert notification configuration |
