# Lakehouse CREATE TABLE Usage Guide

## Overview

Singdata Lakehouse provides full-featured, high-performance table creation capabilities, perfectly supporting smooth migration from Spark, Hive, MaxCompute, Snowflake, Databricks, and traditional databases. This guide is based on official documentation and production environment validation, providing professional migration paths and best practices for users from different technology backgrounds.

### Quick Navigation

* [Spark User Migration Guide](#spark-user-migration-guide) - Seamless conversion from DataFrame to SQL DDL
* [Hive User Migration Guide](#hive-user-migration-guide) - Perfect partition syntax compatibility and performance improvement
* [MaxCompute User Migration Guide](#maxcompute-user-migration-guide) - Natural extension of the Alibaba Cloud ecosystem
* [Snowflake User Migration Guide](#snowflake-user-migration-guide) - Advanced optimization of cloud-native architecture
* [Databricks User Migration Guide](#databricks-user-migration-guide) - Deep integration of Delta Lake concepts
* [Traditional Database User Migration Guide](#traditional-database-user-migration-guide) - Elegant transformation from OLTP to OLAP

***

## CREATE TABLE Complete Syntax

### Syntax Structure

```sql
CREATE TABLE [ IF NOT EXISTS ] table_name 
(
    column_definition [, column_definition, ...]
    [, index_definition_list]
)
[ PARTITIONED BY (partition_spec) ]
[ CLUSTERED BY (column_list) [SORTED BY (column_list)] INTO num_buckets BUCKETS ]
[ COMMENT 'table_comment' ]
[ PROPERTIES ('key' = 'value', ...) ];
```

### Column Definition Syntax

```sql
column_name column_type 
[ NOT NULL ]
[ PRIMARY KEY ]
[ IDENTITY[(seed)] ]
[ GENERATED ALWAYS AS (expr) ]
[ DEFAULT default_expression ]
[ COMMENT 'column_comment' ]
```

### Supported Data Types

| Category        | Data Type               | Description                    | Counterpart in Other Systems   |
| -------------- | ----------------------- | ------------------------------ | ------------------------------ |
| **Numeric**    | TINYINT                 | 1-byte integer (-128 to 127)   | Spark/Hive: TINYINT            |
|                | SMALLINT                | 2-byte integer                 | Spark/Hive: SMALLINT           |
|                | INT                     | 4-byte integer                 | Spark/Hive: INT/INTEGER        |
|                | BIGINT                  | 8-byte integer                 | Spark/Hive: BIGINT/LONG        |
|                | FLOAT                   | 4-byte floating point          | Spark/Hive: FLOAT              |
|                | DOUBLE                  | 8-byte floating point          | Spark/Hive: DOUBLE             |
|                | DECIMAL(p,s)            | Exact numeric                  | Spark/Hive: DECIMAL            |
| **String**     | VARCHAR(n)              | Variable-length (max 1048576)  | Snowflake: VARCHAR             |
|                | CHAR(n)                 | Fixed-length (1-255)           | Oracle: CHAR                   |
|                | STRING                  | Default 16 MB, adjustable      | Hive/Spark: STRING             |
| **Temporal**   | DATE                    | Date (YYYY-MM-DD)              | Common across all systems      |
|                | TIMESTAMP               | Timestamp (local time)         | Spark: TIMESTAMP               |
|                | TIMESTAMP\_NTZ          | Timestamp without timezone     | Snowflake: TIMESTAMP\_NTZ      |
| **Binary**     | BINARY                  | Binary data, default 16 MB     | Hive: BINARY                   |
| **Boolean**    | BOOLEAN                 | True/False                     | Common across all systems      |
| **Complex**    | ARRAY                   | Array                          | Spark/Hive: ARRAY              |
|                | MAP\<K,V>               | Key-value pairs                | Spark/Hive: MAP                |
|                | STRUCT<...>             | Struct                         | Spark/Hive: STRUCT             |
|                | JSON                    | JSON data, default 16 MB       | Snowflake: VARIANT             |
| **Vector**     | VECTOR(dimension)       | Vector type                    | For vector search scenarios    |
|                | VECTOR(type, dimension) | Vector with element type       | type: tinyint/int/float        |

***

## Spark User Migration Guide

### Core Advantages Comparison

| Feature          | Spark              | Lakehouse                | Advantage               |
| ---------------- | ------------------ | ------------------------ | ----------------------- |
| **Table Creation**| DataFrame API-centric | SQL DDL standardized   | Lower learning curve    |
| **Partition Mgmt**| Manual management   | Hidden partition + transform partition | Automatic optimization |
| **Data Organization**| File-level        | Table-level management   | More efficient metadata |
| **Schema Evolution**| Requires rewrite  | In-place evolution       | Greater flexibility      |

### DataFrame to DDL Conversion

**Spark DataFrame Approach**:

```python
# Spark DataFrame table creation
df = spark.read.parquet("path/to/data")
df.write.partitionBy("year", "month") \
  .bucketBy(10, "user_id") \
  .sortBy("timestamp") \
  .saveAsTable("user_events")
```

**Lakehouse DDL Approach**:

```sql
-- Corresponding Lakehouse CREATE TABLE statement
CREATE TABLE user_events (
    user_id BIGINT,
    event_type STRING,
    timestamp TIMESTAMP,
    properties MAP<STRING, STRING>,
    year INT GENERATED ALWAYS AS (year(timestamp)),
    month INT GENERATED ALWAYS AS (month(timestamp))
) 
PARTITIONED BY (year, month)
CLUSTERED BY (user_id) SORTED BY (timestamp) INTO 10 BUCKETS
COMMENT 'User events table';
```

### Advanced Feature Mapping

**1. Dynamic Partition Handling**

```sql
-- Spark requires manual dynamic partition handling
-- Lakehouse handles it automatically with transform partitioning
CREATE TABLE events (
    event_time TIMESTAMP,
    user_id STRING,
    event_data STRING
) PARTITIONED BY (
    days(event_time),        -- Auto partition by day
    bucket(100, user_id)     -- Auto bucket by user ID
);
```

**2. Schema Merge and Evolution**

```sql
-- Lakehouse natively supports schema evolution
ALTER TABLE events ADD COLUMN new_field STRING;
ALTER TABLE events CHANGE COLUMN event_data TYPE JSON;
```

**3. Complex Data Type Handling**

```sql
-- Fully compatible with Spark complex types
CREATE TABLE user_profiles (
    user_id BIGINT,
    tags ARRAY<STRING>,                          -- Tag array
    attributes MAP<STRING, STRING>,              -- Attribute mapping
    address STRUCT<                              -- Nested struct
        street: STRING,
        city: STRING,
        coordinates: STRUCT<lat: DOUBLE, lon: DOUBLE>
    >,
    preferences JSON                             -- Flexible JSON field
);
```

### Performance Optimization Recommendations

```sql
-- Optimized table creation pattern for Spark users
CREATE TABLE optimized_fact_table (
    -- Business fields
    transaction_id BIGINT IDENTITY(1),
    user_id BIGINT,
    product_id INT,
    amount DECIMAL(18, 2),
    transaction_time TIMESTAMP,
    
    -- Generated partition columns (replaces Spark manual partitioning)
    tx_date STRING GENERATED ALWAYS AS (date_format(transaction_time, 'yyyy-MM-dd')),
    tx_hour INT GENERATED ALWAYS AS (hour(transaction_time))
) 
PARTITIONED BY (tx_date, tx_hour)              -- Two-level partitioning
CLUSTERED BY (user_id) INTO 256 BUCKETS        -- Bucket by user dimension
PROPERTIES (
    'data_lifecycle' = '730',                   -- 2-year lifecycle
    'partition.cache.policy.latest.count' = '7' -- Cache last 7 days
);
```

***

## Hive User Migration Guide

### Perfect Syntax Compatibility

Singdata Lakehouse is fully compatible with Hive's partition syntax while offering more powerful features:

**Traditional Hive Table Creation**:

```sql
-- Hive style (fully supported)
CREATE TABLE IF NOT EXISTS sales_fact (
    order_id BIGINT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2)
) PARTITIONED BY (
    dt STRING,
    region STRING
)
STORED AS PARQUET
TBLPROPERTIES ('transactional'='true');
```

**Lakehouse Enhanced Version**:

```sql
-- Same syntax, better performance
CREATE TABLE IF NOT EXISTS sales_fact (
    order_id BIGINT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- New: default value
) PARTITIONED BY (
    dt STRING,
    region STRING
)
COMMENT 'Sales fact table with enhanced features'
PROPERTIES (
    'data_lifecycle' = '1095',      -- New: 3-year lifecycle management
    'change_tracking' = 'false'     -- New: CDC capability reserved
);
```

### Partition Strategy Upgrade

**Evolution from Static Partitioning to Intelligent Partitioning**:

```sql
-- Hive traditional approach: manual partition management required
INSERT OVERWRITE TABLE sales_fact PARTITION(dt='2024-06-20', region='CN')
SELECT ...;

-- Lakehouse intelligent approach: automatic partition management
CREATE TABLE sales_fact_smart (
    order_id BIGINT,
    order_time TIMESTAMP,
    region_code STRING,
    amount DECIMAL(10,2),
    -- Auto-generated partition column
    dt STRING GENERATED ALWAYS AS (date_format(order_time, 'yyyy-MM-dd'))
) PARTITIONED BY (dt, region_code);

-- Partition is automatically handled on insert
INSERT INTO sales_fact_smart (order_id, order_time, region_code, amount)
VALUES (1001, CURRENT_TIMESTAMP, 'CN', 99.99);
```

### Transactional Table Capability Enhancement

```sql
-- Hive transactional tables have many limitations; Lakehouse natively supports
CREATE TABLE transaction_table (
    id BIGINT PRIMARY KEY,           -- Native primary key support
    data STRING,
    version INT,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) 
CLUSTERED BY (id) INTO 16 BUCKETS   -- Required bucketing optimization
PROPERTIES (
    'data_retention_days' = '7'      -- Time Travel capability
);
```

### Performance Improvement Comparison

| Operation Type     | Hive (MapReduce) | Lakehouse   | Improvement |
| ------------------ | ---------------- | ----------- | ----------- |
| Table Creation Speed | Seconds         | Milliseconds | 10x         |
| Partition Pruning  | File-level scan  | Metadata pruning | 100x     |
| Schema Changes     | Requires rebuild | Online change | Infinite    |
| Small File Compaction | Manual maintenance | Automatic optimization | Automated |

***

## MaxCompute User Migration Guide

### Syntax Comparison and Enhancement

MaxCompute users will find Singdata Lakehouse's syntax very familiar, while the functionality is even more powerful:

**MaxCompute Table Creation**:

```sql
-- MaxCompute syntax
CREATE TABLE IF NOT EXISTS sale_detail(
    shop_name STRING,
    customer_id STRING,
    total_price DOUBLE
)
PARTITIONED BY (sale_date STRING, region STRING)
LIFECYCLE 730;
```

**Lakehouse Equivalent Syntax**:

```sql
-- Nearly identical syntax, more features
CREATE TABLE IF NOT EXISTS sale_detail(
    shop_name STRING,
    customer_id STRING,
    total_price DOUBLE,
    -- New capabilities
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_id BIGINT IDENTITY(1)  -- Auto-increment primary key
)
PARTITIONED BY (sale_date STRING, region STRING)
PROPERTIES (
    'data_lifecycle' = '730',  -- Lifecycle (days)
    'data_retention_days' = '7' -- Time Travel retention period
);
```

### Function Compatibility

```sql
-- MaxCompute function -> Lakehouse function mapping
CREATE TABLE datetime_example (
    id INT,
    -- MaxCompute: GETDATE() -> Lakehouse: CURRENT_TIMESTAMP
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Date functions fully compatible
    year_part INT GENERATED ALWAYS AS (YEAR(created_at)),
    month_part INT GENERATED ALWAYS AS (MONTH(created_at)),
    
    -- String functions are the same
    user_name STRING,
    name_length INT GENERATED ALWAYS AS (LENGTH(user_name))
);
```

### Resource Management Comparison

| Feature          | MaxCompute      | Lakehouse            | Advantage        |
| ---------------- | --------------- | -------------------- | ---------------- |
| Compute Resources | Prepaid CU      | Elastic VCLUSTER     | Pay-per-use      |
| Storage Limit    | Project quota   | Unlimited expansion   | More flexible    |
| Concurrency Ctrl | Job queue       | Dynamic scheduling    | More efficient   |
| Cross-region     | Requires migration | Native support     | Global           |

***

## Snowflake User Migration Guide

### Architectural Philosophy Comparison

Both are cloud-native data warehouses, but Lakehouse provides more control:

**Snowflake-Style Table Creation**:

```sql
-- Snowflake
CREATE OR REPLACE TABLE customer_transactions (
    transaction_id NUMBER AUTOINCREMENT,
    customer_id VARCHAR,
    amount NUMBER(18,2),
    transaction_date TIMESTAMP_NTZ,
    status VARCHAR DEFAULT 'PENDING'
) CLUSTER BY (customer_id);
```

**Lakehouse Enhanced Version**:

```sql
-- Lakehouse: more explicit optimization control
CREATE TABLE IF NOT EXISTS customer_transactions (
    transaction_id BIGINT IDENTITY(1),  -- Corresponds to AUTOINCREMENT
    customer_id VARCHAR(100),
    amount DECIMAL(18,2),
    transaction_date TIMESTAMP_NTZ,
    status VARCHAR(20) DEFAULT 'PENDING',
    
    -- Additional optimization columns
    tx_date STRING GENERATED ALWAYS AS (date_format(transaction_date, 'yyyy-MM-dd')),
    INDEX idx_customer (customer_id) BLOOMFILTER  -- Explicit index
) 
PARTITIONED BY (tx_date)  -- Explicit partition strategy
CLUSTERED BY (customer_id) INTO 128 BUCKETS  -- Explicit bucket count
COMMENT 'Customer transaction table with explicit optimizations';
```

### Time Travel and Cloning

```sql
-- Snowflake Time Travel -> Lakehouse Time Travel
CREATE TABLE orders_backup AS
SELECT * FROM orders;  -- Immediate copy

-- Lakehouse also supports:
ALTER TABLE orders SET PROPERTIES ('data_retention_days' = '30');  -- 30-day history
-- Query historical data
SELECT * FROM orders TIMESTAMP AS OF '2024-06-01 00:00:00';
```

### Performance Tuning Differences

```sql
-- Snowflake: auto-optimization
-- Lakehouse: provides more tuning options

CREATE TABLE large_fact_table (
    -- Column definitions
    fact_id BIGINT,
    dim1_id INT,
    dim2_id INT,
    measure1 DECIMAL(18,4),
    measure2 DECIMAL(18,4),
    fact_time TIMESTAMP,
    
    -- Performance optimization
    fact_date STRING GENERATED ALWAYS AS (date_format(fact_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (fact_date)
CLUSTERED BY (dim1_id, dim2_id) 
    SORTED BY (fact_time DESC)    -- Additional sort optimization
    INTO 256 BUCKETS              -- Precise parallelism control
PROPERTIES (
    'partition.cache.policy.latest.count' = '30'  -- Cache policy
);
```

***

## Databricks User Migration Guide

### Deep Integration of Delta Lake Concepts

Lakehouse draws from Delta Lake's design philosophy, offering similar but more concise syntax:

**Databricks Delta Table**:

```python
# Databricks Python API
(spark.sql("""
    CREATE TABLE IF NOT EXISTS events (
        event_id LONG,
        event_time TIMESTAMP,
        user_id STRING,
        event_type STRING,
        properties MAP<STRING, STRING>
    ) USING DELTA
    PARTITIONED BY (date(event_time))
    TBLPROPERTIES (
        'delta.deletedFileRetentionDuration' = '7 days',
        'delta.optimizeWrite' = 'true'
    )
"""))
```

**Lakehouse Native SQL**:

```sql
-- Pure SQL implementation, no Python wrapper needed
CREATE TABLE IF NOT EXISTS events (
    event_id BIGINT,
    event_time TIMESTAMP,
    user_id STRING,
    event_type STRING,
    properties MAP<STRING, STRING>,
    -- Auto partition column
    event_date DATE GENERATED ALWAYS AS (CAST(event_time AS DATE))
) 
PARTITIONED BY (event_date)
PROPERTIES (
    'data_retention_days' = '7',      -- Corresponds to deletedFileRetentionDuration
    'data_lifecycle' = '365'          -- Data lifecycle management
);
```

### Streaming and Batch Unified Architecture

```sql
-- Table design supporting real-time writes
CREATE TABLE streaming_events (
    event_id BIGINT PRIMARY KEY,      -- Supports real-time deduplication
    event_data JSON,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    
    -- Partition design supports streaming writes
    event_hour INT GENERATED ALWAYS AS (hour(received_at)),
    event_date STRING GENERATED ALWAYS AS (date_format(received_at, 'yyyy-MM-dd'))
) 
PARTITIONED BY (event_date, event_hour)
CLUSTERED BY (event_id) INTO 32 BUCKETS
PROPERTIES (
    'change_tracking' = 'false'  -- Reserved for Table Stream
);
```

### Z-Order Optimization Mapping

```sql
-- Databricks: OPTIMIZE table ZORDER BY (col1, col2)
-- Lakehouse: achieve similar effect through CLUSTERED BY + SORTED BY

CREATE TABLE optimized_table (
    col1 INT,
    col2 STRING,
    col3 DECIMAL(10,2),
    col4 TIMESTAMP
)
CLUSTERED BY (col1, col2)      -- Data clustering
SORTED BY (col1, col2)          -- Sort optimization
INTO 64 BUCKETS;
```

***

## Traditional Database User Migration Guide

### Mindset Transformation

Transitioning from OLTP to OLAP requires adjusting table design thinking:

**Traditional OLTP Design**:

```sql
-- MySQL/PostgreSQL/Oracle style
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATETIME DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'NEW',
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_date (order_date),
    INDEX idx_customer (customer_id)
);
```

**Lakehouse OLAP Design**:

```sql
-- Analytics-optimized design
CREATE TABLE orders (
    order_id BIGINT IDENTITY(1),     -- Auto-increment primary key
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'NEW',
    
    -- Analytics optimization columns
    order_year INT GENERATED ALWAYS AS (year(order_date)),
    order_month INT GENERATED ALWAYS AS (month(order_date)),
    order_day INT GENERATED ALWAYS AS (day(order_date)),
    
    -- Index definitions
    INDEX bloom_customer (customer_id) BLOOMFILTER,
    INDEX bloom_status (status) BLOOMFILTER
) 
PARTITIONED BY (order_year, order_month)  -- Monthly partitioning
CLUSTERED BY (customer_id) INTO 256 BUCKETS  -- Customer dimension optimization
PROPERTIES (
    'data_lifecycle' = '2555'  -- 7-year data retention
);
```

### Data Type Mapping

| Traditional DB        | Lakehouse          | Migration Advice              |
| --------------------- | ------------------ | ----------------------------- |
| INT AUTO\_INCREMENT   | BIGINT IDENTITY(1) | Use BIGINT to avoid overflow  |
| DATETIME              | TIMESTAMP          | Unified time type             |
| TEXT                  | STRING             | Default 16 MB, adjustable     |
| ENUM                  | VARCHAR + CHECK    | Use constraints instead       |
| JSON (MySQL)          | JSON               | Native JSON support           |
| SERIAL (PG)           | BIGINT IDENTITY(1) | Fully compatible              |

### Index Strategy Transformation

```sql
-- Traditional B-Tree index -> Columnar storage optimization
CREATE TABLE user_activity (
    user_id BIGINT,
    activity_time TIMESTAMP,
    activity_type VARCHAR(50),
    details JSON,
    
    -- Bloom filter replaces B-Tree (for point queries)
    INDEX bloom_user (user_id) BLOOMFILTER,
    
    -- Inverted index replaces full-text index
    INDEX inv_details (details) INVERTED PROPERTIES ('analyzer' = 'english'),
    
    -- Generated column optimizes time queries
    activity_date STRING GENERATED ALWAYS AS (date_format(activity_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (activity_date)  -- Time partitioning accelerates range queries
CLUSTERED BY (user_id) INTO 128 BUCKETS;  -- User dimension clustering
```

***

## Advanced Features in Detail

### 1. Auto-Increment Column (IDENTITY)

```sql
-- Complete example: Orders table with auto-increment primary key
CREATE TABLE order_master (
    order_id BIGINT IDENTITY(1000),  -- Starts from 1000
    order_no VARCHAR(50) NOT NULL,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(18,2),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT 'Order master table';

-- Notes:
-- 1. Only supports BIGINT type
-- 2. Continuity is not guaranteed (may skip under high concurrency)
-- 3. Cannot be added via ALTER TABLE
```

**2. Generated Column (GENERATED ALWAYS AS)**

```sql
-- Automatic time dimension generation
CREATE TABLE sales_detail (
    sale_time TIMESTAMP,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    
    -- Auto-calculated fields
    total_amount DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price),
    
    -- Time dimension expansion
    sale_date STRING GENERATED ALWAYS AS (date_format(sale_time, 'yyyy-MM-dd')),
    sale_year INT GENERATED ALWAYS AS (year(sale_time)),
    sale_month INT GENERATED ALWAYS AS (month(sale_time)),
    sale_week INT GENERATED ALWAYS AS (weekofyear(sale_time)),
    sale_hour INT GENERATED ALWAYS AS (hour(sale_time))
) 
PARTITIONED BY (sale_date)  -- Generated columns can be used for partitioning
COMMENT 'Sales detail table with auto-calculated fields';
```

**Generated Column Usage Restrictions**:

* Generated columns cannot be used in `CLUSTERED BY` or `SORTED BY`
* Primary key tables cannot use generated columns as partition keys
* Only deterministic functions are supported; non-deterministic functions like `CURRENT_DATE`, `RANDOM` are not allowed

### 3. Default Values (DEFAULT)

```sql
-- Audit table design
CREATE TABLE audit_log (
    log_id BIGINT IDENTITY(1),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    user_id VARCHAR(50) DEFAULT CURRENT_USER(),  -- Current user
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Current time
    client_ip VARCHAR(50) DEFAULT '0.0.0.0',
    status VARCHAR(20) DEFAULT 'SUCCESS',
    details JSON
) 
PARTITIONED BY (date_format(operation_time, 'yyyy-MM-dd'))
COMMENT 'Unified audit log table';
```

### 4. Primary Keys and Unique Constraints

```sql
-- Primary key table design for CDC scenarios
CREATE TABLE customer_snapshot (
    customer_id BIGINT,
    snapshot_date DATE,
    customer_name VARCHAR(200),
    customer_level VARCHAR(20),
    total_purchase DECIMAL(18,2),
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (customer_id, snapshot_date)
) 
PARTITIONED BY (snapshot_date)
CLUSTERED BY (customer_id, snapshot_date) 
SORTED BY (customer_id, snapshot_date) INTO 64 BUCKETS  -- Note: primary key tables must use ASC sorting
COMMENT 'Customer snapshot table for CDC';
```

**Important Primary Key Table Restrictions**:

* Primary key columns must be included in `CLUSTERED BY` and `SORTED BY`
* `SORTED BY` must use ascending order (ASC), descending (DESC) is not allowed
* Partition columns must be a subset of the primary key
* Generated columns cannot be used as partition columns for primary key tables

### 5. Complex Index Strategies

```sql
-- Multi-dimensional query optimization table
CREATE TABLE product_search (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR(500),
    description STRING,
    category_path VARCHAR(200),
    brand VARCHAR(100),
    price DECIMAL(10,2),
    tags ARRAY<STRING>,
    attributes MAP<STRING, STRING>,
    
    -- Multiple index combinations (note: index names must be globally unique)
    INDEX bloom_prod_brand (brand) BLOOMFILTER,  -- Fast brand filtering
    INDEX bloom_prod_category (category_path) BLOOMFILTER,  -- Category filtering
    INDEX inv_prod_name (product_name) INVERTED PROPERTIES ('analyzer' = 'chinese'),  -- Product name search
    INDEX inv_prod_desc (description) INVERTED PROPERTIES ('analyzer' = 'chinese')  -- Description search
)
CLUSTERED BY (product_id) SORTED BY (product_id) INTO 128 BUCKETS  -- Primary key table restriction
COMMENT 'Product search optimization table';
```

**Index Naming Best Practices**:

* Index names must be unique across the entire database
* Recommended format: `table_name_column_name` or `idx_table_name_column_name`
* Avoid overly generic names such as `idx_id`

### 6. Vector Index (VECTOR)

```sql
-- Vector search scenario table design
CREATE TABLE embeddings_search (
    doc_id BIGINT PRIMARY KEY,
    content STRING,
    embedding VECTOR(512),  -- 512-dimensional vector, default float type
    vec_small VECTOR(128),  -- 128-dimensional vector
    vec_int VECTOR(int, 256),  -- 256-dimensional vector with int type
    
    -- Vector index
    INDEX vec_idx (embedding) USING VECTOR PROPERTIES (
        'scalar.type' = 'f32',
        'distance.function' = 'cosine_distance',  -- Cosine distance
        'm' = '16',  -- HNSW algorithm parameter
        'ef.construction' = '200'
    )
)
CLUSTERED BY (doc_id) SORTED BY (doc_id) INTO 64 BUCKETS
COMMENT 'Vector search optimization table';
```

**Vector Type Usage Restrictions**:

* Cannot be used in ORDER BY or GROUP BY
* Supported element types: tinyint, int, float (default)
* Can be mutually converted with array types

***

## Partition Strategy Best Practices

### 1. Time-Based Partition Design

```sql
-- Multi-granularity time partitioning
CREATE TABLE event_log (
    event_id BIGINT,
    event_time TIMESTAMP,
    event_type VARCHAR(50),
    event_data JSON,
    
    -- Multi-level partition column generation
    event_date STRING GENERATED ALWAYS AS (date_format(event_time, 'yyyy-MM-dd')),
    event_hour INT GENERATED ALWAYS AS (hour(event_time))
) 
PARTITIONED BY (event_date, event_hour)  -- Two-level partitioning
COMMENT 'Event log table with hourly partitions';

-- Transform partition function example
CREATE TABLE metric_data (
    metric_time TIMESTAMP,
    metric_name VARCHAR(100),
    metric_value DOUBLE
) 
PARTITIONED BY (
    days(metric_time)  -- Partition by number of days (since 1970-01-01)
);
```

### 2. Business Dimension Partitioning

```sql
-- Multi-dimension combined partitioning
CREATE TABLE transaction_fact (
    tx_id BIGINT IDENTITY(1),
    tx_time TIMESTAMP,
    region_code VARCHAR(10),
    channel_code VARCHAR(10),
    amount DECIMAL(18,2),
    
    tx_date STRING GENERATED ALWAYS AS (date_format(tx_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (tx_date, region_code, channel_code)  -- Three-dimensional partitioning
CLUSTERED BY (tx_id) INTO 256 BUCKETS
COMMENT 'Transaction fact table with multi-dimension partitioning';
```

### 3. Partition Count Control

```sql
-- Properly control partition granularity
CREATE TABLE log_archive (
    log_time TIMESTAMP,
    log_level VARCHAR(10),
    log_content STRING,
    
    -- Monthly partitioning to avoid too many partitions
    log_month STRING GENERATED ALWAYS AS (date_format(log_time, 'yyyy-MM'))
) 
PARTITIONED BY (log_month)
PROPERTIES (
    'data_lifecycle' = '1095'  -- Auto-clean after 3 years
);
```

***

## Bucketing Optimization Guide

### 1. Bucket Count Selection

```sql
-- Bucket count calculation formula: total data size / 128 MB ~ 1 GB

-- Small table (<10 GB): small number of buckets
CREATE TABLE small_dim (
    dim_id INT,
    dim_name VARCHAR(100)
) CLUSTERED BY (dim_id) INTO 8 BUCKETS;

-- Medium table (10 GB ~ 1 TB): moderate number of buckets
CREATE TABLE medium_fact (
    fact_id BIGINT,
    measure DECIMAL(18,4)
) CLUSTERED BY (fact_id) INTO 128 BUCKETS;

-- Large table (>1 TB): large number of buckets
CREATE TABLE large_fact (
    id BIGINT,
    data STRING
) CLUSTERED BY (id) INTO 1024 BUCKETS;
```

### 2. Bucket Key Selection Strategy

```sql
-- JOIN optimization: use the JOIN key as the bucket key
CREATE TABLE order_items (
    order_id BIGINT,
    item_id INT,
    quantity INT,
    price DECIMAL(10,2)
) CLUSTERED BY (order_id) INTO 256 BUCKETS;  -- Same bucketing as orders table

CREATE TABLE orders (
    order_id BIGINT,
    customer_id INT,
    order_date DATE
) CLUSTERED BY (order_id) INTO 256 BUCKETS;  -- Same bucketing strategy
```

### 3. Sort Optimization

```sql
-- SORTED BY accelerates range queries
CREATE TABLE time_series_data (
    device_id VARCHAR(50),
    metric_time TIMESTAMP,
    metric_value DOUBLE
) 
CLUSTERED BY (device_id) 
SORTED BY (metric_time DESC)  -- Latest data first
INTO 128 BUCKETS;
```

***

## Table Properties (PROPERTIES) In-Depth Analysis

### Officially Supported Properties

```sql
CREATE TABLE data_management (
    id BIGINT,
    data STRING,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) 
PROPERTIES (
    -- Lifecycle management
    'data_lifecycle' = '1095',           -- Auto-delete after 3 years (days)
    'data_retention_days' = '30',        -- 30-day Time Travel history
    
    -- Cache policy
    'partition.cache.policy.latest.count' = '7',  -- Cache the most recent 7 partitions
    
    -- Change tracking
    'change_tracking' = 'true',          -- Enable Table Stream functionality
    
    -- Field length limits (bytes)
    'cz.storage.write.max.string.bytes' = '33554432',  -- STRING max 32 MB
    'cz.storage.write.max.binary.bytes' = '33554432',  -- BINARY max 32 MB
    'cz.storage.write.max.json.bytes' = '33554432'     -- JSON max 32 MB
);
```

### Property Usage Reference

| Property Name                          | Description                       | Value Range          | Default Value    |
| -------------------------------------- | --------------------------------- | -------------------- | ---------------- |
| data\_lifecycle                        | Data lifecycle (days)             | >0 or -1 (disabled)  | -1               |
| data\_retention\_days                  | Time Travel retention period      | 0-90                 | 1                |
| partition.cache.policy.latest.count    | Cache the most recent N partitions | >=0                  | 0                |
| change\_tracking                       | Whether to enable change tracking | true/false           | false            |
| cz.storage.write.max.string.bytes      | STRING maximum length             | >0                   | 16777216 (16 MB) |
| cz.storage.write.max.binary.bytes      | BINARY maximum length             | >0                   | 16777216 (16 MB) |
| cz.storage.write.max.json.bytes        | JSON maximum length               | >0                   | 16777216 (16 MB) |

***

## Recommended Table Creation Patterns

### 1. Dimension Table Pattern

```sql
-- Standard dimension table design
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category_id INT,
    brand_id INT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_date DATE,
    modified_date DATE,
    
    -- Audit columns
    created_by VARCHAR(50),
    modified_by VARCHAR(50),
    
    -- Index optimization
    INDEX bloom_code (product_code) BLOOMFILTER,
    INDEX bloom_category (category_id) BLOOMFILTER,
    INDEX inv_name (product_name) INVERTED PROPERTIES ('analyzer' = 'chinese')
) 
CLUSTERED BY (product_id) INTO 32 BUCKETS  -- Dimension tables are usually small
COMMENT 'Product dimension table';
```

### 2. Fact Table Pattern

```sql
-- Large fact table design
CREATE TABLE fact_sales (
    -- Business primary key
    sale_id BIGINT IDENTITY(1),
    
    -- Dimension foreign keys
    date_id INT NOT NULL,
    product_id INT NOT NULL,
    customer_id BIGINT NOT NULL,
    store_id INT NOT NULL,
    
    -- Measures
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(18,2) GENERATED ALWAYS AS 
        (quantity * unit_price - discount_amount + tax_amount),
    
    -- Timestamp
    sale_time TIMESTAMP NOT NULL,
    
    -- Partition column
    sale_date STRING GENERATED ALWAYS AS (date_format(sale_time, 'yyyy-MM-dd')),
    
    -- Indexes
    INDEX bloom_product (product_id) BLOOMFILTER,
    INDEX bloom_customer (customer_id) BLOOMFILTER
) 
PARTITIONED BY (sale_date)
CLUSTERED BY (customer_id) SORTED BY (sale_time DESC) INTO 256 BUCKETS
PROPERTIES (
    'data_lifecycle' = '2555',  -- 7-year retention
    'partition.cache.policy.latest.count' = '30'  -- Cache 30 days
)
COMMENT 'Sales fact table';
```

### 3. Wide Table Pattern

```sql
-- Wide table design (star schema denormalization)
CREATE TABLE user_behavior_wide (
    -- User dimension
    user_id BIGINT,
    user_name VARCHAR(100),
    user_level VARCHAR(20),
    register_date DATE,
    
    -- Behavior facts
    behavior_id BIGINT IDENTITY(1),
    behavior_type VARCHAR(50),
    behavior_time TIMESTAMP,
    
    -- Product dimension (denormalized)
    product_id INT,
    product_name VARCHAR(200),
    category_name VARCHAR(100),
    brand_name VARCHAR(100),
    
    -- Computed columns
    behavior_date STRING GENERATED ALWAYS AS (date_format(behavior_time, 'yyyy-MM-dd')),
    behavior_hour INT GENERATED ALWAYS AS (hour(behavior_time))
) 
PARTITIONED BY (behavior_date, behavior_hour)
CLUSTERED BY (user_id) INTO 512 BUCKETS
COMMENT 'User behavior wide table';
```

***

## Performance Tuning Checklist

### Pre-Creation Assessment

* [ ] **Data Volume Assessment**: Estimate the total table size and growth rate
* [ ] **Query Patterns**: Identify the primary query dimensions and filter conditions
* [ ] **Update Frequency**: Determine whether append-only or updates/deletes are needed
* [ ] **Concurrency Requirements**: Assess query concurrency and response time requirements

### Partition Design Checklist

* [ ] **Partition Key Selection**: Choose the most commonly used filter columns in queries
* [ ] **Partition Granularity**: Ensure single partition size is between 100 MB and 1 GB
* [ ] **Partition Count**: Avoid creating too many partitions (recommended < 10000)
* [ ] **Transform Partitioning**: Consider using transform functions to optimize partitioning

### Bucketing Optimization Checklist

* [ ] **Bucket Key Selection**: Prioritize JOIN keys or high-cardinality columns
* [ ] **Bucket Count**: Choose based on data volume (total / 128 MB ~ 1 GB)
* [ ] **Sort Strategy**: Add SORTED BY for range queries
* [ ] **Data Skew**: Avoid selecting heavily skewed columns as bucket keys

### Index Strategy Checklist

* [ ] **Bloom Filter**: Create for high-cardinality point-query columns
* [ ] **Inverted Index**: Create for text search columns
* [ ] **Vector Index**: Create for vector search scenarios
* [ ] **Index Maintenance**: Periodically execute BUILD INDEX
* [ ] **Index Evaluation**: Monitor index usage rate and effectiveness

***

## FAQ and Solutions

### Q1: How to handle very large tables (>10 TB)?

```sql
-- Multi-level partitioning strategy
CREATE TABLE huge_table (
    id BIGINT,
    event_time TIMESTAMP,
    region VARCHAR(10),
    data STRING,
    
    -- Three-level partitioning
    year INT GENERATED ALWAYS AS (year(event_time)),
    month INT GENERATED ALWAYS AS (month(event_time)),
    day INT GENERATED ALWAYS AS (day(event_time))
) 
PARTITIONED BY (year, month, day, region)
CLUSTERED BY (id) INTO 2048 BUCKETS;
```

### Q2: How to optimize real-time writes?

```sql
-- Real-time write optimized table design
CREATE TABLE realtime_events (
    event_id BIGINT PRIMARY KEY,  -- Supports deduplication
    event_data JSON,
    ingest_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Hourly partitioning reduces write conflicts
    ingest_hour INT GENERATED ALWAYS AS (hour(ingest_time)),
    ingest_date STRING GENERATED ALWAYS AS (date_format(ingest_time, 'yyyy-MM-dd'))
) 
PARTITIONED BY (ingest_date, ingest_hour)
CLUSTERED BY (event_id) INTO 64 BUCKETS;  -- Moderate bucketing
```

### Q3: How to design SCD (Slowly Changing Dimension)?

```sql
-- Type 2 SCD design
CREATE TABLE dim_customer_scd (
    customer_id BIGINT,
    customer_name VARCHAR(200),
    customer_level VARCHAR(20),
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN,
    
    PRIMARY KEY (customer_id, effective_date)
) 
CLUSTERED BY (customer_id, effective_date) 
SORTED BY (customer_id, effective_date)  -- Primary key tables must use ASC sorting
INTO 128 BUCKETS
COMMENT 'Customer dimension with SCD Type 2';
```

### Q4: How to adjust field length limits?

```sql
-- Adjust maximum length of STRING/BINARY/JSON fields
ALTER TABLE large_content_table SET PROPERTIES (
    'cz.storage.write.max.string.bytes' = '67108864',  -- 64 MB
    'cz.storage.write.max.json.bytes' = '33554432'     -- 32 MB
);
```

***

## Migration Success Factors Summary

### Technology Stack Migration Quick Reference

| Source System    | Key Migration Points              | Lakehouse Advantage              |
| ---------------- | --------------------------------- | -------------------------------- |
| **Spark**        | DataFrame -> SQL DDL              | Standard SQL lowers the barrier  |
| **Hive**         | Partition syntax fully compatible | 100x performance improvement     |
| **MaxCompute**   | Functions largely consistent       | Elastic resources, more flexible |
| **Snowflake**    | Add explicit optimization         | Controllable costs               |
| **Databricks**   | Delta concepts aligned            | Pure SQL, more concise           |
| **Traditional DB** | OLTP -> OLAP mindset            | Unlimited scalability            |

### Table Creation Best Practices Summary

1. **Proper Partitioning**: Choose low-cardinality, frequently queried columns
2. **Moderate Bucketing**: Choose based on data volume, avoid over-bucketing
3. **Precise Indexing**: Only create indexes for necessary columns
4. **Smart Use of Generated Columns**: Reduce ETL complexity
5. **Lifecycle Management**: Set a reasonable retention period
6. **Cautious Primary Keys**: Only use in CDC scenarios
7. **Test First**: Validate on small datasets before large-scale application

### Expected Performance Optimization Results

By following the table creation best practices in this guide:

* **Query Performance**: 10-100x improvement over Hive
* **Storage Efficiency**: Columnar compression saves 60-80% space
* **Maintenance Cost**: Automated management reduces manual effort by 90%
* **Scalability**: Supports petabyte-scale data volumes

***

## Important Constraints and Limitations Summary

### Primary Key Table Constraints

* **CLUSTERED BY**: Must include all primary key columns
* **SORTED BY**: Must include all primary key columns and can only use ascending (ASC) order
* **PARTITIONED BY**: Partition columns must be a subset of the primary key
* **Generated Column Restriction**: Primary key tables cannot use generated columns as partition keys

### Generated Column Restrictions

* Cannot be used in `CLUSTERED BY` or `SORTED BY`
* Non-deterministic functions are not supported (e.g., `CURRENT_DATE`, `RANDOM`, `CURRENT_TIMESTAMP`)
* Aggregate functions, window functions, or table functions are not supported
* Values cannot be specified for generated columns during INSERT

### Index Constraints

* Index names must be unique across the entire database
* BLOOMFILTER indexes do not support `BUILD INDEX` after creation
* Inverted indexes must specify an analyzer
* Vector indexes cannot be used in ORDER BY or GROUP BY

### Data Type Restrictions

* Auto-increment columns (IDENTITY) only support the `BIGINT` type
* VARCHAR maximum length is 1048576 (approximately 1 MB)
* STRING/BINARY/JSON default maximum is 16 MB; adjustable via properties
* Partition columns do not support floating-point types such as `FLOAT`, `DOUBLE`, `DECIMAL`
* VECTOR type elements support tinyint, int, float

### Partition Restrictions

* A single task can write to a maximum of 2048 partitions (adjustable via parameters)
* Transform partition functions use `years`, `months`, `days`, `hours` (note the plural form)
* Partition columns do not support complex data types (ARRAY, MAP, STRUCT)

***

## Summary

Singdata Lakehouse's CREATE TABLE functionality provides enterprises with powerful, flexible, high-performance table management capabilities. Regardless of your technology background, you can quickly get started and unlock the system's maximum value. Through the detailed explanations and rich examples in this guide, you should now have mastered all the skills needed to create efficient data tables in Lakehouse.

Start your Lakehouse journey now and experience the powerful capabilities of the next-generation data warehouse!

***

**Note**: This document is compiled based on the Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, always verify the correctness and performance impact of all operations in a test environment.
