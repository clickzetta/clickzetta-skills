# Table Stream SQL Reference

> **⚠️ ClickZetta-specific syntax**
> - Creation syntax is `CREATE TABLE STREAM`, with parameters inside `WITH PROPERTIES (...)`
> - Metadata field is `__change_type` (double underscore), values: `INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`
> - UPDATE produces two records: `UPDATE_BEFORE` (before update) and `UPDATE_AFTER` (after update)
> - Typically only `UPDATE_AFTER` and `INSERT` are needed; `UPDATE_BEFORE` can be ignored

Table Stream captures change data (INSERT / UPDATE / DELETE) from a source table and is the core object for building CDC pipelines. It is typically consumed by Dynamic Tables or SQL tasks.

## CREATE TABLE STREAM

```sql
CREATE [ OR REPLACE ] TABLE STREAM [ IF NOT EXISTS ] <stream_name>
  ON TABLE <source_name>
  [ TIMESTAMP AS OF <timestamp_expr> ]
  [ COMMENT '<comment>' ]
  WITH PROPERTIES (
    'TABLE_STREAM_MODE' = 'STANDARD | APPEND_ONLY',
    'SHOW_INITIAL_ROWS' = 'TRUE | FALSE'
  );
```

**Key parameters:**
- `TABLE_STREAM_MODE = STANDARD` (default): captures all changes — INSERT, UPDATE, DELETE — each row includes a `__change_type` field (`INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`)
- `TABLE_STREAM_MODE = APPEND_ONLY`: captures INSERT only; better performance, suitable for append-only source tables
- `SHOW_INITIAL_ROWS = TRUE`: first consumption returns rows already in the table when the Stream was created; `FALSE` (default) returns only new changes after Stream creation
- `TIMESTAMP AS OF`: specifies the point in time from which the Stream starts capturing changes

**Examples:**
```sql
-- Create a standard stream on a regular table (captures all changes; change_tracking must be enabled first)
ALTER TABLE ods.orders SET PROPERTIES ('change_tracking' = 'true');

CREATE TABLE STREAM orders_stream
  ON TABLE ods.orders
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Append-only stream
CREATE TABLE STREAM events_stream
  ON TABLE dw.events
  COMMENT 'Event stream, append only'
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');

-- Start capturing from a specific timestamp
CREATE TABLE STREAM orders_stream_from_ts
  ON TABLE ods.orders
  TIMESTAMP AS OF '2024-01-01 00:00:00'
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD', 'SHOW_INITIAL_ROWS' = 'TRUE');
```

## Consuming a Table Stream

The Table Stream offset advances through DML operations. **SELECT alone does not advance the offset** — you can query repeatedly for preview. Executing DML (INSERT INTO / MERGE INTO / UPDATE / DELETE) consumes the data and advances the offset.

```sql
-- View current unconsumed change data (does not advance offset)
SELECT * FROM orders_stream;

-- System fields included in change data:
-- __change_type: INSERT | UPDATE_BEFORE | UPDATE_AFTER | DELETE
-- __commit_version: change version number
-- __commit_timestamp: time the change occurred

-- Typical usage: MERGE change data into target table (filter out UPDATE_BEFORE)
MERGE INTO dw.orders_dim AS target
USING (
  SELECT * FROM orders_stream
  WHERE __change_type != 'UPDATE_BEFORE'
) AS src
ON target.order_id = src.order_id
WHEN MATCHED AND src.__change_type = 'UPDATE_AFTER' THEN UPDATE SET target.status = src.status, target.amount = src.amount
WHEN MATCHED AND src.__change_type = 'DELETE' THEN DELETE
WHEN NOT MATCHED AND src.__change_type IN ('INSERT', 'UPDATE_AFTER') THEN INSERT (order_id, status, amount) VALUES (src.order_id, src.status, src.amount);

-- Consume automatically with a Dynamic Table (recommended)
CREATE OR REPLACE DYNAMIC TABLE dw.orders_processed
  REFRESH INTERVAL 1 MINUTE vcluster default
AS
SELECT order_id, status, amount, __change_type, __commit_timestamp
FROM orders_stream
WHERE __change_type IN ('INSERT', 'UPDATE_AFTER');
```

## DROP TABLE STREAM

```sql
DROP TABLE STREAM [ IF EXISTS ] <stream_name>;
```

## SHOW / DESC

```sql
-- List all Table Streams in the current schema
SHOW TABLE STREAMS;

-- List Table Streams in a specific schema
SHOW TABLE STREAMS IN <schema_name>;

-- Filter by name
SHOW TABLE STREAMS LIKE 'orders%';

-- View Table Stream details (source table, mode, creation time)
DESC TABLE STREAM <stream_name>;
```

## Notes

- SELECT alone does not advance the offset; you can query repeatedly for preview
- DML operations (INSERT INTO / MERGE INTO / UPDATE / DELETE) advance the offset
- ⚠️ Even if a DML has a WHERE clause that filters some rows, **the offset advances for all rows**
- If not consumed for a long time, data will be lost once the source table's `data_retention_days` is exceeded
- In `STANDARD` mode, UPDATE produces two records: `UPDATE_BEFORE` (before update) and `UPDATE_AFTER` (after update)
- When consuming, typically filter `__change_type != 'UPDATE_BEFORE'` to ignore old values
- The source table must have `change_tracking` enabled first: `ALTER TABLE name SET PROPERTIES ('change_tracking' = 'true')`

## Reference Documentation

- [CREATE TABLE STREAM](https://www.yunqi.tech/documents/create-table-stream)
- [DESC TABLE STREAM](https://www.yunqi.tech/documents/desc-table-stream)
- [SHOW TABLE STREAMS](https://www.yunqi.tech/documents/show-table-streams)
- [DROP TABLE STREAM](https://www.yunqi.tech/documents/drop-table-stream)
- [Table Stream Overview](https://www.yunqi.tech/documents/tablestream_summary)
- [Table Stream Change Data Capture](https://www.yunqi.tech/documents/table_stream)
- [Table Stream Best Practices](https://www.yunqi.tech/documents/lakehouse-table-stream-best-practices)
