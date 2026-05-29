# Table Stream

Table Stream is the Lakehouse's **change data capture (CDC) mechanism**. It captures INSERT, UPDATE, and DELETE changes on a table for downstream jobs to consume.

Think of a Table Stream as a "change log subscription" for a table — you subscribe to a table's stream, and each time you consume it via a DML statement, the offset advances automatically. The next read only returns changes that occurred after the last consumption.

![](/.topwrite/assets/12-table-stream.svg)

## Core Concepts

**Offset**: The stream records the position of the last consumption. After each DML consumption, the offset advances automatically. Running a `SELECT` alone does not advance the offset.

**Change type column**: Stream query results include a `__change_type` metadata column with values `INSERT`, `UPDATE_BEFORE`, `UPDATE_AFTER`, or `DELETE`.

**STANDARD mode**: Captures all DML changes (INSERT + UPDATE + DELETE). An UPDATE produces two rows: `UPDATE_BEFORE` (old value) and `UPDATE_AFTER` (new value).

**APPEND_ONLY mode**: Captures only INSERT operations. UPDATE and DELETE are not recorded, making it more lightweight.

> ⚠️ **Note**: Even if a WHERE clause filters out some rows, the stream's offset still advances after a DML consumption. Filtered-out change records are permanently lost and cannot be re-consumed.

## Use Cases and Selection Guide

### Suitable Scenarios

| Scenario | Reason |
|---|---|
| Incremental ETL processing | Only processes new or changed data from the source table, avoiding full table scans |
| Real-time data sync | Syncs Lakehouse table changes to downstream systems (e.g., Elasticsearch, ClickHouse) |
| Auditing and compliance | Records data change history to meet audit requirements |

### Unsuitable Scenarios

| Scenario | Recommended Alternative | Reason |
|---|---|---|
| Continuously importing data from Kafka/OSS | [Pipe](pipe-introduction.md) | Pipe is designed for continuous ingestion from external data sources |
| Automatically maintaining aggregation results | [Dynamic Table](om-dynamic-table.md) | Dynamic Tables automatically compute and store results incrementally |
| Syncing an external database CDC into the Lakehouse | Studio real-time sync job | Connects directly to MySQL/PostgreSQL binlog without an intermediate layer |

## Quick Example

### Creating a Stream and Consuming Changes

```sql
-- Create source table
CREATE TABLE IF NOT EXISTS orders_cdc (
    order_id   BIGINT,
    user_id    BIGINT,
    amount     DECIMAL(10,2),
    status     STRING
);

-- Create Stream (STANDARD mode)
CREATE TABLE STREAM orders_stream
    ON TABLE orders_cdc
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Insert initial data
INSERT INTO orders_cdc VALUES (1, 101, 99.00, 'created');

-- Query the Stream to see the INSERT change
SELECT order_id, user_id, amount, status, __change_type
FROM orders_stream;
-- Result:
-- +----------+---------+--------+---------+---------------+
-- | order_id | user_id | amount | status  | __change_type |
-- +----------+---------+--------+---------+---------------+
-- | 1        | 101     | 99.00  | created | INSERT        |
-- +----------+---------+--------+---------+---------------+

-- Create target table and consume the Stream (offset advances automatically)
CREATE TABLE IF NOT EXISTS dwd_orders (
    order_id BIGINT, user_id BIGINT, amount DECIMAL(10,2), status STRING
);

INSERT INTO dwd_orders
SELECT order_id, user_id, amount, status
FROM orders_stream;

-- Query the Stream again — it should be empty (offset has advanced)
SELECT COUNT(*) AS cnt FROM orders_stream;
-- Result:
-- +-----+
-- | cnt |
-- +-----+
-- | 0   |
-- +-----+
```

### Capturing UPDATE and DELETE

```sql
-- Update the source table
UPDATE orders_cdc SET status = 'completed' WHERE order_id = 1;

-- Delete a record from the source table
DELETE FROM orders_cdc WHERE order_id = 1;

-- Query the Stream (SELECT does not advance the offset; all unconsumed changes accumulate)
SELECT order_id, status, __change_type FROM orders_stream ORDER BY __change_type;
-- Result:
-- +----------+-----------+---------------+
-- | order_id | status    | __change_type |
-- +----------+-----------+---------------+
-- | 1        | completed | DELETE        |
-- | 1        | completed | UPDATE_AFTER  |
-- | 1        | created   | UPDATE_BEFORE |
-- +----------+-----------+---------------+
```

## Offset Advancement Rules

| Operation | Offset Advances? | Notes |
|---|---|---|
| `SELECT * FROM stream` | No | View only; data remains for the next query |
| `INSERT INTO ... SELECT ... FROM stream` | Yes | Advances after DML consumption |
| `MERGE INTO ... USING stream ...` | Yes | Advances after DML consumption |
| Transaction rollback | No | Data remains; can be re-consumed next time |

> ⚠️ **Note**: A stream can only be fully consumed by one consumer. Once job A consumes the stream via DML and the offset advances, job B querying the same stream will no longer see that batch of changes. If multiple downstream consumers need to process changes from the same table, create a separate stream for each consumer.

## Common Issues

### Issue 1: WHERE Filter Causes Data Loss

**Problem**: `INSERT INTO target SELECT ... FROM stream WHERE __change_type = 'INSERT'` filters out UPDATE/DELETE changes.

**Symptom**: The filtered UPDATE/DELETE changes are permanently lost and cannot be re-consumed.

**Solution**:
- The stream's offset advances after DML consumption regardless of the WHERE clause
- If you need selective consumption, first write all changes to an intermediate table, then filter and process from there

### Issue 2: Stream Becomes Stale

**Problem**: The stream has not been consumed for a long time, exceeding the source table's Time Travel retention period.

**Symptom**: The stream enters a STALE state and can no longer be read.

**Solution**:
- The stream consumption frequency should be much shorter than the source table's `data_retention_days` (default: 1 day)
- For important tables, set `data_retention_days` to 7 days or longer

### Issue 3: Incorrect Use of APPEND_ONLY Mode

**Problem**: The source table has UPDATE/DELETE operations, but the stream was created in APPEND_ONLY mode.

**Symptom**: UPDATE/DELETE changes are not captured, causing downstream data inconsistency.

**Solution**:
- Use APPEND_ONLY only for append-only scenarios (e.g., log tables) where performance is a priority
- Use STANDARD mode when you need to capture all changes

## Cost Implications

### Storage Cost

- A stream does not store data itself — it only stores the offset (metadata), so the cost is negligible
- Multiple streams share the same source table's historical versions; the additional cost is minimal

### Compute Cost

- Stream queries consume VCluster CRU, proportional to the amount of data queried
- STANDARD mode has higher overhead than APPEND_ONLY mode (all changes must be tracked)

> 💡 **Tip**: For detailed billing rules, refer to the [Billing Documentation](Billing.md).

## Lifecycle Management

```
Create Stream → Source Table Changes → DML Consumption (offset advances) → Stream Expires/Dropped
      ↓                  ↓                       ↓                                ↓
  Record offset   INSERT/UPDATE/DELETE       Offset auto-advances         Exceeds retention or
                  changes captured                                         manually dropped
```

### Creating and Dropping

```sql
-- Create a Stream
CREATE TABLE STREAM my_stream
    ON TABLE my_source
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- List all Streams
SHOW TABLE STREAMS;

-- Drop a Stream (does not affect source table data)
DROP TABLE STREAM my_stream;
```

## Related Documentation

- [Table Stream Overview](tablestream_summary.md) — Full concepts and principles
- [CREATE TABLE STREAM](create-table-stream.md) — Complete SQL syntax
- [Table Stream Best Practices](lakehouse-table-stream-best-practices.md)
- [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md) — Choosing between Pipe, Stream, and Dynamic Table
