---
name: clickzetta-kafka-ingest-pipeline
description: |
  Build Kafka-to-Lakehouse ingestion pipelines using READ_KAFKA Pipe or Kafka External Table + Table Stream.
  Covers: connection validation, JSON/CSV parsing, Pipe DDL, SASL auth, VCluster sizing, latency monitoring, tuning.
  Triggers: Kafka ingestion, Kafka Pipe, read_kafka, Kafka external table, Kafka consumer, message queue import, Kafka backlog.
---

# Kafka Data Ingestion Pipeline Workflow

> **Compatibility**: Requires ClickZetta Lakehouse with Pipe support (v2.0+). All SQL executed via `cz-cli sql --sync`.

## Quick Start (Simple JSON, No Auth)

For the fastest path — flat JSON topic, PLAINTEXT, default settings:

```bash
# 1. Verify connectivity
cz-cli sql "SELECT value::string FROM read_kafka('BROKER:9092','TOPIC','','test_explore','','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest')) LIMIT 5" --sync

# 2. Create target table
cz-cli sql "CREATE TABLE IF NOT EXISTS ods.my_table (id STRING, name STRING, amount DECIMAL(10,2), __kafka_timestamp__ TIMESTAMP)" --sync

# 3. Create Pipe
cz-cli sql "CREATE PIPE my_pipe VIRTUAL_CLUSTER='default' BATCH_INTERVAL_IN_SECONDS='60' AS COPY INTO ods.my_table FROM (SELECT j['id']::STRING, j['name']::STRING, j['amount']::DECIMAL(10,2), CAST(\`timestamp\` AS TIMESTAMP) FROM (SELECT \`timestamp\`, parse_json(value::string) AS j FROM read_kafka('BROKER:9092','TOPIC','','cz_my_group','','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT'))))" --sync

# 4. Verify
cz-cli sql "DESC PIPE EXTENDED my_pipe" --sync
cz-cli sql "SELECT COUNT(*) FROM ods.my_table" --sync
```

Replace `BROKER:9092`, `TOPIC`, field names, and types. Pipe starts automatically.

> **Tip**: If backtick escaping causes issues in your shell, write the SQL to a file and run `cz-cli sql -f pipe.sql --sync` instead.

---

## Decision Tree

```
User wants Kafka → Lakehouse ingestion
│
├─ Message format?
│  ├─ JSON (flat)      → Standard path, parse_json + field extraction
│  ├─ JSON (nested)    → Layer-by-layer parse_json unwrapping (see Step 2 below)
│  ├─ CSV              → split(value::string, ',')[N] extraction (see CSV section)
│  └─ Avro / Protobuf  → NOT SUPPORTED natively; land as raw BINARY, decode downstream
│
├─ Ingestion path?
│  ├─ READ_KAFKA Pipe (default)
│  │   → Simpler, fewer objects, supports complex SQL in COPY INTO
│  │   → Use for: most scenarios
│  │
│  └─ Kafka External Table + Table Stream Pipe
│      → Retains raw messages in external table
│      → Multiple downstream consumers can read same topic independently
│      → Use for: audit trail, multi-consumer fan-out
│
├─ Authentication?
│  ├─ None             → MAP('kafka.security.protocol','PLAINTEXT')
│  ├─ SASL_PLAINTEXT   → Add sasl.mechanism, username, password to MAP
│  └─ SSL / mTLS       → NOT SUPPORTED by Kafka Pipe
│
└─ Starting offset?
   ├─ Latest (default) → Omit RESET_KAFKA_GROUP_OFFSETS
   ├─ Earliest         → RESET_KAFKA_GROUP_OFFSETS = 'earliest'
   └─ Specific time    → RESET_KAFKA_GROUP_OFFSETS = '<epoch_millis>'
```

---

## Wizard: Collect Required Information

Before building a Kafka pipeline, use an interactive Q&A tool (e.g., `question`) to collect the following. If no such tool is available, list all questions in text:

```
question({
  questions: [
    {
      question: "Kafka message format?",
      options: [
        { label: "JSON (flat)", description: "Top-level fields map directly" },
        { label: "JSON (nested)", description: "Requires layer-by-layer parse_json" },
        { label: "CSV", description: "Comma-separated, use split()" },
        { label: "Avro / Protobuf / Other", description: "Land as raw binary, decode downstream" }
      ]
    },
    {
      question: "Ingestion path?",
      options: [
        { label: "READ_KAFKA Pipe (recommended)", description: "General use case, fewer objects" },
        { label: "Kafka External Table + Table Stream", description: "Retain raw messages or multi-consumer fan-out" }
      ]
    },
    {
      question: "Authentication?",
      options: [
        { label: "None (PLAINTEXT)", description: "No credentials needed" },
        { label: "SASL_PLAINTEXT", description: "Username/password authentication" }
      ]
    }
  ]
})
```

**If the user has already provided sufficient information, skip the wizard and proceed directly.**

---

## Key Constraints

- Kafka Pipe supports only **PLAINTEXT** and **SASL_PLAINTEXT** (no SSL/mTLS)
- Pipe **starts automatically** after creation — no manual RESUME needed
- Pipe SQL logic cannot be altered — must DROP + CREATE to change the SELECT
- `CREATE OR REPLACE PIPE` is **not supported** — use DROP then CREATE
- `RESET_KAFKA_GROUP_OFFSETS` only takes effect at creation time
- `topic_pattern` (position 3) is **reserved and unused** — always pass empty string `''`
- Recommend a **dedicated GP VCluster** for Kafka Pipe to avoid resource contention

---

## Path One: READ_KAFKA Pipe (Recommended)

### Step 1: Validate Kafka Connection

> ⚠️ READ_KAFKA uses **positional parameters only**. No `=>` named params, no `TABLE()` wrapper.
> Full parameter reference: see `references/kafka-pipe-syntax.md`

```sql
SELECT value::string
FROM read_kafka(
  'kafka.example.com:9092',  -- bootstrap_servers
  'orders',                   -- topic
  '',                         -- reserved (always empty)
  'test_explore',             -- group_id (use temp name for exploration)
  '', '', '', '',             -- offsets/timestamps (leave empty)
  'raw', 'raw', 0,           -- key_format, value_format, max_errors
  MAP(
    'kafka.security.protocol', 'PLAINTEXT',
    'kafka.auto.offset.reset', 'earliest'
  )
)
LIMIT 10;
```

For SASL authentication, add to MAP:
```sql
MAP(
  'kafka.security.protocol', 'SASL_PLAINTEXT',
  'kafka.sasl.mechanism', 'PLAIN',
  'kafka.sasl.username', 'my_user',
  'kafka.sasl.password', 'my_password',
  'kafka.auto.offset.reset', 'earliest'
)
```

> **Multi-broker format**: `'broker1:9092,broker2:9092,broker3:9092'` (recommended for HA)

### Step 2: Explore Schema and Parse Messages

**JSON (flat)**:
```sql
SELECT
  j['order_id']::STRING AS order_id,
  j['amount']::DECIMAL(10,2) AS amount,
  timestamp_millis(j['created_at']::BIGINT) AS created_at
FROM (
  SELECT parse_json(value::string) AS j
  FROM read_kafka('kafka:9092','orders','','test_schema','','','','','raw','raw',0,
    MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest'))
  LIMIT 5
);
```

**JSON (nested)** — unwrap layer by layer:
```sql
SELECT
  j['id']::STRING AS id,
  parse_json(j['event']::STRING)['action']::STRING AS action,
  parse_json(parse_json(j['event']::STRING)['payload']::STRING)['ref']::STRING AS ref
FROM (
  SELECT parse_json(value::string) AS j
  FROM read_kafka('kafka:9092','events','','test_nested','','','','','raw','raw',0,
    MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest'))
  LIMIT 5
);
```

**CSV** — use `split()`:
```sql
SELECT
  split(value::string, ',')[0] AS id,
  split(value::string, ',')[1] AS name,
  CAST(split(value::string, ',')[2] AS DECIMAL(10,2)) AS amount
FROM read_kafka('kafka:9092','csv_topic','','test_csv','','','','','raw','raw',0,
  MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest'))
LIMIT 5;
```

**Avro / Protobuf**: Not natively supported for parsing. Land as raw binary (`value` column) and decode in a downstream Dynamic Table or external process.

> **Best Practice**: Unwrap all nested JSON with `parse_json` in the Pipe SELECT to avoid repeated computation downstream.

### Step 3: Create Target Table

```sql
CREATE TABLE IF NOT EXISTS ods.kafka_orders (
    order_id    STRING,
    user_id     STRING,
    amount      DECIMAL(10,2),
    status      STRING,
    created_at  TIMESTAMP,
    __kafka_timestamp__ TIMESTAMP COMMENT 'Kafka message timestamp for e2e latency monitoring'
);
```

> Always add `__kafka_timestamp__` for end-to-end latency monitoring.

### Step 4: Create Dedicated VCluster (Recommended)

```sql
CREATE VCLUSTER IF NOT EXISTS pipe_kafka_vc
  VCLUSTER_TYPE = GENERAL
  VCLUSTER_SIZE = 4
  AUTO_SUSPEND_IN_SECOND = 0
  COMMENT 'Dedicated always-on cluster for Kafka Pipe';
```

> Set `AUTO_SUSPEND_IN_SECOND = 0` for sub-minute freshness to avoid cold-start latency.

### Step 5: Create Kafka Pipe

```sql
CREATE PIPE kafka_orders_pipe
  VIRTUAL_CLUSTER = 'pipe_kafka_vc'
  BATCH_INTERVAL_IN_SECONDS = '60'
  BATCH_SIZE_PER_KAFKA_PARTITION = '500000'
AS
COPY INTO ods.kafka_orders FROM (
  SELECT
    j['order_id']::STRING,
    j['user_id']::STRING,
    j['amount']::DECIMAL(10,2),
    j['status']::STRING,
    j['created_at']::TIMESTAMP,
    CAST(`timestamp` AS TIMESTAMP) AS __kafka_timestamp__
  FROM (
    SELECT `timestamp`, parse_json(value::string) AS j
    FROM read_kafka(
      'kafka.example.com:9092',
      'orders',
      '',
      'lakehouse_orders',         -- production group_id
      '', '', '', '',             -- must be empty in Pipe
      'raw', 'raw', 0,
      MAP('kafka.security.protocol', 'PLAINTEXT')
    )
  )
);
```

> **Inside a Pipe**: positional offset params MUST be empty (Pipe manages offsets). Do NOT set `kafka.auto.offset.reset` in MAP — use `RESET_KAFKA_GROUP_OFFSETS` Pipe parameter instead.

For full parameter reference, see `references/kafka-pipe-syntax.md`.

### Step 6: Verify

```sql
DESC PIPE EXTENDED kafka_orders_pipe;
SELECT COUNT(*) FROM ods.kafka_orders;
SELECT * FROM load_history('ods.kafka_orders') ORDER BY last_load_time DESC LIMIT 10;
SHOW JOBS WHERE query_tag = 'pipe.my_workspace.ods.kafka_orders_pipe';
```

---

## Path Two: Kafka External Table + Table Stream Pipe

Use when: raw message retention needed, or multiple independent downstream consumers on the same topic.

### Step 1: Create Kafka Storage Connection

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS kafka_conn
  TYPE KAFKA
  BOOTSTRAP_SERVERS = ['kafka.example.com:9092']
  SECURITY_PROTOCOL = 'PLAINTEXT';
```

> Drop with `DROP CONNECTION IF EXISTS kafka_conn` (not `DROP STORAGE CONNECTION`).

### Step 2: Create Kafka External Table

```sql
CREATE EXTERNAL TABLE kafka_orders_ext (
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
  'group_id' = 'lakehouse_ext_orders',
  'topics' = 'orders',
  'starting_offset' = 'earliest'
)
CONNECTION kafka_conn;
```

> - Column definitions are **required** (omitting causes `failed to detect columns`)
> - `offset` and `timestamp` are reserved words — always backtick-escape
> - Drop with `DROP TABLE` (not `DROP EXTERNAL TABLE`)

### Step 3: Create Table Stream

```sql
CREATE TABLE STREAM kafka_orders_stream
  ON TABLE kafka_orders_ext
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

### Step 4: Create Target Table and Pipe

```sql
CREATE TABLE IF NOT EXISTS ods.kafka_orders_from_ext (
    order_id STRING, user_id STRING, amount DECIMAL(10,2), kafka_ts TIMESTAMP
);

-- Table Stream Pipe uses INSERT INTO ... SELECT (not COPY INTO)
CREATE PIPE kafka_ext_orders_pipe
  VIRTUAL_CLUSTER = 'pipe_kafka_vc'
  BATCH_INTERVAL_IN_SECONDS = '60'
AS
INSERT INTO ods.kafka_orders_from_ext
SELECT
  j['order_id']::STRING,
  j['user_id']::STRING,
  j['amount']::DECIMAL(10,2),
  CAST(`timestamp` AS TIMESTAMP)
FROM (
  SELECT `timestamp`, parse_json(CAST(value AS STRING)) AS j
  FROM kafka_orders_stream
);
```

> **Note**: `GET_JSON_OBJECT(str, '$.path')` also works but `parse_json(str)['field']::TYPE` is preferred — it's more composable for nested structures and consistent with Path One.

---

## Monitoring & Operations

### Check Pipe Status and Lag

```sql
DESC PIPE EXTENDED kafka_orders_pipe;
```

Key field `pipe_latency` (JSON):
- `lastConsumeTimestamp` — last consumed offset time
- `offsetLag` — message backlog count
- `timeLag` — consumer lag in ms (shows -1 when abnormal)

> Normal: `timeLag` fluctuates 0–90s (with 60s batch interval + 2x headroom). Continuously increasing = backlog.

### End-to-End Latency (requires `__kafka_timestamp__`)

```sql
SELECT
  MAX(DATEDIFF('second', __kafka_timestamp__, CURRENT_TIMESTAMP())) AS max_delay_s,
  AVG(DATEDIFF('second', __kafka_timestamp__, CURRENT_TIMESTAMP())) AS avg_delay_s
FROM ods.kafka_orders
WHERE __kafka_timestamp__ >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR;
```

### Pause / Resume

```sql
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = true;   -- pause
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = false;  -- resume
```

### Modify Pipe Properties

Only `PIPE_EXECUTION_PAUSED`, `VIRTUAL_CLUSTER`, and `COPY_JOB_HINT` are alterable (one per ALTER call). Everything else — including `BATCH_INTERVAL_IN_SECONDS`, `BATCH_SIZE_PER_KAFKA_PARTITION`, and SELECT logic — requires drop + recreate. See `references/kafka-pipe-syntax.md` § ALTER PIPE for the full support matrix.

### Modify Pipe SQL Logic (Drop + Recreate)

```sql
DROP PIPE kafka_orders_pipe;

-- Recreate with same group_id, do NOT set RESET_KAFKA_GROUP_OFFSETS → continues from last offset
CREATE PIPE kafka_orders_pipe
  VIRTUAL_CLUSTER = 'pipe_kafka_vc'
  BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO ods.kafka_orders FROM (
  SELECT
    j['order_id']::STRING,
    j['user_id']::STRING,
    j['amount']::DECIMAL(10,2),
    UPPER(j['status']::STRING),  -- changed logic
    j['created_at']::TIMESTAMP,
    CAST(`timestamp` AS TIMESTAMP) AS __kafka_timestamp__
  FROM (
    SELECT `timestamp`, parse_json(value::string) AS j
    FROM read_kafka('kafka.example.com:9092','orders','','lakehouse_orders',
      '','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT'))
  )
);
```

---

## Production Tuning

Run `DESC PIPE EXTENDED` multiple times — if `timeLag` continuously increases, the Pipe is backlogged.

| Problem | Fix |
|---------|-----|
| Batch can't consume a full interval's data | Increase `BATCH_SIZE_PER_KAFKA_PARTITION` (drop + recreate, e.g., `'1000000'`) |
| Job needs multiple rounds | Increase VCluster size so cores ≥ partitions: `ALTER VCLUSTER ... SET VCLUSTER_SIZE = 16` |
| Few partitions, large volume | Split tasks by count: `ALTER PIPE ... SET COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}'` |

> **VCluster size-to-core mapping** (GENERAL type, 1 CRU = 8 cores):
> | VCLUSTER_SIZE (CRU) | Cores | Suitable for |
> |---------------------|-------|--------------|
> | 4 | 32 | ≤ 32 partitions, moderate throughput |
> | 8 | 64 | ≤ 64 partitions, high throughput |
> | 16 | 128 | Large-scale ingestion |
> | 32 | 256 | Very high partition count / throughput |
>
> Rule of thumb: set cores ≥ Kafka partition count so each partition gets a dedicated task slot.

> `COPY_JOB_HINT` must be valid JSON with double-quoted keys/values. Setting it overwrites all previous hints.

---

## Schema Evolution

When the Kafka topic adds new fields:

1. **Add columns** to the target table:
   ```sql
   ALTER TABLE ods.kafka_orders ADD COLUMN new_field STRING;
   ```

2. **Drop and recreate Pipe** with updated SELECT (keep same `group_id`, omit `RESET_KAFKA_GROUP_OFFSETS`):
   ```sql
   DROP PIPE kafka_orders_pipe;
   CREATE PIPE kafka_orders_pipe ...  -- add j['new_field']::STRING to SELECT
   ```

3. Existing rows will have `NULL` in the new column. New messages will populate it.

> There is no ALTER PIPE to change the SELECT — always drop + recreate. Keep the same `group_id` to avoid reprocessing.

---

## Error Recovery Playbook

| Scenario | Recovery |
|----------|----------|
| **Kafka broker failover** | Pipe auto-retries. If stuck > 5 min, pause then resume: `ALTER PIPE ... SET PIPE_EXECUTION_PAUSED = true` then `false` |
| **Consumer group offset expired** (data loss on resume) | Recreate Pipe with `RESET_KAFKA_GROUP_OFFSETS = '<epoch_millis>'` to replay from a known timestamp |
| **Pipe job keeps failing** (bad message) | Check `MAX_SKIP_BATCH_COUNT_ON_ERROR` (default 30). If exceeded, Pipe pauses. Fix data or increase skip count via drop + recreate |
| **Duplicate data after recreate** | Caused by setting `RESET_KAFKA_GROUP_OFFSETS` unnecessarily. Omit it to continue from last committed offset |
| **Target table schema mismatch** | Pipe will fail if SELECT output doesn't match table columns. ALTER TABLE + recreate Pipe |
| **Lakehouse service upgrade** | Pipe jobs may failover temporarily. Auto-recovers. No action needed |
| **VCluster suspended** | Set `AUTO_SUSPEND_IN_SECOND = 0` for Pipe VClusters, or resume manually: `ALTER VCLUSTER ... RESUME` |

---

## Troubleshooting

| Error | Cause & Fix |
|-------|-------------|
| `Syntax error at or near '('` | Using `TABLE(READ_KAFKA(...))` or `=>` named params. Use positional: `FROM read_kafka(...)` |
| `cannot resolve column` | Using `=` assignment (e.g., `KAFKA_BROKER = 'x'`). READ_KAFKA is positional only |
| No data from exploration | Wrong broker/port/topic, or offset is `latest`. Add `'kafka.auto.offset.reset','earliest'` to MAP |
| Pipe created, no data loading | Check `DESC PIPE EXTENDED` — may be paused, or group offset is at latest with no new messages |
| `Syntax error at or near 'SELECT'` (Table Stream Pipe) | Using `COPY INTO ... SELECT`. Table Stream Pipe must use `INSERT INTO ... SELECT` |
| `AlreadyExist` on CREATE OR REPLACE PIPE | Not supported. Use `DROP PIPE` + `CREATE PIPE` |
| SASL auth failure | Confirm protocol is `SASL_PLAINTEXT` (not SSL). Check mechanism/username/password in MAP |
| `COPY_JOB_HINT` params lost | SET overwrites all hints. Include all keys in one JSON string |

---

## Execution via cz-cli

All operations use `cz-cli sql --sync`. Examples:

```bash
# Explore topic
cz-cli sql "SELECT value::string FROM read_kafka('broker:9092','topic','','test','','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest')) LIMIT 5" --sync

# Create table
cz-cli sql "CREATE TABLE IF NOT EXISTS ods.my_table (id STRING, ts TIMESTAMP)" --sync

# Create Pipe
cz-cli sql "CREATE PIPE my_pipe VIRTUAL_CLUSTER='pipe_vc' BATCH_INTERVAL_IN_SECONDS='60' AS COPY INTO ods.my_table FROM (SELECT j['id']::STRING, CAST(\`timestamp\` AS TIMESTAMP) FROM (SELECT \`timestamp\`, parse_json(value::string) AS j FROM read_kafka('broker:9092','topic','','cz_group','','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT'))))" --sync

# Check status
cz-cli sql "DESC PIPE EXTENDED my_pipe" --sync

# Pause
cz-cli sql "ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = true" --sync

# Resume
cz-cli sql "ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = false" --sync

# Drop and recreate (to change logic)
cz-cli sql "DROP PIPE my_pipe" --sync
cz-cli sql "CREATE PIPE my_pipe ..." --sync
```

> For multi-statement workflows, chain `cz-cli sql` calls in a shell script. Each statement must be a separate invocation.

---

## Reference Documentation

- [Pipe Overview](https://www.yunqi.tech/documents/pipe-summary)
- [Continuous Import with read_kafka](https://www.yunqi.tech/documents/pipe-kafka)
- [Kafka External Table + Table Stream](https://www.yunqi.tech/documents/pipe-kafka-table-stream)
- [Best Practice: Kafka Pipe Tuning](https://www.yunqi.tech/documents/pipe-kafka-bestpractice-1)
- [read_kafka Function](https://www.yunqi.tech/documents/read_kafka)
- [Kafka External Table](https://www.yunqi.tech/documents/kafka-external-table)
- [Kafka Storage Connection](https://www.yunqi.tech/documents/Kafka_connection)
- [PIPE Syntax](https://www.yunqi.tech/documents/pipe-syntax)

> **Syntax details** (parameter tables, DDL templates, MAP options): see `references/kafka-pipe-syntax.md`
