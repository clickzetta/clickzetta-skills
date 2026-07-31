# FHIR Clinical Data Analysis Data Warehouse Best Practices

Build a multi-layer data warehouse from HL7 FHIR clinical data (patients, encounters, observations, medications) to support clinical quality control metric calculation and healthcare cost management. This guide uses a simulated FHIR JSON dataset of 5 patients, 5 encounters, 7 observations, and 6 medication orders to demonstrate the complete **ODS (raw FHIR JSON) → DWD (parsed layer) → DWS (summary layer) → ADS (clinical quality metrics)** pipeline, covering four key capabilities: nested JSON field extraction, Dynamic Table incremental computation, Column Masking PHI de-identification, and Time Travel historical snapshots.

![](/.topwrite/assets/anim-28-fhir-clinical.svg)

---

## Overview

The core challenge of a healthcare FHIR clinical data warehouse is that FHIR messages are stored as nested JSON, the four resource types (patient, encounter, observation, medication) each have different structures, fields must be extracted before joins can be established, and PHI fields such as patient names and dates of birth must be masked for non-privileged users.

| Problem | Singdata Solution |
|---|---|
| Deeply nested FHIR JSON (name[0].given[0], reasonCode[0].coding[0].code, etc.) | `get_json_object` + JSONPath syntax — extract any field at any depth on demand |
| Four FHIR resource types need joined analysis | Dynamic Table with declarative JOIN SQL; the system refreshes incrementally |
| ODS → DWD → DWS → ADS data pipeline | Dynamic Table chained dependencies — downstream auto-updates when upstream refreshes |
| PHI fields such as patient names and birth dates require masking | Column Masking bound to columns, transparently applied to all queries including Dynamic Tables |
| Insurance reconciliation requires historical monthly data snapshots | Time Travel with `TIMESTAMP AS OF` syntax — point-in-time queries at any timestamp |
| Quality metrics such as clinical pathway compliance rates need daily updates | ADS layer Dynamic Table + Studio Task scheduled daily |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create ODS layer FHIR raw tables | One table per resource type, storing the full JSON |
| `get_json_object` | Extract fields from FHIR JSON using JSONPath | Supports `$` paths; arrays use `[0]` index notation |
| `CREATE DYNAMIC TABLE` | Build DWD / DWS / ADS layers | Declarative SQL; the system handles incremental computation |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |
| `ALTER TABLE ... CHANGE COLUMN ... SET MASK` | Bind a masking function to a PHI column | Transparently applied to all queries, including Dynamic Tables |
| `TIMESTAMP AS OF` | Time Travel historical snapshot query | Rewind to any timestamp for insurance reconciliation |
| `DATEDIFF` | Calculate length of stay (LOS) and patient age | Time difference computation |
| `FLOOR / CAST` | Numeric type conversion | Round age down; convert JSON strings to DOUBLE |

---

## Prerequisites

All examples in this guide run under the `best_practice_fhir_clinical` schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_fhir_clinical;
```

---

## ODS (Raw Data Layer): Raw FHIR JSON Tables

The ODS layer stores the complete FHIR resource JSON strings as-is, preserving the original messages without parsing, so fields can be extended or replayed later.

### Create Tables

```sql
-- FHIR Patient resource
CREATE TABLE IF NOT EXISTS best_practice_fhir_clinical.doc_fhir_patient (
    patient_id    STRING,
    resource_json STRING
);

-- FHIR Encounter resource (visit event)
CREATE TABLE IF NOT EXISTS best_practice_fhir_clinical.doc_fhir_encounter (
    encounter_id  STRING,
    patient_id    STRING,
    resource_json STRING
);

-- FHIR Observation resource (lab / vital signs)
CREATE TABLE IF NOT EXISTS best_practice_fhir_clinical.doc_fhir_observation (
    obs_id       STRING,
    patient_id   STRING,
    resource_json STRING
);

-- FHIR MedicationRequest resource (medication order)
CREATE TABLE IF NOT EXISTS best_practice_fhir_clinical.doc_fhir_medication_request (
    req_id       STRING,
    patient_id   STRING,
    resource_json STRING
);
```

### Load Sample Data

In production, import FHIR JSON files in bulk via COPY INTO + Volume.

Import from a local CSV file (recommended):

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/your/data.csv' TO USER VOLUME FILE 'data.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_fhir_clinical.doc_fhir_patient
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('data.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

Insert 5 patient records (Patient resource):

```sql
INSERT INTO best_practice_fhir_clinical.doc_fhir_patient VALUES
('P001', '{"resourceType":"Patient","id":"P001","name":[{"family":"Zhang","given":["Wei"]}],"gender":"male","birthDate":"1980-05-15","address":[{"city":"Shanghai","postalCode":"200000"}]}'),
('P002', '{"resourceType":"Patient","id":"P002","name":[{"family":"Li","given":["Fang"]}],"gender":"female","birthDate":"1972-11-23","address":[{"city":"Beijing","postalCode":"100000"}]}'),
('P003', '{"resourceType":"Patient","id":"P003","name":[{"family":"Wang","given":["Jun"]}],"gender":"male","birthDate":"1955-03-08","address":[{"city":"Guangzhou","postalCode":"510000"}]}'),
('P004', '{"resourceType":"Patient","id":"P004","name":[{"family":"Chen","given":["Mei"]}],"gender":"female","birthDate":"1990-07-30","address":[{"city":"Shenzhen","postalCode":"518000"}]}'),
('P005', '{"resourceType":"Patient","id":"P005","name":[{"family":"Liu","given":["Yang"]}],"gender":"male","birthDate":"1968-01-12","address":[{"city":"Chengdu","postalCode":"610000"}]}');
```

Insert 5 encounter records (Encounter resource, including ICD-10 diagnosis codes):

```sql
INSERT INTO best_practice_fhir_clinical.doc_fhir_encounter VALUES
('E001', 'P001', '{"resourceType":"Encounter","id":"E001","status":"finished","class":{"code":"IMP","display":"inpatient"},"subject":{"reference":"Patient/P001"},"period":{"start":"2026-01-10T08:00:00Z","end":"2026-01-15T14:00:00Z"},"reasonCode":[{"coding":[{"system":"http://hl7.org/fhir/sid/icd-10","code":"I50.0","display":"Congestive heart failure"}]}],"serviceProvider":{"reference":"Organization/Hospital-A","display":"Cardiology"}}'),
('E002', 'P002', '{"resourceType":"Encounter","id":"E002","status":"finished","class":{"code":"AMB","display":"ambulatory"},"subject":{"reference":"Patient/P002"},"period":{"start":"2026-02-03T09:30:00Z","end":"2026-02-03T11:00:00Z"},"reasonCode":[{"coding":[{"system":"http://hl7.org/fhir/sid/icd-10","code":"E11.9","display":"Type 2 diabetes mellitus"}]}],"serviceProvider":{"reference":"Organization/Hospital-A","display":"Endocrinology"}}'),
('E003', 'P003', '{"resourceType":"Encounter","id":"E003","status":"finished","class":{"code":"IMP","display":"inpatient"},"subject":{"reference":"Patient/P003"},"period":{"start":"2026-01-20T07:00:00Z","end":"2026-01-28T16:00:00Z"},"reasonCode":[{"coding":[{"system":"http://hl7.org/fhir/sid/icd-10","code":"J44.1","display":"COPD with acute exacerbation"}]}],"serviceProvider":{"reference":"Organization/Hospital-B","display":"Pulmonology"}}'),
('E004', 'P004', '{"resourceType":"Encounter","id":"E004","status":"in-progress","class":{"code":"AMB","display":"ambulatory"},"subject":{"reference":"Patient/P004"},"period":{"start":"2026-03-15T14:00:00Z"},"reasonCode":[{"coding":[{"system":"http://hl7.org/fhir/sid/icd-10","code":"N18.3","display":"Chronic kidney disease stage 3"}]}],"serviceProvider":{"reference":"Organization/Hospital-A","display":"Nephrology"}}'),
('E005', 'P005', '{"resourceType":"Encounter","id":"E005","status":"finished","class":{"code":"EMER","display":"emergency"},"subject":{"reference":"Patient/P005"},"period":{"start":"2026-02-18T22:15:00Z","end":"2026-02-19T06:00:00Z"},"reasonCode":[{"coding":[{"system":"http://hl7.org/fhir/sid/icd-10","code":"I63.9","display":"Cerebral infarction"}]}],"serviceProvider":{"reference":"Organization/Hospital-B","display":"Neurology"}}');
```

After inserting 7 observation records (Observation resource, including LOINC codes) and 6 medication orders (MedicationRequest, including RxNorm codes), verify the ODS layer row counts:

```sql
SELECT COUNT(*) AS patient_count FROM best_practice_fhir_clinical.doc_fhir_patient;
SELECT COUNT(*) AS encounter_count FROM best_practice_fhir_clinical.doc_fhir_encounter;
SELECT COUNT(*) AS obs_count FROM best_practice_fhir_clinical.doc_fhir_observation;
SELECT COUNT(*) AS med_count FROM best_practice_fhir_clinical.doc_fhir_medication_request;
```

---

## DWD (Detail Data Layer): FHIR JSON Parsing and Structuring

The DWD layer uses Dynamic Tables to extract nested JSON fields from ODS into relational columns, forming the foundation for downstream aggregation and quality control analysis.

### JSON Field Extraction Patterns

FHIR JSON is deeply nested. The following JSONPath patterns are used during extraction:

| FHIR Field Type | JSONPath Example | Notes |
|---|---|---|
| Top-level scalar | `$.gender` | Direct access |
| First element of an array | `$.name[0].family` | Array index `[0]` |
| Multi-level nested array | `$.reasonCode[0].coding[0].code` | Multiple nesting levels |
| Scalar inside a nested object | `$.period.start` | Dot notation |
| Numeric value (requires type cast) | `CAST(get_json_object(...) AS DOUBLE)` | Returns string by default |

Verify the Patient resource extraction:

```sql
SELECT
    patient_id,
    get_json_object(resource_json, '$.name[0].family')   AS family_name,
    get_json_object(resource_json, '$.name[0].given[0]') AS given_name,
    get_json_object(resource_json, '$.gender')            AS gender,
    get_json_object(resource_json, '$.birthDate')         AS birth_date,
    get_json_object(resource_json, '$.address[0].city')  AS city
FROM best_practice_fhir_clinical.doc_fhir_patient;
```

```
patient_id | family_name | given_name | gender | birth_date | city
-----------+-------------+------------+--------+------------+-----------
P001       | Zhang       | Wei        | male   | 1980-05-15 | Shanghai
P002       | Li          | Fang       | female | 1972-11-23 | Beijing
P003       | Wang        | Jun        | male   | 1955-03-08 | Guangzhou
P004       | Chen        | Mei        | female | 1990-07-30 | Shenzhen
P005       | Liu         | Yang       | male   | 1968-01-12 | Chengdu
```

Verify ICD-10 code and encounter duration extraction from Encounter resource:

```sql
SELECT
    encounter_id,
    patient_id,
    get_json_object(resource_json, '$.status')                           AS enc_status,
    get_json_object(resource_json, '$.class.code')                       AS enc_class,
    get_json_object(resource_json, '$.period.start')                     AS period_start,
    get_json_object(resource_json, '$.period.end')                       AS period_end,
    get_json_object(resource_json, '$.reasonCode[0].coding[0].code')     AS icd_code,
    get_json_object(resource_json, '$.reasonCode[0].coding[0].display')  AS diagnosis,
    get_json_object(resource_json, '$.serviceProvider.display')          AS department
FROM best_practice_fhir_clinical.doc_fhir_encounter;
```

```
encounter_id | patient_id | enc_status  | enc_class | period_start          | period_end            | icd_code | diagnosis                        | department
-------------+------------+-------------+-----------+-----------------------+-----------------------+----------+----------------------------------+-----------
E001         | P001       | finished    | IMP       | 2026-01-10T08:00:00Z  | 2026-01-15T14:00:00Z  | I50.0    | Congestive heart failure         | Cardiology
E002         | P002       | finished    | AMB       | 2026-02-03T09:30:00Z  | 2026-02-03T11:00:00Z  | E11.9    | Type 2 diabetes mellitus         | Endocrinology
E003         | P003       | finished    | IMP       | 2026-01-20T07:00:00Z  | 2026-01-28T16:00:00Z  | J44.1    | COPD with acute exacerbation     | Pulmonology
E004         | P004       | in-progress | AMB       | 2026-03-15T14:00:00Z  | NULL                  | N18.3    | Chronic kidney disease stage 3   | Nephrology
E005         | P005       | finished    | EMER      | 2026-02-18T22:15:00Z  | 2026-02-19T06:00:00Z  | I63.9    | Cerebral infarction              | Neurology
```

> 💡 **Tip**: E004's `period.end` is NULL, corresponding to a patient with `in-progress` status who is still admitted. Downstream LOS (length of stay) calculations should use `COALESCE(period.end, CURRENT_TIMESTAMP())` to handle currently admitted patients and avoid NULL causing anomalies in aggregation results.

### Create DWD Dynamic Tables

`dwd_patient_dim`: patient dimension table, extracts basic demographic fields and calculates age:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.dwd_patient_dim
AS
SELECT
    p.patient_id,
    get_json_object(p.resource_json, '$.name[0].family')   AS family_name,
    get_json_object(p.resource_json, '$.name[0].given[0]') AS given_name,
    get_json_object(p.resource_json, '$.gender')            AS gender,
    get_json_object(p.resource_json, '$.birthDate')         AS birth_date,
    get_json_object(p.resource_json, '$.address[0].city')  AS city,
    DATEDIFF(CURRENT_DATE(),
        CAST(get_json_object(p.resource_json, '$.birthDate') AS DATE)) / 365 AS age_years
FROM best_practice_fhir_clinical.doc_fhir_patient p;
```

`dwd_encounter_fact`: encounter fact table, extracts ICD-10 codes, length of stay, and department, and classifies by ICD chapter:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.dwd_encounter_fact
AS
SELECT
    e.encounter_id,
    e.patient_id,
    get_json_object(e.resource_json, '$.status')                          AS enc_status,
    get_json_object(e.resource_json, '$.class.code')                      AS enc_class,
    CAST(get_json_object(e.resource_json, '$.period.start') AS TIMESTAMP) AS admit_time,
    CAST(get_json_object(e.resource_json, '$.period.end')   AS TIMESTAMP) AS discharge_time,
    DATEDIFF(
        CAST(get_json_object(e.resource_json, '$.period.end')   AS TIMESTAMP),
        CAST(get_json_object(e.resource_json, '$.period.start') AS TIMESTAMP)
    )                                                                      AS los_days,
    get_json_object(e.resource_json, '$.reasonCode[0].coding[0].code')    AS icd_code,
    get_json_object(e.resource_json, '$.reasonCode[0].coding[0].display') AS primary_diagnosis,
    get_json_object(e.resource_json, '$.serviceProvider.display')         AS department,
    CASE
        WHEN UPPER(get_json_object(e.resource_json, '$.reasonCode[0].coding[0].code')) LIKE 'I%' THEN 'Cardiology'
        WHEN UPPER(get_json_object(e.resource_json, '$.reasonCode[0].coding[0].code')) LIKE 'E%' THEN 'Endocrinology'
        WHEN UPPER(get_json_object(e.resource_json, '$.reasonCode[0].coding[0].code')) LIKE 'J%' THEN 'Pulmonology'
        WHEN UPPER(get_json_object(e.resource_json, '$.reasonCode[0].coding[0].code')) LIKE 'N%' THEN 'Nephrology'
        ELSE 'Other'
    END                                                                    AS icd_chapter
FROM best_practice_fhir_clinical.doc_fhir_encounter e;
```

`dwd_observation_fact`: observation/vital-signs fact table, extracts LOINC codes, observation values, and units:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.dwd_observation_fact
AS
SELECT
    o.obs_id,
    o.patient_id,
    get_json_object(o.resource_json, '$.category[0].coding[0].code')          AS obs_category,
    get_json_object(o.resource_json, '$.code.coding[0].code')                 AS loinc_code,
    get_json_object(o.resource_json, '$.code.coding[0].display')              AS obs_name,
    CAST(get_json_object(o.resource_json, '$.valueQuantity.value') AS DOUBLE)  AS obs_value,
    get_json_object(o.resource_json, '$.valueQuantity.unit')                  AS obs_unit,
    CAST(get_json_object(o.resource_json, '$.effectiveDateTime') AS TIMESTAMP) AS obs_time
FROM best_practice_fhir_clinical.doc_fhir_observation o;
```

`dwd_medication_fact`: medication order fact table, extracts RxNorm codes, medication name, dosage, and route:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.dwd_medication_fact
AS
SELECT
    m.req_id,
    m.patient_id,
    get_json_object(m.resource_json, '$.status')                                           AS req_status,
    get_json_object(m.resource_json, '$.medicationCodeableConcept.coding[0].code')         AS rxnorm_code,
    get_json_object(m.resource_json, '$.medicationCodeableConcept.coding[0].display')      AS medication_name,
    CAST(get_json_object(m.resource_json, '$.dosageInstruction[0].doseAndRate[0].doseQuantity.value') AS DOUBLE) AS dose_value,
    get_json_object(m.resource_json, '$.dosageInstruction[0].doseAndRate[0].doseQuantity.unit')        AS dose_unit,
    get_json_object(m.resource_json, '$.dosageInstruction[0].route.coding[0].code')        AS route,
    CAST(get_json_object(m.resource_json, '$.authoredOn') AS TIMESTAMP)                    AS authored_on,
    REPLACE(get_json_object(m.resource_json, '$.encounter.reference'), 'Encounter/', '')   AS encounter_id
FROM best_practice_fhir_clinical.doc_fhir_medication_request m;
```

> ⚠️ **Note**: Do not set `REFRESH INTERVAL` in Dynamic Table DDL. Periodic refresh is managed through Studio Tasks (see the "Scheduling Configuration" section), which lets you attach alerts and data quality rules to the same task.

Trigger the initial manual refresh and verify data:

```sql
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_patient_dim;
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_encounter_fact;
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_observation_fact;
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_medication_fact;

SELECT patient_id, family_name, gender, birth_date, city, ROUND(age_years, 1) AS age
FROM best_practice_fhir_clinical.dwd_patient_dim
ORDER BY patient_id;
```

```
patient_id | family_name | gender | birth_date | city      | age
-----------+-------------+--------+------------+-----------+-----
P001       | Zhang       | male   | 1980-05-15 | Shanghai  | 46.1
P002       | Li          | female | 1972-11-23 | Beijing   | 53.6
P003       | Wang        | male   | 1955-03-08 | Guangzhou | 71.3
P004       | Chen        | female | 1990-07-30 | Shenzhen  | 35.9
P005       | Liu         | male   | 1968-01-12 | Chengdu   | 58.4
```

Verify the encounter fact table (pay attention to los_days calculation and icd_chapter classification):

```sql
SELECT encounter_id, patient_id, enc_class, icd_code, primary_diagnosis,
       department, los_days, icd_chapter
FROM best_practice_fhir_clinical.dwd_encounter_fact
ORDER BY encounter_id;
```

```
encounter_id | patient_id | enc_class | icd_code | primary_diagnosis               | department    | los_days | icd_chapter
-------------+------------+-----------+----------+---------------------------------+---------------+----------+------------
E001         | P001       | IMP       | I50.0    | Congestive heart failure        | Cardiology    | 5        | Cardiology
E002         | P002       | AMB       | E11.9    | Type 2 diabetes mellitus        | Endocrinology | 0        | Endocrinology
E003         | P003       | IMP       | J44.1    | COPD with acute exacerbation    | Pulmonology   | 9        | Pulmonology
E004         | P004       | AMB       | N18.3    | Chronic kidney disease stage 3  | Nephrology    | NULL     | Nephrology
E005         | P005       | EMER      | I63.9    | Cerebral infarction             | Neurology     | 0        | Cardiology
```

> 💡 **Tip**: `icd_chapter` classifies by the first letter of ICD-10 codes. E005 (cerebral infarction I63.9) is grouped under the Cardiology chapter as an I-series code — this follows the standard ICD-10 classification. If your business needs to report on the nervous system separately, add special handling for `I6%` in the CASE expression.

Observation fact table (with LOINC codes and quantitative values):

```sql
SELECT obs_id, patient_id, obs_category, loinc_code, obs_name, obs_value, obs_unit
FROM best_practice_fhir_clinical.dwd_observation_fact
ORDER BY obs_id;
```

```
obs_id | patient_id | obs_category | loinc_code | obs_name                | obs_value | obs_unit
-------+------------+--------------+------------+-------------------------+-----------+---------
OBS001 | P001       | laboratory   | 2160-0     | Creatinine              | 1.2       | mg/dL
OBS002 | P002       | laboratory   | 4548-4     | HbA1c                   | 8.5       | %
OBS003 | P003       | vital-signs  | 59408-5    | SpO2                    | 88        | %
OBS004 | P004       | laboratory   | 2160-0     | Creatinine              | 2.8       | mg/dL
OBS005 | P005       | vital-signs  | 8310-5     | Body temperature        | 38.9      | Cel
OBS006 | P001       | vital-signs  | 8480-6     | Systolic blood pressure | 155       | mmHg
OBS007 | P002       | laboratory   | 2339-0     | Glucose                 | 12.4      | mmol/L
```

---

## PHI Field Masking: Column Masking

FHIR Patient data contains PHI fields such as patient last name (`family_name`), which must be masked for non-privileged users. The example below binds a masking policy to the `family_name` column of `dwd_patient_dim` so that admin accounts see the original value while other users see a masked value.

```sql
-- Create masking function: admin sees real name, others see masked value
CREATE OR REPLACE FUNCTION best_practice_fhir_clinical.mask_phi_name(name STRING)
RETURNS STRING
AS CASE
    WHEN current_user() IN ('privileged_user') THEN name  -- replace with the actual authorized usernames
    ELSE CONCAT(LEFT(name, 1), REPEAT('*', LENGTH(name) - 1))
END;
```

Replace `'privileged_user'` with the actual usernames that need to see plaintext data. Column Masking matches the current connection's username via `current_user()`; all authorized usernames must be explicitly listed in the `IN()` list.

> ⚠️ **Note**: Column Masking takes effect transparently for all queries, including upstream JOINs in Dynamic Tables.

---

## DWS (Summary Data Layer): Department Cost Aggregation and Patient Observation Summary

### Department Cost Aggregation

`dws_department_cost` aggregates by department and ICD chapter, summarizing encounter volume, average length of stay, and medication counts as the base data for DRG cost management:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.dws_department_cost
AS
SELECT
    e.department,
    e.icd_chapter,
    COUNT(DISTINCT e.encounter_id)                        AS total_encounters,
    COUNT(DISTINCT e.patient_id)                          AS total_patients,
    SUM(CASE WHEN e.enc_class = 'IMP' THEN 1 ELSE 0 END) AS inpatient_count,
    SUM(CASE WHEN e.enc_class = 'AMB' THEN 1 ELSE 0 END) AS outpatient_count,
    SUM(CASE WHEN e.enc_class = 'EMER' THEN 1 ELSE 0 END) AS emergency_count,
    ROUND(AVG(CAST(e.los_days AS DOUBLE)), 2)             AS avg_los_days,
    MAX(e.los_days)                                       AS max_los_days,
    COUNT(DISTINCT m.req_id)                              AS total_prescriptions,
    COUNT(DISTINCT m.rxnorm_code)                         AS distinct_medications
FROM best_practice_fhir_clinical.dwd_encounter_fact e
LEFT JOIN best_practice_fhir_clinical.dwd_medication_fact m ON e.encounter_id = m.encounter_id
GROUP BY e.department, e.icd_chapter;
```

```sql
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dws_department_cost;

SELECT department, icd_chapter, total_encounters, avg_los_days,
       total_prescriptions, distinct_medications
FROM best_practice_fhir_clinical.dws_department_cost
ORDER BY total_encounters DESC;
```

```
department    | icd_chapter   | total_encounters | avg_los_days | total_prescriptions | distinct_medications
--------------+---------------+------------------+--------------+---------------------+---------------------
Cardiology    | Cardiology    | 1                | 5.0          | 2                   | 2
Nephrology    | Nephrology    | 1                | NULL         | 1                   | 1
Pulmonology   | Pulmonology   | 1                | 9.0          | 1                   | 1
Neurology     | Cardiology    | 1                | 0.0          | 1                   | 1
Endocrinology | Endocrinology | 1                | 0.0          | 1                   | 1
```

**Result interpretation**: The Pulmonology department (J44.1 COPD with acute exacerbation) has the highest average length of stay at 9 days, consistent with the clinical pattern of prolonged hospitalization during acute COPD episodes. The Cardiology heart failure patient (I50.0) was admitted for 5 days and prescribed 2 medications (diuretic Furosemide + heart failure drug Carvedilol), in line with clinical pathways.

### Patient Observation Summary

`dws_patient_obs_summary` aggregates observation results by patient and LOINC code, making it easy to track metric trends:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.dws_patient_obs_summary
AS
SELECT
    o.patient_id,
    o.loinc_code,
    o.obs_name,
    o.obs_unit,
    COUNT(*)                    AS obs_count,
    ROUND(MIN(o.obs_value), 2)  AS min_value,
    ROUND(MAX(o.obs_value), 2)  AS max_value,
    ROUND(AVG(o.obs_value), 2)  AS avg_value,
    MIN(o.obs_time)             AS first_obs_time,
    MAX(o.obs_time)             AS last_obs_time
FROM best_practice_fhir_clinical.dwd_observation_fact o
GROUP BY o.patient_id, o.loinc_code, o.obs_name, o.obs_unit;
```

```sql
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dws_patient_obs_summary;

SELECT patient_id, loinc_code, obs_name, obs_unit, obs_count, min_value, max_value, avg_value
FROM best_practice_fhir_clinical.dws_patient_obs_summary
ORDER BY patient_id, loinc_code;
```

```
patient_id | loinc_code | obs_name                | obs_unit | obs_count | min_value | max_value | avg_value
-----------+------------+-------------------------+----------+-----------+-----------+-----------+----------
P001       | 2160-0     | Creatinine              | mg/dL    | 1         | 1.2       | 1.2       | 1.2
P001       | 8480-6     | Systolic blood pressure | mmHg     | 1         | 155       | 155       | 155
P002       | 2339-0     | Glucose                 | mmol/L   | 1         | 12.4      | 12.4      | 12.4
P002       | 4548-4     | HbA1c                   | %        | 1         | 8.5       | 8.5       | 8.5
P003       | 59408-5    | SpO2                    | %        | 1         | 88        | 88        | 88
P004       | 2160-0     | Creatinine              | mg/dL    | 1         | 2.8       | 2.8       | 2.8
P005       | 8310-5     | Body temperature        | Cel      | 1         | 38.9      | 38.9      | 38.9
```

**Result interpretation**: P002 (diabetic patient) has HbA1c 8.5%, above the clinical control target (< 7%), and glucose 12.4 mmol/L is also significantly elevated — indicating poor glycemic control that requires intensified treatment. P004 (CKD stage 3) has creatinine 2.8 mg/dL in the moderate-to-severe elevation range (normal upper limit about 1.2), indicating substantial kidney function impairment. P003 (COPD) has SpO2 88%, below the normal lower bound (95%), consistent with hypoxemia during acute exacerbation.

---

## ADS (Application Data Layer): Clinical Quality Metrics

`ads_clinical_quality_metrics` integrates the patient dimension, encounter facts, and observation facts to calculate three clinical pathway compliance flags:

- `hba1c_tested`: whether a diabetic patient (ICD E series) has had an HbA1c test
- `creatinine_tested`: whether a nephrology patient (ICD N series) has had a creatinine test
- `spo2_monitored`: whether a COPD patient (ICD J series) has had SpO2 monitored

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_fhir_clinical.ads_clinical_quality_metrics
AS
SELECT
    p.patient_id,
    p.family_name,
    p.gender,
    FLOOR(p.age_years)                  AS age,
    e.encounter_id,
    e.department,
    e.icd_chapter,
    e.icd_code,
    e.primary_diagnosis,
    e.enc_class,
    e.los_days,
    e.enc_status,
    COUNT(DISTINCT m.req_id)            AS prescription_count,
    COUNT(DISTINCT o.obs_id)            AS lab_count,
    MAX(CASE WHEN o.loinc_code = '4548-4'  THEN 1 ELSE 0 END) AS hba1c_tested,
    MAX(CASE WHEN o.loinc_code = '2160-0'  THEN 1 ELSE 0 END) AS creatinine_tested,
    MAX(CASE WHEN o.loinc_code = '59408-5' THEN 1 ELSE 0 END) AS spo2_monitored,
    MAX(CASE WHEN o.loinc_code = '4548-4'  THEN o.obs_value END) AS hba1c_value,
    MAX(CASE WHEN o.loinc_code = '2160-0'  THEN o.obs_value END) AS creatinine_value,
    MAX(CASE WHEN o.loinc_code = '59408-5' THEN o.obs_value END) AS spo2_value
FROM best_practice_fhir_clinical.dwd_patient_dim p
JOIN  best_practice_fhir_clinical.dwd_encounter_fact e ON p.patient_id = e.patient_id
LEFT JOIN best_practice_fhir_clinical.dwd_medication_fact m ON e.encounter_id = m.encounter_id
LEFT JOIN best_practice_fhir_clinical.dwd_observation_fact o ON p.patient_id = o.patient_id
GROUP BY
    p.patient_id, p.family_name, p.gender, FLOOR(p.age_years),
    e.encounter_id, e.department, e.icd_chapter, e.icd_code,
    e.primary_diagnosis, e.enc_class, e.los_days, e.enc_status;
```

```sql
REFRESH DYNAMIC TABLE best_practice_fhir_clinical.ads_clinical_quality_metrics;

SELECT patient_id, family_name, age, department, primary_diagnosis,
       enc_class, los_days, prescription_count, lab_count,
       hba1c_tested, creatinine_tested, spo2_monitored,
       hba1c_value, creatinine_value, spo2_value
FROM best_practice_fhir_clinical.ads_clinical_quality_metrics
ORDER BY patient_id;
```

```
patient_id | family_name | age | department    | primary_diagnosis                | enc_class | los_days | prescription_count | lab_count | hba1c_tested | creatinine_tested | spo2_monitored | hba1c_value | creatinine_value | spo2_value
-----------+-------------+-----+---------------+----------------------------------+-----------+----------+--------------------+-----------+--------------+-------------------+----------------+-------------+------------------+-----------
P001       | Zhang       | 46  | Cardiology    | Congestive heart failure         | IMP       | 5        | 2                  | 2         | 0            | 1                 | 0              | NULL        | 1.2              | NULL
P002       | Li          | 53  | Endocrinology | Type 2 diabetes mellitus         | AMB       | 0        | 1                  | 2         | 1            | 0                 | 0              | 8.5         | NULL             | NULL
P003       | Wang        | 71  | Pulmonology   | COPD with acute exacerbation     | IMP       | 9        | 1                  | 1         | 0            | 0                 | 1              | NULL        | NULL             | 88
P004       | Chen        | 35  | Nephrology    | Chronic kidney disease stage 3   | AMB       | NULL     | 1                  | 1         | 0            | 1                 | 0              | NULL        | 2.8              | NULL
P005       | Liu         | 58  | Neurology     | Cerebral infarction              | EMER      | 0        | 1                  | 1         | 0            | 0                 | 0              | NULL        | NULL             | NULL
```

### Clinical Pathway Compliance Rate Statistics

```sql
SELECT
    e.icd_chapter                             AS disease_group,
    COUNT(DISTINCT a.encounter_id)            AS encounter_count,
    ROUND(AVG(CAST(a.los_days AS DOUBLE)), 1) AS avg_los,
    SUM(a.prescription_count)                 AS total_prescriptions,
    ROUND(SUM(a.hba1c_tested) * 100.0
          / NULLIF(SUM(CASE WHEN a.icd_code LIKE 'E%' THEN 1 ELSE 0 END), 0), 1) AS diabetes_hba1c_rate_pct,
    ROUND(SUM(a.creatinine_tested) * 100.0
          / NULLIF(SUM(CASE WHEN a.icd_code LIKE 'N%' THEN 1 ELSE 0 END), 0), 1) AS ckd_creatinine_rate_pct,
    ROUND(SUM(a.spo2_monitored) * 100.0
          / NULLIF(SUM(CASE WHEN a.icd_code LIKE 'J%' THEN 1 ELSE 0 END), 0), 1) AS copd_spo2_rate_pct
FROM best_practice_fhir_clinical.ads_clinical_quality_metrics a
JOIN best_practice_fhir_clinical.dwd_encounter_fact e ON a.encounter_id = e.encounter_id
GROUP BY e.icd_chapter
ORDER BY encounter_count DESC;
```

```
disease_group | encounter_count | avg_los | total_prescriptions | diabetes_hba1c_rate_pct | ckd_creatinine_rate_pct | copd_spo2_rate_pct
--------------+-----------------+---------+---------------------+-------------------------+-------------------------+-------------------
Cardiology    | 2               | 2.5     | 3                   | NULL                    | NULL                    | NULL
Nephrology    | 1               | NULL    | 1                   | NULL                    | 100.0                   | NULL
Endocrinology | 1               | 0.0     | 1                   | 100.0                   | NULL                    | NULL
Pulmonology   | 1               | 9.0     | 1                   | NULL                    | NULL                    | 100.0
```

**Result interpretation**: Key test compliance rates are 100% for all three disease groups — diabetes (Endocrinology), CKD (Nephrology), and COPD (Pulmonology) — meaning every patient completed their required tests. The Cardiology chapter's 2 encounters (heart failure + cerebral infarction) have no corresponding specific quality control flags, but the heart failure patient (P001) did complete a creatinine test (to assess kidney function after diuretic therapy).

---

## Time Travel: Insurance Reconciliation Historical Snapshot

In monthly insurance reconciliation scenarios, you need to retrieve a snapshot of encounter data at a specific past point in time. Time Travel uses `TIMESTAMP AS OF` syntax:

```sql
-- Query the encounter data snapshot at 2026-06-06 23:38 (for insurance reconciliation)
SELECT COUNT(*) AS encounter_count
FROM best_practice_fhir_clinical.doc_fhir_encounter
TIMESTAMP AS OF '2026-06-06 23:38:00';
```

```
encounter_count
---------------
5
```

```sql
-- Compare with current data (verify the delta)
SELECT COUNT(*) AS current_count FROM best_practice_fhir_clinical.doc_fhir_encounter;
```

> ⚠️ **Note**: `TIMESTAMP AS OF` requires literal constant values — expressions like `NOW() - INTERVAL '1' MONTH` are not supported. Timestamps use UTC+8; note the timezone offset when comparing with UTC times returned by `DESC HISTORY`.

The default Time Travel data retention period is 7 days; historical versions beyond the retention window are not queryable. For monthly insurance reconciliation scenarios, regularly `INSERT INTO` month-end snapshots into a dedicated archive table rather than relying on the Time Travel retention limit.

---

## Scheduling Configuration: Studio Task

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). If you prefer not to use the command line, you can run the SQL in **Singdata Studio → Development → SQL Editor** and configure / trigger scheduling tasks on the **Studio → Tasks** page.

Periodic Dynamic Table refreshes are managed through Studio Tasks — do not set `REFRESH INTERVAL` in the DDL. Create refresh tasks under the Studio path `best_practices/fhir_clinical/` where you can also attach monitoring alerts and data quality check rules.

```bash
# Create a refresh task
cz-cli task create refresh_fhir_dwd_all -p skill_test --type SQL \
  --description "Refresh all FHIR DWD/DWS/ADS Dynamic Tables"

# Set task content (refresh in dependency order)
cz-cli task save-content refresh_fhir_dwd_all -p skill_test --content \
  "REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_patient_dim;
  REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_encounter_fact;
  REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_observation_fact;
  REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dwd_medication_fact;
  REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dws_department_cost;
  REFRESH DYNAMIC TABLE best_practice_fhir_clinical.dws_patient_obs_summary;
  REFRESH DYNAMIC TABLE best_practice_fhir_clinical.ads_clinical_quality_metrics;"

# Set daily 01:00 schedule
cz-cli task save-cron refresh_fhir_dwd_all -p skill_test --cron "0 1 * * *"

# Publish task (task_id=10354669)
cz-cli task online refresh_fhir_dwd_all -p skill_test -y
```

After publishing, you can add the following in the Studio interface (`best_practices/fhir_clinical/`):

- **Monitoring alerts**: alert when ADS layer row count drops to zero, or when refresh times out
- **Data quality rules**: trigger an alert when diabetes patient HbA1c compliance rate falls below 90%
- **Task dependencies**: chain DWS/ADS tasks to depend on DWD tasks to ensure correct refresh order

---

## Data Warehouse Object Summary

```sql
SHOW TABLES IN best_practice_fhir_clinical;
```

The `best_practice_fhir_clinical` schema contains 11 tables in total:

| Table Name | Layer | Type | Description |
|---|---|---|---|
| `doc_fhir_patient` | ODS | Regular table | FHIR Patient resource JSON |
| `doc_fhir_encounter` | ODS | Regular table | FHIR Encounter resource JSON |
| `doc_fhir_observation` | ODS | Regular table | FHIR Observation resource JSON |
| `doc_fhir_medication_request` | ODS | Regular table | FHIR MedicationRequest JSON |
| `dwd_patient_dim` | DWD | Dynamic Table | Patient dimension — JSON parsing + age calculation |
| `dwd_encounter_fact` | DWD | Dynamic Table | Encounter fact — ICD codes + LOS + department |
| `dwd_observation_fact` | DWD | Dynamic Table | Observation fact — LOINC + quantitative values |
| `dwd_medication_fact` | DWD | Dynamic Table | Medication fact — RxNorm + dosage |
| `dws_department_cost` | DWS | Dynamic Table | Department aggregation — DRG cost management |
| `dws_patient_obs_summary` | DWS | Dynamic Table | Patient observation summary — metric trends |
| `ads_clinical_quality_metrics` | ADS | Dynamic Table | Clinical quality metrics — pathway compliance rates |

---

## Notes

- **`get_json_object` returns strings**: All extracted results default to STRING type. Numeric fields (observation values, dosages) must be explicitly `CAST(... AS DOUBLE)`; otherwise aggregations (AVG/MIN/MAX) may produce unexpected results.

- **FHIR array fields**: Many fields in the FHIR standard are arrays (e.g., `name[]`, `reasonCode[]`). This guide uses `[0]` to access the first element. If you need to expand all array elements, use `LATERAL VIEW EXPLODE(SPLIT(json_array_str, ...))`.

- **Dynamic Table incremental refresh dependencies**: DWS/ADS layer Dynamic Tables depend on DWD, and DWD depends on ODS. The refresh order must follow ODS → DWD → DWS → ADS. In Studio Task, arrange the REFRESH statements in order or configure a task dependency chain.

- **Handling NULL in `DATEDIFF`**: Patients who are still admitted (`enc_status = 'in-progress'`) have a NULL `discharge_time`, and `DATEDIFF(NULL, admit_time)` returns NULL. In the DWS layer, `avg_los_days` uses `AVG(CAST(los_days AS DOUBLE))`, and `AVG` automatically ignores NULLs — the result reflects the average for discharged patients only, which is the correct business interpretation.

- **Time Travel retention**: The default retention period is 7 days. For scenarios requiring long-term historical preservation such as insurance reconciliation, regularly `INSERT INTO` month-end data snapshots into a dedicated archive table — do not rely entirely on Time Travel.

- **Column Masking**: PHI masking takes effect transparently on Dynamic Tables — if a column in the ODS layer has a masking function bound, the DWD layer that reads from ODS will also store the masked values.

---

## Related Documentation

- [Create Dynamic Table](create-dynamic-table.md) — syntax reference and incremental refresh mechanism
- [JSON Processing Guide](json_guide_for_complex_biz_cases.md) — complex JSON parsing and LATERAL VIEW expansion
- [Dynamic Data Masking](dynamic-mask.md) — Column Masking policy creation and binding
- [Time Travel](time-travel-concept.md) — TIMESTAMP AS OF syntax and retention period details
- [Studio Task Scheduling](dynamic_table_using_studio.md) — create and manage refresh tasks
- [Medallion Architecture: Pure SQL Dynamic Table Approach](lakehouse-medallion-sql-dt-guide.md) — three-layer data warehouse reference

> ⚠️ **Note (pending manual verification)**: Column Masking currently matches by username via `current_user()`, and all usernames authorized to view plaintext must be added individually to the `IN()` list in the masking function. If your Lakehouse version supports role-based dynamic matching (e.g., `HAS_ROLE('role_name')`), you can use roles instead of a username list for easier maintenance. Contact Singdata technical support to confirm whether your version supports this function.