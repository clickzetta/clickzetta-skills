# Table Stream

Table Stream is the change data capture (CDC) mechanism in Lakehouse. It captures INSERT, UPDATE, and DELETE changes on a table for downstream tasks to consume.

For a detailed introduction, see [Table Stream Object Model](om-table-stream.md).

---

## In This Chapter

| Page | Description |
|------|-------------|
| [TABLE STREAM Overview](tablestream_summary.md) | Full concepts, how it works, and best practices |
| [CREATE TABLE STREAM](create-table-stream.md) | Create a stream; supports STANDARD and APPEND_ONLY modes |
| [DESC TABLE STREAM](desc-table-stream.md) | View stream details, including offset position and stale status |
| [SHOW TABLE STREAMS](show-table-streams.md) | List all streams in the current schema |
| [DROP TABLE STREAM](drop-table-stream.md) | Drop a stream (source table data is unaffected) |

---

## Common Operations

### Create a Stream

```SQL
-- STANDARD mode: captures all DML changes (INSERT / UPDATE / DELETE)
CREATE TABLE STREAM orders_stream
    ON TABLE orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- APPEND_ONLY mode: captures only INSERT; suited for append-only log tables
CREATE TABLE STREAM events_stream
    ON TABLE events
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

### Consume a Stream

```SQL
-- Consume via INSERT INTO ... SELECT; offset advances automatically
INSERT INTO dwd_orders
SELECT order_id, user_id, amount, status
FROM orders_stream;
```

> ⚠️ **Note**: SELECT alone does not consume: querying a stream without a DML statement does not advance the offset. The offset only advances through DML operations (INSERT/MERGE).

> ⚠️ **Note**: WHERE filters cause data loss: changes filtered out are permanently lost and cannot be re-consumed. When selective consumption is needed, write all changes to an intermediate table first, then filter.

### View and Drop

```SQL
-- List streams
SHOW TABLE STREAMS;

-- View stream details (including offset and stale status)
DESC TABLE STREAM orders_stream;

-- Drop a stream
DROP TABLE STREAM orders_stream;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Table Stream Object Model](om-table-stream.md) | Core concepts, selection scenarios, FAQs, cost notes |
| [Table Stream Best Practices](lakehouse-table-stream-best-practices.md) | Configuration recommendations for production environments |
| [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md) | Comparison of Pipe / Stream / Dynamic Table |
