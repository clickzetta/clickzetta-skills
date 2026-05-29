# Pipe Syntax

Pipe is a continuous data ingestion object that automates importing data from object storage or Kafka into the Lakehouse. This document provides a complete reference for Pipe-related SQL syntax.

## Create Pipe

### Import Data from Object Storage

```SQL
CREATE PIPE [IF NOT EXISTS] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    INGEST_MODE = 'LIST_PURGE' | 'EVENT_NOTIFICATION'
    [COPY_JOB_HINT = '']
AS <copy_statement>;
```

**Parameter Description:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `pipe_name` | Yes | Name of the Pipe object |
| `VIRTUAL_CLUSTER` | Yes | Name of the compute cluster used to execute COPY jobs |
| `INGEST_MODE` | Yes | Data ingestion mode: `LIST_PURGE` (polling scan) or `EVENT_NOTIFICATION` (event notification trigger) |
| `COPY_JOB_HINT` | No | Lakehouse reserved parameter. Supports `IGNORE_TMP_FILE` (value `true`\|`false`, default `true`), which filters files or directories starting with `.` or `_temporary` |
| `copy_statement` | Yes | A standard `COPY INTO` statement. Supports the `ON_ERROR=CONTINUE\|ABORT` parameter for error handling strategy |

**Usage Restrictions:**

- COPY statements in a Pipe do not support the `FILES`, `REGEXP`, or `SUBDIRECTORY` parameters.
- Each Pipe must correspond to an independent Volume; Volumes cannot be reused.

**Reference:** [Import Data Continuously from Object Storage Using Pipe](pipe-storage-object.md)

### Import Data from Kafka

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
|-----------|----------|---------|-------------|
| `VIRTUAL_CLUSTER` | Yes | -- | Name of the compute cluster used to execute COPY jobs |
| `INITIAL_DELAY_IN_SECONDS` | No | 0 | Initial delay in seconds before the first job is scheduled |
| `BATCH_INTERVAL_IN_SECONDS` | No | 60 | Batch interval in seconds |
| `BATCH_SIZE_PER_KAFKA_PARTITION` | No | 500000 | Maximum number of messages per batch for each Kafka partition |
| `MAX_SKIP_BATCH_COUNT_ON_ERROR` | No | 30 | Maximum number of retries when skipping batches on error |
| `RESET_KAFKA_GROUP_OFFSETS` | No | none | Initial Kafka offset when starting the Pipe. Possible values: `none` (no action), `valid` (reset expired offsets), `earliest`, `latest`, `${TIMESTAMP_MILLISECONDS}` |

**Reference:**

- [Import Kafka Data Continuously Using read_kafka](pipe-kafka.md)
- [Import Kafka Data Continuously Using Kafka Table Stream](pipe-kafka-table-stream.md)

## Pause and Resume Pipe

Control the execution state of a Pipe:

```SQL
-- Pause Pipe
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = true;

-- Resume Pipe
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = false;
```

## Modify Pipe Properties

Modify the configuration properties of a Pipe. Only one property can be modified at a time; to modify multiple properties, execute multiple `ALTER` commands.

```SQL
ALTER PIPE pipe_name SET
    [VIRTUAL_CLUSTER = 'virtual_cluster_name']
    | [BATCH_INTERVAL_IN_SECONDS = '']
    | [BATCH_SIZE_PER_KAFKA_PARTITION = '']
    | [MAX_SKIP_BATCH_COUNT_ON_ERROR = '']
    | [COPY_JOB_HINT = ''];
```

**Examples:**

```SQL
-- Modify the compute cluster
ALTER PIPE pipe_name SET VIRTUAL_CLUSTER = 'default';
-- Set COPY_JOB_HINT
ALTER PIPE pipe_name SET COPY_JOB_HINT = '{"cz.mapper.kafka.message.size": "2000000"}';
```

## View Pipe List

List all Pipe objects within the specified scope:

```SQL
-- List all Pipes in the current schema
SHOW PIPES;
-- List all Pipes in a specified schema
SHOW PIPES IN SCHEMA schema_name;
-- List all Pipes in a specified workspace
SHOW PIPES IN WORKSPACE workspace_name;
```

**Return Columns:**

| Column Name | Description |
|-------------|-------------|
| `pipe_name` | Pipe name |
| `pipe_kind` | Pipe type (object storage or Kafka) |
| `status` | Current status, e.g., `RUNNING`, `PAUSED`, `INVALID` |
| `copy_statement` | The COPY INTO statement associated with the Pipe |

## View Pipe Details

View detailed information about a specific Pipe object:

```SQL
DESC PIPE [EXTENDED] <name>;
```

**Sample Output:**

```
DESC PIPE EXTENDED kafka_pipe_stream;
+--------------------+-----------------------------------------------------+
|     info_name      |                     info_value                      |
+--------------------+-----------------------------------------------------+
| name               | kafka_pipe_stream                                   |
| creator            | UAT_TEST                                            |
| created_time       | 2025-03-05 10:40:55.405                             |
| last_modified_time | 2025-03-05 10:40:55.405                             |
| comment            |                                                     |
| properties         | ((virtual_cluster,test_alter))                      |
| copy_statement     | COPY INTO TABLE example.pipe_schema.sink_table ...  |
| pipe_status        | RUNNING                                             |
| output_name        | workspace.pipe_schema.sink_table                    |
| input_name         | kafka_table_stream:workspace.pipe_schema.stream1    |
| invalid_reason     |                                                     |
| pipe_latency       | {"kafka":{"lags":{"0":0},"offsetLag":0}}            |
+--------------------+-----------------------------------------------------+
```

## View Pipe Creation Statement

```SQL
SHOW CREATE PIPE <name>;
```

## Drop Pipe

When a Pipe object is no longer needed, use the following command to delete it:

```SQL
DROP PIPE <name>;
```

## load_history Function

**Description**: View the COPY job import file history of a table, with a retention period of 7 days. When a Pipe runs, it uses `load_history` to avoid re-importing existing files, ensuring data uniqueness.

**Syntax:**

```SQL
load_history('schema_name.table_name')
```

**Example:**

```SQL
SELECT * FROM load_history('myschema.mytable');
```

## Constraints and Limitations

- When the data source is Kafka: Only one `read_kafka` function is allowed in a Pipe.
- When the data source is object storage: Only one Volume object is allowed in a Pipe.
