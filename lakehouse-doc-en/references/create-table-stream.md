# Table Stream

Table Stream is a real-time data stream used to record data manipulation language (DML) changes made to a table, including insert, update, and delete operations. At the same time, Table Stream also provides metadata about each change, so you can take appropriate actions based on the changed data. Table Stream can be created on Table, Dynamic Table, Materialized View, and External Table (Kafka). It also supports creating Volume Stream on External Volumes to monitor file change events in external object storage (such as OSS).

## Table Stream Syntax

**Syntax for Creating Table Stream on Table, Dynamic Table, and Materialized View**

```SQL
CREATE [OR REPLACE] TABLE STREAM [IF NOT EXISTS]
  <name>
  ON TABLE <table_name>
  [TIMESTAMP AS OF timestamp_expression]
  [COMMENT = '<string_literal>']
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY|STANDARD','SHOW_INITIAL_ROWS'='TRUE|FALSE');
```

* `<name>`: The name of the Table Stream.

* `<table_name>`: The base table from which to get the incremental data. Views are not supported.

* `TIMESTAMP AS OF timestamp_expression`: (Optional) Specifies the timestamp expression from which the Table Stream should start receiving updates from the underlying table. If this parameter is omitted, the Table Stream will start receiving updates from the current time.

  * The `timestamp_expression` returns a standard timestamp type expression. The earliest timestamp specified by TIMESTAMP AS OF depends on the [TIME TRAVEL](TIMETRAVEL.md)(data\_retention\_days) parameter. If the specified version does not exist, an error will be reported. If not specified, the current timestamp version data will be used, for example:
    * `'2023-11-07 14:49:18'`, a string that can be cast to a timestamp.
    * `cast('2023-11-07 14:49:18 Asia/Shanghai' as timestamp)`.
    * `current_timestamp() - interval '12' hours`.
    * Any other expression that is itself a timestamp or can be cast to a timestamp.

* `COMMENT`: (Optional) Comment for the Table Stream.

* `'TABLE_STREAM_MODE' = 'APPEND_ONLY|STANDARD'`: (Required) Choose one of the two values, APPEND\_ONLY or STANDARD.

  * APPEND\_ONLY records only the INSERT operations of the object. Update and delete operations are not recorded. For example, if 10 rows were initially inserted into the table and then 5 rows were deleted without moving the offset, the Table Stream would still record 10 rows of operations.
  * STANDARD mode: In STANDARD mode, all DML changes to the source object can be tracked, including inserts, updates, and deletes (including table truncation). This row-level change is provided by joining and processing all delta data changes. The delta changes in the Table Stream refer to the data changes that occur between two transaction points. For example, if a row is inserted and then updated after the Table Stream's offset, the delta change is a new row. If a row is inserted and then deleted after the stream's offset, the delta change is no row. In other words, the delta change reflects the latest state of the source object, not the historical changes.

* SHOW\_INITIAL\_ROWS: Optional parameter that controls the visibility of existing data in the table at the time of Stream creation:
  * `'FALSE'` (default): Existing data in the table at the time of Stream creation is not visible; only changes that occur **after** Stream creation are captured.
  * `'TRUE'`: Existing data in the table at the time of Stream creation is exposed as `INSERT` records in the first consumption. After consuming the initial snapshot, subsequent changes produce `UPDATE_BEFORE`/`UPDATE_AFTER`/`DELETE` as normal.

  **Note**: `SHOW_INITIAL_ROWS` only affects whether historical data is visible at the time of Stream creation, and **does not affect the values of `__change_type`**. Regardless of the value of this parameter, in STANDARD mode, UPDATE always produces both `UPDATE_BEFORE` and `UPDATE_AFTER` rows, and DELETE always produces `DELETE` records.

> CAUTION: **Visible Delay for Streaming Write Data**: Data written to the source table through the Ingestion Service (real-time streaming write) requires approximately **1 minute** to be committed before it can be queried in the Table Stream. Data written directly via SQL DML has no such delay and is immediately visible after the task succeeds.

### Notes

* The earliest timestamp specified by TIMESTAMP AS OF depends on the [TIME TRAVEL](TIMETRAVEL.md)(data\_retention\_days) parameter. If the specified version does not exist, an error will be reported. This parameter defines the length of time that deleted data is retained. By default, Lakehouse retains data for one day. Depending on your business needs, you can extend or shorten the data retention period by adjusting the `data_retention_days` parameter. Please note that adjusting the data retention period may affect storage costs. Extending the retention period will increase storage requirements, which may increase related costs.
* Data written through real-time uploads can only be read after one minute, and Table Stream can only read committed data. Data written by real-time tasks needs to wait for 1 minute to be confirmed, so Table Stream also needs to wait for 1 minute to see it.

### Usage Examples

Case 1: Create a Table Stream in APPEND\_ONLY mode

```SQL
-- Clean up the environment
DROP      TABLE IF EXISTS data_change_test;

DROP      TABLE STREAM IF EXISTS data_change_test_stream;

-- Create test table
CREATE    TABLE data_change_test (id int, name string);

INSERT    INTO data_change_test
VALUES    (1, 'apple');

-- Create TABLE stream to capture incremental records inserted from the current time
CREATE    TABLE STREAM data_change_test_stream ON TABLE data_change_test
WITH      PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');

-- Insert test data
INSERT    INTO data_change_test
VALUES    (2, 'banana');

-- View STREAM data
SELECT    *
FROM      data_change_test_stream;
```

Case 2: Create a Table Stream in STANDARD mode

```SQL
-- Clean up the environment
DROP      TABLE IF EXISTS data_change_test;

DROP      TABLE STREAM IF EXISTS data_change_test_stream;

-- Create test table
CREATE    TABLE data_change_test (id int, name string);

INSERT    INTO data_change_test
VALUES    (1, 'apple');

-- Create Table Stream in STANDARD mode
CREATE    TABLE STREAM data_change_test_stream ON TABLE data_change_test
WITH      PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Insert test data
INSERT    INTO data_change_test
VALUES    (2, 'banana');

-- Update test data
update data_change_test set name = 'orange'
WHERE     id = 2;

-- Delete test data
DELETE
FROM      data_change_test
WHERE     id = 1;

-- View stream data (STANDARD mode reflects the current state of the source table)
SELECT    *
FROM      data_change_test_stream;
```

## Kafka Table Stream

Supports creating a Table Stream on a Kafka external table for real-time consumption of Topic data.

#### Syntax

```sql
CREATE TABLE STREAM [IF NOT EXISTS] stream_name 
ON TABLE external_kafka_table 
[TIMESTAMP AS OF timestamp_expression]  -- Optional, specifies the consumption start time point
WITH PROPERTIES (
  'table_stream_mode' = 'append_only',  -- Only append mode is supported
  'show_initial_rows' = 'true'|'false'
);
```

### Parameter Description

* `TIMESTAMP AS OF`: Specifies the consumption start time point (optional). Supported formats:
  * **Explicit timestamp**: `'2023-01-01 12:00:00'`
  * **Time function**: `CURRENT_TIMESTAMP() - INTERVAL '1' HOUR`
* `show_initial_rows`: Controls initial data loading behavior:
  * `true`: Loads historical data from the offset specified when the external table was created to the offset specified by the Table Stream
  * `false`: Starts consuming from the latest offset (`latest`), does not load historical data (default value)
* `table_stream_mode`: Fixed to `append_only`, only processes new Kafka data (update/delete operations are not supported)

#### Examples

1. Creating a Kafka External Table
   First, you need to create a [Kafka External Table](kafka-external-table.md). This is the foundation for creating a Table Stream. The following is the syntax for creating a Kafka external table:

Create a Kafka Connection

```SQL
CREATE STORAGE CONNECTION pipe_kafka
    TYPE kafka
    BOOTSTRAP_SERVERS = ['47.99.48.62:9092']
    SECURITY_PROTOCOL = 'PLAINTEXT';
```

Create a Kafka External Table

```SQL
CREATE EXTERNAL TABLE external_table_kafka (   
 key_column binary,   
 value_column binary NOT NULL)
USING kafka
OPTIONS (    'group_id' = 'external_table_lh',    'topics' = 'test_long')
CONNECTION pipe_kafka;
```

* `external_table_kafka` is the name of the external table.
* `key_column` and `value_column` represent the key and value of the Kafka message respectively, where `value_column` is required.
* `USING kafka` specifies that Kafka is used as the data source.
* The `OPTIONS` section contains Kafka consumer configuration, such as the consumer group ID (`group_id`) and the topic to subscribe to (`topics`).
* `CONNECTION pipe_kafka` specifies the connection configuration to Kafka, which typically includes the Kafka cluster address and other connection parameters.

2. Creating a Table Stream

Based on the Kafka external table, you can create a Table Stream for real-time processing of the Kafka data stream. The following is the syntax for creating a Table Stream:

```
CREATE TABLE STREAM kafka_table_stream_pipe1
 ON TABLE external_table_kafka
WITH PROPERTIES (
    'table_stream_mode' = 'append_only',
    'show_initial_rows' = 'true');
```

## Volume Stream

**CREATE VOLUME STREAM Syntax**

Used to create a Volume Stream on the Directory Table of an External Volume to monitor file creation and deletion events in external object storage.

```
CREATE [OR REPLACE] STREAM [IF NOT EXISTS] <name>
  ON VOLUME <volume_name>;
```

**Parameter Description**

`<name>`: The name of the Volume Stream.

`<volume_name>`: The name of the External Volume to monitor. The Volume must meet the following conditions:

* Directory feature must be enabled, i.e., specify DIRECTORY = (ENABLE = TRUE) when creating the table;
* Recursive monitoring must be enabled, i.e., specify RECURSIVE = TRUE when creating the table.

**Example**

```
-- Create a Volume Stream to track file creation and deletion
CREATE OR REPLACE STREAM str_app_log
  ON VOLUME vol_app_log;

```

**Notes**

* Before creating a Volume Stream, you must enable DIRECTORY = (ENABLE = TRUE) and RECURSIVE = TRUE.
* Volume Stream is essentially a Table Stream built on top of a Directory Table, and its consumption mechanism is fully consistent with Table Stream: only DML statements (such as INSERT INTO ... SELECT FROM stream) advance the consumption offset; pure SELECT queries do not advance it.
* Since object storage events are delivered through message queues with approximately 1 minute of delay, you need to wait about 1 minute after uploading a file before the corresponding change record can be queried in the Volume Stream.
