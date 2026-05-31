# Kafka Pipe Troubleshooting & Operations

## Production Tuning

Run `DESC PIPE EXTENDED` multiple times — if `timeLag` continuously increases, the Pipe is backlogged.

| Problem | Fix |
|---|---|
| Batch can't consume a full interval's data | Increase `BATCH_SIZE_PER_KAFKA_PARTITION` (drop + recreate, e.g., `'1000000'`) |
| Job needs multiple rounds | Increase VCluster size so cores ≥ partitions: `ALTER VCLUSTER ... SET VCLUSTER_SIZE = 16` |
| Few partitions, large volume | Split tasks by count: `ALTER PIPE ... SET COPY_JOB_HINT = '{"cz.sql.split.kafka.strategy":"size","cz.mapper.kafka.message.size":"200000"}'` |

**VCluster size-to-core mapping** (GENERAL type, 1 CRU = 8 cores):

| VCLUSTER_SIZE (CRU) | Cores | Suitable for |
|---|---|---|
| 4 | 32 | ≤32 partitions, moderate throughput |
| 8 | 64 | ≤64 partitions, high throughput |
| 16 | 128 | Large-scale ingestion |
| 32 | 256 | Very high partition count / throughput |

Rule of thumb: set cores ≥ Kafka partition count so each partition gets a dedicated task slot.

`COPY_JOB_HINT` must be valid JSON with double-quoted keys/values. Setting it overwrites all previous hints.

## Error Recovery Playbook

| Scenario | Recovery |
|---|---|
| Kafka broker failover | Pipe auto-retries. If stuck >5 min, pause then resume |
| Consumer group offset expired (data loss on resume) | Recreate Pipe with `RESET_KAFKA_GROUP_OFFSETS = '<epoch_millis>'` to replay from a known timestamp |
| Pipe job keeps failing (bad message) | Check `MAX_SKIP_BATCH_COUNT_ON_ERROR` (default 30). If exceeded, Pipe pauses. Fix data or increase skip count via drop + recreate |
| Duplicate data after recreate | Caused by setting `RESET_KAFKA_GROUP_OFFSETS` unnecessarily. Omit it to continue from last committed offset |
| Target table schema mismatch | Pipe fails if SELECT output doesn't match table columns. ALTER TABLE + recreate Pipe |
| VCluster suspended | Set `AUTO_SUSPEND_IN_SECOND = 0` for Pipe VClusters, or resume manually |

## Troubleshooting

| Error | Cause & Fix |
|---|---|
| `Syntax error at or near '('` | Using `TABLE(READ_KAFKA(...))` or `=>` named params. Use positional: `FROM read_kafka(...)` |
| `cannot resolve column` | Using `=` assignment. READ_KAFKA is positional only |
| No data from exploration | Wrong broker/port/topic, or offset is `latest`. Add `'kafka.auto.offset.reset','earliest'` to MAP |
| Pipe created, no data loading | Check `DESC PIPE EXTENDED` — may be paused, or group offset is at latest with no new messages |
| `Syntax error at or near 'SELECT'` (Table Stream Pipe) | Using `COPY INTO ... SELECT`. Table Stream Pipe must use `INSERT INTO ... SELECT` |
| `AlreadyExist` on CREATE OR REPLACE PIPE | Not supported. Use `DROP PIPE` + `CREATE PIPE` |
| SASL auth failure | Confirm protocol is `SASL_PLAINTEXT` (not SSL). Check mechanism/username/password in MAP |
| `COPY_JOB_HINT` params lost | SET overwrites all hints. Include all keys in one JSON string |

## Execution via cz-cli

All operations use `cz-cli sql --sync`:

```bash
# Explore topic
cz-cli sql "SELECT value::string FROM read_kafka('broker:9092','topic','','test','','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT','kafka.auto.offset.reset','earliest')) LIMIT 5" --sync

# Create table
cz-cli sql "CREATE TABLE IF NOT EXISTS ods.my_table (id STRING, ts TIMESTAMP)" --sync

# Create Pipe (escape backticks in shell)
cz-cli sql "CREATE PIPE my_pipe VIRTUAL_CLUSTER='pipe_vc' BATCH_INTERVAL_IN_SECONDS='60' AS COPY INTO ods.my_table FROM (SELECT j['id']::STRING, CAST(\`timestamp\` AS TIMESTAMP) FROM (SELECT \`timestamp\`, parse_json(value::string) AS j FROM read_kafka('broker:9092','topic','','cz_group','','','','','raw','raw',0,MAP('kafka.security.protocol','PLAINTEXT'))))" --sync

# Check status
cz-cli sql "DESC PIPE EXTENDED my_pipe" --sync

# Pause / Resume
cz-cli sql "ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = true" --sync
cz-cli sql "ALTER PIPE my_pipe SET PIPE_EXECUTION_PAUSED = false" --sync

# Drop and recreate (to change logic)
cz-cli sql "DROP PIPE my_pipe" --sync
cz-cli sql "CREATE PIPE my_pipe ..." --sync
```

For multi-statement workflows, chain `cz-cli sql` calls in a shell script — each statement must be a separate invocation.
