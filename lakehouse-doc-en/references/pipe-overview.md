# Data Pipelines and Change Capture

This chapter covers two types of objects: **Pipe** (continuous data ingestion) and **Table Stream** (change data capture). A Pipe automatically writes data from external files or message streams into a table; a Table Stream records incremental changes on a table for downstream incremental processing.

A Pipe is a **continuous data ingestion object** in Lakehouse. Once created, it runs automatically, continuously reading data from object storage (OSS/COS/S3) or Kafka and writing it to a target table — no manual triggering required.

Think of a Pipe as a continuously running conveyor belt. After a file is uploaded to an OSS subdirectory, the Pipe detects it and loads it within approximately 30 seconds. Kafka messages are consumed and written in batches at a configured interval. Unlike scheduled jobs, a Pipe runs persistently and processes new data as it arrives.

![](/.topwrite/assets/14-pipe.png)

---

## Pipe Types

| Type | Data Source | Detection Latency | Typical Use Case |
|------|--------|---------|---------|
| **Object Storage Pipe** | OSS / COS / S3 | ~30 seconds | Automatically ingest periodically uploaded CSV/Parquet/JSON files |
| **Kafka Pipe** | Kafka Topic | Per batch interval (default 60 seconds) | Real-time ingestion of logs and business events |

A Pipe is functionally equivalent to a Studio sync task. The difference is that a Pipe is created and managed via SQL DDL, making it suitable for code-driven pipeline management, while Studio sync tasks are configured through a visual interface and support more data sources (including relational databases).

---

## Continuous Ingestion from Object Storage

**Prerequisites**: Create a Storage Connection → Create an External Volume (must point to a specific subdirectory, not the bucket root path) → Create the target table → Create the Pipe.

> ⚠️ **Note**: The Volume's `LOCATION` must point to an OSS subdirectory (e.g., `oss://bucket/pipe_data/`), not the bucket root path (`oss://bucket/`). Using the root path will cause an error when creating the Pipe.

```sql
-- Step 1: Create a Storage Connection
CREATE STORAGE CONNECTION my_oss_conn
    TYPE OSS
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_ID = '...'
    ACCESS_KEY = '...';

-- Step 2: Create an External Volume (pointing to a specific subdirectory)
CREATE EXTERNAL VOLUME orders_pipe_vol
    LOCATION 'oss://my-bucket/orders_incoming/'
    USING CONNECTION my_oss_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
    RECURSIVE = TRUE;

-- Step 3: Create the target table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT,
    amount   DECIMAL(10,2),
    status   STRING
);

-- Step 4: Create the Pipe
CREATE PIPE orders_oss_pipe
    VIRTUAL_CLUSTER = 'default'
    INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO orders
FROM VOLUME orders_pipe_vol (order_id INT, amount DECIMAL(10,2), status STRING)
USING CSV OPTIONS('header' = 'true')
PURGE = TRUE;
```

Once created, the Pipe starts running immediately and checks the Volume for new files approximately every 30 seconds.

### Two Ingestion Modes

| Mode | Trigger | Source File Handling | Use Case |
|------|---------|-----------|---------|
| `LIST_PURGE` | Periodic polling scan (~30 seconds) | **Source file deleted after ingestion** | Simple setup, suitable for most scenarios |
| `EVENT_NOTIFICATION` | Object storage event notification (near real-time) | Source file retained | When you need to keep the original files; OSS and S3 only |

> ⚠️ **Note**: In `LIST_PURGE` mode, source files in OSS are **permanently deleted** after a successful ingestion and cannot be recovered. Use `EVENT_NOTIFICATION` mode if you need to retain the files.

### Deduplication

A Pipe uses `load_history` to record the paths of already-ingested files. Each unique file path is only ingested once — re-uploading the same file will not trigger a duplicate ingestion. Records in `load_history` are retained for 7 days.

```sql
-- View ingested file records
SELECT * FROM load_history('orders');
-- Result includes: file_path, last_copy_time, file_size, status, first_error_message
```

---

## Continuous Consumption from Kafka

A Pipe creates a persistent consumer group that pulls data from a Kafka Topic at a configured batch interval and writes it to a table.

```sql
CREATE PIPE kafka_orders_pipe
    VIRTUAL_CLUSTER = 'default'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO orders_raw
FROM (
    SELECT CAST(value AS STRING) AS raw_msg
    FROM TABLE(READ_KAFKA(
        'kafka-host:9092',    -- bootstrap.servers
        'orders_topic',       -- topic
        '',                   -- topic pattern (not supported yet, leave empty)
        'pipe_orders_group',  -- group_id (must be unique per Pipe for the same Topic)
        '', '', '', '',       -- start/end offsets and timestamps, managed by Pipe automatically
        'raw', 'raw',         -- key/value format
        0, map()              -- max error count, additional Kafka config
    ))
);
```

> ⚠️ **Note**: Each Pipe can only consume one Kafka Topic. Multiple Topics require multiple Pipes, and each Pipe's `group_id` must be unique.

---

## Monitoring and Management

```sql
-- View all Pipes (including status, type, VCluster)
SHOW PIPES;

-- View Pipe details
DESC PIPE orders_oss_pipe;

-- Trigger an immediate scan (without waiting for the next detection cycle)
ALTER PIPE orders_oss_pipe REFRESH;

-- Pause a Pipe
ALTER PIPE orders_oss_pipe SET PIPE_EXECUTION_PAUSED = TRUE;

-- Resume a Pipe
ALTER PIPE orders_oss_pipe SET PIPE_EXECUTION_PAUSED = FALSE;

-- Drop a Pipe (does not affect data in the target table)
DROP PIPE orders_oss_pipe;
```

Key fields in `DESC PIPE` output:

| Field | Description |
|------|------|
| `pipe_status` | `RUNNING` / `PAUSED` |
| `pipe_kind` | `VOLUME` (object storage) or `KAFKA` |
| `properties` | Configuration such as ingest_mode and vcluster |
| `input_name` | Data source (Volume or Kafka Topic) |
| `output_name` | Full path of the target table |
| `invalid_reason` | Error reason when the Pipe is in an abnormal state |

To view Pipe execution history, filter job history by `query_tag` in the format `pipe.workspace_name.schema_name.pipe_name`.

---

## Important Notes

- **Volume must point to a subdirectory**: `LOCATION` cannot be the bucket root path, or Pipe creation will fail.
- **Each Pipe requires its own Volume**: Different Pipes cannot share the same Volume.
- **The COPY statement cannot be modified**: To change the ingestion logic, drop the Pipe and recreate it.
- **Data loading order is not strictly guaranteed.**
- **Recommended file sizes**: gzip-compressed files should be under 50 MB; uncompressed CSV/Parquet files should be 128 MB–256 MB.
- **`EVENT_NOTIFICATION` mode** requires additional MNS message queue configuration, supports only Alibaba Cloud OSS and AWS S3, and requires RoleARN-based authorization.

---

## Related Documentation

- [Object Storage Pipe](pipe-storage-object.md) — Complete configuration for LIST_PURGE and EVENT_NOTIFICATION
- [Kafka Pipe](pipe-kafka.md) — READ_KAFKA parameter reference and consumer offset management
- [Pipe Syntax Reference](pipe-syntax.md) — Complete DDL syntax
- [Table Stream](om-table-stream.md) — Change data capture for CDC-driven incremental processing
