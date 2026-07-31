# Equipment Predictive Maintenance Solution

**Industry**: Discrete Manufacturing / Process Industry  
**Scenario**: Real-time factory equipment sensor data collection → Anomaly detection → AI maintenance recommendations  
**Tech Stack**: Singdata Lakehouse · Dynamic Table · AI_COMPLETE · DeepSeek V3

An unplanned factory equipment shutdown costs an average of **$260,000 per hour**. This solution uses Singdata Lakehouse to implement a complete closed-loop pipeline in pure SQL — from sensor data ingestion to 1-hour rolling anomaly detection to AI-generated maintenance recommendations — with no standalone stream processing cluster and no AI service deployment required. Implementation time shrinks from months to days.

---

## 1. Business Background

The Industry 4.0 and smart manufacturing wave is driving factories to accelerate the shift from "reactive repair" to "predictive maintenance." Modern factory equipment is widely equipped with IoT sensors for vibration, temperature, pressure, and rotation speed. Each machine generates multi-dimensional data streams every second, laying the groundwork for data-driven failure prediction.

**Key industry scenarios covered**:

| Industry | Typical Equipment | Core Monitoring Metrics |
|----------|------------------|------------------------|
| Automotive Manufacturing | CNC machining centers, stamping presses, welding robots | Spindle temperature, vibration, power load |
| Electronics / Semiconductor | SMT placement machines, lithography machines, vacuum pumps | Temperature uniformity, rotation speed, pressure |
| Injection Molding / Rubber | Injection molding machines, extruders | Hydraulic pressure, barrel temperature, screw speed |
| Process Chemicals | Reactors, compressors, heat exchangers | Temperature, pressure, flow rate |
| Logistics / Warehousing | Conveyor belts, AGVs, palletizing robots | Motor temperature, vibration frequency, load current |

---

## 2. Industry Pain Points

### 2.1 Unplanned Downtime Is Extremely Costly

- Average cost of unplanned downtime in manufacturing: ~**$260,000/hour** (Aberdeen Research)
- Automotive industry single downtime event can exceed **$2.3 million/hour**
- Equipment failure is the leading cause of downtime events, accounting for ~**44%**, with an average duration of **238 minutes**
- Global manufacturers lose up to **$852 million per week** due to unplanned downtime

### 2.2 Three Key Flaws of Traditional Maintenance Models

**Reactive Maintenance**
- Problems are addressed only after failure — losses have already occurred
- Emergency spare parts procurement costs 3–5x more than planned procurement
- High risk of cascading failures (spindle failure → entire production line shutdown)

**Preventive Maintenance**
- Parts are replaced on fixed schedules; many components are discarded while still within their useful life
- Approximately **30% of effective maintenance** globally is unnecessary over-maintenance
- Cannot handle early failure caused by abnormal operating conditions

**Manual Inspection**
- Relies on individual experience with point-in-time sampling; high miss rate
- Unable to perform multi-dimensional integrated analysis
- Cannot provide 7×24-hour coverage of hundreds of machines

### 2.3 Data Silos and High Build Costs

- Sensor data lands in SCADA/PLC systems and is disconnected from MES and ERP data — joint analysis is impossible
- Historical failure data and maintenance logs are scattered across multiple systems with no traceability
- Traditional predictive maintenance solutions require stacking multiple components (time-series database + stream processing + ML platform + AI inference service), resulting in long build cycles and complex operations
- Modeling depends on dedicated data science teams; delivery takes months with poor ROI

**This solution addresses all of the above pain points**: Singdata Lakehouse unifies real-time computation, historical storage, and AI inference — the entire solution requires only SQL and depends on no external systems.

---

## 3. Solution

### 3.1 Overall Architecture

![Predictive Maintenance Architecture](/.topwrite/assets/predictive_maintenance_architecture.svg)

After IoT device sensor data enters the `equipment_sensors` raw table, two Dynamic Tables automatically perform continuous computation: the first computes 1-hour rolling averages (to suppress single-point spike false alarms), and the second applies multi-dimensional threshold filtering and risk classification. Finally, `AI_COMPLETE` is called for medium/high-risk equipment to generate structured maintenance recommendations, which are written to `equipment_alerts` for downstream consumption. The entire pipeline requires no external scheduler — the platform automatically detects data changes and performs incremental refresh.

### 3.2 Data Model

**Raw data table** `equipment_sensors`

```sql
-- The partition column must be the first field in the composite primary key (Singdata convention)
CREATE TABLE equipment_sensors (
    sensor_id       STRING        NOT NULL,
    equipment_id    STRING        NOT NULL COMMENT 'Equipment ID',
    equipment_type  STRING                 COMMENT 'Equipment type: CNC lathe / injection molding machine / conveyor belt',
    temperature     DOUBLE                 COMMENT 'Temperature (°C)',
    vibration       DOUBLE                 COMMENT 'Vibration (mm/s)',
    pressure        DOUBLE                 COMMENT 'Pressure (Bar)',
    rotation_speed  DOUBLE                 COMMENT 'Rotation speed (RPM)',
    power_load      DOUBLE                 COMMENT 'Power load (%)',
    record_time     TIMESTAMP_NTZ NOT NULL,
    PRIMARY KEY (record_time, sensor_id)   -- Partition column record_time must be first
) PARTITIONED BY (DAYS(record_time));

-- Enable change tracking to drive Dynamic Table to process only newly added data
ALTER TABLE equipment_sensors
    SET TBLPROPERTIES ('change_tracking' = 'true');

-- BloomFilter index: accelerates equality queries on high-cardinality columns (verified syntax)
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_equipment_id ON TABLE equipment_sensors(equipment_id);
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_sensor_id    ON TABLE equipment_sensors(sensor_id);
```

**Alert output table** `equipment_alerts`

```sql
-- Partition column alert_time must be the first field in the composite primary key
CREATE TABLE equipment_alerts (
    alert_id                STRING        NOT NULL,
    equipment_id            STRING        NOT NULL,
    equipment_type          STRING,
    alert_time              TIMESTAMP_NTZ NOT NULL,
    anomaly_metrics         STRING   COMMENT 'Anomaly metric description, e.g. "High temp:95°C, High vibration:9.2mm/s"',
    risk_level              STRING   COMMENT 'High / Medium',
    maintenance_advice      STRING   COMMENT 'AI-generated maintenance recommendation (≤50 characters)',
    predicted_failure_hours INT      COMMENT 'AI-predicted hours until failure',
    PRIMARY KEY (alert_time, alert_id)   -- Partition column alert_time must be first
) PARTITIONED BY (DAYS(alert_time));

-- BloomFilter index
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_alert_equipment_id ON TABLE equipment_alerts(equipment_id);
```

### 3.3 Three-Layer Processing Pipeline

**Layer 1: 1-Hour Rolling Window Aggregation (`equipment_metrics_1h`)**

Using averages instead of raw sample values as the basis for anomaly detection eliminates false alarms caused by sensor spikes and brief fluctuations. The Dynamic Table automatically refreshes incrementally every 10 minutes with no manual scheduling required.

```sql
CREATE DYNAMIC TABLE equipment_metrics_1h
    REFRESH INTERVAL 10 MINUTE
AS
SELECT
    equipment_id, equipment_type,
    MAX(record_time)             AS last_record_time,
    ROUND(AVG(temperature), 2)  AS avg_temp,
    ROUND(MAX(temperature), 2)  AS max_temp,
    ROUND(AVG(vibration),   2)  AS avg_vib,
    ROUND(MAX(vibration),   2)  AS max_vib,
    ROUND(AVG(pressure),    2)  AS avg_pres,
    ROUND(AVG(power_load),  2)  AS avg_load,
    COUNT(*)                     AS reading_cnt
FROM equipment_sensors
WHERE record_time >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
GROUP BY equipment_id, equipment_type;
```

**Layer 2: Multi-Dimensional Threshold Filtering and Risk Classification (`equipment_anomaly_candidates`)**

Two-stage filtering: first a loose pre-filter (`WHERE` clause), then precise classification with strict thresholds (`CASE WHEN`), significantly reducing downstream AI call volume.

```sql
CREATE DYNAMIC TABLE equipment_anomaly_candidates
    REFRESH INTERVAL 10 MINUTE
AS
SELECT
    equipment_id, equipment_type, last_record_time,
    avg_temp, max_temp, avg_vib, max_vib, avg_pres, avg_load,
    -- Concatenate description strings for all metrics exceeding thresholds
    CONCAT_WS(',',
        CASE WHEN max_temp > 90   THEN CONCAT('High temp:',      CAST(max_temp  AS STRING), '°C')   END,
        CASE WHEN max_vib  > 8.0  THEN CONCAT('High vibration:', CAST(max_vib   AS STRING), 'mm/s') END,
        CASE WHEN avg_pres > 12   THEN CONCAT('High pressure:',  CAST(avg_pres  AS STRING), 'Bar')  END,
        CASE WHEN avg_load > 95   THEN CONCAT('High load:',      CAST(avg_load  AS STRING), '%')    END
    ) AS anomaly_metrics,
    -- Risk classification: any metric exceeding high-risk threshold → High; exceeding medium-risk → Medium
    CASE
        WHEN max_temp > 100 OR max_vib > 12 OR avg_load > 98 THEN 'High'
        WHEN max_temp > 90  OR max_vib > 8  OR avg_pres > 12 THEN 'Medium'
        ELSE 'Low'
    END AS risk_level
FROM equipment_metrics_1h
WHERE max_temp > 85 OR max_vib > 6 OR avg_pres > 10 OR avg_load > 90;  -- Loose pre-filter
```

Detection threshold reference:

| Metric | Loose Pre-filter | Medium Risk | High Risk |
|--------|-----------------|-------------|-----------|
| Temperature | > 85°C | > 90°C | > 100°C |
| Vibration | > 6 mm/s | > 8 mm/s | > 12 mm/s |
| Power Load | > 90% | > 95% | > 98% |
| Pressure | > 10 Bar | > 12 Bar | — |

**Layer 3: AI-Generated Maintenance Recommendations Written to Alert Table**

Only equipment with `risk_level IN ('High', 'Medium')` triggers `AI_COMPLETE`. Equipment type, anomaly metrics, and current averages are passed as context to the model. The `advice` and `predicted_failure_hours` fields are parsed from the JSON response and written directly to the alert table.

```sql
INSERT INTO equipment_alerts
SELECT
    CONCAT(equipment_id, '_', DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyyMMddHHmm')) AS alert_id,
    equipment_id, equipment_type,
    CURRENT_TIMESTAMP() AS alert_time,
    anomaly_metrics, risk_level,
    -- AI call: extract maintenance recommendation text
    -- REGEXP_EXTRACT handles possible markdown code fence wrapping from LLM, extracting pure JSON object
    GET_JSON_OBJECT(
        REGEXP_EXTRACT(
            AI_COMPLETE(
                'conn_dashscope:deepseek-v3',
                'You are a factory equipment maintenance engineer. Based on the following sensor anomaly data, provide a concise maintenance recommendation. '
                || 'Return JSON: {"advice":"specific maintenance action, no more than 50 characters","predicted_failure_hours":number}'
                || 'Equipment type: ' || COALESCE(equipment_type, '')
                || ', Anomaly metrics: ' || anomaly_metrics
                || ', Current avg temperature: ' || CAST(avg_temp AS STRING) || '°C'
                || ', Max vibration: ' || CAST(max_vib AS STRING) || 'mm/s'
            ), '(?s)\{.*\}', 0
        ), '$.advice'
    ) AS maintenance_advice,
    -- AI call: extract predicted hours until failure
    CAST(GET_JSON_OBJECT(
        REGEXP_EXTRACT(
            AI_COMPLETE(
                'conn_dashscope:deepseek-v3',
                'You are a factory equipment maintenance engineer. Based on the following sensor anomaly data, provide a concise maintenance recommendation. '
                || 'Return JSON: {"advice":"specific maintenance action, no more than 50 characters","predicted_failure_hours":number}'
                || 'Equipment type: ' || COALESCE(equipment_type, '')
                || ', Anomaly metrics: ' || anomaly_metrics
                || ', Current avg temperature: ' || CAST(avg_temp AS STRING) || '°C'
                || ', Max vibration: ' || CAST(max_vib AS STRING) || 'mm/s'
            ), '(?s)\{.*\}', 0
        ), '$.predicted_failure_hours'
    ) AS INT) AS predicted_failure_hours
FROM equipment_anomaly_candidates
WHERE risk_level IN ('High', 'Medium');
```

---

## 4. Singdata Technical Advantages

### 4.1 Dynamic Table: Declarative Continuous Computation, Zero Operations

Traditional solutions require independently deploying Flink or Spark Streaming clusters and manually managing JobManagers, TaskManagers, and checkpoints. Singdata Dynamic Table declares computation logic with a single `CREATE DYNAMIC TABLE` SQL statement. The platform automatically detects upstream data changes (relying on Change Tracking) and performs incremental computation at the configured refresh interval — no external scheduler required.

| Comparison Dimension | Traditional Streaming (Flink) | Singdata Dynamic Table |
|---------------------|------------------------------|------------------------|
| Development Language | Java / Python + operator API | Standard SQL |
| Operational Burden | Standalone cluster + monitoring + restart policy | Fully managed by platform |
| Refresh Latency | Millisecond-level (overkill for this scenario) | Minute-level (configurable: 1min–1h) |
| Dependency Management | Manual DAG maintenance | Automatically tracks upstream table dependencies |
| Applicable Scenario | Millisecond-level real-time response | Minute-level monitoring and alerting (this scenario) |

This anomaly detection solution does not require millisecond-level response — equipment typically has a window of several hours between developing anomalous averages and actual failure. A 10-minute refresh is fully sufficient, making Dynamic Table the most cost-effective choice.

### 4.2 AI_COMPLETE: Large Model Inference Embedded in SQL, No Extra Service

`AI_COMPLETE` is a built-in Singdata function. Large model inference is performed directly within SQL statements — no standalone AI service deployment, no API integration code, no model version management. API keys are centrally managed through Connection objects, supporting mainstream providers including DashScope (DeepSeek, Qwen), OpenAI, and others.

Two key design decisions ensure cost control:

- **Two-level filtering controls call volume**: Loose pre-filter plus medium/high risk gate — token consumption is reduced by 90%+ compared to calling for all records
- **Structured output written directly to the table**: The LLM response is stripped of any markdown code fence wrapping via `REGEXP_EXTRACT('(?s)\{.*\}', 0)`, then `GET_JSON_OBJECT` extracts `$.advice` and `$.predicted_failure_hours` for direct insertion into the alert table, requiring no secondary parsing by downstream systems

### 4.3 Lakehouse: Unified Storage for Real-Time and Historical Data

Raw sensor data is stored in the Lakehouse partitioned by day, serving both as the upstream data source for Dynamic Tables (real-time computation) and as a data store supporting historical analysis queries across time ranges — without needing to sync data to a separate data warehouse or time-series database. This means:

- The same `equipment_sensors` table simultaneously supports "past 1-hour anomaly detection" and "past 6-month failure trend analysis"
- Can be joined directly with MES order tables and ERP spare parts inventory tables — no ETL pipeline required

### 4.4 Change Tracking: Incremental Processing, No Full-Table Scans

After enabling `change_tracking = 'true'` on `equipment_sensors`, Dynamic Table refresh only processes rows added since the last refresh — not a full table scan. As historical data accumulates, refresh performance remains stable and does not degrade with data growth.

### 4.5 BloomFilter Index: High-Cardinality Column Equality Query Acceleration

#### Background

`equipment_sensors` is a core wide table. Even after day-based partitioning, each partition may store millions of records. When operations personnel or downstream systems need to query specific equipment:

```sql
-- Scenario 1: Retrieve all raw sensor data for a specific equipment over the past 30 days (failure investigation)
SELECT * FROM equipment_sensors
WHERE equipment_id = 'EQ_CNC_01'
  AND record_time >= CURRENT_TIMESTAMP() - INTERVAL 30 DAY;

-- Scenario 2: Bulk fetch latest data for multiple equipment items (Dashboard refresh)
SELECT * FROM equipment_sensors
WHERE equipment_id IN ('EQ_CNC_01', 'EQ_INJ_02', 'EQ_CONV_01')
  AND record_time >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR;

-- Scenario 3: Look up historical alert details by alert ID
SELECT * FROM equipment_alerts
WHERE equipment_id = 'EQ_CNC_01'
  AND alert_time >= '2026-01-01';
```

`equipment_id` is a high-cardinality column (unique identifier per equipment; the larger the factory, the higher the cardinality). It is not part of the partition key or the sort prefix of the primary key. Without an additional index, the engine must scan all data blocks within the partition to find matching rows — cost grows linearly with data volume.

#### How BloomFilter Works

A BloomFilter index is a probability-based **skip index**. At build time, each data block (page/granule) maintains a BloomFilter bitmap recording which values appeared in that block. At query time:

```
Query: WHERE equipment_id = 'EQ_CNC_01'

  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
  │  Block 1   │  │  Block 2   │  │  Block 3   │  │  Block 4   │
  │ BF: absent │  │ BF: maybe  │  │ BF: absent │  │ BF: maybe  │
  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
        │               │               │               │
      Skip        Read and filter      Skip        Read and filter
```

- **Definitively absent**: skipped entirely — zero I/O
- **Possibly present**: block is read and precisely filtered (a very small false-positive probability, controlled by the `fpp` parameter)
- In typical scenarios, **90%+ of data blocks** can be skipped, drastically reducing scan volume

#### Creating the Index

```sql
-- Singdata actual syntax (verified): CREATE BLOOMFILTER INDEX
-- Note: PROPERTIES('fpp'=...) parameter is not supported; platform default false-positive rate is used
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_equipment_id ON TABLE equipment_sensors(equipment_id);
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_sensor_id    ON TABLE equipment_sensors(sensor_id);
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_alert_equipment_id ON TABLE equipment_alerts(equipment_id);
```

#### Use Cases and Boundaries

| Query Pattern | Suitable for BloomFilter | Notes |
|---------------|--------------------------|-------|
| `WHERE equipment_id = 'EQ_CNC_01'` | **Yes** | Equality query — optimal scenario |
| `WHERE equipment_id IN (...)` | **Yes** | Multi-value equality — probed one by one |
| `WHERE equipment_id LIKE 'EQ_%'` | No | Fuzzy queries cannot utilize BloomFilter |
| `WHERE temperature > 90` | No | Range queries use Min/Max statistics, not BloomFilter |
| `WHERE risk_level = 'High'` | No | Low-cardinality column (only High/Medium/Low) — BloomFilter benefit is negligible |

> BloomFilter is designed specifically for **equality queries on high-cardinality columns**. Using BloomFilter on low-cardinality columns (such as `risk_level`, `equipment_type`) wastes space and is not recommended. Range queries and LIKE queries should rely on partition pruning and Inverted Index respectively.

#### Synergy with Other Indexes

In this solution, three types of indexes play complementary roles:

| Index Type | Target Columns | Query Pattern Accelerated |
|------------|---------------|--------------------------|
| Partition pruning | `record_time` | `WHERE record_time >= ...` time range filtering |
| BloomFilter | `equipment_id`, `sensor_id` | High-cardinality column equality queries — skips irrelevant data blocks |
| Inverted Index | STRING text columns | `LIKE`, full-text search (e.g., alert content search) |

When all three are applied together, the engine first prunes partitions (dramatically narrowing the scan scope), then uses BloomFilter to skip irrelevant data blocks within the partition, and finally applies precise filtering only on the remaining rows.

---

## 5. Customer Value

### 5.1 Direct Economic Benefits

| Value Dimension | Industry Benchmark | Realization Path |
|----------------|-------------------|-----------------|
| Reduce unplanned downtime | **35–50% reduction** | Identify anomalies 4–48 hours in advance, preserving maintenance windows |
| Lower maintenance costs | **25–30% reduction** | Reduce over-maintenance; replace parts on demand |
| Extend equipment lifespan | **20–40% improvement** | Avoid accelerated wear from running equipment while degraded |
| ROI payback period | **12–18 months** | Typical industry implementation timeframe |

The loss from a single downtime event (average $260K/hour × average 4 hours = **$1M+**) far exceeds the build and operating costs of this entire solution — the ROI logic is clear.

### 5.2 Operational Efficiency Gains

- **Schedule optimization**: The `predicted_failure_hours` field provides remaining useful time, allowing maintenance teams to arrange personnel and spare parts in advance, completing planned repairs during non-production windows and avoiding emergency line shutdowns
- **Reduced false alarms**: The 1-hour rolling average baseline combined with two-level threshold filtering reduces false alarm rate by 60%+, letting maintenance teams focus on genuine threats rather than noise
- **Full equipment coverage**: Automated monitoring replaces manual inspection — 7×24-hour coverage of hundreds of machines simultaneously; personnel shift from inspection to repair work

### 5.3 Decision Support Upgrade

- Evolves from "fix when broken" to "know in advance which equipment will have what problem and how many hours away"
- The `anomaly_metrics` field precisely lists metrics exceeding thresholds, so maintenance engineers can prepare the right tools and spare parts before arriving on-site
- Historical alert data and raw sensor data are retained on the same platform, enabling equipment health profiles and identification of recurring failure root causes

### 5.4 Solution Build Cost Comparison

| Solution | Required Components | Build Time | Operational Complexity |
|----------|--------------------|-----------|-----------------------|
| Traditional | IoT platform + time-series DB + Flink cluster + ML platform + AI inference service + BI tool | 3–6 months | High (6+ systems) |
| **This Solution** | **Singdata Lakehouse (one platform)** | **Days** | **Low (pure SQL)** |

---

## 6. Quick Start

**Prerequisites**: Create an API Connection named `conn_dashscope` in Singdata Studio:

```sql
-- Using Singdata CREATE API CONNECTION syntax (validated)
CREATE API CONNECTION IF NOT EXISTS conn_dashscope
TYPE ai_function
PROPERTIES (
    'BASE_URL' = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'API_KEY'  = '<your-dashscope-api-key>'
);
```

**Execution order**:

```
1. setup.sql      -- Create equipment_sensors and equipment_alerts tables, enable Change Tracking
2. test_data.sql  -- Import sample sensor data for 3 equipment items (includes normal, medium-risk, high-risk samples)
3. pipeline.sql   -- Create two Dynamic Tables, trigger first refresh, trigger AI alert writes
```

**Verify results**:

```sql
-- View latest alerts, confirm AI recommendations and predicted failure times have been generated
SELECT equipment_id, equipment_type, risk_level, anomaly_metrics,
       maintenance_advice, predicted_failure_hours
FROM equipment_alerts
ORDER BY alert_time DESC
LIMIT 10;
```

**Clean up environment** (optional):

```sql
-- teardown.sql: drop all tables in dependency order
DROP TABLE IF EXISTS equipment_anomaly_candidates;
DROP TABLE IF EXISTS equipment_metrics_1h;
DROP TABLE IF EXISTS equipment_alerts;
DROP TABLE IF EXISTS equipment_sensors;
```

---

## 7. Extension Directions

Listed in order of implementation priority:

**Near-term ready**

| Direction | Description | Implementation |
|-----------|-------------|----------------|
| Integrate equipment operation logs | Inject maintenance records and parts replacement history into AI context to prevent recently-serviced equipment from being incorrectly flagged as high risk | Add `equipment_maintenance_log` table, JOIN and include in AI prompt |
| Supply chain spare parts linkage | After failure prediction, automatically query spare parts inventory and trigger replenishment orders when insufficient | Join `equipment_alerts` with spare parts inventory table, write to purchase request table |

**Medium-term planning**

| Direction | Description | Implementation |
|-----------|-------------|----------------|
| Cross-factory horizontal comparison | Aggregate equipment health metrics across multiple production lines/factories to identify systemic issues (e.g., parts from the same batch failing early across the board) | Add `factory_id` dimension to `equipment_sensors`, add cross-factory aggregation Dynamic Table |
| Adaptive thresholds | Calculate personalized normal ranges based on each equipment's historical data to replace current fixed thresholds | Use historical percentiles (P95/P99) to dynamically compute thresholds, write to threshold config table for Step 2 to query |

**Long-term evolution**

| Direction | Description |
|-----------|-------------|
| Digital twin integration | Push alert coordinates (equipment ID + anomaly type) to factory 3D visualization system for spatial positioning |
| Multimodal fault diagnosis | Incorporate equipment vibration spectrum and thermal imaging data, combined with vision large models to improve diagnostic accuracy |


---

## Related Documentation

### AI Functions

| Document | Description |
|----------|-------------|
| [AI Functions Overview](../ai_functions_overview.md) | Overall introduction to AI functions, model selection, calling methods, billing |
| [AI_COMPLETE](../ai_complete.md) | General-purpose LLM completion function; used in this solution to generate structured maintenance recommendations and predict failure times |
| [CREATE API CONNECTION](../create-api-connection.md) | Create API Connections to manage access credentials for large model services (DashScope/OpenAI, etc.) |

### Dynamic Table

| Document | Description |
|----------|-------------|
| [Dynamic Table Overview](../dynamic_table_summary.md) | Dynamic Table core concepts, incremental refresh mechanism, and comparison with materialized views and stream processing |
| [Dynamic Table Development Guide](../sql_dynamic_table_guide.md) | End-to-end examples for creating tables, refreshing, and viewing history |
| [CREATE DYNAMIC TABLE](../create-dynamic-table.md) | Table creation syntax reference, including `change_tracking`, `REFRESH INTERVAL`, and other parameter descriptions |
| [Dynamic Table Refresh Modes](../dynamic-table-incre.md) | Incremental vs. full refresh mode explanation, and how to determine the current refresh strategy |
| [Dynamic Table Refresh Scheduling](../dynamic-table-scheduling.md) | Scheduled refresh configuration to control anomaly detection pipeline refresh frequency |
| [Monitoring Dynamic Tables with Studio](../dynamic_table_using_studio.md) | Visually monitor Dynamic Table refresh status and dependency chain health through Studio |

### Indexes

| Document | Description |
|----------|-------------|
| [Index Overview](../index-overview.md) | Use cases and selection comparison for various index types (BloomFilter / Inverted / Vector) |
| [BloomFilter Index](../bloomfilter-summary.md) | BloomFilter working principle and applicable boundaries; high-cardinality column equality query acceleration |
| [CREATE BLOOMFILTER INDEX](../create-bloomfilter-index.md) | Index creation syntax reference; used in this solution to accelerate `equipment_id`, `sensor_id` equality queries |
| [Inverted Index](../inverted-index.md) | Suitable for fuzzy queries and full-text search on STRING columns; complementary to BloomFilter |
| [Lakehouse Index Best Practices Guide](../lakehouse-index-best-practice.md) | Combined index usage strategies, including partition pruning + BloomFilter + inverted index stacking pattern |

### Partitioned Tables

| Document | Description |
|----------|-------------|
| [Partitioning and Bucketing](../partition_table_guide.md) | Partitioned table design concepts, including `PARTITIONED BY (DAYS(...))` time partitioning usage |
| [Partitioned Table Usage Guide](../notes-and-guidelines-for-partition-tables.md) | Partitioned table notes, including the rule that composite primary keys must include the partition key (the key constraint for this solution) |

### JSON and Regex Functions

| Document | Description |
|----------|-------------|
| [get_json_object](../sql_functions/scalar_functions/json_functions/get_json_object.md) | Extract values at a specified path from a JSON string; used in this solution to parse `$.advice` and `$.predicted_failure_hours` from AI responses |
| [regexp_extract](../sql_functions/scalar_functions/string_functions/regexp_extract.md) | Regex extraction function; used in this solution to strip potential markdown code fence wrapping from LLM responses and extract the pure JSON object |
