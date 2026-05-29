# Best Practice: Efficiently Ingesting Kafka Data Using Pipe

## Quick Verification of Kafka Parameters

In Singdata Lakehouse, using Kafka Pipe makes it easy to build minute-level near-real-time data integration pipelines. Before you begin, confirm three things:

1. Network connectivity
2. Kafka bootstrap addresses, ports, and topics
3. (Optional) Authentication method and related parameters

You can quickly verify all of the above by running a query like `select * from read_kafka()`.

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

> The `read_kafka` function has many parameters, but in practice you only need to fill in the bootstrap address, topic, and group id. During the exploration phase, use `test` as the group id.

Here is an example reading Kafka with SASL\_PLAINTEXT authentication (Pipe supports only PLAINTEXT and SASL\_PLAINTEXT):

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

If the parameters are configured correctly, executing the above SQL will return 10 rows of sample data.

![](/.topwrite/assets/image_1760681545512.png)

# Read Small Batches to Confirm Schema and Create the Target Table

Both the key and value in Kafka data are binary types. Usually you care more about the value content. If it is originally stored as a string, you can cast it to string during SELECT to quickly explore its content.

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

![](/.topwrite/assets/image_1760681595348.png)

Click "Copy" to retrieve sample data and explore it. The value appears to be JSON, but some string fields within the JSON are themselves complete JSON objects — the structure is nested and somewhat complex:

```JSON
{"event":"{\"instance_id\":1,\"workspace_id\":1057330101457946860,\"session_id\":0,\"job_id\":\"\",\"log_id\":8316782525667550489,\"operator_id\":0,\"operator_type\":\"PT_USER\",\"start_time\":1740590015608,\"end_time\":1740590015608,\"state\":1,\"properties\":\"[]\",\"statements\":\"{\\\"statements\\\":[{\\\"identifier\\\":{\\\"type\\\":\\\"VIRTUAL_CLUSTER\\\",\\\"instanceId\\\":\\\"1\\\",\\\"namespace\\\":[\\\"system_automv_warehouse\\\"],\\\"namespaceId\\\":[\\\"1057330101457946860\\\"],\\\"namespaceType\\\":[],\\\"name\\\":\\\"CZ_MV_DEFAULT\\\",\\\"id\\\":\\\"8013167251718801474\\\",\\\"version\\\":\\\"default_v2\\\",\\\"instanceName\\\":\\\"clickzetta\\\",\\\"accountId\\\":\\\"1\\\",\\\"accountName\\\":\\\"rwyaytaa\\\"},\\\"operations\\\":[{\\\"lsn\\\":0,\\\"type\\\":\\\"ALTER\\\",\\\"alterEntity\\\":{\\\"ifExists\\\":false,\\\"identifier\\\":{\\\"type\\\":\\\"VIRTUAL_CLUSTER\\\",\\\"instanceId\\\":\\\"1\\\",\\\"namespace\\\":[\\\"system_automv_warehouse\\\"],\\\"namespaceId\\\":[\\\"1057330101457946860\\\"],\\\"namespaceType\\\":[],\\\"name\\\":\\\"CZ_MV_DEFAULT\\\",\\\"id\\\":\\\"8013167251718801474\\\",\\\"version\\\":\\\"default_v2\\\",\\\"instanceName\\\":\\\"clickzetta\\\",\\\"accountId\\\":\\\"1\\\",\\\"accountName\\\":\\\"rwyaytaa\\\"},\\\"changeComment\\\":false,\\\"entity\\\":{\\\"identifier\\\":{\\\"type\\\":\\\"VIRTUAL_CLUSTER\\\",\\\"instanceId\\\":\\\"1\\\",\\\"namespace\\\":[\\\"system_automv_warehouse\\\"],\\\"namespaceId\\\":[\\\"1057330101457946860\\\"],\\\"namespaceType\\\":[],\\\"name\\\":\\\"CZ_MV_DEFAULT\\\",\\\"id\\\":\\\"8013167251718801474\\\",\\\"version\\\":\\\"\\\",\\\"instanceName\\\":\\\"clickzetta\\\",\\\"accountId\\\":\\\"1\\\",\\\"accountName\\\":\\\"rwyaytaa\\\"},\\\"creator\\\":\\\"101\\\",\\\"creatorType\\\":\\\"PT_USER\\\",\\\"properties\\\":[],\\\"createTime\\\":\\\"1698056353612\\\",\\\"lastModifyTime\\\":\\\"1740590015607\\\",\\\"state\\\":\\\"ONLINE\\\",\\\"category\\\":\\\"MANAGED\\\",\\\"basicSpecId\\\":0,\\\"flags\\\":\\\"0\\\",\\\"virtualCluster\\\":{\\\"clusterType\\\":\\\"GENERAL\\\",\\\"tag\\\":{},\\\"clusterSize\\\":\\\"SMALL\\\",\\\"autoStopLatencySec\\\":1,\\\"autoStartEnabled\\\":true,\\\"queryProcessTimeLimitSec\\\":259200,\\\"state\\\":\\\"RESUMING\\\",\\\"preState\\\":\\\"SUSPENDED\\\",\\\"errorMsg\\\":\\\"\\\",\\\"workspaceId\\\":\\\"1057330101457946860\\\",\\\"vcId\\\":\\\"8013167251718801474\\\",\\\"stateInfo\\\":\\\"{\\\\\\\"resourceVersion\\\\\\\":\\\\\\\"1740590006831\\\\\\\",\\\\\\\"resumeTaskState\\\\\\\":\\\\\\\"true\\\\\\\"}\\\",\\\"version\\\":\\\"default_v2\\\",\\\"computePoolId\\\":\\\"0\\\",\\\"deployMode\\\":\\\"SERVERLESS\\\"},\\\"comment\\\":\\\"\\\"},\\\"alterProperty\\\":[]}}]}]}\",\"sub_type\":\"\"}","op_type":"CREATE","datasource_id":"17319","database_name":"lakehouse_hz_uat_bak","schema_name":"lakehouse_hz_uat_bak","table_name":"cz_commit_logs_vc","event_ts":1740590015000,"event_seq":"3521832368","server_ts":1740590015924,"server_seq":138789}
```

Adjust the SELECT statement to use `parse_json` to expand the value field and the `event` within it:

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

Running this reveals that `statements` inside `event` is still JSON.

![](/.topwrite/assets/image_1760681703861.png)

Continue adjusting the SELECT statement until all JSON-formatted strings are fully parsed before writing to the table, avoiding redundant `parse_json` calculations in subsequent queries.

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

Based on the SELECT exploration results, determine the target table structure and create the table:

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

> Kafka data typically consists of append-only log tables. We therefore added an auto-generated column `pt_date` as the partition column based on the business timestamp `server_ts`, combined with the `data_lifecycle` table property to control data volume.

> The table DDL includes the `__kafka_timestamp__` field, which records the time data passed through Kafka. This column has little direct business value, but it can be used to diagnose the cause of data delays. We recommend keeping it.

At this point, you have completed the alignment between the Kafka data and the target table structure.

# Creating the Pipe

Next, use the exploration SELECT statement as a foundation to construct the Pipe DDL. A Pipe is essentially a wrapper around `COPY INTO <table> FROM (SELECT ... FROM READ_KAFKA(...))`, with additional parameters for specifying compute resources, scheduling frequency, and other operational settings.

Given that Kafka data typically arrives as a stream, if you need 1-minute data freshness — meaning the Pipe schedules a `COPY INTO` job every 60 seconds — we recommend allocating a dedicated GP cluster for the Pipe.

```sql
CREATE VCLUSTER pipe_ods_commit_log 
    VCLUSTER_TYPE = GENERAL 
    VCLUSTER_SIZE = 1
;
```

> Don't worry about the GP vcluster size for now — you can adjust it later based on actual job execution.

> One reason to allocate a dedicated cluster is that high data freshness requirements (e.g., less than 5 minutes) leave the cluster almost no idle time, making it effectively a permanently resident resource. You generally should not run Pipes on a large cluster, which would waste resources. Conversely, if the Kafka data volume is small, there is no need to allocate a separate cluster for each Pipe. In that case, a group of Pipes can share a single resident cluster to save resources.

The Pipe DDL is as follows:

1. Remove the `LIMIT 10` from the `select ... from read_kafka(...)` clause.
2. Change the group id from `test` to the production name you intend to use, such as `sub2cz`.
3. (Optional) Use the `RESET_KAFKA_GROUP_OFFSETS` parameter to specify the starting time point for reading Kafka (otherwise it reads from `latest` per the `kafka.auto.offset.reset` setting). The value must be in millisecond epoch format.

```sql
CREATE PIPE pipe_ods_commit_log 
    VIRTUAL_CLUSTER = 'pipe_ods_commit_log' 
    BATCH_INTERVAL_IN_SECONDS = '60'
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

> Here we added three parameters to `read_kafka`: `cz.kafka.fetch.retry.enable`, `cz.kafka.fetch.retry.times`, and `cz.kafka.fetch.retry.intervalMs`. These specify the retry strategy when the function encounters failures reading from Kafka, which helps reduce alerts and manual interventions in production.

After the Pipe is created, it starts running automatically. In Studio, click "Compute" → "Cluster" → "PIPE\_ODS\_COMMIT\_LOG" → "Jobs" to quickly check the execution status of jobs submitted by the Pipe.

When multiple Pipes share a VCluster, you can also use `query_tag` in Studio's "Compute" → "Job History" page or the `job_history` table in InformationSchema to quickly query the job execution of a specific Pipe. For jobs submitted by Pipes, the `query_tag` follows the format `pipe.<workspace_name>.<schema_name>.<pipe_name>`:

```sql
select query_tag, job_id, status, start_time, end_time, execution_time, input_bytes, output_bytes, rows_produced
from information_schema.job_history
where pt_date>='yyyy-MM-dd' -- eg. 2025-03-03
and query_tag = 'pipe.<workspace_name>.<schema_name>.<pipe_name>' -- eg. 'pipe.quick_start.public.pipe_ods_commit_log'
order by start_time desc;
```

# Large-Scale Data and Resource Optimization

Optimizing a Kafka Pipe for stable production operation means using the minimum resource configuration (VCluster) within the required freshness cycle (`BATCH_INTERVAL_IN_SECONDS`) to complete the computation and persistence of incoming data. In production, maintain some computing capacity reserve to ensure the Pipe can catch up when data volume fluctuates, cluster upgrades cause job failovers, etc. We typically recommend maintaining double the redundancy. In plain terms with our example: you need to be able to process all the data that flowed in from Kafka over 1 minute within roughly 30 seconds.

The default Pipe settings work well in most cases. However, if the ingested Kafka data volume is particularly large, adjust parameters based on actual conditions, as indicated by the red annotations in the figure below:

![](/.topwrite/assets/image_1760681949544.png)

To check whether the current Pipe is experiencing backlog, run `desc pipe extended` multiple times and observe whether `timeLag` in the `pipe_latency` row (the gap between the Kafka offset and current time, in milliseconds) is continuously increasing. With 60-second data freshness and double computing redundancy, `timeLag` should fluctuate between 0–90 seconds (without any redundancy, it should fluctuate between 0–120 seconds). If `timeLag` exceeds the upper limit and continues rising over several cycles, the Pipe is building up a backlog.

## Confirm Kafka Message Peak Value (Increase `BATCH_SIZE_PER_KAFKA_PARTITION`)

To prevent the Pipe from reading excessive data at startup and creating oversized jobs, Pipe limits the number of records read from each partition per batch. This is controlled by `BATCH_SIZE_PER_KAFKA_PARTITION`, which defaults to 50,000. When the peak message volume per partition per cycle exceeds this value, manually specify this parameter when creating the Pipe. We typically recommend setting it to 2× the peak value. If the Pipe is already running, you can dynamically adjust it with `alter pipe <pipe_name> set BATCH_SIZE_PER_KAFKA_PARTITION=<event_number>;`.

As shown in the figure, even though the Pipe's per-minute jobs complete in under 30 seconds, `desc pipe extended` may show `timeLag` continuously increasing.

![](/.topwrite/assets/image_1760681973997.png)

Click on the job to enter the job details page. You can see this is a Kafka topic with 10 partitions. Even with `BATCH_SIZE_PER_KAFKA_PARTITION` set to 100,000, not all data from one cycle is read — you need to keep increasing it.

![](/.topwrite/assets/image_1760681981294.png)

Ultimately, by continuously increasing this value and observing `timeLag` (in production you should ideally know the per-partition peak value in advance and set it directly), you determine that at 500,000 the Pipe's consumption speed is fast enough to keep up with Kafka.

> Unlike a direct `select ... read_kafka(...)`, the `copy into` jobs generated by Pipe show the offset information recorded in the Kafka group id managed by the Pipe. This makes it easy to identify how many partitions the Kafka topic has and the actual offset values of each partition.

## Adjusting VCluster Size

By default, the `copy into` jobs started by Pipe have a task count equal to the Kafka topic partition count — each task reads one partition. When the VCluster Size is small, job tasks may need multiple rounds to complete, significantly extending execution time.

Therefore, when you want jobs to finish quickly, ensure the VCluster's allowed task concurrency >= partition count, so all tasks complete in a single round.

In the figure below, a Pipe job using a 128CRU VCluster (1024 cores) consumes a Kafka topic with 1,200 partitions. It runs in two rounds: the first round with 1,024 tasks, and the remaining 176 tasks in the second round, significantly extending execution time. In this case, setting the VCluster to 150CRU (1,200 cores) is appropriate.

![](/.topwrite/assets/image_1760681994525.png)

## Splitting Kafka Data to Utilize More Compute Resources (Setting `COPY_JOB_HINT`)

When Kafka data volume is large but partition count is small, or the computation logic before writing to the table is complex enough that a single task cannot complete within the cycle requirement, consider setting `COPY_JOB_HINT` to further split tasks and combine with more compute resources for acceleration.

`COPY_JOB_HINT` is a composite parameter expressed in JSON format. To manually split Kafka data, use the following two keys together:

1. `"cz.sql.split.kafka.strategy":"size"` — The default is `"simple"`, meaning one task per partition. Change it to `"size"` to split tasks by record count.
2. `"cz.mapper.kafka.message.size":"200000"` — Specifies how many events constitute one task. The default is 1,000,000 and takes effect when `"cz.sql.split.kafka.strategy"` is `"size"`.

You can adjust the Pipe's task splitting strategy at any time with:
`alter pipe pipe_ods_commit_log set COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}';`

> `COPY_JOB_HINT` is a composite JSON parameter. When setting it via `alter pipe`, it is an overwrite operation — be careful not to accidentally lose previously set keys. You can retrieve the complete current settings from the `copy_job_hint` field in the properties row of `desc pipe extended` and modify from there.

After adjusting parameters, update the corresponding Pipe DDL to prevent parameter loss from rebuilds or migrations later.

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

# Modifying Pipe SQL Logic

Pipe allows relatively complex computations between `copy into` and `read_kafka`. When computation logic changes or the target table schema changes (a typical scenario is adding columns), you need to modify the existing Pipe definition.

In short, modifying the Pipe DDL means deleting and rebuilding the Pipe while keeping the `read_kafka` parameters unchanged.

For example, if you need to modify `pipe_ods_commit_log` to remove the `statements` content from the `event` field in the target table (because it is redundantly stored in the `statements` field), proceed as follows:

1. Delete the currently running Pipe

```SQL
drop pipe pipe_ods_commit_log;
```

> Dropping or altering an existing Pipe may be blocked by currently running jobs within the Pipe until those jobs complete, which may take some time.

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

> Pipe uses Kafka groups to record read offsets. As long as you use the same Kafka cluster, topic, and group id, rebuilding the Pipe will not lose the offset — you get a "resume from checkpoint" effect.

However, `RESET_KAFKA_GROUP_OFFSETS` forcibly overwrites the offset recorded in the group id and should be used with caution.

# Pipe Production Monitoring and Alerting

## Monitoring the Pipe Itself

Studio's data quality module provides latency monitoring capabilities for Pipes.

![](/.topwrite/assets/image_1760682100684.png)

## Monitoring Output Tables

Earlier, we added the `__kafka_timestamp__` field to the Pipe's output table `ods_commit_log`. You can use this field combined with Studio's data quality features for end-to-end latency monitoring, expressed as:

```SQL
select DATEDIFF(second, max(`__kafka_timestamp__`), now())from ods_commit_logwhere pt_date='${today}';
```

In Studio, click "Data" → "Data Quality" → "Quality Rules" → "Create Rule".

![](/.topwrite/assets/image_1760682111260.png)

Configure the parameter `today` with value `$[yyyyMMdd]`, select Custom SQL, and fill in the SQL query above. Set other required parameters as shown in the figure and click Save.

In Studio, click "Operations" → "Monitoring Alerts" → "Monitoring Rules" → "Create Rule".

Fill in the required fields as shown in the figure and save.

![](/.topwrite/assets/image_1760682120092.png)
