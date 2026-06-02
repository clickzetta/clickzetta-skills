# Table Stream SQL Reference

> **⚠️ ClickZetta-specific Syntax**
> - Creation syntax is `CREATE TABLE STREAM`, parameters placed in `WITH PROPERTIES (...)`
> - Metadata field is `__change_type` (double underscore), values: `INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`
> - UPDATE produces two records: `UPDATE_BEFORE` (before update) and `UPDATE_AFTER` (after update)
> - Usually only need `UPDATE_AFTER` and `INSERT`, ignore `UPDATE_BEFORE`

Table Stream captures change data (INSERT / UPDATE / DELETE) from source table, is the core object for building CDC pipelines. Usually consumed with Dynamic Table or SQL tasks.

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

**Key Parameters:**
- `TABLE_STREAM_MODE = STANDARD` (default): Captures all changes INSERT, UPDATE, DELETE, each row has `__change_type` field (`INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`)
- `TABLE_STREAM_MODE = APPEND_ONLY`: Only captures INSERT, better performance, suitable for append-only source tables
- `SHOW_INITIAL_ROWS = TRUE`: First consumption returns existing rows when Stream created; `FALSE` (default) only returns new changes after Stream creation
- `TIMESTAMP AS OF`: Specify which timestamp Stream starts capturing changes from

**Examples:**
```sql
-- Create standard stream on regular table (captures all changes, need to enable change_tracking first)
ALTER TABLE ods.orders SET PROPERTIES ('change_tracking' = 'true');

CREATE TABLE STREAM orders_stream
  ON TABLE ods.orders
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Append-only stream
CREATE TABLE STREAM events_stream
  ON TABLE dw.events
  COMMENT 'Event stream, append only'
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');

-- Start capturing from specified timestamp
CREATE TABLE STREAM orders_stream_from_ts
  ON TABLE ods.orders
  TIMESTAMP AS OF '2024-01-01 00:00:00'
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD', 'SHOW_INITIAL_ROWS' = 'TRUE');
```

## Consuming Table Stream

Table Stream offset moves through DML operations. **SELECT only does not move offset**, can be queried repeatedly for preview. After executing DML (INSERT INTO / MERGE INTO / UPDATE / DELETE) to consume data, offset advances.

```sql
-- View current unconsumed change data (does not move offset)
SELECT * FROM orders_stream;

-- System fields included in change data
-- __change_type: INSERT | UPDATE_BEFORE | UPDATE_AFTER | DELETE
-- __commit_version: Change version number
-- __commit_timestamp: Change occurrence time

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

-- Auto-consume with Dynamic Table (recommended)
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
-- List all Table Streams in current schema
SHOW TABLE STREAMS;

-- List Table Streams in specified schema
SHOW TABLE STREAMS IN <schema_name>;

-- Filter by name
SHOW TABLE STREAMS LIKE 'orders%';

-- View Table Stream details (source table, mode, creation time)
DESC TABLE STREAM <stream_name>;
```

## Important Notes

- SELECT only does not move offset, can query repeatedly for preview
- DML operations (INSERT INTO / MERGE INTO / UPDATE / DELETE) move offset
- ⚠️ Even if DML has WHERE condition filtering some rows, **offset for all rows will move**
- If not consumed for long time, data will be lost after exceeding source table's `data_retention_days`
- In `STANDARD` mode UPDATE produces two records: `UPDATE_BEFORE` (before update) and `UPDATE_AFTER` (after update)
- When consuming usually filter `__change_type != 'UPDATE_BEFORE'`, ignore old values
- Source table needs to enable `change_tracking` first: `ALTER TABLE name SET PROPERTIES ('change_tracking' = 'true')`

## Reference Documentation

- [CREATE TABLE STREAM](https://www.yunqi.tech/documents/create-table-stream)
- [DESC TABLE STREAM](https://www.yunqi.tech/documents/desc-table-stream)
- [SHOW TABLE STREAMS](https://www.yunqi.tech/documents/show-table-streams)
- [DROP TABLE STREAM](https://www.yunqi.tech/documents/drop-table-stream)
- [TABLE STREAM Introduction](https://www.yunqi.tech/documents/tablestream_summary)
- [Table Stream Change Data Capture](https://www.yunqi.tech/documents/table_stream)
- [Table Stream Best Practices](https://www.yunqi.tech/documents/lakehouse-table-stream-best-practices)