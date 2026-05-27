# Table Stream

Table Stream is the Lakehouse's **Change Data Capture (CDC)** mechanism, used to capture INSERT, UPDATE, and DELETE changes occurring on a table for downstream task consumption.

Analogy: a Table Stream is like a "change log subscription" on a table — you subscribe to a table's stream, and each time you consume from it, you only get the change records added since the last consumption.

## Core Concepts

**Offset**: The stream records the position up to which it has been consumed. After each query against the stream, the offset automatically advances, and the next query only returns newly added changes.

**Change Type Column**: Stream query results include a `_change_type` column with values of `INSERT`, `UPDATE_BEFORE`, `UPDATE_AFTER`, or `DELETE`.

> ⚠️ **Important**: Even if a WHERE clause filters out some rows, the stream's offset will still advance. Filtered-out change data is permanently lost and cannot be re-consumed.

## Comparison with Pipe

| Scenario | Recommended Solution |
|------|---------|
| Continuously import data from Kafka/OSS | [Pipe](pipe-introduction.md) |
| Capture changes from Lakehouse tables to drive downstream processing | Table Stream |
| CDC sync of external database changes to Lakehouse | Studio real-time sync task |

## Typical Usage: Stream + Dynamic Table

```sql
-- 1. Create a stream on the source table
CREATE TABLE STREAM orders_stream ON TABLE orders;

-- 2. Create a dynamic table to consume the stream for incremental UPSERT
CREATE DYNAMIC TABLE dwd_orders
TARGET_LAG = '1 MINUTE'
AS
SELECT order_id, user_id, amount, _change_type
FROM orders_stream
WHERE _change_type IN ('INSERT', 'UPDATE_AFTER');
```

## Related Documentation

- [Table Stream Feature Introduction](tablestream_summary.md)
- [Create Table Stream](create-table-stream.md)
- [Table Stream Best Practices](lakehouse-table-stream-best-practices.md)
- [Real-time Data Pipeline Selection Guide](realtime-pipeline-selection-guide.md)
