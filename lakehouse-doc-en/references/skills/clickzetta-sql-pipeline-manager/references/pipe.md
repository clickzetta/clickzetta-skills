# Pipe SQL Reference

> **⚠️ ClickZetta-specific Syntax**
> - Kafka read function is `read_kafka(...)`, using **positional parameters** (not named parameters `=>`)
> - JSON field extraction uses `parse_json(value::string)['field']::TYPE` syntax
> - Pipe auto-starts after creation, no need for manual RESUME
> - OSS Pipe's `PURGE=true` follows immediately after `USING <format>` (e.g. `USING CSV PURGE=true`)

Pipe is ClickZetta Lakehouse's continuous data ingestion object, defined by SQL to automatically and continuously import data from Kafka or object storage (OSS/S3/COS) to target tables without external scheduling.

## CREATE PIPE — Import from Kafka

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
    '<bootstrap_servers>',   -- Required: Kafka cluster address
    '<topic>',               -- Required: Topic name
    '',                      -- Reserved (fill with empty string)
    '<group_id>',            -- Required: Persistent consumer group ID
    '', '', '', '',          -- Positional parameters left empty, managed by Pipe
    'raw',                   -- key format (currently only supports raw)
    'raw',                   -- value format (currently only supports raw)
    0,                       -- max_errors
    MAP(<kafka_config>)      -- Kafka configuration parameters
  )
);
```

**Examples:**
```sql
-- Continuously import JSON data from Kafka
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

## Verify Kafka Connection (Before Creating Pipe)

When independently using `read_kafka` to explore data, you can set `kafka.auto.offset.reset` in MAP:

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

> ⚠️ **Independent Exploration vs In Pipe Difference**:
> - Independent exploration: can set `kafka.auto.offset.reset` to `earliest` in MAP to read historical data
> - In Pipe: positional parameters must be left empty, consumption offset controlled by Pipe's `RESET_KAFKA_GROUP_OFFSETS` parameter

## CREATE PIPE — Import from Object Storage

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

**Key Parameters:**
- `VIRTUAL_CLUSTER`: Specify virtual cluster name (required for OSS Pipe)
- `INGEST_MODE = 'LIST_PURGE'`: General mode, periodically scan file list, must set `PURGE=true`
- `INGEST_MODE = 'EVENT_NOTIFICATION'`: Event notification mode, low latency (only Alibaba Cloud OSS + AWS S3), does not need `PURGE=true`
- `COMMENT 'text'`: Without equals sign (`COMMENT = 'text'` will error)
- `PURGE=true`: Place at end, OPTIONS before it: `USING CSV OPTIONS (...) PURGE=true`
- COPY statement in PIPE does not support `files`, `regexp`, `subdirectory` parameters

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

-- EVENT_NOTIFICATION mode (does not need PURGE)
CREATE PIPE oss_event_pipe
  VIRTUAL_CLUSTER = 'default'
  INGEST_MODE = 'EVENT_NOTIFICATION'
  ALICLOUD_MNS_QUEUE = 'my-mns-queue-name'
AS
COPY INTO ods.events
FROM VOLUME my_oss_event_volume
USING PARQUET;
```

## Start/Stop Pipe

```sql
-- Suspend Pipe
ALTER PIPE <pipe_name> SET PIPE_EXECUTION_PAUSED = true;

-- Resume Pipe
ALTER PIPE <pipe_name> SET PIPE_EXECUTION_PAUSED = false;
```

## Modify Pipe Properties

```sql
-- Can only modify one property at a time
ALTER PIPE <pipe_name> SET VIRTUAL_CLUSTER = 'new_vc';
ALTER PIPE <pipe_name> SET COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}';
```

> ⚠️ **ALTER PIPE Supported Properties**:
> - ✅ `PIPE_EXECUTION_PAUSED`
> - ✅ `VIRTUAL_CLUSTER`
> - ✅ `COPY_JOB_HINT`
> - ❌ `BATCH_INTERVAL_IN_SECONDS` (not supported to modify, needs drop and recreate)
> - ❌ `BATCH_SIZE_PER_KAFKA_PARTITION` (not supported to modify, needs drop and recreate)
>
> Does not support modifying COPY/INSERT statement logic, needs to drop Pipe then recreate.
> `COPY_JOB_HINT` modification will overwrite all existing hints, need to set all parameters at once.

## DROP PIPE

```sql
DROP PIPE [ IF EXISTS ] <pipe_name>;
```

## SHOW PIPE

```sql
-- List all Pipes in current schema
SHOW PIPES;

-- View Pipe details (status, latency, definition)
DESC PIPE <pipe_name>;
DESC PIPE EXTENDED <pipe_name>;
```

## Important Notes

- Pipe auto-starts after creation, no need for manual RESUME
- Kafka Pipe uses consumer group to manage offset, recreating Pipe with same group_id can continue from last offset
- Object storage Pipe detects new files through file list or event notification, `load_history` deduplication records retained for 7 days
- Pipe does not support modifying AS clause, needs to drop then recreate (not `CREATE OR REPLACE`)
- Kafka Pipe only supports PLAINTEXT and SASL_PLAINTEXT security protocols, does not support SSL

## Reference Documentation

- [Pipe Introduction](https://www.yunqi.tech/documents/pipe-summary)
- [Continuous Import with read_kafka Function](https://www.yunqi.tech/documents/pipe-kafka)
- [Continuous Import with Kafka External Table Stream](https://www.yunqi.tech/documents/pipe-kafka-table-stream)
- [Best Practice: Efficiently Ingesting Kafka Data with Pipe](https://www.yunqi.tech/documents/pipe-kafka-bestpractice-1)
- [Continuous Import of Object Storage Data with Pipe](https://www.yunqi.tech/documents/pipe-storage-object)
