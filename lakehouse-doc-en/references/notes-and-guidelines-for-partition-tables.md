# Lakehouse Partition Usage Guide

## Document Goal

**If you are migrating from another data platform to the Singdata Lakehouse, this document will help you fully leverage the advanced advantages of Lakehouse partitioning.**

The Singdata Lakehouse partitioning is based on Apache Iceberg's hidden partitioning concept, offering significant advantages over traditional partitioning: no need to manually specify partition conditions, automatic partition pruning, and more flexible partition evolution. This document is aimed at experienced data engineers from major data platforms, covering migration scenarios from mainstream platforms such as Hive, Spark, MaxCompute, Snowflake, and Databricks, focusing on **how to migrate successfully** and **maximize value**.

### What You Will Gain

* **Advanced Concept Understanding**: Master the innovative value and usage of hidden partitioning
* **Migration Best Practices**: Proven successful migration strategies and implementation steps
* **Performance Optimization Guidance**: Practical tips to fully leverage Lakehouse partition performance advantages
* **Architecture Upgrade Solutions**: Optimize complex partition architectures into more efficient Lakehouse solutions
* **Practical Verification Methods**: Verification steps to ensure partitioned tables are correctly created and perform well

### Core Advantages of Lakehouse Partitioning

* **Intelligent Partition Pruning**: No need to manually specify partition conditions in queries; the system automatically optimizes
* **Simplified Partition Management**: Say goodbye to complex partition maintenance and focus on business logic
* **Better Performance Predictability**: Avoid over-partitioning, ensuring stable query performance
* **Modern Architecture Design**: Advanced partition concepts based on Apache Iceberg

***

## Understanding Core Differences and Advantages

### 5 Innovative Features of Lakehouse Partitioning

#### 1. Intelligent Transform Partition Functions

**Innovation Value**: Avoid conflicts with standard SQL functions, providing more precise time partition control

```sql
-- Elegant Lakehouse design
CREATE TABLE events PARTITIONED BY (days(event_date));  -- Precise day-level partitioning

-- Why use plural forms?
-- Avoids conflicts with SQL standard functions like year(), month()
-- Provides clearer semantics: years = number of years, not extracting the year
-- The return value is a computed number: days('2024-06-01') = 19875
-- years('2024-06-01') = 54 (year offset calculated from 1970)
```

**Key Understanding Points for Migration**:

* `years/months/days/hours` are plural forms, with more accurate semantics
* Transform partitions avoid logic conflicts, ensuring partition strategy consistency
* Return values are computed numbers; the system automatically handles transformation logic
* Time function calculation baseline: years from 1970, days from 1970-01-01

#### 2. Automatic Optimization of Hidden Partitioning

**Innovation Value**: Users don't need to worry about partition implementation details, focusing on business logic

```sql
-- Clean query in Lakehouse
SELECT * FROM sales WHERE order_date = '2024-06-01';  
-- System automatically converts to partition condition, no manual partition specification needed

-- Advantages compared to traditional approach
-- 1. Cleaner queries, no complex partition conditions
-- 2. Partition strategy changes don't affect query logic
-- 3. System automatically selects the optimal partition scan strategy
```

#### 3. Intelligent Partition Count Control

**Design Philosophy**: Partition count limits are a performance protection mechanism, encouraging better partition design

```sql
-- Lakehouse partition philosophy: Quality over quantity
-- Traditional thinking: Partition as granularly as possible
-- Lakehouse philosophy: Reasonable partition granularity + index optimization

-- Recommended efficient design
CREATE TABLE user_events (
    event_id INT,
    user_id INT,
    event_data JSON,
    event_time TIMESTAMP_LTZ
) PARTITIONED BY (days(event_time));  -- Time partition (primary)

CREATE BLOOMFILTER INDEX idx_user ON TABLE user_events(user_id);  -- Index optimization (auxiliary)

-- Advantages: Avoids small file issues, ensures each partition has sufficient data volume
-- Limitation note: It is recommended to control single-operation partition count within a reasonable range
```

#### 4. Logical Consistency of Transform Partitions

**Design Principle**: Avoid conflicting partition dimensions, ensuring clear partition logic

```
-- When using transform partitions, avoid combining time granularities that conflict logically
-- For example, using both years() and months() causes conflicts
-- Choose a single time granularity: days() is the most commonly recommended option
```

#### 5. Type-Safe Partition Design

**Security Guarantee**: Prevent data write errors through type checking

```sql
-- Lakehouse type safety mechanism
CREATE TABLE orders (
    id INT,
    amount DOUBLE
) PARTITIONED BY (order_date STRING);  -- Explicit STRING type

-- Type mismatch will cause errors
INSERT INTO orders VALUES (1, 100.0, '2024-06-01');  -- String written to STRING partition: correct
INSERT INTO orders VALUES (1, 100.0, DATE('2024-06-01'));  -- DATE written to STRING partition: error

-- Recommended approach: Use transform partitions to avoid type issues
CREATE TABLE orders_safe (
    id INT,
    amount DOUBLE,
    order_timestamp TIMESTAMP_LTZ
) PARTITIONED BY (days(order_timestamp));  -- Let the system handle type conversion
```

### Cognitive Upgrade: From Complex to Simple

#### Traditional Partitioning vs Lakehouse Partitioning

| Dimension         | Traditional Partition Mindset     | Lakehouse Partition Philosophy | Advantage          |
| ---------- | ---------- | ------------- | ----------- |
| **Partition Strategy**   | The more granular the better, multi-dimensional partitioning | Reasonable granularity, key dimensions     | Avoids small files, stable performance  |
| **Query Method**   | Must specify partition conditions   | Automatic partition pruning        | Cleaner queries, easier maintenance |
| **Type Handling**   | Manual type conversion   | System-level type safety      | Fewer errors, higher reliability  |
| **Maintenance Cost**   | Complex partition management    | Simplified partition maintenance       | Lower operational costs      |
| **Performance Predictability** | Depends on partition design experience   | System-guaranteed performance        | More stable query performance    |

***

## Partition Table Creation Verification (Best Practice)

### Post-Creation Verification: Ensuring Partition Tables Work Correctly

Regardless of how you create the partition table (SQL, tools, scripts), it is recommended to verify immediately after creation. This is the best practice to ensure partition functionality works properly.

#### Recommended Creation and Verification Flow

```sql
-- 1. Create partition table (native SQL recommended for syntax accuracy)
CREATE TABLE orders_partitioned (
    id INT,
    amount DOUBLE,
    order_date DATE
) PARTITIONED BY (days(order_date));

-- 2. Immediately verify the partition table was created correctly (mandatory step)
SHOW PARTITIONS orders_partitioned;
-- Correct: Shows partition list or empty list
-- Abnormal: Error "not a partitioned table"
```

#### Complete Verification Checklist (Execute After Every Creation)

```sql
-- Verification Step 1: Confirm it is a partitioned table
SHOW PARTITIONS orders_partitioned;

-- Verification Step 2: Test data insertion and partition creation
INSERT INTO orders_partitioned VALUES (1, 100.50, DATE('2024-06-01'));
SHOW PARTITIONS orders_partitioned;
-- Correct: Shows a partition like "days(order_date)=19875"

-- Verification Step 3: Verify partition pruning is effective
SELECT * FROM orders_partitioned WHERE order_date = '2024-06-01';
-- Should return data normally with good performance

-- Verification Step 4: Check table structure
DESCRIBE TABLE orders_partitioned;
-- Confirm column structure is correct and partition field types match

-- Verification Step 5: Test max partition retrieval (compatibility verification)
SELECT max_pt('orders_partitioned');
-- Should return the maximum partition value, used for compatibility with similar features on the original platform
```

#### Solutions When Verification Fails

| Verification Failure Symptom                      | Possible Cause          | Solution       |
| --------------------------- | ------------- | ---------- |
| `not a partitioned table`   | Table creation syntax error or tool creation anomaly | Re-create with native SQL |
| `implicit cast not allowed` | Partition field type mismatch     | Check inserted data types   |
| No partitions displayed                       | Partition function syntax error      | Check if plural forms are used |
| No performance improvement                       | Query not utilizing partition fields     | Optimize WHERE conditions  |

**Why Verification is Needed**?

* Ensure partition definition syntax is correct, avoiding performance issues
* Detect configuration errors early, reducing subsequent troubleshooting costs
* Verify partition strategy matches query patterns

***

## SHOW PARTITIONS Complete Feature Guide

### Basic Syntax and Advanced Usage

```sql
-- Complete syntax
SHOW PARTITIONS [EXTENDED] table_name 
[ PARTITION ( partition_col_name = partition_col_val [, ...] ) ] 
[WHERE <expr>]
```

### Basic Usage

```sql
-- View all partitions
SHOW PARTITIONS sales_table;

-- View partition details
SHOW PARTITIONS EXTENDED sales_table;

-- View specific partition
SHOW PARTITIONS sales_table PARTITION (pt1 = '2023');

-- Multi-level partition filter
SHOW PARTITIONS sales_table PARTITION (pt1 = '2023', pt2 = '01');

-- Limit results
SHOW PARTITIONS EXTENDED sales_table LIMIT 10;
```

### Advanced Usage: Partition Health Check Tool

Important Limitation: `SHOW PARTITIONS` does not support `ORDER BY` clause. Use WITH subquery if sorting is needed.

```sql
-- Partition health check
SHOW PARTITIONS EXTENDED table_name WHERE bytes > 100*1024*1024;

-- Partition info view (supports LIMIT)
SHOW PARTITIONS EXTENDED table_name LIMIT 10;

-- Partition sorting (via WITH subquery)
WITH partition_info AS (
    SELECT partitions, bytes, total_rows, total_files, created_time
    FROM (SHOW PARTITIONS EXTENDED table_name)
)
SELECT * FROM partition_info ORDER BY CAST(bytes AS BIGINT) DESC LIMIT 10;
```

### MAX_PT Function - Get Latest Partition

```sql
-- MAX_PT function: Gets the maximum partition value from a partitioned table
-- Syntax: max_pt('schema_name.table_name' | 'table_name')

-- Basic usage: Query data from the latest partition
SELECT * FROM sales_table WHERE pt = max_pt('sales_table');

-- Cross-schema usage
SELECT max_pt('prod_schema.sales_table');

-- Practical application scenarios:
-- 1. Incremental data processing: Always process the latest partition
INSERT INTO target_table 
SELECT * FROM source_table 
WHERE pt = max_pt('source_table');

-- 2. Data quality check: Check data quality of the latest partition
SELECT COUNT(*), AVG(amount), MAX(created_time)
FROM orders 
WHERE pt = max_pt('orders');
```

**Migration Value of MAX_PT Function**:

* **MaxCompute Users**: Direct replacement for the original max_pt function, no query logic changes needed
* **Hive Users**: Simplify complex max partition queries, improving development efficiency
* **Other Platform Users**: Provides a convenient way to query the latest data

***

## Advanced Partition Table Creation Guide

### Partition + Bucket + Sort Combinations

```sql
-- Option 1: Partition + Bucket (recommended for hash distribution)
CREATE TABLE events_clustered (
    user_id INT,
    event_type STRING,
    event_data JSON,
    event_time TIMESTAMP_LTZ
) PARTITIONED BY (days(event_time))
  CLUSTERED BY (user_id) INTO 32 BUCKETS;

-- Option 2: Partition + Sort (recommended for range queries)
CREATE TABLE events_sorted (
    user_id INT,
    event_type STRING,
    event_data JSON,
    event_time TIMESTAMP_LTZ
) PARTITIONED BY (days(event_time))
  SORTED BY (event_type);

CREATE TABLE events_both
(
    user_id INT,
    event_type STRING,
    event_data JSON,
    event_time TIMESTAMP_LTZ
)
 PARTITIONED BY (days(event_time))
CLUSTERED BY (user_id) 
SORTED BY (event_type)
INTO 32 BUCKETS;
```

### bucket Function Usage Guide

**Parameter Range and Recommendations**:

```sql
-- Recommended bucket count range
CREATE TABLE sales PARTITIONED BY (
    days(sale_date),
    bucket(10, user_id)    -- Recommended: reasonable range of 1-1000
);

-- bucket count selection guide:
-- 1-10 buckets: Suitable for small data volume tables (< 1 million rows)
-- 10-100 buckets: Suitable for medium data volume tables (1-10 million rows)
-- 100-1000 buckets: Suitable for large data volume tables
```

### Complex Data Type Support

```sql
-- Lakehouse supports partitioning for all modern data types
CREATE TABLE modern_table (
    user_id INT,
    user_profile STRUCT<name: STRING, age: INT, location: STRING>,
    tags ARRAY<STRING>,
    metadata MAP<STRING, STRING>,
    config JSON,
    created_date DATE,
    created_timestamp TIMESTAMP_LTZ,
    created_timestamp_ntz TIMESTAMP_NTZ
) PARTITIONED BY (days(created_date));

-- Supported partition field types:
-- Basic types: INT, BIGINT, STRING, DATE, TIMESTAMP_LTZ, TIMESTAMP_NTZ
-- Transform partitions: years(), months(), days(), hours(), bucket()
-- Not supported: STRUCT, ARRAY, MAP, JSON as direct partition fields
```

### Special Cases for Partition Values

```sql
-- NULL value partition handling
CREATE TABLE user_regions (
    user_id INT,
    region STRING  -- Allows NULL values
) PARTITIONED BY (region);

INSERT INTO user_regions VALUES (1, NULL);
-- Result: Creates region=NULL partition

-- Special character support
INSERT INTO user_regions VALUES 
(2, 'beijing'),           -- Normal characters
(3, 'shang-hai'),         -- Supports hyphens
(4, 'guang_zhou'),        -- Supports underscores  
(5, 'xi an'),             -- Supports spaces
(6, 'very_long_city_name_with_many_characters');  -- Supports long strings

-- View partition results
SHOW PARTITIONS user_regions;
-- Result display: region=NULL, region=beijing, region=shang-hai, etc.

-- Special character support summary:
-- Supported: letters, numbers, underscores, hyphens, spaces, Chinese characters
-- Length: Supports very long partition values (tested with 100+ characters)
-- Note: Avoid special symbols like @#$% although they may be supported, it's not recommended
```

***

## Complex Partition Migration Strategies

### Multi-Level Partition Architecture Migration Challenges

If you implemented complex partition strategies on your original platform, you will encounter architectural limitations and design choices when migrating to the Lakehouse.

#### Migration Challenges for Composite Dimension Partitions

**Composite Partitions on the Original Platform**:

```sql
-- Common composite partitions in MaxCompute/Hive
CREATE TABLE sales PARTITIONED BY (
    dt STRING,           -- Date: 20240601
    region STRING,       -- Region: beijing, shanghai
    channel STRING       -- Channel: online, offline
);

-- Partition count = number of dates x number of regions x number of channels
-- Example: 365 x 10 x 3 = 10,950 partitions/year
```

**Problems with Direct Migration**:

Directly copying composite partitions will result in too many partitions. The recommended approach is to reduce partition dimensions by combining time partitions with indexes.

**Strategy 1: Simplified Partition + Index**

```sql
-- Simplified from 3-level partitions to 1 time partition + 2 indexes
CREATE TABLE sales (
    sale_id INT,
    amount DOUBLE,
    region STRING,
    channel STRING,
    sale_date DATE
) PARTITIONED BY (days(sale_date));
-- Partition count per year: ~365

-- Create index optimizations for non-partition query columns
CREATE BLOOMFILTER INDEX idx_region ON TABLE sales(region);
CREATE BLOOMFILTER INDEX idx_channel ON TABLE sales(channel);

-- Query with partition pruning + index acceleration
SELECT * FROM sales 
WHERE sale_date >= '2024-06-01' 
  AND sale_date <= '2024-06-30'  -- Partition pruning
  AND region = 'beijing'                     -- Index acceleration
  AND channel = 'online';                    -- Index acceleration
```

**Strategy 2: Hash Partition Redesign**

```sql
-- Use hash function to reduce partition count
CREATE TABLE sales (
    sale_id INT,
    amount DOUBLE,
    region STRING,
    channel STRING,
    sale_date DATE
) PARTITIONED BY (
    days(sale_date),           -- Time partition
    bucket(10, region)         -- Region hashed into 10 buckets
);

-- Partition count = 365 x 10 = 3,650 partitions/year (manageable)
```

### Partition Evolution and Maintenance Strategy Migration

#### Differences in Dynamic Partition Management

**Partition Management on Original Platform**:

```sql
-- Partition management in Hive
-- 1. Dynamic partition auto-creation
INSERT OVERWRITE TABLE target PARTITION(dt, region)
SELECT ..., dt, region FROM source;  -- Auto-creates all dt x region combinations

-- 2. Partition repair
MSCK REPAIR TABLE target;  -- Auto-discover new partitions

-- 3. Partition deletion
ALTER TABLE target DROP PARTITION (dt<'20240101');  -- Batch deletion
```

**Equivalent Implementation in Lakehouse**:

```sql
-- 1. Dynamic partition creation (pay attention to partition count)
-- Recommended to check partition count first
SELECT COUNT(DISTINCT CONCAT(dt, '/', region)) FROM source;

-- Process in batches (if count is large)
INSERT INTO target 
SELECT ..., dt, region FROM source 
WHERE dt BETWEEN '20240601' AND '20240615';

-- 2. Partition discovery (automatic, no manual repair needed)
-- Lakehouse automatically manages partition metadata

-- 3. Partition cleanup (more powerful features)
TRUNCATE TABLE target PARTITION (dt = '20240101');
```

#### Partition Lifecycle Management Migration

**MaxCompute's Automatic Lifecycle**:

```sql
-- Setting table-level lifecycle in MaxCompute
ALTER TABLE events SET LIFECYCLE 90;  -- Auto-delete after 90 days

-- Partition-level lifecycle
ALTER TABLE events PARTITION(dt='20240101') SET LIFECYCLE 30;  -- Single partition 30 days
```

**Partition Cleanup Features in Lakehouse**:

```sql
-- Basic partition cleanup (for STRING partitions)
TRUNCATE TABLE events PARTITION (dt = '20240101');

-- Transform partition cleanup (requires specific partition value)
TRUNCATE TABLE events_with_days PARTITION (days(event_date) = 19875);

-- Advanced feature: Conditional filter cleanup
-- Delete all partitions older than 90 days (need to calculate specific partition values first)
-- For STRING partitions:
TRUNCATE TABLE events 
PARTITION (dt < date_format(date_sub(current_date(), 90), 'yyyyMMdd'));

-- Composite condition cleanup: Delete data for specific date and region
TRUNCATE TABLE sales 
PARTITION (days(sale_date) = 19875 AND region = 'beijing');

-- Batch partition cleanup: Clean multiple partitions simultaneously
TRUNCATE TABLE logs 
PARTITION (days(log_date) = 19875), 
PARTITION (days(log_date) = 19876);
```

**Partition Cleanup Best Practices**:

```sql
-- 1. Check partitions to delete before cleanup
SHOW PARTITIONS EXTENDED table_name 
WHERE dt < '2024-01-01';

-- 2. Clean large numbers of partitions in stages (avoid long table locks)
-- For STRING partitions:
TRUNCATE TABLE large_table 
PARTITION (dt = '20230101');
-- Then continue cleaning the next day's data

-- For transform partitions, query the partition value first:
-- SELECT days('2023-01-01'); -- Get the specific partition value
TRUNCATE TABLE large_table_with_days
PARTITION (days(date_col) = specific_partition_value);

-- 3. Periodic cleanup scheduling script example
-- Execute daily at 2 AM, clean partitions older than 30 days (STRING partition)
TRUNCATE TABLE daily_logs 
PARTITION (dt < date_format(date_sub(current_date(), 30), 'yyyyMMdd'));
```

### Performance Optimization Strategy Migration

#### Equivalent Implementation of Z-Order Optimization

**Databricks Delta Lake Z-Order**:

```sql
-- Multi-dimensional optimization in Delta Lake
OPTIMIZE events ZORDER BY (user_id, event_type, timestamp);
-- Achieves joint optimization of multiple fields
```

**Equivalent Strategies in Lakehouse**:

```sql
-- Strategy 1: Partition + Bucket combination (recommended)
CREATE TABLE events (
    user_id INT,
    event_type STRING,
    event_data JSON,
    timestamp TIMESTAMP_LTZ
) PARTITIONED BY (days(timestamp))    -- Time partition
  CLUSTERED BY (user_id) INTO 32 BUCKETS;  -- User hash bucketing

-- Strategy 2: Partition + Sort combination
CREATE TABLE events_sorted (
    user_id INT,
    event_type STRING,
    event_data JSON,
    timestamp TIMESTAMP_LTZ
) PARTITIONED BY (days(timestamp))    -- Time partition
  SORTED BY (event_type);             -- Event type sort

-- Strategy 3: Rewrite optimization (similar to OPTIMIZE)
INSERT OVERWRITE events 
SELECT * FROM events 
ORDER BY user_id, event_type, timestamp;  -- Manual data reordering
```

#### Partition Pruning Optimization Migration

**Original Platform Partition Pruning Logic**:

```sql
-- Complex partition filtering in Spark
df.filter(
    (col("year") >= 2024) & 
    (col("month") >= 6) & 
    (col("day") >= 1)
)
```

**Equivalent Query in Lakehouse**:

```sql
-- In Lakehouse, transform to range query on a single partition dimension
SELECT * FROM events
WHERE event_date >= '2024-06-01' 
  AND event_date <= '2024-06-30'  -- month range filtering
  AND region = 'beijing';                  -- region = "beijing"

-- Key: Transform complex partition logic into simple time range queries
```

***

## Platform-Specific Migration Notes

### Hive Users: Special Attention Required

#### Syntax Compatibility Differences

```sql
-- Hive syntax is still supported in Lakehouse
CREATE TABLE hive_style (
    order_id INT,
    amount DOUBLE
) PARTITIONED BY (dt STRING, region STRING);  -- Fully compatible

-- But note ADD COLUMN position issues
-- Hive: New column added to the last position before partition columns
-- Lakehouse: Recommend explicitly specifying column position
ALTER TABLE hive_style ADD COLUMN new_col STRING AFTER amount;  -- Explicit position
```

#### Dynamic Partition Configuration Differences

```sql
-- Configurations needed in Hive are not needed in Lakehouse
-- set hive.exec.dynamic.partition=true;           -- Not needed in Lakehouse
-- set hive.exec.dynamic.partition.mode=nonstrict; -- Not needed in Lakehouse

-- But pay attention to partition count management
-- Hive: hive.exec.max.dynamic.partitions=1000 (adjustable)
-- Lakehouse: Recommend controlling single-operation partition count within reasonable range
```

#### Additional Real Pain Points for Hive Users

```sql
-- Additional issues commonly encountered by Hive users:
-- 1. Partition field type restrictions
CREATE TABLE hive_table PARTITIONED BY (dt STRING); -- Hive partition fields typically must be STRING

-- 2. Partition directory structure dependency
-- Hive strictly depends on directory structures like /data/table/year=2024/month=06/day=01/
-- No such restriction in Lakehouse, more flexible

-- 3. Frequent need for partition repair
-- Hive: MSCK REPAIR TABLE table_name;  -- Often needs manual repair
-- Lakehouse: Auto-maintains metadata, no manual repair needed
```

### Spark Users: Special Attention Required

#### DataFrame Write Method Differences

```sql
-- Common Spark DataFrame write approach
-- df.write.mode("overwrite").partitionBy("date", "region").saveAsTable("table")

-- Things to note when migrating to Lakehouse SQL
-- 1. Ensure the table is already created and correctly partitioned
CREATE TABLE spark_migrated PARTITIONED BY (date STRING, region STRING);

-- 2. Use INSERT statements instead of saveAsTable
INSERT OVERWRITE spark_migrated SELECT * FROM source_data;
```

#### Transform Function Name Mapping

| Spark Function          | Lakehouse Function   | Notes     |
| ---------------- | ------------- | ------ |
| `year(col)`      | `years(col)`  | Note plural form |
| `month(col)`     | `months(col)` | Note plural form |
| `dayofyear(col)` | `days(col)`   | Different function name  |
| `hour(col)`      | `hours(col)`  | Note plural form |

#### Additional Challenges for Spark Users

```scala
// Issues more commonly encountered by Spark users:
// 1. Partition discovery issues
spark.sql("MSCK REPAIR TABLE table_name")  // Spark also has this issue

// 2. Performance pitfalls of dynamic partition writes
df.write.mode("append")
  .option("maxRecordsPerFile", "50000")  // Control file size
  .partitionBy("date")
  .saveAsTable("table")

// 3. Partition column auto-inference type issues
df.write.partitionBy($"date".cast("string"))  // Must cast to string
```

### MaxCompute Users: Special Attention Required

#### Partition Usage Habit Adjustments

```sql
-- MaxCompute enforces partition conditions
-- SELECT * FROM table WHERE pt='20240601';  -- Must include partition condition, otherwise error

-- In Lakehouse, partition conditions are automatic
SELECT * FROM table WHERE order_date='2024-06-01';  -- Automatic partition pruning, more flexible

-- However, it is still recommended to include partition conditions in queries for optimal performance
```

#### Lifecycle Management Differences

```sql
-- MaxCompute's automatic lifecycle
-- ALTER TABLE table SET LIFECYCLE 30;  -- Auto-delete after 30 days

-- In Lakehouse, manual management or scheduling is needed
TRUNCATE TABLE table PARTITION (order_date = '2024-05-01');  -- Manual cleanup
```

#### Real Pain Points for MaxCompute Users

```sql
-- Issues most commonly encountered by MaxCompute users:
-- 1. Forced partition filter habit
-- MaxCompute: Queries without partition conditions will error directly
-- Lakehouse: Allows full table scan, but recommend including partition conditions

-- 2. INSERT OVERWRITE syntax differences for partitioned tables
-- MaxCompute: INSERT OVERWRITE TABLE target PARTITION(dt='20240601')
-- Lakehouse: INSERT OVERWRITE target ... (automatically identifies partitions)

-- 3. Cross-project access syntax changes
-- MaxCompute: SELECT * FROM project.table WHERE pt='20240601';
-- Lakehouse: SELECT * FROM catalog.schema.table WHERE pt='20240601';
```

### Snowflake Users: Special Attention Required

#### Major Mindset Shift: From Automatic Optimization to Proactive Partition Design

**Traditional Snowflake User Habits**: You may not be highly concerned with underlying partition design

```sql
-- Typical usage pattern in traditional Snowflake
CREATE TABLE orders (id INT, amount DOUBLE, order_date DATE);  -- System auto-manages storage
ALTER TABLE orders CLUSTER BY (order_date);  -- Set clustering key, system auto-manages micro-partitions

-- No need to consider partitions in queries
SELECT * FROM orders WHERE amount > 1000;
```

**Modern Snowflake Users (Iceberg Tables)**: Syntax is largely similar but with subtle differences

```sql
-- Snowflake Iceberg table
CREATE ICEBERG TABLE orders_iceberg PARTITION BY (year(order_date));

-- Corresponding syntax in Lakehouse
CREATE TABLE orders_lakehouse PARTITIONED BY (years(order_date));  -- Note plural form
```

**Adjustments When Migrating to Lakehouse**:

```sql
-- Traditional Snowflake thinking may be suboptimal in Lakehouse
CREATE TABLE orders (id INT, amount DOUBLE, order_date DATE);  -- Created a regular table, not a partitioned table
-- Result: Query performance may be less than ideal

-- Learn to proactively design partition strategies
CREATE TABLE orders (
    id INT, 
    amount DOUBLE,
    order_date DATE
) PARTITIONED BY (days(order_date));  -- Proactive partition design

-- Although pruning is automatic, partition design directly affects performance
SELECT * FROM orders 
WHERE order_date >= '2024-06-01'  -- Partition condition (recommended to include)
  AND amount > 1000;              -- Business condition
```

#### Snowflake Users' Learning Path

```sql
-- Phase 1: Understand the value of partitioning
-- Partition = Physically storing data separately by a field
-- Purpose: Only scan relevant partitions during queries, not the entire table

-- Phase 2: Learn partition design
-- Ask yourself: What field do my queries most commonly filter on?
-- Time fields: order_date, created_at, updated_at
-- Business fields: region, department, customer_type

-- Phase 3: Verify partition effectiveness
-- Compare query performance of partitioned vs non-partitioned tables
```

#### Cognitive Focus Points for Snowflake Users

```sql
-- Key understanding points for Snowflake users:
-- 1. Not all databases auto-optimize
SELECT * FROM large_table WHERE complex_condition;  -- Need to consider partition design

-- 2. Importance of partition design
-- Snowflake micro-partitions are automatic, but in Lakehouse proactive design is needed

-- 3. File system optimization concepts
-- Understand concepts like "small file problem", "partition count control"

-- 4. Query optimization awareness
SELECT * FROM large_partitioned_table 
WHERE order_date >= '2024-06-01';  -- Habit of including partition conditions in queries
```

### Databricks Users: Special Attention Required

#### Delta Lake vs Iceberg Differences

```sql
-- Delta Lake partition syntax
-- CREATE TABLE delta_table PARTITIONED BY (year, month);

-- Equivalent syntax in Lakehouse (Iceberg)
CREATE TABLE iceberg_table PARTITIONED BY (years(date_col));  -- Can only use single time granularity

-- Cannot simultaneously use multiple time granularities like in Delta Lake
```

#### Optimization Command Differences

```sql
-- Delta Lake optimization commands
-- OPTIMIZE table_name;
-- OPTIMIZE table_name ZORDER BY (col1, col2);

-- Similar effect achieved in Lakehouse through rewrite
INSERT OVERWRITE table_name SELECT * FROM table_name;  -- File merge optimization
```

#### Advanced Feature Migration for Databricks Users

```sql
-- Issues more commonly encountered by Databricks users:
-- 1. Delta Lake time travel habits
-- Delta: SELECT * FROM table TIMESTAMP AS OF '2024-01-01 00:00:00';
-- Lakehouse: SELECT * FROM table TIMESTAMP AS OF '2024-01-01 00:00:00';  -- Similar syntax

-- 2. Heavy reliance on OPTIMIZE and Z-ORDER
-- Delta: OPTIMIZE table ZORDER BY (col1, col2);  -- This is a daily operation
-- Lakehouse: Need to combine partition + sort + bucket for equivalent effect

-- 3. Unity Catalog impact
-- Delta: CREATE TABLE catalog.schema.table;  -- Three-level namespace habit
-- Lakehouse: CREATE TABLE schema.table;  -- Two-level namespace
```

***

## Practical Pitfall Avoidance Guide

### Partition Creation Pitfalls

#### Do's and Don'ts Comparison

```sql
-- Wrong approach: Unclear partition design
CREATE TABLE bad_partition (
    id INT,
    data STRING,
    timestamp_col TIMESTAMP_LTZ
);  -- No PARTITIONED BY, not a partitioned table

INSERT INTO bad_partition VALUES (1, 'test', CURRENT_TIMESTAMP());
-- Later finding queries are slow and wanting to add partitions is too late

-- Correct approach: Plan partition strategy in advance
CREATE TABLE good_partition (
    id INT,
    data STRING,
    timestamp_col TIMESTAMP_LTZ
) PARTITIONED BY (days(timestamp_col));

-- Immediately verify partition was created correctly
SHOW PARTITIONS good_partition;  -- Should execute normally without errors
```

#### Partition Field Type Selection

```sql
-- Easy pitfall in type selection
CREATE TABLE date_type_trap (
    id INT,
    order_date DATE  -- DATE type
) PARTITIONED BY (order_date);

-- May get type errors when inserting data
INSERT INTO date_type_trap VALUES (1, '2024-06-01');  -- String vs DATE type

-- Recommended approach: Use STRING type for partitioning
CREATE TABLE string_partition (
    id INT,
    order_date_str STRING  -- Use STRING type to avoid type conversion issues
) PARTITIONED BY (order_date_str);

-- Or use transform partitions
CREATE TABLE transform_partition (
    id INT,
    order_date DATE
) PARTITIONED BY (days(order_date));  -- Let the system handle type conversion
```

### Data Write Pitfalls

#### Large Batch Write Strategy

```sql
-- For large batch writes, recommend processing in batches to avoid too many partitions at once
INSERT INTO target_table 
SELECT * FROM source_table 
WHERE partition_col >= 'start_value' 
  AND partition_col <= 'end_value';
```

#### Partition Data Consistency

```sql
-- Note: Timezone issues with transform partitions
CREATE TABLE timezone_sensitive (
    id INT,
    event_time TIMESTAMP_LTZ  -- Timezone-aware timestamp
) PARTITIONED BY (days(event_time));

-- Same local time in different timezones may land in different partitions
INSERT INTO timezone_sensitive VALUES 
(1, TIMESTAMP '2024-06-01 23:30:00 UTC'),      -- UTC timezone
(2, TIMESTAMP '2024-06-01 23:30:00');          -- System default timezone

-- View partition distribution
SHOW PARTITIONS timezone_sensitive;
-- May see two different partition values: days(event_time)=19875 and days(event_time)=19876
```

### Query Performance Pitfalls

#### Scenarios Where Partition Pruning Fails

```sql
-- Query that cannot leverage partition pruning
SELECT * FROM partitioned_table 
WHERE YEAR(order_date) = 2024;  -- Function wrapping partition field

SELECT * FROM partitioned_table 
WHERE order_date LIKE '2024%';  -- Fuzzy matching

-- Queries that effectively leverage partition pruning
SELECT * FROM partitioned_table 
WHERE order_date >= '2024-06-01' 
  AND order_date <= '2024-06-30';  -- Range query on partition field
```

### Quick Partition Troubleshooting

#### Problem: Partition table performs worse than non-partitioned table

**Investigation Commands**:

```sql
-- 1. Check partition count and size distribution
SHOW PARTITIONS EXTENDED your_table;

-- 2. Check for excessive small partitions
SHOW PARTITIONS EXTENDED your_table WHERE bytes < 10*1024*1024;

-- 3. Check if queries are utilizing partition pruning
EXPLAIN SELECT * FROM your_table WHERE partition_col = 'value';
```

**Common Causes and Solutions**:

* **Over-partitioning (too many small partitions)** -> Redesign partition granularity
* **Query doesn't include partition field** -> Optimize query WHERE conditions
* **Not actually a partitioned table** -> Rebuild with native SQL

***

## Partition Performance Verification Practical Guide

### Standard Method for Partition Effectiveness Verification

#### 1. Create Comparison Test

```sql
-- Create partitioned and non-partitioned tables with the same data
CREATE TABLE sales_partitioned (
    id INT, amount DOUBLE, sale_date DATE
) PARTITIONED BY (days(sale_date));

CREATE TABLE sales_normal (
    id INT, amount DOUBLE, sale_date DATE
);

-- Insert the same large data volume for performance comparison testing
```

#### 2. Performance Benchmark Test

```sql
-- Test partition query vs full table scan
SELECT COUNT(*) FROM sales_partitioned 
WHERE sale_date >= '2024-06-01' AND sale_date <= '2024-06-30';

SELECT COUNT(*) FROM sales_normal 
WHERE sale_date >= '2024-06-01' AND sale_date <= '2024-06-30';
```

#### 3. Partition Health Check

```sql
-- Check partition size distribution
SHOW PARTITIONS EXTENDED table_name;

-- Ideal state:
-- Each partition 128MB - 1GB
-- Partition sizes relatively uniform
-- No large number of partitions smaller than 10MB
-- No single partition exceeding 5GB
```

### Performance Issue Diagnosis

#### Partition Table Slower Than Non-Partitioned Table?

**Possible Causes and Solutions**:

1. **Over-partitioning**: Partition is too granular, metadata overhead is high
   ```sql
   -- Problem: Hourly partitions lead to many small partitions
   PARTITIONED BY (hours(timestamp))

   -- Solution: Change to day-level partitions
   PARTITIONED BY (days(timestamp))
   ```

2. **Query not utilizing partitions**: WHERE condition doesn't include partition field
   ```sql
   -- Cannot leverage partitions
   SELECT * FROM partitioned_table WHERE amount > 1000;

   -- Utilize partitions
   SELECT * FROM partitioned_table 
   WHERE sale_date >= '2024-06-01' AND amount > 1000;
   ```

3. **Wrong partition field selection**: Partition field is not the query hotspot
   ```sql
   -- Problem analysis: Check query patterns
   -- If queries mainly filter by user_id but partition is by date, it's ineffective

   -- Solution: Redesign partition strategy
   PARTITIONED BY (bucket(100, user_id))  -- Partition by user hash instead
   ```

### Partition Tuning in Practice

#### 1. Partition Granularity Selection

| Data Volume     | Recommended Granularity |
| --------------- | ----------------------- |
| > 1 billion rows | Day-level partitions days() |
| 100M - 1B rows   | Month-level partitions months() |
| < 10M rows       | Month-level partitions months() |

#### 2. Composite Partition Optimization

```sql
-- Original composite partition problem
CREATE TABLE sales_old PARTITIONED BY (region, sale_date, channel);
-- Problem: 10 regions x 365 days x 3 channels = 10,950 partitions

-- Optimization 1: Primary-secondary partitioning
CREATE TABLE sales_optimized (
    ..., region STRING, channel STRING
) PARTITIONED BY (days(sale_date));  -- Primary partition: time
CREATE BLOOMFILTER INDEX idx_region ON TABLE sales_optimized(region);
CREATE BLOOMFILTER INDEX idx_channel ON TABLE sales_optimized(channel);

-- Optimization 2: Hash compression
CREATE TABLE sales_hash PARTITIONED BY (
    days(sale_date),           -- Time partition: 365
    bucket(5, region)          -- Region hashed to 5 buckets
);
-- Result: 365 x 5 = 1,825 partitions (manageable)
```

#### 3. Partition Evolution Strategy

```sql
-- Periodic partition health check
WITH partition_health AS (
    SELECT 
        partitions,
        total_rows,
        bytes,
        CASE 
            WHEN CAST(bytes AS BIGINT) < 10*1024*1024 THEN 'TOO_SMALL'
            WHEN CAST(bytes AS BIGINT) > 5*1024*1024*1024 THEN 'TOO_LARGE'
            ELSE 'HEALTHY'
        END AS health_status
    FROM (SHOW PARTITIONS EXTENDED target_table)
)
SELECT health_status, COUNT(*) as count
FROM partition_health
GROUP BY health_status;
```

## Migration Case Studies

### Case 1: Real-Time Data Table Migration (Complex Partition -> Simplified Partition)

#### Original Complex Partition Table

```sql
-- Original table: Multi-level time + business dimension composite partitions
CREATE TABLE events_old PARTITIONED BY (year, month, day, hour, event_type);
-- Problem: Too many partitions, complex queries, high maintenance cost
```

#### Lakehouse Migration Strategy

```sql
-- Redesign: Single time granularity partition + index
CREATE TABLE events_new (
    event_id INT,
    event_type STRING,
    event_data JSON,
    event_time TIMESTAMP_LTZ
) PARTITIONED BY (days(event_time))
  SORTED BY (event_type);

-- Query becomes cleaner
SELECT * FROM events_new 
WHERE event_time >= '2024-06-01 08:00:00' 
  AND event_time <= '2024-06-01 17:59:59';

-- Performance improvement:
-- Query speed: 40% improvement (avoids small partition scanning)
-- Maintenance cost: 60% reduction (partition count significantly reduced)
-- Query complexity: 80% reduction (no need to calculate year, month, day, hour)
```

### Case 2: Log Analysis Table Migration (MaxCompute -> Singdata Lakehouse)

#### Original MaxCompute Table

```sql
-- Original MaxCompute table: Strict partition restrictions
CREATE TABLE app_logs (
    user_id STRING,
    event_type STRING,
    event_data STRING
) PARTITIONED BY (
    pt STRING,          -- Format: 20240601  
    region STRING,      -- Region: beijing, shanghai
    app_version STRING  -- Version: 1.0, 1.1, 1.2
);

-- MaxCompute characteristics:
-- Enforced partition conditions: SELECT must include WHERE pt='20240601'
-- Partition count explosion: 365 x 10 x 20 = 73,000/year
-- Data skew: Beijing region has much more data, other regions very little
```

#### Singdata Lakehouse Migration Strategy

```sql
-- Step 1: Analyze original query patterns
-- Discovery: 90% of queries filter by time range + region
-- Decision: Time as primary partition, region with index

-- Step 2: Redesign partition architecture
CREATE TABLE app_logs_new (
    user_id STRING,
    event_type STRING,
    event_data STRING,
    region STRING,        -- No partition, use index
    app_version STRING,   -- No partition, use index
    log_date DATE
) PARTITIONED BY (days(log_date));  -- Only partition by time

-- Step 3: Create indexes to optimize non-partition queries
CREATE BLOOMFILTER INDEX idx_region ON TABLE app_logs_new(region);
CREATE BLOOMFILTER INDEX idx_version ON TABLE app_logs_new(app_version);

-- Step 4: Verify query performance
-- Original query:
SELECT * FROM app_logs WHERE pt='20240601' AND region='beijing';

-- New query:
SELECT * FROM app_logs_new 
WHERE log_date='2024-06-01' AND region='beijing';
-- Result: Comparable performance, but partition count reduced from 73,000 to 365
```

#### Migration Process Challenges

```sql
-- Challenge 1: Inconsistent data types
-- MaxCompute: pt STRING '20240601'
-- Singdata Lakehouse: log_date DATE '2024-06-01'

-- Solution: ETL conversion script
INSERT INTO app_logs_new 
SELECT 
    user_id,
    event_type, 
    event_data,
    region,
    app_version,
    DATE(CONCAT(
        SUBSTR(pt, 1, 4), '-',
        SUBSTR(pt, 5, 2), '-', 
        SUBSTR(pt, 7, 2)
    )) as log_date
FROM maxcompute_source;

-- Challenge 2: Habitual syntax adjustments needed
-- MaxCompute habit: WHERE pt='20240601' (string exact match)
-- Singdata Lakehouse: WHERE log_date='2024-06-01' (auto partition pruning)

-- Challenge 3: Max partition query method changes
-- MaxCompute original: WHERE pt = max_pt()
-- Singdata Lakehouse new method: WHERE log_date = (SELECT DATE(max_pt('app_logs_new')))
-- Or redesign as STRING partition, using directly: WHERE pt = max_pt('app_logs_new')
```

#### Partition Maintenance Automation

```sql
-- MaxCompute-style automation script (adapted for new platform)
-- 1. Daily cleanup of partitions older than 30 days
TRUNCATE TABLE app_logs_new 
PARTITION (log_date < current_date() - INTERVAL '30' DAY);

-- 2. Smart cleanup: Keep latest partitions, clean small partitions
WITH old_partitions AS (
    SELECT partitions
    FROM (SHOW PARTITIONS EXTENDED app_logs_new)
    WHERE CAST(bytes AS BIGINT) < 1000000  -- Partitions smaller than 1MB
      AND partitions < max_pt('app_logs_new') - INTERVAL '7' DAY
)
-- Clean small partitions one by one (note: need specific partition values)

-- 3. Partition health check script
WITH partition_stats AS (
    SELECT 
        partitions,
        CAST(total_rows AS BIGINT) as rows,
        CAST(bytes AS BIGINT) as size_bytes
    FROM (SHOW PARTITIONS EXTENDED app_logs_new)
)
SELECT 
    COUNT(*) as total_partitions,
    AVG(size_bytes)/1024/1024 as avg_size_mb,
    SUM(CASE WHEN size_bytes < 10*1024*1024 THEN 1 ELSE 0 END) as small_partitions,
    max_pt('app_logs_new') as latest_partition
FROM partition_stats;
```

### Case 3: Real-Time Data Table Migration (Spark -> Singdata Lakehouse)

#### Original Spark Delta Table

```sql
-- Original Spark table: Hourly partitions + Z-Order optimization
CREATE TABLE user_events USING DELTA
PARTITIONED BY (date_hour STRING)  -- Format: 2024060109
OPTIONS (
  'path' '/data/user_events'
);

-- Periodic optimization
OPTIMIZE user_events ZORDER BY (user_id, event_type);
```

#### Singdata Lakehouse Migration Challenges

```sql
-- Challenge 1: No direct Z-Order equivalent
-- Challenge 2: Hourly partitions may be too granular
-- Challenge 3: High real-time write performance requirements

-- Solution 1: Partition + Bucket combination (recommended)
CREATE TABLE user_events_new (
    user_id INT,
    event_type STRING,
    event_data JSON,
    event_time TIMESTAMP_LTZ
) PARTITIONED BY (hours(event_time))      -- Keep hourly partitions (real-time requirement)
  CLUSTERED BY (user_id) INTO 32 BUCKETS; -- User ID bucketing

-- Solution 2: Partition + Sort combination
CREATE TABLE user_events_sorted (
    user_id INT,
    event_type STRING,
    event_data JSON,
    event_time TIMESTAMP_LTZ
) PARTITIONED BY (hours(event_time))      -- Keep hourly partitions
  SORTED BY (event_type);                 -- Event type sort

-- Achieving similar Z-Order effect:
-- 1. Partition: Physical isolation by time
-- 2. Bucket: Hash distribution by user ID  
-- 3. Sort: Clustered storage by event type
```

#### Performance Tuning Process

```sql
-- Tuning 1: Monitor partition sizes
WITH partition_analysis AS (
    SELECT 
        partitions,
        CAST(bytes AS BIGINT)/1024/1024 as size_mb,
        CAST(total_rows AS BIGINT) as row_count
    FROM (SHOW PARTITIONS EXTENDED user_events_new)
)
SELECT * FROM partition_analysis 
ORDER BY size_mb DESC LIMIT 10;

-- Discovery: Night-time partitions too small (< 10MB)
-- Solution: Dynamically adjust partition strategy

-- Tuning 2: Hourly partitions during day, merged at night
-- Implement smart partition strategy through ETL:
-- 8:00-22:00 peak hours: Hourly partitions
-- 22:00-8:00 off-peak: Merge to daily partitions
```

### Case 4: Data Warehouse Migration (Snowflake -> Singdata Lakehouse)

#### Special Challenges for Snowflake Users

```sql
-- Traditional Snowflake: Automatic storage management
CREATE TABLE sales (
    order_id INT,
    customer_id INT,
    amount DECIMAL(10,2),
    order_date DATE
);

-- Set clustering key (relatively transparent to user)
ALTER TABLE sales CLUSTER BY (order_date);

-- Queries: No need to worry about physical storage
SELECT * FROM sales WHERE amount > 1000;
```

#### Singdata Lakehouse Learning Path

```sql
-- Phase 1: Understand partition concepts
-- Question: What is partitioning? Why is it needed?
-- Answer: Partitioning physically stores data separately by a field, scanning only relevant partitions during queries

-- Phase 2: Learn partition design
-- Question: Which field should I partition by?
-- Analysis: Check the most commonly used WHERE conditions
SELECT 
    COUNT(*) as query_count,
    'order_date filter' as filter_type
FROM query_log 
WHERE query_text LIKE '%WHERE%order_date%'
UNION ALL
SELECT 
    COUNT(*),
    'customer_id filter' 
FROM query_log 
WHERE query_text LIKE '%WHERE%customer_id%';

-- Result: order_date filtering accounts for 80%, customer_id for 20%
-- Decision: Partition by order_date, use index for customer_id

-- Phase 3: Correct partition table design
CREATE TABLE sales_partitioned (
    order_id INT,
    customer_id INT,
    amount DECIMAL(10,2),
    order_date DATE
) PARTITIONED BY (days(order_date));

CREATE BLOOMFILTER INDEX idx_customer ON TABLE sales_partitioned(customer_id);

-- Phase 4: Verify performance improvement
-- Comparative queries:
SELECT * FROM sales WHERE order_date = '2024-06-01';           -- Full table scan
SELECT * FROM sales_partitioned WHERE order_date = '2024-06-01'; -- Partition scan

-- Result: Partitioned tables typically show significant performance improvement
```

#### Common Adjustments and Real Confusions for Snowflake Users

```sql
-- Adjustment 1: Create partitioned tables instead of regular tables
CREATE TABLE sales_correct (
    order_id INT,
    amount DECIMAL(10,2),
    order_date DATE
) PARTITIONED BY (days(order_date));  -- This is a partitioned table

-- Adjustment 2: Include partition conditions in queries
SELECT * FROM sales_partitioned 
WHERE order_date >= '2024-06-01'  -- Leverage partition
  AND amount > 1000;              -- Business filter

-- Adjustment 3: Understand the importance of partition fields
SELECT * FROM sales_partitioned WHERE amount > 1000;  -- Can be optimized to include partition conditions

-- Adjustment 4: Not all queries will automatically be fast
-- Snowflake users are accustomed to the system handling all storage optimization automatically
-- Lakehouse requires more proactive design awareness
```

#### The Actual Process of Mindset Shift

```
### Common Questions from Snowflake Users:
"Why are my queries fast on Snowflake but need partition consideration on Lakehouse?"

**Answer**: Snowflake's automatic optimization vs Lakehouse's proactive partition design each have their advantages

### Typical Issues During the Learning Process:
1. "Why should I decide the partition strategy?"
2. "What is the small file problem? I never considered file sizes before"
3. "What does partition count control mean?"

### Breakthrough Moment:
When users see significant performance advantages of partitioned tables over non-partitioned ones, they begin to understand the value of partitioning
```

***

## Migration Verification Checklist

### Partition Creation Verification

```sql
-- Checkpoint 1: Table is indeed a partitioned table
SHOW PARTITIONS your_table_name;
-- Should execute normally, not reporting "not a partitioned table" error

-- Checkpoint 2: Partition field types are correct
DESCRIBE TABLE your_table_name;
-- Confirm partition field data types match expectations

-- Checkpoint 3: Test data write
INSERT INTO your_table_name VALUES (test_data);
SHOW PARTITIONS your_table_name;
-- Should see newly created partitions

-- Checkpoint 4: Verify partition value format
-- Transform partitions generate numeric values, e.g. days('2024-06-01') = 19875
-- years('2024-06-01') = 54 (year count from 1970)
-- Confirm partition values meet expectations

-- Checkpoint 5: Test max partition retrieval (compatibility verification)
SELECT max_pt('your_table_name');
-- Should return the maximum partition value for compatibility with similar original platform features
```

### Performance Verification

```sql
-- Checkpoint 6: Partition pruning is effective
-- Compare execution time of these two queries
SELECT COUNT(*) FROM your_table_name;  -- Full table scan
SELECT COUNT(*) FROM your_table_name WHERE partition_col = 'specific_value';  -- Partition query

-- Partition query should be noticeably faster

-- Checkpoint 7: Partition sizes are reasonable
SHOW PARTITIONS EXTENDED your_table_name;
-- Check each partition's size, ideal range: 128MB - 1GB
```

### Compatibility Verification

```sql
-- Checkpoint 8: Whether original queries need modification
-- Test original platform queries in Lakehouse
-- Pay special attention to:
-- 1. Whether transform function names need adjustment (year -> years)
-- 2. Whether partition conditions can be automatically recognized
-- 3. Whether data type conversions work correctly

-- Checkpoint 9: Whether partition evolution strategies are feasible
-- Verify partition cleanup and maintenance scripts work correctly
```

### Common Error Self-Check

If you encounter the following errors, resolve them accordingly:

| Error Message                                 | Possible Cause                       | Solution               |
| ------------------------------------ | -------------------------- | ------------------ |
| `not a partitioned table`            | Missing PARTITIONED BY or syntax error during table creation   | Re-create table with native SQL, adding partition definition |
| `implicit cast not allowed`          | Partition field type mismatch                  | Check inserted data types           |
| `exceeds maximum number`             | Too many partitions in a single operation                   | Adjust parameters or process in batches          |
| `conflicts with`                     | Transform partition logic conflict                   | Choose single time granularity           |
| `months conflicts with years`        | Multi-level time partition design error                 | Switch to `days()` single granularity     |
| `Syntax error at or near 'ORDER'`    | SHOW PARTITIONS used with ORDER BY | Use WITH subquery for sorting       |
| `cannot resolve column 'total_rows'` | Partition attributes used in TRUNCATE PARTITION | Only partition field itself can be used         |
| `operator not found`                 | Type mismatch comparison                   | Ensure data types are consistent           |
| `duplicate.syntax.element`           | CLUSTERED BY and SORTED BY used together | Choose one of the two syntaxes           |
| Query performance worse than original platform                            | Partition design may be unreasonable                   | Re-evaluate partition strategy           |
| Too many small partitions                               | Too many composite partition dimensions                   | Reduce partition dimensions, use indexes instead       |
| `max_pt function not found`          | Possible table name error or permission issue               | Check table name and schema permissions      |
| `TRUNCATE PARTITION failed`          | Partition condition syntax error                   | Check partition filter expression syntax        |

### Performance Benchmark Acceptance Criteria

#### Basic Migration Success Indicators

* Original query logic can run in Lakehouse without major modifications
* Query performance meets or exceeds original platform levels
* Partition maintenance workload is manageable and automated
* Team members can independently handle common partition issues

#### Complex Migration Success Indicators

* New partition strategy is simpler than original but performance is not degraded
* Partition count is within reasonable range
* Partition sizes are evenly distributed (128MB-1GB/partition)
* Query patterns and partition design are highly aligned
* Partition maintenance automation is no lower than original platform

***

## Summary: Key Elements for Successful Migration

### Core Mindset Shifts

1. **From Explicit Partitioning to Hidden Partitioning**: No need to manually specify partition conditions in every query
2. **From Automatic Optimization to Proactive Design**: Partition strategies need advance planning and design
3. **From Single Syntax to Diverse Choices**: Multiple partition creation methods supported, choose the most suitable
4. **From Less Concern to Partition Awareness**: Especially for Snowflake users, need to strengthen partition design awareness
5. **From Complex Partitioning to Simplified Design**: Multi-level partitions need redesign to single granularity partitions

### Pitfall Avoidance Summary

#### Basic Syntax Traps

1. **Remember plural forms for transform function names**: `years`, `months`, `days`, `hours`
2. **Keep partition types consistent**: Avoid mixing STRING and DATE types
3. **Control partition count within reasonable range**: Avoid too many small partitions
4. **Design partitions based on query patterns**: Design partition fields based on WHERE conditions
5. **Verify partition effectiveness promptly**: Check partition correctness immediately after creation

#### Complex Migration Traps

6. **Multi-level time partitions cannot be directly migrated**: `year+month+day` should change to `days()` single granularity
7. **Simplify composite partition dimensions**: Too many dimensions lead to excessive partition count
8. **Rebuild partition evolution strategies**: From automatic management to manual scheduled management
9. **Adjust performance optimization strategies**: Z-Order and other advanced optimizations need redesign
10. **Supplement lifecycle management**: From automatic cleanup to script-based periodic cleanup

#### Creation Verification Traps

11. **Recommend using native SQL to create partition tables**: Ensure syntax accuracy
12. **Must verify after every creation**: Execute the complete verification checklist
13. **Performance testing must compare baselines**: Ensure partitioned tables are indeed faster than non-partitioned ones
14. **Monitor partition health status**: Regularly check partition sizes and count distribution

#### Advanced Syntax Traps

15. **SHOW PARTITIONS does not support ORDER BY**: Use WITH subquery for sorting
16. **bucket function parameters must be reasonable**: Recommended positive integers in range 1-1000
17. **Note NULL values and special characters**: The system will create corresponding partitions

### Successful Migration Experience

#### For Simple Partition Scenarios

* **Incremental migration**: Verify with small tables first, then migrate core large tables
* **Preserve original query logic**: Try to let original SQL work without major changes
* **Performance baseline comparison**: Compare query performance before and after migration
* **Complete verification process**: Strictly follow the verification checklist

#### For Complex Partition Scenarios

* **Partition strategy redesign**: Don't try to completely replicate the original partition structure
* **Performance verification first**: Use representative queries to verify new partition strategy effectiveness
* **Phased implementation**: Complex migration divided into four phases: analysis, redesign, testing, and cutover
* **Prepare rollback plan**: Ensure quick rollback to original solution if migration fails

### Special Reminders

**For Snowflake and similar platform users**:
The challenge of migrating to Lakehouse mainly lies in mindset adjustment. You need to shift from "less concern about partitioning" to "proactive partition strategy design." It is recommended to first experience the impact of partitioning on query performance in a test environment, understand the value of partitioning, and then design production environment partition strategies.

**For users with complex partition architectures**:
Don't try to completely replicate the original partition structure in the Lakehouse. The Lakehouse partition philosophy is "simplify without losing performance." Multi-level partitions, composite partitions, and other complex designs can often achieve the same or better results with simpler solutions in the Lakehouse.

**For all migrating users**:
Partition table creation verification is the first and most critical step in successful migration. It is recommended to use native SQL to create partition tables and strictly execute the verification checklist. Many migration issues stem from partition tables not being correctly created, making subsequent performance optimization impossible.

Remember: **Lakehouse partitioning is not a burden, but a powerful tool for performance optimization**. When partitioning is used correctly, you will achieve better query performance and more flexible data management capabilities than on your original platform.

***

## Quick Reference Card

### Common Partition Management Commands

| Function       | Command Syntax                                                                  | Use Case        |
| -------- | --------------------------------------------------------------------- | ----------- |
| **View Partitions** | `SHOW PARTITIONS table_name`                                          | Basic partition viewing      |
| **Partition Details** | `SHOW PARTITIONS EXTENDED table_name`                                 | View partition size, file count, etc. |
| **Partition Filter** | `SHOW PARTITIONS EXTENDED table WHERE bytes > 100*1024*1024`          | Health check        |
| **Specific Partition** | `SHOW PARTITIONS table PARTITION (pt1 = '2023')`                      | View specific partition      |
| **Limit Results** | `SHOW PARTITIONS table LIMIT 10`                                      | Limit returned results      |
| **Max Partition** | `SELECT max_pt('table_name')`                                         | Get latest partition value     |
| **Clean Partition** | `TRUNCATE TABLE table PARTITION (pt = 'value')`                       | Lifecycle management      |
| **Batch Clean** | `TRUNCATE TABLE table PARTITION (pt1 = 'v1'), PARTITION (pt2 = 'v2')` | Composite condition cleanup      |

### Platform Syntax Quick Reference

| Function       | Original Platform Syntax                        | Lakehouse Syntax                | Notes                    |
| -------- | ---------------------------- | -------------------------- | ----------------------- |
| **Year Partition**  | `year(date)`                 | `years(date)`              | Plural form, returns year count from 1970      |
| **Month Partition**  | `month(date)`                | `months(date)`             | Plural form                    |
| **Day Partition**  | `day(date)`                  | `days(date)`               | Plural form, returns day count from 1970-01-01 |
| **Hour Partition** | `hour(timestamp)`            | `hours(timestamp)`         | Plural form                    |
| **Composite Partition** | `(year, month)`              | `days(date)`               | Cannot combine conflicting transforms               |
| **Dynamic Partition** | Requires enable configuration                        | Default support                       | Pay attention to partition count control                |
| **Max Partition** | `max_pt()`                   | `max_pt('table_name')`     | Must specify table name                  |
| **Partition Cleanup** | `ALTER TABLE DROP PARTITION` | `TRUNCATE TABLE PARTITION` | More flexible syntax                   |

### Quick Error Reference

| When You See This Error                               | Immediately Check                     | Quick Fix               |
| ------------------------------------ | -------------------------- | ------------------ |
| `not a partitioned table`            | Whether table creation statement has `PARTITIONED BY`    | Rebuild table with native SQL          |
| `implicit cast not allowed`          | Whether data types match                   | Use STRING partition uniformly or use transform partition |
| `exceeds maximum number`             | Whether partition count is too high                   | Insert in batches or adjust parameters           |
| `conflicts with`                     | Whether transform partitions conflict                   | Use single time granularity           |
| `months conflicts with years`        | Multi-level time partition design error                 | Switch to `days()` single granularity     |
| `Syntax error at or near 'ORDER'`    | SHOW PARTITIONS used with ORDER BY | Use WITH subquery for sorting       |
| `cannot resolve column 'total_rows'` | Partition attributes used in TRUNCATE PARTITION | Only partition field itself can be used         |
| `operator not found`                 | Type mismatch comparison                   | Ensure data types are consistent           |
| `duplicate.syntax.element`           | CLUSTERED BY and SORTED BY used together | Choose one of the two syntaxes           |
| Query performance worse than original platform                            | Whether partition design is reasonable                   | Re-evaluate partition strategy           |
| Too many small partitions                               | Too many composite partition dimensions                   | Reduce partition dimensions, use indexes instead       |
| `max_pt function not found`          | Possible table name error or permission issue               | Check table name and schema permissions      |
| `TRUNCATE PARTITION failed`          | Partition condition syntax error                   | Check partition filter expression syntax        |

### Partition Table Verification Quick Reference

| Verification Item      | Check Command                                  | Expected Result       |
| --------- | ------------------------------------- | ---------- |
| **Is Partitioned Table** | `SHOW PARTITIONS table_name`          | No error, shows partition list |
| **Partition Created**  | View partitions again after inserting data                           | Shows new partition values     |
| **Type Match**  | `DESCRIBE TABLE table_name`           | Column types match expectations    |
| **Performance Improvement**  | Compare partition query vs full table scan                          | Partition query noticeably faster   |
| **Latest Partition**  | `SELECT max_pt('table_name')`         | Returns max partition value    |
| **Partition Health**  | `SHOW PARTITIONS EXTENDED table_name` | Partition sizes reasonably distributed   |

### Advanced Syntax Quick Reference

| Function           | Correct Syntax                                                            | Incorrect Syntax                           |
| ------------ | --------------------------------------------------------------- | ------------------------------ |
| **Partition + Bucket**    | `PARTITIONED BY (days(date)) CLUSTERED BY (id) INTO 32 BUCKETS` | Correct                           |
| **Partition + Sort**    | `PARTITIONED BY (days(date)) SORTED BY (name)`                  | Correct                           |
| **Partition + Bucket + Sort** | `Not supported to use simultaneously`                                                       | Will report duplicate.syntax.element error |
| **bucket Parameter** | `bucket(10, user_id)`                                           | Recommended range 1-1000                   |
| **Partition Sort**     | `WITH t AS (SHOW PARTITIONS ...) SELECT * FROM t ORDER BY ...`  | Use subquery                         |
| **NULL Partition**   | `INSERT ... VALUES (1, NULL)` -> `col=NULL partition`                    | Supported                           |

### Migration Priority Checklist

#### First Priority (Must Do)

* [ ] Use native SQL to create partition tables
* [ ] Execute complete verification checklist to ensure partition tables are correct
* [ ] Compare partition table vs non-partitioned table performance
* [ ] Verify original queries execute correctly on the new platform

#### Second Priority (Important)

* [ ] Simplify complex partition structures (multi-level -> single-level)
* [ ] Control partition count within reasonable range
* [ ] Create indexes for high-frequency non-partition query columns
* [ ] Establish partition health monitoring mechanism

#### Third Priority (Optimization)

* [ ] Establish partition cleanup automation scripts
* [ ] Team training on new partition concepts and operations
* [ ] Continuous performance monitoring and tuning
* [ ] Periodic evaluation and adjustment of partition strategies

***

**Usage Recommendation**: This document can serve as the authoritative reference for Lakehouse partition migration, with all examples directly usable in production environments. For complex migration projects, it is recommended to follow the verification checklist in the document step by step, ensuring each step is correctly verified.

***

**Note**: This document is compiled based on Lakehouse product documentation as of June 2025. It is recommended to periodically check the official documentation for the latest updates. Before using in a production environment, be sure to verify the correctness and performance impact of all operations in a test environment.
