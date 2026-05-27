# Pipe

Pipe is Lakehouse's **continuous data ingestion object**. Created via SQL DDL, it runs automatically, continuously reading data from Kafka or object storage (OSS/COS/S3) and writing it to target tables without manual triggering.

Analogy: A Pipe is like an automated conveyor belt — when data files are uploaded to OSS or messages are written to Kafka, the Pipe automatically detects and loads them. No scheduled tasks to configure.

## Comparison with Studio Sync Tasks

| Dimension | Pipe | Studio Sync Task |
|------|------|----------------|
| Creation Method | SQL DDL | Studio visual interface |
| Applicable Sources | Kafka, OSS/COS/S3 | Relational databases, Kafka, object storage |
| Management Method | SQL commands | Studio interface |
| Suitable For | SQL-oriented, code-based management | Prefer visual configuration |

The two are functionally equivalent; choose based on your workflow preference.

## Pipe Types

### Object Storage Pipe (OSS/COS/S3)

Continuously scans for new files in object storage and ingests them:

```sql
CREATE PIPE oss_pipe
  AUTO_INGEST = TRUE
  INGEST_MODE = LIST_PURGE
AS
COPY INTO orders
FROM VOLUME my_oss_volume
USING CSV OPTIONS('header'='true');
```

> Note: The `LIST_PURGE` mode **deletes source files** after ingestion. To keep files, use the `EVENT_NOTIFICATION` mode.

### Kafka Pipe

Continuously consumes Kafka topics and writes to tables:

```sql
CREATE PIPE kafka_pipe AS
INSERT INTO orders
SELECT * FROM TABLE(
    READ_KAFKA(
        'bootstrap.servers' = 'kafka-host:9092',
        'topic' = 'orders'
    )
);
```

## Related Documents

- [Pipe Introduction](pipe-introduction.md)
- [Object Storage Pipe](pipe-storage-object.md)
- [Kafka Pipe](pipe-kafka.md)
- [Pipe Syntax Reference](pipe-syntax.md)
