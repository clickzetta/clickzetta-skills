# Using Table Stream and Pipe to Import Kafka Data into Lakehouse

## 1. Background Introduction

In the field of big data processing, efficiently importing streaming data from Kafka into a Lakehouse (data lake warehouse) is a common requirement. CloudTech provides powerful Table Stream and Pipe functionalities that simplify and enhance this process. This article will detail how to use Table Stream and Pipe to import Kafka data into a Lakehouse, including the complete process of creating a Kafka external table and a Kafka Table Stream.

## 2. Operational Steps

### Creating a Kafka External Table

Before using Table Stream and Pipe, we need to create an external table integrated with Kafka to access data in Kafka.

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

### Creating a Table Stream

Create a Table Stream on the Kafka external table to capture real-time data changes in Kafka.

```sql
CREATE TABLE STREAM kafka_table_stream_pipe1 
ON TABLE external_table_kafka
WITH PROPERTIES (
    'table_stream_mode' = 'append_only'
);
```

- `kafka_table_stream_pipe1`: Name of the Table Stream.
- `ON TABLE external_table_kafka`: Specifies that the Table Stream is created based on the previously created Kafka external table.
- `table_stream_mode='append_only'`: Sets the mode of the Table Stream to append-only, meaning it will only capture newly added data rows.

After creation, you can verify the data in the Table Stream with the following query:

```sql
SELECT CAST(value AS STRING) FROM kafka_table_stream_pipe1;
```

This query converts the `value` field in the Table Stream to a string type and returns it for subsequent processing.

### Creating a Target Table

Next, create a target table to store data imported from Kafka.

```sql
CREATE TABLE kafak_sink_table_1 (
    a TIMESTAMP,
    b STRING
);
```

- `kafak_sink_table_1`: Name of the target table.
- `a TIMESTAMP`: First field for storing timestamp data.
- `b STRING`: Second field for storing string data.

### Creating a Pipe

Finally, use a Pipe to continuously import data from the Table Stream into the target table.

```sql
CREATE PIPE kafka_pipe_stream
VIRTUAL_CLUSTER = 'test_alter'
AS
COPY INTO kafak_sink_table_1
FROM (
    SELECT CURRENT_TIMESTAMP(), CAST(value AS STRING) FROM kafka_table_stream_pipe1
);
```

- `kafka_pipe_stream`: Name of the Pipe.
- `VIRTUAL_CLUSTER = 'test_alter'`: Specifies the virtual cluster to use.
- `COPY INTO kafak_sink_table_1`: Copies data into the target table `kafak_sink_table_1`.
- `SELECT CURRENT_TIMESTAMP(), CAST(value AS STRING) FROM kafka_table_stream_pipe1`: Selects data from the Table Stream, using the current timestamp and the converted `value` field as the two columns for the target table.

Other Configurable Properties:
- `INITIAL_DELAY_IN_SECONDS`: Initial job scheduling delay (optional, default 0 seconds)
- `BATCH_INTERVAL_IN_SECONDS`: (Optional) Sets the batch processing interval, default 60 seconds.
- `BATCH_SIZE_PER_KAFKA_PARTITION`: (Optional) Sets the batch size per Kafka partition, default 500,000 records.
- `MAX_SKIP_BATCH_COUNT_ON_ERROR`: (Optional) Sets the maximum number of batches to skip on error, default 30.
- `RESET_KAFKA_GROUP_OFFSETS`: (Optional) Sets the initial offset for Kafka when starting the pipe. Cannot be modified. Possible values: `latest`, `earliest`, `none`, `valid`, `${TIMESTAMP_MILLISECONDS}`
    - `none`: Default, no action.
    - `valid`: Checks if the current offset in the group is expired and resets expired partitions to the current earliest.
    - `earliest`: Resets to the current earliest.
    - `latest`: Resets to the current latest.
    - `${TIMESTAMP_MILLISECONDS}`: Resets to the offset corresponding to the millisecond timestamp, e.g., '1737789688000' (2025-01-25 15:21:28).

## 3. Verifying Results

You can verify whether the data has been successfully imported by querying the target table:

```sql
SELECT * FROM kafak_sink_table_1;
```

Additionally, check the running status of the Pipe to ensure it is functioning properly:

```sql
SHOW PIPES;
```

This command lists all created Pipes and their status information, including whether they are running and the last run time.

## 4. Status Monitoring and Management

### Checking Kafka Consumption Latency

Use the `DESC PIPE` command. For example, the JSON string in `pipe_latency` below:
- `lastConsumeTimestamp`: The last consumed offset.
- `offsetLag`: The backlog of Kafka data.
- `timeLag`: Consumption latency, calculated as the current time minus the last consumed offset. If Kafka consumption is abnormal, the value is -1.

```sql
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
| copy_statement     | COPY INTO TABLE qingyun.pipe_schema.kafak_sink_table_1 FROM (SELECT `current_timestamp`() AS ```current_timestamp``()`, CAST(kafka_table_stream_pipe1.`value` AS string) AS `value` |
| pipe_status        | RUNNING                                                                                                                                                                             |
| output_name        | xxxxxxx.pipe_schema.kafak_sink_table_1                                                                                                                                              |
| input_name         | kafka_table_stream:xxxxxxx.pipe_schema.kafka_table_stream_pipe1                                                                                                                     |
| invalid_reason     |                                                                                                                                                                                     |
| pipe_latency       | {"kafka":{"lags":{"0":0,"1":0,"2":0,"3":0},"lastConsumeTimestamp":-1,"offsetLag":0,"timeLag":-1}}                                                                                   |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

### Viewing Pipe Execution History

Since each Pipe execution is a copy operation, you can view all operations in the job history. Use the `query_tag` in the [Job History](web-job-history.md) to filter, as all Pipe copy jobs are tagged in the format `pipe.``workspace_name``.schema_name.pipe_name`, making it easy to track and manage.

### Stopping and Starting a Pipe

- Pause a Pipe:
  ```sql
  ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = true;
  ```

- Resume a Pipe:
  ```sql
  ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = false;
  ```

### Modifying Pipe Properties

You can modify Pipe properties, but only one property at a time. If multiple properties need to be modified, execute the `ALTER` command multiple times. Below are the modifiable properties and their syntax:

```sql
ALTER PIPE pipe_name SET 
   [VIRTUAL_CLUSTER = 'virtual_cluster_name'],
    [BATCH_INTERVAL_IN_SECONDS=''],
   [ BATCH_SIZE_PER_KAFKA_PARTITION=''],
    [MAX_SKIP_BATCH_COUNT_ON_ERROR=''],
    [COPY_JOB_HINT='']
```

Examples:
```sql
-- Modify compute cluster
ALTER PIPE pipe_name SET VIRTUAL_CLUSTER = 'default';

-- Set COPY_JOB_HINT
ALTER PIPE pipe_name SET copy_hints='{"cz.mapper.kafka.message.size": "2000000"}';
```

**Note**
- Modifying the COPY statement logic is not supported. If needed, delete the Pipe and recreate it.
- When modifying the `COPY_JOB_HINT` of a Pipe, the new settings will overwrite existing hints. If your Pipe already has hints (e.g., `{"cz.sql.split.kafka.strategy":"size"}`), you must set all required hints together when adding new ones; otherwise, existing hints will be overwritten. Separate multiple parameters with commas.