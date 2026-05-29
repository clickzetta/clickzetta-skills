# Pipe Continuous Ingestion

Pipe is Singdata Lakehouse's continuous data ingestion pipeline object, used to continuously import data from Kafka or object storage (OSS/S3/COS) into Lakehouse tables.

You can think of Pipe as an automated conveyor belt: after data files are uploaded to OSS/S3/COS or messages are written to Kafka, Pipe automatically detects and ingests them into the warehouse without manual triggering or configuring scheduled tasks.

**Selection Guide**: If you are accustomed to managing data pipelines with SQL, choose Pipe. If you need to connect to relational databases (MySQL/PostgreSQL, etc.), or prefer visual configuration, choose Studio sync tasks.

## What Is a Pipe

A Pipe is a SQL object created via DDL statements. Once created, the Pipe runs continuously, automatically reading data from the data source and writing it to the target table.

**Differences from Studio Sync Tasks**:

| Dimension | Pipe | Studio Sync Task |
|---|---|---|
| Creation Method | SQL DDL | Studio visual interface |
| Management Method | SQL commands | Studio interface + cz-cli |
| Applicable Scenarios | Familiar with SQL, need code-based pipeline management | Prefer visual configuration, or need to connect to relational databases |
| Data Sources | Kafka, object storage | Relational databases, Kafka, object storage |

The two are functionally equivalent; choose based on your usage habits.

## Pipe Types

### Kafka Pipe

Continuously consumes data from a Kafka topic and writes it to a Lakehouse table.

```sql
CREATE PIPE kafka_pipe AS
  COPY INTO orders FROM READ_KAFKA(...) USING JSON;
```

**Two Ingestion Paths**:
1. **READ_KAFKA Pipe** (Recommended): Uses the `READ_KAFKA()` function directly in the Pipe
2. **Kafka External Table + Table Stream**: First create a Kafka external table, then consume via Table Stream

### Object Storage Pipe

Continuously scans new files from OSS/S3/COS and imports them.

```sql
CREATE PIPE oss_pipe
    VIRTUAL_CLUSTER = 'default'
    INGEST_MODE = 'LIST_PURGE'
    AS COPY INTO orders FROM VOLUME my_volume USING CSV PURGE = TRUE;
```

**Comparison of Two Scan Modes**:

| Dimension | LIST_PURGE | EVENT_NOTIFICATION |
|------|-----------|-------------------|
| Trigger Method | Periodic polling scan of directory | Object storage event notification (near real-time trigger) |
| Supported Clouds | OSS, S3, COS | OSS, S3 only |
| Authorization Method | Secret key or Role ARN | Role ARN only |
| Source File Processing | **Auto-deletes source files after successful import** (requires `PURGE = TRUE`) | Preserves source files |
| Configuration Complexity | Simple, no extra configuration needed | Requires MNS queue configuration |

> ⚠️ **Warning**: `LIST_PURGE` mode **permanently deletes** the source files in object storage after successful import. If you need to preserve the original files, use `EVENT_NOTIFICATION` mode.

> ⚠️ **Note**: Each Pipe must correspond to an independent Volume. Pipe COPY statements do not support `FILES`, `SUBDIRECTORY`, or `REGEXP` parameters.

## Pipe Lifecycle

```
Create Pipe --> Auto Run --> Continuous Ingestion
     |              |
     v              v
  Suspend Pipe   Monitor Status
     |
     v
  Resume Pipe
```

## Monitoring Pipes

```sql
-- Check Pipe status
SHOW PIPES;

-- View Pipe details
DESC PIPE my_pipe;
```

## Applicable Scenarios

- **Kafka Real-time Ingestion**: Log data, business events written in real time
- **Object Storage Batch Import**: Regularly uploaded CSV/JSON/Parquet files automatically ingested
- **Replace Scheduled Tasks**: No need to configure Cron; Pipe runs continuously

## Related Documents

- [Pipe Introduction](pipe-summary.md)
- [Kafka Pipe](pipe-kafka.md)
- [Object Storage Pipe](pipe-storage-object.md)
- [Pipe Syntax](pipe-syntax.md)
