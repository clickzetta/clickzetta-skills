# Pipe

Pipe is the continuous data ingestion object in the Lakehouse. Once created via SQL DDL, it runs automatically, continuously reading data from object storage (OSS/COS/S3) or Kafka and writing it to a target table.

For a detailed introduction, see [Pipe Object Model](om-pipe.md).

---

## Chapter Contents

| Page | Description |
|------|-------------|
| [CREATE PIPE](create-pipe.md) | Create an object storage Pipe or Kafka Pipe |
| [ALTER PIPE](alter-pipe.md) | Pause, resume, or modify batch interval and other properties |
| [DROP PIPE](drop-pipe.md) | Drop a Pipe (does not affect target table data) |
| [SHOW PIPES](show-pipes.md) | List all Pipes in the current Schema |
| [SHOW CREATE PIPE](show-create-pipe.md) | View the creation statement of a Pipe |
| [DESC PIPE](desc-pipe.md) | View Pipe details including status, source, target, and latency |

---

## Common Operations

### Create an Object Storage Pipe

```SQL
-- LIST_PURGE mode: periodic polling, deletes source files after import
CREATE PIPE orders_pipe
    VIRTUAL_CLUSTER = 'DEFAULT'
    INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO orders FROM VOLUME orders_vol USING CSV OPTIONS('header' = 'true');
```

> ⚠️ `LIST_PURGE` mode **permanently deletes** source files from OSS after a successful import. This is irreversible. Use `EVENT_NOTIFICATION` mode if you need to retain the files.

### Create a Kafka Pipe

```SQL
CREATE PIPE kafka_orders_pipe
    VIRTUAL_CLUSTER = 'DEFAULT'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO orders_raw
FROM (
    SELECT CAST(value AS STRING) AS raw_msg
    FROM TABLE(READ_KAFKA(
        'kafka-host:9092', 'orders_topic', '',
        'pipe_orders_group', '', '', '', '',
        'raw', 'raw', 0, map()
    ))
);
```

### Pause and Resume

```SQL
-- Pause
ALTER PIPE orders_pipe SET PIPE_EXECUTION_PAUSED = TRUE;

-- Resume
ALTER PIPE orders_pipe SET PIPE_EXECUTION_PAUSED = FALSE;

-- Trigger an immediate scan
ALTER PIPE orders_pipe REFRESH;
```

### View and Drop

```SQL
-- View all Pipes
SHOW PIPES;

-- View Pipe details
DESC PIPE orders_pipe;

-- Drop a Pipe
DROP PIPE orders_pipe;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Pipe Object Model](om-pipe.md) | Core concepts, comparison of two modes, deduplication mechanism, complete parameter reference |
| [Object Storage Pipe Detailed Configuration](pipe-storage-object.md) | Complete configuration for EVENT_NOTIFICATION mode |
| [Kafka Pipe Detailed Configuration](pipe-kafka.md) | READ_KAFKA parameter reference, consumer offset management |
| [Real-time Pipeline Selection Guide](realtime-pipeline-selection-guide.md) | Comparison and selection guide for Pipe / Stream / Dynamic Table |
