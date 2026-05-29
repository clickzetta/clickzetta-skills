# Pipe

Pipe is the Lakehouse's **continuous data ingestion object**. Created via SQL DDL, it runs automatically, continuously reading data from Kafka or object storage (OSS/COS/S3) and writing it to target tables without any manual triggering.

Think of a Pipe as an "automated conveyor belt" — once data files are uploaded to an OSS subdirectory or messages are written to Kafka, the Pipe automatically detects and loads them. Unlike scheduled jobs, a Pipe runs persistently; files are typically ingested within about 30 seconds of being uploaded.

## Pipe vs. Studio Sync Jobs

| Dimension | Pipe | Studio Sync Job |
|------|------|----------------|
| Creation method | SQL DDL | Studio visual interface |
| Applicable sources | Kafka, OSS/COS/S3 | Relational databases, Kafka, object storage |
| Management method | SQL commands | Studio interface |
| Suitable for | SQL-oriented, code-based management | Prefer visual configuration |

The two are functionally equivalent; choose based on your workflow preference.

## Pipe Types

### Object Storage Pipe (OSS/COS/S3)

Continuously scans for new files in object storage and ingests them. Two modes are supported:

| Mode | Trigger | Source File Handling | Extra Configuration |
|------|---------|-----------|---------|
| `LIST_PURGE` | Periodic polling scan (approx. 30 seconds) | **Permanently deletes source files after ingestion** | No extra configuration needed |
| `EVENT_NOTIFICATION` | Object storage event notification (near real-time) | Retains source files | Requires MNS message queue configuration; OSS and S3 only |

> ⚠️ **Note**: In `LIST_PURGE` mode, source files in OSS are **permanently deleted** after successful ingestion and cannot be recovered. To retain files, use `EVENT_NOTIFICATION` mode.

> ⚠️ **Note**: The Volume's `LOCATION` must point to a specific subdirectory (e.g., `oss://bucket/data/`), not the bucket root path (`oss://bucket/`). Using the root path will cause an error when creating the Pipe.

```sql
-- Step 1: Create a storage connection and Volume (must point to a subdirectory)
CREATE STORAGE CONNECTION my_oss_conn
    TYPE OSS
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_ID = 'your-access-id'
    ACCESS_KEY = 'your-access-key';

CREATE EXTERNAL VOLUME orders_vol
    LOCATION 'oss://my-bucket/orders_incoming/'
    USING CONNECTION my_oss_conn
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
    RECURSIVE = TRUE;

-- Step 2: Create the target table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT,
    amount   DECIMAL(10,2),
    status   STRING
);

-- Step 3: Create the Pipe
CREATE PIPE orders_oss_pipe
    VIRTUAL_CLUSTER = 'default'
    INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO orders
FROM VOLUME orders_vol (order_id INT, amount DECIMAL(10,2), status STRING)
USING CSV OPTIONS('header' = 'true')
PURGE = TRUE;
```

**Deduplication mechanism**: Pipe uses `load_history` to record the file paths already ingested. A file at the same path is only ingested once — re-uploading the same file will not trigger a duplicate ingestion. Records are retained for 7 days.

```sql
-- View ingested file records
SELECT * FROM load_history('orders');
-- Returns: file_path, last_copy_time, file_size, status, first_error_message
```

### Kafka Pipe

Creates a persistent consumer group that continuously pulls data from a Kafka topic in batches and writes it to a table.

> ⚠️ **Note**: A single Pipe can only consume one Kafka topic. Multiple Pipes consuming the same topic must use different `group_id` values.

```sql
CREATE PIPE kafka_orders_pipe
    VIRTUAL_CLUSTER = 'default'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO orders_raw
FROM (
    SELECT CAST(value AS STRING) AS raw_msg
    FROM TABLE(READ_KAFKA(
        'kafka-host:9092',    -- bootstrap.servers; 2–3 broker addresses are sufficient
        'orders_topic',       -- topic name
        '',                   -- topic pattern (not yet supported; leave empty)
        'pipe_orders_group',  -- group_id; must be unique across Pipes consuming the same topic
        '', '', '', '',       -- start/end offsets and timestamps; managed by Pipe, leave empty
        'raw', 'raw',         -- key/value format
        0, map()              -- max error count, extra Kafka config (e.g., SSL/SASL)
    ))
);
```

## Kafka Pipe Parameters

| Parameter | Required | Default | Description |
|------|------|--------|------|
| `VIRTUAL_CLUSTER` | Yes | — | Compute cluster for executing COPY jobs |
| `INITIAL_DELAY_IN_SECONDS` | No | 0 | Delay before the first job is scheduled (seconds) |
| `BATCH_INTERVAL_IN_SECONDS` | No | 60 | Batch processing interval (seconds) |
| `BATCH_SIZE_PER_KAFKA_PARTITION` | No | 500000 | Maximum messages per Kafka partition per batch |
| `MAX_SKIP_BATCH_COUNT_ON_ERROR` | No | 30 | Maximum number of batches to skip on error |
| `RESET_KAFKA_GROUP_OFFSETS` | No | none | Initial Kafka offset on startup. Options: `none` (no action), `valid` (reset expired offsets), `earliest`, `latest`, `${TIMESTAMP_MILLISECONDS}` |
| `COPY_JOB_HINT` | No | — | Reserved parameter. Supports `IGNORE_TMP_FILE` (default `true`), which filters files starting with `.` or `_temporary` |

## load_history Function

View the COPY job file ingestion history for a table. Records are retained for 7 days. Pipe uses `load_history` to avoid re-ingesting the same files.

```SQL
-- View ingested file records
SELECT * FROM load_history('schema_name.table_name');
-- Returns: file_path, last_copy_time, file_size, status, first_error_message
```

## ALTER PIPE Syntax

Only one property can be modified per statement. Run multiple statements to modify multiple properties:

```SQL
ALTER PIPE pipe_name SET
    [VIRTUAL_CLUSTER = 'vc_name']
    | [BATCH_INTERVAL_IN_SECONDS = '60']
    | [BATCH_SIZE_PER_KAFKA_PARTITION = '500000']
    | [MAX_SKIP_BATCH_COUNT_ON_ERROR = '30']
    | [COPY_JOB_HINT = '{"cz.mapper.kafka.message.size": "2000000"}'];
```

## DESC PIPE Field Reference

`DESC PIPE` returns key-value format output. Key fields:

| Field | Description |
|------|------|
| `pipe_status` | `RUNNING` / `PAUSED` / `INVALID` |
| `pipe_kind` | `VOLUME` (object storage) or `KAFKA` |
| `properties` | Shows `ingest_mode` and `virtual_cluster` configuration |
| `input_name` | Data source, in the format `volume:catalog.schema.volume_name` or `kafka_table_stream:workspace.schema.stream` |
| `output_name` | Target table full path `catalog.schema.table` |
| `invalid_reason` | Error reason when the Pipe is in an invalid state; empty when normal |
| `pipe_latency` | Kafka Pipe consumption lag (`offsetLag` of 0 means no backlog) |

```
DESC PIPE EXTENDED kafka_pipe_stream;
+--------------------+-----------------------------------------------------+
|     info_name      |                     info_value                      |
+--------------------+-----------------------------------------------------+
| name               | kafka_pipe_stream                                   |
| pipe_status        | RUNNING                                             |
| pipe_kind          | KAFKA                                               |
| input_name         | kafka_table_stream:workspace.pipe_schema.stream1    |
| output_name        | workspace.pipe_schema.sink_table                    |
| invalid_reason     |                                                     |
| pipe_latency       | {"kafka":{"lags":{"0":0},"offsetLag":0}}            |
+--------------------+-----------------------------------------------------+
```

## Constraints and Limitations

- Object storage Pipe: the COPY statement does not support `FILES`, `REGEXP`, or `SUBDIRECTORY` parameters
- Object storage Pipe: each Pipe corresponds to a dedicated Volume; different Pipes cannot share the same Volume
- Kafka Pipe: a single Pipe can only contain one `READ_KAFKA` function
- The `COPY` statement cannot be modified after creation; to change the ingestion logic, drop the Pipe and recreate it

```sql
-- List all Pipes (including status, type, VCluster)
SHOW PIPES;

-- View Pipe details (key-value format, including pipe_status, input_name, output_name, etc.)
DESC PIPE orders_oss_pipe;

-- Immediately trigger a scan (without waiting for the next detection cycle)
ALTER PIPE orders_oss_pipe REFRESH;

-- Pause a Pipe
ALTER PIPE orders_oss_pipe SET PIPE_EXECUTION_PAUSED = TRUE;

-- Resume a Pipe
ALTER PIPE orders_oss_pipe SET PIPE_EXECUTION_PAUSED = FALSE;

-- Drop a Pipe (does not affect target table data)
DROP PIPE orders_oss_pipe;
```

`DESC PIPE` key field reference:

| Field | Description |
|------|------|
| `pipe_status` | `RUNNING` / `PAUSED` |
| `pipe_kind` | `VOLUME` (object storage) or `KAFKA` |
| `properties` | Shows `ingest_mode` and `virtual_cluster` configuration |
| `input_name` | Data source, in the format `volume:catalog.schema.volume_name` |
| `output_name` | Target table full path `catalog.schema.table` |
| `invalid_reason` | Error reason when the Pipe is in an invalid state; empty when normal |

To view Pipe execution history: filter job history by `query_tag` in the format `pipe.workspace_name.schema_name.pipe_name`.

## Important Notes

- **Volume cannot point to the bucket root path**: `LOCATION` must be a subdirectory; otherwise Pipe creation will fail
- **Each Pipe requires a dedicated Volume**: different Pipes cannot share the same Volume
- **COPY statement cannot be modified**: to change the ingestion logic, drop the Pipe and recreate it
- **Data loading order is not strictly guaranteed**
- **Recommended file sizes**: gzip-compressed files should be under 50 MB; uncompressed CSV/Parquet files should be 128 MB–256 MB

## Related Documentation

- [Pipe Overview](pipe-introduction.md) — How it works and applicable scenarios
- [Object Storage Pipe](pipe-storage-object.md) — Complete EVENT_NOTIFICATION mode configuration
- [Kafka Pipe](pipe-kafka.md) — READ_KAFKA parameter reference, offset management
- [Pipe Syntax Reference](pipe-syntax.md) — Complete DDL syntax
- [Data Pipelines and Change Capture](pipe-overview.md) — Scenario selection and operation workflows
