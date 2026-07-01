# Using Table Stream and Pipe to Import Kafka Data into Lakehouse

## 1. Background

In big data processing, efficiently ingesting streaming data from Kafka into a Lakehouse is a common requirement. Singdata Lakehouse provides powerful Table Stream and Pipe functionality that makes this process simpler and more efficient. This article describes how to use Table Stream and Pipe to import Kafka data into the Lakehouse, covering the complete process of creating a Kafka external table and a Kafka Table Stream.

## 2. Steps

### Create a Kafka External Table

Before using Table Stream and Pipe, create an [external table integrated with Kafka](create-kafka-external.md) to access data in Kafka.

```sql
CREATE STORAGE CONNECTION pipe_kafka
 TYPE kafka 
BOOTSTRAP_SERVERS = ['47.00.08.62:9092'] 
SECURITY_PROTOCOL = 'PLAINTEXT';

CREATE EXTERNAL TABLE external_table_kafka (   
 key_column binary,   
 value_column binary NOT NULL)
USING kafka
OPTIONS (   'group_id' = 'external_table_lh',    'topics' = 'my_topic')
CONNECTION pipe_kafka;
```

### Create a Table Stream

[Create a Table Stream](create-table-stream.md) on the Kafka external table to capture real-time data changes from Kafka.

```sql
CREATE TABLE STREAM kafka_table_stream_pipe1 
ON TABLE external_table_kafka
WITH PROPERTIES (
    'table_stream_mode' = 'append_only'

);
```

* `kafka_table_stream_pipe1`: Name of the Table Stream.
* `ON TABLE external_table_kafka`: Specifies that the Table Stream is created based on the previously created Kafka external table.
* `table_stream_mode='append_only'`: Sets the mode to append-only, meaning only newly added data rows are captured.

After creation, verify the data in the Table Stream with the following query:

```sql
SELECT CAST(value AS STRING) FROM kafka_table_stream_pipe1;
```

This query converts the `value` field in the Table Stream to a string type and returns it for subsequent processing.

### Create a Target Table

Create a target table to store data imported from Kafka.

```sql
CREATE TABLE kafka_sink_table_1 (
    a TIMESTAMP,
    b STRING
);
```

* `kafka_sink_table_1`: Name of the target table.
* `a TIMESTAMP`: First field for storing timestamp data.
* `b STRING`: Second field for storing string data.

### Create a Pipe

Use a Pipe to continuously import data from the Table Stream into the target table.

```sql
CREATE PIPE kafka_pipe_stream
VIRTUAL_CLUSTER = 'test_alter'
AS
COPY INTO kafka_sink_table_1
FROM (
    SELECT CURRENT_TIMESTAMP(), CAST(value AS STRING) FROM kafka_table_stream_pipe1
);
```

* `kafka_pipe_stream`: Name of the Pipe.
* `VIRTUAL_CLUSTER = 'test_alter'`: Specifies the Virtual Cluster to use.
* `COPY INTO kafka_sink_table_1`: Copies data into the target table `kafka_sink_table_1`.
* `SELECT CURRENT_TIMESTAMP(), CAST(value AS STRING) FROM kafka_table_stream_pipe1`: Selects data from the Table Stream, using the current timestamp and the converted `value` field as the two columns for the target table.

Other configurable properties:
- `INITIAL_DELAY_IN_SECONDS`: Initial job scheduling delay (optional, default 0 seconds)
- `BATCH_INTERVAL_IN_SECONDS`: (Optional) Batch processing interval, default 60 seconds.
- `BATCH_SIZE_PER_KAFKA_PARTITION`: (Optional) Batch size per Kafka partition, default 500,000 records.
- `MAX_SKIP_BATCH_COUNT_ON_ERROR`: (Optional) Maximum number of batches to skip on error, default 30.
- `RESET_KAFKA_GROUP_OFFSETS`: (Optional) Initial Kafka offset when starting the Pipe. Cannot be modified after creation. Possible values: `latest`, `earliest`, `none`, `valid`, `${TIMESTAMP_MILLISECONDS}`
    - `none`: No action (default)
    - `valid`: Checks if the current group offset is expired and resets expired partition offsets to the current earliest
    - `earliest`: Resets to the current earliest
    - `latest`: Resets to the current latest
    - `${TIMESTAMP_MILLISECONDS}`: Resets to the offset corresponding to the millisecond timestamp, e.g., `1737789688000` (2025-01-25 15:21:28)

## 3. Verify Results

Verify whether data has been successfully imported by querying the target table:

```sql
SELECT * FROM kafka_sink_table_1;
```

Check the running status of the Pipe to ensure it is working properly:

```sql
SHOW PIPES;
```

This command lists all created Pipes and their status information, including whether they are running and the last run time.

## 4. Status Monitoring and Management

### Check Kafka Consumption Latency

Use the `DESC PIPE` command. The JSON string in `pipe_latency` contains the following fields:
- `lastConsumeTimestamp`: The last consumed offset timestamp
- `offsetLag`: The backlog of Kafka data
- `timeLag`: Consumption latency, calculated as the current time minus the last consumed offset timestamp. When Kafka consumption is abnormal, the value is -1


````
DESC PIPE EXTENDED kafka_pipe_stream
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|     info_name      |                                                                                                               info_value                                                            |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name               | kafka_pipe_stream                                                                                                                                                                   |
| creator            | UAT_TEST                                                                                                                                                                            |
| created_time       | 2025-03-05 10:40:55.405                                                                                                                                                             |
| last_modified_time | 2025-03-05 10:40:55.405                                                                                                                                                             |
| comment            |                                                                                                                                                                                     |
| properties         | ((virtual_cluster,test_alter))                                                                                                                                                      |
| copy_statement     | COPY INTO TABLE qingyun.pipe_schema.kafka_sink_table_1 FROM (SELECT `current_timestamp`() AS ```current_timestamp``()`, CAST(kafka_table_stream_pipe1.`value` AS string) AS `value` |
| pipe_status        | RUNNING                                                                                                                                                                             |
| output_name        | xxxxxxx.pipe_schema.kafka_sink_table_1                                                                                                                                              |
| input_name         | kafka_table_stream:xxxxxxx.pipe_schema.kafka_table_stream_pipe1                                                                                                                     |
| invalid_reason     |                                                                                                                                                                                     |
| pipe_latency       | {"kafka":{"lags":{"0":0,"1":0,"2":0,"3":0},"lastConsumeTimestamp":-1,"offsetLag":0,"timeLag":-1}}                                                                                   |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

````

### View Pipe Execution History

Since each Pipe execution is a COPY operation, you can view all operations in the job history. Filter by `query_tag` in [Job History](<web-job-history.md>). All Pipe COPY jobs are tagged in the format `pipe.``workspace_name``.schema_name.pipe_name` for easy tracking.

### Stop and Start a Pipe

- Pause a Pipe:
```
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = true;
```
- Resume a Pipe:
```
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = false;
```

### Modify Pipe Properties

You can modify Pipe properties one at a time. If multiple properties need to be changed, run the `ALTER` command multiple times. Below are the modifiable properties and their syntax:

```SQL
ALTER PIPE pipe_name SET 
    [VIRTUAL_CLUSTER = 'virtual_cluster_name'],
    [BATCH_INTERVAL_IN_SECONDS=''],
    [BATCH_SIZE_PER_KAFKA_PARTITION=''],
    [MAX_SKIP_BATCH_COUNT_ON_ERROR=''],
    [COPY_JOB_HINT='']
```

Examples:
```
-- Modify the Virtual Cluster
ALTER PIPE pipe_name SET VIRTUAL_CLUSTER = 'DEFAULT'
-- Set COPY_JOB_HINT
ALTER PIPE pipe_name SET COPY_JOB_HINT='{"cz.mapper.kafka.message.size": "2000000"}'

```

**Notes**
- Modifying the COPY statement logic is not supported. If you need to modify it, delete the Pipe and recreate it.
- When modifying the `COPY_JOB_HINT` of a Pipe, the new settings will overwrite all existing hints. If your Pipe already has hints such as `{"cz.sql.split.kafka.strategy":"size"}`, you must include all required hints together when setting new ones; otherwise existing hints will be overwritten. Separate multiple parameters with commas.
