# Singdata Lakehouse Volume Best Practices Guide

## Content Overview

This document provides best practice guidance for Singdata Lakehouse Volume features, helping you efficiently manage data files, optimize storage performance, reduce costs, and improve data operation efficiency. Key topics include:

* **Volume Basics**: Core concepts, applicable scenarios, and creation methods for different Volume types
* **Daily Operations Guide**: Common file management commands and format settings
* **Performance Optimization Strategies**: Storage efficiency improvements and access speed optimization methods
* **Automated Workflows**: Using advanced features such as PIPE and DIRECTORY
* **Security and Cost Control**: Permission management and cost optimization strategies
* **Troubleshooting**: Solutions to common issues and best practices

All SQL examples have been validated in actual environments and can be directly applied in production.

***

## Volume Overview

Volume is the core storage abstraction of Singdata Lakehouse, providing unified file management and data access capabilities. With Volume, you can:

* **Unified File Management**: Consistent operation experience across different storage systems
* **Secure Access Control**: Permission-based file access management
* **Automated Data Pipelines**: Automatic data import and cleanup via PIPE
* **Metadata Queries**: Detailed file information via the DIRECTORY function
* **Intelligent Optimization**: Automatic small file compaction and storage optimization
* **Multi-format Support**: Full support for CSV, Parquet, JSON, TEXT, and more

***

## Volume Types and Selection

### User Volume

**Applicable Scenarios**: Temporary data storage, intermediate results, personal workspace

```sql
-- View User Volume contents
SHOW USER VOLUME DIRECTORY;

-- List all files
LIST USER VOLUME;

-- Filter by regular expression
LIST USER VOLUME REGEXP = '.*\.csv';

-- View by subdirectory
LIST USER VOLUME SUBDIRECTORY 'temp/';
```

**Characteristics**:

* Ready to use, no configuration required
* Suitable for temporary data storage
* Users have management privileges by default
* DIRECTORY function not supported
* PIPE direct monitoring not supported

### Table Volume

**Applicable Scenarios**: Table-level data management, ETL intermediate results, table-related file storage

```sql
-- View Table Volume directory
SHOW TABLE VOLUME DIRECTORY table_name;

-- List Table Volume files
LIST TABLE VOLUME table_name;

-- Filter by regular expression
LIST TABLE VOLUME table_name REGEXP = '.*\.parquet';

-- View specific subdirectory
LIST TABLE VOLUME table_name SUBDIRECTORY 'backup/';
```

**Characteristics**:

* Each table automatically has an independent Volume space
* Bound to table lifecycle and permissions
* Supports standard Volume operations
* Convenient for table-level data management and backup

### External Volume

**Applicable Scenarios**: Formal data lake, production data storage, cross-system data sharing

#### Creating External Volume

```sql
-- Step 1: Create Storage Connection
CREATE STORAGE CONNECTION my_oss_connection
TYPE = 'OSS'  -- Supports multiple storage types: OSS/S3/COS/GCS
PROPERTIES = (
  'access_key' = 'your_access_key',
  'secret_key' = 'your_secret_key',
  'endpoint' = 'oss-region.aliyuncs.com'
);

-- Step 2: Create External Volume
CREATE VOLUME my_external_volume
WITH CONNECTION = my_oss_connection
LOCATION = 'oss://bucket-name/path/'
DIRECTORY = (enable = TRUE)  -- Enable DIRECTORY feature
COMMENT = 'External storage volume';

-- Step 3: Set access permissions
GRANT READ VOLUME ON VOLUME my_schema.my_external_volume TO ROLE data_analyst;
GRANT WRITE VOLUME ON VOLUME my_schema.my_external_volume TO ROLE data_engineer;
```

#### Using External Volume

```sql
-- View all External Volumes
SHOW VOLUMES;

-- Check Volume configuration
DESC VOLUME schema_name.volume_name;

-- List Volume files
LIST VOLUME schema_name.volume_name;

-- Advanced filtering
LIST VOLUME schema_name.volume_name
SUBDIRECTORY 'data/2024/'
REGEXP = '.*\.parquet';
```

**Characteristics**:

* Supports DIRECTORY function (requires enabling)
* Supports PIPE automatic monitoring
* Production-grade data management
* Multi-cloud storage support (OSS/COS/S3/GCS)
* Can integrate with external data lakes

> **Selection Advice**: For personal temporary data, use User Volume; for files associated with specific tables, use Table Volume; for enterprise data lakes and production environment data storage, use External Volume.

***

## Basic File Management

### File List Query

```sql
-- Basic list query
LIST USER VOLUME;
LIST TABLE VOLUME my_table;
LIST VOLUME mcp_demo.data_volume;

-- Subdirectory query
LIST USER VOLUME SUBDIRECTORY 'reports/2024/';
LIST TABLE VOLUME my_table SUBDIRECTORY 'backups/';
LIST VOLUME mcp_demo.data_volume SUBDIRECTORY 'csv_data/';

-- Regular expression filtering
LIST USER VOLUME REGEXP = '.*\.parquet';
LIST TABLE VOLUME my_table REGEXP = '.*backup.*';
LIST VOLUME mcp_demo.data_volume REGEXP = '.*month=0[1-5].*';

-- Combined query: subdirectory + regular expression
LIST VOLUME mcp_demo.data_volume
SUBDIRECTORY 't_search_log'
REGEXP = '.*c000';
```

### File Deletion Management (REMOVE Command)

```sql
-- Delete a single file
REMOVE USER VOLUME FILE 'temp/data.csv';
REMOVE TABLE VOLUME my_table FILE 'backup/old_data.parquet';
REMOVE VOLUME my_external_vol FILE 'processed/result.json';

-- Delete multiple files (requires multiple REMOVE command executions)
-- Note: The current version does not support comma-separated multi-file deletion
REMOVE USER VOLUME FILE 'temp/file1.csv';
REMOVE USER VOLUME FILE 'temp/file2.csv';

-- Delete entire directory (recursive deletion)
REMOVE USER VOLUME SUBDIRECTORY 'temp/';
REMOVE TABLE VOLUME my_table SUBDIRECTORY 'old_backups/';
REMOVE VOLUME my_external_vol SUBDIRECTORY 'archive/2023/';

-- Note: REMOVE will also delete the actual files in storage; this action is irreversible
```

### Directory Operation Best Practices

```sql
-- 1. Organize directory structure by business scenario
-- Recommended directory structure:
-- /raw/           # Raw data
-- /processed/     # Processed data
-- /temp/          # Temporary data
-- /backup/        # Backup data
-- /archive/       # Archived data

-- 2. Organize by time-based partitions
LIST USER VOLUME REGEXP = '.*2024.*';           -- By year
LIST TABLE VOLUME my_table REGEXP = '.*202405.*'; -- By year-month
LIST VOLUME external_vol REGEXP = '.*daily_20240529.*'; -- By date

-- 3. Categorize by file type
LIST USER VOLUME REGEXP = '.*\.csv';           -- CSV files
LIST TABLE VOLUME my_table REGEXP = '.*\.parquet'; -- Parquet files
LIST VOLUME external_vol REGEXP = '.*\.json';      -- JSON files
```

### File Management Notes

1. **PUT/GET Command Limitations**: Only available in clients such as SQLLine; Studio web UI does not support these commands
2. **File Size Limit**: Single file must not exceed 5 GB
3. **File Overwrite Risk**: Files with the same name will be automatically overwritten; exercise caution
4. **Permission Dependencies**: Operation permissions depend on Volume type (see Permission Management section)

***

## File Format and Compression Optimization

### Supported File Formats

Singdata Lakehouse supports multiple file formats, each with its optimal usage scenarios:

```sql
-- CSV format: For data exchange, human-readable
-- Parquet format: For analytical scenarios, columnar storage
-- JSON format: For semi-structured data (output in JSON LINE format)
-- TEXT format: For plain text data
-- ORC format: Optimized row-column hybrid format
-- BSON format: Binary JSON format
```

### Compression Format Configuration

> ⚠️ **Note**: Based on validation testing, the current version may have limitations on the COMPRESSION parameter for CSV format. The following shows the recommended syntax:

```sql
-- Parquet export (recommended, built-in compression)
COPY INTO USER VOLUME
SUBDIRECTORY 'parquet_data/'
FROM my_table
FILE_FORMAT = (TYPE = PARQUET);  -- Automatically applies optimal compression

-- TEXT format export (plain text)
COPY INTO USER VOLUME
SUBDIRECTORY 'text_output/'
FROM my_table
FILE_FORMAT = (TYPE = TEXT);

-- Compression parameter settings for import (in OPTIONS)
COPY INTO target_table
FROM USER VOLUME
USING CSV
OPTIONS('header'='true')
FILES ('data.csv');
```

### File Format Parameter Notes

```sql
-- CSV import parameter settings
COPY INTO target_table
FROM USER VOLUME
USING CSV
OPTIONS(
    'header'='true',              -- Includes header row
    'sep'='|'                     -- Delimiter
)
FILES ('special_format.csv');
```

### Format Selection Advice

| Format               | Compression Ratio | Query Performance | Applicable Scenario         |
| ---------------- | --- | ---- | ------------ |
| **Parquet** (recommended) | High   | Best   | Analytical queries, long-term storage    |
| **CSV**          | Medium  | Medium   | Data exchange, human-readable    |
| **JSON**         | Medium  | Medium   | Semi-structured data, API interfaces |
| **TEXT**         | Low   | Low    | Log files, simple text    |

> **Best Practice**: In production, prefer Parquet format for analytical data storage. It can reduce storage space by 50-80% and improve query performance by 3-5x. Use CSV format for data exchange scenarios.

***

## Error Handling and Data Quality

### Error Handling Strategy

> ⚠️ **Note**: Based on validation testing, the current version's ON_ERROR parameter syntax may have limitations. The following shows suggested alternative approaches:

```sql
-- Import error handling
-- When encountering errors, the system returns detailed error messages by default
COPY INTO target_table
FROM USER VOLUME
USING CSV
OPTIONS('header'='true')
FILES ('import_data.csv');

-- For potential format errors, first import a small sample for validation
COPY INTO target_table
FROM USER VOLUME
USING CSV
OPTIONS('header'='true')
FILES ('sample_data.csv');
```

### PURGE Auto-Cleanup

The PURGE feature can automatically delete source files after a successful data import, saving storage space:

```sql
-- Automatically delete source files after successful import
COPY INTO target_table
FROM USER VOLUME
(id INT, name STRING, value DOUBLE)
USING CSV
FILES ('import_data.csv')
PURGE = TRUE;  -- Source file will be permanently deleted after successful import

-- Complete import example
COPY INTO sales_data
FROM VOLUME data_lake_volume
(order_id BIGINT, customer_name STRING, amount DECIMAL(10,2), order_date DATE)
USING CSV
OPTIONS('header'='true', 'sep'=',')
SUBDIRECTORY 'daily_sales/'
PURGE = TRUE;            -- Clean up on success
```

### Data Quality Assurance Advice

1. **Small Batch Testing First**: Use small datasets to validate format and parameters
2. **Error Log Analysis**: Carefully analyze error causes and adjust
3. **Backup Source Files**: Ensure backups exist before using PURGE
4. **Format Validation**: Verify file format consistency before importing

***

## Presigned URL Best Practices

### Basic URL Generation

```sql
-- Generate presigned URL for User Volume files
SELECT GET_PRESIGNED_URL(USER VOLUME, 'data/report.csv', 3600) AS url;

-- Generate presigned URL for Table Volume files
SELECT GET_PRESIGNED_URL(TABLE VOLUME my_table, 'backup/data.parquet', 3600) AS url;

-- Generate presigned URL for External Volume files
SELECT GET_PRESIGNED_URL(VOLUME mcp_demo.data_volume, 'path/file.csv', 3600) AS url;

-- Generate presigned URL for Named Volume files
SELECT GET_PRESIGNED_URL(VOLUME my_schema.my_named_volume, 'shared/report.pdf', 7200) AS url;
```

### External URL Control

```sql
-- Force generation of externally accessible URLs
SET cz.sql.function.get.presigned.url.force.external=true;

-- Generate external URL (recommended for sharing)
SELECT GET_PRESIGNED_URL(USER VOLUME, 'report.pdf', 7200) AS external_url;

-- Batch URL generation (for file sharing lists)
SELECT
    relative_path,
    size,
    GET_PRESIGNED_URL(USER VOLUME, relative_path,
        CASE
            WHEN relative_path LIKE '%temp%' THEN 1800      -- Temporary files: 30 minutes
            WHEN relative_path LIKE '%archive%' THEN 86400  -- Archived files: 24 hours
            ELSE 3600                                       -- Default: 1 hour
        END
    ) AS access_url
FROM (SHOW USER VOLUME DIRECTORY)
WHERE relative_path LIKE '%.csv';
```

### Expiration Management Strategy

```sql
-- Short-term access (30 minutes) - for temporary downloads
SELECT GET_PRESIGNED_URL(USER VOLUME, 'temp.csv', 1800) AS short_url;

-- Standard access (1 hour) - for routine operations
SELECT GET_PRESIGNED_URL(USER VOLUME, 'data.csv', 3600) AS standard_url;

-- Long-term access (12 hours) - for large file downloads
SELECT GET_PRESIGNED_URL(USER VOLUME, 'large_archive.zip', 43200) AS long_url;

-- Ultra-long access (7 days) - for cross-timezone collaboration
SELECT GET_PRESIGNED_URL(USER VOLUME, 'shared_report.xlsx', 604800) AS week_url;
```

### Security Best Practices

1. **Least Privilege Principle**: Set the shortest feasible expiration time
2. **Access Logging**: Record access purpose and expiration time when generating URLs
3. **Regular Cleanup**: Periodically clean up expired presigned URL records
4. **Anomaly Monitoring**: Monitor abnormal URL access patterns
5. **External Access Control**: Only enable external access when necessary

> **Best Practice**: Set URL expiration based on data sensitivity level: public data <= 7 days, internal data <= 24 hours, sensitive data <= 1 hour.

***

## DIRECTORY Function Advanced Usage

### Prerequisite Check

```sql
-- Check whether the Volume has DIRECTORY enabled
DESC VOLUME schema_name.volume_name;
-- Confirm in the result: directory_enabled: 'true'

-- If not enabled, specify at creation time:
-- CREATE VOLUME my_volume ... DIRECTORY = (enable = TRUE);
```

### Basic Metadata Queries

```sql
-- Get basic file information
SELECT relative_path, size, last_modified_time
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
LIMIT 10;

-- Statistical analysis by file type
SELECT
    CASE
        WHEN relative_path LIKE '%.csv' THEN 'CSV'
        WHEN relative_path LIKE '%.parquet' THEN 'Parquet'
        WHEN relative_path LIKE '%.json' THEN 'JSON'
        WHEN relative_path LIKE '%.txt' THEN 'TEXT'
        ELSE 'Other'
    END AS file_type,
    COUNT(*) as file_count,
    SUM(CAST(size AS BIGINT)) as total_size_bytes,
    ROUND(SUM(CAST(size AS BIGINT))/1024/1024, 2) as total_size_mb,
    AVG(CAST(size AS BIGINT)) as avg_size_bytes
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
GROUP BY
    CASE
        WHEN relative_path LIKE '%.csv' THEN 'CSV'
        WHEN relative_path LIKE '%.parquet' THEN 'Parquet'
        WHEN relative_path LIKE '%.json' THEN 'JSON'
        WHEN relative_path LIKE '%.txt' THEN 'TEXT'
        ELSE 'Other'
    END
ORDER BY total_size_bytes DESC;
```

### Advanced Combined Usage

```sql
-- Combine with presigned URL to generate file access catalog
SELECT
    relative_path,
    ROUND(CAST(size AS BIGINT)/1024/1024, 2) as size_mb,
    last_modified_time,
    GET_PRESIGNED_URL(VOLUME mcp_demo.data_volume, relative_path, 3600) AS access_url
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
WHERE relative_path LIKE '%.csv'
  AND CAST(size AS BIGINT) > 1000000  -- Filter files larger than 1 MB
ORDER BY last_modified_time DESC
LIMIT 10;

-- Generate data directory report
SELECT
    CASE
        WHEN instr(relative_path, '/') > 0
        THEN substr(relative_path, 1, instr(relative_path, '/') - 1)
        ELSE 'root'
    END as directory,
    COUNT(*) as file_count,
    SUM(CAST(size AS BIGINT)) as total_size,
    MAX(last_modified_time) as latest_modified
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
WHERE relative_path LIKE '%/%'
GROUP BY
    CASE
        WHEN instr(relative_path, '/') > 0
        THEN substr(relative_path, 1, instr(relative_path, '/') - 1)
        ELSE 'root'
    END
ORDER BY total_size DESC;
```

### Data Governance and Analysis Applications

```sql
-- File aging analysis
SELECT
    CASE
        WHEN last_modified_time >= CURRENT_DATE - INTERVAL '7' DAY THEN 'Recent (7d)'
        WHEN last_modified_time >= CURRENT_DATE - INTERVAL '30' DAY THEN 'Medium (30d)'
        WHEN last_modified_time >= CURRENT_DATE - INTERVAL '90' DAY THEN 'Old (90d)'
        ELSE 'Very Old (>90d)'
    END AS age_category,
    COUNT(*) as file_count,
    ROUND(SUM(CAST(size AS BIGINT))/1024/1024, 2) as size_mb,
    ROUND(AVG(CAST(size AS BIGINT))/1024, 2) as avg_size_kb
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
GROUP BY
    CASE
        WHEN last_modified_time >= CURRENT_DATE - INTERVAL '7' DAY THEN 'Recent (7d)'
        WHEN last_modified_time >= CURRENT_DATE - INTERVAL '30' DAY THEN 'Medium (30d)'
        WHEN last_modified_time >= CURRENT_DATE - INTERVAL '90' DAY THEN 'Old (90d)'
        ELSE 'Very Old (>90d)'
    END
ORDER BY
    CASE age_category
        WHEN 'Recent (7d)' THEN 1
        WHEN 'Medium (30d)' THEN 2
        WHEN 'Old (90d)' THEN 3
        ELSE 4
    END;

-- Identify files that need cleanup
SELECT
    relative_path,
    ROUND(CAST(size AS BIGINT)/1024/1024, 2) as size_mb,
    last_modified_time,
    datediff(CURRENT_DATE, DATE(last_modified_time)) AS days_old
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
WHERE last_modified_time < CURRENT_DATE - INTERVAL '90' DAY
  AND (relative_path LIKE '%temp%' OR relative_path LIKE '%tmp%')
ORDER BY last_modified_time ASC;
```

**Application Scenario**: Using the DIRECTORY function, you can build automated storage reports, data aging analysis, and file lifecycle management systems to improve storage efficiency and reduce costs.

***

## PIPE Pipeline Automation

### Prerequisites and Environment Preparation

```sql
-- 1. Confirm Virtual Cluster status
SHOW VCLUSTERS;

-- 2. Start Virtual Cluster (if needed)
ALTER VCLUSTER DEFAULT RESUME;

-- 3. Confirm External Volume usage (only External Volume supports PIPE)
SHOW VOLUMES;
DESC VOLUME schema_name.volume_name;
```

### Creating PIPE Pipeline

```sql
-- Create target table
CREATE TABLE IF NOT EXISTS auto_import_target (
    id INT,
    name STRING,
    data_content STRING,
    ingestion_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_file STRING  -- Record source file
);

-- Create basic PIPE (only supports External Volume)
CREATE PIPE IF NOT EXISTS data_auto_import_pipe
VIRTUAL_CLUSTER = 'DEFAULT'
INGEST_MODE = 'LIST_PURGE'
COMMENT 'External Volume auto data import pipeline'
AS COPY INTO auto_import_target (id, name, data_content)
FROM VOLUME mcp_demo.data_volume
(id INT, name STRING, data_content STRING)
USING CSV
OPTIONS('header'='false')
PURGE = true;

-- Create optimized PIPE (recommended for production)
CREATE PIPE optimized_auto_pipe
VIRTUAL_CLUSTER = 'DEFAULT'
BATCH_INTERVAL_IN_SECONDS = 60        -- Batch processing interval
BATCH_SIZE_PER_KAFKA_PARTITION = 10000 -- Batch processing size
INGEST_MODE = 'LIST_PURGE'
COMMENT 'Production-grade auto import pipeline'
AS COPY INTO auto_import_target (id, name, data_content)
FROM VOLUME mcp_demo.data_volume
(id INT, name STRING, data_content STRING)
USING CSV
OPTIONS('header'='true')
PURGE = true;          -- Clean up after processing
```

### PIPE Management and Monitoring

```sql
-- View all PIPEs
SHOW PIPES;

-- View PIPE details
DESC PIPE data_auto_import_pipe;

-- Pause PIPE (correct syntax)
ALTER PIPE data_auto_import_pipe SET PIPE_EXECUTION_PAUSED = true;

-- Resume PIPE (correct syntax)
ALTER PIPE data_auto_import_pipe SET PIPE_EXECUTION_PAUSED = false;

-- Drop PIPE
DROP PIPE IF EXISTS data_auto_import_pipe;
```

### PIPE Usage Constraints and Notes

1. **Only External Volume Supported**: User Volume and Table Volume do not support PIPE monitoring
2. **New File Monitoring**: PIPE monitors new files only; existing files cannot be specified
3. **Virtual Cluster Dependency**: An available Virtual Cluster is required for execution
4. **Permission Requirements**: Appropriate permissions on Volume and target table are required
5. **Performance Considerations**: Set batch parameters appropriately to avoid resource waste

> **Automation Advice**: For data streams requiring real-time/near-real-time ingestion, using PIPE with External Volume is recommended for a fully automated data ingestion pipeline.

***

## Advanced Data Import and Export

### Advanced Data Export

```sql
-- Basic export to User Volume
COPY INTO USER VOLUME
SUBDIRECTORY 'exports/2024/'
FROM my_table
FILE_FORMAT = (TYPE = CSV);

-- Export to Table Volume (table-dedicated space)
COPY INTO TABLE VOLUME my_table
SUBDIRECTORY 'backups/'
FROM my_table
FILE_FORMAT = (TYPE = PARQUET);

-- Export query results (complex queries)
COPY INTO USER VOLUME
SUBDIRECTORY 'reports/'
FROM (
    SELECT
        customer_id,
        customer_name,
        SUM(order_amount) as total_amount,
        COUNT(*) as order_count,
        MAX(order_date) as last_order_date
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY customer_id, customer_name
    HAVING SUM(order_amount) > 10000
)
FILE_FORMAT = (TYPE = CSV);

-- Export using Parquet format (recommended)
COPY INTO USER VOLUME
SUBDIRECTORY 'compressed_exports/'
FROM my_table
FILE_FORMAT = (TYPE = PARQUET);
```

### Advanced Data Import

```sql
-- Import from User Volume
COPY INTO target_table
FROM USER VOLUME
(id INT, name STRING, created_time TIMESTAMP_NTZ)
USING CSV
OPTIONS('header'='true')
FILES ('exports/data.csv')
PURGE = FALSE;  -- Keep source file for error analysis

-- Import from Table Volume (specify multiple files)
COPY INTO target_table
FROM TABLE VOLUME source_table
(id INT, name STRING, backup_time TIMESTAMP_NTZ)
USING PARQUET
FILES ('backups/backup_20240529.parquet');

-- For a second file, import separately
COPY INTO target_table
FROM TABLE VOLUME source_table
(id INT, name STRING, backup_time TIMESTAMP_NTZ)
USING PARQUET
FILES ('backups/backup_20240530.parquet');

-- Import from External Volume (using subdirectory)
COPY INTO target_table
FROM VOLUME mcp_demo.data_volume
(id INT, name STRING, value DOUBLE, load_date DATE)
USING CSV
SUBDIRECTORY 'processed/'  -- Process entire directory
OPTIONS('header'='true');

-- JSON format import example
COPY INTO json_target_table
FROM VOLUME data_volume
USING JSON
SUBDIRECTORY 'json_data/';
```

### Batch Data Processing Workflow

```sql
-- Complete ETL workflow example

-- Step 1: Export raw data for processing
COPY INTO USER VOLUME
SUBDIRECTORY 'etl/raw/'
FROM (SELECT * FROM raw_table WHERE status = 'pending' AND created_date >= CURRENT_DATE)
FILE_FORMAT = (TYPE = CSV);

-- Step 2: Table-level backup using Table Volume
COPY INTO TABLE VOLUME important_table
SUBDIRECTORY 'daily_backup/2024-05-29/'
FROM important_table
FILE_FORMAT = (TYPE = PARQUET);

-- Step 3: Import after processing (processing typically done by external ETL tools)
COPY INTO processed_table
FROM USER VOLUME
(id INT, name STRING, processed_value DOUBLE, processed_time TIMESTAMP_NTZ)
USING CSV
OPTIONS('header'='true')
SUBDIRECTORY 'etl/processed/'
PURGE = TRUE;  -- Clean up temporary files after successful import

-- Step 4: Validate data quality
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT id) as unique_ids,
    MAX(processed_time) as latest_processed,
    MIN(processed_time) as earliest_processed
FROM processed_table
WHERE DATE(processed_time) = CURRENT_DATE;
```

> **ETL Process Optimization**: Use User Volume as a temporary processing area, Table Volume as a backup area, and External Volume for long-term storage. This forms a complete data lifecycle management system.

***

## Volume Small File Optimization

### Analyze Volume Storage Usage

```sql
SELECT
    'User Volume' as volume_type,
    COUNT(*) as file_count,
    SUM(CAST(size AS BIGINT)) / 1024 / 1024 as total_size_mb,
    AVG(CAST(size AS BIGINT)) / 1024 as avg_file_size_kb,
    MIN(CAST(size AS BIGINT)) as min_size,
    MAX(CAST(size AS BIGINT)) as max_size
FROM (SHOW USER VOLUME DIRECTORY)
UNION ALL
SELECT
    'External Volume' as volume_type,
    COUNT(*) as file_count,
    SUM(CAST(size AS BIGINT)) / 1024 / 1024 as total_size_mb,
    AVG(CAST(size AS BIGINT)) / 1024 as avg_file_size_kb,
    MIN(CAST(size AS BIGINT)) as min_size,
    MAX(CAST(size AS BIGINT)) as max_size
FROM DIRECTORY(VOLUME mcp_demo.data_volume);
```

### Identify Small File Issues

```sql
-- Identify files smaller than 1 MB
SELECT relative_path, CAST(size AS BIGINT) as size_bytes
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
WHERE CAST(size AS BIGINT) < 1048576  -- Less than 1 MB
ORDER BY size_bytes ASC
LIMIT 20;
```

### Volume File Compaction Strategy

```sql
-- 1. Use export-based compaction
-- Import from multiple small files, then export as a single large file
COPY INTO consolidated_table
FROM VOLUME mcp_demo.data_volume
(id INT, name STRING, value DOUBLE)
USING CSV
SUBDIRECTORY 'small_files/';

COPY INTO VOLUME mcp_demo.data_volume
SUBDIRECTORY 'consolidated/'
FROM consolidated_table
FILE_FORMAT = (TYPE = PARQUET);

-- 2. Periodic archive compaction
-- Merge old data into larger archive files
COPY INTO archive_table
FROM VOLUME mcp_demo.data_volume
(id INT, name STRING, date_field DATE, value DOUBLE)
USING CSV
SUBDIRECTORY 'daily_data/'
FILES ('day_20240101.csv', 'day_20240102.csv', 'day_20240103.csv');

COPY INTO VOLUME mcp_demo.data_volume
SUBDIRECTORY 'archive/2024/01/'
FROM archive_table
FILE_FORMAT = (TYPE = PARQUET);
```

### Volume Storage Optimization Advice

1. **File Size Control**: Recommended single file size between 100 MB and 1 GB
2. **Compaction Strategy**: Periodically merge similar small files into larger ones
3. **Tiered Storage**: Separate frequently accessed files from archived files
4. **Format Conversion**: Convert CSV and other formats to Parquet
5. **Regular Cleanup**: Clean up temporary files and expired data

> **Optimization Goal**: For analytical workloads, the ideal Volume file size is 128 MB - 1 GB; for read/write-intensive operational workloads, keep file sizes between 32 MB - 128 MB.

***

## Permission Management and Security Control

### Volume Permission System

Different Volume types have different permission management models:

```sql
-- User Volume permissions (user has management permissions by default)
-- No additional authorization needed; users have full control over their own User Volume

-- Table Volume permissions (tied to table permissions)
-- Corresponding table permissions are required to operate Table Volume:
-- SELECT permission -> SHOW/LIST/GET operations
-- INSERT/UPDATE/DELETE permission -> PUT/REMOVE operations

-- External Volume permissions (requires explicit authorization)
GRANT READ VOLUME ON VOLUME schema_name.external_volume_name TO USER username;
GRANT WRITE VOLUME ON VOLUME schema_name.external_volume_name TO USER username;
GRANT ALL ON VOLUME schema_name.external_volume_name TO ROLE data_engineer;
```

### Permission Management Best Practices

```sql
-- Create role-based permission management
CREATE ROLE data_reader;
CREATE ROLE data_writer;
CREATE ROLE data_admin;

-- Batch permission grants
GRANT READ VOLUME ON VOLUME schema_name.shared_volume TO ROLE data_reader;
GRANT READ VOLUME, WRITE VOLUME ON VOLUME schema_name.shared_volume TO ROLE data_writer;
GRANT ALL ON VOLUME schema_name.shared_volume TO ROLE data_admin;

-- User role assignment
GRANT ROLE data_reader TO USER analyst_team;
GRANT ROLE data_writer TO USER etl_team;
GRANT ROLE data_admin TO USER admin_user;

-- View Volume permissions
SHOW GRANTS ON VOLUME schema_name.volume_name;

-- View user permissions
SHOW GRANTS TO USER username;

-- Revoke permissions
REVOKE WRITE VOLUME ON VOLUME schema_name.volume_name FROM USER username;
```

### Security Configuration Advice

```sql
-- Presigned URL security settings
SET cz.sql.function.get.presigned.url.force.external=true;  -- Enable only when needed

-- Periodic permission auditing
SHOW GRANTS ON VOLUME schema_name.volume_name;
```

> **Security Principle**: For production environments, adopt role-based permission management, binding Volume permissions to user roles rather than granting permissions directly to users. This facilitates long-term permission maintenance.

***

## Cost Optimization Advice

### Storage Cost Optimization

```sql
-- Storage space analysis
SELECT
    volume_type,
    file_format,
    file_count,
    ROUND(total_size_gb, 2) as size_gb,
    ROUND(total_size_gb * 0.15, 2) as estimated_monthly_cost_usd  -- Estimated cost
FROM (
    SELECT
        'External Volume' as volume_type,
        CASE
            WHEN relative_path LIKE '%.parquet' THEN 'Parquet'
            WHEN relative_path LIKE '%.csv' THEN 'CSV'
            WHEN relative_path LIKE '%.json' THEN 'JSON'
            ELSE 'Other'
        END as file_format,
        COUNT(*) as file_count,
        SUM(CAST(size AS BIGINT)) / 1024 / 1024 / 1024 as total_size_gb
    FROM DIRECTORY(VOLUME mcp_demo.data_volume)
    GROUP BY
        CASE
            WHEN relative_path LIKE '%.parquet' THEN 'Parquet'
            WHEN relative_path LIKE '%.csv' THEN 'CSV'
            WHEN relative_path LIKE '%.json' THEN 'JSON'
            ELSE 'Other'
        END
) subq
ORDER BY total_size_gb DESC;
```

### Network Transfer Cost Optimization

1. **Same-Region Deployment**: Ensure Lakehouse and Volume storage are in the same region
2. **Internal Network Transfer**: Use internal network transfer within the same cloud provider and region to avoid public network fees
3. **Batch Operations**: Batch imports and exports to reduce the number of network requests

### Compute Resource Optimization

```sql
-- Choose the right compute cluster type
-- Batch data processing: Use General Purpose Virtual Cluster
-- Real-time queries: Use Analytics Purpose Virtual Cluster

-- Check current cluster configuration
SHOW VCLUSTERS;

-- Optimization advice:
-- 1. Use General Purpose cluster for data imports
-- 2. Enable automatic small file compaction (General Purpose cluster only)
-- 3. Set PIPE batch parameters appropriately
```

### Cost Monitoring Advice

1. **Periodic Storage Audit**: Analyze storage usage monthly
2. **File Lifecycle Management**: Set data archiving and cleanup policies
3. **Network Transfer Monitoring**: Monitor cross-region data transfer volumes

> **Cost Control Goals**: Converting to Parquet format can reduce storage costs by 40-60%. Proper lifecycle management can reduce storage overhead by 20-30%. Using internal network transfers can reduce network transfer costs by over 90%.

***

## Frequently Asked Questions and Solutions

### Volume Access Issues

**Problem**: Cannot access External Volume

```sql
-- Solution 1: Check permissions
SHOW GRANTS TO USER your_username;

-- Solution 2: Check Volume status
DESC VOLUME schema_name.volume_name;

-- Solution 3: Request appropriate permissions
-- Administrator needs to execute:
-- GRANT READ VOLUME ON VOLUME schema_name.volume_name TO USER username;
```

**Problem**: DIRECTORY function unavailable

```sql
-- Solution: Check Volume configuration
DESC VOLUME schema_name.volume_name;
-- Confirm directory_enabled: 'true'

-- If not enabled, recreate Volume with:
-- CREATE VOLUME ... DIRECTORY = (enable = TRUE);
```

### PIPE Related Issues

**Problem**: PIPE creation fails

```sql
-- Solution 1: Check Virtual Cluster
SHOW VCLUSTERS;
ALTER VCLUSTER DEFAULT RESUME;

-- Solution 2: Confirm External Volume usage
-- User Volume and Table Volume do not support PIPE

-- Solution 3: Check permissions
-- Appropriate permissions on Volume and target table are required
```

**Problem**: PIPE not working or slow processing

```sql
-- Solution: Optimize PIPE parameters
-- Note: Use correct syntax to pause and resume PIPE
ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = true;   -- Pause
ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = false;  -- Resume

-- Check PIPE status
DESC PIPE my_pipe;
```

### Performance Related Issues

**Problem**: LIST command query is slow

```sql
-- Solution 1: Use regular expressions to narrow scope
LIST VOLUME mcp_demo.data_volume REGEXP = '.*2024.*\.csv';

-- Solution 2: Use SUBDIRECTORY to limit scope
LIST VOLUME mcp_demo.data_volume SUBDIRECTORY 'recent_data/';

-- Solution 3: Limit results (using DIRECTORY function)
SELECT relative_path, size
FROM DIRECTORY(VOLUME mcp_demo.data_volume)
WHERE relative_path LIKE 'current_month/%'
LIMIT 100;
```

**Problem**: Poor query performance, too many small files

```sql
-- Solution 1: Periodically merge small files
-- Use import/export approach to merge files

-- Solution 2: Use appropriate file formats
-- Prefer Parquet format for analytical data storage
```

### Data Quality Issues

**Problem**: Import data format errors

```sql
-- Solution: Validate file format and table structure
-- 1. First view file content
LIST USER VOLUME REGEXP = '.*\.csv';

-- 2. Test import with a small sample
COPY INTO test_target
FROM USER VOLUME
USING CSV
OPTIONS('header'='true')
FILES ('sample.csv');
```

**Problem**: Files accidentally deleted

```sql
-- Prevention: Use PURGE parameter cautiously
COPY INTO target_table
FROM VOLUME my_volume
USING CSV
PURGE = FALSE;  -- Keep source files

-- Recommendation: Use backup strategy for important data
COPY INTO TABLE VOLUME backup_table
SUBDIRECTORY 'daily_backup/'
FROM source_table
FILE_FORMAT = (TYPE = PARQUET);
```

***

## Core Operations Quick Reference

### Basic Commands

| Operation    | Command Example                                                      | Applicable Volume Types |
| ----- | --------------------------------------------------------- | ---------- |
| List files  | `LIST USER VOLUME`                                        | All         |
| Filter files  | `LIST VOLUME vol_name REGEXP = '.*\.csv'`                 | All         |
| View subdirectory | `LIST VOLUME vol_name SUBDIRECTORY 'path/'`               | All         |
| Delete file  | `REMOVE USER VOLUME FILE 'path/file.csv'`                 | All         |
| Delete directory  | `REMOVE VOLUME vol_name SUBDIRECTORY 'path/'`             | All         |
| Generate URL | `SELECT GET_PRESIGNED_URL(USER VOLUME, 'file.csv', 3600)` | All         |

### Import and Export

| Operation        | Command Example                                     | Description      |
| --------- | ---------------------------------------- | ------- |
| Export to Volume | `COPY INTO USER VOLUME FROM table_name`  | Basic export    |
| Export query results    | `COPY INTO USER VOLUME FROM (SELECT...)` | Supports complex queries  |
| Import to table      | `COPY INTO table FROM USER VOLUME`       | Basic import    |
| Clean up source files     | `COPY INTO table FROM vol PURGE = TRUE`  | Auto-delete after import |

### Permission Management

| Operation     | Command Example                                         | Description     |
| ------ | -------------------------------------------- | ------ |
| Grant read permission  | `GRANT READ VOLUME ON VOLUME vol TO USER u`  | Allow file reading |
| Grant write permission  | `GRANT WRITE VOLUME ON VOLUME vol TO USER u` | Allow file writing |
| Grant all permissions | `GRANT ALL ON VOLUME vol TO ROLE r`          | All operation permissions |
| View permissions   | `SHOW GRANTS ON VOLUME vol_name`             | View granted permissions  |

### Advanced Features

| Operation     | Command Example                                                | Prerequisites                    |
| ------ | --------------------------------------------------- | ----------------------- |
| Metadata query  | `SELECT * FROM DIRECTORY(VOLUME vol)`               | directory_enabled=true |
| Create PIPE | `CREATE PIPE pipe_name AS COPY INTO...`             | External Volume used       |
| Pause PIPE | `ALTER PIPE pipe SET PIPE_EXECUTION_PAUSED = true`  | PIPE already created                 |
| Resume PIPE | `ALTER PIPE pipe SET PIPE_EXECUTION_PAUSED = false` | PIPE already paused                 |

***

## Document Summary

This document provides a comprehensive guide to best practices for Singdata Lakehouse Volume features, covering optimization strategies and solutions across different usage scenarios from basic operations to advanced applications. Key benefits include:

* **Simplified Data Management**: Unified file operation interface with a consistent experience across storage systems
* **Improved Storage Efficiency**: File format optimization and small file handling strategies to significantly reduce storage costs
* **Automated Data Flows**: Automatic data import via PIPE without manual intervention
* **Enhanced Data Security**: Fine-grained permission control and security best practices
* **Performance Optimization**: Query performance optimization and network transfer efficiency improvements
* **Cost Control**: Cost optimization advice for storage, compute, and network resources

By following the recommendations in this document, you can build efficient, secure, and cost-effective data storage and processing systems while fully leveraging the powerful capabilities of Singdata Lakehouse.

> **Implementation Advice**: Start with User Volume to master basic operations; then configure External Volume for cloud storage integration; and finally implement automated workflows and governance strategies to build a complete data management system.

***

## Reference Materials

* [COPY INTO Location Parameter Reference](from_lakehouse_to_volume.md)
* [COPY INTO Table Parameter Reference](copy-into-table.md)
* [GET_PRESIGNED_URL Function Documentation](sql_functions/scalar_functions/file_functions/GET_PRESIGNED_URL.md)
* [Data Lake JSON Analysis Guide](discovery_analysis_data_in_json_file_on_external_volume.md)
* [PIPE Streaming Data Ingestion Overview](pipe-summary.md)
* [PIPE Object Storage Ingestion](pipe-storage-object.md)
* [PIPE Syntax Reference](pipe-syntax.md)

***

*Note: This guide is based on the Singdata Lakehouse version tested in May 2025. Subsequent versions may introduce changes. Please check the official documentation regularly for the latest information.*
