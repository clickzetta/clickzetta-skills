# TABLE STREAM Function Introduction

## Overview

Table Stream is an object in the Lakehouse architecture that can record changes in Data Manipulation Language (DML) operations on a table, including insert, update, and delete operations. Table Stream also provides metadata information about each change, allowing users to take corresponding actions based on this information. It can record row-level changes between two transaction time points in a table, similar to the Change Data Capture (CDC) feature of relational databases. Downstream systems can consume Table Stream through SQL statements, and when downstream DML operations include Table Stream, the Table Stream's offset will automatically shift. Table Stream can be created on Table, Dynamic Table, Materialized View, and External Table (Kafka).

Volume Stream can also be created on an External Volume to monitor file change events in external object storage (such as OSS).

## TABLE STREAM OFFSET on Table, Dynamic Table, and Materialized View

Table Stream Offset is a mechanism for storing the offset of the stream (i.e., the current transaction version of the source object). The offset determines the range of change records returned by the Table Stream. Here are some characteristics of Table Stream Offset:

1. When a Table Stream is created, an initial snapshot of each row of the source object is taken to initialize an offset. Subsequently, Table Stream records information about DML changes that occur after this snapshot.
2. Table Stream itself does not contain any table data; it only stores the offset of the source object and uses the version history of the source object to return change records.
3. The offset of Table Stream can be specified at creation or updated during consumption. The method to specify the offset uses a timestamp.
4. The offset of Table Stream is located between two table versions of the source object. When querying Table Stream, it returns changes caused by transactions committed after the offset and before the current time.

## TABLE Version Control on Table, Dynamic Table, and Materialized View

In Lakehouse, whenever an insert, update, or delete operation is performed on a table, a new table version (also known as a snapshot) is generated. These versions are immutable, meaning once created, they cannot be modified. Each version contains a record of all data changes since the previous version. Table Stream is implemented based on TABLE versions. When a Stream is created, it tracks all subsequent versions of the source table and allows users to query changes that have occurred since the Table Stream was created.

![](.topwrite/assets/image_1704374346251.png)

The example above shows a source table with 10 committed versions on the timeline. The offset of the Table Stream is currently between table versions v3 and v4. When querying (or consuming) the stream, the returned records include versions from table version v4, i.e., versions after the stream offset in the table timeline, to v10, i.e., the most recently committed table version in the timeline, including the minimal change set between these two versions.

## Types Supported by TABLE STREAM on Table, Dynamic Table, and Materialized View

1. STANDARD Mode: In this mode, all DML changes of the source object can be tracked, including insert, update, and delete (including table truncation). This mode provides row-level changes by connecting and processing all delta data changes to provide row-level increments. Delta changes in Table Stream refer to data changes that occur between two transaction time points.
2. APPEND_ONLY Mode: Only records the INSERT operation data of the object. UPDATE and DELETE operations are not recorded.

## Range of Data Recorded by TABLE STREAM on Table, Dynamic Table, and Materialized View

This time range depends on the data retention period and data extension period (DATA_RETENTION_DAYS) of the source object. The data retention period refers to the length of time the historical data of the source object can be queried through Time Travel.

## Consuming TABLE STREAM

Consumers of Table Stream refer to downstream SQL containing DML statements that will consume Table Stream data. When downstream DML operations include Table Stream, the offset of the Table Stream will automatically shift. Executing DQL operations will not shift the offset, such as SELECT statements. A source object can have multiple streams tracking its changes simultaneously. Each Table Stream can have a different offset, i.e., different starting points. Each Table Stream can be used by different consumers, such as different tasks, scripts, or other mechanisms. Consumers can consume the change data in Table Stream by executing DML transactions, thereby updating the offset of the Table Stream.

## Metadata Fields in TABLE STREAM

When querying Table Stream, the result set includes additional metadata columns, including the type of change, the committed version, and the committed time. The specific fields are as follows:

* `__change_type`: Change type. In STANDARD mode, values are `INSERT` (new row), `UPDATE_BEFORE` (old value before update), `UPDATE_AFTER` (new value after update), `DELETE` (deleted row). In APPEND_ONLY mode, it is always `INSERT`. This behavior is independent of the `SHOW_INITIAL_ROWS` parameter.
* `__commit_version`: Version at which the data was committed
* `__commit_timestamp`: Time at which the data was committed

## Notes

* Table Stream can be created directly on any regular table; no additional configuration is required.
* Data written through [realtime data upload](java_reference/realtime-upload.md) can only be read after one minute. Table Stream can only read committed data. Data written by real-time tasks needs to wait 1 minute to be confirmed, so Table Stream also needs to wait 1 minute to see it.

## Use Cases

### APPEND_ONLY Mode Case

```SQL
-- Create a test table
CREATE TABLE test_table (id INT, name VARCHAR, age INT);
-- Must be enabled when creating table stream
ALTER table test_table set PROPERTIES ('change_tracking' = 'true');

-- Create append-only stream
CREATE table stream test_stream ON TABLE test_table
WITH
  PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');

-- Insert some data into the test table
INSERT INTO test_table VALUES
  (1, 'Alice', 20),
  (2, 'Bob', 25),
  (3, 'Charlie', 30),
  (4, 'David', 35),
  (5, 'Eve', 40);

-- Query the test stream, should return the inserted data
SELECT * FROM test_stream;
+---------------+------------------+-------------------------+----+---------+-----+
| __change_type | __commit_version |   __commit_timestamp    | id |  name   | age |
+---------------+------------------+-------------------------+----+---------+-----+
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 1  | Alice   | 20  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 2  | Bob     | 25  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 3  | Charlie | 30  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 4  | David   | 35  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 5  | Eve     | 40  |
+---------------+------------------+-------------------------+----+---------+-----+
-- Update some data in the test table
UPDATE test_table SET age = age + 5 WHERE     id = 1 OR       id = 3;
-- Query the test stream, should return the first appended records, only records the first inserted data, updates are not recorded
SELECT * FROM test_stream;
+---------------+------------------+-------------------------+----+---------+-----+
| __change_type | __commit_version |   __commit_timestamp    | id |  name   | age |
+---------------+------------------+-------------------------+----+---------+-----+
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 1  | Alice   | 20  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 2  | Bob     | 25  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 3  | Charlie | 30  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 4  | David   | 35  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 5  | Eve     | 40  |
+---------------+------------------+-------------------------+----+---------+-----+
-- Delete some data from the test table
DELETE FROM test_table WHERE id = 2 OR id = 4;
-- Query the test stream, should return the first appended records, only records the first inserted data, deletes are not recorded
SELECT * FROM test_stream;
+---------------+------------------+-------------------------+----+---------+-----+
| __change_type | __commit_version |   __commit_timestamp    | id |  name   | age |
+---------------+------------------+-------------------------+----+---------+-----+
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 1  | Alice   | 20  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 2  | Bob     | 25  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 3  | Charlie | 30  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 4  | David   | 35  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 5  | Eve     | 40  |
+---------------+------------------+-------------------------+----+---------+-----+
-- Delete the original table
DELETE FROM test_table;
-- Query the test stream, should return the first appended records, only records the first inserted data, deletes are not recorded
SELECT * FROM test_stream;
+---------------+------------------+-------------------------+----+---------+-----+
| __change_type | __commit_version |   __commit_timestamp    | id |  name   | age |
+---------------+------------------+-------------------------+----+---------+-----+
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 1  | Alice   | 20  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 2  | Bob     | 25  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 3  | Charlie | 30  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 4  | David   | 35  |
| INSERT        | 3                | 2025-04-28 17:37:25.785 | 5  | Eve     | 40  |
+---------------+------------------+-------------------------+----+---------+-----+
```

**Note**

To create a Table Stream, the following must be executed on the base table:

```SQL
ALTER TABLE table_name set PROPERTIES ('change_tracking' = 'true');
```

### STANDARD Mode Case

```SQL
-- Create a test table
CREATE TABLE test_table_offset (id INT, name VARCHAR, age INT);
-- Must enable when creating table stream
ALTER TABLE test_table_offset set PROPERTIES ('change_tracking' = 'true');
CREATE table stream test_table_offset_stream ON TABLE test_table_offset
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
-- Insert some data into the test table
INSERT INTO test_table_offset VALUES
  (1, 'Alice', 20),
  (2, 'Bob', 25),
  (3, 'Charlie', 30),
  (4, 'David', 35),
  (5, 'Eve', 40);

-- Query the test stream, should return the inserted data
CREATE TABLE test_table_offset_consume (id INT, name VARCHAR, age INT);
-- Synchronize the just inserted data to the target table to keep consistency
INSERT INTO test_table_offset_consume
SELECT id,name,age FROM test_table_offset_stream;
-- Check if the stream has data
SELECT * FROM test_table_offset_stream;
+---------------+------------------+--------------------+----+------+-----+
| __change_type | __commit_version | __commit_timestamp | id | name | age |
+---------------+------------------+--------------------+----+------+-----+
-- Update some data in the test table
UPDATE test_table_offset SET age = age + 5 WHERE id = 1 OR id = 3;

-- Query the test stream, should return the updated data, at this point there will be two rows of data before and after the update
SELECT * FROM test_table_offset_stream;
+---------------+------------------+-------------------------+----+---------+-----+
| __change_type | __commit_version |   __commit_timestamp    | id |  name   | age |
+---------------+------------------+-------------------------+----+---------+-----+
| UPDATE_AFTER  | 4                | 2025-04-28 17:41:18.507 | 1  | Alice   | 25  |
| UPDATE_AFTER  | 4                | 2025-04-28 17:41:18.507 | 3  | Charlie | 35  |
| UPDATE_BEFORE | 3                | 2025-04-28 17:40:54.626 | 1  | Alice   | 20  |
| UPDATE_BEFORE | 3                | 2025-04-28 17:40:54.626 | 3  | Charlie | 30  |
+---------------+------------------+-------------------------+----+---------+-----+
-- Consume the updated data, use the stream data to update the target table
MERGE INTO test_table_offset_consume target USING test_table_offset_stream source_stream ON target.id = source_stream.id WHEN MATCHED
AND source_stream.__change_type = 'UPDATE_AFTER' THEN update set target.age = source_stream.age WHEN MATCHED
AND source_stream.__change_type = 'DELETE' THEN DELETE WHEN NOT MATCHED
AND source_stream.__change_type = 'INSERT' THEN
INSERT VALUES (source_stream.id, source_stream.name, source_stream.age);

-- Check if the data in the updated table test_table_offset_consume is correct
SELECT * FROM test_table_offset_consume;
+----+---------+-----+
| id |  name   | age |
+----+---------+-----+
| 1  | Alice   | 25  |
| 3  | Charlie | 35  |
| 2  | Bob     | 25  |
| 4  | David   | 35  |
| 5  | Eve     | 40  |
+----+---------+-----+
-- Check if there is still data in the table stream, the data in the table stream has been fully consumed
SELECT * FROM test_table_offset_stream;
+---------------+------------------+--------------------+----+------+-----+
| __change_type | __commit_version | __commit_timestamp | id | name | age |
+---------------+------------------+--------------------+----+------+-----+
-- Delete some data from the test table
DELETE FROM test_table_offset WHERE id = 2 OR id = 4;
-- Check the table stream
SELECT * FROM test_table_offset_stream;
+---------------+------------------+-------------------------+----+-------+-----+
| __change_type | __commit_version |   __commit_timestamp    | id | name  | age |
+---------------+------------------+-------------------------+----+-------+-----+
| DELETE        | 3                | 2025-04-28 17:40:54.626 | 2  | Bob   | 25  |
| DELETE        | 3                | 2025-04-28 17:40:54.626 | 4  | David | 35  |
+---------------+------------------+-------------------------+----+-------+-----+
-- Consume the deleted data, use the table stream data to update the target table
MERGE INTO test_table_offset_consume target USING test_table_offset_stream source_stream ON target.id = source_stream.id WHEN MATCHED
AND source_stream.__change_type = 'UPDATE_AFTER' THEN update set target.age = source_stream.age WHEN MATCHED
AND source_stream.__change_type = 'DELETE' THEN DELETE WHEN NOT MATCHED
AND source_stream.__change_type = 'INSERT' THEN
INSERT VALUES (source_stream.id, source_stream.name, source_stream.age);

---- Check if the data in the updated table test_table_offset_consume is correct
SELECT * FROM test_table_offset_consume;
+----+---------+-----+
| id |  name   | age |
+----+---------+-----+
| 1  | Alice   | 25  |
| 3  | Charlie | 35  |
| 5  | Eve     | 40  |
+----+---------+-----+
-- Check if there is still data in the table stream, the data in the table stream has been fully consumed
SELECT * FROM test_table_offset_stream;
+---------------+------------------+--------------------+----+------+-----+
| __change_type | __commit_version | __commit_timestamp | id | name | age |
+---------------+------------------+--------------------+----+------+-----+
```

## Volume Stream Function Introduction

Volume Stream is a special form of Table Stream, built on top of the Directory Table of an External Volume. The Directory Table is a metadata table automatically maintained when the External Volume has the directory feature enabled (DIRECTORY = (ENABLE = TRUE)), recording information such as file paths, sizes, and modification times of all files in the Volume. Volume Stream tracks changes in the Directory Table to detect file creation and deletion events in external storage (such as object storage OSS, S3, etc.).

Unlike regular Table Stream which tracks DML changes in user tables, Volume Stream tracks changes at the file level. Updates to the Directory Table rely on the cloud provider's message queue service (such as Alibaba Cloud MNS, AWS SQS, etc.) to push object storage event notifications to the system in real time, which drives Directory Table refreshes and enables Volume Stream to detect file creation and deletion events.

Typical use cases include: application log analysis, IoT device data ingestion, image/audio/video metadata extraction, multi-source file archiving, etc. By using Volume Stream as an incremental driver, combined with scheduled tasks, you can implement an efficient incremental processing model that "only processes new/changed files", avoiding the performance and cost overhead of full scans.

***

## Prerequisites

Before creating a Volume Stream, the following cloud service and database object preparations must be completed (using Alibaba Cloud Hangzhou region as an example).

> Note: The current version (2026.03) only supports Alibaba Cloud and AWS.

### STEP-1: Create an MNS Queue

1. Go to the [Alibaba Cloud MNS Console](https://mns.console.aliyun.com/region/cn-hangzhou/queues).
2. Create a queue, enter a name (e.g., `volume-stream-20251203`), select **Standard Queue**, and keep other settings at their defaults.

### STEP-2: Create OSS Event Notification

1. Open the OSS Bucket management page, select **Data Processing -> Event Notifications**.
2. Create a rule:
   * Select event types as needed (recommended: check `ObjectCreate:*`, `ObjectRemoved:*`).
   * Configure object matching prefixes/suffixes as needed.
   * Set the notification target to the MNS queue created in STEP-1.

### STEP-3: Create RAM Policy and Role

**a. Create a permission policy** ([Policy Management Page](https://ram.console.aliyun.com/policies)), reference configuration:

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "oss:GetObject",
        "oss:HeadBucket",
        "oss:PutObject",
        "oss:DeleteObject",
        "oss:ListObjects"
      ],
      "Resource": [
        "acs:oss:oss-cn-hangzhou:<AccountID>:<BucketName>",
        "acs:oss:oss-cn-hangzhou:<AccountID>:<BucketName>/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "mns:GetQueueAttributes",
        "mns:SetQueueAttributes"
      ],
      "Resource": "acs:mns:cn-hangzhou:<AccountID>:/queues/<QueueName>"
    },
    {
      "Effect": "Allow",
      "Action": [
        "mns:DeleteMessage",
        "mns:ReceiveMessage",
        "mns:PeekMessage",
        "mns:BatchPeekMessage"
      ],
      "Resource": "acs:mns:cn-hangzhou:<AccountID>:/queues/<QueueName>/messages"
    }
  ]
}
```

**b. Create a role** ([Role Management Page](https://ram.console.aliyun.com/roles)):

1. **Trusted Entity Type**: Select "Cloud Account".
2. **Trusted Entity Name**: Select "Another Cloud Account", enter the Lakehouse platform's account ID (`1384322691904283`).
3. **Role Name**: e.g., `CzVolumeStreamRole`.
4. Grant the permission policy created in STEP-3a to this role.

### STEP-4: Create Storage Connection

**a. Create the connection**:

```sql
CREATE STORAGE CONNECTION conn_hz
    TYPE OSS
    REGION = 'cn-hangzhou'
    ROLE_ARN = 'acs:ram::<AccountID>:role/<RoleName>'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

**b. Get the External ID for subsequent trust policy configuration**:

```sql
DESCRIBE CONNECTION conn_hz;
```

Record the `externalId` field value from the returned result.

**c. Update the role trust policy** (fill in the `externalId`):

```json
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<externalId returned by describe connection>"
        }
      },
      "Effect": "Allow",
      "Principal": {
        "RAM": [
          "acs:ram::1384322691904283:root"
        ]
      }
    }
  ],
  "Version": "1"
}
```

***

## Volume Stream Syntax

### Creating an External Volume

Before creating a Volume Stream, you must first create an External Volume with message notification configuration:

```sql
CREATE [OR REPLACE] EXTERNAL VOLUME <volume_name>
  LOCATION '<oss://bucket/path/>'
  USING CONNECTION <connection_name>
  NOTIFICATION = (
    QUEUE_TYPE = 'ALICLOUD_MNS',
    QUEUE_NAME = '<volume-stream-20251203>', -- Queue name created in STEP-1
    VIRTUAL_CLUSTER = 'DEFAULT'
  )
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;
```

**Parameter Description**:

* `<volume_name>`: Name of the External Volume.
* `LOCATION`: OSS storage path, format `oss://<bucket>/<prefix>/`.
* `USING CONNECTION <connection_name>`: Associates the Storage Connection created in STEP-4.
* `NOTIFICATION`: Message notification configuration block.
  * `QUEUE_TYPE`: Message queue type. Currently supports `ALICLOUD_MNS`.
  * `QUEUE_NAME`: MNS queue name confirmed in STEP-1.
  * `VIRTUAL_CLUSTER`: Virtual cluster name. Default is `DEFAULT`.
* `DIRECTORY = (ENABLE = TRUE)`: Enables directory mode. Volume Stream depends on this configuration.
* `RECURSIVE = TRUE`: Recursively monitors file changes in all subdirectories under the path.

### Creating a Volume Stream

```sql
CREATE [OR REPLACE] STREAM <name>
  ON VOLUME <volume_name>;
```

**Parameter Description**:

* `<name>`: Name of the Volume Stream.
* `<volume_name>`: Name of the External Volume to monitor.

***

## Notes

* The current version (2026.03) only supports Alibaba Cloud and AWS.
* The `sts:ExternalId` must be correctly configured in the RAM role's trust policy; otherwise, the Lakehouse platform cannot assume the role to read MNS messages and OSS files.
* Volume Stream can only read files that have been fully uploaded. Due to a certain delivery delay in event notifications (typically about 1 minute), you need to wait approximately 1 minute after uploading a file before the corresponding change record can be queried in the Volume Stream.
* Similar to Table Stream, Volume Stream records the position of processed events via a consumption offset. The consumption action is typically a DML operation (not a SELECT). After each consumption, the offset advances to avoid duplicate consumption.

***

## Example: Incremental Analysis of OSS Images

The following example demonstrates a Volume Stream configuration process for monitoring file creation and deletion events in the `dish-images/` directory under the `sh-oss-derek` bucket. Using an image recognition function, only `INSERT` and `UPDATE_AFTER` events are consumed (new images + replaced images), skipping DELETE and UPDATE_BEFORE. The AI function is called for recognition, and results are written to a target table. The DML execution automatically advances the consumption offset.

> Note: The cloud provider role ARN, image recognition function, etc. used in this example need to be customized; they are not provided by the system by default.

### 1. Create Storage Connection

```sql
CREATE STORAGE CONNECTION conn_sh_oss
  TYPE OSS
  REGION = 'cn-shanghai'
  ROLE_ARN = 'acs:ram::1450476637304722:role/czvolumestreamrole' -- Replace with your own RoleARN
  ENDPOINT = 'oss-cn-shanghai.aliyuncs.com';
```

### 2. Get External ID and Update Trust Policy

```sql
DESCRIBE CONNECTION conn_sh_oss;
```

Fill the returned `externalId` (e.g., `EOKskml6SMldYOb9`) into the role's trust policy and save.

### 3. Create Basic Objects

```sql
-- 1. Create External Volume (OSS image bucket, enable MNS event notification)
CREATE EXTERNAL VOLUME vol_dish_images
  LOCATION 'oss://sh-oss-derek/dish-images/'
  USING CONNECTION conn_sh_oss
  NOTIFICATION = (
    QUEUE_TYPE    = 'ALICLOUD_MNS',
    QUEUE_NAME    = 'cz-queue-mns-ossevent',
    VIRTUAL_CLUSTER = 'DEFAULT'
  )
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;

-- 2. Create recognition results table
CREATE TABLE IF NOT EXISTS dish_recognition_results (
    file_path          VARCHAR        COMMENT 'Relative path of the image',
    file_url           VARCHAR        COMMENT 'Full OSS URL of the image',
    file_size          BIGINT         COMMENT 'File size (bytes)',
    last_modified_time TIMESTAMP      COMMENT 'File last modified time',
    recognized_content VARCHAR        COMMENT 'AI recognition result',
    change_type        VARCHAR        COMMENT 'Trigger event type: INSERT/UPDATE_AFTER',
    commit_version     BIGINT         COMMENT 'Stream consumption version number',
    processed_at       TIMESTAMP      COMMENT 'Processing time'
);

-- 3. Create Volume Stream (STANDARD mode, can detect creation and replacement)
CREATE STREAM IF NOT EXISTS str_dish_images
  ON VOLUME vol_dish_images
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

### 4. Incremental Consumption

```
-- Incremental recognition node: only processes INSERT (new image) and UPDATE_AFTER (replaced image), automatically advances offset
INSERT INTO dish_recognition_results
SELECT
    relative_path   AS file_path,
    url   AS file_url,
    size   AS file_size,
    last_modified_time,
    public.fc_image_to_text('dish_recognition', url) AS recognized_content,
    __change_type  AS change_type,
    __commit_version  AS commit_version,
    current_timestamp() AS processed_at
FROM str_dish_images
WHERE __change_type IN ('INSERT', 'UPDATE_AFTER')  -- Only process new and replaced, skip DELETE / UPDATE_BEFORE
  AND (
       lower(relative_path) LIKE '%.jpg'
    OR lower(relative_path) LIKE '%.jpeg'
    OR lower(relative_path) LIKE '%.png'
    OR lower(relative_path) LIKE '%.webp'
  );                       
```

### 5. Query Recognition Results

```
-- View the latest recognition results
SELECT
    file_path,
    recognized_content,
    change_type,
    processed_at
FROM dish_recognition_results
ORDER BY processed_at DESC
LIMIT 20;

-- Count recognition results by dish category
SELECT
    recognized_content,
    COUNT(*) AS cnt
FROM dish_recognition_results
GROUP BY recognized_content
ORDER BY cnt DESC;

```

^
