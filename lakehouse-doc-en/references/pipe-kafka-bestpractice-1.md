# Best Practice: Efficiently Ingesting Kafka Data Using Pipe

## Quick Verification of Kafka Parameters

In ClickZetta Lakehouse, using Kafka Pipe enables you to easily build minute-level near real-time data integration pipelines. Before you begin, you need to confirm three things:

1. Network connectivity
2. Kafka bootstrap addresses, ports, and topics
3. (Optional) Authentication methods and related parameters

The above purposes can be achieved by directly running queries like `select * from read_kafka()`.

Here is an example of unauthenticated Kafka ingestion:

```SQL
SELECT *
FROM read_kafka(
  'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
  'topic-name',   -- topic
  '',             -- reserved
  'test',         -- kafka group id, for keeping read position
  '', '', '', '', -- reserved
  'raw',          -- key format, can only be raw
  'raw',          -- value format, can only be raw
  0,
  MAP(
    'kafka.security.protocol','PLAINTEXT',
    'kafka.auto.offset.reset','latest'
  )
)
LIMIT 10;
```

> The `read_kafka` function has many parameters, but in practice only the bootstrap address, topic, and group id need to be filled in. During the exploration phase, we use 'test' as the group id.

Here is an example of reading Kafka with SASL\_PLAINTEXT authentication (Pipe supports only PLAINTEXT and SASL\_PLAINTEXT):

```SQL
SELECT *
FROM read_kafka(
  'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
  'topic-name',   -- topic
  '',             -- reserved
  'test',         -- kafka group id, for keeping read position
  '', '', '', '', -- reserved
  'raw',          -- key format, can only be raw
  'raw',          -- value format, can only be raw
  0,
  MAP(
    'kafka.security.protocol','SASL_PLAINTEXT',
    'kafka.sasl.mechanism','PLAIN',
    'kafka.sasl.username','<username>',
    'kafka.sasl.password','<password>',
    'kafka.auto.offset.reset','latest'
  )
)
LIMIT 10;
```

If the parameters are configured correctly, executing the above SQL will retrieve 10 rows of sample data.

![](/.topwrite/assets/image_1761125223064.png)

## Read Small Batches to Confirm Schema and Create Target Table

Both the key and value in Kafka data are binary types. Usually, we are more concerned with the value content. If it is originally stored as a string, we can cast it to string during SELECT to quickly explore its content.

```sql
SELECT key::string, value::string
FROM read_kafka(
  'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
  'topic-name',   -- topic
  '',             -- reserved
  'test',         -- kafka group id, for keeping read position
  '', '', '', '', -- reserved
  'raw',          -- key format, can only be raw
  'raw',          -- value format, can only be raw
  0,
  MAP(
    'kafka.security.protocol','PLAINTEXT',
    'kafka.auto.offset.reset','latest'
  )
)
LIMIT 10;
```

![](/.topwrite/assets/image_1761125274450.png)

Click "Copy" to retrieve sample data and explore it. We can see that the value is roughly JSON, but some string fields in the JSON are complete JSON objects as well. The structure appears to be nested:

```JSON
{"event":"{\"instance_id\":1,\"workspace_id\":1057330101457946860,\"session_id\":0,\"job_id\":\"\",\"log_id\":8316782525667550489,\"operator_id\":0,\"operator_type\":\"PT_USER\",\"start_time\":1740590015608,\"end_time\":1740590015608,\"state\":1,\"properties\":\"[]\",\"statements\":\"{\\\"statements\\\":[{\\\"identifier\\\":{\\\"type\\\":\\\"VIRTUAL_CLUSTER\\\",\\\"instanceId\\\":\\\"1\\\",\\\"namespace\\\":[\\\"system_automv_warehouse\\\"],\\\"namespaceId\\\":[\\\"1057330101457946860\\\"],\\\"namespaceType\\\":[],\\\"name\\\":\\\"CZ_MV_DEFAULT\\\",\\\"id\\\":\\\"8013167251718801474\\\",\\\"version\\\":\\\"default_v2\\\",\\\"instanceName\\\":\\\"clickzetta\\\",\\\"accountId\\\":\\\"1\\\",\\\"accountName\\\":\\\"rwyaytaa\\\"},\\\"operations\\\":[{\\\"lsn\\\":0,\\\"type\\\":\\\"ALTER\\\",\\\"alterEntity\\\":{\\\"ifExists\\\":false,\\\"identifier\\\":{\\\"type\\\":\\\"VIRTUAL_CLUSTER\\\",\\\"instanceId\\\":\\\"1\\\",\\\"namespace\\\":[\\\"system_automv_warehouse\\\"],\\\"namespaceId\\\":[\\\"1057330101457946860\\\"],\\\"namespaceType\\\":[],\\\"name\\\":\\\"CZ_MV_DEFAULT\\\",\\\"id\\\":\\\"8013167251718801474\\\",\\\"version\\\":\\\"default_v2\\\",\\\"instanceName\\\":\\\"clickzetta\\\",\\\"accountId\\\":\\\"1\\\",\\\"accountName\\\":\\\"rwyaytaa\\\"},\\\"changeComment\\\":false,\\\"entity\\\":{\\\"identifier\\\":{\\\"type\\\":\\\"VIRTUAL_CLUSTER\\\",\\\"instanceId\\\":\\\"1\\\",\\\"namespace\\\":[\\\"system_automv_warehouse\\\"],\\\"namespaceId\\\":[\\\"1057330101457946860\\\"],\\\"namespaceType\\\":[],\\\"name\\\":\\\"CZ_MV_DEFAULT\\\",\\\"id\\\":\\\"8013167251718801474\\\",\\\"version\\\":\\\"\\\",\\\"instanceName\\\":\\\"clickzetta\\\",\\\"accountId\\\":\\\"1\\\",\\\"accountName\\\":\\\"rwyaytaa\\\"},\\\"creator\\\":\\\"101\\\",\\\"creatorType\\\":\\\"PT_USER\\\",\\\"properties\\\":[],\\\"createTime\\\":\\\"1698056353612\\\",\\\"lastModifyTime\\\":\\\"1740590015607\\\",\\\"state\\\":\\\"ONLINE\\\",\\\"category\\\":\\\"MANAGED\\\",\\\"basicSpecId\\\":0,\\\"flags\\\":\\\"0\\\",\\\"virtualCluster\\\":{\\\"clusterType\\\":\\\"GENERAL\\\",\\\"tag\\\":{},\\\"clusterSize\\\":\\\"SMALL\\\",\\\"autoStopLatencySec\\\":1,\\\"autoStartEnabled\\\":true,\\\"queryProcessTimeLimitSec\\\":259200,\\\"state\\\":\\\"RESUMING\\\",\\\"preState\\\":\\\"SUSPENDED\\\",\\\"errorMsg\\\":\\\"\\\",\\\"workspaceId\\\":\\\"1057330101457946860\\\",\\\"vcId\\\":\\\"8013167251718801474\\\",\\\"stateInfo\\\":\\\"{\\\\\\\"resourceVersion\\\\\\\":\\\\\\\"1740590006831\\\\\\\",\\\\\\\"resumeTaskState\\\\\\\":\\\\\\\"true\\\\\\\"}\\\",\\\"version\\\":\\\"default_v2\\\",\\\"computePoolId\\\":\\\"0\\\",\\\"deployMode\\\":\\\"SERVERLESS\\\"},\\\"comment\\\":\\\"\\\"},\\\"alterProperty\\\":[]}}]}]}\",\"sub_type\":\"\"}","op_type":"CREATE","datasource_id":"17319","database_name":"lakehouse_hz_uat_bak","schema_name":"lakehouse_hz_uat_bak","table_name":"cz_commit_logs_vc","event_ts":1740590015000,"event_seq":"3521832368","server_ts":1740590015924,"server_seq":138789}
```

Adjust the SELECT statement to use `parse_json` to expand the value field and the event within it:

```SQL
SELECT
    parse_json(j['event']::string) as event,
    j['op_type']::string as op_type,
    j['datasource_id']::string as datasource_id,
    j['database_name']::string as database_name,
    j['schema_name']::string as schema_name,
    j['table_name']::string as table_name,
    timestamp_millis(j['event_ts']::bigint) as event_ts,
    j['event_seq']::string as event_seq,
    timestamp_millis(j['server_ts']::bigint) as server_ts,
    j['server_seq']::bigint as server_seq
FROM (
    SELECT parse_json(value::string) as j
    FROM read_kafka(
    'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
    'topic_name',   -- topic
    '',             -- reserved
    'test',         -- kafka group id, for keeping read position
    '', '', '', '', -- reserved
    'raw',          -- key format, can only be raw
    'raw',          -- value format, can only be raw
    0,
    MAP(
        'kafka.security.protocol','PLAINTEXT',
        'kafka.auto.offset.reset','latest'
    )
    )
    LIMIT 10
);
```

Running this, we find that the event field's statements is still JSON.

![](/.topwrite/assets/image_1761125295993.png)

Continue adjusting the SELECT statement until all JSON-formatted strings are fully parsed before storing in the table, avoiding redundant `parse_json` calculations in subsequent queries.

```SQL
SELECT
    parse_json(j['event']::string) as event,
    parse_json(parse_json(j['event']::string)['statements']::string) as statements,
    j['op_type']::string as op_type,
    j['datasource_id']::string as datasource_id,
    j['database_name']::string as database_name,
    j['schema_name']::string as schema_name,
    j['table_name']::string as table_name,
    timestamp_millis(j['event_ts']::bigint) as event_ts,
    j['event_seq']::string as event_seq,
    timestamp_millis(j['server_ts']::bigint) as server_ts,
    j['server_seq']::bigint as server_seq
FROM (
    SELECT parse_json(value::string) as j
    FROM read_kafka(
    'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
    'topic_name',   -- topic
    '',             -- reserved
    'test',         -- kafka group id, for keeping read position
    '', '', '', '', -- reserved
    'raw',          -- key format, can only be raw
    'raw',          -- value format, can only be raw
    0,
    MAP(
        'kafka.security.protocol','PLAINTEXT',
        'kafka.auto.offset.reset','latest'
    )
    )
    LIMIT 10
);
```

Based on the results of the SELECT exploration, determine the target table structure and create the table:

```SQL
CREATE TABLE ods_commit_log (
    event json,
    statements json,
    op_type string,
    datasource_id string,
    database_name string,
    schema_name string,
    table_name string,
    event_ts timestamp,
    event_seq string,
    server_ts timestamp,
    server_seq bigint,
    __kafka_timestamp__ timestamp,
    pt_date string generated always as (date_format(`server_ts`, 'yyyyMMdd')) stored
) PARTITIONED BY (pt_date)
PROPERTIES(
    'data_lifecycle'='14'
);
```

> Typically, data flowing from Kafka consists of append-only logs. Therefore, we added an auto-generated column `pt_date` as the partition column based on the business timestamp `server_ts`, combined with the `data_lifecycle` property to control table data volume.

> The table DDL includes the `__kafka_timestamp__` field, which records the time when data passed through Kafka. While this column has little business value, it can be used for troubleshooting when data delays occur. We recommend keeping it.

At this point, we have completed the alignment of Kafka data and the target table structure.

## Creating the Pipe Formally

Next, use the existing exploration SELECT statement as a foundation to construct the Pipe DDL. Pipe is essentially a wrapper around `COPY INTO <table> FROM (SELECT ... FROM READ_KAFKA(...))`, while also adding parameters for specifying compute resources, scheduling frequency, and other engineering considerations.

```SQL
CREATE PIPE pipe_ods_commit_log
    VIRTUAL_CLUSTER = 'pipe_ods_commit_log' 
    BATCH_INTERVAL_IN_SECONDS = '60'
    BATCH_SIZE_PER_KAFKA_PARTITION = 50000
    RESET_KAFKA_GROUP_OFFSETS = '1740931200000' -- epoch in millis of 2025-03-03 00:00:00
AS COPY INTO ods_commit_log FROM (
SELECT
    parse_json(j['event']::string) as event,
    parse_json(parse_json(j['event']::string)['statements']::string) as statements,
    j['op_type']::string as op_type,
    j['datasource_id']::string as datasource_id,
    j['database_name']::string as database_name,
    j['schema_name']::string as schema_name,
    j['table_name']::string as table_name,
    timestamp_millis(j['event_ts']::bigint) as event_ts,
    j['event_seq']::string as event_seq,
    timestamp_millis(j['server_ts']::bigint) as server_ts,
    j['server_seq']::bigint as server_seq,
    `timestamp` as __kafka_timestamp__
FROM (
    SELECT `timestamp`, parse_json(value::string) as j
    FROM read_kafka(
    'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
    'topic_name',   -- topic
    '',             -- reserved
    'sub2cz',       -- kafka group id, for keeping read position
    '', '', '', '', -- reserved
    'raw',          -- key format, can only be raw
    'raw',          -- value format, can only be raw
    0,
    MAP(
        'kafka.security.protocol','PLAINTEXT',
        'cz.kafka.fetch.retry.enable','true', 
        'cz.kafka.fetch.retry.times','20',
        'cz.kafka.fetch.retry.intervalMs','2000'
    )
)));
```

> Here we added three retry strategy parameters to the `read_kafka` function: `cz.kafka.fetch.retry.enable`, `cz.kafka.fetch.retry.times`, and `cz.kafka.fetch.retry.intervalMs`. These specify the retry strategy when the function encounters failures reading from Kafka. This helps reduce alarm incidents and manual interventions in production jobs.

After the Pipe is created, it automatically starts running. In Studio, click "Compute" → "Cluster" → "PIPE\_ODS\_COMMIT\_LOG" → "Jobs" to quickly check the execution status of jobs submitted by the pipe.

When multiple pipes share a VCluster, you can also use `query_tag` in Studio's "Compute" → "Job History" page or the `job_history` table in InformationSchema to quickly query the job execution of a specific pipe. For jobs submitted by pipes, the `query_tag` follows the format `pipe.<workspace_name>.<schema_name>.<pipe_name>`:

```sql
select query_tag, job_id, status, start_time, end_time, execution_time, input_bytes, output_bytes, rows_produced
from information_schema.job_history
where pt_date>='yyyy-MM-dd' -- eg. 2025-03-03
and query_tag = 'pipe.<workspace_name>.<schema_name>.<pipe_name>' -- eg. 'pipe.quick_start.public.pipe_ods_commit_log'
order by start_time desc;
```

## Large-Scale Data and Resource Optimization

Optimizing a Kafka Pipe to run stably in production means using the minimum resource configuration (VCluster) within the required freshness cycle (BATCH\_INTERVAL\_IN\_SECONDS) to complete the computation and persistence of incoming data. In production, you should maintain some computing capacity reserve to ensure the Pipe can catch up with data when data volume fluctuates, cluster upgrade jobs fail over, etc. We typically recommend maintaining double the redundancy. In simpler terms with our example, we need to be able to process all the data flowing in from Kafka in 1 minute within approximately 30 seconds.

The default settings for Pipe work well in most cases. However, if the ingested Kafka data volume is particularly large, you should adjust parameters based on actual conditions, as indicated by the red text in the following figure:

![](/.topwrite/assets/image_1761125330491.png)

To confirm whether the current Pipe is experiencing backlog, you can run `desc pipe extended` multiple times and check if `timeLag` in the `pipe_latency` row (the difference between the Kafka offset and current time, in milliseconds) is continuously increasing. When data freshness is 60 seconds and computing redundancy is double, `timeLag` should fluctuate between 0\~90 seconds (without redundancy, it should fluctuate between 0\~120 seconds). If `timeLag` exceeds the upper limit and continues to increase over several cycles, the Pipe will experience backlog.

### Confirm Kafka Message Peak Value (Increase `BATCH_SIZE_PER_KAFKA_PARTITION` Parameter)

To prevent the Pipe from reading excessive data at startup and creating oversized jobs, Pipe limits the number of data records read from each partition. This is controlled via `BATCH_SIZE_PER_KAFKA_PARTITION`, which defaults to 50,000. When the peak message volume of a Kafka partition per cycle exceeds this value, you should manually specify this parameter when creating the Pipe. We typically recommend setting this to 2 times the peak value. If the Pipe is already running, you can also dynamically adjust this value using `alter pipe <pipe_name> set BATCH_SIZE_PER_KAFKA_PARTITION=<event_number>;`.

As shown in the figure, although the Pipe's minute-level jobs complete in less than 30 seconds, `desc pipe extended` may indicate that `timeLag` is continuously increasing.

![](/.topwrite/assets/image_1761125345626.png)

Click on the job to enter the job details page. You can see this is a Kafka topic with 10 partitions. Even with `BATCH_SIZE_PER_KAFKA_PARTITION` set to 100,000, not all data from one cycle is read. It needs to be increased further.

![](/.topwrite/assets/image_1761125357982.png)

Ultimately, by continuously increasing this value and observing `timeLag` (in production, you should ideally know the peak value per Kafka partition beforehand and set it directly), we determine that when this value is set to 500,000, the Pipe's consumption speed is fast enough to keep up with Kafka.

> Unlike a direct `select ... read_kafka(...)`, the `copy into` jobs generated by Pipe can show the offset information recorded in the Kafka group id managed by the Pipe, making it easy to identify how many partitions the read Kafka topic has and the actual offset values of each partition.

### Adjusting VCluster Size

By default, the `copy into` jobs started by Pipe have a task count equal to the Kafka topic partition count—each task reads one partition. When the VCluster Size is small, the job tasks may need multiple rounds to complete, significantly extending job execution time.

Therefore, when you want the job to finish quickly, ensure the VCluster's allowed task concurrency >= partition count, so all tasks complete in one round.

In the figure below, a Pipe job using a 128CRU VCluster (1024 cores) consumes a Kafka topic with 1,200 partitions. It needs to run in two rounds: the first round with 1,024 tasks, and the remaining 176 tasks in the second round, significantly extending the execution time. In this case, setting the VCluster to 150CRU (1200 cores) would be appropriate.

![](/.topwrite/assets/image_1761125366953.png)

### Splitting Kafka Data to Utilize More Compute Resources (Setting `COPY_JOB_HINT`)

When Kafka data volume is large but partition count is small, or the computation logic before Pipe writes to the table is complex such that a single task cannot complete within the cycle requirement, you can consider setting `COPY_JOB_HINT` to further split tasks and combine them with more compute resources to achieve acceleration.

`COPY_JOB_HINT` is a composite parameter expressed in JSON format. To manually split Kafka data, you need to use the following two keys together:

1. `"cz.sql.split.kafka.strategy":"size"` - The default is `"simple"`, meaning one task per partition. Change it to `"size"`, which means splitting tasks by record count.
2. `"cz.mapper.kafka.message.size":"200000"` - Indicates how many events define one task. The default value is 1,000,000 and takes effect when `"cz.sql.split.kafka.strategy"` is `"size"`.

You can adjust the Pipe's task splitting strategy at any time using `alter pipe pipe_ods_commit_log set COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}';`.

> `COPY_JOB_HINT` is a composite parameter in JSON format. When setting it via `alter pipe`, it's an overwrite operation. Be careful not to accidentally lose other keys you've set previously. In such cases, you can retrieve the complete settings from the `copy_job_hint` in the properties row via `desc pipe extended` and modify based on that.

After adjusting parameters, we recommend updating the corresponding Pipe DDL to prevent parameter loss from rebuilds/migrations in subsequent processes.

```SQL
CREATE VCLUSTER pipe_ods_commit_log 
    VCLUSTER_TYPE = GENERAL 
    VCLUSTER_SIZE = 150
;

CREATE PIPE pipe_ods_commit_log
    VIRTUAL_CLUSTER = 'PIPE_ODS_COMMIT_LOG' 
    BATCH_INTERVAL_IN_SECONDS = '60'
    BATCH_SIZE_PER_KAFKA_PARTITION = 2000000
    RESET_KAFKA_GROUP_OFFSETS = '1740931200000' -- epoch in millis of 2025-03-03 00:00:00
    COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}' -- to accelerate load
AS COPY INTO ods_commit_log FROM 
...
```

## Modifying Pipe SQL Logic

Pipe allows relatively complex computations between `copy into` and `read_kafka`. When computation logic changes or target table schema changes (typical scenario: adding columns), you need to modify the existing Pipe definition.

In short, modifying the Pipe DDL means deleting and rebuilding the Pipe while keeping the `read_kafka` parameters unchanged.

For example, if we need to modify `pipe_ods_commit_log` to remove the statements content from the target table's event field (because it's redundantly stored in the statements field), we can proceed as follows:

1. Delete the currently running Pipe

```SQL
drop pipe pipe_ods_commit_log;
```

> Dropping or altering an existing Pipe may be blocked by currently running jobs within the Pipe until the jobs complete, which may take some time.

2. Rebuild the Pipe (note: remove the `RESET_KAFKA_GROUP_OFFSETS` parameter)

```sql
CREATE PIPE pipe_ods_commit_log 
    VIRTUAL_CLUSTER = 'pipe_ods_commit_log' 
    BATCH_INTERVAL_IN_SECONDS = '60'
    BATCH_SIZE_PER_KAFKA_PARTITION = 2000000
    -- RESET_KAFKA_GROUP_OFFSETS = '1740931200000' -- epoch in millis of 2025-03-03 00:00:00
    COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}' -- to accelerate load
AS COPY INTO ods_commit_log FROM (
SELECT
    remove_json(parse_json(j['event']::string), '$.statements') as event,
    parse_json(parse_json(j['event']::string)['statements']::string) as statements,
    j['op_type']::string as op_type,
    j['datasource_id']::string as datasource_id,
    j['database_name']::string as database_name,
    j['schema_name']::string as schema_name,
    j['table_name']::string as table_name,
    timestamp_millis(j['event_ts']::bigint) as event_ts,
    j['event_seq']::string as event_seq,
    timestamp_millis(j['server_ts']::bigint) as server_ts,
    j['server_seq']::bigint as server_seq,
    `timestamp` as __kafka_timestamp__
FROM (
    SELECT `timestamp`, parse_json(value::string) as j
    FROM read_kafka(
    'kafka-bootstrap-1:9092,kafka-bootstrap-2:9092,kafka-bootstrap-3:9092', -- bootstrap
    'topic_name',   -- topic
    '',             -- reserved
    'sub2cz',       -- kafka group id, for keeping read position
    '', '', '', '', -- reserved
    'raw',          -- key format, can only be raw
    'raw',          -- value format, can only be raw
    0,
    MAP(
        'kafka.security.protocol','PLAINTEXT',
        'cz.kafka.fetch.retry.enable','true', 
        'cz.kafka.fetch.retry.times','20',
        'cz.kafka.fetch.retry.intervalMs','2000'
    )
)));
```

> Pipe uses Kafka groups to record read offsets. Therefore, as long as you use the same Kafka cluster, topic, and group id, even if you rebuild the Pipe, the offset won't be lost, achieving a "resume from checkpoint" effect.

However, `RESET_KAFKA_GROUP_OFFSETS` forcibly overwrites the offset recorded in the group id and should be used with caution.

## Pipe Production Monitoring and Alerting

### Monitoring the Pipe Itself

Studio's data quality module provides latency monitoring capabilities for Pipes.

![](/.topwrite/assets/image_1761126247823.png)

### Monitoring Output Tables

In our earlier work, we added the `__kafka_timestamp__` field to the Pipe's output table `ods_commit_log`. You can use this field combined with Studio's data quality features for end-to-end latency monitoring, expressed as:

```SQL
select DATEDIFF(second, max(`__kafka_timestamp__`), now())from ods_commit_logwhere pt_date='${today}';
```

In Studio, click "Data" → "Data Quality" → "Quality Rules" → "Create Rule"

![](/.topwrite/assets/image_1761126316018.png)

Configure the parameter 'today' with value `$[yyyyMMdd]`, select Custom SQL, and fill in the SQL query from above. Set other necessary parameters as shown in the figure and click Save.

In Studio, click "Operations" → "Monitoring Alerts" → "Monitoring Rules" → "Create Rule"

![](/.topwrite/assets/image_1761126368876.png)

Fill in the necessary items as shown in the figure and save.
