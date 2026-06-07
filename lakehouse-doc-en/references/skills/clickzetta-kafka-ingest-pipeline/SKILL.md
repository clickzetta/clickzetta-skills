---
name: clickzetta-kafka-ingest-pipeline
description: |
  Build Kafka-to-Lakehouse ingestion pipelines using READ_KAFKA Pipe or Kafka External Table + Table Stream.
  Covers: connection validation, JSON/CSV parsing, Pipe DDL, SASL auth, VCluster sizing, latency monitoring, tuning.
  Trigger when the user says: "Kafka ingestion", "Kafka Pipe", "read_kafka", "Kafka external table",
  "Kafka consumer", "message queue import", "Kafka backlog", "ingest from Kafka",
  "stream data to Lakehouse", "real-time Kafka pipeline", "Kafka to ODS".
  Keywords: Kafka, Pipe, read_kafka, message queue, streaming ingestion, real-time ETL
---

# Kafka Data Ingestion Pipeline Workflow

See [references/kafka-pipe-syntax.md](references/kafka-pipe-syntax.md) for full parameter reference, DDL templates, and MAP options.
See [references/operations.md](references/operations.md) for production tuning, error recovery, troubleshooting, and cz-cli examples.

> **Compatibility**: Requires ClickZetta Lakehouse with Pipe support (v2.0+). All SQL executed via `cz-cli sql --sync`.

## Quick Start (Simple JSON, No Auth)

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

---

## Decision Tree

```
User wants Kafka → Lakehouse ingestion
│
├─ Message format?
│  ├─ JSON (flat)      → Standard path, parse_json + field extraction
│  ├─ JSON (nested)    → Layer-by-layer parse_json unwrapping
│  ├─ CSV              → split(value::string, ',')[N] extraction
│  └─ Avro / Protobuf  → NOT SUPPORTED natively; land as raw BINARY, decode downstream
│
├─ Ingestion path?
│  ├─ READ_KAFKA Pipe (default) — simpler, fewer objects, use for most scenarios
│  └─ Kafka External Table + Table Stream — raw message retention, multi-consumer fan-out
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

Ask three questions: (1) Message format (JSON flat / JSON nested / CSV / Avro/Protobuf)? (2) Ingestion path (READ_KAFKA Pipe / Kafka External Table + Table Stream)? (3) Authentication (None/PLAINTEXT / SASL_PLAINTEXT)?

**If the user has already provided sufficient information, skip the wizard and proceed directly.**

---

## Key Constraints

- Kafka Pipe supports only **PLAINTEXT** and **SASL_PLAINTEXT** (no SSL/mTLS)
- Pipe **starts automatically** after creation — no manual RESUME needed
- Pipe SQL logic cannot be altered — must DROP + CREATE to change the SELECT
- `CREATE OR REPLACE PIPE` is **not supported** — use DROP then CREATE
- `RESET_KAFKA_GROUP_OFFSETS` only takes effect at creation time
- `topic_pattern` (position 3) is **reserved and unused** — always pass empty string `''`
- Use a **dedicated GP VCluster** for Kafka Pipe to avoid resource contention with other workloads

---

## Path One: READ_KAFKA Pipe (Recommended)

### Step 1: Validate Kafka Connection

> ⚠️ READ_KAFKA uses **positional parameters only**. No `=>` named params, no `TABLE()` wrapper.

```sql
SELECT value::string
FROM read_kafka(
  'kafka.example.com:9092',  -- bootstrap_servers
  'orders',                   -- topic
  '',                         -- reserved (always empty)
  'test_explore',             -- group_id (use temp name for exploration)
  '', '', '', '',
  'raw', 'raw', 0,
  MAP('kafka.security.protocol', 'PLAINTEXT', 'kafka.auto.offset.reset', 'earliest')
)
LIMIT 10;
```

For SASL: add `'kafka.sasl.mechanism','PLAIN','kafka.sasl.username','user','kafka.sasl.password','pass'` to MAP.

### Step 2: Explore Schema and Parse Messages

**JSON (flat)**:
```sql
SELECT j['order_id']::STRING, j['amount']::DECIMAL(10,2)
FROM (SELECT parse_json(value::string) AS j
      FROM read_kafka('kafka:9092','orders','','test_schema','','','','','raw','raw',0,
        MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest')) LIMIT 5);
```

**JSON (nested)** — unwrap layer by layer:
```sql
SELECT j['id']::STRING, parse_json(j['event']::STRING)['action']::STRING AS action
FROM (SELECT parse_json(value::string) AS j FROM read_kafka(...) LIMIT 5);
```

**CSV** — use `split()`:
```sql
SELECT split(value::string, ',')[0] AS id, split(value::string, ',')[1] AS name
FROM read_kafka(...) LIMIT 5;
```

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

Always add `__kafka_timestamp__` — it enables end-to-end latency monitoring without which you cannot tell how fresh the data is.

### Step 4: Create Dedicated VCluster

```sql
CREATE VCLUSTER IF NOT EXISTS pipe_kafka_vc
  VCLUSTER_TYPE = GENERAL
  VCLUSTER_SIZE = 4
  AUTO_SUSPEND_IN_SECOND = 0   -- keep always-on to avoid cold-start latency
  COMMENT 'Dedicated always-on cluster for Kafka Pipe';
```

### Step 5: Create Kafka Pipe

```sql
CREATE PIPE kafka_orders_pipe
  VIRTUAL_CLUSTER = 'pipe_kafka_vc'
  BATCH_INTERVAL_IN_SECONDS = '60'
  BATCH_SIZE_PER_KAFKA_PARTITION = '500000'
AS
COPY INTO ods.kafka_orders FROM (
  SELECT
    j['order_id']::STRING, j['user_id']::STRING,
    j['amount']::DECIMAL(10,2), j['status']::STRING,
    j['created_at']::TIMESTAMP,
    CAST(`timestamp` AS TIMESTAMP) AS __kafka_timestamp__
  FROM (
    SELECT `timestamp`, parse_json(value::string) AS j
    FROM read_kafka('kafka.example.com:9092', 'orders', '', 'lakehouse_orders',
      '', '', '', '', 'raw', 'raw', 0,
      MAP('kafka.security.protocol', 'PLAINTEXT'))
  )
);
```

> Inside a Pipe: positional offset params MUST be empty (Pipe manages offsets). Do NOT set `kafka.auto.offset.reset` in MAP.

### Step 6: Verify

```sql
DESC PIPE EXTENDED kafka_orders_pipe;
SELECT COUNT(*) FROM ods.kafka_orders;
SELECT * FROM load_history('ods.kafka_orders') ORDER BY last_load_time DESC LIMIT 10;
```

---

## Path Two: Kafka External Table + Table Stream Pipe

Use when raw message retention is needed, or multiple independent downstream consumers on the same topic.

### Step 1: Create Kafka Storage Connection

```sql
CREATE STORAGE CONNECTION IF NOT EXISTS kafka_conn
  TYPE KAFKA
  BOOTSTRAP_SERVERS = ['kafka.example.com:9092']
  SECURITY_PROTOCOL = 'PLAINTEXT';
```

### Step 2: Create Kafka External Table

```sql
CREATE EXTERNAL TABLE kafka_orders_ext (
  topic STRING, partition INT, `offset` BIGINT, `timestamp` TIMESTAMP,
  timestamp_type STRING, headers STRING, key BINARY, value BINARY
)
USING KAFKA
OPTIONS ('group_id' = 'lakehouse_ext_orders', 'topics' = 'orders', 'starting_offset' = 'earliest')
CONNECTION kafka_conn;
```

> Column definitions are required. `offset` and `timestamp` are reserved words — always backtick-escape. Drop with `DROP TABLE` (not `DROP EXTERNAL TABLE`).

### Step 3: Create Table Stream and Pipe

```sql
CREATE TABLE STREAM kafka_orders_stream ON TABLE kafka_orders_ext
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');

CREATE TABLE IF NOT EXISTS ods.kafka_orders_from_ext (order_id STRING, kafka_ts TIMESTAMP);

-- Table Stream Pipe uses INSERT INTO ... SELECT (not COPY INTO)
CREATE PIPE kafka_ext_orders_pipe
  VIRTUAL_CLUSTER = 'pipe_kafka_vc'
  BATCH_INTERVAL_IN_SECONDS = '60'
AS
INSERT INTO ods.kafka_orders_from_ext
SELECT j['order_id']::STRING, CAST(`timestamp` AS TIMESTAMP)
FROM (SELECT `timestamp`, parse_json(CAST(value AS STRING)) AS j FROM kafka_orders_stream);
```

---

## Monitoring & Operations

```sql
-- Check Pipe status and lag
DESC PIPE EXTENDED kafka_orders_pipe;
-- Key: pipe_latency.timeLag (ms) — continuously increasing = backlog

-- End-to-end latency (requires __kafka_timestamp__)
SELECT MAX(DATEDIFF('second', __kafka_timestamp__, CURRENT_TIMESTAMP())) AS max_delay_s
FROM ods.kafka_orders WHERE __kafka_timestamp__ >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR;

-- Pause / Resume
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = true;
ALTER PIPE kafka_orders_pipe SET PIPE_EXECUTION_PAUSED = false;
```

For production tuning, error recovery, and troubleshooting, see [references/operations.md](references/operations.md).

---

## Schema Evolution

When the Kafka topic adds new fields:
1. `ALTER TABLE ods.kafka_orders ADD COLUMN new_field STRING;`
2. Drop and recreate Pipe with updated SELECT (keep same `group_id`, omit `RESET_KAFKA_GROUP_OFFSETS`)
3. Existing rows will have `NULL` in the new column; new messages will populate it.
