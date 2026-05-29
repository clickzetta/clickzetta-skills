# Table Stream Change Data Capture

Table Stream is the Change Data Capture (CDC) mechanism of Singdata Lakehouse, used to capture change data of table objects. By defining a Table Stream object, you can record and track data changes based on an existing table.

## Quick Guide: Is This What You Need?

If you are familiar with Kafka, you can think of Table Stream as a "consumer offset on a table" -- it records the last version you read, and the next query only returns rows that changed after that point. Unlike a Kafka consumer group, the offset only advances when you consume with DML statements; it will not lose data due to ordinary queries.

**Quick Selection**:

| Scenario | Recommended Solution |
|---|---|
| Capture row-level changes (INSERT/UPDATE/DELETE) on a table | **Table Stream** (this document) |
| Continuously import data from Kafka or OSS into a table | **Pipe** |
| Automatically maintain derived tables with aggregated or transformed results | **Dynamic Table** |

> Not sure which to use? See the [Realtime Data Pipeline Selection Guide](realtime-pipeline-selection-guide.md) for a complete comparison.

## What Is Table Stream

Table Stream leverages the multi-version history feature of Lakehouse Table, recording the specified version (or the latest version) of the source table as the initial read position when created. When you query the Table Stream, it returns all change records from the initial offset to the current latest version.

**Core Features**:
- Table Stream **does not store actual data**; it only records and maintains the data version offset of the source table
- The offset is only updated to the latest data version when Table Stream is consumed using DML statements (INSERT/DELETE/UPDATE/MERGE)
- Based on the MVCC mechanism, no additional log storage or complex CDC configuration is required

```
Source Table (Base Table)                    Table Stream
+------------------+                 +------------------+
| Version 1: [A, B] |                 | Initial Offset: Version 1 |
| Version 2: [A,B,C] |  <-- DML -->   | Visible Changes: [C]     |
| Version 3: [A,X,C] |  <-- DML -->   | Visible Changes: [B->X]   |
| Version 4: [A,X]   |  <-- DML -->   | Visible Changes: [C deleted] |
+------------------+                 +------------------+
```

## Working Principle

```
1. Create Table Stream
   +-- Records the source table's current version as the initial offset

2. DML changes occur on the source table
   +-- MetaService records new versions
   +-- Table Stream automatically detects changes

3. Query Table Stream
   +-- Returns all change records from the initial offset to the latest version

4. Consume Table Stream (DML operation)
   +-- INSERT INTO target SELECT * FROM stream
   +-- Offset automatically updates to the latest version
```

## Table Stream Types

| Type | Tracking Scope | Applicable Scenarios |
|---|---|---|
| **STANDARD** | All DML changes (INSERT, UPDATE, DELETE, TRUNCATE) | ETL scenarios requiring complete change data capture |
| **APPEND_ONLY** | INSERT operations only | Log-type, event-type append-only data scenarios |

### STANDARD Type Details

The STANDARD type provides row-level changes by joining and processing all delta data changes to provide row-level increments. **Delta changes reflect the latest state of the source object, not historical changes**.

For example:
- If a row is inserted and then updated after the Table Stream's offset, the delta change is the **row after the update**
- If a row is inserted and then deleted after the Table Stream's offset, the delta change is **no such row**

### APPEND_ONLY Type Details

The APPEND_ONLY type only records INSERT operation data. Update and delete operations are not recorded.

For example: 10 rows are initially inserted into the table, then a delete operation removes 5 rows while the offset remains unmoved. The Table Stream still records all 10 rows.

## How to Determine Change Types

In STANDARD mode, the `__change_type` field has four values, **regardless of the `SHOW_INITIAL_ROWS` parameter**:

| `__change_type` | Meaning | Description |
|---|---|---|
| `INSERT` | New row | An INSERT was performed on the source table |
| `UPDATE_BEFORE` | Old value before update | Appears paired with `UPDATE_AFTER`; `__commit_version` is the old version number |
| `UPDATE_AFTER` | New value after update | Appears paired with `UPDATE_BEFORE`; `__commit_version` is the new version number |
| `DELETE` | Deleted row | A DELETE was performed on the source table; retains the field values of the deleted row |

An UPDATE operation produces two rows: `UPDATE_BEFORE` (old value) and `UPDATE_AFTER` (new value). Both rows have the same `id` but different `__commit_version`.

**STANDARD Mode Example**:

```sql
-- Source table executes UPDATE: UPDATE source SET val = 999 WHERE id = 1
SELECT __change_type, __commit_version, id, val FROM my_stream ORDER BY id, __change_type;
+-----------------+------------------+----+-----+
| __change_type   | __commit_version | id | val |
+-----------------+------------------+----+-----+
| UPDATE_AFTER    | 4                | 1  | 999 |  <-- New value
| UPDATE_BEFORE   | 2                | 1  | 100 |  <-- Old value
+-----------------+------------------+----+-----+

-- Source table executes DELETE: DELETE FROM source WHERE id = 2
SELECT __change_type, id, val FROM my_stream;
+-----------------+----+-----+
| __change_type   | id | val |
+-----------------+----+-----+
| DELETE          | 2  | 200 |  <-- Deleted row, retains field values
+-----------------+----+-----+
```

In **APPEND_ONLY** mode, `__change_type` is always `INSERT`. UPDATE and DELETE operations produce no records.

### Actual Effect of the `SHOW_INITIAL_ROWS` Parameter

`SHOW_INITIAL_ROWS` controls **whether existing data in the table at the time of Stream creation is visible**. It does not affect the value of `__change_type`:

| `SHOW_INITIAL_ROWS` | Behavior |
|---|---|
| `'FALSE'` (default) | Data already in the table at Stream creation is invisible; only changes that occur **after** Stream creation are captured |
| `'TRUE'` | Data already in the table at Stream creation is exposed as `INSERT` during the first consumption. After consuming the initial snapshot, subsequent changes produce `UPDATE_BEFORE`/`UPDATE_AFTER`/`DELETE` normally |

**Standard pattern for consuming a STANDARD-mode Stream in a MERGE statement**:

```sql
MERGE INTO target t
USING source_stream s ON t.id = s.id
WHEN MATCHED AND s.__change_type = 'UPDATE_AFTER'
    THEN UPDATE SET t.name = s.name, t.val = s.val
WHEN MATCHED AND s.__change_type = 'DELETE'
    THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT'
    THEN INSERT (id, name, val) VALUES (s.id, s.name, s.val);
-- UPDATE_BEFORE rows do not need to be processed; MERGE automatically ignores unmatched conditions
```

## Using Table Stream

### Prerequisites

Table Stream can be created directly on any regular table; no additional configuration is required.

> 💡 **Tip**: If the source table has `change_tracking` enabled, Table Stream behavior remains consistent. `change_tracking` is not a prerequisite for creating a Table Stream.

### Creating a Table Stream

Table Stream can be created directly on any regular table:

```sql
-- Create a test table
CREATE TABLE data_change_test (id INT, name STRING);

-- Insert initial data
INSERT INTO data_change_test VALUES (1, 'apple');

-- Create an APPEND_ONLY type Table Stream
CREATE TABLE STREAM data_change_test_stream ON TABLE data_change_test
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

### Querying a Table Stream

```sql
-- Insert new data
INSERT INTO data_change_test VALUES (2, 'banana');

-- Query the source table (2 records)
SELECT * FROM data_change_test;
+----+--------+
| id | name   |
+----+--------+
| 1  | apple  |
| 2  | banana |
+----+--------+

-- Query the Table Stream (only 1 new record)
SELECT * FROM data_change_test_stream;
+----+--------+
| id | name   |
+----+--------+
| 2  | banana |
+----+--------+
```

### Consuming a Table Stream

When consuming a Table Stream using DML statements, the offset automatically updates:

```sql
-- Create a target table
CREATE TABLE data_change_test_offset (id INT, name STRING);

-- Consume the Stream data (offset automatically updates)
INSERT INTO data_change_test_offset SELECT id, name FROM data_change_test_stream;

-- Query the Stream again (data has been consumed, returns empty)
SELECT * FROM data_change_test_stream;
+----+------+
| id | name |
+----+------+
+----+------+
```

> **WHERE conditions do not prevent offset advancement**: If a DML statement consuming a Stream has a WHERE condition, filtered-out data is **not** retained for the next consumption -- the offset advances to the latest position regardless, and filtered change records are permanently lost. If you want to process only part of the data without discarding the rest, consume the full stream into a staging table first, then filter from the staging table:
>
> ```sql
> -- Correct approach: consume the full stream into a staging table first
> INSERT INTO staging SELECT * FROM my_stream;
> -- Then process from the staging table by condition
> INSERT INTO target SELECT * FROM staging WHERE value > 100;
> ```

### Deleting a Table Stream

```sql
DROP TABLE STREAM IF EXISTS data_change_test_stream;
```

## Data Change Visibility Timeliness

| Data Write Method | Table Stream Visibility Timeliness |
|---|---|
| DML (INSERT/UPDATE/DELETE) | Immediately visible after task completes successfully |
| Bulkload | Immediately visible after task completes successfully |
| Streaming Ingestion (Ingestion Service) | Visible after changes are committed, by default every 1 minute |

> ⚠️ **Note**: For streaming writes, SQL queries on the target table itself show data in real time. This constraint only applies to the visibility timeliness of a Table Stream based on that target table.

## Relationship Between Table Stream and Dynamic Table

| Dimension | Table Stream | Dynamic Table |
|---|---|---|
| **Positioning** | Low-level CDC mechanism that captures table change data | High-level data processing feature that performs data transformation based on incremental computation |
| **Stores Data** | No, only records the offset | Yes, stores computation results |
| **Performs Computation** | No, only returns change records | Yes, executes defined SQL logic |
| **Refresh Method** | Returns changes on query; updates offset on consumption | Automatically refreshes at configured intervals |
| **Typical Scenarios** | Change data capture, real-time data synchronization | Data warehouse layered processing, metric aggregation |

### Collaborative Working Mode

In practice, Table Stream and Dynamic Table often work together:

```
Source Table --[Table Stream]--> Capture Changes --[Dynamic Table]--> Transform & Aggregate --> Target Table
```

- **ETL Data Processing Chain**: Create a Table Stream on the source table to capture change data, then use a Dynamic Table to perform transformation and aggregation on these changes
- **Multi-level Incremental Computation**: Build a series of Dynamic Tables, where each Dynamic Table processes the incremental data produced by the previous table in sequence
- **Real-time Data Analysis**: Use Table Stream to capture business system data changes in real time, then use Dynamic Table for real-time analysis and computation

## Best Practices

### 1. Create Directly

Table Stream can be created directly on any regular table; no additional configuration is required:

```sql
-- Create Table Stream directly
CREATE TABLE STREAM my_stream ON TABLE source_table
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

### 2. Choose the Right Type

- If you only need to capture newly added data (e.g., log tables, event tables), use **APPEND_ONLY** type for better performance
- If you need complete change data (including updates and deletes), use **STANDARD** type

### 3. Consume Promptly

Table Stream's change data depends on the source table's Time Travel retention period. If not consumed for an extended period, the source table's historical versions may be cleaned up, causing the Table Stream to be unable to obtain complete change data.

### 4. Monitor Offset Status

Use `DESC TABLE STREAM` to check the current offset status of a Table Stream:

```sql
DESC TABLE STREAM my_stream;
+------------------------+---------------------------+
| info_name              | info_value                |
+------------------------+---------------------------+
| name                   | my_stream                 |
| creator                | qiliang                   |
| created_time           | 2026-05-19 22:29:26.01    |
| last_modified_time     | 2026-05-19 22:29:26.017   |
| workspace              | quick_start               |
| base_tables            | quick_start.source_table  |
| stale                  | false                     |
| offset                 | -1                        |
| current_offset_time    | 2026-05-19 22:28:47.669   |
| current_offset_version | 1                         |
+------------------------+---------------------------+
```

- `stale = true` means the source table's historical versions have been cleaned up, and the Table Stream may not be able to obtain complete changes
- `offset` of -1 means no data has been consumed yet

## Notes

- Table Stream can be created directly on any regular table; no additional configuration is required
- When the source table is deleted, the associated Table Stream becomes invalid
- Table Stream offset updates only occur on DML consumption; queries alone do not update the offset
- In STANDARD mode, UPDATE produces `UPDATE_BEFORE` + `UPDATE_AFTER` two rows, and DELETE produces a `DELETE` record, regardless of the `SHOW_INITIAL_ROWS` parameter
- **`CREATE OR REPLACE TABLE` makes the associated Stream stale**: Executing `CREATE OR REPLACE TABLE` (table rebuild) on the source table clears the table's historical versions, causing all Table Streams based on that table to immediately become stale (`stale = true`) and unable to obtain complete change data. If you need to modify the table structure, prefer using `ALTER TABLE` instead of `CREATE OR REPLACE TABLE`.

## Related Documentation

- [CREATE TABLE STREAM](create-table-stream.md)
- [DESC TABLE STREAM](desc-table-stream.md)
- [SHOW TABLE STREAMS](show-table-streams.md)
- [DROP TABLE STREAM](drop-table-stream.md)
- [Dynamic Table Introduction](dynamic-table-introduce.md)
- [Realtime Data Pipeline Selection Guide](realtime-pipeline-selection-guide.md)
