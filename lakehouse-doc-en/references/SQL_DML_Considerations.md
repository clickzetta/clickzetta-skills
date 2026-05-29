# Lakehouse SQL DML Statement Usage Guide

## 1. INSERT Statement Specification

### 1.1 Basic Syntax

```sql
INSERT INTO|OVERWRITE [TABLE] table_name 
    [ PARTITION partition_spec] 
    [ (column1, column2, ...)] 
    {VALUES(value1 [,...],(value2 [,...]),...) | subquery}
```

### 1.2 Recommended Data Import Methods

#### Bulk Data Import - Preferred Approach

* **Recommended**: `INSERT INTO...SELECT` statement
* **Recommended**: COPY INTO command with Volume storage
* **Recommended**: Professional data import tools

```sql
-- ✅ Recommended: Use SELECT method
INSERT INTO target_table 
SELECT col1, col2, col3 FROM source_table WHERE condition;

-- ✅ Recommended: Use COPY INTO command
COPY INTO target_table 
FROM VOLUME my_volume 
USING CSV OPTIONS ('header' = 'true');
```

#### Small Data Import - VALUES Method

```sql
-- ✅ Suitable for: Small data volume (recommended within 100 rows)
INSERT INTO table_name VALUES 
(1, 'data1'), (2, 'data2'), (3, 'data3');
```

**Advantages of Recommended Methods**:

* Higher import performance and throughput
* Better resource utilization
* Transactional guarantee support
* Reduced network transmission overhead

### 1.3 Data Type Literal Syntax

#### Types Requiring Prefixes

```sql
date'2023-12-25'                       -- DATE type
timestamp'2023-12-25 15:30:45'         -- TIMESTAMP type
timestamp'2023-12-25 15:30:45.123'     -- Millisecond precision supported
json'{"key": "value", "num": 123}'     -- JSON type
X'48656C6C6F'                          -- BINARY type (hexadecimal)
```

#### Types with Optional Suffixes

```sql
-- Numeric type suffixes are optional; both forms are valid
1       -- or 1l (BIGINT)
100     -- or 100s (SMALLINT)  
200     -- INT type
89.5    -- or 89.5f (FLOAT)
3.14159 -- or 3.14159d (DOUBLE)
99.99   -- or 99.99bd (DECIMAL)
```

#### Composite Type Syntax

```sql
ARRAY(1,2,3)                          -- ARRAY type
MAP('k1','v1','k2','v2')             -- MAP type
STRUCT(1, 'hello', 3.14)             -- STRUCT type
```

### 1.4 INSERT OVERWRITE Behavior

* **Partitioned Table**: Overwrites matching partition data
* **Non-partitioned Table**: Overwrites entire table data
* **Prerequisite**: Target table must exist

### 1.5 Partition Operation Limits

* **Partition Count Limit**: Maximum 2048 partitions per task
* **Exceeding Limit**: Import in batches or optimize partition strategy
* **Recommended Check**: Count partitions before bulk import

### 1.6 Column Mapping and Type Matching

* **Explicit Specification**: Recommended to explicitly specify target column names
* **Type Matching**: Ensure precise data type correspondence
* **NULL Handling**: Unspecified columns will be filled with NULL values

## 2. UPDATE Statement Specification

### 2.1 Basic Syntax

```sql
UPDATE target_table 
SET column_name1 = new_value1 [, column_name2 = new_value2, ...] 
[ WHERE condition ] 
[ORDER BY ...] 
[LIMIT row_count]
```

### 2.2 WHERE Condition Requirements

* **Necessity**: Strongly recommended to use WHERE conditions to limit the update scope
* **Precision**: Use precise conditions to avoid mistaken operations
* **Complex Queries**: Subqueries and expressions are supported

### 2.3 Batch Update Optimization

* **Batch Processing**: Use ORDER BY + LIMIT for batched updates
* **Determinism**: ORDER BY ensures consistent update ordering
* **Performance Control**: LIMIT controls the number of rows updated per batch

### 2.4 Safe Operation Recommendations

* **Test First**: Validate in a test environment before production
* **Data Backup**: Create backups before important updates
* **Rollback Preparation**: Prepare a data recovery plan

## 3. DELETE Statement Specification

### 3.1 Basic Syntax

```sql
DELETE FROM table_name WHERE condition;
```

### 3.2 Safety Requirements

* **WHERE Condition**: Avoid omitting WHERE to prevent full table deletion
* **Condition Validation**: Verify condition accuracy before deletion
* **Backup Protection**: Back up important data before deletion

### 3.3 Performance Optimization

* **Index Utilization**: Fully leverage indexes in WHERE conditions
* **Partition Filtering**: Use partition columns for filtering on partitioned tables
* **Batch Deletion**: Consider batched execution for large-scale deletions

## 4. MERGE INTO Statement Specification

### 4.1 Basic Syntax

```sql
MERGE INTO target_table USING source_table ON merge_condition 
{ WHEN MATCHED [AND matched_condition] THEN matched_action |
  WHEN NOT MATCHED [AND not_matched_condition] THEN not_matched_action } ...
```

### 4.2 Statement Order Requirements

**WHEN MATCHED must precede WHEN NOT MATCHED**

```sql
-- ✅ Correct order
MERGE INTO target USING source ON target.key = source.key 
WHEN MATCHED THEN UPDATE SET target.col1 = source.col1
WHEN NOT MATCHED THEN INSERT (col1, col2) VALUES (source.col1, source.col2);
```

### 4.3 Match Condition Design

* **Uniqueness**: Ensure the ON condition produces one-to-one matching
* **Determinism**: Avoid multiple source rows matching the same target row
* **Filter Support**: AND conditions are supported for additional filtering

### 4.4 Operation Types

* **MATCHED Operations**: UPDATE SET or DELETE
* **NOT MATCHED Operations**: INSERT statement
* **Conditional Execution**: Multiple WHEN clauses are executed in the specified order

## 5. TRUNCATE Statement Specification

### 5.1 Basic Syntax

```sql
TRUNCATE TABLE [IF EXISTS] table_name;
```

### 5.2 Operational Characteristics

* **Data Clearing**: Deletes all records but retains the table structure
* **Performance Advantage**: More efficient than DELETE FROM
* **Irrecoverable**: Data cannot be directly recovered after the operation

### 5.3 Usage Recommendations

* **IF EXISTS**: Use the IF EXISTS clause to avoid errors
* **Permission Check**: Ensure you have the appropriate operation permissions
* **Backup Protection**: Back up data before operating on important tables

## 6. Dynamic Table DML Specification

### 6.1 Parameter Configuration

```sql
-- Recommended to explicitly enable DML operations
set cz.optimizer.incremental.backfill.enabled=true;
```

### 6.2 Supported Operations

```sql
-- ✅ Fully supported
INSERT INTO dynamic_table VALUES (1, 'data', 100);
INSERT OVERWRITE dynamic_table SELECT * FROM source;
DELETE FROM dynamic_table WHERE condition;
TRUNCATE TABLE dynamic_table;
```

### 6.3 Operation Limitations

* **UPDATE Limitation**: UPDATE operations have technical limitations; using DELETE + INSERT as a workaround is recommended
* **Refresh Impact**: DML operations may cause the next refresh to switch to full mode
* **Performance Consideration**: Full refresh incurs higher overhead than incremental refresh

## 7. Performance Optimization Strategies

### 7.1 Partition Design Principles

* **Partition Size**: Follow industry standards; avoid overly small partitions that affect query performance
* **Partition Count**: Control the total number of partitions, balancing storage and query efficiency
* **Filter Optimization**: Partition columns should be commonly used filter conditions

### 7.2 Bucketing Configuration Strategy

* **Bucket Column Selection**: Choose high-cardinality, evenly-distributed columns
* **Bucket Count**: Determine a reasonable number based on data volume and query patterns
* **Sort Optimization**: Choose frequently queried columns for SORTED BY

### 7.3 Index Optimization

* **BLOOM FILTER Index**: Suitable for equality queries and high-cardinality columns
* **INVERTED Index**: Suitable for full-text search; requires specifying an analyzer
* **VECTOR Index**: Suitable for vector similarity search scenarios

### 7.4 Small File Management

```sql
-- Auto-compaction configuration
SET cz.sql.compaction.after.commit = true;

-- Manual compaction command
OPTIMIZE table_name [WHERE predicate] [OPTIONS ('key' = 'value')];
```

## 8. Data Type Conversion

### 8.1 Conversion Methods

```sql
-- CAST function
CAST(expression AS type)

-- Conversion operator
expression::type

-- TYPE function (returns NULL on conversion failure)
TYPE(expr)
```

### 8.2 Conversion Rules

* **Numeric Widening**: Conversions that expand precision are supported
* **String Conversion**: Conversions that increase length are supported
* **Date Conversion**: Bidirectional conversion between strings and date types
* **Overflow Handling**: Be aware of numeric conversion overflow risks

### 8.3 TIMESTAMP Handling

* **Format Support**: Standard format, millisecond precision, ISO 8601
* **Timezone Handling**: Default TIMESTAMP_LTZ type
* **Precision Support**: Up to microsecond precision supported

## 9. Transaction and Version Control

### 9.1 Historical Version Query

#### View Table History

```sql
-- View complete operation history of a table
DESCRIBE HISTORY table_name;
```

Returned information includes:

* **version**: Version number
* **time**: Operation time
* **total_rows**: Total row count for that version
* **operation**: Operation type (CREATE, INSERT_INTO, UPDATE, DELETE, TRUNCATE, etc.)
* **user**: Executing user
* **job_id**: Job ID

#### Time Travel Queries

```sql
-- Query historical data using relative time
SELECT * FROM table_name 
TIMESTAMP AS OF (CURRENT_TIMESTAMP() - INTERVAL '1' HOUR);

-- Query using absolute time (requires a precise timestamp)
SELECT * FROM table_name 
TIMESTAMP AS OF '2025-06-18 10:30:45.123';

-- Use CAST function to specify timezone
SELECT * FROM table_name 
TIMESTAMP AS OF CAST('2025-06-18 10:30:45 Asia/Shanghai' AS TIMESTAMP);
```

### 9.2 Data Recovery Operations

#### Table Data Recovery

```sql
-- Restore table to a specified point in time
RESTORE TABLE table_name TO TIMESTAMP AS OF '2025-06-18 10:30:45';

-- Restore Dynamic Table
RESTORE DYNAMIC TABLE table_name TO TIMESTAMP AS OF '2025-06-18 10:30:45';
```

Supported time formats:

* Full timestamp: '2025-06-18 10:30:45.123'
* Second-level precision: '2025-06-18 10:30:45'
* With timezone: '2025-06-18 10:30:45 Asia/Shanghai'
* Relative time: CURRENT_TIMESTAMP() - INTERVAL '1' DAY

#### Recover Dropped Objects

```sql
-- Recover a dropped table
UNDROP TABLE table_name;

-- Recover a dropped Dynamic Table
UNDROP DYNAMIC TABLE table_name;

-- Recover a dropped Materialized View
UNDROP MATERIALIZED VIEW view_name;
```

### 9.3 Change Tracking Configuration

#### Enable Change Tracking

```sql
-- Enable change tracking for a table
ALTER TABLE table_name SET PROPERTIES('change_tracking' = 'true');
```

#### Create Table Stream

```sql
-- Create a Table Stream in standard mode
CREATE TABLE STREAM stream_name 
ON TABLE table_name
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Create a Table Stream in append-only mode
CREATE TABLE STREAM stream_name 
ON TABLE table_name
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

### 9.4 Data Retention Policy

#### Set Data Retention Period

```sql
-- Set the Time Travel data retention period (unit: days)
ALTER TABLE table_name SET PROPERTIES('data_retention_days' = '7');

-- Set the data lifecycle (auto-clean historical data)
ALTER TABLE table_name SET PROPERTIES('data_lifecycle' = '365');
```

#### Query Historical Load Records

```sql
-- View historical load records for a table
SELECT * FROM load_history('schema.table_name');
```

## 10. System Parameter Configuration

### 10.1 DML-Related Parameters

```sql
-- Enable DML for Dynamic Tables
set cz.optimizer.incremental.backfill.enabled=true;

-- Auto-compaction for small files
SET cz.sql.compaction.after.commit = true;

-- Query tag setting
SET query_tag = 'dml_operation';

-- Session timezone configuration
SET timezone = 'Asia/Shanghai';
```

### 10.2 Workspace-Level Configuration

#### Auto Index Recommendation

```sql
-- Enable workspace-level auto index recommendation
ALTER WORKSPACE workspace_name SET properties (auto_index='day[,150,5,100]');
```

Parameter description:

* **day**: Recommendation frequency (daily)
* **150**: Query count threshold
* **5**: Query duration threshold (seconds)
* **100**: Index recommendation count limit

## 11. Error Handling Guide

### 11.1 Common Error Types

#### Data Type Conversion Error

```
Error message: implicit cast not allowed for 'colX': string not null to date/timestamp/json/binary
Solution: Use the correct type prefix syntax
```

#### Partition Count Exceeded Error

```
Error message: The count of dynamic partitions exceeds the maximum number 2048
Solution: Import in batches or optimize the partition strategy
```

#### MERGE Statement Order Error

```
Error message: Syntax error at or near 'WHEN'
Solution: Adjust the order of WHEN clauses
```

#### Dynamic Table UPDATE Limitation

```
Error message: Not support hidden column :MV__KEY
Solution: Use DELETE + INSERT instead of UPDATE
```

### 11.2 Performance Diagnosis

```sql
-- Query execution plan
EXPLAIN SELECT * FROM table_name WHERE condition;

-- Check partition information
SHOW PARTITIONS EXTENDED table_name;
```

## 12. Best Practices

### 12.1 Data Type Usage Specification

| Data Type  | Prefix Required | Syntax Example                     |
| ---------- | --------------- | ---------------------------------- |
| DATE       | Required        | `date'2023-12-25'`                 |
| TIMESTAMP  | Required        | `timestamp'2023-12-25 15:30:45'`   |
| JSON       | Required        | `json'{"key": "value"}'`           |
| BINARY     | Required        | `X'48656C6C6F'`                    |
| BIGINT     | Optional        | `1` or `1l`                        |
| DECIMAL    | Optional        | `99.99` or `99.99bd`               |
| FLOAT      | Optional        | `89.5` or `89.5f`                  |
| DOUBLE     | Optional        | `3.14` or `3.14d`                  |

### 12.2 INSERT Statement Template

```sql
-- Recommended bulk data import
INSERT INTO target_table 
SELECT col1, col2, col3 FROM source_table WHERE condition;

-- Type-safe VALUES insertion
INSERT INTO table_name (
    bigint_col, decimal_col, date_col, 
    timestamp_col, json_col, binary_col
) VALUES (
    1, 99.99, date'2023-12-25',
    timestamp'2023-12-25 15:30:45',
    json'{"key": "value"}', X'48656C6C6F'
);
```

### 12.3 MERGE Statement Template

```sql
MERGE INTO target_table AS target 
USING source_table AS source 
ON target.key_column = source.key_column 
WHEN MATCHED THEN 
    UPDATE SET target.col1 = source.col1, target.col2 = source.col2
WHEN NOT MATCHED THEN 
    INSERT (key_column, col1, col2) 
    VALUES (source.key_column, source.col1, source.col2);
```

### 12.4 Dynamic Table DML Template

```sql
-- Session configuration
set cz.optimizer.incremental.backfill.enabled=true;

-- Supported operations
INSERT INTO dynamic_table VALUES (1, 'data', 100);
DELETE FROM dynamic_table WHERE condition;

-- Workaround for UPDATE
DELETE FROM dynamic_table WHERE key_column = target_value;
INSERT INTO dynamic_table VALUES (new_key, new_col1, new_col2);
```

### 12.5 Safe Operation Principles

1. **Test First**: Complete test validation before production operations
2. **Backup Protection**: Create backups before critical data operations
3. **Least Privilege**: Use the minimum necessary permissions for operations
4. **Precise Conditions**: Use precise WHERE conditions to limit operation scope
5. **Monitor and Audit**: Record execution logs of important DML operations

### 12.6 Performance Optimization Principles

1. **Batch First**: Prioritize batch operations for efficiency
2. **Index Utilization**: Fully leverage indexes to accelerate queries and DML
3. **Partition Filtering**: Use partition pruning to reduce data scanning
4. **Resource Management**: Properly configure compute resources and concurrency
5. **File Management**: Regularly perform small file compaction optimization

### 12.7 Version Control and Data Recovery Principles

1. **Set Data Retention**: Configure the data retention period based on business requirements
2. **Enable Change Tracking**: Enable change tracking for important tables to facilitate data auditing
3. **Regular History Review**: Periodically review table operation history to detect anomalies
4. **Verify Recovery Operations**: Validate recovery results in a test environment before executing
5. **Time Travel Queries**: Use relative time queries to avoid timezone issues

### 12.8 Table Stream Usage Principles

```sql
-- Recommended Stream creation and usage pattern
-- 1. Enable change tracking
ALTER TABLE source_table SET PROPERTIES('change_tracking' = 'true');

-- 2. Create Stream
CREATE TABLE STREAM change_stream 
ON TABLE source_table
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- 3. Query change data
SELECT * FROM change_stream WHERE cz_stream_action IN ('INSERT', 'UPDATE', 'DELETE');
```

### 12.9 Historical Version and Data Recovery Template

```sql
-- View table history
DESCRIBE HISTORY table_name;

-- Time Travel query
SELECT * FROM table_name 
TIMESTAMP AS OF (CURRENT_TIMESTAMP() - INTERVAL '1' HOUR);

-- Data recovery
RESTORE TABLE table_name TO TIMESTAMP AS OF '2025-06-18 10:30:45';

-- Recover dropped table
UNDROP TABLE table_name;

-- Enable change tracking
ALTER TABLE table_name SET PROPERTIES('change_tracking' = 'true');

-- Create Table Stream
CREATE TABLE STREAM stream_name 
ON TABLE table_name
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Set data retention period
ALTER TABLE table_name SET PROPERTIES('data_retention_days' = '7');
```

***

**Note**: This document is compiled based on the Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, always verify the correctness and performance impact of all operations in a test environment.
