# CREATE PIPE

Creates a Pipe object for continuously importing data from object storage or Kafka into the Lakehouse.

## Import Data from Object Storage

```SQL
CREATE PIPE [IF NOT EXISTS] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    INGEST_MODE = 'LIST_PURGE' | 'EVENT_NOTIFICATION'
    [COPY_JOB_HINT = '']
AS <copy_statement>;
```

**Parameter Description:**

| Parameter | Required | Description |
|------|------|------|
| `pipe_name` | Yes | Name of the Pipe object |
| `VIRTUAL_CLUSTER` | Yes | The name of the compute cluster used to execute COPY jobs |
| `INGEST_MODE` | Yes | Data ingestion mode: `LIST_PURGE` (polling scan) or `EVENT_NOTIFICATION` (event notification trigger) |
| `COPY_JOB_HINT` | No | Lakehouse reserved parameter. Supports `IGNORE_TMP_FILE` (value `true`\|`false`, default `true`), used to filter files or directories starting with `.` or `_temporary` |
| `copy_statement` | Yes | A standard `COPY INTO` statement. Supports the `ON_ERROR=CONTINUE\|ABORT` parameter to control error handling strategy |

**Usage Restrictions:**

- COPY statements in a Pipe do not support the `FILES`, `REGEXP`, or `SUBDIRECTORY` parameters.
- Each Pipe must correspond to an independent Volume and cannot be reused.

## Import Data from Kafka

```SQL
CREATE PIPE [IF NOT EXISTS] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    [INITIAL_DELAY_IN_SECONDS = '']
    [BATCH_INTERVAL_IN_SECONDS = '']
    [BATCH_SIZE_PER_KAFKA_PARTITION = '']
    [MAX_SKIP_BATCH_COUNT_ON_ERROR = '']
    [RESET_KAFKA_GROUP_OFFSETS = '']
    [COPY_JOB_HINT = '']
AS <copy_statement>;
```

**Parameter Description:**

| Parameter | Required | Default | Description |
|------|------|--------|------|
| `VIRTUAL_CLUSTER` | Yes | -- | The name of the compute cluster used to execute COPY jobs |
| `INITIAL_DELAY_IN_SECONDS` | No | 0 | Delay in seconds before the first job is scheduled |
| `BATCH_INTERVAL_IN_SECONDS` | No | 60 | Batch processing interval in seconds |
| `BATCH_SIZE_PER_KAFKA_PARTITION` | No | 500000 | Maximum number of messages per batch per Kafka partition |
| `MAX_SKIP_BATCH_COUNT_ON_ERROR` | No | 30 | Maximum number of retries to skip a batch on error |
| `RESET_KAFKA_GROUP_OFFSETS` | No | none | Initial Kafka offset position when starting the Pipe. Options: `none` (no action), `valid` (reset expired offsets), `earliest`, `latest`, `${TIMESTAMP_MILLISECONDS}` |

## Related Documents

- [Pipe Full Syntax Reference](pipe-syntax.md)
- [Continuously Import Object Storage Data Using Pipe](pipe-storage-object.md)
- [Continuously Import Kafka Data Using read_kafka](pipe-kafka.md)
- [Continuous Data Ingestion](SQL_Pipe_Guide.md): Full usage scenarios for Pipe, including OSS file scanning, Kafka consumption, and error handling strategies
