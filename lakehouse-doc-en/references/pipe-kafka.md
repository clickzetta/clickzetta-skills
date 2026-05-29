# Continuous Data Import from Kafka Using Pipe

## Kafka Pipe Syntax

```SQL
-- Syntax for creating a Pipe from Kafka
CREATE PIPE [ IF NOT EXISTS ] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    [BATCH_INTERVAL_IN_SECONDS='']
   [ BATCH_SIZE_PER_KAFKA_PARTITION='']
    [MAX_SKIP_BATCH_COUNT_ON_ERROR='']
    [RESET_KAFKA_GROUP_OFFSETS='']
    [COPY_JOB_HINT='']
AS <copy_statement>;
```

* `<pipe_name>`: The name of the Pipe object you want to create.
* `VIRTUAL_CLUSTER`: Specify the name of the virtual cluster.
* `BATCH_INTERVAL_IN_SECONDS`: (Optional) Set the batch interval time, default is 60 seconds.
* `BATCH_SIZE_PER_KAFKA_PARTITION`: (Optional) Set the batch size per Kafka partition, default is 500,000 records.
* `MAX_SKIP_BATCH_COUNT_ON_ERROR`: (Optional) Set the maximum retry count for skipped batches on error, default is 30.
- `RESET_KAFKA_GROUP_OFFSETS`: (Optional) Sets the initial offset for Kafka when starting the pipe. This property cannot be modified after the pipe is created. Possible values are `latest`, `earliest`, `none`, `valid`, and `${TIMESTAMP_MILLISECONDS}`.
    - `none`: No action by default.
    - `valid`: Checks if the current offset in the group is expired and resets expired partitions to the current earliest offset.
    - `earliest`: Resets to the current earliest offset.
    - `latest`: Resets to the current latest offset.
    - `${TIMESTAMP_MILLISECONDS}`: Resets to the offset corresponding to the millisecond timestamp, for example, `'1737789688000'` (which corresponds to January 25, 2025, 15:21:28).

## Usage Example

```SQL
/*Use Lakehouse Pipe task object to continuously import Kafka data into the target table*/
---Step01: Create the target table for Kafka writes
create table kafka_raw(value string);

---Step02: Create PIPE task to read from Kafka and write to the target table
CREATE PIPE  load_kafka01
VIRTUAL_CLUSTER = 'DEFAULT' 
BATCH_INTERVAL_IN_SECONDS = '10'
AS
COPY INTO kafka_raw
FROM (
        SELECT
                CAST(value AS string) as value
        FROM 
        read_kafka (
        'host01:9092,host02:9092,host03:9092',-- bootstrap
        'test',-- topic name
        '', -- topic prefix not supported yet
        'pipe_kafka_group',-- group id
        '',-- Point-related parameters, leave blank in pipe ddl
        '',-- Point-related parameters, leave blank in pipe ddl
        '',-- Point-related parameters, leave blank in pipe ddl
        '',-- Point-related parameters, leave blank in pipe ddl
        'raw',-- format of key, currently only supports binary
        'raw',-- format of value, currently only supports binary
        0,
        map()
        )
);
---Step03: View and manage PIPE objects
--View pipe list
show pipes;

pipe_name    copy_statement                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
-----             ------ 
load_kafka01 COPY INTO TABLE ur_ws.public.kafka_raw FROM (SELECT CAST(read_kafka.`value` AS string) AS `value` FROM READ_KAFKA('host01:9092,host02:9092,host03:9092', 'mytopic', '', 'pipe_kafka_group', '', '', '', '', 'raw', 'raw', 0) read_kafka) 

--View pipe object details
desc pipe load_kafka01;
info_name          info_value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
--                        ------- 
name               load_kafka01                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
creator            czuser                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
created_time       2024-06-08 23:11:16.079                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
last_modified_time 2024-06-08 23:11:16.079                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
comment            my first pipe                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
properties         ((batch_interval_in_seconds,10),(virtual_cluster,DEFAULT))                                                                                                                                                                                                                                                                                                                                                                                                                                             
copy_statement     COPY INTO TABLE ql_ws.rc5_l.kafka_raw FROM (SELECT CAST(read_kafka.`value` AS string) AS `value` FROM READ_KAFKA('host01:9092,host02:9092,host03:9092', 'mytopic', '', 'pipe_kafka_group', '', '', '', '', 'raw', 'raw', 0) read_kafka)                 
copy_template      PCF1______::COPY INTO TABLE ql_ws.rc5_l.kafka_raw FROM (SELECT CAST(read_kafka.`value` AS string) AS `value` FROM READ_KAFKA('host01:9092,host02:9092,host03:9092', 'mytopic', '', 'pipe_kafka_group', PCF1______, '', '', 'raw', 'raw', 0) read_kafka) 
pipe_status        PTS_RUNNING                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
invalid_reason                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            

--View imported data
SELECT * FROM kafka_raw LIMIT 100;

--Delete PIPE task object
DROP PIPE load_kafka01;
```

## Function: read\_kafka

> Note: This function is currently in preview release

## Function Description

Read data from an Apache Kafka cluster and return the data in tabular form.

## Function Syntax

```SQL
read_kafka (
    <bootstrapServers>,
    <topic>,
    <topic_prefix>,
    <group_id>,
    <STARTING_OFFSETS>,
    <ENDING_OFFSETS>,
    <STARTING_OFFSETS_TIMESTAMP>,
    <ENDING_OFFSETS_TIMESTAMP>,
    <KEY_FORMAT>,
    <VALUE_FORMAT>,
    <MAX_ERROR_NUMBER>,
    <kafka_parameters>
)
```

## Parameter Description

* bootstrap: Comma-separated Kafka broker server addresses, such as `1.2.3.1:9092,1.2.3.2:9092`.
* topic: Kafka topic name, multiple topics separated by commas, such as `topicA,topicB`.
* topic\_pattern: Topic regex, not supported yet, leave it empty by default. For example: ''.
* group\_id: Kafka consumer group ID.
* STARTING\_OFFSETS: Specifies the starting offset to read from, default is `latest`. This parameter does not need to be passed in the pipe.
* ENDING\_OFFSETS: Specifies the ending offset, default is `latest`. This parameter does not need to be passed in the pipe.
* STARTING\_OFFSETS\_TIMESTAMP: Specifies the timestamp for the starting offset. This parameter does not need to be passed in the pipe.
* ENDING\_OFFSETS\_TIMESTAMP: Specifies the timestamp for the ending offset. This parameter does not need to be passed in the pipe.
* KEY\_FORMAT: Specifies the format of the key to read, case-insensitive STRING type. Currently, only raw format is supported.
* VALUE\_FORMAT: Specifies the format of the value to read, case-insensitive STRING type. Currently, only raw format is supported.
* MAX\_ERROR\_NUMBER: The maximum number of allowed error rows within the reading window. Must be greater than or equal to 0. The default is 0, which means no error rows are allowed, with a range of 0-100000.
* kafka\_parameters: Parameters to be passed to Kafka, prefixed with kafka., directly using Kafka's parameters. These options can be found in Kafka. The format is like MAP('kafka.security.protocol', 'PLAINTEXT', 'kafka.auto.offset.reset', 'latest'). For values, refer to the [Kafka documentation](https://kafka.apache.org/documentation/#consumerconfigs).

## Return Values

| Field           | Meaning                      | Type                 |
| --------------- | ---------------------------- | -------------------- |
| topic           | Kafka topic name             | STRING               |
| partition       | Data partition ID            | INT                  |
| offset          | Offset in Kafka partition    | BIGINT               |
| timestamp       | Kafka message timestamp      | TIMESTAMP\_LTZ       |
| timestamp\_type | Kafka message timestamp type | STRING               |
| headers         | Kafka message headers        | MAP\<STRING, BINARY> |
| key             | Kafka key value              | BINARY               |
| value           | Kafka value                  | BINARY               |


## Status Monitoring and Management

### Viewing Kafka Consumption Latency

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

Since each Pipe execution triggers a copy operation, you can view all operations in the job history. Use the `query_tag` in the [Job History](web-job-history.md) to filter. All Pipe copy jobs are tagged in the format `pipe.``workspace_name``.schema_name.pipe_name`, making it easy to track and manage.

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

You can modify the properties of a Pipe, but only one property at a time. If multiple properties need to be modified, execute the `ALTER` command multiple times. Below are the modifiable properties and their syntax:

```sql
ALTER PIPE pipe_name SET 
   [VIRTUAL_CLUSTER = 'virtual_cluster_name'],
    [BATCH_INTERVAL_IN_SECONDS=''],
   [ BATCH_SIZE_PER_KAFKA_PARTITION=''],
    [MAX_SKIP_BATCH_COUNT_ON_ERROR=''],
    [RESET_KAFKA_GROUP_OFFSETS=''],
    [COPY_JOB_HINT='']
```

Examples:
```sql
-- Modify the compute cluster
ALTER PIPE pipe_name SET VIRTUAL_CLUSTER = 'default';

-- Set COPY_JOB_HINT
ALTER PIPE pipe_name SET copy_hints='{"cz.mapper.kafka.message.size": "2000000"}';
```

**Note**
- Modifying the logic of the COPY statement is not supported. If you need to modify it, delete the Pipe and recreate it.
- When modifying the `COPY_JOB_HINT` of a Pipe, the new settings will overwrite existing hints. Therefore, if your Pipe already has hints (e.g., `{"cz.sql.split.kafka.strategy":"size"}`), you must set all required hints together when adding new ones; otherwise, the existing hints will be overwritten by the new settings. Separate multiple parameters with commas.