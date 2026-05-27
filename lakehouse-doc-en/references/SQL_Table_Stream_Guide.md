# Lakehouse CDC Change Data Capture Guide (Table Stream)

## Overview

Change Data Capture (CDC) is the foundation of real-time data pipelines. Singdata Lakehouse provides the `TABLE STREAM` object, which automatically tracks `INSERT`, `UPDATE`, and `DELETE` operations on a table and presents them as an incremental data stream for downstream consumption. This guide is organized by business scenario to help you quickly master Table Stream creation and consumption methods.

### Quick Navigation

* [Create Table Stream](#create-table-stream) -- Bind a source table to enable change tracking
* [Consume Change Data](#consume-change-data) -- Query the Stream to obtain incremental records
* [Offset Advancement After Consumption](#offset-advancement-after-consumption) -- Understand the automatic advancement mechanism
* [View Stream Information](#view-stream-information) -- Monitor Stream status
* [Drop Table Stream](#drop-table-stream) -- Clean up Streams no longer needed

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE TABLE STREAM` | Create a change data stream | Bind to a source table and enable CDC tracking |
| `SELECT * FROM stream_name` | Query incremental data | Consume change data into downstream tables |
| `SHOW TABLE STREAMS` | View Stream list | Monitor Stream status and lag |
| `DROP TABLE STREAM` | Drop a Stream | Clean up CDC objects no longer needed |

***

## Prerequisites

The following examples use a simulated user table `users_cdc`:

```sql
-- Create source table
CREATE TABLE IF NOT EXISTS users_cdc (
    user_id INT,
    user_name STRING,
    status STRING
);

-- Insert initial data
INSERT INTO users_cdc VALUES
(1, 'Alice', 'active'),
(2, 'Bob', 'active');
```

***

## Create Table Stream

Use `CREATE TABLE STREAM` to bind to a source table. The Stream records all changes since its creation or since the last consumption.

```sql
-- Create a Table Stream
CREATE TABLE STREAM users_cdc_stream ON TABLE users_cdc
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

> **Tip**: Once the Stream is created, any `INSERT`, `UPDATE`, or `DELETE` operations on the source table are recorded.

***

## Consume Change Data

Query the Stream to retrieve incremental change records. The rows returned by the Stream include all columns from the original table as well as the metadata column `__change_type` (operation type).

```sql
-- Simulate source table changes
INSERT INTO users_cdc VALUES (3, 'Carol', 'active');
UPDATE users_cdc SET status = 'inactive' WHERE user_id = 2;

-- Query the Stream to retrieve changes
SELECT *, __change_type 
FROM users_cdc_stream 
ORDER BY user_id;
```

**Result Explanation**:

| user_id | user_name | status | __change_type |
|---------|-----------|--------|---------------|
| 2 | Bob | active | UPDATE_BEFORE |
| 2 | Bob | inactive | UPDATE_AFTER |
| 3 | Carol | active | INSERT |

> **Note**: `__change_type` values include `INSERT`, `UPDATE_AFTER`, `UPDATE_BEFORE`, `DELETE`. The Stream also returns the `__commit_version` and `__commit_timestamp` metadata columns.

***

## Offset Advancement After Consumption

The Table Stream offset **automatically advances after downstream DML operations consume the Stream**. This means that once you insert Stream data into a target table, the Stream's cursor advances, and the next query will only return new changes.

```sql
-- Create a target table
CREATE TABLE IF NOT EXISTS users_sync (
    user_id INT,
    user_name STRING,
    status STRING,
    sync_time TIMESTAMP
);

-- Consume the Stream and write to the target table (offset advances automatically)
INSERT INTO users_sync
SELECT user_id, user_name, status, CURRENT_TIMESTAMP()
FROM users_cdc_stream;

-- Query the Stream again (should be empty as the offset has advanced)
SELECT COUNT(*) FROM users_cdc_stream;
```

**Result Explanation**:

| COUNT(*) |
|----------|
| 0 |

> **Tip**: If you only execute a `SELECT` without a DML consumption, the offset will not advance, and the next query will return the same data.

***

## View Stream Information

Use `SHOW TABLE STREAMS` to view a Stream's status, bound table, and consumption lag.

```sql
-- View the Stream list
SHOW TABLE STREAMS LIKE 'users_cdc_stream';
```

**Key Field Descriptions**:
* `table_name`: The bound source table
* `mode`: Consumption mode (STANDARD / APPEND_ONLY)
* `stale_after`: Stream expiration time (the Stream becomes invalid if not consumed beyond this time)

***

## Drop Table Stream

Use `DROP TABLE STREAM` to remove a Stream object that is no longer needed.

```sql
-- Drop the Stream
DROP TABLE STREAM users_cdc_stream;
```

> **Tip**: Dropping a Stream does not affect the source table data, but unconsumed change records will be lost.

***

## Clean Up Test Data

After completing CDC verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS users_cdc;
DROP TABLE IF EXISTS users_cdc_stream;
DROP TABLE IF EXISTS users_sync;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Offset Advancement Mechanism**: The Stream offset only advances when consumed by DML statements (such as `INSERT INTO ... SELECT FROM stream`). Pure `SELECT` queries do not advance the offset.
2. **Expiration Time**: Streams depend on the Time Travel retention period. If left unconsumed beyond `data_retention_days`, the Stream becomes `STALE` and cannot be read further.
3. **APPEND_ONLY Mode**: If the source table is append-only (no UPDATE/DELETE), you can create a Stream in `APPEND_ONLY` mode for better performance: `CREATE TABLE STREAM ... WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY')`.
4. **Dynamic Table Consumption**: Dynamic Tables can build incremental pipelines based on Table Streams, enabling end-to-end real-time data warehousing.

***

## Related Documentation

* [TABLE STREAM Introduction](tablestream_summary.md)
* [CREATE TABLE STREAM](create-table-stream.md)
* [Dynamic Table Development Quick Start](SQL_Dynamic_Table_Guide.md)
