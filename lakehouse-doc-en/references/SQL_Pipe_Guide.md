# Lakehouse Continuous Data Ingestion Guide (Pipe)

## Overview

Pipe is Singdata Lakehouse's continuous data ingestion pipeline, supporting automatic and continuous data ingestion from Kafka or object storage (OSS/S3/COS) into Lakehouse tables. There is no need to manually configure scheduling tasks -- Pipe maintains consumption offsets and runs continuously. This guide is organized by business scenario to help you quickly master Pipe creation and monitoring methods.

### Quick Navigation

* [Create Kafka Pipe](#create-kafka-pipe) -- Continuously import data from Kafka topics
* [Create OSS Pipe](#create-oss-pipe) -- Continuously import files from object storage
* [Check Pipe Status](#check-pipe-status) -- Monitor pipeline running status
* [Manual Trigger Execution](#manual-trigger-execution) -- Execute a data import immediately
* [Drop Pipe](#drop-pipe) -- Clean up pipelines that are no longer needed

***

## Related SQL Commands

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `CREATE PIPE ... AS COPY INTO ... FROM READ_KAFKA(...)` | Create a Kafka pipeline | Real-time logs, message queue ingestion |
| `CREATE PIPE ... AS COPY INTO ... FROM VOLUME ...` | Create a Volume pipeline | Continuous object storage file import |
| `SHOW PIPES` | View pipeline list | Monitor Pipe status |
| `DESC PIPE` | View pipeline details | Check configuration and runtime information |
| `DROP PIPE` | Drop a pipeline | Clean up unused pipelines |

***

## Prerequisites

The following examples use simulated Kafka topics and Volume paths:

```sql
-- Create target table (Kafka import)
CREATE TABLE IF NOT EXISTS kafka_logs (
    log_time TIMESTAMP,
    level STRING,
    message STRING
);

-- Create target table (Volume import)
CREATE TABLE IF NOT EXISTS oss_data (
    id INT,
    value STRING
);
```

***

## Create Kafka Pipe

Use `CREATE PIPE` with the `READ_KAFKA` function to define the logic for continuous Kafka import.

```sql
-- Create Kafka Pipe
CREATE PIPE pipe_kafka_logs
    VIRTUAL_CLUSTER = 'default'
    BATCH_INTERVAL_IN_SECONDS = '30'
AS
COPY INTO kafka_logs
FROM (
    SELECT 
        CAST(PARSE_JSON(VALUE::STRING)['time'] AS TIMESTAMP) as log_time,
        PARSE_JSON(VALUE::STRING)['level']::STRING as level,
        PARSE_JSON(VALUE::STRING)['message']::STRING as message
    FROM READ_KAFKA(
        'kafka-broker:9092',      -- bootstrap_servers
        'app_logs',               -- topic
        '',                       -- topic_prefix
        'lakehouse_consumer',     -- group_id
        '', '', '', '',           -- offset parameters (Pipe manages automatically)
        'raw', 'raw',             -- key/value format
        0,                        -- max_errors
        map()                     -- kafka_configs
    )
);
```

**Parameter Description**:
* `BATCH_INTERVAL_IN_SECONDS`: Executes a batch import every 30 seconds.
* The offset parameters in `READ_KAFKA` are left empty, and Pipe automatically manages consumption offsets.

***

## Create OSS Pipe

Use `CREATE PIPE` with a Volume to define the logic for continuous object storage file import.

```sql
-- Create OSS Pipe
CREATE PIPE pipe_oss_data
    VIRTUAL_CLUSTER = 'default'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO oss_data
FROM VOLUME my_oss_volume
USING CSV OPTIONS ('header' = 'true');
```

**Operating Modes**:
* **LIST_PURGE** (default): Scans files in the Volume and auto-deletes them after import.
* **LIST**: Scans and imports, but preserves the source files.

***

## Check Pipe Status

Use `SHOW PIPES` to view the running status of all Pipes.

```sql
-- View Pipe list
SHOW PIPES LIKE 'pipe_kafka_logs';
```

**Key Field Description**:
* `status`: Running status (RUNNING / SUSPENDED / FAILED)
* `pipe_kind`: Pipeline type (READ_KAFKA / VOLUME)
* `copy_statement`: The underlying COPY INTO statement

***

## Manual Trigger Execution

Pipes run automatically based on `BATCH_INTERVAL_IN_SECONDS` by default, but can also be triggered manually via `ALTER PIPE`.

```sql
-- Immediately execute a data import
ALTER PIPE pipe_kafka_logs EXECUTE;
```

> 💡 **Tip**: Manual triggering is suitable for debugging or backfill scenarios and does not affect the automatic scheduling cycle.

***

## Drop Pipe

Use `DROP PIPE` to delete pipelines that are no longer needed.

```sql
-- Drop Pipe
DROP PIPE pipe_kafka_logs;
```

> 💡 **Tip**: Dropping a Pipe does not delete data that has already been imported into the target table.

***

## Clean Up Test Data

After verifying the Pipe, it is recommended to clean up the test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS kafka_logs;
DROP TABLE IF EXISTS oss_data;
DROP PIPE IF EXISTS pipe_kafka_logs;
DROP PIPE IF EXISTS pipe_oss_data;
```

> 💡 **Tip**: The Lakehouse supports `UNDROP TABLE`, so accidentally dropped tables can be restored within the retention period.

***

## Notes

1. **Consumption Offset Management**: Kafka Pipes automatically manage consumer group offsets. After restarts or failure recovery, consumption resumes from the last offset.
2. **Error Handling**: Use the `max_errors` parameter to control the tolerated number of erroneous records. If the threshold is exceeded, the Pipe will pause and report an error.
3. **VCluster Selection**: It is recommended to use an `INTEGRATION` or `GENERAL` type VCluster to run Pipes.
4. **Permission Requirements**: Creating a Pipe requires `INSERT` permission on the target table and read permission on Kafka/Volume.
5. **Idempotency**: Pipes guarantee at-least-once semantics by default. It is recommended to design a primary key for the target table or use `MERGE INTO` for deduplication.

***

## Related Documents

* [Pipe Introduction](pipe-summary.md)
* [CREATE PIPE](create-pipe.md)
* [READ_KAFKA Function](sql_functions/table_functions/read_kafka.md)
