# Continuous Data Collection from Kafka Using Pipe

## Overview

Pipe is the **continuous data ingestion** solution provided by the Lakehouse, designed to automatically and continuously import data from Kafka into Lakehouse tables. Pipe creates a persistent consumer group, maintains the consumption position, and runs continuously according to the configured scheduling strategy.

A Kafka Pipe is like a continuously running consumer group. You only need to define the consumption logic, and it automatically pulls data from the Topic and writes it to a table — no manual triggering or Cron configuration required.

## Kafka Pipe Syntax

```SQL
-- Syntax for creating a Pipe from Kafka
CREATE PIPE [ IF NOT EXISTS ] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    [INITIAL_DELAY_IN_SECONDS='']
    [BATCH_INTERVAL_IN_SECONDS='']
    [BATCH_SIZE_PER_KAFKA_PARTITION='']
    [MAX_SKIP_BATCH_COUNT_ON_ERROR='']
    [RESET_KAFKA_GROUP_OFFSETS='']
    [COPY_JOB_HINT='']
AS <copy_statement>;
```

* `<pipe_name>`: The name of the Pipe object, used for management and monitoring.
* `VIRTUAL_CLUSTER`: Specifies the name of the Virtual Cluster to execute Pipe tasks.
* `INITIAL_DELAY_IN_SECONDS`: Initial job scheduling delay (optional, default 0 seconds).
* `BATCH_INTERVAL_IN_SECONDS`: (Optional) Controls how long to accumulate data per batch before writing — a shorter interval means fresher data, a longer interval means more efficient single writes. Default of 60 seconds works for most scenarios.
* `BATCH_SIZE_PER_KAFKA_PARTITION`: (Optional) Batch size per Kafka partition, default 500,000 records.
* `MAX_SKIP_BATCH_COUNT_ON_ERROR`: (Optional) Maximum number of batches to skip on error, default 30.
* `RESET_KAFKA_GROUP_OFFSETS`: (Optional) Controls where the Pipe starts consuming Kafka data when it starts. Only settable at startup. If not set and the consumer group has no historical position, Kafka's [auto.offset.reset](https://kafka.apache.org/documentation/#consumerconfigs_auto.offset.reset) configuration is used (default `latest`). Supported values:
  * `none`: No action; uses [auto.offset.reset](https://kafka.apache.org/documentation/#consumerconfigs_auto.offset.reset)
  * `valid`: Checks if the current group offset is expired and resets expired partition offsets to the current earliest
  * `earliest`: Resets to the current earliest
  * `latest`: Resets to the current latest
  * `${TIMESTAMP_MILLISECONDS}`: Resets to the offset corresponding to the millisecond timestamp, e.g., `1737789688000` (2025-01-25 15:21:28)

## Using READ\_KAFKA in a Pipe

For temporary exploration, you can use the READ_KAFKA function directly (see [READ_KAFKA Function](<sql_functions/table_functions/read_kafka.md>)). When using `READ_KAFKA` in a Pipe's COPY statement, the following **important differences** apply:

### Parameter Passing Rules

```sql
-- READ_KAFKA syntax in a Pipe
read_kafka (
    'bootstrap_servers',     -- Required: Kafka cluster address in host:port format, multiple brokers separated by commas — 2-3 broker addresses are sufficient, no need to list all nodes
    'topic',                 -- Required: Topic name — one Pipe corresponds to one Topic; create multiple Pipes for multiple Topics
    '',                      -- Required: Topic pattern (not yet supported, leave empty string)
    'group_id',              -- Required: Persistent consumer group ID — use a meaningful name (e.g., pipe_orders_group); different Pipes for the same Topic must use different group_ids
    '',                      -- Leave empty: start position is managed automatically by Pipe (when using READ_KAFKA standalone, fill starting_offsets here)
    '',                      -- Leave empty: end position managed automatically by Pipe
    '',                      -- Leave empty: start timestamp managed automatically by Pipe
    '',                      -- Leave empty: end timestamp managed automatically by Pipe
    'raw',                   -- Key format
    'raw',                   -- Value format
    0,                       -- Max error count
    map()                    -- Kafka config parameters — fill in SSL, SASL and other auth params here when needed, e.g., map('security.protocol','SASL_SSL',...)
)
```

### Key Differences

| Feature | READ\_KAFKA Function (standalone) | READ\_KAFKA (in a Pipe) |
| ------ | ------------------------ | --------------------- |
| Consumer group | Temporary, destroyed after execution | Persistent, maintains consumption position |
| Position management | Manually specify starting\_offsets etc. | Managed automatically by Pipe; position parameters must be left empty |
| Execution mode | One-time query | Continuously scheduled |
| Default start position | earliest (explore historical data) | latest (process new data) |

### Best Practices

See [Efficiently Ingesting Kafka Data with Pipe](<pipe-kafka-bestpractice-1.md>)

## Usage Example

```SQL
/*Use a Lakehouse Pipe task object to continuously import Kafka data into a target table*/
---Step01: Create the target table for Kafka writes
create table kafka_raw(value string);

---Step02: Create a PIPE task to read from Kafka and write to the target table
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
        '',-- offset-related parameter, leave empty in pipe ddl
        '',-- offset-related parameter, leave empty in pipe ddl
        '',-- offset-related parameter, leave empty in pipe ddl
        '',-- offset-related parameter, leave empty in pipe ddl
        'raw',-- key format, currently only supports binary
        'raw',-- value format, currently only supports binary
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



## Status Monitoring and Management

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

Since each Pipe execution is a COPY operation, you can view all operations in the job history. Filter by `query_tag` in the [Job History](web-job-history.md). All Pipe COPY jobs are tagged in the format `pipe.``workspace_name``.schema_name.pipe_name` for easy tracking.

### Stop and Start a Pipe

* Pause a Pipe:

```
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = true;
```

* Resume a Pipe:

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

* Modifying the COPY statement logic is not supported. If you need to modify it, delete the Pipe and recreate it.
* When modifying the `COPY_JOB_HINT` of a Pipe, the new settings will overwrite all existing hints. If your Pipe already has hints such as `{"cz.sql.split.kafka.strategy":"size"}`, you must include all required hints together when setting new ones; otherwise existing hints will be overwritten. Separate multiple parameters with commas.
