# Kafka Pipe SQL Syntax Reference

> Canonical syntax reference for ClickZetta Kafka Pipe operations.
> For workflow guidance, see `SKILL.md`.

---

## READ_KAFKA Function Signature

```sql
read_kafka(
  '<bootstrap_servers>',   -- Pos 1: Kafka broker addresses (required)
  '<topic_name>',          -- Pos 2: Topic name (required)
  '',                      -- Pos 3: Topic pattern (RESERVED — always empty string)
  '<group_id>',            -- Pos 4: Consumer group ID (required)
  '<starting_offsets>',    -- Pos 5: Starting offsets (empty in Pipe; 'earliest'/'latest' standalone)
  '<ending_offsets>',      -- Pos 6: Ending offsets (typically empty)
  '<starting_timestamp>',  -- Pos 7: Starting timestamp (typically empty)
  '<ending_timestamp>',    -- Pos 8: Ending timestamp (typically empty)
  '<key_format>',          -- Pos 9: Key format (only 'raw' supported)
  '<value_format>',        -- Pos 10: Value format (only 'raw' supported)
  <max_errors>,            -- Pos 11: Max errors (integer, typically 0)
  MAP(<kafka_config>)      -- Pos 12: Kafka configuration key-value pairs
)
```

> ⚠️ **Positional parameters only.**
> - ❌ `=>` named parameters not supported
> - ❌ `TABLE(READ_KAFKA(...))` wrapper not supported
> - ✅ `FROM read_kafka('broker','topic','','group','','','','','raw','raw',0,MAP(...))`

### Output Columns

| Column | Type | Description |
|--------|------|-------------|
| `key` | BINARY | Message key |
| `value` | BINARY | Message value (payload) |
| `topic` | STRING | Source topic name |
| `partition` | INT | Partition number |
| `offset` | BIGINT | Message offset |
| `timestamp` | TIMESTAMP | Message timestamp |
| `timestamp_type` | STRING | Timestamp type |

### Behavior: Standalone vs. Inside Pipe

| Aspect | Standalone | Inside Pipe |
|--------|-----------|-------------|
| Consumer group | Temporary, destroyed after query | Persistent, offset committed |
| Offset management | Via MAP `kafka.auto.offset.reset` | Pipe manages; positions 5–8 **must be empty** |
| Execution | One-shot query | Continuously scheduled |
| Default start | latest (override in MAP) | latest (override via `RESET_KAFKA_GROUP_OFFSETS`) |

---

## MAP Configuration Parameters

| Key | Values | Description |
|-----|--------|-------------|
| `kafka.security.protocol` | `PLAINTEXT`, `SASL_PLAINTEXT` | Security protocol (SSL not supported) |
| `kafka.sasl.mechanism` | `PLAIN` | SASL mechanism |
| `kafka.sasl.username` | string | SASL username |
| `kafka.sasl.password` | string | SASL password |
| `kafka.auto.offset.reset` | `earliest`, `latest` | Standalone exploration only; ignored in Pipe |
| `cz.kafka.fetch.retry.enable` | `true`, `false` | Enable fetch retry |
| `cz.kafka.fetch.retry.times` | integer | Retry count |
| `cz.kafka.fetch.retry.intervalMs` | integer | Retry interval (ms) |

---

## CREATE PIPE (READ_KAFKA)

```sql
CREATE PIPE <pipe_name>
  VIRTUAL_CLUSTER = '<vcluster_name>'
  [ BATCH_INTERVAL_IN_SECONDS = '<seconds>' ]
  [ BATCH_SIZE_PER_KAFKA_PARTITION = '<count>' ]
  [ MAX_SKIP_BATCH_COUNT_ON_ERROR = '<count>' ]
  [ INITIAL_DELAY_IN_SECONDS = '<seconds>' ]
  [ RESET_KAFKA_GROUP_OFFSETS = '<offset_value>' ]
  [ COPY_JOB_HINT = '<json_string>' ]
AS
COPY INTO <schema>.<table> FROM (
  SELECT <expressions>
  FROM (
    SELECT `timestamp`, parse_json(value::string) AS j
    FROM read_kafka(...)
  )
);
```

> `CREATE OR REPLACE PIPE` is **not supported**. Use `DROP PIPE` + `CREATE PIPE`.

### Pipe Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `VIRTUAL_CLUSTER` | Yes | — | Compute cluster for Pipe execution |
| `BATCH_INTERVAL_IN_SECONDS` | No | `'60'` | Batch interval = data freshness (seconds) |
| `BATCH_SIZE_PER_KAFKA_PARTITION` | No | `'500000'` | Max messages per partition per batch |
| `MAX_SKIP_BATCH_COUNT_ON_ERROR` | No | `'30'` | Consecutive error batches before Pipe pauses |
| `INITIAL_DELAY_IN_SECONDS` | No | `'0'` | Delay before first scheduled job |
| `RESET_KAFKA_GROUP_OFFSETS` | No | — | Initial offset (creation-time only) |
| `COPY_JOB_HINT` | No | — | JSON job hints |

### RESET_KAFKA_GROUP_OFFSETS Values

| Value | Effect |
|-------|--------|
| `'none'` | No reset; use Kafka default (`auto.offset.reset` = latest) |
| `'valid'` | Reset only expired partitions to earliest |
| `'earliest'` | Consume from beginning |
| `'latest'` | Consume only new messages |
| `'<epoch_millis>'` | Consume from specific timestamp (e.g., `'1737789688000'`) |

### COPY_JOB_HINT Keys

| Key | Default | Description |
|-----|---------|-------------|
| `cz.sql.split.kafka.strategy` | `simple` | `simple` = 1 task/partition; `size` = split by message count |
| `cz.mapper.kafka.message.size` | `1000000` | Messages per task when strategy = `size` |

> Must be valid JSON: `'{"key":"value","key2":"value2"}'`. Setting overwrites all previous hints.

---

## CREATE PIPE (Table Stream)

```sql
CREATE PIPE <pipe_name>
  VIRTUAL_CLUSTER = '<vcluster_name>'
  [ BATCH_INTERVAL_IN_SECONDS = '<seconds>' ]
AS
INSERT INTO <schema>.<table>
SELECT <expressions>
FROM <stream_name>;
```

> Table Stream Pipe uses `INSERT INTO ... SELECT`, **not** `COPY INTO`.

---

## CREATE STORAGE CONNECTION

```sql
CREATE STORAGE CONNECTION [ IF NOT EXISTS ] <conn_name>
  TYPE KAFKA
  BOOTSTRAP_SERVERS = ['<host1>:<port1>', '<host2>:<port2>']
  SECURITY_PROTOCOL = '<PLAINTEXT | SASL_PLAINTEXT>';
```

Drop: `DROP CONNECTION [ IF EXISTS ] <conn_name>;`

---

## CREATE EXTERNAL TABLE (Kafka)

```sql
CREATE EXTERNAL TABLE <table_name> (
  topic STRING,
  partition INT,
  `offset` BIGINT,
  `timestamp` TIMESTAMP,
  timestamp_type STRING,
  headers STRING,
  key BINARY,
  value BINARY
)
USING KAFKA
OPTIONS (
  'group_id' = '<consumer_group>',
  'topics' = '<topic_name>',
  'starting_offset' = '<earliest | latest>'
)
CONNECTION <conn_name>;
```

> - Column definitions **required** (error: `failed to detect columns` if omitted)
> - `offset`, `timestamp` are reserved words — backtick-escape always
> - Drop with `DROP TABLE` (not `DROP EXTERNAL TABLE`)

---

## CREATE TABLE STREAM

```sql
CREATE TABLE STREAM <stream_name>
  ON TABLE <source_table>
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

---

## ALTER PIPE

```sql
ALTER PIPE <pipe_name> SET <property> = <value>;
```

Supported properties (one per ALTER):

| Property | Alterable | Notes |
|----------|-----------|-------|
| `PIPE_EXECUTION_PAUSED` | ✅ | `true` / `false` |
| `VIRTUAL_CLUSTER` | ✅ | New VCluster name |
| `COPY_JOB_HINT` | ✅ | JSON string; overwrites all hints |
| `BATCH_INTERVAL_IN_SECONDS` | ❌ | Drop + recreate |
| `BATCH_SIZE_PER_KAFKA_PARTITION` | ❌ | Drop + recreate |
| SELECT logic | ❌ | Drop + recreate |

---

## DROP PIPE

```sql
DROP PIPE [ IF EXISTS ] <pipe_name>;
```

---

## Monitoring Queries

```sql
-- Pipe details (includes pipe_latency JSON)
DESC PIPE EXTENDED <pipe_name>;

-- List all Pipes
SHOW PIPES;

-- Load history (retained 7 days)
SELECT * FROM load_history('<schema>.<table>') ORDER BY last_copy_time DESC LIMIT 20;

-- Pipe jobs by query_tag
SHOW JOBS WHERE query_tag = 'pipe.<workspace>.<schema>.<pipe_name>';
```

### pipe_latency Fields

| Field | Description |
|-------|-------------|
| `lastConsumeTimestamp` | Timestamp of last consumed offset |
| `offsetLag` | Number of unconsumed messages |
| `timeLag` | Consumer lag in ms (-1 = abnormal) |

---

## JSON Field Extraction Patterns

```sql
-- Binary → String
value::string

-- String → JSON object
parse_json(value::string)

-- Extract top-level field
parse_json(value::string)['field']::TYPE

-- Extract nested field
parse_json(value::string)['parent']['child']::TYPE

-- Deeply nested (string-within-string)
parse_json(parse_json(value::string)['outer']::STRING)['inner']::TYPE

-- Recommended: parse once in subquery
SELECT j['id']::STRING, j['amount']::DECIMAL(10,2)
FROM (SELECT parse_json(value::string) AS j FROM read_kafka(...))
```

---

## CSV Field Extraction Pattern

```sql
split(value::string, ',')[0]::STRING   -- first field
split(value::string, ',')[1]::STRING   -- second field
CAST(split(value::string, ',')[2] AS DECIMAL(10,2))  -- with type cast
```

---

## Reference Links

- [Pipe Overview](https://www.yunqi.tech/documents/pipe-summary)
- [read_kafka Continuous Import](https://www.yunqi.tech/documents/pipe-kafka)
- [Kafka External Table + Table Stream](https://www.yunqi.tech/documents/pipe-kafka-table-stream)
- [Kafka Pipe Best Practice](https://www.yunqi.tech/documents/pipe-kafka-bestpractice-1)
- [read_kafka Function](https://www.yunqi.tech/documents/read_kafka)
- [Kafka External Table](https://www.yunqi.tech/documents/kafka-external-table)
- [Kafka Storage Connection](https://www.yunqi.tech/documents/Kafka_connection)
- [PIPE Syntax](https://www.yunqi.tech/documents/pipe-syntax)
