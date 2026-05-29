# Pipe SQL Reference

> **⚠️ ClickZetta-specific syntax**
> - The Kafka read function is `read_kafka(...)`, using **positional parameters** (not named parameters with `=>`)
> - JSON field extraction uses `parse_json(value::string)['field']::TYPE` syntax
> - A Pipe starts automatically after creation; no manual RESUME is needed
> - For OSS Pipes, `PURGE=true` follows immediately after `USING <format>` (e.g., `USING CSV PURGE=true`)

Pipe is the continuous data ingestion object in ClickZetta Lakehouse. Defined by SQL, it automatically and continuously imports data from Kafka or object storage (OSS/S3/COS) into a target table without external scheduling.

## CREATE PIPE — Ingest from Kafka

```sql
CREATE [ OR REPLACE ] PIPE <pipe_name>
  VIRTUAL_CLUSTER = '<vcluster_name>'
  [ BATCH_INTERVAL_IN_SECONDS = '<seconds>' ]
  [ BATCH_SIZE_PER_KAFKA_PARTITION = '<count>' ]
  [ RESET_KAFKA_GROUP_OFFSETS = '<none|valid|earliest|latest|timestamp_ms>' ]
  [ COPY_JOB_HINT = '<json>' ]
AS
COPY INTO <target_table> FROM (
  SELECT <expr> [, ...]
  FROM read_kafka(
    '<bootstrap_servers>',   -- required: Kafka cluster address
    '<topic>',               -- required: topic name
    '',                      -- reserved (leave empty string)
    '<group_id>',            -- required: persistent consumer group ID
    '', '', '', '',          -- positional params left empty, managed by Pipe automatically
    'raw',                   -- key format (only 'raw' supported currently)
    'raw',                   -- value format (only 'raw' supported currently)
    0,                       -- max_errors
    MAP(<kafka_config>)      -- Kafka configuration parameters
  )
);
```

**Examples:**
```sql
-- Continuously ingest JSON data from Kafka
CREATE OR REPLACE PIPE kafka_orders_pipe
  VIRTUAL_CLUSTER = 'default'
  BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO ods.orders FROM (
  SELECT
    j['order_id']::STRING AS order_id,
    j['user_id']::STRING AS user_id,
    j['amount']::DECIMAL(10,2) AS amount,
    j['created_at']::TIMESTAMP AS created_at,
    CAST(`timestamp` AS TIMESTAMP) AS kafka_ts
  FROM (
    SELECT `timestamp`, parse_json(value::string) AS j
    FROM read_kafka(
      'kafka.example.com:9092',
      'orders',
      '',
      'lakehouse_consumer',
      '', '', '', '',
      'raw', 'raw', 0,
      MAP('kafka.security.protocol', 'PLAINTEXT')
    )
  )
);

-- SASL authentication
CREATE PIPE kafka_secure_pipe
  VIRTUAL_CLUSTER = 'pipe_vc'
  BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO ods.secure_events FROM (
  SELECT parse_json(value::string)['id']::STRING AS id,
         CAST(`timestamp` AS TIMESTAMP) AS kafka_ts
  FROM read_kafka(
    'kafka.example.com:9092', 'secure_events', '', 'cz_secure',
    '', '', '', '', 'raw', 'raw', 0,
    MAP(
      'kafka.security.protocol', 'SASL_PLAINTEXT',
      'kafka.sasl.mechanism', 'PLAIN',
      'kafka.sasl.username', 'my_user',
      'kafka.sasl.password', 'my_password'
    )
  )
);
```

## Verify Kafka Connection (Before Creating a Pipe)

When using `read_kafka` standalone to explore data, you can set `kafka.auto.offset.reset` in the MAP:

```sql
-- Verify connection and data format
SELECT value::string
FROM read_kafka(
  'kafka.example.com:9092',
  'orders',
  '',
  'test_explore',
  '', '', '', '',
  'raw', 'raw', 0,
  MAP('kafka.security.protocol', 'PLAINTEXT', 'kafka.auto.offset.reset', 'earliest')
)
LIMIT 10;
```

> ⚠️ **Standalone exploration vs inside a Pipe**:
> - Standalone exploration: you can set `kafka.auto.offset.reset` to `earliest` in the MAP to read historical data
> - Inside a Pipe: positional parameters must be left empty; the consumer offset is controlled by the Pipe's `RESET_KAFKA_GROUP_OFFSETS` parameter

## CREATE PIPE — Ingest from Object Storage

```sql
CREATE [ OR REPLACE ] PIPE [ IF NOT EXISTS ] <pipe_name>
  VIRTUAL_CLUSTER = '<virtual_cluster_name>'
  INGEST_MODE = 'LIST_PURGE' | 'EVENT_NOTIFICATION'
  [ COMMENT '<comment>' ]
  [ COPY_JOB_HINT = '<hint>' ]
AS
COPY INTO <target_table>
FROM VOLUME <volume_name>
USING <csv | parquet | orc | json> [OPTIONS ('<key>' = '<value>', ...)] PURGE=true;
```

**Key parameters:**
- `VIRTUAL_CLUSTER`: specifies the virtual cluster name (required for OSS Pipes)
- `INGEST_MODE = 'LIST_PURGE'`: general mode, periodically scans the file list; `PURGE=true` must be set
- `INGEST_MODE = 'EVENT_NOTIFICATION'`: event notification mode, low latency (Alibaba Cloud OSS + AWS S3 only); `PURGE=true` is not required
- `COMMENT 'text'`: no equals sign (`COMMENT = 'text'` will cause an error)
- `PURGE=true`: placed at the end, after OPTIONS: `USING CSV OPTIONS (...) PURGE=true`
- COPY statements inside a PIPE do not support `files`, `regexp`, or `subdirectory` parameters

**Examples:**
```sql
-- LIST_PURGE mode (with OPTIONS)
CREATE OR REPLACE PIPE oss_events_pipe
  VIRTUAL_CLUSTER = 'default'
  INGEST_MODE = 'LIST_PURGE'
  COMMENT 'OSS events pipeline'
AS
COPY INTO ods.events
FROM VOLUME my_oss_volume
USING PARQUET PURGE=true;

-- CSV format with OPTIONS (OPTIONS before PURGE)
CREATE PIPE oss_csv_pipe
  VIRTUAL_CLUSTER = 'default'
  INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO ods.csv_data
FROM VOLUME my_csv_volume
USING CSV OPTIONS ('header' = 'true', 'sep' = ',') PURGE=true;

-- EVENT_NOTIFICATION mode (PURGE not required)
CREATE PIPE oss_event_pipe
  VIRTUAL_CLUSTER = 'default'
  INGEST_MODE = 'EVENT_NOTIFICATION'
  ALICLOUD_MNS_QUEUE = 'my-mns-queue-name'
AS
COPY INTO ods.events
FROM VOLUME my_oss_event_volume
USING PARQUET;
```

## Start / Stop a Pipe

```sql
-- Pause Pipe
ALTER PIPE <pipe_name> SET PIPE_EXECUTION_PAUSED = true;

-- Resume Pipe
ALTER PIPE <pipe_name> SET PIPE_EXECUTION_PAUSED = false;
```

## Modify Pipe Properties

```sql
-- Only one property can be modified at a time
ALTER PIPE <pipe_name> SET VIRTUAL_CLUSTER = 'new_vc';
ALTER PIPE <pipe_name> SET COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}';
```

> ⚠️ **Supported ALTER PIPE properties**:
> - ✅ `PIPE_EXECUTION_PAUSED`
> - ✅ `VIRTUAL_CLUSTER`
> - ✅ `COPY_JOB_HINT`
> - ❌ `BATCH_INTERVAL_IN_SECONDS` (not supported; must drop and recreate)
> - ❌ `BATCH_SIZE_PER_KAFKA_PARTITION` (not supported; must drop and recreate)
>
> Modifying the COPY/INSERT statement logic is not supported; drop the Pipe and recreate it.
> Modifying `COPY_JOB_HINT` overwrites all existing hints; all parameters must be set at once.

## DROP PIPE

```sql
DROP PIPE [ IF EXISTS ] <pipe_name>;
```

## SHOW PIPE

```sql
-- List all Pipes in the current schema
SHOW PIPES;

-- View Pipe details (status, latency, definition)
DESC PIPE <pipe_name>;
DESC PIPE EXTENDED <pipe_name>;
```

## Notes

- A Pipe starts automatically after creation; no manual RESUME is needed
- Kafka Pipes use a consumer group to manage offsets; keeping the same group_id when recreating a Pipe allows resuming from the last offset
- Object storage Pipes detect new files via file list scanning or event notifications; `load_history` deduplication records are retained for 7 days
- Pipes do not support modifying the AS clause; drop and recreate (not `CREATE OR REPLACE`)
- Kafka Pipes only support PLAINTEXT and SASL_PLAINTEXT security protocols; SSL is not supported

## Reference Documentation

- [Pipe Overview](https://www.yunqi.tech/documents/pipe-summary)
- [Continuous Ingestion with read_kafka](https://www.yunqi.tech/documents/pipe-kafka)
- [Continuous Ingestion with Kafka External Table Stream](https://www.yunqi.tech/documents/pipe-kafka-table-stream)
- [Best Practices: Efficient Kafka Ingestion with Pipe](https://www.yunqi.tech/documents/pipe-kafka-bestpractice-1)
- [Continuous Ingestion from Object Storage with Pipe](https://www.yunqi.tech/documents/pipe-storage-object)
