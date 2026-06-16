# Volume + Pipe + Dynamic Table End-to-End Practice

"Data lake acceleration" refers to using the three capabilities of object storage mounting (Volume), continuous data ingestion (Pipe), and incremental computation (Dynamic Table) to directly query, process, and consume file data in object storage using Serverless compute—without migrating data—replacing traditional Spark/Hive ETL and Presto/Trino ad hoc queries.

Applicable scenarios:
- **Automatic file ingestion**: CSV/Parquet files periodically uploaded to OSS/COS/S3 are automatically detected and ingested by Pipe, no manual trigger required
- **Incremental ETL**: After files are ingested, Dynamic Table automatically computes aggregated metrics incrementally, T+1 reports generated without delay
- **Legacy data activation**: Large volumes of historical files in object storage can be queried directly via Volume mount, no data migration required

Core data flow:

```
OSS/COS/S3 files → External Volume (mount) → Pipe (continuous ingestion) → Target table → Dynamic Table (incremental aggregation)
                        ↕                              ↕
                 COPY INTO/SELECT FROM         COPY INTO/SELECT FROM
```

---

## Core Concepts

| Object | Description | Analogy |
|------|------|------|
| **External Volume** | Mounts OSS/COS/S3 path for zero-copy access | "Filesystem" of Lakehouse |
| **Pipe** | Continuously running data ingestion pipeline, automatically detects new files | Conveyor belt—files are ingested as soon as they are uploaded |
| **Dynamic Table** | Materialized aggregation table that automatically refreshes incrementally | Replaces scheduled ETL jobs |

The three work together to form a **self-driving data pipeline**: file upload → automatic ingestion → automatic aggregation, fully automated with no manual scheduling.

---

## SQL Commands Involved

| Command / Function | Purpose | Use Case |
|------------|------|---------|
| `CREATE STORAGE CONNECTION` | Establish object storage authentication channel | One-time setup, shared by all Volumes |
| `CREATE EXTERNAL VOLUME` | Mount object storage path to a Schema | Configure once per Bucket subdirectory |
| `COPY INTO VOLUME` | Export data to Volume | Generate files for downstream consumption |
| `SELECT FROM VOLUME` | Directly query files in Volume | Ad hoc queries, data exploration |
| `DIRECTORY()` | List files in a Volume | View file list, validate exports |
| `ALTER VOLUME REFRESH` | Manually refresh Volume directory cache | Use when `AUTO_REFRESH=FALSE` |
| `CREATE PIPE` | Create continuous data ingestion pipeline | Automatic file ingestion |
| `ALTER PIPE` | Pause/resume Pipe | Operations management |
| `DESC PIPE EXTENDED` | View Pipe status and configuration | Monitoring, troubleshooting |
| `load_history()` | Query table's historical load records | Validate Pipe loading, troubleshoot deduplication |
| `CREATE DYNAMIC TABLE` | Create auto-incrementally refreshing aggregation table | Replace scheduled ETL jobs |
| `REFRESH DYNAMIC TABLE` | Manually trigger Dynamic Table refresh | Immediately refresh after initial creation |
| `SHOW DYNAMIC TABLE REFRESH HISTORY` | View refresh history | Monitor incremental refresh status |

---

## Prerequisites

The following uses Alibaba Cloud OSS as an example, completing the full pipeline using the `semantic_model_test` schema and `DEFAULT` Virtual Cluster.

> ⚠️ **Prerequisites**: OSS Bucket has been created, and you have AccessKey ID / AccessKey Secret. Virtual Cluster must be in RUNNING state (queries auto-wake in Serverless mode).

---

## End-to-End Practice

### Step 1: Create Storage Connection

Establish the authentication channel between Lakehouse and OSS.

```sql
-- Create OSS storage connection
CREATE STORAGE CONNECTION IF NOT EXISTS my_oss_conn
    TYPE OSS
    access_id = '<your_access_key_id>'
    access_key = '<your_access_key_secret>'
    ENDPOINT = 'oss-cn-shanghai.aliyuncs.com';
```

> **Parameter note**: Alibaba Cloud OSS uses lowercase `access_id` / `access_key`. Uppercase `ACCESS_KEY_ID` / `ACCESS_KEY_SECRET` also works. Do not use `ACCESS_KEY` / `SECRET_KEY` (missing suffixes will cause errors).

### Step 2: Create External Volume

Mount the OSS Bucket subdirectory as a Lakehouse Volume.

```sql
CREATE EXTERNAL VOLUME IF NOT EXISTS my_data_vol
    LOCATION 'oss://my-bucket/data/'
    USING CONNECTION my_oss_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = FALSE)
    RECURSIVE = TRUE
    COMMENT 'Dedicated Volume for data lake acceleration';
```

Key parameter descriptions:

| Parameter | Description |
|---|---|
| `LOCATION` | OSS path, must point to a specific subdirectory, not the bucket root path |
| `USING CONNECTION` | References the Storage Connection created in step 1 |
| `DIRECTORY.ENABLE` | Enables directory metadata index; allows using `DIRECTORY()` function to query file list |
| `AUTO_REFRESH` | Set to `TRUE` for auto-refresh; when set to `FALSE`, manual `ALTER VOLUME REFRESH` is required |
| `RECURSIVE` | Recursively scan subdirectories |

### Step 3: Create Source Table and Export to Volume

Verify bidirectional read/write capability of the Volume.

```sql
-- 1. Create source table and insert test data
CREATE TABLE IF NOT EXISTS sales_source (
    id       BIGINT        COMMENT 'Order ID',
    product  STRING        COMMENT 'Product name',
    category STRING        COMMENT 'Category',
    amount   DECIMAL(10,2) COMMENT 'Amount',
    dt       STRING        COMMENT 'Date'
) COMMENT 'Data lake acceleration test source table';

INSERT INTO sales_source VALUES
    (1, 'iPhone 15',    'Electronics', 8999.00, '2026-06-01'),
    (2, 'MacBook Pro',  'Electronics', 14999.00, '2026-06-01'),
    (3, 'AirPods',      'Electronics', 1299.00, '2026-06-01'),
    (4, 'Nike Air Max', 'Sports',      899.00, '2026-06-01'),
    (5, 'Yoga Mat',     'Sports',      199.00, '2026-06-01');

-- 2. Export as CSV to Volume
COPY INTO VOLUME my_data_vol
    SUBDIRECTORY 'export/'
FROM TABLE sales_source
    FILE_FORMAT = (TYPE = CSV);

-- 3. Export as Parquet to Volume
COPY INTO VOLUME my_data_vol
    SUBDIRECTORY 'export/'
FROM TABLE sales_source
    FILE_FORMAT = (TYPE = PARQUET);
```

> ⚠️ **`COPY INTO VOLUME` requires `SUBDIRECTORY`**: omitting this clause will throw `Syntax error at or near 'FROM'`. To export to the Volume root path, use `SUBDIRECTORY '/'`.

> ⚠️ **Export syntax**: `COPY INTO VOLUME` uses `FILE_FORMAT = (TYPE = CSV/PARQUET)`, not `USING CSV`. `USING` is only used for `SELECT FROM VOLUME` to query files.

### Step 4: Validate Volume File Read/Write

```sql
-- Refresh directory cache (manual refresh required when AUTO_REFRESH=FALSE)
ALTER VOLUME my_data_vol REFRESH;

-- View exported files
SELECT relative_path, size, last_modified_time
FROM DIRECTORY(VOLUME my_data_vol)
WHERE relative_path LIKE 'export/%';

-- Directly query CSV files
SELECT * FROM VOLUME my_data_vol
    USING CSV
    FILES('export/part00001.csv');

-- Directly query Parquet files (preserves column names)
SELECT id, product, category, amount, dt
FROM VOLUME my_data_vol
    USING PARQUET
    FILES('export/part00001.parquet');
```

> **CSV vs Parquet column name difference**: CSV files without headers auto-generate column names `f0, f1, f2...`; Parquet files preserve original column names. To use original column names with CSV, add `OPTIONS('header'='true')` on import.

### Step 5: Create Pipe for Continuous Ingestion

Pipe continuously monitors the Volume for new files and automatically ingests them into the target table.

```sql
-- 1. Create dedicated Volume for Pipe (must point to a separate subdirectory)
CREATE EXTERNAL VOLUME IF NOT EXISTS pipe_vol
    LOCATION 'oss://my-bucket/data/incoming/'
    USING CONNECTION my_oss_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
    RECURSIVE = TRUE
    COMMENT 'Dedicated Volume for Pipe continuous ingestion';

-- 2. Create target table
CREATE TABLE IF NOT EXISTS sales_ods (
    id       BIGINT        COMMENT 'Order ID',
    product  STRING        COMMENT 'Product name',
    category STRING        COMMENT 'Category',
    amount   DECIMAL(10,2) COMMENT 'Amount',
    dt       STRING        COMMENT 'Date'
) COMMENT 'ODS layer — Pipe ingestion target table';

-- 3. Create Pipe (LIST_PURGE mode)
CREATE PIPE IF NOT EXISTS sales_pipe
    INGEST_MODE = 'LIST_PURGE'
    VIRTUAL_CLUSTER = 'DEFAULT'
    COMMENT 'Sales data continuous ingestion pipeline'
AS
COPY INTO sales_ods
FROM VOLUME pipe_vol
USING CSV PURGE = TRUE;
```

> ⚠️ **Pipe key constraints**:
> - Each Pipe needs a dedicated Volume; multiple Pipes cannot share the same Volume
> - `LOCATION` must point to a specific subdirectory, not the bucket root path
> - `LIST_PURGE` mode **deletes source files** after successful ingestion (irreversible); use `EVENT_NOTIFICATION` mode to keep files
> - `PURGE = TRUE` must appear after `USING <format>`, not inside OPTIONS

#### Pipe Management

```sql
-- View Pipe status
DESC PIPE EXTENDED sales_pipe;
-- Key fields: pipe_status (RUNNING/PAUSED), ingest_mode, input_name, output_name

-- Pause Pipe (stop scanning new files)
ALTER PIPE sales_pipe SET PIPE_EXECUTION_PAUSED = TRUE;

-- Resume Pipe (restart scanning)
ALTER PIPE sales_pipe SET PIPE_EXECUTION_PAUSED = FALSE;

-- View imported file records (7-day retention)
SELECT * FROM load_history('sales_ods');
-- Returns: file_path, last_copy_time, file_size, status, first_error_message
```

> **Deduplication mechanism**: Pipe deduplicates by file path via `load_history` (within 7 days). Files with the same name will not be re-imported. To reload the same file, wait 7 days or rename the file before re-uploading.

#### Trigger Pipe Loading

Pipe starts running immediately after creation (polls approximately every 30 seconds). Writing new files to the Volume path triggers loading:

```sql
-- Simulate "new file arrival" via COPY INTO VOLUME
COPY INTO VOLUME pipe_vol
    SUBDIRECTORY '/'
FROM (SELECT * FROM sales_source WHERE dt = '2026-06-01')
    FILE_FORMAT = (TYPE = CSV);

-- Verify data has been loaded after a moment
SELECT COUNT(*) FROM sales_ods;  -- should return 5
```

> ⚠️ **Files written during pause**: Files written while Pipe is paused will not be loaded. After resuming, they will be detected in the next scan. If the file name matches an already-loaded file, it will be skipped by the deduplication mechanism.

### Step 6: Create Dynamic Table for Incremental Consumption

Based on the Pipe-ingested table, create a Dynamic Table for automatic incremental aggregation.

```sql
-- Enable change tracking on source table (prerequisite for incremental refresh)
ALTER TABLE sales_ods SET PROPERTIES ('change_tracking' = 'true');

-- Create Dynamic Table, aggregate by category
CREATE OR REPLACE DYNAMIC TABLE sales_summary
    REFRESH INTERVAL 1 HOUR vcluster DEFAULT
    COMMENT 'Category summary — incremental refresh'
AS
SELECT
    category,
    COUNT(*)     AS order_cnt,
    SUM(amount)  AS total_amount,
    AVG(amount)  AS avg_amount,
    MIN(dt)      AS min_date,
    MAX(dt)      AS max_date
FROM sales_ods
GROUP BY category;

-- Immediately trigger first refresh (resets refresh baseline time)
REFRESH DYNAMIC TABLE sales_summary;

-- Query results
SELECT * FROM sales_summary ORDER BY category;
```

> **Refresh frequency note**: `REFRESH INTERVAL 1 HOUR` calculates the next trigger based on creation time and does not align to clock hours. To trigger at a specific time, create near the target time, or execute `REFRESH` immediately after creation to reset the baseline.

#### View DT Refresh History

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'sales_summary';
-- Key fields: state (SUCCEED), refresh_mode (INCREMENTAL/FULL), duration, source_tables
```

---

## Full Data Flow Validation

```sql
-- Validate data consistency across all stages
SELECT 'Source' AS stage, COUNT(*) AS rows FROM sales_source
UNION ALL
SELECT 'ODS' AS stage, COUNT(*) AS rows FROM sales_ods
UNION ALL
SELECT 'Summary' AS stage, COUNT(*) AS rows FROM sales_summary;
```

| Stage | Data Volume | Description |
|---|---|---|
| Source | 5 rows | Raw data (INSERT) |
| ODS | 5 rows | Pipe ingestion (CSV → table) |
| Summary | 3 rows | Dynamic Table aggregation (3 category groups) |

---

## Best Practices

### File Size Recommendations

| Format | Recommended Size | Description |
|---|---|---|
| gzip compressed | ~50 MB | Files that are too large reduce parallelism |
| CSV uncompressed | 128-256 MB | Balance between scan speed and file count |
| Parquet uncompressed | 128-256 MB | Columnar storage, more efficient for queries |

### Volume and Pipe Design Principles

1. **Each Pipe has its own Volume**: Different Pipes cannot share the same Volume to avoid interference
2. **Volume points to a subdirectory**: Do not point to the bucket root path, as this will cause Pipe creation errors
3. **LIST_PURGE vs EVENT_NOTIFICATION**:
   - `LIST_PURGE`: Simple configuration, suitable for most scenarios, deletes source files after loading
   - `EVENT_NOTIFICATION`: Low latency, retains source files, but only supports OSS+S3, and requires additional MNS/SQS configuration

### Dynamic Table Design Principles

1. **Use GP type Virtual Cluster** (such as `DEFAULT`): GP type supports small file merging; AP type does not
2. **Enable change_tracking**: If the source table does not have it enabled, DT performs a full refresh every time with no incremental support
3. **REFRESH immediately after creation**: Ensures first data availability and resets the refresh baseline time

### Data Lifecycle

```
File upload → Pipe scan → COPY INTO ingest → PURGE delete → Dynamic Table incremental refresh
     ↓              ↓              ↓               ↓                        ↓
 OSS write     30s polling   load_history record  source file deleted   aggregation update
```

---

## Test Validation Results

The following results are from actual testing on an Alibaba Cloud Shanghai instance (`f8866243`):

| Test Item | Result | Details |
|---|---|---|
| Storage Connection creation | ✅ | OSS connection normal |
| External Volume mount | ✅ | Directory access normal; `AUTO_REFRESH=FALSE` requires manual refresh |
| SELECT FROM VOLUME (CSV) | ✅ | Without header, column names are f0-f4; Parquet preserves column names |
| SELECT FROM VOLUME (Parquet) | ✅ | Column names and types both preserved |
| COPY INTO TABLE (CSV) | ✅ | 5 rows correctly imported |
| COPY INTO TABLE (Parquet) | ✅ | 5 rows correctly imported |
| COPY INTO VOLUME export | ⚠️ | **Must include `SUBDIRECTORY`**, otherwise syntax error |
| Pipe LIST_PURGE creation | ✅ | Status immediately becomes RUNNING |
| Pipe load trigger | ✅ | Auto-loaded in ~30 seconds; load_history records complete |
| Pipe PURGE deletion | ✅ | Source files auto-deleted after successful load |
| Pipe pause/resume | ✅ | Files not loaded during pause; re-scanned after resume |
| Pipe deduplication | ✅ | Same-name files correctly blocked by load_history (7-day retention) |
| Dynamic Table incremental refresh | ✅ | INCREMENTAL mode, aggregation completed in 346ms |

---

## Notes

| Note | Impact | Recommendation |
|---|---|---|
| `COPY INTO VOLUME` requires `SUBDIRECTORY` | Without it, syntax error | Use `SUBDIRECTORY '/'` for root path |
| Generic CSV column names | Without header, column names are f0-f4 | Use `OPTIONS('header'='true')` or switch to Parquet |
| Manual refresh needed when `AUTO_REFRESH=FALSE` | Directory does not update | Execute `ALTER VOLUME name REFRESH` |
| Pipe same-name file deduplication | Same-name files not loaded after pause/resume | Rename file on re-upload, or wait 7 days for expiration |
| `load_history` column name | `last_copy_time` not `last_load_time` | Pay attention to column name when querying |
| Virtual Cluster auto-sleep | Suspends after 60s without queries | Serverless mode pays on-demand, no concern needed |
| Pipe COPY statement is immutable | When logic adjustment is needed | DROP PIPE then CREATE again |
| AP type Virtual Cluster does not support small file merging | Query performance degrades over time | Always use GP type (`DEFAULT`) |

---

## Related Documents

- [Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md) — Alibaba Cloud/Tencent Cloud/AWS real-world comparison
- [Volume Overview](volume-overview.md) — Volume concepts, types, and file operations
- [Object Storage Pipe](pipe-storage-object.md) — LIST_PURGE and EVENT_NOTIFICATION complete configuration
- [Pipe Overview](pipe-overview.md) — Pipe vs Table Stream comparison
- [Dynamic Table Overview](dynamic-table-introduce.md) — Incremental computation mechanism
- [Create External Volume](create-external-volume.md) — Complete DDL syntax
- [Import Data from Volume](from_volume_to_table.md) — COPY INTO syntax
- [Export Data to Volume](from_lakehouse_to_volume.md) — Export syntax
- [Query SHOW JOBS](show-jobs.md) — Filter Pipe jobs by query_tag
