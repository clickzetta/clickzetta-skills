# Singdata Lakehouse Data Engineering Handbook

This document provides data engineers and architects with a comprehensive guide covering **data ingestion method selection**, **performance tuning**, and **production operations diagnostics** for Singdata Lakehouse. The content is distilled from production environment best practices.

> **Scope**: This document includes some internal tuning parameters (with the `cz.*` prefix) that are configured at the session level via the `SET` command. Some parameters may be superseded by adaptive mechanisms as the product evolves — always refer to the official documentation.

---

## Part 1: Data Ingestion Method Selection and Implementation

When importing external data into Lakehouse, there are five typical paths depending on data volume, latency requirements, and operational preferences.

### 1.1 Method Selection Decision Matrix

| Method | Use Case | Data Volume | Latency | Typical Example |
|------|----------|----------|--------|----------|
| **Studio UI Import** | Ad hoc testing, small-scale data, no-code operation | < 2GB, < 200 columns | One-time | Quick upload of Excel/CSV for validation |
| **Volume Load (View/Table)** | Large-scale historical data, very wide tables | Unlimited | Batch | Offline CSV/Parquet bulk ingestion |
| **Object Storage Pipe** | OSS/S3/COS continuous monitoring, automatic ingestion | Unlimited | Near real-time (minute-level) | Timed log file scanning and ingestion |
| **Kafka Pipe** | Log collection, real-time metrics, high-concurrency streaming | TB/day scale | Second-level | App behavior log real-time writes |
| **Real-time/Offline Sync Tasks** | Direct database (RDS) connection, continuous production integration | Unlimited | Near real-time/offline | MySQL → Lakehouse full/incremental sync |

> **Summary recommendations**:
> *   For **large wide tables with hundreds of megabytes** (e.g., 3000+ columns), skip Studio and use the **Volume Load method** instead.
> *   For **continuous object storage ingestion** (files being generated continuously), use **Object Storage Pipe** (LIST_PURGE or EVENT_NOTIFICATION mode).
> *   For **production-grade database sync**, migrate to **Sync Tasks** or **Kafka Pipe**.
> *   Studio import should only be used as a **supplementary method** for small-scale validation.

---

### 1.2 Method Implementation and Best Practices

#### Method 1: Studio Data Import (Small Scale)

Studio provides a visual "Upload Data" feature that uses a synchronous call mechanism internally.

**⚠️ Key limitations:**
*   **File size**: Recommended not to exceed **2 GiB**.
*   **Column count limit**: Recommended to stay within **100–200 columns**.
    *   **Note 1: Schema inference timeout**. When the column count exceeds 1000, Studio will error out when reading the first 1000 rows to infer field types, as this exceeds the 1-minute timeout.
    *   **Note 2: Case sensitivity**. Importing table names or field names containing **uppercase letters** may trigger compatibility issues in the Lakehouse SDK, causing the import to fail.
    *   **Note 3: Dirty data is hard to locate**. If a row contains dirty data, Studio may abort with an unclear error message.

#### Method 2: Loading Data from Volume (Large Scale)

Upload files to object storage (OSS/S3/COS) and load them directly via SQL.

**Step 1: Upload files**
Use `ossutil` or another tool to upload CSV/Parquet files to the path mounted by the Volume.

**Step 2: Create a View or Table**

**Option A: Create a View** — suitable for quick queries without moving data

```sql
-- Query a CSV file via User Volume (no schema specified, auto-inferred)
SELECT * FROM USER VOLUME
USING CSV
OPTIONS ('header' = 'true')
FILES ('data.csv')
LIMIT 5;

-- Query via User Volume with explicit schema (recommended to avoid inference errors)
SELECT * FROM USER VOLUME
    (col_1 STRING, col_2 STRING, col_3 INT)
USING CSV
OPTIONS ('header' = 'true')
FILES ('data.csv')
LIMIT 5;

-- Create a view to encapsulate the query logic
CREATE VIEW IF NOT EXISTS wide_table_view AS
SELECT * FROM USER VOLUME
    (col_1 STRING, col_2 STRING, col_3 INT)
USING CSV
OPTIONS ('header' = 'true')
FILES ('data.csv');
```

**Option B: Create a Physical Table** — suitable for long-term storage and accelerated queries

```sql
-- Create a physical table directly from Volume (data written to Lakehouse storage)
CREATE TABLE IF NOT EXISTS wide_table_physical AS
SELECT * FROM USER VOLUME
    (col_1 STRING, col_2 STRING, col_3 INT)
USING CSV
OPTIONS ('header' = 'true')
FILES ('data.csv');

-- Or use COPY INTO (suitable for large data volumes, supports error handling)
COPY INTO wide_table_physical
FROM USER VOLUME
USING CSV
OPTIONS ('header' = 'true')
FILES ('data.csv')
ON_ERROR = 'CONTINUE';
```

> **Named Volume syntax**: If you use an explicitly created Named Volume, the syntax is `FROM VOLUME vol_name (...)`, for example:
> ```sql
> SELECT * FROM VOLUME my_vol (id INT, name STRING)
> USING CSV OPTIONS ('header' = 'true') FILES ('data.csv');
> ```

#### Method 3: Object Storage Pipe for Continuous Ingestion

Object Storage Pipe continuously monitors OSS/S3/COS for new files and automatically imports them into a Lakehouse table. Two modes are supported:

*   **LIST_PURGE**: Periodically scans the directory and deletes source files after import (suitable when you don't need to retain original files)
*   **EVENT_NOTIFICATION**: Triggered by object storage event notifications (suitable for near real-time scenarios)

```sql
-- Create an Object Storage Pipe (LIST_PURGE mode)
CREATE PIPE IF NOT EXISTS my_oss_pipe
    VIRTUAL_CLUSTER = 'default'
    INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO target_table
FROM VOLUME my_oss_vol
USING CSV
OPTIONS ('header' = 'true')
ON_ERROR = 'CONTINUE';

-- Create an Object Storage Pipe (EVENT_NOTIFICATION mode, near real-time)
CREATE PIPE IF NOT EXISTS my_oss_pipe_realtime
    VIRTUAL_CLUSTER = 'default'
    INGEST_MODE = 'EVENT_NOTIFICATION'
AS
COPY INTO target_table
FROM VOLUME my_oss_vol
USING PARQUET
ON_ERROR = 'CONTINUE';
```

> **Key difference**:
> *   **Volume Load**: Execute `COPY INTO` once manually — suitable for bulk historical data ingestion
> *   **Object Storage Pipe**: Runs continuously, automatically detects new files and imports them — suitable for continuously generated data files
>
> 📖 See also: [Using Pipe for Continuous Object Storage Ingestion](pipe-storage-object.md), [Pipe Continuous Ingestion Introduction](pipe-introduction.md)

#### Method 4: Kafka Pipe for Real-Time Ingestion

Kafka Pipe supports second-level writes and is suitable for high-throughput scenarios.

```sql
CREATE PIPE IF NOT EXISTS yishou_data.ods_sls_h5_log_dt_pipe
    VIRTUAL_CLUSTER = 'kafka_pipe'
    BATCH_INTERVAL_IN_SECONDS = '30'
    BATCH_SIZE_PER_KAFKA_PARTITION = '100000'
AS
COPY INTO yishou_data.ods_sls_h5_log_dt
FROM (
    SELECT
        json.`activity` AS activity,
        json.`data` AS data,
        date_format(cast(json.`__time__` AS TIMESTAMP), 'yyyyMMdd') AS dt
    FROM (
        SELECT from_json(
                    cast(value AS STRING),
                    'struct<`activity`:string, `data`:string, `__time__`:string>'
                ) AS json
        FROM read_kafka (
            '1.4.4.8:9011,1.6.6.5:9011',  -- Kafka address
            'bigdata_sls_h5_log',          -- Topic
            '',
            'group_id_behavior_log',       -- Consumer Group
            '', '', '', '',
            'raw', 'raw',
            0,
            MAP('kafka.security.protocol', 'PLAINTEXT')
        )
    )
);
```

> **Parameter notes**:
> * `VIRTUAL_CLUSTER`: Specifies the compute cluster for COPY jobs (note: Pipe syntax uses `VIRTUAL_CLUSTER`, not `VCLUSTER`)
> * `BATCH_INTERVAL_IN_SECONDS`: Batch processing interval in seconds, default 60
> * `BATCH_SIZE_PER_KAFKA_PARTITION`: Number of messages per partition per batch, default 500000

---

## Part 2: Core Object Performance Tuning Guide

In production environments, Lakehouse provides a rich set of parameters (Flags/Properties) for performance tuning. The following organizes high-frequency **best practices** and **notes** by component.

> **Parameter configuration notes**:
> * **Session level**: Configure via `SET parameter_name = value;` — applies only to the current session
> * **Table level**: Configure via `ALTER TABLE ... SET PROPERTIES ('parameter_name' = 'value');` — persists for the table

### 2.1 Table and Storage Optimization

#### Best Practices

| Parameter / Property | Configuration Level | Recommended Value / Behavior | Description |
|-------------|----------|---------------|------|
| `cz.table.target.file.size` | Session | `134217728` (128MB) | **Core parameter**. Controls target file size, which in turn automatically adjusts DOP. Recommended replacement for the older `output.file.max.size`. |
| `cz.compaction.strategy` | Table property | `dml` / `auto` | **MV + DT default is dml**. **Dimension tables should be set to dml**. To disable automatic Compaction, configure `disable`. |
| `data_lifecycle` | Table property | `14` | Controls data retention in days, productized. |
| `cz.storage.parquet.json.storage.mode` | Session | `jsonb` | **No column extraction**. Suitable for querying the entire JSON (e.g., `SELECT json_column`). |
| `cz.storage.parquet.json.storage.mode` | Session | `jsonb_extracted` | **Column extraction** (default). Suitable for querying partial JSON columns (e.g., `SELECT json_extract(...)`). |
| `cz.common.json.build.jsonb.index` | Session | `false` | Can be set to false in specific scenarios to improve write performance. |

**Configuration examples**:

```sql
-- Session level: set target file size to 128MB
SET cz.table.target.file.size = 134217728;

-- Session level: set JSON storage mode to no column extraction
SET cz.storage.parquet.json.storage.mode = 'jsonb';

-- Table level: set Compaction strategy for a dimension table to dml
ALTER TABLE dim_users SET PROPERTIES ('cz.compaction.strategy' = 'dml');

-- Table level: set data lifecycle to 14 days
ALTER TABLE logs SET PROPERTIES ('data_lifecycle' = '14');
```

#### Notes
*   **Parquet Block Size**: If a particular column is very large (e.g., `exps_arr`), the default Row Group will be small, increasing query IO. Try increasing `cz.storage.parquet.block.size` (e.g., to 2GB).
*   **File Slice Cache**: If the upstream table of a DT is updated frequently, the cache version may be too new, causing Cache Misses. Configure `file_slice_cache_refresh_delay_sec='1800'` to retain the version from 30 minutes ago.

---

### 2.2 Dynamic Table (DT)

#### Best Practices
*   **Automatic Compaction**: MV and DT have Compaction enabled by default — no additional configuration needed.
*   **Multi-SQL jobs**: For large tables, enabling `cz.compaction.server.multi.sql.job='true'` can split partitions for concurrent processing (subject to available resources).

#### Common Issues
1.  **Global Shuffle Blocking (Severe)**
    *   **Symptom**: A DT refresh generates a huge, complex incremental plan, causing massive EPH Shuffle consumption globally and degrading the performance of other incremental tasks in production.
    *   **Cause**: Backfill was not correctly enabled, or the dimension table scope was not restricted.
    *   **Solution**:
        *   Set at session level: `SET cz.optimizer.incremental.backfill.enabled = true;`
        *   Explicitly specify dimension tables: `SET cz.optimizer.incremental.dimension.tables = 'your_dim_table';`

2.  **Forcing Incremental Refresh on External Tables (Anti-pattern)**
    *   **Note**: External tables theoretically do not support incremental computation. While you can force incremental refresh via `CREATE DT`, product behavior is not guaranteed to be stable.
    *   **Recommendation**: For external data sources, use **Kafka Pipe** or **full refresh** instead.

---

### 2.3 Pipe Tuning (Kafka + Object Storage)

#### Kafka Pipe Best Practices
*   **Kafka Split Strategy**: Default splits by partition. For topics with severe data skew, enable the `size` strategy:
    *   `SET cz.sql.split.kafka.strategy = 'size';`
    *   `SET cz.mapper.kafka.message.size = '200000';` (adjusts split count based on the configured size)

#### Kafka Pipe Notes
*   **Delta File Merge**: For UBT tables, it is recommended to disable Delta file merging: `SET cz.sql.enable.dml.delta.file.merge = false;`. This is generally only needed for Merge Into on partitioned tables.

#### Object Storage Pipe Best Practices
*   **LIST_PURGE mode**: Suitable for scenarios where files are generated infrequently and minute-level latency is acceptable. The Pipe periodically scans the directory and deletes source files after import.
*   **EVENT_NOTIFICATION mode**: Suitable for near real-time scenarios (second to minute level). Triggered by object storage event notifications (e.g., OSS EventBridge), no polling required.
*   **File format selection**: Parquet format has better import performance than CSV (no text parsing needed, reads columnar data directly).

#### Object Storage Pipe Notes
*   **The COPY statement in a Pipe does not support `FILES`, `REGEXP`, or `SUBDIRECTORY` parameters**: The Pipe automatically scans all files in the Volume root directory — you cannot specify particular files.
*   **Each Pipe requires a dedicated Volume**: You cannot reuse the same Volume for multiple Pipes, as this will cause file conflicts.
*   **Small file problem**: If the source generates a large number of small files, set `cz.table.target.file.size` in the Pipe's COPY statement to control output file size.

> 📖 See also: [Using Pipe for Continuous Object Storage Ingestion](pipe-storage-object.md), [Pipe Continuous Ingestion Introduction](pipe-introduction.md)

---

### 2.4 Query and UDF Tuning

#### Note: UDF Concurrency Explosion
*   **Symptom**: A UDF spawned 40,000 Tasks, resulting in terrible performance.
*   **Cause**: The parameter threshold was set too small, bypassing automatic DOP.
    *   Example of incorrect configuration: `SET cz.sql.dag.shuffle.vertex.manager.desired.task.input.size = 4194304;` (4MB is too small)
*   **Solution**: Adjust Split Size and Skew Threshold appropriately based on data volume, or rely on system adaptive behavior.

#### Key Query Flag Reference
*   `cz.sql.stage.memory.mb`: If you increase file size or Parquet Row Group size, you must also increase Task Memory accordingly (e.g., `SET cz.sql.stage.memory.mb = 8192;`), otherwise **OOM** is very likely.
*   `cz.sql.enable.dag.auto.adaptive.split.size`: Recommended to enable (`SET cz.sql.enable.dag.auto.adaptive.split.size = true;`) so the system automatically adjusts DOP based on Target File Size.

---

## Part 3: Production Operations and Diagnostics

### 3.1 Slow Query Diagnosis: Three-Step Approach

When you encounter a slow query, follow these three steps to quickly locate the problem:

**Step 1: Check the execution plan (`EXPLAIN`)**

```sql
-- Basic execution plan: quickly identify the execution method
EXPLAIN SELECT * FROM large_table WHERE status = 'active';

-- Extended execution plan: view logical plan, physical plan, and optimization details
EXPLAIN EXTENDED SELECT * FROM large_table WHERE status = 'active';
```

*   **Identify Shuffle Join**: `PhysicalShuffleJoin` in the execution plan indicates a large-table-to-large-table join, which is prone to data skew.
*   **Identify Broadcast Join**: `PhysicalBroadcastJoin` in the execution plan indicates a small table is broadcast to a large table — this is best practice.
*   **Identify full table scans**: Check whether predicate pushdown and partition pruning are in effect.

> 📖 See also: [EXPLAIN Command](explain.md)

**Step 2: Check job status (`SHOW JOBS`)**

```sql
-- View the most recent 10 jobs
SHOW JOBS LIMIT 10;

-- View jobs with execution time exceeding 5 minutes
SHOW JOBS WHERE execution_time > INTERVAL 5 MINUTE;

-- View failed jobs in a specific VCluster
SHOW JOBS IN VCLUSTER default WHERE status = 'FAILED';
```

*   **Queued** (`QUEUED`): Insufficient resources, job is waiting in the queue. Consider scaling up the VCluster or adjusting job priority.
*   **Running slowly** (`RUNNING` but taking a long time): SQL or data issue — proceed to Step 3.

> 📖 See also: [SHOW JOBS](show-jobs.md)

**Step 3: Check job details (`DESC JOB`)**

```sql
-- Get the job_id and view detailed information
DESC JOB '2026051922541032000079660';
```

*   `execution_time`: Execution duration (milliseconds)
*   `input_tables`: Input tables with rows read and bytes read
*   `output_tables`: Output result rows and bytes
*   `vcluster_type`: Compute resource type (`GENERAL` / `ANALYTICS`)

> 📖 See also: [DESC JOB](desc-job.md)

---

### 3.2 Small File Management and Compaction in Practice

Small files are a performance killer in Lakehouse. Frequent small-batch INSERT/UPDATE/DELETE operations generate large numbers of small files, increasing metadata overhead and query IO.

**Automatic Compaction**

*   Regular tables and Dynamic Tables have automatic Compaction enabled by default (`cz.compaction.strategy = 'dml'`)
*   Background processes periodically merge small files — no manual intervention needed

**Manual OPTIMIZE**

When automatic Compaction cannot keep up with write speed, or when immediate optimization is needed:

```sql
-- Asynchronously merge small files for the entire table (default, non-blocking)
OPTIMIZE my_table;

-- Synchronous merge (blocking, suitable for development and testing)
OPTIMIZE my_table OPTIONS('cz.sql.optimize.table.async' = 'false');

-- Merge only a specific partition
OPTIMIZE my_table WHERE dt = '2024-01-15';
```

> ⚠️ **Note**: OPTIMIZE can only run in a **general-purpose compute cluster (GENERAL)**. It will not take effect in an analytics cluster.

**Diagnosing Small File Severity**

```sql
-- View the number and size of files in a table
DESC EXTENDED my_table;
```

If the file count is much larger than the data volume (e.g., 10,000 files for 10GB of data), the small file problem is severe.

> 📖 See also: [OPTIMIZE Command](optimize.md)

---

### 3.3 Dynamic Table Refresh Optimization

Slow DT refresh is the most frequently reported issue.

**Viewing Refresh Details**

```sql
-- View the most recent 10 refresh records
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'dws_daily_orders' LIMIT 10;
```

Key field explanations:
*   `refresh_mode`: `INCREMENTAL` / `FULL` / `NO_DATA` (no changes)
*   `state`: `SUCCEED` / `FAILED` / `RUNNING`
*   `stats`: Rows processed incrementally (e.g., `rows_inserted=1000:rows_deleted=50`)
*   `duration`: Refresh duration

> 📖 See also: [SHOW REFRESH HISTORY](refresh-history.md)

**How to determine whether a DT is using incremental refresh**

```sql
-- Method 1: Check refresh history (post-hoc confirmation)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt' LIMIT 1;

-- Method 2: EXPLAIN preview (pre-execution confirmation, requires enabling the flag)
SET cz.optimizer.explain.can.incrementalize = true;
EXPLAIN REFRESH DYNAMIC TABLE my_dt;
-- CanBeIncrementalized = Yes in the output means incremental is supported
```

> 📖 See also: [Using EXPLAIN to View Dynamic Table Refresh Mode](dynamic-table-incre.md)

**What operations cause a DT to fall back to full refresh?**

*   Modifying the source table schema (adding, dropping, or changing column types)
*   Using SQL operators that do not support incremental processing (e.g., `ORDER BY`, `ROW_NUMBER()` and other window functions)
*   Source table data change volume exceeds the threshold (automatic fallback)
*   Parameter values for a partitioned DT change

**The power of partitioned DTs**

For massive datasets, using `PARTITIONED BY` in a DT can narrow the refresh scope to a single partition, improving performance by 10–100x:

```sql
-- Create a partitioned dynamic table
CREATE DYNAMIC TABLE dws_daily_orders (order_date, order_cnt, total_amount)
    PARTITIONED BY (order_date)
    REFRESH INTERVAL 1 HOUR VCLUSTER default
AS
SELECT DATE(created_at) AS order_date, COUNT(*) AS order_cnt, SUM(amount) AS total_amount
FROM ods_orders
WHERE created_at >= SESSION_CONFIGS()['dt.args.order_date']
GROUP BY DATE(created_at);

-- Refresh only a specific partition (incremental)
SET dt.args.order_date = '2024-01-15';
REFRESH DYNAMIC TABLE dws_daily_orders PARTITION (order_date = '2024-01-15');
```

> 📖 See also: [Dynamic Table Parameterized Definition](dynamic-table-parameters.md), [Dynamic Table Scheduling and Deployment Standards](dynamic-table-scheduling.md)

---

### 3.4 Cost Optimization Checklist

**VCluster Auto-Suspend**

```sql
-- ETL cluster: auto-suspend after 60 seconds of idle time
ALTER VCLUSTER etl_cluster SET AUTO_SUSPEND_IN_SECOND = 60;

-- BI query cluster: auto-suspend after 30 minutes of idle time (leverages cache acceleration)
ALTER VCLUSTER bi_cluster SET AUTO_SUSPEND_IN_SECOND = 1800;
```

> 📖 See also: [Compute Cluster Cache](vc_cache.md)

**DT Refresh Frequency Tuning**

Don't blindly pursue 1-minute refresh intervals. Adjust based on actual business latency tolerance:

| Scenario | Recommended Refresh Interval | CRU Consumption |
|---|---|---|
| T+1 reports | `1 DAY` | Lowest |
| Hourly metrics | `1 HOUR` | Medium |
| Minute-level dashboards | `10~30 MINUTE` | Higher |
| Second-level real-time | Not recommended for DT — use real-time sync tasks instead | Highest |

**Hot/Cold Data Tiering**

Use `data_lifecycle` to automatically clean up expired data, and combine with External Volume to archive cold data to low-frequency OSS storage:

```sql
-- Set data lifecycle to 90 days (data not updated in 90 days is automatically reclaimed)
ALTER TABLE logs SET PROPERTIES ('data_lifecycle' = '90');

-- Delete table metadata when lifecycle expires (saves metadata storage)
ALTER TABLE temp_logs SET PROPERTIES ('data_lifecycle' = '7', 'data_lifecycle_delete_meta' = 'true');
```

> 📖 See also: [Data Lifecycle](data-lifecycle.md)

---

### 3.5 Query Acceleration Features

Lakehouse has several features that are enabled by default but not widely known:

**Result Cache**

*   Conditions for the same SQL to return in seconds:
    *   Underlying table data has not changed
    *   SQL statement matches exactly (including case and whitespace)
    *   Does not contain non-deterministic functions (e.g., `CURRENT_TIMESTAMP()`, `RAND()`)
    *   Does not contain view references
*   Retained for 24 hours by default; extended by 24 hours if reused
*   Can be disabled via `SET cz.sql.enable.shortcut.result.cache = false;`

> 📖 See also: [Understanding and Using Result Cache](result_cache.md)

**Metadata Cache**

*   Why do aggregate queries like `COUNT(*)`, `MAX()`, `MIN()` return in milliseconds?
*   Lakehouse maintains metadata for each table (row count, max/min values, etc.), allowing results to be returned without scanning data files.

**Compute Cluster Local Cache (VC Cache)**

*   **Active caching**: Use `ALTER VCLUSTER ... SET PRELOAD_TABLES` to preload hot tables onto the cluster's local SSD, reducing BI report query latency by 50%+
*   **Passive caching**: Files read during the first query are automatically cached locally, and subsequent queries hit the cache directly

```sql
-- View the preload table status for the current VCluster
SHOW PRELOAD CACHED STATUS;

-- Configure active caching (supported by AP-type clusters)
ALTER VCLUSTER bi_cluster SET PRELOAD_TABLES = 'dws.daily_sales,dws.user_profile';
```

> 📖 See also: [Compute Cluster Cache](vc_cache.md)
