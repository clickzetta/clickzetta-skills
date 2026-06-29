# Smart Mine Safety Early Warning Solution

Based on Singdata Lakehouse, this solution unifies data from the six major subsystems of coal and non-coal mines, enabling cross-system correlation analysis and AI-driven proactive alerting — upgrading from "reactive alarming" to "predictive early warning," with PoC deployment completed in 6 weeks.

---

## 1. Business Background

China produces approximately 4.7 billion tons of raw coal annually, accounting for nearly 50% of global output. Mining is a high-risk industry — **between 2001 and 2022, coal mine water hazard accidents caused 4,667 cumulative deaths, and a single major gas explosion can result in direct losses exceeding 50 million RMB** — with 200 to 500 workers operating underground each shift, making early warning failures a matter of mass casualties.

The fundamental contradiction in current mine digitalization: **sensors generate massive amounts of data every second, but the six major subsystems operate independently, data silos are severe, and cross-system correlation analysis is virtually nonexistent.**

### Mandatory Policy Requirements (Mandatory from 2025)

| Requirement | Regulatory Basis |
|------|---------|
| CH₄ overrun: automatic power cutoff within **1 second**, non-compliance results in shutdown | Coal Mine Safety Regulations, 2022 Edition |
| Safety monitoring data **real-time reporting** to provincial/national platforms | AQ 1029-2019 |
| Sensor historical data retained **≥ 1 year** | GB 16423-2020 |
| Personnel underground location **real-time queryable** per shift | Smart Mine Construction Guidelines 2025 |

The global connected mine market is projected to reach **$48.7 billion by 2033** (CAGR 13.4%). Among approximately 4,000 large-scale coal mines in China, only 30% have completed initial intelligentization — **the data fusion layer is the largest gap.**

### Six Major Subsystems

| Subsystem | Core Metrics | Collection Frequency | Safety Weight |
|--------|---------|---------|---------|
| Ventilation System | CH₄, CO, Wind Speed, Temperature | 1–10s | ★★★★★ |
| Monitoring System | Personnel Location, Violation Behavior | 1s/person | ★★★★★ |
| Transport System | Belt Deviation, Rope Tension, Vehicle Position | 1–5s | ★★★★☆ |
| Power System | Three-Phase Voltage/Current, Power Factor | 50ms | ★★★★☆ |
| Excavation System | Cutting Current, Support Pressure | 100ms–1s | ★★★☆☆ |
| Dispatch System | Production Plans, Safety Events, Work Orders | Business-driven | ★★★☆☆ |

Ventilation + Monitoring carry the highest weights: **gas outburst × personnel presence = mass casualties**. Data from these two systems is completely isolated in traditional architectures — this is the core entry point of this solution.

---

## 2. Industry Pain Points

### Quantified Accident Data

- From 2001 to 2022, China recorded 1,103 coal mine water hazard accidents with 4,667 deaths
- Roof collapse accidents account for approximately 30%–40% of total coal mine accidents, with underground mines being the hardest hit
- Gas accidents remain the greatest threat to coal mines, with frequent over-limit gas concentration incidents in outburst mines

### Three Major Deficiencies of Traditional Solutions

**① Data Silos — No Linkage**

The six major subsystems are independently built by different vendors, with Modbus/OPC-UA/MQTT/proprietary protocols coexisting. Typical failure scenarios:
- ZONE-101 CH₄ concentration exceeds 1.0% alarm threshold → but power feeder switch does not automatically trip
- Personnel positioning shows 3 people in hazardous zone → but the ventilation system is unaware, and dispatch receives no notification

**② Delayed Warning — Only Reactive**

Existing systems only perform threshold alarming for the five major hazards (gas/fire/water/roof/dust) and have no trend prediction capability. CH₄ rising from 0.7% to 1.0% takes an average of 20–30 minutes — sufficient time to warn and evacuate — but traditional systems provide no proactive alerts.

**③ Manual Dependency — Hard to Scale**

Dispatch command relies on human experience; checking 2,000+ monitoring points per shift is impractical. Inspection personnel cannot cover the entire mine, and hazard identification is delayed.

### Data Platform Pain Points

| Problem | Manifestation |
|------|------|
| Protocol Heterogeneity | Multi-vendor systems with non-unified protocols, high integration cost |
| Insufficient Real-time Capability | Safety warnings require second-level response; traditional batch architectures cannot meet this |
| Difficult AI Deployment | Model training and inference are separated, iteration cycles are long, no unified Feature Store |
| Lack of Standardization | Each system has a different data model; cross-system analysis relies on manual effort |

**This core gap is precisely where Singdata Lakehouse excels** — unified ingestion, real-time aggregation, SQL-embedded AI — one platform connecting six isolated islands.

---

## 3. Solution

### Overall Architecture

![Architecture Diagram](/.topwrite/assets/smart_mine_architecture.svg)

> Architecture Overview: Sensor/event data from six major subsystems is uniformly written into the Singdata raw layer. Aggregation-layer Dynamic Tables recalculate risk indicators for each subsystem on a 5-minute rolling basis. Anomaly-layer Dynamic Tables perform cross-system correlation detection. HIGH/CRITICAL anomalies trigger AI_COMPLETE to generate response recommendations. Alert work orders are pushed to large screens, dispatch systems, and mobile devices.

### Data Model

**Raw Layer (8 Tables)**

```sql
-- Ventilation system: sensor data for CH₄/CO/wind speed/temperature, etc.
CREATE TABLE mine_ventilation_sensors (
    collected_at    TIMESTAMP_NTZ  NOT NULL,
    sensor_id       STRING         NOT NULL,
    mine_id         STRING         NOT NULL,
    zone_id         STRING         NOT NULL,
    sensor_type     STRING         NOT NULL,   -- CH4/CO/CO2/WIND_SPEED/TEMP/HUMIDITY
    value           DOUBLE         NOT NULL,
    unit            STRING         NOT NULL,
    device_status   STRING         NOT NULL,
    PRIMARY KEY (collected_at, sensor_id)
) PARTITIONED BY (DAYS(collected_at));

-- Personnel positioning (UWB, 1 second/reading)
CREATE TABLE mine_personnel_location (
    collected_at       TIMESTAMP_NTZ  NOT NULL,
    person_id          STRING         NOT NULL,
    mine_id            STRING         NOT NULL,
    zone_id            STRING         NOT NULL,
    location_x         DOUBLE         NOT NULL,
    location_y         DOUBLE         NOT NULL,
    depth              DOUBLE         NOT NULL,
    is_in_danger_zone  BOOLEAN        NOT NULL DEFAULT FALSE,
    shift_id           STRING         NOT NULL,
    PRIMARY KEY (collected_at, person_id)
) PARTITIONED BY (DAYS(collected_at));

-- Safety event ledger (cross-system linkage event markers)
CREATE TABLE mine_safety_events (
    event_at          TIMESTAMP_NTZ  NOT NULL,
    event_id          STRING         NOT NULL,
    mine_id           STRING         NOT NULL,
    zone_id           STRING         NOT NULL,
    source_system     STRING         NOT NULL,
    event_level       STRING         NOT NULL,  -- INFO/WARNING/ALARM/EMERGENCY
    is_cross_system   BOOLEAN        NOT NULL DEFAULT FALSE,
    related_event_ids STRING,
    PRIMARY KEY (event_at, event_id)
) PARTITIONED BY (DAYS(event_at));
```

> Full DDL is available in the GitHub repository, including 8 tables, BloomFilter indexes, and Change Tracking configuration.

**Key Indexes**

```sql
CREATE BLOOMFILTER INDEX idx_bf_vent_zone    ON TABLE mine_ventilation_sensors(zone_id);
CREATE BLOOMFILTER INDEX idx_bf_person_zone  ON TABLE mine_personnel_location(zone_id);
CREATE BLOOMFILTER INDEX idx_bf_safety_level ON TABLE mine_safety_events(event_level);
```

### Three-Layer Data Pipeline

**Layer 1: Aggregation-Layer Dynamic Table (one per subsystem, 5-minute refresh)**

```sql
-- Ventilation metrics aggregation: statistics on gas indicators by zone over the last 10 minutes
CREATE DYNAMIC TABLE mine_ventilation_metrics
REFRESH INTERVAL 5 MINUTE
AS
SELECT
    zone_id,
    mine_id,
    MAX(CASE WHEN sensor_type = 'CH4' THEN value END)        AS ch4_max_pct,
    MIN(CASE WHEN sensor_type = 'WIND_SPEED' THEN value END) AS wind_speed_min,
    CASE
        WHEN MAX(CASE WHEN sensor_type = 'CH4' THEN value END) >= 1.5 THEN 'CRITICAL'
        WHEN MAX(CASE WHEN sensor_type = 'CH4' THEN value END) >= 1.0 THEN 'HIGH'
        WHEN MAX(CASE WHEN sensor_type = 'CH4' THEN value END) >= 0.7 THEN 'MEDIUM'
        ELSE 'NORMAL'
    END AS ch4_risk_level
FROM mine_ventilation_sensors
WHERE collected_at >= CURRENT_TIMESTAMP() - INTERVAL 10 MINUTE
GROUP BY zone_id, mine_id;
```

**Layer 2: Cross-System Correlation Anomaly Detection Dynamic Table (core differentiator)**

```sql
-- JOIN five aggregation-layer tables together; power is precisely correlated via zone_id + mine_id; outputs a composite risk rating
CREATE DYNAMIC TABLE mine_cross_system_anomalies
REFRESH INTERVAL 5 MINUTE
AS
SELECT
    v.zone_id,
    v.ch4_risk_level,
    pw.switch_status AS feeder_switch_status,   -- Note alias, not pw.switch_status
    -- Composite risk rating: joint judgment across multiple systems
    CASE
        WHEN v.ch4_risk_level = 'CRITICAL'
             AND COALESCE(p.persons_in_danger, 0) > 0
             AND pw.switch_status = 'CLOSED'
             THEN 'CRITICAL'
        WHEN v.ch4_risk_level IN ('CRITICAL','HIGH')
             AND COALESCE(p.persons_in_danger, 0) > 0
             THEN 'HIGH'
        ...
    END AS overall_risk_level,
    -- Structured summary, used as input for both AI_CLASSIFY and AI_COMPLETE
    CONCAT_WS('; ',
        CASE WHEN v.ch4_risk_level != 'NORMAL'
             THEN CONCAT('CH4 concentration ', v.ch4_max_pct, '%') END,
        CASE WHEN COALESCE(p.persons_in_danger, 0) > 0
             THEN CONCAT(p.persons_in_danger, ' persons in hazardous zone') END,
        CASE WHEN pw.switch_status = 'CLOSED' AND v.ch4_risk_level IN ('HIGH','CRITICAL')
             THEN 'Feeder switch not tripped (power cutoff linkage required)' END
    ) AS anomaly_summary
FROM mine_ventilation_metrics v
LEFT JOIN mine_personnel_metrics p  ON v.zone_id = p.zone_id AND v.mine_id = p.mine_id
LEFT JOIN mine_power_metrics     pw ON v.zone_id = pw.zone_id AND v.mine_id = pw.mine_id
LEFT JOIN mine_excavation_metrics ex
    ON v.mine_id = ex.mine_id
    AND ex.working_face_id = CONCAT('FACE-', SUBSTR(v.zone_id, 6))
LEFT JOIN mine_transport_metrics tr
    -- Precise zone_id correlation: belt anomalies only associated with the local zone, not cross-zone pollution
    ON v.zone_id = tr.zone_id AND v.mine_id = tr.mine_id AND tr.device_type = 'CONVEYOR'
WHERE v.ch4_risk_level != 'NORMAL' OR v.co_risk_level != 'NORMAL' OR ...;
```

**Layer 3: AI Classification + AI Alert Work Order Generation (CTE single-call)**

```sql
-- CTE structure: AI_CLASSIFY called once + AI_COMPLETE called once, avoiding inconsistent results from multiple calls
WITH anomalies AS (
    SELECT * FROM mine_cross_system_anomalies WHERE overall_risk_level IN ('HIGH', 'CRITICAL')
),
classified AS (
    SELECT *,
           REGEXP_EXTRACT(AI_CLASSIFY('conn_dashscope:deepseek-v3', anomaly_summary,
               ARRAY('GAS','FIRE','ROOF','FLOOD','EQUIPMENT','COMPOUND')), '(?s)\{.*\}', 0) AS classify_json
    FROM anomalies
),
completed AS (
    SELECT *,
           REGEXP_EXTRACT(AI_COMPLETE('conn_dashscope:deepseek-v3',
               CONCAT('You are a mine safety engineer. Disaster type: ',
                      COALESCE(GET_JSON_OBJECT(classify_json,'$.label'),'unknown'),
                      ', anomaly: ', anomaly_summary, ...)), '(?s)\{.*\}', 0) AS complete_json
    FROM classified
)
INSERT INTO mine_ai_safety_alerts (...)
SELECT
    GET_JSON_OBJECT(classify_json, '$.label')                AS disaster_type,
    CAST(GET_JSON_OBJECT(classify_json, '$.score') AS DOUBLE) AS disaster_confidence,
    GET_JSON_OBJECT(complete_json, '$.alert_title')           AS alert_title,
    GET_JSON_OBJECT(complete_json, '$.immediate_actions')     AS immediate_actions,
    CAST(GET_JSON_OBJECT(complete_json, '$.evacuation_required')   AS BOOLEAN) AS evacuation_required,
    CAST(GET_JSON_OBJECT(complete_json, '$.power_cutoff_required') AS BOOLEAN) AS power_cutoff_required,
    ...
FROM completed;
```

> Full pipeline available in the GitHub repository pipeline.sql.

### Three Major Linkage Scenarios

| Scenario | Systems Involved | Trigger Condition | AI Response Recommendation |
|------|---------|---------|-----------|
| Gas-Personnel-Power Linkage | Ventilation + Monitoring + Power | CH₄ ≥ 1.0% + Personnel present + Feeder not tripped | Immediate power cutoff / evacuation / enhanced ventilation |
| Belt Failure — Production Chain Interruption | Transport + Dispatch | Belt deviation > 50mm + Shearer in operation | Shutdown for maintenance / adjust production plan |
| Goaf Spontaneous Combustion Warning | Ventilation + Dispatch | CO concentration trend rising (> 24ppm and rate > 2ppm/10min) | Grouting to seal / adjust ventilation mode |

### Pipeline A: Real-Time Data Processing Pipeline

The existing 5-minute Dynamic Table refresh is sufficient for most scenarios, but some safety events (sudden CH₄ rise, sharp wind speed drop) need to be detected within **1 minute**. The real-time pipeline adds a high-frequency bypass on top of the existing 5-layer pipeline:

```
Sensors → MQTT Collection Gateway → mine_ventilation_sensors
                                          ↓ Change Tracking driven
                                  Studio Task (1-minute Cron)
                                          ↓ Single-point threshold HAVING filter
                                  mine_realtime_alerts
                                          ↓
                                  Push: WebSocket / Dispatch Console / Mobile
```

**Key Design Decisions:**

- **1-minute window aggregation** (not per-record triggering): avoids massive false positives from sensor jitter while keeping latency to ≤ 90 seconds
- **Regulation thresholds hardcoded**: CH₄ 0.75%/1.0%/1.5%, CO 24/50ppm, wind speed 0.25m/s, temperature 26/30°C are written directly into CASE logic, not dependent on external configuration
- **ingestion_lag_ms monitoring**: records the delay from sensor to database ingestion per record, used in Studio monitoring dashboards to detect collection pipeline health
- **Division of responsibilities with Dynamic Table**: the real-time pipeline handles single-point extreme value triggering; Dynamic Tables handle multi-sensor aggregation and cross-system correlation — the two are complementary

```sql
-- Real-time pipeline core: 1-minute window, keep only records exceeding thresholds
INSERT INTO mine_realtime_alerts (...)
SELECT sensor_id, sensor_type, MAX(value) AS current_value, alert_rule, ...
FROM mine_ventilation_sensors
WHERE collected_at >= CURRENT_TIMESTAMP() - INTERVAL 1 MINUTE
GROUP BY mine_id, zone_id, sensor_id, sensor_type
HAVING (sensor_type = 'CH4' AND MAX(value) >= 0.75)
    OR (sensor_type = 'CO'  AND MAX(value) >= 24)
    OR (sensor_type = 'WIND_SPEED' AND MAX(value) < 0.25)
    OR (sensor_type = 'TEMP' AND MAX(value) >= 26);
```

### Pipeline B: Offline Unstructured Data Processing Pipeline

Mines have accumulated large amounts of unstructured data: historical accident investigation reports, equipment maintenance records, geological survey archives, and safety regulation training materials. These are the most valuable safety knowledge assets, but they have long been stored in isolation as PDFs, Word documents, or scanned files, inaccessible for AI retrieval.

The offline pipeline transforms these documents into a searchable structured knowledge base:

```
PDF / Word / Images (Object Storage)
        ↓ OCR / Document Parsing
mine_unstructured_docs (raw text + metadata)
        ↓ Studio Task (daily batch)
        ↓ AI_COMPLETE (mine safety expert Prompt)
mine_doc_knowledge (structured knowledge: summaries / risks / lessons learned)
        ↓
Real-time alert AI enhancement (RAG retrieval of historical similar incident response plans)
```

**Supported Document Types:**

| doc_type | Source | AI Extraction Focus |
|----------|------|-----------|
| ACCIDENT_REPORT | Accident investigation reports | Incident process, root cause, lessons learned |
| MAINTENANCE_LOG | Equipment maintenance records | Failure modes, replaced parts, prevention recommendations |
| GEO_SURVEY | Geological survey archives | Stratum structure, fault locations, gas occurrence patterns |
| REGULATION | Regulations / standard documents | Applicable clauses, key thresholds, operational requirements |
| TRAINING | Training materials | Safe operating procedures, emergency response workflows |

**RAG Enhancement:** When a new alert occurs, historical accident experience from the same zone and disaster type can be retrieved from `mine_doc_knowledge` and injected into the AI_COMPLETE Prompt to make the generated response recommendations more targeted.

```sql
-- Retrieve similar historical incidents, inject into alert AI Prompt
SELECT summary, lessons_learned
FROM mine_doc_knowledge
WHERE mine_id = 'MINE-001'
  AND involved_zones LIKE '%ZONE-101%'
  AND disaster_types LIKE '%GAS%'
ORDER BY processed_at DESC LIMIT 3;
```

> Full implementation available in the GitHub repository pipeline.sql, Pipeline A (real-time) and Pipeline B (offline) sections.

### Complete Technical Implementation Matrix

The following covers the complete technical solutions for each business scenario, all implemented using Singdata Lakehouse native capabilities — no external frameworks required.

#### Ventilation System Extension: CH₄ Concentration Trend Prediction

The current real-time pipeline only performs single-point threshold evaluation. The following Dynamic Table adds trend prediction, providing 20–30 minutes of advance warning during slow CH₄ rise:

```sql
CREATE DYNAMIC TABLE mine_ch4_trend
REFRESH INTERVAL 5 MINUTE
AS
SELECT
    zone_id, mine_id,
    MAX(CASE WHEN sensor_type = 'CH4' THEN value END) AS ch4_current,
    (AVG(CASE WHEN sensor_type = 'CH4' AND collected_at >= CURRENT_TIMESTAMP() - INTERVAL 5 MINUTE  THEN value END) -
     AVG(CASE WHEN sensor_type = 'CH4' AND collected_at <= CURRENT_TIMESTAMP() - INTERVAL 25 MINUTE THEN value END)
    ) / 25.0 AS ch4_slope_per_min,
    MAX(CASE WHEN sensor_type = 'CH4' THEN value END) +
    (AVG(CASE WHEN sensor_type = 'CH4' AND collected_at >= CURRENT_TIMESTAMP() - INTERVAL 5 MINUTE THEN value END) -
     AVG(CASE WHEN sensor_type = 'CH4' AND collected_at <= CURRENT_TIMESTAMP() - INTERVAL 25 MINUTE THEN value END)
    ) AS ch4_predicted_30min,
    CASE
        WHEN MAX(CASE WHEN sensor_type = 'CH4' THEN value END) +
             (AVG(CASE WHEN sensor_type = 'CH4' AND collected_at >= CURRENT_TIMESTAMP() - INTERVAL 5 MINUTE THEN value END) -
              AVG(CASE WHEN sensor_type = 'CH4' AND collected_at <= CURRENT_TIMESTAMP() - INTERVAL 25 MINUTE THEN value END)
             ) >= 1.0  THEN 'TREND_WARN'
        WHEN MAX(CASE WHEN sensor_type = 'CH4' THEN value END) +
             (AVG(CASE WHEN sensor_type = 'CH4' AND collected_at >= CURRENT_TIMESTAMP() - INTERVAL 5 MINUTE THEN value END) -
              AVG(CASE WHEN sensor_type = 'CH4' AND collected_at <= CURRENT_TIMESTAMP() - INTERVAL 25 MINUTE THEN value END)
             ) >= 0.75 THEN 'TREND_CAUTION'
        ELSE 'STABLE'
    END AS trend_level
FROM mine_ventilation_sensors
WHERE collected_at >= CURRENT_TIMESTAMP() - INTERVAL 30 MINUTE
  AND sensor_type = 'CH4'
GROUP BY zone_id, mine_id;
```

#### Transport System Extension: Belt Full Lifecycle Health Score

Calculate a health score of 0–100 per shift, weighted by deviation (40%), temperature (30%), and current overload (30%), to drive maintenance scheduling:

```sql
CREATE DYNAMIC TABLE mine_belt_health_score
REFRESH INTERVAL 30 MINUTE
AS
SELECT
    device_id, mine_id,
    ROUND(
        GREATEST(0, 100 - MAX(CASE WHEN metric_name = 'DEVIATION' THEN value ELSE 0 END) / 70.0 * 40) * 0.4 +
        GREATEST(0, 100 - GREATEST(0, MAX(CASE WHEN metric_name = 'TEMP' THEN value ELSE 0 END) - 50) * 2) * 0.3 +
        GREATEST(0, 100 - GREATEST(0, MAX(CASE WHEN metric_name = 'CURRENT' THEN value ELSE 0 END) - 85) / 85.0 * 30) * 0.3,
    1) AS health_score,
    CASE
        WHEN health_score < 40 THEN 'CRITICAL'   -- Immediate maintenance
        WHEN health_score < 65 THEN 'DEGRADED'   -- Scheduled maintenance within 72h
        WHEN health_score < 80 THEN 'WARNING'    -- Monitor closely
        ELSE 'HEALTHY'
    END AS health_status
FROM mine_transport_sensors
WHERE device_type = 'CONVEYOR'
  AND collected_at >= CURRENT_TIMESTAMP() - INTERVAL 480 MINUTE
GROUP BY device_id, mine_id;
```

#### Monitoring System Extension: Personnel Abnormal Behavior Detection

Analyze trajectory for stationary duration to identify emergency states such as collapse or injury, linked with personnel risk rating to trigger search and rescue plans:

```sql
CREATE DYNAMIC TABLE mine_personnel_behavior
REFRESH INTERVAL 3 MINUTE
AS
SELECT
    person_id, mine_id, zone_id, shift_id,
    MAX(collected_at) AS last_seen_at,
    SUM(CASE WHEN location_x = LAG(location_x) OVER (PARTITION BY person_id ORDER BY collected_at)
              AND location_y = LAG(location_y) OVER (PARTITION BY person_id ORDER BY collected_at)
             THEN 1 ELSE 0 END) OVER (PARTITION BY person_id) AS static_seconds,
    is_in_danger_zone,
    CASE
        WHEN static_seconds > 300 AND is_in_danger_zone THEN 'EMERGENCY'  -- Stationary 5 min in danger zone
        WHEN static_seconds > 600                        THEN 'ABNORMAL'  -- Stationary 10 min in any zone
        ELSE 'NORMAL'
    END AS behavior_status
FROM mine_personnel_location
WHERE collected_at >= CURRENT_TIMESTAMP() - INTERVAL 10 MINUTE;
```

#### Power System Extension: Load Forecasting and Reactive Power Compensation Optimization

Use AI_COMPLETE to forecast the next hour's load based on historical same-period features (same weekday, same time slot), proactively scheduling reactive power compensation timing. Target power factor ≥ 0.92, saving 300,000–800,000 RMB per mine per year:

```sql
CREATE DYNAMIC TABLE mine_power_load_features
REFRESH INTERVAL 30 MINUTE
AS
SELECT
    substation_id, mine_id,
    DAYOFWEEK(collected_at) AS day_of_week,
    HOUR(collected_at)      AS hour_of_day,
    AVG(CASE WHEN metric_name = 'ACTIVE_POWER' THEN value END) AS avg_load_kw,
    MIN(CASE WHEN metric_name = 'POWER_FACTOR' THEN value END) AS min_pf
FROM mine_power_sensors
WHERE collected_at >= CURRENT_TIMESTAMP() - INTERVAL 10080 MINUTE
GROUP BY substation_id, mine_id, DAYOFWEEK(collected_at), HOUR(collected_at);
```

#### Excavation System Extension: Equipment Predictive Health Management (PHM)

Based on feature vectors of current fluctuation, overload count, and hydraulic pressure, AI predicts remaining useful life (RUL) and automatically dispatches P1/P2 maintenance work orders:

```sql
CREATE DYNAMIC TABLE mine_excavation_features
REFRESH INTERVAL 30 MINUTE
AS
SELECT
    device_id, device_type, mine_id, working_face_id,
    AVG(CASE WHEN metric_name = 'CURRENT' THEN value END)    AS avg_current,
    STDDEV(CASE WHEN metric_name = 'CURRENT' THEN value END) AS current_stddev,
    MIN(CASE WHEN metric_name = 'PRESSURE' THEN value END)   AS min_pressure,
    COUNT(CASE WHEN metric_name = 'CURRENT' AND value > 420 THEN 1 END) AS overload_count
FROM mine_excavation_sensors
WHERE collected_at >= CURRENT_TIMESTAMP() - INTERVAL 480 MINUTE
GROUP BY device_id, device_type, mine_id, working_face_id;
```

When `overload_count >= 3`, AI_COMPLETE RUL prediction is triggered, outputting `{"rul_hours": value, "priority": "P1/P2", "advice": "..."}` and automatically writing to `mine_maintenance_orders`.

#### Dispatch System Extension: Intelligent Ventilation Network Optimization

Ventilation network computation: back-calculate required airflow from CH₄ concentration in each zone, AI outputs local fan adjustment plans written to the dispatch table. Target ventilation power consumption reduction of 15–20%, while ensuring CH₄ < 0.5% in all zones.

#### Mine-Wide: Group-Level Safety Management

Group-level unified workspace, real-time safety score ranking for each mine, prioritizing intervention at the mine with the lowest safety score:

```sql
CREATE DYNAMIC TABLE group_mine_safety_dashboard
REFRESH INTERVAL 10 MINUTE
AS
SELECT
    mine_id,
    COUNT(CASE WHEN overall_risk_level = 'CRITICAL' THEN 1 END) AS critical_count,
    COUNT(CASE WHEN overall_risk_level = 'HIGH'     THEN 1 END) AS high_count,
    SUM(persons_in_danger)                                       AS total_persons_at_risk,
    GREATEST(0, 100
        - COUNT(CASE WHEN overall_risk_level = 'CRITICAL' THEN 1 END) * 20
        - COUNT(CASE WHEN overall_risk_level = 'HIGH'     THEN 1 END) * 10
        - SUM(persons_in_danger) * 5)                           AS safety_score
FROM mine_cross_system_anomalies
GROUP BY mine_id
ORDER BY safety_score ASC;
```

#### Knowledge Base Retrieval: Full-Text Search + Vector Search + Hybrid Search

The accident reports, maintenance records, and geological archives accumulated over the years in a mine are the most valuable safety knowledge assets. Singdata natively supports full-text search and vector search, transforming these unstructured documents into a machine-searchable knowledge base to provide RAG enhancement for real-time alerts.

**Full-Text Search**: Dispatchers quickly locate relevant cases using natural language keywords, supporting Chinese IK word segmentation:

```sql
-- Scenario: after an alert triggers, the dispatcher searches "ZONE-101 gas power cutoff" for historical response experience
SELECT doc_id, doc_type, summary, lessons_learned,
       MATCH(chunk_text, summary) AGAINST ('ZONE-101 gas power cutoff' IN NATURAL LANGUAGE MODE) AS relevance
FROM mine_doc_knowledge
WHERE mine_id = 'MINE-001'
  AND MATCH(chunk_text, summary) AGAINST ('ZONE-101 gas power cutoff' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC
LIMIT 5;

-- Full-text search index (established in setup.sql)
CREATE FULLTEXT INDEX idx_ft_know_text
    ON TABLE mine_doc_knowledge(chunk_text, summary, key_findings, lessons_learned)
    WITH PROPERTIES ('analyzer' = 'ik_max_word');
```

**Vector Search**: Semantic similarity-based retrieval captures cases with "different wording but identical meaning," providing broader coverage than keyword search:

```sql
-- Scenario: vectorize the current alert summary, find the most semantically similar historical incidents
WITH alert_vec AS (
    SELECT AI_EMBEDDING('conn_dashscope:text-embedding-v3', anomaly_summary) AS q_vec
    FROM mine_ai_safety_alerts WHERE alert_id = 'ALERT-ZONE-101-xxx'
)
SELECT k.doc_id, k.summary, k.lessons_learned,
       COSINE_SIMILARITY(k.content_vector, a.q_vec) AS similarity
FROM mine_doc_knowledge k CROSS JOIN alert_vec a
WHERE k.mine_id = 'MINE-001' AND k.doc_type = 'ACCIDENT_REPORT'
ORDER BY similarity DESC
LIMIT 5;

-- Vector index (HNSW approximate nearest neighbor)
CREATE VECTOR INDEX idx_vec_know_content
    ON TABLE mine_doc_knowledge(content_vector)
    WITH PROPERTIES ('metric_type' = 'cosine', 'index_type' = 'hnsw');
```

**Hybrid Search**: Full-text recall × vector re-ranking, optimizing both precision and recall:

```sql
-- Full-text search recalls Top-20, then re-ranked by vector semantics, weighted fusion outputs Top-5
WITH kw_results AS (
    SELECT doc_id, chunk_id, summary, lessons_learned,
           MATCH(chunk_text, summary) AGAINST ('gas power cutoff evacuation') AS kw_score
    FROM mine_doc_knowledge
    WHERE mine_id = 'MINE-001'
      AND MATCH(chunk_text, summary) AGAINST ('gas power cutoff evacuation')
    LIMIT 20
),
reranked AS (
    SELECT k.*, COSINE_SIMILARITY(d.content_vector,
        AI_EMBEDDING('conn_dashscope:text-embedding-v3', 'CH4 overrun personnel evacuation power cutoff response plan')
    ) AS vec_score
    FROM kw_results k JOIN mine_doc_knowledge d
         ON k.doc_id = d.doc_id AND k.chunk_id = d.chunk_id
)
SELECT doc_id, summary, lessons_learned,
       kw_score * 0.3 + vec_score * 0.7 AS hybrid_score  -- Higher weight on vector
FROM reranked
ORDER BY hybrid_score DESC LIMIT 5;
```

All three retrieval capabilities are expressed directly in SQL — no separate search engine (Elasticsearch/Milvus) required.

---

## 4. Singdata Technical Advantages

### Dynamic Table: Two-Level Real-Time Incremental Processing — Replacing the Flink + Batch Dual Stack

Mine sensors generate thousands of records per second; safety alerts cannot wait for batch processing windows. Singdata uses a single mechanism to cover both minute-level aggregation and second-level trend computation:

| Layer | Refresh Interval | Purpose | Traditional Equivalent |
|------|---------|------|------------|
| Real-time Pipeline | 1 min (Studio Cron) | Single-point threshold extreme value triggering | Flink CEP Rule Engine |
| Aggregation DT | 5 min | Multi-sensor rolling aggregation + risk rating | Spark Structured Streaming |
| Anomaly DT | 5 min | Cross-system correlation + composite rating | Independent correlation service |
| Trend Prediction DT | 5 min | CH₄ slope + 30min prediction | Independent time-series prediction service |

```sql
-- 4 time window types, same SQL paradigm, zero additional systems
CREATE DYNAMIC TABLE mine_ch4_trend      REFRESH INTERVAL 5 MINUTE AS ...;
CREATE DYNAMIC TABLE mine_belt_health    REFRESH INTERVAL 30 MINUTE AS ...;
CREATE DYNAMIC TABLE mine_power_features REFRESH INTERVAL 30 MINUTE AS ...;
```

Change Tracking drives incremental computation — TB-scale historical data does not affect refresh performance. Traditional solutions require a separate stream processing cluster (Flink/Spark Streaming) plus a batch scheduling system. Singdata replaces both with declarative SQL.

### AI_CLASSIFY + AI_COMPLETE: SQL-Embedded Two-Level AI Inference

Mine safety requires two fundamentally different AI capabilities, which Singdata chains together in a single CTE:

**Level 1: AI_CLASSIFY Fast Classification (low latency, low cost)**

Performs multi-class classification on anomaly summaries, outputting disaster type labels (GAS/FIRE/ROOF/FLOOD/EQUIPMENT/COMPOUND). Compared to using AI_COMPLETE to ask "what type of disaster is this," classification is faster, consumes fewer tokens, and is suited for high-frequency trigger scenarios:

```sql
AI_CLASSIFY(
    'conn_dashscope:deepseek-v3',
    anomaly_summary,
    ARRAY('GAS', 'FIRE', 'ROOF', 'FLOOD', 'EQUIPMENT', 'COMPOUND')
) AS classify_json  -- Returns {"label":"GAS","score":0.92}
```

**Level 2: AI_COMPLETE Structured Response Plan Generation (deep reasoning)**

Injects the disaster type + cross-system anomaly summary + RAG-retrieved historical accident experience together into the Prompt to generate a complete response plan. The CTE structure ensures each level is called exactly once, avoiding result inconsistencies from repeated calls:

```sql
WITH classified AS (
    SELECT *, REGEXP_EXTRACT(AI_CLASSIFY(...), '(?s)\{.*\}', 0) AS classify_json
    FROM anomalies
),
completed AS (
    SELECT *, REGEXP_EXTRACT(AI_COMPLETE('conn_dashscope:deepseek-v3',
        CONCAT('Disaster type: ', GET_JSON_OBJECT(classify_json,'$.label'),
               '; Historical similar cases: ', rag_context,
               '; Current anomaly: ', anomaly_summary, ...)),
        '(?s)\{.*\}', 0) AS complete_json
    FROM classified
)
-- All fields extracted from the same JSON, results fully consistent
SELECT GET_JSON_OBJECT(complete_json, '$.alert_title')      AS alert_title,
       GET_JSON_OBJECT(complete_json, '$.immediate_actions') AS immediate_actions, ...
FROM completed;
```

Compared to a standalone AI platform: zero data movement, no additional latency, no ETL cost.

### API Connection: Unified Multi-Model Management

All AI calls go through a single `conn_dashscope` connection entry, supporting runtime model switching, key rotation, and rate-limiting circuit breakers — without modifying any SQL logic:

```sql
-- Currently using DeepSeek-V3; switching to Qwen-Max only requires updating the Connection configuration
CREATE API CONNECTION IF NOT EXISTS conn_dashscope
TYPE ai_function
PROPERTIES (
    'BASE_URL' = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'API_KEY'  = '<your-api-key>'
);
-- SQL references remain unchanged: AI_COMPLETE('conn_dashscope:deepseek-v3', ...)
--                               → AI_COMPLETE('conn_dashscope:qwen-max', ...)
```

Supports connecting to multiple LLMs (DashScope, DeepSeek, OpenAI-compatible interfaces), as well as domain fine-tuned mine safety proprietary models.

### BloomFilter: Millisecond-Level Retrieval Across Tens of Millions of Monitoring Points

A single mine has 500–2,000 sensor points; medium-sized mine areas can reach tens of thousands; group-level can reach hundreds of thousands. BloomFilter indexes reduce point-query latency on zone_id/sensor_type/event_level from seconds to milliseconds — the foundation for high-frequency alert queries:

```sql
CREATE BLOOMFILTER INDEX idx_bf_vent_zone    ON TABLE mine_ventilation_sensors(zone_id);
CREATE BLOOMFILTER INDEX idx_bf_alert_level  ON TABLE mine_ai_safety_alerts(overall_risk_level);
CREATE BLOOMFILTER INDEX idx_bf_rt_level     ON TABLE mine_realtime_alerts(threshold_level);
```

### Full-Text Search: Fast Keyword Lookup in Accident Knowledge Base

Accident investigation reports, regulation clauses, and maintenance records accumulated over the years can be indexed with FULLTEXT INDEX, allowing dispatchers to search directly with Chinese keywords (e.g., "ZONE-101 gas power cutoff") — no separate Elasticsearch cluster required:

```sql
-- Full-text index (IK Chinese word segmentation, supports mine-specific terminology)
CREATE FULLTEXT INDEX idx_ft_know_text
    ON TABLE mine_doc_knowledge(chunk_text, summary, key_findings, lessons_learned)
    WITH PROPERTIES ('analyzer' = 'ik_max_word');

-- Full-text search on safety alert response records
CREATE FULLTEXT INDEX idx_ft_alert_actions
    ON TABLE mine_ai_safety_alerts(immediate_actions, alert_title)
    WITH PROPERTIES ('analyzer' = 'ik_max_word');
```

**Why full-text search fits this scenario:** Mine accident reports contain extensive industry terminology (e.g., "fully-mechanized mining face," "roof weighting," "goaf spontaneous combustion"). Exact keyword matching is more than 100× faster than LIKE fuzzy queries, with relevance ranking, helping dispatchers find the most relevant historical response plans in seconds.

```sql
-- After an alert triggers, automatically retrieve related historical experience (millisecond response)
SELECT summary, lessons_learned,
       MATCH(chunk_text, summary) AGAINST ('CH4 overrun power cutoff evacuation' IN NATURAL LANGUAGE MODE) AS score
FROM mine_doc_knowledge
WHERE mine_id = 'MINE-001'
  AND MATCH(chunk_text, summary) AGAINST ('CH4 overrun power cutoff evacuation' IN NATURAL LANGUAGE MODE)
ORDER BY score DESC LIMIT 5;
```

### Vector Search: Semantic Similarity Search and RAG Enhancement

Keyword search depends on exact vocabulary matching and cannot handle cases with "different wording but identical meaning." Vector search is based on semantic vectors generated by AI_EMBEDDING — even with completely different phrasing, semantically similar content can be retrieved:

```sql
-- Vector index (HNSW algorithm, cosine similarity)
CREATE VECTOR INDEX idx_vec_know_content
    ON TABLE mine_doc_knowledge(content_vector)
    WITH PROPERTIES ('metric_type' = 'cosine', 'index_type' = 'hnsw');

-- AI_EMBEDDING generates vectors (called in pipeline.sql Pipeline B)
AI_EMBEDDING('conn_dashscope:text-embedding-v3', summary_text) AS content_vector
```

**RAG Three-Step Process (entirely within SQL):**

```sql
-- Step 1: Vectorize the current alert
-- Step 2: Vector search for Top-K similar historical cases
-- Step 3: Inject search results into AI_COMPLETE Prompt
WITH query_vec AS (
    SELECT AI_EMBEDDING('conn_dashscope:text-embedding-v3', anomaly_summary) AS vec
    FROM mine_ai_safety_alerts WHERE alert_id = 'ALERT-ZONE-101-xxx'
),
top_k AS (
    SELECT k.lessons_learned,
           COSINE_SIMILARITY(k.content_vector, q.vec) AS sim
    FROM mine_doc_knowledge k CROSS JOIN query_vec q
    WHERE k.doc_type = 'ACCIDENT_REPORT'
    ORDER BY sim DESC LIMIT 3
)
SELECT AI_COMPLETE('conn_dashscope:deepseek-v3',
    CONCAT('Historical similar incident experience:\n',
           GROUP_CONCAT(lessons_learned SEPARATOR '\n'),
           '\n\nBased on the above experience, provide response recommendations: ', anomaly_summary)
) AS rag_advice
FROM top_k, mine_ai_safety_alerts
WHERE alert_id = 'ALERT-ZONE-101-xxx';
```

**Synergy with BloomFilter:** Before vector search, use BloomFilter to filter by mine_id and doc_type to narrow the candidate set, then perform ANN search — reducing retrieval latency from seconds to hundreds of milliseconds.

**Why a standalone vector database (Milvus/Pinecone) is not needed:** Singdata natively supports the VECTOR field type and VECTOR INDEX. Vector search and structured filtering (mine_id, zone_id, doc_type) are completed in a single SQL statement, with no cross-system data synchronization required.

### Lakehouse Unified Architecture: Eliminating Data Silos

Traditional mine six-system architectures are each independently operated; cross-system correlation analysis requires a custom integration layer. Singdata Lakehouse places all data in the same storage layer, making cross-system JOINs nearly indistinguishable in performance from single-table queries:

```sql
-- Six subsystems, one SQL completing cross-system correlation, no intermediate layer, no data copying
FROM mine_ventilation_metrics v
LEFT JOIN mine_personnel_metrics p  ON v.zone_id = p.zone_id AND v.mine_id = p.mine_id
LEFT JOIN mine_power_metrics     pw ON v.zone_id = pw.zone_id AND v.mine_id = pw.mine_id
LEFT JOIN mine_excavation_metrics ex ON ...
LEFT JOIN mine_transport_metrics  tr ON ...
```

The same platform supports real-time streaming (Dynamic Table), batch processing (INSERT SELECT), AI inference (AI_COMPLETE), and unstructured processing (offline Pipeline B) — unified operations and unified access control.

### Studio: End-to-End Operations Automation

Studio incorporates the entire data pipeline into unified scheduling — no external scheduling tools (Airflow/DolphinScheduler) required:

| Studio Capability | Usage in the Mine Solution |
|------------|----------------|
| Task scheduled execution (Cron) | Real-time pipeline 1-min alerts + offline pipeline daily knowledge base updates |
| Workflow DAG orchestration | Dependency ordering for REFRESH DT → AI inference → alert write |
| API Connection management | DeepSeek key encrypted storage, runtime model switching |
| Runtime monitoring dashboard | DT refresh latency, AI inference success rate, ingestion_lag_ms visualization |
| SQL editor | Dynamic Table interactive debugging, AI_COMPLETE Prompt iteration |

### Technical Advantages Comparison Summary

| Capability Dimension | Traditional Solution | Singdata Lakehouse |
|---------|---------|---------------------|
| Real-time alert latency | 5–15 minutes (batch window) | ≤ 90 seconds (real-time pipeline) / 5 minutes (DT aggregation) |
| Cross-system correlation | Custom integration layer, months to deliver | SQL JOIN, delivered in days |
| AI response recommendations | Standalone AI platform + ETL sync | AI_COMPLETE embedded, zero data movement |
| Disaster type classification | Manual judgment / rule engine | AI_CLASSIFY millisecond-level classification |
| Historical knowledge retrieval | Manual archive search | Full-text search (IK segmentation) + vector search (HNSW) + Hybrid Search |
| RAG enhancement | Standalone vector DB (Milvus) + sync pipeline | SQL-embedded AI_EMBEDDING + VECTOR INDEX, zero external dependencies |
| Unstructured documents | Standalone document management, data isolated | Offline pipeline unified ingestion, knowledge accumulation |
| Operational complexity | Kafka + Flink + Spark + AI platform + ETL | Single Singdata + Studio |
| PoC delivery cycle | 6–12 months | 6 weeks |

---

## 5. Customer Value

### ROI Estimation

| Metric | Before | After | Improvement |
|------|--------|--------|---------|
| Major safety incidents | Baseline | -50%+ | Reduced compliance risk, fewer regulatory penalties |
| Unplanned downtime duration | Baseline | -40%+ | At coal price 820 RMB/ton, each 1h reduction avoids losses of 200,000–800,000 RMB |
| Violation detection rate | ~30% (manual inspection) | 90%+ | Violation-caused accident rate down 60% |
| Incident investigation cycle | 3–7 days | < 1 day | System automatically correlates multi-system logs |
| PoC construction cycle | Traditional 6–12 months | 6 weeks | SQL-first, no separate ETL + AI platform |

### Operational Efficiency Improvement

| Direction | Improvement |
|------|------|
| Dispatch decisions | Data-driven replaces experience-based judgment; alert lead time increases from 0 to 15–30 minutes |
| Compliance reporting | Automatically generates regulatory-required reports; data retained ≥ 1 year |
| Maintenance planning | AI predicts remaining useful life of equipment, shifting from "emergency repairs" to "preventive maintenance" |

### Construction Cost Comparison with Traditional Solutions

| Dimension | Traditional Solution (Distributed Systems) | Singdata Lakehouse |
|------|---------------------|---------------------|
| Number of systems | 6+ independent systems | 1 unified platform |
| Cross-system linkage | Requires custom integration layer | SQL JOIN natively supported |
| AI capability | Standalone AI platform + MLOps | AI_COMPLETE built-in |
| Operations staff | Dedicated ops required per system | Unified operations |
| Data retention cost | Distributed storage, high duplication cost | Unified Lakehouse, low storage cost |

### Full Capability Overview

This solution covers the core capabilities for the current phase and includes the technical foundation for the following advanced scenarios:

| Scenario | Core Technology | Expected Value | Status |
|------|---------|---------|------|
| Six-system real-time early warning | Dynamic Table + cross-system JOIN | Alert lead time 15–30 min | **Implemented** |
| AI disaster classification + response recommendations | AI_CLASSIFY + AI_COMPLETE CTE | Response plans auto-generated | **Implemented** |
| Real-time pipeline (1-min window) | Change Tracking + Studio Cron | Latency ≤ 90s, regulation thresholds hardcoded | **Implemented** |
| Offline knowledge base + RAG | AI_COMPLETE + mine_doc_knowledge | Historical experience injected into Prompt | **Implemented** |
| Full-text search (accident knowledge base) | FULLTEXT INDEX + IK segmentation | Chinese keyword case lookup in seconds | **Implemented** |
| Vector search (semantic similarity) | VECTOR INDEX + AI_EMBEDDING + HNSW | RAG semantic enhancement, no standalone vector DB | **Implemented** |
| Hybrid Search | Full-text recall + vector re-ranking, weighted fusion | Optimized precision + recall | **Implemented** |
| CH₄ concentration trend prediction | Dynamic Table sliding window slope | Alert lead time +20–30 min | Extensible |
| Belt health scoring | Shift-aggregated weighted scoring | Unplanned downtime -40% | Extensible |
| Personnel abnormal behavior detection | Window function trajectory stationary analysis | Reduced search and rescue response time | Extensible |
| Power load forecasting | Historical features + AI_COMPLETE time-series prediction | Annual energy savings 300k–800k RMB/mine | Extensible |
| Equipment PHM (RUL prediction) | Feature engineering + AI prediction + auto work orders | Downtime reduced 50% | Extensible |
| Intelligent ventilation network optimization | Ventilation network computation + AI fan scheduling | Ventilation power consumption -15–20% | Extensible |
| Digital twin 3D visualization | 3D data interface + real-time view DT | Dispatch decision time reduced to seconds | Planned |
| Mine safety domain large model | Corpus construction + SFT fine-tuning | AI recommendation accuracy +30–50% | Planned |
| Automated compliance reporting | AQ 1029 format + Studio push | Zero manual effort, zero missed reports | Planned |
| Multi-mine group management | Cross-workspace sync + safety scoring | Group accident rate -30% | Planned |

---

## 6. Quick Start

### Prerequisites

1. Singdata Lakehouse workspace (schema already created)
2. DashScope / DeepSeek API Key (for AI_COMPLETE)

### Execution Order

> **⚠️ Time Sensitivity (verified conclusion)**: The sliding window for aggregation-layer Dynamic Tables is **10 minutes**. Timestamps in `test_data.sql` are based on relative offsets from execution time. **The REFRESH in step 3 must be completed within 8 minutes of finishing test_data.sql execution**, otherwise data falls outside the window and the DT returns empty results.

```bash
# Step 1: Create tables, indexes, Change Tracking (first run only)
execute setup.sql

# Step 2: Write test data
execute test_data.sql

# ⏱ Execute step 3 immediately after step 2 (within 8 minutes)

# Step 3: Create Dynamic Tables and immediately REFRESH
execute pipeline.sql   # Contains CREATE DYNAMIC TABLE statements

REFRESH DYNAMIC TABLE mine_ventilation_metrics;
REFRESH DYNAMIC TABLE mine_transport_metrics;
REFRESH DYNAMIC TABLE mine_excavation_metrics;
REFRESH DYNAMIC TABLE mine_power_metrics;
REFRESH DYNAMIC TABLE mine_personnel_metrics;
REFRESH DYNAMIC TABLE mine_production_metrics;
REFRESH DYNAMIC TABLE mine_cross_system_anomalies;

# Step 4: Execute AI alert generation (replace API Key in pipeline.sql first)
# Execute the INSERT INTO mine_ai_safety_alerts section of pipeline.sql
```

### Validation Queries

```sql
-- 1. Aggregation layer: confirm ZONE-101 CH4 exceeds production cutoff threshold (≥ 1.0%)
SELECT zone_id, ch4_max_pct, co_max_ppm, wind_speed_min,
       temp_max_celsius, ch4_risk_level, co_risk_level, temp_risk_level
FROM mine_ventilation_metrics
ORDER BY ch4_max_pct DESC;
-- Expected: ZONE-101 ch4_max_pct=1.62 (CRITICAL), co_max_ppm=32, ch4_risk_level=CRITICAL

-- 2. Cross-system anomaly layer: ZONE-101 CRITICAL (CH4 overrun + personnel present + feeder not tripped)
SELECT zone_id, overall_risk_level, persons_in_danger,
       feeder_switch_status, anomaly_summary
FROM mine_cross_system_anomalies
ORDER BY overall_risk_level;
-- Expected: ZONE-101 overall_risk_level=CRITICAL, persons_in_danger=3
--           anomaly_summary contains "CH4 concentration 1.62% [critical overrun]; 3 persons in hazardous zone; feeder switch not tripped"

-- 3. Personnel risk check (3 in danger zone)
SELECT zone_id, total_persons, persons_in_danger, personnel_risk_level
FROM mine_personnel_metrics
WHERE personnel_risk_level != 'NORMAL';
-- Expected: ZONE-101 persons_in_danger=3, personnel_risk_level=CRITICAL

-- 4. Transport risk (ZONE-201 belt deviation)
SELECT zone_id, device_id, belt_deviation_mm, transport_risk_level, device_status
FROM mine_transport_metrics
WHERE transport_risk_level != 'NORMAL';
-- Expected: ZONE-201 belt_deviation_mm=68, transport_risk_level=HIGH, device_status=ALARM

-- 5. AI alert work orders
SELECT alert_id, zone_id, overall_risk_level, disaster_type, disaster_confidence,
       alert_title, evacuation_required, power_cutoff_required,
       immediate_actions, responsible_team
FROM mine_ai_safety_alerts
ORDER BY alert_at DESC;
-- Expected: HIGH/CRITICAL alerts have complete immediate_actions, disaster_type=GAS,
--           evacuation_required=true, power_cutoff_required=true
```

### Re-validation (When Test Data Has Expired)

If the previously written test data was inserted more than 10 minutes ago, Dynamic Tables will return empty results. Reset steps:

```bash
# Option A: Clear data only, keep table structure (recommended, faster)
# Uncomment TRUNCATE statements in teardown.sql and execute,
# then restart from step 2

# Option B: Full rebuild (drop all objects and re-run setup.sql)
execute teardown.sql   # DROP all tables and DTs
execute setup.sql      # Rebuild table structure
# Then start from step 2
```

### Clean Up Environment

```bash
execute teardown.sql   # Executes in DROP mode by default (confirm TRUNCATE comments are not active or skip the TRUNCATE section)
```

---

## Related Documentation

### AI Functions

| Document | Description |
|------|------|
| [AI Functions Overview](../ai_functions_overview.md) | General introduction to AI functions, model selection, invocation methods, and billing |
| [AI_CLASSIFY](../ai_classify.md) | Multi-label classification function; used in this solution for rapid disaster type classification (GAS/FIRE/ROOF/FLOOD/EQUIPMENT/COMPOUND) at lower cost than AI_COMPLETE |
| [AI_COMPLETE](../ai_complete.md) | General LLM inference function; used in this solution to generate structured response plans (evacuation/power cutoff/emergency commands) and supports RAG injection of historical incident experience |
| [AI_EMBEDDING](../ai_embedding.md) | Text vectorization function; used in this solution to convert accident reports and alert summaries to semantic vectors, powering vector search and RAG enhancement |
| [CREATE API CONNECTION](../create-api-connection.md) | Create API Connection for unified LLM credential management, supporting runtime model switching without modifying SQL |

### Dynamic Table

| Document | Description |
|------|------|
| [Dynamic Table Introduction](../dynamic_table_summary.md) | Dynamic Table core concepts, incremental refresh mechanism, and comparison with Flink/Spark Streaming |
| [Dynamic Table Development Guide](../sql_dynamic_table_guide.md) | End-to-end example of creating, refreshing, and viewing history |
| [CREATE DYNAMIC TABLE](../create-dynamic-table.md) | Table creation syntax reference, including `REFRESH INTERVAL`, `change_tracking`, and other parameter descriptions |
| [Dynamic Table Refresh Scheduling](../dynamic-table-scheduling.md) | Scheduled refresh configuration, controlling refresh frequency for each aggregation layer (5 min), health score layer (30 min), and group dashboard (10 min) |
| [Using Studio to Develop and Monitor Dynamic Tables](../dynamic_table_using_studio.md) | Monitor Dynamic Table refresh latency and multi-layer pipeline health via Studio |

### Indexes

| Document | Description |
|------|------|
| [Index Overview](../index-overview.md) | Use cases and selection comparison for various index types (BloomFilter / Inverted / Vector) |
| [BloomFilter Index](../bloomfilter-summary.md) | BloomFilter working principles; used in this solution to accelerate equality queries on high-cardinality columns such as zone_id / event_level / sensor_type |
| [CREATE BLOOMFILTER INDEX](../create-bloomfilter-index.md) | BloomFilter index creation syntax reference |
| [Inverted Index](../inverted-index.md) | Inverted index overview, supporting full-text search and IK Chinese word segmentation |
| [CREATE INVERTED INDEX](../create-inverted-index.md) | Full-text index creation syntax; used in this solution for Chinese keyword search in accident reports and response records (supporting mine-specific terminology) |
| [Vector Index](../vector-search.md) | Vector index overview, supporting HNSW approximate nearest neighbor search and cosine similarity |
| [CREATE VECTOR INDEX](../create-vector-index.md) | Vector index creation syntax; used in this solution for semantic similarity search, synergizing with BloomFilter to narrow the candidate set |
| [Vector Search and RAG Applications in Practice](../sql_vector_search_guide.md) | End-to-end RAG practice including vectorization, retrieval, and Prompt injection, directly corresponding to the RAG enhancement pattern in this solution |
| [Best Practices for Full-Text + Vector Hybrid Search with RRF](../rrf-fulltext-vector-hybrid-search-best-practices.md) | Hybrid Search best practices, corresponding to the full-text recall + vector re-ranking weighted fusion pattern in this solution |
| [Lakehouse Index Best Practices Guide](../lakehouse-index-best-practice.md) | Combined usage strategies for partition pruning + BloomFilter + full-text + vector indexes |

### Partitioned Tables

| Document | Description |
|------|------|
| [Partitioning and Bucketing](../partition_table_guide.md) | Partition table design concepts, including `PARTITIONED BY (DAYS(...))` time partitioning usage |
| [Partitioned Table Usage Guide](../notes-and-guidelines-for-partition-tables.md) | Partition table guidelines, including the constraint that composite primary keys must include the partition key (the basis for `collected_at`/`event_at` being first in the primary key for each table in this solution) |

### Window Functions

| Document | Description |
|------|------|
| [Window Functions Overview](../windowfunction.md) | Window function syntax, including `OVER (PARTITION BY ... ORDER BY ...)` usage |
| [lag](../sql_functions/window_functions/lag.md) | Lag function; used in personnel behavior detection in this solution to compare previous and current positions to determine if stationary |

### JSON and Regular Expression Functions

| Document | Description |
|------|------|
| [get_json_object](../sql_functions/scalar_functions/json_functions/get_json_object.md) | Extract specified path fields from JSON strings; used in this solution to parse `$.label`, `$.advice`, and other fields returned by `AI_CLASSIFY` and `AI_COMPLETE` |
| [regexp_extract](../sql_functions/scalar_functions/string_functions/regexp_extract.md) | Regular expression extraction function; used in this solution with DOTALL mode `(?s)\{.*\}` to strip markdown code fences that may appear in LLM responses |

### Studio Tasks and Scheduling

| Document | Description |
|------|------|
| [Studio Task Development and Operations](../cz-cli-studio-tasks.md) | Studio Task creation, deployment, and Cron scheduling; used in this solution for real-time pipeline 1-minute window triggering and offline knowledge base daily batch updates |
| [Studio Task Development and Operations Best Practices](../studio-task-practice.md) | Studio Task best practices, including DAG dependency orchestration and runtime monitoring alert configuration |
