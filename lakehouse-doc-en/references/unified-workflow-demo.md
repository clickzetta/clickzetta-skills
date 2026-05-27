# Vehicle Image Intelligent Recognition Case Based on Singdata Lakehouse

### Overview

Singdata Lakehouse innovatively provides an **AI + BI Unified Workflow** solution, seamlessly integrating traditional data processing pipelines with AI data application workflows on a single platform, achieving true data-intelligence convergence. This article uses vehicle image recognition as an example to demonstrate how to build a complete AI + BI unified workflow.

### Business Scenario

A smart traffic management platform needs to:

* Process vehicle images from intersection cameras in real time
* Automatically identify vehicle model, color, year, and other information
* Build a vehicle feature database to support subsequent traffic analysis and management decisions

### Architecture Design

```
OSS Image Storage →  Volume Data Lake →  AI Recognition Processing  →  Structured Storage  →   BI Analysis & Display
     ↓                   ↓                    ↓                          ↓                    ↓
  Raw Images       Incremental Detection    AI UDF Call           Data Parsing & Storage    Visual Reports
```

### Workflow Implementation

![](.topwrite/assets/AIworkflow.png =743)

#### **Task 1: Data Source Refresh and Incremental Detection**

```sql
-- Refresh the Volume to detect newly added image files
ALTER VOLUME sg_volume_images REFRESH;

-- Record the refresh timestamp for subsequent incremental processing
SET refresh_timestamp = CURRENT_TIMESTAMP();
```

**Best Practice Highlights**:

* Refresh the Volume periodically to discover new files
* Use timestamps to record refresh points, supporting incremental processing
* Set a reasonable refresh frequency based on business requirements (e.g., every 5 minutes)

#### **Task 2: AI Recognition and Structured Processing**

```sql
-- Incrementally process new images from the last ${last_min} minutes
WITH check_new_files AS (
    SELECT COUNT(*) AS file_count
    FROM DIRECTORY(VOLUME sg_volume_images)
    WHERE last_modified_time >= DATEADD(MINUTE, -${last_min}, CURRENT_TIMESTAMP())
),
-- AI recognition processing
recognition AS (
    SELECT *
    FROM (
        SELECT 
            relative_path as vehicle_images,
            pre_signed_url,
            -- Call the AI external function for vehicle recognition
            public.fc_image_to_text('vehicle_type', pre_signed_url) as vehicle_recognition,
            last_modified_time
        FROM (
            SELECT 
                relative_path,
                -- Generate a temporary access URL, valid for 2 hours
                get_presigned_url(volume sg_volume_images, relative_path, 7200) as pre_signed_url,
                last_modified_time
            FROM DIRECTORY(VOLUME sg_volume_images)
            WHERE last_modified_time >= DATEADD(MINUTE, -${last_min}, CURRENT_TIMESTAMP())
        )
    ) subq
    WHERE EXISTS (SELECT 1 FROM check_new_files WHERE file_count > 0)
)
-- Parse the JSON result returned by AI and insert into the table
INSERT INTO vehicle_type_data (
    car_model, car_color, year, score, 
    vehicle_recognition, pre_signed_url, last_modified_time, process_time
)
SELECT 
    get_json_object(regexp_replace(vehicle_recognition, "'", '"'), '$.result[0].name') as car_model,
    get_json_object(regexp_replace(vehicle_recognition, "'", '"'), '$.color_result') as car_color,
    get_json_object(regexp_replace(vehicle_recognition, "'", '"'), '$.result[0].year') as year,
    cast(get_json_object(regexp_replace(vehicle_recognition, "'", '"'), '$.result[0].score') as decimal(16,6)) as score,
    vehicle_recognition,
    r.pre_signed_url,
    last_modified_time,
    CURRENT_TIMESTAMP() as process_time
FROM recognition r
WHERE EXISTS (SELECT 1 FROM check_new_files WHERE file_count > 0);
```

**Best Practice Highlights**:

* Use CTE for incremental detection to avoid processing already recognized images
* Generate pre-signed URLs for the AI service to access, ensuring security
* Pay attention to quote conversion and data type conversion when parsing JSON
* Record processing timestamps for easier monitoring and auditing

#### **Task 3: Data Quality Control and Exception Handling**

```sql
-- Data quality check and exception handling
WITH quality_check AS (
    -- Check for records with failed recognition
    SELECT 
        vehicle_images,
        pre_signed_url,
        vehicle_recognition,
        CASE 
            WHEN vehicle_recognition IS NULL THEN 'AI service call failed'
            WHEN score < 0.6 THEN 'Recognition confidence too low'
            WHEN car_model IS NULL THEN 'Vehicle model recognition failed'
            ELSE 'Normal'
        END as quality_status
    FROM vehicle_type_data
    WHERE process_time >= DATEADD(MINUTE, -${last_min}, CURRENT_TIMESTAMP())
)
-- Write abnormal records to the error log table
INSERT INTO vehicle_recognition_errors (
    vehicle_images, pre_signed_url, error_type, 
    error_details, retry_count, created_time
)
SELECT 
    vehicle_images,
    pre_signed_url,
    quality_status as error_type,
    vehicle_recognition as error_details,
    0 as retry_count,
    CURRENT_TIMESTAMP() as created_time
FROM quality_check
WHERE quality_status != 'Normal';

-- Update processing statistics
MERGE INTO vehicle_process_stats AS target
USING (
    SELECT 
        DATE(CURRENT_TIMESTAMP()) as process_date,
        COUNT(*) as total_processed,
        SUM(CASE WHEN quality_status = 'Normal' THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN quality_status != 'Normal' THEN 1 ELSE 0 END) as error_count
    FROM quality_check
) AS source
ON target.process_date = source.process_date
WHEN MATCHED THEN UPDATE SET
    total_processed = target.total_processed + source.total_processed,
    success_count = target.success_count + source.success_count,
    error_count = target.error_count + source.error_count,
    last_update_time = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
    process_date, total_processed, success_count, 
    error_count, last_update_time
) VALUES (
    source.process_date, source.total_processed, 
    source.success_count, source.error_count, CURRENT_TIMESTAMP()
);
```

**Best Practice Highlights**:

* Implement data quality checks to identify low-quality results
* Establish an error handling mechanism to support subsequent retries
* Maintain processing statistics for easier monitoring of system health

### Best Practice Summary

1.  **Unified Platform Advantages**
    * Data storage, AI processing, and BI analysis are completed on the same platform
    * Eliminates data movement, reducing latency and costs
    * Unified permission management and data governance

2.  **Incremental Processing Strategy**
    * Use timestamps to implement incremental recognition, avoiding duplicate processing
    * Set reasonable processing batch sizes to balance real-time performance and resource consumption

Through this complete AI + BI unified workflow, enterprises can rapidly build end-to-end intelligent applications from data collection and AI processing to business analysis, truly enabling data-driven business decision-making.
