# Build a Healthcare Operations Data Warehouse

Integrate data from hospital information systems (HIS), electronic medical records (EMR), and laboratory systems to build a healthcare operations data warehouse that outputs department performance metrics and a hospital-level KPI dashboard. This guide uses California hospital Q1 2025 admission data to walk through the complete **MySQL offline sync → ODS → DWD → DWS → ADS** pipeline, and covers three key capabilities: Column Masking, RBAC access tiering, and Time Travel compliance auditing.

![](/.topwrite/assets/anim-17-healthcare-platform.svg)

---

## Overview

Core challenges in a healthcare data warehouse: patient privacy protection, multi-source system integration, automated operational metric calculation, and historical data traceability for insurance reconciliation.

| Challenge | Singdata Solution |
|---|---|
| Daily full or incremental sync of HIS/EMR data | MySQL multi-table offline sync (full-database mirror mode), auto-scheduled |
| Import of HL7/JSON format lab report files | COPY INTO + Volume, supports JSON batch loading |
| ODS → DWD → DWS → ADS automatic incremental computation | Dynamic Table with declarative SQL; the system automatically maintains refresh dependency chains |
| De-identification of PII fields such as patient ID and diagnosis | Column Masking bound to columns, dynamically controlled by role |
| Access tiering for clinicians, management, and BI analysts | RBAC custom roles with fine-grained schema/table-level authorization |
| Historical version retrieval for insurance reconciliation and compliance audits | Time Travel — `DESC HISTORY` + `TIMESTAMP AS OF` queries any historical version |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create ODS layer raw tables and dimension tables | Regular tables, used as upstream source for Dynamic Tables |
| `CREATE DYNAMIC TABLE` | Create DWD / DWS / ADS layer incremental computation tables | Declarative SQL; the system handles incremental refresh |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |
| `CREATE FUNCTION` | Create a Column Masking policy function | SQL UDF — dynamically masks patient PII fields based on role |
| `ALTER TABLE ... CHANGE COLUMN ... SET MASK` | Bind the masking function to a column | Transparent to the bound column; executed dynamically at read time |
| `CREATE ROLE` | Create custom RBAC roles | Distinguishes clinical, management, and BI user permission levels |
| `GRANT` | Grant roles data access | Schema-level or table-level authorization |
| `DESC HISTORY` | View the table's historical version list | Returns timestamp, operation type, and row change count per version |
| `SELECT ... TIMESTAMP AS OF` | Query historical data at a specific point in time | Insurance reconciliation, audit, and data recovery scenarios |

---

## Prerequisites

All examples in this guide run under the `best_practice_healthcare_dw` schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_healthcare_dw;
```

---

## ODS (Raw Data Layer): Loading Raw Business Data

The ODS layer stores raw data synced from HIS, EMR, and laboratory systems without any business transformation, while Column Masking is configured on patient privacy fields.

### Create Tables

Hospital dimension table (static reference data):

```sql
CREATE TABLE IF NOT EXISTS best_practice_healthcare_dw.doc_hospital_dim (
    hospital_id     STRING,
    hospital_name   STRING,
    county          STRING,
    city            STRING,
    hospital_type   STRING,
    bed_count       INT,
    is_teaching     BOOLEAN
);
```

Admission record master table (HIS offline sync target table):

```sql
CREATE TABLE IF NOT EXISTS best_practice_healthcare_dw.doc_ods_admissions (
    admission_id              STRING,
    hospital_id               STRING,
    patient_id                STRING,
    age                       INT,
    sex                       STRING,
    race                      STRING,
    county_of_residence       STRING,
    admission_date            DATE,
    discharge_date            DATE,
    los_days                  INT,
    admission_type            STRING,
    admission_source          STRING,
    discharge_disposition     STRING,
    principal_diagnosis_code  STRING,
    principal_diagnosis_desc  STRING,
    major_diagnostic_category STRING,
    department                STRING,
    payer_type                STRING,
    total_charges             DECIMAL(12,2),
    drg_code                  STRING,
    drg_description           STRING,
    load_time                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

Lab results table (LIS system JSON file COPY INTO target table):

```sql
CREATE TABLE IF NOT EXISTS best_practice_healthcare_dw.doc_ods_lab_results (
    lab_id             STRING,
    admission_id       STRING,
    patient_id         STRING,
    hospital_id        STRING,
    test_name          STRING,
    test_code          STRING,
    result_value       STRING,
    reference_range    STRING,
    abnormal_flag      STRING,
    collection_time    TIMESTAMP,
    result_time        TIMESTAMP,
    ordering_physician STRING,
    department         STRING,
    load_time          TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### MySQL Multi-Table Offline Sync Configuration

HIS systems typically run on MySQL and contain multiple business tables such as admissions, billing, and procedure records. In Singdata Studio, use a [multi-table offline sync task](../multitable_batch_sync.md) for daily full + incremental sync:

- Sync mode: **full-database mirror (whole-database sync)** — all business tables in the HIS database are automatically mapped to the `best_practice_healthcare_dw` schema
- Schedule: daily incremental sync at 02:00; first run performs a full sync
- Studio task path: `best_practices/healthcare_dw/`

> 💡 **Tip**: Multi-table offline sync tasks support field mapping and type conversion. You can map `DATETIME` fields in HIS to the Lakehouse `TIMESTAMP` type in the task configuration.

### COPY INTO to Import HL7/JSON Lab Reports

Laboratory systems (LIS) typically output JSON or HL7 format lab report files stored in object storage (OSS/S3/COS), which are loaded periodically via COPY INTO + Volume. Create a storage connection and external volume first, then run COPY INTO:

```sql
-- Step 1: Create a Storage Connection pointing to object storage
-- Alibaba Cloud OSS example; replace TYPE, ENDPOINT, and credentials for AWS S3 / Tencent COS.
CREATE STORAGE CONNECTION IF NOT EXISTS lab_reports_oss_conn
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_ID = '<your_access_key_id>'
    ACCESS_KEY = '<your_access_key_secret>';

-- Step 2: Mount the LIS lab report directory as an External Volume
CREATE EXTERNAL VOLUME IF NOT EXISTS best_practice_healthcare_dw.lab_reports_volume
    LOCATION 'oss://<your-bucket>/lis/lab-reports/'
    USING CONNECTION lab_reports_oss_conn
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

After mounting, bulk-import JSON lab reports from `lab_reports_volume`:

```sql
COPY INTO best_practice_healthcare_dw.doc_ods_lab_results
FROM VOLUME best_practice_healthcare_dw.lab_reports_volume
USING json
ON_ERROR = 'CONTINUE';
```

> ⚠️ **Note**: `ON_ERROR = 'CONTINUE'` skips malformed files and continues loading. After loading, query `COPY_HISTORY` to check whether any files were skipped.

---

## ODS (Raw Data Layer): Column Masking for Patient PII

Patient IDs and diagnostic information in healthcare data are protected health information (PHI), and must be dynamically masked based on the accessor's role. Singdata uses Column Masking to bind masking policies at the column level, transparently hiding sensitive fields from non-privileged users.

### Create Masking Policy Functions

Patient ID masking: users without the `workspace_admin` role see only the first and last character with `*` in between.

```sql
CREATE OR REPLACE FUNCTION best_practice_healthcare_dw.mask_patient_id(pid STRING)
RETURNS STRING
AS
CASE
    WHEN array_contains(current_roles(), 'workspace_admin') THEN pid
    ELSE CONCAT(SUBSTR(pid, 1, 1), REPEAT('*', LENGTH(pid) - 2), SUBSTR(pid, LENGTH(pid), 1))
END;
```

Diagnosis masking: only `workspace_admin` and `workspace_dev` roles can see the full diagnosis; all other roles see `RESTRICTED`.

```sql
CREATE OR REPLACE FUNCTION best_practice_healthcare_dw.mask_diagnosis(diag STRING)
RETURNS STRING
AS
CASE
    WHEN array_contains(current_roles(), 'workspace_admin')
      OR array_contains(current_roles(), 'workspace_dev') THEN diag
    ELSE 'RESTRICTED'
END;
```

### Bind Masking Policies to Columns

```sql
-- Bind patient ID masking
ALTER TABLE best_practice_healthcare_dw.doc_ods_admissions
CHANGE COLUMN patient_id
SET MASK best_practice_healthcare_dw.mask_patient_id;

-- Bind diagnosis masking
ALTER TABLE best_practice_healthcare_dw.doc_ods_admissions
CHANGE COLUMN principal_diagnosis_desc
SET MASK best_practice_healthcare_dw.mask_diagnosis;
```

After binding, `workspace_admin` query result (full data):

```
admission_id | patient_id | principal_diagnosis_code | principal_diagnosis_desc     | payer_type
-------------|------------|--------------------------|------------------------------|------------
ADM001       | P10001     | I21.9                    | Acute myocardial infarction  | Medicare
ADM002       | P10002     | K92.1                    | Melena                       | Commercial
ADM003       | P10003     | J18.9                    | Pneumonia unspecified        | Medicare
```

A regular BI analyst querying the same table after masking takes effect:

```
admission_id | patient_id | principal_diagnosis_code | principal_diagnosis_desc | payer_type
-------------|------------|--------------------------|--------------------------|------------
ADM001       | P****1     | I21.9                    | RESTRICTED               | Medicare
ADM002       | P****2     | K92.1                    | RESTRICTED               | Commercial
ADM003       | P****3     | J18.9                    | RESTRICTED               | Medicare
```

> ⚠️ **Note**: Column Masking is a preview feature. Contact technical support to enable it for production use. Once a masking function is bound, it takes effect on all query paths, including indirect reads through views and Dynamic Tables.

---

## DWD (Detail Data Layer): Patient Visit Event Wide Table

The DWD layer uses Dynamic Tables to join ODS admission records with the hospital dimension table, and derives fields such as age group and discharge category to form an analysis-friendly patient visit event wide table.

### Create Tables

```sql
CREATE DYNAMIC TABLE best_practice_healthcare_dw.doc_dwd_patient_visits
REFRESH INTERVAL 60 MINUTE VCLUSTER DEFAULT
AS
SELECT
    a.admission_id,
    a.hospital_id,
    h.hospital_name,
    h.county         AS hospital_county,
    h.hospital_type,
    h.is_teaching,
    a.patient_id,
    a.age,
    CASE
        WHEN a.age < 18  THEN 'Pediatric'
        WHEN a.age < 45  THEN 'Adult'
        WHEN a.age < 65  THEN 'Middle-Aged'
        ELSE 'Senior'
    END AS age_group,
    a.sex,
    a.race,
    a.county_of_residence,
    a.admission_date,
    a.discharge_date,
    a.los_days,
    a.admission_type,
    a.admission_source,
    a.discharge_disposition,
    a.principal_diagnosis_code,
    a.principal_diagnosis_desc,
    a.major_diagnostic_category,
    a.department,
    a.payer_type,
    a.total_charges,
    a.drg_code,
    a.drg_description,
    CASE
        WHEN a.discharge_disposition IN ('Home', 'Home Health') THEN 'Routine'
        WHEN a.discharge_disposition = 'SNF'                   THEN 'Extended Care'
        ELSE 'Other'
    END AS discharge_category,
    CASE WHEN a.los_days > 7 THEN 1 ELSE 0 END AS is_long_stay,
    a.load_time
FROM best_practice_healthcare_dw.doc_ods_admissions a
LEFT JOIN best_practice_healthcare_dw.doc_hospital_dim h
    ON a.hospital_id = h.hospital_id;
```

Lab event wide table, computing lab turnaround time (TAT):

```sql
CREATE DYNAMIC TABLE best_practice_healthcare_dw.doc_dwd_lab_events
REFRESH INTERVAL 60 MINUTE VCLUSTER DEFAULT
AS
SELECT
    l.lab_id,
    l.admission_id,
    l.patient_id,
    l.hospital_id,
    h.hospital_name,
    l.test_name,
    l.test_code,
    l.result_value,
    l.reference_range,
    l.abnormal_flag,
    l.collection_time,
    l.result_time,
    TIMESTAMPDIFF(MINUTE, l.collection_time, l.result_time) AS tat_minutes,
    l.ordering_physician,
    l.department
FROM best_practice_healthcare_dw.doc_ods_lab_results l
LEFT JOIN best_practice_healthcare_dw.doc_hospital_dim h
    ON l.hospital_id = h.hospital_id;
```

```sql
REFRESH DYNAMIC TABLE best_practice_healthcare_dw.doc_dwd_patient_visits;
REFRESH DYNAMIC TABLE best_practice_healthcare_dw.doc_dwd_lab_events;
```

DWD patient visit wide table query results:

```
admission_id | hospital_name              | age_group    | department    | los_days | discharge_category | is_long_stay
-------------|----------------------------|--------------|---------------|----------|--------------------|-------------
ADM001       | Cedars-Sinai Medical Center | Senior       | Cardiology    | 4        | Routine            | 0
ADM003       | UCSF Medical Center        | Senior       | Pulmonology   | 7        | Extended Care      | 0
ADM008       | Stanford Health Care       | Senior       | Neurology     | 8        | Extended Care      | 1
```

DWD lab event wide table — the TAT column reflects minutes from sample collection to result availability:

```
lab_id | hospital_name              | test_name        | abnormal_flag | tat_minutes
-------|----------------------------|------------------|---------------|------------
LAB001 | Cedars-Sinai Medical Center | Complete Blood Count | H          | 150
LAB002 | Cedars-Sinai Medical Center | Troponin I           | H          | 45
LAB007 | Huntington Hospital         | BNP                  | H          | 60
LAB011 | Cedars-Sinai Medical Center | ABG                  | H          | 30
```

Abnormal results by department (`abnormal_flag IN ('H', 'A')`):

```
department    | abnormal_results | avg_tat_min
--------------|------------------|------------
Cardiology    | 5                | 111
Neurology     | 3                | 80
Orthopedics   | 2                | 120
Pulmonology   | 1                | 120
Nephrology    | 1                | 90
```

Cardiology has the most abnormal results (5), with an average turnaround time of 111 minutes. ICU is the fastest (30 minutes).

---

## DWS (Summary Data Layer): Monthly Department Performance Aggregation

The DWS layer aggregates by month × hospital × department to produce department operational performance metrics.

### Create Tables

```sql
CREATE DYNAMIC TABLE best_practice_healthcare_dw.doc_dws_dept_monthly
REFRESH INTERVAL 60 MINUTE VCLUSTER DEFAULT
AS
SELECT
    DATE_TRUNC('month', admission_date)  AS admission_month,
    hospital_id,
    hospital_name,
    department,
    major_diagnostic_category,
    COUNT(*)                             AS total_admissions,
    COUNT(DISTINCT patient_id)           AS unique_patients,
    ROUND(AVG(los_days), 2)              AS avg_los_days,
    MAX(los_days)                        AS max_los_days,
    SUM(CASE WHEN is_long_stay = 1 THEN 1 ELSE 0 END)  AS long_stay_count,
    ROUND(SUM(CASE WHEN is_long_stay = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS long_stay_pct,
    ROUND(SUM(total_charges), 2)         AS total_charges,
    ROUND(AVG(total_charges), 2)         AS avg_charges,
    SUM(CASE WHEN admission_type = 'Emergency' THEN 1 ELSE 0 END) AS emergency_count,
    SUM(CASE WHEN payer_type = 'Medicare'   THEN 1 ELSE 0 END) AS medicare_count,
    SUM(CASE WHEN payer_type = 'Medicaid'   THEN 1 ELSE 0 END) AS medicaid_count,
    SUM(CASE WHEN payer_type = 'Commercial' THEN 1 ELSE 0 END) AS commercial_count
FROM best_practice_healthcare_dw.doc_dwd_patient_visits
GROUP BY 1, 2, 3, 4, 5;
```

```sql
REFRESH DYNAMIC TABLE best_practice_healthcare_dw.doc_dws_dept_monthly;
```

Query January department performance (sorted by total charges descending):

```sql
SELECT
    department, total_admissions, avg_los_days, long_stay_pct,
    total_charges, emergency_count, medicare_count
FROM best_practice_healthcare_dw.doc_dws_dept_monthly
WHERE admission_month = '2025-01-01'
ORDER BY total_charges DESC
LIMIT 6;
```

```
department    | total_admissions | avg_los_days | long_stay_pct | total_charges | emergency_count | medicare_count
--------------|------------------|--------------|---------------|---------------|-----------------|---------------
ICU           | 1                | 7.00         | 0.0           | 96800.00      | 1               | 1
Neurology     | 1                | 8.00         | 100.0         | 89400.00      | 1               | 1
Orthopedics   | 1                | 7.00         | 0.0           | 74500.00      | 1               | 1
Pulmonology   | 1                | 7.00         | 0.0           | 62100.00      | 1               | 1
Cardiology    | 1                | 6.00         | 0.0           | 58300.00      | 1               | 1
Gastroenterology | 1             | 6.00         | 0.0           | 52700.00      | 1               | 1
```

ICU and Neurology have the highest per-case average charges, and both departments have a 100% emergency admission rate, reflecting that high-complexity cases are concentrated in these departments.

Distribution by major diagnostic category (full quarter):

```sql
SELECT
    major_diagnostic_category,
    COUNT(*) AS admission_count,
    ROUND(AVG(los_days), 2) AS avg_los,
    ROUND(AVG(total_charges), 0) AS avg_charges
FROM best_practice_healthcare_dw.doc_dwd_patient_visits
GROUP BY major_diagnostic_category
ORDER BY admission_count DESC
LIMIT 8;
```

```
major_diagnostic_category | admission_count | avg_los | avg_charges
--------------------------|-----------------|---------|------------
Circulatory               | 8               | 5.13    | 50913
Nervous System            | 8               | 5.50    | 62638
Digestive                 | 7               | 2.71    | 28800
Kidney                    | 6               | 4.33    | 39050
Respiratory               | 6               | 6.00    | 60883
Reproductive              | 2               | 2.50    | 30600
Endocrine                 | 2               | 2.00    | 16000
ENT                       | 2               | 1.00    | 10000
```

Circulatory and nervous system diseases are tied for the highest admission volume. Nervous system diseases have the highest average hospitalization cost ($62,638), while respiratory diseases have the longest average length of stay (6 days).

Payer mix analysis:

```sql
SELECT
    payer_type,
    COUNT(*) AS admission_count,
    ROUND(AVG(los_days), 2) AS avg_los,
    ROUND(SUM(total_charges), 0) AS total_revenue,
    ROUND(AVG(total_charges), 0) AS avg_charges
FROM best_practice_healthcare_dw.doc_dwd_patient_visits
GROUP BY payer_type
ORDER BY admission_count DESC;
```

```
payer_type  | admission_count | avg_los | total_revenue | avg_charges
------------|-----------------|---------|---------------|------------
Medicare    | 25              | 6.20    | 1588600       | 63544
Commercial  | 16              | 1.63    | 302000        | 18875
Medicaid    | 9               | 2.44    | 241600        | 26844
```

Medicare patients account for 50% of total admissions, but their average length of stay (6.2 days) and average charges ($63,544) are far higher than other payers, consistent with this population's older age and higher clinical complexity.

---

## ADS (Application Data Layer): Hospital-Level KPI Executive Dashboard

The ADS layer aggregates further to hospital granularity to produce the core KPIs needed for executive dashboards.

### Create Tables

```sql
CREATE DYNAMIC TABLE best_practice_healthcare_dw.doc_ads_hospital_kpi
REFRESH INTERVAL 60 MINUTE VCLUSTER DEFAULT
AS
SELECT
    hospital_id,
    hospital_name,
    hospital_county,
    hospital_type,
    is_teaching,
    COUNT(*)                               AS total_admissions,
    COUNT(DISTINCT patient_id)             AS unique_patients,
    ROUND(AVG(los_days), 2)                AS avg_los_days,
    SUM(CASE WHEN is_long_stay = 1 THEN 1 ELSE 0 END) AS long_stay_count,
    ROUND(SUM(CASE WHEN is_long_stay = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS long_stay_rate_pct,
    ROUND(SUM(total_charges), 2)           AS total_revenue,
    ROUND(AVG(total_charges), 2)           AS avg_revenue_per_admission,
    SUM(CASE WHEN admission_type = 'Emergency' THEN 1 ELSE 0 END) AS emergency_admissions,
    ROUND(SUM(CASE WHEN admission_type = 'Emergency' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS emergency_rate_pct,
    SUM(CASE WHEN discharge_category = 'Extended Care' THEN 1 ELSE 0 END) AS snf_discharges,
    SUM(CASE WHEN payer_type = 'Medicare'   THEN 1 ELSE 0 END) AS medicare_cases,
    SUM(CASE WHEN payer_type = 'Medicaid'   THEN 1 ELSE 0 END) AS medicaid_cases,
    SUM(CASE WHEN payer_type = 'Commercial' THEN 1 ELSE 0 END) AS commercial_cases,
    COUNT(DISTINCT department)             AS active_departments
FROM best_practice_healthcare_dw.doc_dwd_patient_visits
GROUP BY hospital_id, hospital_name, hospital_county, hospital_type, is_teaching;
```

```sql
REFRESH DYNAMIC TABLE best_practice_healthcare_dw.doc_ads_hospital_kpi;
```

Hospital-level KPI query results (sorted by total revenue descending):

```sql
SELECT
    hospital_name, total_admissions, avg_los_days, long_stay_rate_pct,
    total_revenue, avg_revenue_per_admission, emergency_rate_pct,
    medicare_cases, commercial_cases, medicaid_cases
FROM best_practice_healthcare_dw.doc_ads_hospital_kpi
ORDER BY total_revenue DESC;
```

```
hospital_name                | total_admissions | avg_los_days | long_stay_rate_pct | total_revenue | avg_revenue | emergency_rate_pct
-----------------------------|------------------|--------------|-------------------|---------------|-------------|-------------------
Cedars-Sinai Medical Center  | 8                | 4.88         | 0.0               | 447100.00     | 55887.50    | 75.0
UCSF Medical Center          | 7                | 4.29         | 0.0               | 322200.00     | 46028.57    | 42.9
Stanford Health Care         | 6                | 5.17         | 16.7              | 312600.00     | 52100.00    | 66.7
Huntington Hospital          | 6                | 4.17         | 0.0               | 257200.00     | 42866.67    | 50.0
Kaiser Permanente Fontana    | 6                | 4.00         | 0.0               | 217100.00     | 36183.33    | 50.0
```

Cedars-Sinai has the highest total revenue ($447,100) and also the highest emergency admission rate (75%). Stanford Health Care has a 16.7% long-stay rate (LOS > 7 days), reflecting its higher proportion of complex cases.

Quarterly monthly trend analysis:

```sql
SELECT
    CASE EXTRACT(month FROM admission_date)
        WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
    END AS month_name,
    COUNT(*) AS total_admissions,
    ROUND(AVG(los_days), 2) AS avg_los,
    ROUND(SUM(total_charges), 0) AS total_revenue,
    SUM(CASE WHEN admission_type = 'Emergency' THEN 1 ELSE 0 END) AS emergency_count
FROM best_practice_healthcare_dw.doc_dwd_patient_visits
GROUP BY EXTRACT(month FROM admission_date),
         CASE EXTRACT(month FROM admission_date)
             WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
         END
ORDER BY EXTRACT(month FROM admission_date);
```

```
month_name | total_admissions | avg_los | total_revenue | emergency_count
-----------|------------------|---------|---------------|----------------
January    | 25               | 3.84    | 996800        | 12
February   | 15               | 4.33    | 686700        | 8
March      | 10               | 4.20    | 448700        | 6
```

January has the highest admission volume (25 cases), consistent with California's high incidence of respiratory illness and flu season in winter. February has a slightly higher average length of stay (4.33 days), indicating higher average case complexity in February.

---

## RBAC: Access Tiering Configuration

Different users in a healthcare data warehouse have significantly different data access needs and permission levels. Custom RBAC roles provide tiered control.

### Create Custom Roles

```sql
-- Clinical staff: can view patient visit events (DWD layer), but patient PII fields are controlled by Column Masking
CREATE ROLE IF NOT EXISTS healthcare_clinical_viewer
    COMMENT 'Clinical staff - view patient clinical data with PII masking';

-- Operations management: can only access department-level aggregated data (DWS/ADS layer), no patient-level record access
CREATE ROLE IF NOT EXISTS healthcare_mgmt_analyst
    COMMENT 'Management - view aggregate KPIs only, no patient-level access';

-- BI analysts: can only access the ADS layer KPI tables for reporting and dashboards
CREATE ROLE IF NOT EXISTS healthcare_bi_analyst
    COMMENT 'BI team - ADS layer only, read-only for reporting';
```

### Grant Schema Access

```sql
-- Clinical staff: grant schema metadata read access (actual table-level access is controlled separately on each table)
GRANT READ METADATA ON SCHEMA best_practice_healthcare_dw
    TO ROLE healthcare_clinical_viewer;

-- Management and BI analysts also get only metadata read access
GRANT READ METADATA ON SCHEMA best_practice_healthcare_dw
    TO ROLE healthcare_mgmt_analyst;

GRANT READ METADATA ON SCHEMA best_practice_healthcare_dw
    TO ROLE healthcare_bi_analyst;
```

### Access Tier Summary

| Role | Accessible Layers | Visible Patient PII | Typical Users |
|---|---|---|---|
| `workspace_admin` | ODS / DWD / DWS / ADS | Full data | DBA, data platform administrators |
| `healthcare_clinical_viewer` | DWD visit events | patient_id masked, diagnosis RESTRICTED | Clinicians, nurses |
| `healthcare_mgmt_analyst` | DWS / ADS layers | No patient-level fields | Department heads, operations management |
| `healthcare_bi_analyst` | ADS KPI only | No patient-level fields | BI engineers, report developers |

> ⚠️ **Note**: After granting RBAC roles, assign them to specific users with `GRANT ROLE <role_name> TO USER <username>`. Roles themselves cannot log in to the system.

---

## Time Travel: Compliance Auditing and Insurance Reconciliation

Healthcare compliance requires that data changes be traceable. Singdata Time Travel supports queries on any historical version via `DESC HISTORY` and `TIMESTAMP AS OF`, suitable for insurance reconciliation, regulatory review, and data error recovery.

### View Historical Versions

```sql
DESC HISTORY best_practice_healthcare_dw.doc_ods_admissions;
```

```
version | time                      | total_rows | operation   | user       | stats
--------|---------------------------|------------|-------------|------------|----------------------------------
5       | 2026-06-06T13:32:08.973   | 50         | ALTER       | admin_user | rows_inserted:25, rows_deleted:0
4       | 2026-06-06T13:32:04.327   | 50         | ALTER       | admin_user | rows_inserted:25, rows_deleted:0
3       | 2026-06-06T13:28:59.337   | 50         | INSERT_INTO | admin_user | rows_inserted:25, rows_deleted:0
2       | 2026-06-06T13:28:29.718   | 25         | INSERT_INTO | admin_user | rows_inserted:25, rows_deleted:0
1       | 2026-06-06T13:26:34.306   | 0          | CREATE      | admin_user | —
```

Version 2 had only 25 records (first batch of admission data). Versions 4 and 5 are ALTER operations (binding Column Masking).

### Timestamp-Based Historical Data Queries

Insurance reconciliation scenario: query the original data state at the time of submitting the reconciliation report to confirm the number of admission records at that point.

```sql
-- Query the data snapshot at version 2 (2026-06-06 13:28:29)
SELECT COUNT(*) AS row_count
FROM best_practice_healthcare_dw.doc_ods_admissions
TIMESTAMP AS OF '2026-06-06T13:28:29.718';
```

```
row_count
---------
25
```

The current table has 50 records, but `TIMESTAMP AS OF` can precisely rewind to version 2 state, confirming only 25 records existed at that time. This is suited to scenarios where an insurance audit agency requests "a data snapshot at the time of a specific claim submission".

### Data Recovery Scenario

Use Time Travel to recover data after an accidental operation:

```sql
-- Restore accidentally deleted data to a specific point in time
RESTORE TABLE best_practice_healthcare_dw.doc_ods_admissions
TO TIMESTAMP AS OF '2026-06-06T13:28:29.718';
```

> ⚠️ **Note**: `RESTORE TABLE` is an irreversible write operation that rolls the table back to the specified historical version and overwrites current data. Verify the target version's data is correct with a `TIMESTAMP AS OF` query before executing the restore. Time Travel retains 7 days of historical versions by default; versions beyond the retention window cannot be restored.

---

## Notes

- **Column Masking is a preview feature**: Contact technical support to enable it. Confirm it is enabled before production use. Once a masking policy is bound, it takes effect on all query paths (including indirect reads through Dynamic Tables).
- **Dynamic Table decoupling from upstream ODS**: The Column Masking behavior of DWD/DWS/ADS layer Dynamic Tables is determined by the ODS table's policy — there is no need to bind masking functions again on the DWD tables.
- **Principle of least privilege for RBAC roles**: Assign roles by department or function. Avoid granting high-privilege roles such as `workspace_admin` or `workspace_dev` to regular business users.
- **Time Travel retention**: Default 7 days; historical versions are cleaned up after that. For scenarios with long-term audit needs such as insurance reconciliation, archive key versions to a standalone table via periodic snapshots (CTAS).
- **Full vs. incremental strategy for HIS offline sync**: The initial sync is best run during low-traffic hours (e.g., 02:00) as a full sync. Switch to incremental mode afterward to avoid excessive compute usage from full syncs as data volume grows.

---

## Related Documentation

- [Dynamic Table](../dynamic-table.md) — Dynamic Table creation syntax and refresh mechanism
- [Column-Level Security (Dynamic Masking)](../dynamic-mask.md) — Column Masking full syntax and use cases
- [User Management](../authority-management.md) — RBAC role creation and permission granting
- [MySQL Multi-Table Offline Sync](../multitable_batch_sync.md) — full-database mirror sync configuration
- [COPY INTO](../copy-into.md) — bulk data import from Volume / object storage