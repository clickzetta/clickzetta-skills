# Singdata Lakehouse Table Stream Best Practices Guide

## The Role of Table Stream in Enterprise Data Organization

In modern data-driven enterprises, real-time capture and processing of data changes has become a critical capability. Enterprise data organizations typically face the following challenges:

* Decision delays caused by cross-system data synchronization latency
* Difficulties with incremental updates in complex ETL processes
* Complexity in tracking and auditing data change history
* Challenges in implementing real-time data integration and event-driven architectures

Singdata Lakehouse's Table Stream feature is a core component designed to address these challenges. It plays a key role in enterprise data organization:

1. **Data Integration Hub**: Serves as the core mechanism for Change Data Capture (CDC), facilitating real-time data flow between different systems
2. **Data Quality Assurance**: Provides traceability of data changes, supporting data lineage and impact analysis
3. **Real-Time Analytics Foundation**: Delivers data change streams for real-time data warehouses, instant reports, and dashboards
4. **Event-Driven Triggers**: Acts as an event source to drive downstream business processes and automated operations
5. **Data Governance Pillar**: Supports compliance requirements by recording change history of sensitive data

In the data architecture, Table Stream connects OLTP systems and analytical systems, enabling enterprises to build a modern data platform with unified batch and streaming, improving data timeliness and business responsiveness.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Preparation](#2-preparation)
3. [Creation and Configuration](#3-creation-and-configuration)
4. [Using Different Modes](#4-using-different-modes)
5. [Consuming and Processing Data](#5-consuming-and-processing-data)
6. [Using Metadata Fields](#6-using-metadata-fields)
7. [Real-World Application Scenarios](#7-real-world-application-scenarios)
8. [Performance Optimization](#8-performance-optimization)
9. [Common Issues and Solutions](#9-common-issues-and-solutions)
10. [Best Practices Summary](#10-best-practices-summary)

## 1. Introduction

### 1.1 What Is Table Stream

Table Stream is a core feature of the Singdata Lakehouse architecture, providing Change Data Capture (CDC) capabilities to record insert, update, and delete operations on table data. It creates a "change table" that enables users to query and consume row-level change records between two transaction time points.

### 1.2 Core Features

* **Change Capture**: Records table-level DML operations (INSERT, UPDATE, DELETE)
* **Metadata Recording**: Provides metadata such as version and timestamp for each change
* **Incremental Processing**: Supports incremental reading and processing of data changes
* **Consumption Mechanism**: Supports consuming change data and advancing the offset through DML operations

### 1.3 Applicable Scenarios

* Data synchronization and replication
* Real-time data integration
* Incremental ETL/ELT processes
* Auditing and data governance
* Event-driven architectures

## 2. Preparation

### 2.1 Table Configuration Requirements

Before using Table Stream, you must ensure the source table is properly configured:

```sql
-- Create source table example
CREATE TABLE source_table (
    id INT,
    name STRING,
    value DOUBLE,
    updated_at TIMESTAMP
);
```

### 2.2 Enabling Change Tracking (Required Step)

**Important**: You must enable change tracking on the source table before creating a Table Stream:

```sql
-- Enable change tracking
ALTER TABLE source_table SET PROPERTIES ('change_tracking' = 'true');
```

This step is **mandatory**. If not performed, the Table Stream may be created successfully but will not capture changes correctly.

### 2.3 Preparing the Target Table

If you plan to write Stream data to a target table, create a target table with a compatible structure in advance:

```sql
-- Create target table
CREATE TABLE target_table (
    id INT,
    name STRING,
    value DOUBLE,
    updated_at TIMESTAMP
);
```

## 3. Creation and Configuration

### 3.1 Basic Syntax

Basic syntax for creating a Table Stream:

```sql
CREATE TABLE STREAM stream_name 
ON TABLE source_table
[COMMENT 'stream description']
WITH PROPERTIES (
    'TABLE_STREAM_MODE' = 'STANDARD|APPEND_ONLY',
    ['SHOW_INITIAL_ROWS' = 'TRUE|FALSE']
);
```

### 3.2 Important Parameters

#### 3.2.1 TABLE\_STREAM\_MODE

* **STANDARD**: Captures all DML operations (INSERT, UPDATE, DELETE), reflecting the current state of the table
* **APPEND\_ONLY**: Captures only INSERT operations, preserving original INSERT records even if rows are updated or deleted

#### 3.2.2 SHOW\_INITIAL\_ROWS

* **TRUE**: Returns all existing rows from the table when the Stream was created on first consumption
* **FALSE** (default): Returns only new changes after the Stream was created on first consumption

### 3.3 Time Point Configuration

You can specify the time point at which the Stream starts capturing changes:

```sql
CREATE TABLE STREAM stream_name 
ON TABLE source_table
TIMESTAMP AS OF current_timestamp()
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

**Best Practice**: Use `current_timestamp()` or a specific timestamp string, avoiding complex time expressions.

### 3.4 Adding Comments

Add descriptive comments to the Stream:

```sql
CREATE TABLE STREAM stream_name 
ON TABLE source_table
COMMENT 'Capture data changes from source_table'
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

**Note**: Use the correct syntax `COMMENT 'comment content'`, not `COMMENT = 'comment content'`.

## 4. Using Different Modes

### 4.1 STANDARD Mode

**Recommended Use**: When you need the complete current state of the table, including update and delete operations.

```sql
CREATE TABLE STREAM standard_stream 
ON TABLE source_table
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

Characteristics:

* Accurately reflects the current state of the table
* Updates show the latest values
* Deleted rows do not appear in the results

### 4.2 APPEND\_ONLY Mode

**Recommended Use**: When you need to preserve all insert records, including those subsequently updated or deleted.

```sql
CREATE TABLE STREAM append_stream 
ON TABLE source_table
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

Characteristics:

* Records all INSERT operations
* Does not reflect UPDATE and DELETE operations
* Original INSERT records are preserved even if rows are deleted

### 4.3 Mode Selection Guide

| Requirement                           | Recommended Mode |
| ------------------------------------- | ---------------- |
| Data synchronization (keep target consistent with source) | STANDARD         |
| Auditing all insert records           | APPEND\_ONLY     |
| Incremental ETL processes             | STANDARD         |
| Historical record preservation        | APPEND\_ONLY     |

## 5. Consuming and Processing Data

### 5.1 Querying Stream Data

```sql
-- Query change data in the Stream
SELECT * FROM my_stream;
```

**Important**: Using only SELECT queries will not advance the Stream's offset.

### 5.2 Consuming and Advancing Offset

To advance the Stream's offset (consume data), you must use DML operations:

```sql
-- Insert Stream data into the target table (advances offset)
INSERT INTO target_table
SELECT id, name, value, updated_at 
FROM my_stream;
```

### 5.3 Consumption Modes

#### 5.3.1 Full Consumption

```sql
-- Consume all change data in the Stream
INSERT INTO target_table
SELECT id, name, value, updated_at 
FROM my_stream;
```

#### 5.3.2 Conditional Consumption

```sql
-- Consume only change data that meets specific conditions
INSERT INTO target_table
SELECT id, name, value, updated_at 
FROM my_stream
WHERE value > 100;
```

**Note**: Even when using a WHERE condition, the offset for all Stream data will still advance.

### 5.4 Verifying Consumption Status

Verify whether data has been consumed by querying the Stream again:

```sql
-- Verify Stream status after consumption
SELECT COUNT(*) FROM my_stream;
```

If consumption was successful, COUNT should be 0 or contain only new change data.

## 6. Using Metadata Fields

### 6.1 Available Metadata Fields

The results returned by Table Stream include the following metadata fields:

* `__change_type`: Change type
* `__commit_version`: Commit version
* `__commit_timestamp`: Commit timestamp

### 6.2 Determining Change Types

**Note**: Based on our testing, the actual behavior of the `__change_type` field may differ from the documentation description. All records are marked as "INSERT", even for update or delete operations.

Therefore, we recommend determining change types through the following methods:

1. **INSERT Operation**: New records appear in the Stream
2. **UPDATE Operation**: The `__commit_version` field value increases for records with the same ID
3. **DELETE Operation**: Records no longer appear in the results of STANDARD mode

### 6.3 Using Metadata for Incremental Processing

```sql
-- Filter based on commit version
SELECT * FROM my_stream
WHERE __commit_version > last_processed_version;

-- Filter based on commit timestamp
SELECT * FROM my_stream
WHERE __commit_timestamp > TIMESTAMP '2025-05-01 00:00:00';
```

### 6.4 Metadata Field Best Practices

* Do not rely on the `__change_type` field to distinguish operation types
* Use `__commit_version` and `__commit_timestamp` to track changes
* Focus on the final state of data rather than the change process
* Save the maximum version number consumed for disaster recovery

## 7. Real-World Application Scenarios

### 7.1 Real-Time Data Synchronization

```sql
-- Execute periodically to sync changes to the target table
INSERT INTO target_table
SELECT id, name, value, updated_at 
FROM source_stream;
```

This can be combined with scheduled tasks or triggers for automated synchronization.

### 7.2 Incremental ETL Process

```sql
-- Incrementally extract, transform, and load data
INSERT INTO dwh_fact_table (dimension_id, metric_value, load_date)
SELECT 
    dim.dimension_id,
    stream.value,
    current_date()
FROM source_stream stream
JOIN dimension_table dim ON stream.id = dim.source_id;
```

### 7.3 Event-Driven Processing

```sql
-- Detect specific events and trigger processing
CREATE OR REPLACE PROCEDURE process_high_value_changes() AS
BEGIN
    -- Check for high-value changes
    DECLARE high_value_changes CURSOR FOR 
        SELECT * FROM value_stream WHERE value > 1000;
    
    -- Process these changes
    FOR change IN high_value_changes DO
        -- Execute processing logic
        INSERT INTO high_value_alerts VALUES (change.id, change.value, current_timestamp());
    END FOR;
    
    -- Consume all changes
    INSERT INTO processed_changes
    SELECT * FROM value_stream;
END;
```

### 7.4 Audit Trail

```sql
-- Capture all changes for auditing
CREATE TABLE STREAM audit_stream 
ON TABLE sensitive_data
WITH PROPERTIES (
    'TABLE_STREAM_MODE' = 'APPEND_ONLY',
    'SHOW_INITIAL_ROWS' = 'TRUE'
);

-- Periodically archive to audit table
INSERT INTO audit_history
SELECT 
    *,
    __commit_timestamp AS audit_timestamp,
    __commit_version AS change_version
FROM audit_stream;
```

## 8. Performance Optimization

### 8.1 Reducing Data Volume

* Select only necessary columns rather than `SELECT *`
* Set appropriate retention periods on source tables
* Regularly consume Stream data to avoid accumulation

### 8.2 Batch Processing

```sql
-- Batch consume multiple Streams and merge processing
INSERT INTO consolidated_target
SELECT 'customers' AS source, id, name, NULL AS product_id, NULL AS order_id, __commit_timestamp
FROM customer_stream
UNION ALL
SELECT 'products' AS source, id, name, product_id, NULL AS order_id, __commit_timestamp
FROM product_stream
UNION ALL
SELECT 'orders' AS source, id, NULL AS name, NULL AS product_id, order_id, __commit_timestamp
FROM order_stream;
```

### 8.3 Parallel Processing

Split large Streams into multiple smaller parts for parallel processing:

```sql
-- Partition 1 processing
INSERT INTO target_partition_1
SELECT * FROM source_stream WHERE MOD(id, 4) = 0;

-- Partition 2 processing
INSERT INTO target_partition_2
SELECT * FROM source_stream WHERE MOD(id, 4) = 1;

-- And so on...
```

### 8.4 Frequency Optimization

* High change rate tables: Consume Streams more frequently
* Low change rate tables: Reduce consumption frequency
* Critical tables: Real-time or near-real-time consumption
* Non-critical tables: Batch periodic consumption

## 9. Common Issues and Solutions

### 9.1 Stream Not Capturing Changes

**Issue**: Stream fails to capture table changes after creation.

**Solution**:

1. Confirm change tracking is enabled: `ALTER TABLE table_name SET PROPERTIES ('change_tracking' = 'true')`
2. Verify you have sufficient permissions
3. Confirm DML operations were executed after Stream creation

### 9.2 Cannot Distinguish Change Types

**Issue**: All changes are marked as INSERT, making it impossible to distinguish updates and deletes.

**Solution**:

1. Use `__commit_version` changes to detect updates
2. Record previous state and compare with current state
3. For STANDARD mode, determine deletions by whether records exist

### 9.3 Duplicate Data Consumption

**Issue**: Repeatedly running consumption logic causes duplicate data in the target table.

**Solution**:

1. Use MERGE statements instead of INSERT
2. Implement idempotent processing
3. Record the last consumed version and timestamp

```sql
-- Idempotent consumption example
MERGE INTO target_table t
USING my_stream s
ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET 
        t.name = s.name,
        t.value = s.value,
        t.updated_at = s.updated_at
WHEN NOT MATCHED THEN
    INSERT (id, name, value, updated_at)
    VALUES (s.id, s.name, s.value, s.updated_at);
```

### 9.4 Offset Not Advancing After Consumption

**Issue**: Querying again after consumption still returns the same data.

**Solution**:

1. Ensure data is consumed using DML operations (INSERT, UPDATE, MERGE)
2. Do not use only SELECT queries, which do not advance the offset
3. Check whether the DML operation was successfully committed

## 10. Best Practices Summary

### 10.1 Design Principles

1. **Always Enable Change Tracking**: Enable change tracking on the table before creating a Stream
2. **Choose the Right Mode**: Select STANDARD or APPEND\_ONLY mode based on requirements
3. **Consume Regularly**: Do not let Streams accumulate too much data
4. **Focus on Final State**: Focus on the final state of data rather than the change process
5. **Do Not Rely on Change Type**: Do not rely on the `__change_type` field to distinguish operation types

### 10.2 Usage Checklist

* [ ] Enable change\_tracking on the source table
* [ ] Select the appropriate Stream mode
* [ ] Consider whether SHOW\_INITIAL\_ROWS is needed
* [ ] Use DML operations to consume data
* [ ] Implement idempotent consumption mechanism
* [ ] Monitor Stream size and performance
* [ ] Record consumed version and timestamp
* [ ] Implement error handling and retry logic

### 10.3 Keys to Successful Implementation

* **Understand the Mechanism**: Master how Stream works and its limitations
* **Test Properly**: Fully test before deploying to production
* **Maintain Regularly**: Monitor and optimize Stream performance
* **Record State**: Track consumption status to ensure data consistency
* **Design for Fault Tolerance**: Consider disaster recovery and edge cases

By following these best practices, you will be able to fully leverage the Singdata Lakehouse Table Stream feature to build efficient and reliable data change capture and processing pipelines.

## References

1. [Singdata Table Stream Documentation](tablestream_summary.md) - Feature description and syntax reference
2. [Singdata Table Stream Creation Syntax](create-table-stream.md) - Detailed creation syntax and parameter descriptions
3. [Change Data Capture (CDC) Best Practices](czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables.md) - General best practices related to change data capture
4. [Singdata SQL Reference Manual](sql-reference.md) - Complete SQL syntax reference, including Table Stream related operations

***

*Note: This guide is based on testing results from the Singdata Lakehouse version as of May 2025. Subsequent versions may change. Please regularly check the official documentation for the latest information.*
