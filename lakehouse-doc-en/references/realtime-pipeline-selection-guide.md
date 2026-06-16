# Real-Time Data Pipeline Selection Guide

Singdata Lakehouse provides three types of real-time data processing objects: **Pipe** (continuous ingestion), **Table Stream** (change data capture), and **Dynamic Table** (incremental computation). They solve different problems and are often used together, but choosing the wrong one will lead you down unproductive paths.

This article answers two questions: which object suits which scenario, and how to choose for common business requirements.

---

## Positioning of the Three Object Types

| Object | Problem It Solves | Data Flow Direction | Typical Usage |
|--------|-------------------|---------------------|---------------|
| **Pipe** | Continuous flow of external data into Lakehouse | External -> Table | Kafka message ingestion, OSS file loading |
| **Table Stream** | Perceiving data changes within a table (CDC) | Table -> Downstream processing | Change sync, incremental ETL driver |
| **Dynamic Table** | Automatically maintaining real-time processing results | Table -> Processed result table | ODS->DWD->DWS incremental processing chain |

These three are not in competition; they are different stages of a pipeline:

```
External Data Source
    ↓ Pipe (continuous ingestion)
  ODS Table
    ↓ Dynamic Table (incremental processing)
  DWD / DWS Table
    ↓ Table Stream (change perception, driving downstream sync)
  Downstream System / Target Table
```

---

## Selection Decision Tree

**First question: Where does the data come from?**

- From Kafka or object storage (OSS/S3/COS) → Use **Pipe**
- Already in a Lakehouse table → See next question

**Second question: What do you want to do?**

- Process and transform table data, keeping results up-to-date in real time → Use **Dynamic Table**
- Need to perceive row-level changes (INSERT/UPDATE/DELETE) in a table to drive downstream processing → Use **Table Stream**
- Just a one-time or low-frequency import → Use **COPY INTO**, no Pipe needed

**Third question (for Pipe scenarios): Trigger method?**

- Real-time trigger when files are uploaded (minute-level latency) → **EVENT_NOTIFICATION mode** (requires message queue configuration)
- No real-time requirement; periodic scanning with original file deletion is acceptable → **LIST_PURGE mode** (simple configuration)

---

## Pipe: Suitable for Continuous Ingestion, Not Batch Import

### Scenarios Suitable for Pipe

- Kafka Topic data continuously writing to Lakehouse tables
- OSS/S3 files being continuously uploaded with automatic loading needed
- Data sources produce data continuously, requiring the system to automatically maintain read positions

### Scenarios NOT Suitable for Pipe

- One-time historical data import → Use `COPY INTO` directly
- Low-frequency (once daily) batch sync → Scheduling `COPY INTO` tasks is simpler
- Strictly ordered data processing is required → **Pipe does not guarantee load order**

### Pipe vs COPY INTO Comparison

| | Pipe | COPY INTO (Scheduled) |
|-|------|-----------------------|
| Suitable Scenario | Data flows continuously; new files auto-processed | Low-frequency batch import, one-time migration |
| Trigger Method | File event-driven or periodic scanning | Manual or external scheduling system trigger |
| Read Position Management | System auto-maintains (load_history) | Caller must manage on their own |
| File Deduplication | Auto dedup (same path + same filename = imported once) | No built-in dedup; repeated execution = repeated import |
| Ops Complexity | Auto-runs after creation, no intervention needed | Requires schedule config, execution monitoring |
| Compute Resources | Requires VCluster online | Requires VCluster online |

**File Deduplication Behavior**: Pipe records imported files via `load_history` (retained for 7 days). Files with the same path and filename are imported only once. If you need to re-import a file, you must manually execute `COPY INTO`.

**File Size Recommendations**:
- gzip-compressed files: recommended within 50MB
- CSV / Parquet uncompressed: recommended 128MB to 256MB

Files that are too small increase scheduling overhead; files that are too large affect single-batch loading time.

### Pipe: Two Mode Choices

| | EVENT_NOTIFICATION | LIST_PURGE |
|-|--------------------|------------|
| Latency | Minute-level (event-triggered) | Depends on scan interval |
| Configuration Complexity | Requires message queue config (Alibaba Cloud MNS / AWS SQS) | Simple, no extra config needed |
| Original File Handling | Preserves original files | **Deletes original files after import** |
| Suitable Scenario | Latency-sensitive, files need to be preserved | Low latency requirement, file deletion acceptable |
| Cloud Provider Support | Alibaba Cloud OSS, AWS S3 | All object storage |

> ⚠️ **Note**: LIST_PURGE mode deletes source files after successful import. Confirm that your scenario allows deletion of original files before using this mode.

---

## Table Stream: Suitable for Perceiving Changes, Not Direct Queries

### Scenarios Suitable for Table Stream

- Need to capture INSERT / UPDATE / DELETE changes on a source table and sync to a target system
- Incremental ETL: only process data that is "new/changed since last processing," avoiding full scans
- Driving SCD (Slowly Changing Dimension) maintenance
- Listening for OSS file arrival events (Volume Stream)

### Scenarios NOT Suitable for Table Stream

- Only need to query current data → Query the table directly, no Stream needed
- Only need to capture new data, not updates or deletes → Use **APPEND_ONLY mode**, better performance
- Need real-time data processing with maintained result updates → Use **Dynamic Table**

### STANDARD vs APPEND_ONLY?

| | STANDARD | APPEND_ONLY |
|-|---------|-------------|
| Captured Operations | INSERT, UPDATE, DELETE | INSERT only |
| UPDATE Representation | UPDATE_BEFORE + UPDATE_AFTER (two rows) | Not recorded (only original insert value) |
| Suitable Scenario | Need to handle updates and deletes (e.g., MERGE sync) | Append-only log data, pursue performance |
| Performance | Higher overhead (tracking all changes) | Lighter weight |

### Offset Advancement Rules (Important)

Table Stream offsets advance **only after a DML transaction containing the Stream commits successfully**.

- `SELECT * FROM stream` → **Does not advance** offset; data remains available next query
- `INSERT INTO target SELECT ... FROM stream` → Offset advances after transaction commit; data is consumed
- Transaction rollback → No advancement; data remains

This means: if you only SELECT to view Stream data, the offset does not change; you must consume data through DML operations that include the Stream to advance the offset.

### Multi-Consumer Pattern

**One Stream can only be fully consumed by one consumer**. When Task A consumes the Stream via DML, the offset advances, and Task B querying the same Stream will no longer see that batch of changes.

If multiple downstream tasks all need to consume changes from the same table, **create a separate Stream for each consumer**:

```sql
-- Enable change tracking on the table
ALTER TABLE orders SET PROPERTIES ('change_tracking' = 'true');

-- Create a Stream for each consumer
CREATE TABLE STREAM orders_stream_for_dw
    ON TABLE orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

CREATE TABLE STREAM orders_stream_for_notify
    ON TABLE orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

Each Stream independently maintains its own offset, without interfering with others. Streams only store offsets, not a copy of the data, so the additional cost of creating multiple Streams is very low.

### Data Retention Period and Stream Invalidation

Table Stream relies on the source table's historical version data (Time Travel) to return change records. If a Stream is not consumed for a long time and the source table's historical versions are cleaned up (exceeding `DATA_RETENTION_DAYS`, default 7 days), the Stream will become unavailable.

Daily recommendation: the Stream consumption frequency should be much shorter than the source table's `DATA_RETENTION_DAYS` to avoid Stream invalidation due to historical version loss.

---

## Dynamic Table: Suitable for Declarative Incremental Processing, Not High-Real-Time Requirements

### Scenarios Suitable for Dynamic Table

- Multi-layer ETL processing chains: ODS -> DWD -> DWS
- Query performance optimization: materialize complex computation results, avoiding recalculation on each query
- Near-real-time analysis with fixed dimensions, tolerating minute-level latency

### Scenarios NOT Suitable for Dynamic Table

- Sub-second real-time requirements → Current minimum refresh interval is 1 minute
- SQL with extensive ORDER BY → Incremental refresh is limited; degrades to full refresh
- Extensive Outer Joins with frequently changing right-side tables → Low incremental computation efficiency
- Need to directly modify data (UPDATE/DELETE/TRUNCATE) → Dynamic Table does not support this

### Refresh Mode Selection

Singdata Dynamic Table supports three refresh scheduling methods:

| Scheduling Method | Suitable Scenario | Characteristics |
|-------------------|-------------------|-----------------|
| DDL-defined refresh interval (`REFRESH INTERVAL`) | Simple scenarios, quick launch | No upstream/downstream dependency support; min interval 1 minute |
| Lakehouse Studio scheduling | Multi-layer DT chains, dependency control needed | Supports task dependencies (A completes then triggers B); monitoring and alerting |
| Third-party scheduling engine | Existing scheduling system, flexible control needed | Time interval not limited, but introduces external dependency |

**Key Constraint for Multi-Layer Chains**: The upstream DT's refresh frequency determines the minimum latency achievable by the downstream DT. If upstream refreshes every 5 minutes, downstream latency will be at least 5 minutes even if set to 1 minute.

### Freshness vs Cost Trade-off

More frequent refreshing means fresher data but higher compute costs. Method for determining a reasonable refresh interval:

1. Assess business tolerance for data latency ("Is 5-minute-old data acceptable?")
2. Check single refresh duration (`SHOW DYNAMIC TABLE REFRESH HISTORY`)
3. Refresh interval > single refresh duration to avoid task backlog
4. If refresh duration approaches the interval, incremental computation may have degraded to full; optimize SQL or extend the interval

### Incremental Refresh vs Full Refresh

Dynamic Table automatically selects incremental or full mode:

- **Incremental Refresh (INCREMENTAL)**: Only computes data changed since the last refresh; high efficiency
- **Full Refresh (FULL)**: Recomputes all data; suitable for initial refresh or when incremental conditions are not met

The following situations trigger full refresh or prevent incremental computation:
- SQL contains operators that cannot be incrementally processed (e.g., window functions with ORDER BY)
- First-time `REFRESH DYNAMIC TABLE`
- Source table changes are too large (approaching full data volume)

Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to view the `refresh_mode` field for each refresh, confirming whether incremental mode was successfully used.

---

## Typical Architecture Patterns

### Pattern 1: Kafka Real-Time Ingestion + Incremental Processing

Suitable for: log analysis, real-time dashboards, user behavior analysis

```
Kafka Topic
    ↓ Pipe (continuous ingestion)
  ods.events table
    ↓ Dynamic Table (1-minute incremental aggregation)
  dwd.event_stats table
    ↓ Dynamic Table (5-minute summarization)
  dws.daily_summary table
```

**End-to-End SQL Example** (replace table names and connection names with actual values):

```SQL
-- Pattern 1 complete example: Kafka log real-time ingestion + dynamic table incremental aggregation
-- Assumes existing Kafka Connection: kafka_conn, Topic: app_events

-- Step 1: Create target table (ODS layer)
CREATE TABLE IF NOT EXISTS ods.app_events (
    event_id    STRING,
    user_id     BIGINT,
    event_type  STRING,
    page        STRING,
    ts          TIMESTAMP
);

-- Step 2: Create Pipe for continuous Kafka consumption
CREATE PIPE ods.kafka_events_pipe AS
    COPY INTO ods.app_events
    FROM READ_KAFKA(
        CONNECTION => 'kafka_conn',
        TOPIC => 'app_events'
    ) USING JSON;

-- Step 3: Create Dynamic Table for minute-level aggregation (DWD layer)
CREATE DYNAMIC TABLE dwd.event_stats
    REFRESH INTERVAL 1 MINUTE VCLUSTER DEFAULT
AS
SELECT
    DATE_TRUNC('minute', ts)  AS minute,
    event_type,
    COUNT(*)                  AS event_cnt,
    COUNT(DISTINCT user_id)   AS uv
FROM ods.app_events
GROUP BY 1, 2;

-- Query results (after refresh)
SELECT * FROM dwd.event_stats ORDER BY minute DESC LIMIT 5;
```

The Pipe auto-runs after creation; no manual trigger is needed. The Dynamic Table auto-refreshes incrementally every minute, processing only events newly added since the last refresh.

### Pattern 2: OSS File Auto-Loading + Incremental Processing

Suitable for: IoT device data, log archiving, batch file processing

```
OSS Bucket (new files continuously uploaded)
    ↓ Pipe EVENT_NOTIFICATION (minute-level trigger)
  ods.raw_files table
    ↓ Dynamic Table (incremental parsing/cleaning)
  dwd.cleaned_data table
```

### Pattern 3: Table Stream-Driven Cross-System Sync

Suitable for: syncing Lakehouse internal table changes to external systems, SCD maintenance

```
source_table (business table)
    ↓ Table Stream (STANDARD mode)
  MERGE INTO target (Studio scheduled task, consuming every minute)
  target_table (sync target)
```

**End-to-End SQL Example** (replace table names with actual values):

```SQL
-- Pattern 3 complete example: Table Stream-driven incremental sync
-- Scenario: sync changes from orders table to orders_replica (cross-schema sync)

-- Step 1: Create STANDARD mode Stream on the source table
CREATE TABLE STREAM orders_sync_stream
    ON TABLE ods.orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Step 2: Create target replica table (same structure as source)
CREATE TABLE IF NOT EXISTS dwd.orders_replica
    AS SELECT * FROM ods.orders WHERE 1=0;  -- Copy structure only, not data

-- Step 3: Studio scheduled task (executes every minute)
MERGE INTO dwd.orders_replica t
USING orders_sync_stream s ON t.order_id = s.order_id
WHEN MATCHED AND s.__change_type = 'UPDATE_AFTER'
    THEN UPDATE SET t.status = s.status, t.amount = s.amount
WHEN MATCHED AND s.__change_type = 'DELETE'
    THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT'
    THEN INSERT VALUES (s.order_id, s.customer_id, s.product,
                        s.amount, s.status, s.order_date);
-- UPDATE_BEFORE rows are automatically ignored
```

The Stream's offset advances automatically after MERGE commits successfully. If MERGE fails (transaction rollback), the offset does not advance, and the next execution will re-consume the same batch of changes, ensuring no data loss.

### Pattern 4: Volume Stream Monitoring File Changes

Suitable for: image/document AI processing, incremental file analysis

```
OSS Bucket (new images uploaded)
    ↓ Volume Stream (based on Directory Table)
  INSERT INTO (consume Stream, invoke AI functions for processing)
  results table
```

---

## Related Documents

- [Pipe Continuous Ingestion Overview](pipe-summary.md)
- [Using Pipe for Continuous Object Storage Data Ingestion](pipe-storage-object.md)
- [Table Stream Introduction](tablestream_summary.md)
- [Table Stream Best Practices](lakehouse-table-stream-best-practices.md)
- [Dynamic Table Introduction](dynamic_table_summary.md)
- [Dynamic Table Refresh Scheduling](dynamic-table-scheduling.md)
- [Incremental Computing Overview](streaming_data_pipeline_overview.md)
- [Developing Dynamic Tables for Near-Real-Time Incremental Processing](streaming_pipeline_with_dynamic_table.md)
- [Implementing SCD with Streams and Tasks](slowly-changing-dimensions-with-streams-and-tasks.md)
