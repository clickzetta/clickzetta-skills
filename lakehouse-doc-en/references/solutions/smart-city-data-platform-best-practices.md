# Build a Smart City Government Data Platform

Aggregate open data from multiple government departments — transportation, urban management, civil affairs, public health, and more — to build a four-layer data warehouse supporting city operations KPI dashboards and cross-department joint analysis. This guide uses three NYC Open Data datasets (311 citizen complaint tickets, traffic accidents, and health inspections) to walk through the complete **COPY INTO + Volume → ODS → DWD → DWS → ADS** pipeline, covering five key capabilities: External Schema (connecting existing Hive data lakes), RBAC (multi-department data isolation), Dynamic Table (cross-department data fusion), Table Stream (complaint ticket status change capture), and Column Masking (PII field de-identification).

![](/.topwrite/assets/anim-18-smart-city.svg)

---

## Overview

The core challenges for a government data platform: diverse data sources, inconsistent formats, complex permission boundaries, and a need to support cross-department joint analysis while protecting individual privacy.

| Problem | Solution |
|---|---|
| Departments periodically submit CSV files that need to be batch-loaded into the warehouse | COPY INTO + Volume — declarative loading, automatically skips already-loaded files |
| Existing Hive data lake holds historical data with high migration cost | External Schema mounts Hive metadata for direct cross-source federated queries |
| Different departments' data formats are inconsistent; they need to be standardized into city-topic events | Dynamic Table with CTE-based UNION ALL; automatically incremental fusion |
| Some fields (coordinates, names) are PII and need dynamic masking | Column Masking bound to columns, masking is transparent to all queries |
| Department analysts can only see their own department's data; admins see everything | RBAC — grant SELECT on schema or table level by role |
| Complaint ticket status changes need to be captured in real time to drive processing statistics | Table Stream — captures UPDATE_BEFORE / UPDATE_AFTER |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create ODS layer raw data tables for each department | Regular tables, targets for COPY INTO |
| `COPY INTO` | Batch import CSV files from each department via Volume | Automatically skips already-loaded files |
| `CREATE EXTERNAL SCHEMA` | Mount existing Hive data lake | No migration needed; direct federated queries |
| `CREATE TABLE STREAM` | Capture complaint ticket status changes | STANDARD mode — supports INSERT / UPDATE / DELETE |
| `CREATE DYNAMIC TABLE` | Create DWD / DWS / ADS three-layer incremental computation tables | Declarative SQL; automatic dependency-chain refresh |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |
| `CREATE ROLE` / `GRANT` / `REVOKE` | Role creation and permission management | Multi-department data isolation |
| `ALTER TABLE ... CHANGE COLUMN ... SET MASK` | Bind Column Masking de-identification policy | PII field dynamic masking |

---

## Prerequisites

All examples in this guide run under the `best_practice_smart_city` schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_smart_city;
```

---

## ODS (Raw Data Layer): Raw Data Tables for Each Department

The ODS layer stores data by source department in isolation. This guide demonstrates three data types: NYC 311 complaint tickets (citizen services hotline), traffic accidents (DOT/NYPD), and health inspections (Dept of Health) — all corresponding to the real data structures in NYC Open Data.

### Create Tables

```sql
CREATE TABLE IF NOT EXISTS best_practice_smart_city.doc_ods_311_complaints (
    complaint_id      STRING,
    created_date      TIMESTAMP,
    closed_date       TIMESTAMP,
    agency            STRING,
    agency_name       STRING,
    complaint_type    STRING,
    descriptor        STRING,
    location_type     STRING,
    incident_zip      STRING,
    incident_address  STRING,
    city              STRING,
    borough           STRING,
    latitude          DOUBLE,
    longitude         DOUBLE,
    status            STRING,
    resolution_desc   STRING,
    community_board   STRING,
    bbl               STRING,
    open_data_channel STRING,
    load_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

```sql
CREATE TABLE IF NOT EXISTS best_practice_smart_city.doc_ods_traffic_accidents (
    accident_id           STRING,
    crash_date            DATE,
    crash_time            STRING,
    borough               STRING,
    zip_code              STRING,
    latitude              DOUBLE,
    longitude             DOUBLE,
    on_street_name        STRING,
    cross_street_name     STRING,
    persons_injured       INT,
    persons_killed        INT,
    pedestrians_injured   INT,
    pedestrians_killed    INT,
    cyclists_injured      INT,
    cyclists_killed       INT,
    motorists_injured     INT,
    motorists_killed      INT,
    vehicle_type_1        STRING,
    vehicle_type_2        STRING,
    contributing_factor_1 STRING,
    contributing_factor_2 STRING,
    load_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

```sql
CREATE TABLE IF NOT EXISTS best_practice_smart_city.doc_ods_health_inspections (
    inspection_id   STRING,
    facility_name   STRING,
    facility_type   STRING,
    borough         STRING,
    zip_code        STRING,
    inspection_date DATE,
    inspection_type STRING,
    violation_code  STRING,
    violation_desc  STRING,
    grade           STRING,
    grade_date      DATE,
    score           INT,
    latitude        DOUBLE,
    longitude       DOUBLE,
    load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

```sql
CREATE TABLE IF NOT EXISTS best_practice_smart_city.doc_dim_district (
    district_code STRING,
    district_name STRING,
    borough       STRING,
    city          STRING,
    population    INT,
    area_sqkm     DOUBLE,
    district_type STRING
);
```

### Batch Import CSV Files via COPY INTO + Volume

Departments periodically submit their data as CSV files stored in their own dedicated object storage directories. First create a Volume pointing to the department's upload directory, then use COPY INTO for batch import.

Step 1: Create a Storage Connection and Volume (Alibaba Cloud OSS example):

```sql
-- Create Storage Connection
CREATE STORAGE CONNECTION IF NOT EXISTS conn_city_data
TYPE = OSS
ACCESS_ID = '<your-access-id>'
ACCESS_KEY = '<your-access-key>'
ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com';

-- Create Volume for 311 complaint data
CREATE EXTERNAL VOLUME IF NOT EXISTS best_practice_smart_city.vol_311_complaints
TYPE = OSS
BUCKET = '<your-bucket>'
PATH = 'smart-city/311_complaints/'
CONNECTION = conn_city_data;
```

Step 2: Run COPY INTO to load:

```sql
COPY INTO best_practice_smart_city.doc_ods_311_complaints
FROM VOLUME best_practice_smart_city.vol_311_complaints
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
ON_ERROR = CONTINUE;
```

> ⚠️ **Note**: `ON_ERROR = CONTINUE` skips malformed rows and continues loading. In production, change to `ON_ERROR = ABORT` and after loading use `SELECT * FROM load_history('doc_ods_311_complaints')` to see skipped files — this prevents silent data loss.

COPY INTO automatically records metadata for loaded files; re-running the same COPY statement will not re-import the same files. This is very useful for periodic department submissions: just trigger COPY INTO on a schedule and the system automatically processes only new files.

View load history:

```sql
SELECT * FROM load_history('doc_ods_311_complaints') LIMIT 5;
```

### External Schema: Connect Existing Hive Data Lake

If a department already has a Hive data lake with historical data, External Schema can mount it directly without migration.

```sql
-- First create a Connection pointing to the Hive Metastore
CREATE CATALOG CONNECTION IF NOT EXISTS conn_hive_metastore
CATALOG_TYPE = HIVE
METASTORE_URI = 'thrift://<hive-metastore-host>:9083'
HDFS_DEFAULT_FS = 'hdfs://<namenode>:8020';

-- Mount the Hive database as an External Schema
CREATE EXTERNAL SCHEMA IF NOT EXISTS hive_civil_affairs
CONNECTION = conn_hive_metastore
DATABASE = 'civil_affairs_db';
```

After mounting, query Hive tables directly:

```sql
-- Federated query: Hive historical data + Singdata new data
SELECT
    ha.district_code,
    ha.population_2020,
    COUNT(c.complaint_id) AS recent_complaints
FROM hive_civil_affairs.district_population ha
LEFT JOIN best_practice_smart_city.doc_ods_311_complaints c
    ON ha.zip_code = c.incident_zip
    AND c.created_date >= CAST('2026-01-01' AS TIMESTAMP)
GROUP BY ha.district_code, ha.population_2020;
```

> 💡 **Tip**: External Schema is read-only. Write operations still need to be performed in the Singdata schema. It is suited for transitional architectures where Hive serves as the historical archive layer and Singdata as the incremental processing layer.

---

## Table Stream: Capture Complaint Ticket Status Changes

311 complaint tickets go through multiple status changes during processing (`Open` → `In Progress` → `Closed`). Each change needs to be recorded in an audit log for processing timeliness analysis.

### Create Table Stream

Create a STANDARD-mode Stream on the complaint tickets table to capture all INSERT / UPDATE / DELETE operations:

```sql
CREATE TABLE STREAM IF NOT EXISTS best_practice_smart_city.doc_stream_complaint_changes
ON TABLE best_practice_smart_city.doc_ods_311_complaints
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

Verify the Stream was created:

```sql
SHOW STREAMS IN best_practice_smart_city;
```

```
create_time                  | schema_name                 | name                           | table_name                                                              | mode     | comment
-----------------------------+-----------------------------+--------------------------------+-------------------------------------------------------------------------+----------+--------
2026-06-06T14:40:10.831      | best_practice_smart_city    | doc_stream_complaint_changes   | quick_start.best_practice_smart_city.doc_ods_311_complaints            | STANDARD |
```

> ⚠️ **Note**: Streams only record changes **after creation** — historical data that existed before the Stream was created will not appear in the Stream. If you need a historical snapshot, run a `SELECT` to archive data before creating the Stream.

### Simulate Ticket Status Changes

```sql
-- Ticket CMP002: Sewer Backup complaint resolved
UPDATE best_practice_smart_city.doc_ods_311_complaints
SET status = 'Closed',
    closed_date = CAST('2026-01-10 16:00:00' AS TIMESTAMP),
    resolution_desc = 'Issue resolved after second inspection.'
WHERE complaint_id = 'CMP002';

-- Ticket CMP015: Elevator repair completed
UPDATE best_practice_smart_city.doc_ods_311_complaints
SET status = 'Closed',
    closed_date = CAST('2026-01-11 10:00:00' AS TIMESTAMP),
    resolution_desc = 'Elevator maintenance completed.'
WHERE complaint_id = 'CMP015';
```

### Consume Stream: Write to Ticket Audit Log

Complaint ticket status change audit log table:

```sql
CREATE TABLE IF NOT EXISTS best_practice_smart_city.doc_dwd_complaint_audit_log (
    complaint_id    STRING,
    change_type     STRING,
    change_version  BIGINT,
    change_time     TIMESTAMP,
    new_status      STRING,
    closed_date     TIMESTAMP,
    resolution_desc STRING,
    agency          STRING,
    borough         STRING,
    complaint_type  STRING
);
```

View change records in the Stream (preview with SELECT before consuming):

```sql
SELECT __change_type, complaint_id, status, closed_date, __commit_timestamp
FROM best_practice_smart_city.doc_stream_complaint_changes
LIMIT 10;
```

```
__change_type | complaint_id | status | closed_date         | __commit_timestamp
--------------+--------------+--------+---------------------+--------------------
UPDATE_AFTER  | CMP002       | Closed | 2026-01-10T16:00:00 | 2026-06-06T14:42:56.449
UPDATE_AFTER  | CMP015       | Closed | 2026-01-11T10:00:00 | 2026-06-06T14:43:02.979
UPDATE_BEFORE | CMP002       | Open   | null                | 2026-06-06T14:37:45.066
UPDATE_BEFORE | CMP015       | In Progress | null           | 2026-06-06T14:37:45.066
```

In STANDARD mode, each UPDATE produces one `UPDATE_BEFORE` (before the change) and one `UPDATE_AFTER` (after the change). Consume changes and advance the offset with `INSERT INTO ... SELECT FROM stream`:

```sql
-- Keep only UPDATE_AFTER rows, write to audit log
INSERT INTO best_practice_smart_city.doc_dwd_complaint_audit_log
SELECT
    complaint_id,
    __change_type                AS change_type,
    __commit_version             AS change_version,
    __commit_timestamp           AS change_time,
    status                       AS new_status,
    closed_date,
    resolution_desc,
    agency,
    borough,
    complaint_type
FROM best_practice_smart_city.doc_stream_complaint_changes
WHERE __change_type = 'UPDATE_AFTER';
```

Verify after consumption that the offset has advanced — Stream becomes empty:

```sql
SELECT COUNT(*) AS remaining_changes
FROM best_practice_smart_city.doc_stream_complaint_changes;
```

```
remaining_changes
-----------------
0
```

View the audit log:

```sql
SELECT complaint_id, change_type, change_version, change_time,
       new_status, borough, complaint_type
FROM best_practice_smart_city.doc_dwd_complaint_audit_log
ORDER BY change_time;
```

```
complaint_id | change_type  | change_version | change_time             | new_status | borough  | complaint_type
-------------+--------------+----------------+-------------------------+------------+----------+---------------
CMP002       | UPDATE_AFTER | 3              | 2026-06-06T14:42:56.449 | Closed     | BROOKLYN | Sewer
CMP015       | UPDATE_AFTER | 4              | 2026-06-06T14:43:02.979 | Closed     | QUEENS   | ELEVATOR
```

`change_version` increases monotonically to ensure chronological integrity of the audit log. This `INSERT INTO ... SELECT FROM stream` statement can be created as a periodic task in Studio (hourly is recommended) for continuous complaint ticket status change tracking.

> 💡 **Tip**: The Stream offset advances only after a DML statement (`INSERT INTO ... SELECT FROM stream`) executes. A pure `SELECT` preview does not consume the offset — you can safely preview changes multiple times without affecting production consumption.

---

## DWD (Detail Data Layer): Cross-Department Event Standardization

The DWD layer unifies raw events from different departments into city-topic events, resolving inconsistencies in field naming and status code meanings across source tables.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_smart_city.doc_dwd_city_events
AS
SELECT
    complaint_id                                          AS event_id,
    'COMPLAINT'                                           AS event_category,
    complaint_type                                        AS event_type,
    agency                                                AS dept_code,
    agency_name                                           AS dept_name,
    borough,
    incident_zip                                          AS zip_code,
    latitude,
    longitude,
    created_date                                          AS event_time,
    CASE
        WHEN status = 'Closed' THEN 'RESOLVED'
        WHEN status = 'Open'   THEN 'OPEN'
        ELSE 'IN_PROGRESS'
    END                                                   AS event_status,
    DATEDIFF(CAST(closed_date AS DATE), CAST(created_date AS DATE)) AS resolution_days,
    CONCAT(borough, '-', incident_zip)                    AS geo_key
FROM best_practice_smart_city.doc_ods_311_complaints
WHERE created_date IS NOT NULL

UNION ALL

SELECT
    accident_id                                           AS event_id,
    'TRAFFIC_ACCIDENT'                                    AS event_category,
    contributing_factor_1                                 AS event_type,
    'DOT'                                                 AS dept_code,
    'Department of Transportation'                        AS dept_name,
    borough,
    zip_code,
    latitude,
    longitude,
    CAST(crash_date AS TIMESTAMP)                         AS event_time,
    'RESOLVED'                                            AS event_status,
    0                                                     AS resolution_days,
    CONCAT(borough, '-', zip_code)                        AS geo_key
FROM best_practice_smart_city.doc_ods_traffic_accidents
WHERE crash_date IS NOT NULL;
```

Trigger the initial manual refresh and verify:

```sql
REFRESH DYNAMIC TABLE best_practice_smart_city.doc_dwd_city_events;

SELECT event_category, COUNT(*) AS cnt
FROM best_practice_smart_city.doc_dwd_city_events
GROUP BY event_category
ORDER BY cnt DESC;
```

```
event_category   | cnt
-----------------+----
COMPLAINT        | 20
TRAFFIC_ACCIDENT | 15
```

The DWD layer merged 311 complaints (20 rows) and traffic accidents (15 rows) into standardized fields such as `event_id`, `event_category`, and `geo_key`. Downstream DWS/ADS layers only need to query this single Dynamic Table, without dealing with each department's original field differences.

---

## DWS (Summary Data Layer): Daily Summary by Street / Borough

The DWS layer aggregates at `borough` × date × event category granularity for borough-level managers to view daily event volumes and processing efficiency.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_smart_city.doc_dws_borough_daily
AS
SELECT
    borough,
    DATE_TRUNC('day', event_time)            AS stat_date,
    event_category,
    COUNT(*)                                  AS event_count,
    SUM(CASE WHEN event_status = 'RESOLVED' THEN 1 ELSE 0 END)  AS resolved_count,
    SUM(CASE WHEN event_status = 'OPEN'     THEN 1 ELSE 0 END)  AS open_count,
    ROUND(AVG(CASE WHEN resolution_days IS NOT NULL
                    AND resolution_days >= 0 THEN resolution_days END), 2) AS avg_resolution_days
FROM best_practice_smart_city.doc_dwd_city_events
WHERE event_time IS NOT NULL
GROUP BY borough, DATE_TRUNC('day', event_time), event_category;
```

```sql
REFRESH DYNAMIC TABLE best_practice_smart_city.doc_dws_borough_daily;

SELECT borough, stat_date, event_category, event_count, resolved_count, avg_resolution_days
FROM best_practice_smart_city.doc_dws_borough_daily
ORDER BY stat_date, borough, event_category
LIMIT 10;
```

```
borough       | stat_date           | event_category  | event_count | resolved_count | avg_resolution_days
--------------+---------------------+-----------------+-------------+----------------+--------------------
BROOKLYN      | 2026-01-03T00:00:00 | COMPLAINT       | 1           | 0              | null
BROOKLYN      | 2026-01-03T00:00:00 | TRAFFIC_ACCIDENT| 1           | 1              | 0
MANHATTAN     | 2026-01-03T00:00:00 | COMPLAINT       | 2           | 2              | 1.5
MANHATTAN     | 2026-01-03T00:00:00 | TRAFFIC_ACCIDENT| 1           | 1              | 0
BRONX         | 2026-01-04T00:00:00 | COMPLAINT       | 1           | 1              | 2
BRONX         | 2026-01-04T00:00:00 | TRAFFIC_ACCIDENT| 1           | 1              | 0
QUEENS        | 2026-01-04T00:00:00 | TRAFFIC_ACCIDENT| 1           | 1              | 0
STATEN ISLAND | 2026-01-04T00:00:00 | COMPLAINT       | 1           | 0              | null
BROOKLYN      | 2026-01-05T00:00:00 | COMPLAINT       | 1           | 1              | 1
MANHATTAN     | 2026-01-05T00:00:00 | TRAFFIC_ACCIDENT| 1           | 1              | 0
```

`avg_resolution_days` being null means complaints for that day were not yet closed (`closed_date` is empty). The `CASE WHEN resolution_days >= 0` filters out negative values (data anomalies) and nulls, avoiding pulling down the average.

Borough complaint processing summary (aggregated across days):

```sql
SELECT
    borough,
    event_category,
    SUM(event_count)                                      AS total_events,
    ROUND(100.0 * SUM(resolved_count)
          / NULLIF(SUM(event_count), 0), 1)               AS resolution_rate_pct,
    ROUND(AVG(avg_resolution_days), 2)                    AS avg_days_to_resolve
FROM best_practice_smart_city.doc_dws_borough_daily
GROUP BY borough, event_category
ORDER BY total_events DESC;
```

```
borough       | event_category  | total_events | resolution_rate_pct | avg_days_to_resolve
--------------+-----------------+--------------+---------------------+--------------------
MANHATTAN     | COMPLAINT       | 6            | 66.7                | 1.5
BROOKLYN      | COMPLAINT       | 4            | 50.0                | 1.5
BRONX         | COMPLAINT       | 4            | 100.0               | 2
QUEENS        | COMPLAINT       | 4            | 75.0                | 2
MANHATTAN     | TRAFFIC_ACCIDENT| 4            | 100.0               | 0
BROOKLYN      | TRAFFIC_ACCIDENT| 3            | 100.0               | 0
BRONX         | TRAFFIC_ACCIDENT| 3            | 100.0               | 0
QUEENS        | TRAFFIC_ACCIDENT| 3            | 100.0               | 0
STATEN ISLAND | COMPLAINT       | 2            | 50.0                | 1
STATEN ISLAND | TRAFFIC_ACCIDENT| 2            | 100.0               | 0
```

**Result interpretation**: BRONX has the highest complaint closure rate (100%) but an average processing time of 2 days — higher than MANHATTAN's 1.5 days. This means the Bronx resolves all complaints but responds more slowly. BROOKLYN and STATEN ISLAND have only 50% closure rates, indicating a backlog that needs attention. Traffic accident events all have 100% closure rates because they are already processed when recorded.

---

## ADS (Application Data Layer): City Operations Index and KPI Dashboard

The ADS layer aggregates multiple event types to compute a comprehensive city operations score for direct consumption by BI tools and management dashboards.

### Create Tables

City operations score formula: `100 - (backlog complaint ratio × penalty factor + average processing days × timeliness factor)`, range 0–100, higher is better.

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_smart_city.doc_ads_city_ops_index
AS
SELECT
    borough,
    DATE_TRUNC('day', event_time)            AS stat_date,
    COUNT(*)                                  AS total_events,
    SUM(CASE WHEN event_category = 'COMPLAINT'        THEN 1 ELSE 0 END) AS complaint_count,
    SUM(CASE WHEN event_category = 'TRAFFIC_ACCIDENT' THEN 1 ELSE 0 END) AS accident_count,
    SUM(CASE WHEN event_status = 'RESOLVED' THEN 1 ELSE 0 END)           AS resolved_count,
    ROUND(
        100.0 * SUM(CASE WHEN event_status = 'RESOLVED' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 1
    )                                         AS resolution_rate_pct,
    ROUND(
        AVG(CASE WHEN resolution_days IS NOT NULL
                  AND resolution_days >= 0 THEN resolution_days END), 2
    )                                         AS avg_resolution_days,
    -- City operations score: penalties for backlogged events and long processing times
    ROUND(
        100.0 - LEAST(100.0,
            SUM(CASE WHEN event_status = 'OPEN' THEN 1 ELSE 0 END) * 10.0
            + COALESCE(AVG(CASE WHEN resolution_days IS NOT NULL
                                 AND resolution_days >= 0 THEN resolution_days END), 0) * 5.0
        ), 1
    )                                         AS city_ops_score
FROM best_practice_smart_city.doc_dwd_city_events
WHERE event_time IS NOT NULL
GROUP BY borough, DATE_TRUNC('day', event_time);
```

```sql
REFRESH DYNAMIC TABLE best_practice_smart_city.doc_ads_city_ops_index;

SELECT borough,
       ROUND(AVG(city_ops_score), 1)  AS avg_ops_score,
       SUM(total_events)              AS total_events,
       SUM(complaint_count)           AS complaints,
       SUM(accident_count)            AS accidents,
       ROUND(AVG(resolution_rate_pct), 1) AS resolution_rate_pct
FROM best_practice_smart_city.doc_ads_city_ops_index
GROUP BY borough
ORDER BY avg_ops_score DESC;
```

```
borough       | avg_ops_score | total_events | complaints | accidents | resolution_rate_pct
--------------+---------------+--------------+------------+-----------+--------------------
QUEENS        | 95.0          | 7            | 4          | 3         | 90.0
BRONX         | 93.8          | 7            | 4          | 3         | 100.0
BROOKLYN      | 79.2          | 7            | 4          | 3         | 75.0
MANHATTAN     | 78.8          | 10           | 6          | 4         | 75.0
STATEN ISLAND | 73.8          | 4            | 2          | 2         | 75.0
```

**Result interpretation**:

- **QUEENS (95)** and **BRONX (93.8)** have the best city operations status. BRONX's 100% closure rate is the main driver of its high score.
- **MANHATTAN (78.8)** has the highest event volume (10 records) but 2 backlogged complaints (not closed), which pulls down its score. MANHATTAN's high absolute event volume places the most pressure on overall city operations management.
- **STATEN ISLAND (73.8)** has the smallest event volume (4 records) but a 50% backlog rate — still needs close follow-up.

Department complaint processing efficiency comparison (cross-department analysis from different dimensions):

```sql
SELECT
    agency_name,
    COUNT(*)                                                           AS total_complaints,
    SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END)                AS resolved,
    SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS pending,
    ROUND(100.0 * SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                               AS resolution_rate_pct
FROM best_practice_smart_city.doc_ods_311_complaints
GROUP BY agency_name
ORDER BY total_complaints DESC;
```

```
agency_name                                       | total_complaints | resolved | pending | resolution_rate_pct
--------------------------------------------------+-----------------+----------+---------+--------------------
New York City Police Department                   | 4               | 3        | 1       | 75.0
Department of Transportation                      | 4               | 3        | 1       | 75.0
Department of Sanitation New York                 | 4               | 4        | 0       | 100.0
Department of Housing Preservation and Development| 4               | 4        | 0       | 100.0
Department of Environmental Protection            | 4               | 2        | 2       | 50.0
```

The Environmental Protection department (DEP) has only a 50% closure rate, with 2 of its 4 complaints still backlogged (water quality and noise complaints typically have longer processing cycles) — the department most in need of attention right now.

---

## Studio Periodic Refresh Task Configuration

Dynamic Table scheduling is managed by creating tasks in Studio, which lets you configure monitoring alerts and data quality rules on the same task.

The three Dynamic Tables each have refresh tasks based on their dependency levels:

1. In Studio **Development → Tasks**, navigate to path `best_practices/smart_city/`
2. Create a "Refresh Dynamic Table" task for each Dynamic Table:

| Task Name | Target Table | Schedule | Dependency |
|---|---|---|---|
| `refresh_dwd_city_events` | `doc_dwd_city_events` | Daily 02:00 | None (reads ODS directly) |
| `refresh_dws_borough_daily` | `doc_dws_borough_daily` | Daily 03:00 | After `refresh_dwd_city_events` completes |
| `refresh_ads_city_ops_index` | `doc_ads_city_ops_index` | Daily 04:00 | After `refresh_dws_borough_daily` completes |

3. Attach data quality rules to the `refresh_ads_city_ops_index` task: row count > 0, `avg_ops_score` between 0–100

On the same task page you can also schedule the Table Stream consumption task (`INSERT INTO doc_dwd_complaint_audit_log SELECT FROM stream`) — running hourly is recommended to keep the audit log near real-time.

> ⚠️ **Note**: Dynamic Table `CREATE` DDL does not include the `REFRESH INTERVAL` parameter. Scheduling is entirely managed by Studio Tasks, which lets you configure monitoring alerts, data quality checks, and task dependencies in one place without modifying DDL.

---

## RBAC: Multi-Department Data Isolation

Government data platforms typically require strict data isolation: department analysts can only see their own department's ODS data; city operations management can see DWS/ADS summaries; platform administrators have full-layer access.

### Create Roles

```sql
-- Read-only access to ADS layer public indexes (for departments to view city-wide operations status)
CREATE ROLE IF NOT EXISTS smart_city_viewer;

-- A specific department's dedicated analyst (NYPD analyst in this example)
CREATE ROLE IF NOT EXISTS dept_nypd_analyst;

-- City operations platform administrator
CREATE ROLE IF NOT EXISTS city_ops_admin;
```

### Grant Access by Layer

```sql
-- smart_city_viewer: read-only on ADS and DWS summary layers (all tables)
GRANT SELECT ON ALL TABLES IN SCHEMA best_practice_smart_city TO ROLE smart_city_viewer;

-- city_ops_admin: full-layer access
GRANT SELECT ON ALL TABLES IN SCHEMA best_practice_smart_city TO ROLE city_ops_admin;
```

View role permissions:

```sql
SHOW GRANTS TO ROLE smart_city_viewer;
```

```
granted_type       | privilege    | granted_on | object_name                           | grantee_name
-------------------+--------------+------------+---------------------------------------+------------------
OBJECT_HIERARCHY   | SELECT TABLE | TABLE      | quick_start.best_practice_smart_city.* | smart_city_viewer
PRIVILEGE          | READ METADATA| SCHEMA     | quick_start.best_practice_smart_city   | smart_city_viewer
```

The `OBJECT_HIERARCHY` type authorization automatically covers all existing and future tables under the schema, so there is no need to re-grant permissions each time a new table is created.

### Revoke Permissions

```sql
-- Execute when an employee leaves or permissions change
REVOKE SELECT ON ALL TABLES IN SCHEMA best_practice_smart_city FROM ROLE dept_nypd_analyst;
```

> 💡 **Tip**: Row-level permissions (department analysts can only see their own department's ODS data) are configured through the Studio **Data Security → Row-Level Permissions** UI — there is no corresponding SQL DDL. Rules support filtering by the `agency` field and automatically apply to all queries for that role after configuration.

---

## Column Masking: PII Field Dynamic De-Identification

311 complaint tickets and health inspection data contain geographic coordinates (latitude/longitude), and some scenarios also include complainant names and contact information as PII (Personally Identifiable Information). Column Masking can bind a de-identification function at the column level to automatically return masked values for non-privileged users.

> ⚠️ **Note**: Column Masking is generally available. Follow this process to bind a de-identification policy:

Step 1: Create a masking function (coordinate precision reduction example):

```sql
CREATE OR REPLACE FUNCTION best_practice_smart_city.mask_geo_coord(coord DOUBLE)
RETURNS DOUBLE
AS CASE
    WHEN CURRENT_USER() IN ('privileged_user') THEN coord  -- replace with actual authorized usernames
    ELSE ROUND(coord, 1)   -- non-privileged users see precision reduced to 1 decimal place (about 11km range)
END;
```

Replace `'privileged_user'` with the actual usernames that need to see plaintext data. Column Masking matches the current connection's username via `current_user()`; all authorized usernames must be explicitly listed in the `IN()` list.

Step 2: Bind the masking function to the sensitive columns:

```sql
ALTER TABLE best_practice_smart_city.doc_ods_311_complaints
CHANGE COLUMN latitude
SET MASK best_practice_smart_city.mask_geo_coord;

ALTER TABLE best_practice_smart_city.doc_ods_311_complaints
CHANGE COLUMN longitude
SET MASK best_practice_smart_city.mask_geo_coord;
```

After binding, regular analysts can only see reduced-precision coordinates (e.g., `40.7` instead of `40.7484`) while admin accounts see the original precision. The masking effect is also transparently applied to Dynamic Tables (DWD/DWS/ADS layers) — downstream tables store the masked values.

> 💡 **Tip**: The DDL syntax above (`ALTER TABLE ... CHANGE COLUMN ... SET MASK`) can be executed directly; the masking effect takes immediate effect on all queries.

---

## Data Warehouse Object Summary

After the full build, objects in the `best_practice_smart_city` schema:

```sql
SHOW TABLES IN best_practice_smart_city;
```

```
schema_name               | table_name                       | is_dynamic
--------------------------+----------------------------------+-----------
best_practice_smart_city  | doc_ads_city_ops_index           | true
best_practice_smart_city  | doc_dim_district                 | false
best_practice_smart_city  | doc_dwd_city_events              | true
best_practice_smart_city  | doc_dwd_complaint_audit_log      | false
best_practice_smart_city  | doc_dws_borough_daily            | true
best_practice_smart_city  | doc_ods_311_complaints           | false
best_practice_smart_city  | doc_ods_health_inspections       | false
best_practice_smart_city  | doc_ods_traffic_accidents        | false
```

Data warehouse layer structure:

```
CSV files submitted by departments (OSS / COS / S3)
    │
    ▼  COPY INTO + Volume (batch import)
doc_ods_311_complaints       doc_ods_traffic_accidents     doc_ods_health_inspections
(citizen hotline)             (traffic accidents)           (health inspections)
    │                               │                              │
    ├── Table Stream ──────────────────────────────────────────────┤
    │   doc_stream_complaint_changes                               │
    │   (STANDARD mode: UPDATE_BEFORE / UPDATE_AFTER)             │
    │   → INSERT INTO doc_dwd_complaint_audit_log (Studio hourly) │
    │                                                              │
    └──────────────────────────────┬───────────────────────────────┘
                                   ▼  REFRESH daily 02:00 (Studio Task)
                         doc_dwd_city_events (Dynamic Table)
                         UNION ALL standardization · event_category · geo_key
                                   │
                                   ▼  REFRESH daily 03:00 (Studio Task)
                         doc_dws_borough_daily (Dynamic Table)
                         borough × day × category · avg_resolution_days
                                   │
                                   ▼  REFRESH daily 04:00 (Studio Task)
                         doc_ads_city_ops_index (Dynamic Table)
                         city_ops_score · resolution_rate_pct

External Schema (Hive data lake)
    └── Direct query without migration; can cross-source JOIN with ODS tables
```

Three roles were also created (`smart_city_viewer`, `dept_nypd_analyst`, `city_ops_admin`) for multi-department data isolation access control.

---

## Notes

- **COPY INTO is safe for repeated execution**: COPY INTO automatically records loaded file metadata; the same file will not be re-imported. However, if file content changes while the filename stays the same (overwrite), the system will not re-load it — use date-based directory naming conventions (e.g., separate directories by date) for Volume files.

- **Dynamic Table does not set `REFRESH INTERVAL`**: None of the Dynamic Table DDL in this guide includes `REFRESH INTERVAL`. Scheduling is entirely managed by Studio Tasks, which lets you configure monitoring alerts, data quality checks, and task dependencies in one place without modifying DDL.

- **Table Stream offset advance mechanism**: The Stream offset advances only after a DML statement (`INSERT INTO ... SELECT FROM stream`) executes. A pure `SELECT` query does not consume the offset and will not drop changes. Once the offset advances it cannot be rolled back — ensure DML statements are idempotent.

- **External Schema is read-only**: After mounting the Hive data lake, you can only read; write operations still need to be performed in the Singdata schema. External Schema cannot be used as a target table for Dynamic Tables, only as an upstream data source.

- **RBAC row-level permissions have no DDL**: The row-level filter rules that restrict department analysts to only seeing their own department's data are configured through the Studio **Data Security → Row-Level Permissions** UI — there is no corresponding SQL DDL. Do not write statements like `CREATE ROW ACCESS POLICY` in code (this syntax does not exist).

- **Column Masking**: The masking effect is transparently applied to all downstream queries (including Dynamic Table SELECTs); DWD/DWS/ADS layers also store the masked values. If you need high-precision coordinates for spatial analysis, query the ODS raw table directly with a privileged admin account.

---

## Related Documentation

- [COPY INTO Data Import](../copy-into.md) — COPY INTO full parameter reference and file format support
- [Create External Schema](../create-external-schema.md) — Hive / JDBC external data source connections
- [Create Dynamic Table](../create-dynamic-table.md) — syntax reference and incremental refresh mechanism
- [Table Stream User Guide](../SQL_Table_Stream_Guide.md) — Stream creation, consumption, and offset management
- [Role and Permission Management](../role-privilege-manage.md) — RBAC full GRANT / REVOKE syntax
- [Dynamic Data Masking](../dynamic-mask.md) — Column Masking policy creation and binding
- [Medallion Architecture: Pure SQL Dynamic Table Approach](../lakehouse-medallion-sql-dt-guide.md) — large-scale three-layer data warehouse reference

> ⚠️ **Note (pending manual verification)**: Column Masking currently matches by username via `current_user()`, and all usernames authorized to view plaintext must be added individually to the `IN()` list in the masking function. If your Lakehouse version supports role-based dynamic matching (e.g., `HAS_ROLE('role_name')`), you can use roles instead of a username list for easier maintenance. Contact Singdata technical support to confirm whether your version supports this function.