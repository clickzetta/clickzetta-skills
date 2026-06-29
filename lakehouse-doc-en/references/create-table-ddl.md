# CREATE TABLE

## Description

This statement is used to create a new table. In Lakehouse, a table is the basic unit for storing data. By creating a table, you can organize and manage data according to a specified structure.

**This document covers**: basic table creation syntax → column types → primary key / auto-increment / generated columns / default values → index definitions (Bloomfilter / inverted / vector) → partitioning (PARTITIONED BY) → bucketing (CLUSTERED BY) → table properties (PROPERTIES) → LIKE table creation → CTAS (AS SELECT) → complete examples.

### Basic Table Creation Statement

```SQL
CREATE TABLE [ IF NOT EXISTS ] table_name
(
    column_definition  [column_definition ,...]
    index_definition_list
)
[ PARTITIONED BY (column_name column_type | column_name | transform_function) ]
[ CLUSTERED BY (column_name,...) 
    [SORTED BY (column_name [ ASC | DESC ])] 
    [INTO num_buckets BUCKETS] 
]
[ ROW FILTER filter_function ON (column_name,...) ]
[ COMMENT 'table_comment' ]
[PROPERTIES('data_lifecycle'='day_num')];


```
### column\_definition Description

#### Syntax
```
column_name column_type 
{ NOT NULL |
  PRIMARY KEY|
  UNIQUE|
  IDENTITY[(seed)]|
  GENERATED ALWAYS AS ( expr ) |
  DEFAULT default_expression |
  COMMENT column_comment |   
}
```
#### Column Type column\_type

* **column\_type**: The data type of the column, supporting integers, floating-point numbers, strings, date/time, booleans, arrays, Map, Struct, JSON, VECTOR, and other types. For the complete list and descriptions, see [Data Types](data-type.md).

* **NOT NULL**: Indicates that this column is not allowed to be NULL. It only supports being specified when creating the table and does not support adding using the ALTER syntax. If you need to remove the NOT NULL constraint, please use the modify table type syntax:
```
ALTER TABLE table_name CHANGE COLUMN colum_name data_type
```
For example, remove the `not null` constraint for the `int` type
```
CREATE TABLE aa_not_null (id int NOT NULL)
ALTER TABLE aa_not_null CHANGE COLUMN id TYPE int;
```
#### Primary Key (PRIMARY KEY)

* **PRIMARY KEY**: Used to ensure the uniqueness of each record in the table. In big data scenarios, since data volumes are typically very large, checking all keys one by one to ensure uniqueness is impractical and inefficient, so primary key constraints are generally not recommended in big data environments. However, Lakehouse still provides support for primary keys to meet data integrity requirements in specific scenarios. In the Lakehouse architecture, for tables with a defined primary key, the system will automatically deduplicate data based on the primary key value during real-time data ingestion, which is especially important for Change Data Capture (CDC) scenarios. For example, you can synchronize MySQL database binlog logs to Lakehouse in real time to ensure data consistency. Once a primary key is set, you need to handle data through the [real-time data interface](java_reference/realtime-upload.md). During CDC real-time writes, the system will automatically deduplicate data based on the primary key to maintain data accuracy and integrity. This can only be specified when creating the table. For more details, refer to the [Primary Key Introduction](primary-key.md).
```
CREATE    TABLE pk_table 
(id int, col string PRIMARY KEY (id));

CREATE    TABLE pk_table 
(id int PRIMARY KEY, col string);
--Definition of primary key in bucketed table
CREATE    TABLE pk_table (
          id int,
          col string,
          cluster_key string,
          PRIMARY key (id)
          ) CLUSTERED BY (id, cluster_key) SORTED BY (id) INTO 16 BUCKETS;

--Definition of primary key in partitioned table
CREATE    TABLE pk_table (
          id int,
          col string,
          pt string,
          PRIMARY key (id, pt)
          ) PARTITIONED BY (pt);
```
#### Unique Key (UNIQUE)

* **Unique Key (UNIQUE)** is used to declare that the values of a column or a combination of columns are unique. Unlike primary keys, UNIQUE is a **declarative constraint**: in the default mode (`DISABLE NOVALIDATE RELY`), uniqueness is not enforced at write time. It is primarily used to declare data semantics to the query optimizer to improve query optimization. UNIQUE columns allow NULL values. A table can have multiple UNIQUE constraints, and they can only be specified at table creation time. Both column-level and table-level (including composite) forms are supported. For detailed behavior, see [Unique Key Introduction](unique-key.md).

```
-- Column-level
CREATE TABLE uk_table (id int UNIQUE, col string);

-- Table-level (single column)
CREATE TABLE uk_table (id int, col string, UNIQUE (id));

-- Table-level (composite)
CREATE TABLE uk_table (a int, b int, UNIQUE (a, b));

-- With modifier (default is DISABLE NOVALIDATE RELY)
CREATE TABLE uk_table (id int UNIQUE NORELY, col string);
```

> ⚠️ If you need to enforce deduplication at write time, use a primary key (PRIMARY KEY); do not rely on the UNIQUE constraint.

#### Auto-increment Column (IDENTITY\[(seed)])

* **IDENTITY\[(seed**)]: Supports specifying auto-increment. It cannot guarantee that the values in the sequence are continuous (gapless), nor can it guarantee that the sequence values are allocated in a specific order. This is because other concurrent inserts may occur in the table. These limitations are part of the design to improve performance. For specific usage, refer to the [IDENTITY Column documentation](identity-column.md)
```
CREATE    TABLE identity_test (id bigint IDENTITY(1), col string);
```
#### Generated Columns (GENERATED ALWAYS AS)

* **GENERATED ALWAYS AS (expr)**: Automatically generates the value of a column through the expression `expr`. The expression can include constants and built-in scalar deterministic SQL functions. Non-deterministic functions such as (current\_date, random, current\_timestamp, context functions) or operators are not supported. Aggregate functions, window functions, or table functions are also not supported. Partition columns using generated columns are supported.
```
CREATE TABLE t_genet (col1 TIMESTAMP,pt STRING GENERATED ALWAYS AS (date_format(col1, 'yyyy-MM-dd'))) PARTITIONED BY (pt);
```
#### Default Values (DEFAULT)

* **DEFAULT default\_expression**: Defines a default value for a newly added column. If the value of this column is not specified in INSERT, UPDATE, or MERGE operations, this default value will be automatically used. For data rows that existed before the column was added, the column will be filled with null. Supports non-deterministic functions such as (current\_date, random, current\_timestamp, context functions) and constant values.
```
CREATE TABLE t_default(id INT,col1 STRING DEFAULT current_timestamp());
```
### Index Definition (index\_definition\_list)

####  Syntax
```
INDEX index_name (col_name) index_type [COMMENT 'xxxxxx'] [PROPERTIES('key'='value')]
```
**columns\_difinition**: Defines the field information of the table, the last field must be separated by a comma

**INDEX**: Keyword

**index\_name**: Custom name of the index

**column\_name**: The name of the field that needs to be indexed

**index\_type**: Index type, currently supports [bloomfilter](create-bloomfilter-index.md), [inverted](inverted-index.md), [vector](create-vector-index.md)

**COMMENT**: Specifies the description information of the index

**PROPERTIES**: Specifies the parameters of the INDEX, different indexes support different parameters, refer to the corresponding index documentation for details

### Partitioned By (PARTITIONED BY) {#partitioned-by}

Partitioning is a method of speeding up queries by grouping similar rows together at the time of writing. Using partitioning can achieve data pruning and optimize queries. When querying a table, use the WHERE clause to query the specified partition to avoid full table scans, improve processing efficiency, and reduce computing resources. For details, refer to [Partition Introduction](partition_table.md). Note that a single task currently limits 2048 partitions during writes; exceeding this limit will report an error: `The count of dynamic partitions exceeds the maximum number 2048`. Before inserting, it is recommended to count the number of partitions first, e.g.: `select count(distinct pt) from table`. If you do have that many partitions, you can import in batches, or you can modify this limit by adding the parameter `set cz.sql.table.sink.max.partition.per.thread=10000`. There is no limit on the total number of partitions in Lakehouse; the limit applies per single task. If your data volume is small, it is recommended not to set cluster key and partition key. It is recommended to keep a single partition and cluster key at the hundreds of MB to GB level, for example a parquet format file compressed to 128MB.

Two writing methods are supported.
The first method declares the partition fields and types when creating the table; just declare the fields in the PARTITIONED BY clause:
```SQL
CREATE TABLE prod.db.sample (
id bigint,
category string,
data string
)
PARTITIONED BY(category)
```
The second type of partition field and type is written in the PARTITIONED BY statement:
```SQL
CREATE TABLE prod.db.sample (
id bigint,
data string)
PARTITIONED BY(category string)
```
### Bucketed Table (CLUSTERED BY)

* CLUSTERED BY: Specify the Hash Key. Singdata will perform a hash operation on the specified column and distribute the data into various data buckets based on the hash value. To avoid data skew and hotspots, and to improve parallel execution efficiency, it is recommended to choose columns with a large range of values and few duplicate keys as the Hash Key. This usually has a significant effect when performing join operations. It is recommended to use CLUSTERED BY in scenarios with large amounts of data, generally with a bucket size between 128MB and 1GB. If no bucketing is specified, the default is 256 buckets. It is recommended to keep SORTED BY and CLUSTERED BY consistent for better performance. When the SORTED BY clause is specified, row data will be sorted according to the specified columns. For more information, refer to [Bucketing](cluster-table.md)
```
--Specify bucketing and sorting
CREATE TABLE sales_data (
    sale_id INT,
    product_id INT,
    quantity_sold INT,
    sale_date DATE
) CLUSTERED BY (product_id)
SORTED BY (sale_date DESC)
INTO 50 BUCKETS;
--Specify bucketing and the number of buckets
CREATE TABLE sales_data (
    sale_id INT,
    product_id INT,
    quantity_sold INT,
    sale_date DATE
) CLUSTERED BY (product_id)
INTO 50 BUCKETS;
```
### SORTED BY

SORTED BY: Specifies the sorting method for fields within a file. SORTED BY in Lakehouse can be used independently, indicating sorting within the file when used alone. Specifying SORTED BY can speed up data retrieval, but since sorting is required during writing, it may increase the time taken for writing.
```
CREATE TABLE sales_data (
    sale_id INT,
    product_id INT,
    quantity_sold INT,
    sale_date DATE
) 
SORTED BY (sale_date DESC);
```
### ROW FILTER (Row-Level Security)

> [Preview Release] This feature is currently in an invite-only preview. Contact our technical support team for assistance.

* **ROW FILTER**: Binds a filter function that returns `BOOLEAN` to a table. The system automatically applies it during queries and DML operations — only rows for which the function returns `true` are visible to the current operation. Commonly used for multi-tenant isolation and row-level data access control by user/role. The filter function can use security context functions such as `current_user()` and `current_roles()` to dynamically filter based on the current login identity. Columns listed in `ON (...)` are passed in order as arguments to the filter function; their types and count must match the function definition. It is recommended to reference filter functions using schema-qualified names. See [Row-Level Security (Row Filter)](row-filter.md).

```sql
-- Create a filter function: each user can only see rows where owner equals their login name
CREATE FUNCTION my_schema.owner_only(owner STRING) RETURNS BOOLEAN
AS owner = current_user();

-- Bind a row filter at table creation
CREATE TABLE my_schema.docs (
    id      INT,
    owner   STRING,
    content STRING
) ROW FILTER my_schema.owner_only ON (owner);
```

You can also bind or remove a row filter on an existing table using `ALTER TABLE ... SET ROW FILTER ...` and `ALTER TABLE ... DROP ROW FILTER`.

### PROPERTIES

You can set table-level properties via `PROPERTIES` at table creation time, and also modify them via `ALTER TABLE ... SET PROPERTIES`.

| Parameter | Description | Example Value |
|------|------|--------|
| `data_lifecycle` | Data lifecycle (days). Data older than the specified number of days is automatically expired and deleted. Suitable for time-sensitive data such as logs and transaction records. See [Data Lifecycle](data-lifecycle.md) | `'365'` |
| `data_retention_days` | Time Travel data retention period (days). Determines how long historical version data is retained, affecting the available window for Time Travel, Table Stream, and Dynamic Table. Default is 1 day | `'7'` |
| `change_tracking` | Enable Table Stream change tracking. **Note: specifying this at table creation time has no effect**; it must be enabled via the ALTER command | `'true'` |
| `partition.cache.policy.latest.count` | Cache the latest N partitions to the local SSD of the compute cluster. When new partitions are added, the cache of old partitions is automatically invalidated. Suitable for accelerating hot data in time-partitioned tables | `'10'` |

> ⚠️ **Note**: `change_tracking` does not take effect when specified at table creation time; it must be enabled via ALTER:
> ```sql
> ALTER TABLE table_name SET PROPERTIES ('change_tracking' = 'true');
> ```

```sql
-- Set lifecycle and Time Travel retention period at table creation
CREATE TABLE historical_prices (
    ticker_symbol STRING,
    trading_date  DATE,
    closing_price DECIMAL(10, 2)
) PROPERTIES (
    'data_lifecycle'      = '365',
    'data_retention_days' = '7'
);

-- Modify properties of an existing table
ALTER TABLE historical_prices SET PROPERTIES ('data_lifecycle' = '30');
ALTER TABLE historical_prices SET PROPERTIES ('partition.cache.policy.latest.count' = '10');

-- View current property settings of a table
SHOW PROPERTIES IN TABLE historical_prices;

-- Remove a property
ALTER TABLE historical_prices UNSET PROPERTIES ('data_lifecycle');
```

### Using LIKE Statement to Create a Table
```SQL
CREATE TABLE [ IF NOT EXISTS ] table_name
LIKE source_table
[ INCLUDING TBLPROPERTIES ]
[ COMMENT 'table_comment' ]
[ TBLPROPERTIES ('key'='value', ...) ];
```
When creating a new table using the LIKE statement, the target table will have the same table structure as the source table (column definitions, primary key, unique key, bucketing, sort key), but the data will not be copied. The source table's COMMENT is automatically copied to the new table unless the user explicitly specifies a new COMMENT.

By default, the source table's table properties (TBLPROPERTIES) are not copied. If you need to copy the source table's properties, use the `INCLUDING TBLPROPERTIES` clause. User-specified TBLPROPERTIES will override properties of the same name copied from the source table.

### Creating a Table Using the AS Statement

The CREATE TABLE AS SELECT (CTAS) statement can be used to query the original table synchronously or asynchronously, create a new table based on the query results, and then insert the query results into the new table. It should be noted that tables created in this way do not copy partition information.
```SQL
CREATE TABLE [ IF NOT EXISTS ] table_name
[ AS select_statement ];
```
## Example

1. Create a partitioned table

Syntax 1:
```SQL
CREATE TABLE table_part (id INT, name STRING)
PARTITIONED BY (age INT);
```
Syntax Two:
```SQL
CREATE TABLE table_fpart (id INT, name STRING, dt STRING)
PARTITIONED BY (dt) COMMENT '11';
```
2. Create a product table with an auto-increment column as a unique identifier
```sql
CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT IDENTITY(1) COMMENT 'Product ID',
    name VARCHAR(255) NOT NULL COMMENT 'Product Name',
    price DECIMAL(10, 2) NOT NULL COMMENT 'Price'
) COMMENT 'Product List';
```
3. Create a Timestamp Conversion Table with Generated Columns

```sql
CREATE TABLE IF NOT EXISTS timestamps (
    event_time TIMESTAMP COMMENT 'Event occurrence time',
    formatted_date STRING GENERATED ALWAYS AS (date_format(event_time, 'yyyy-MM-dd')) COMMENT 'Formatted date'
) PARTITIONED BY (formatted_date);
```
4. Create an activity record table with a default value of the current timestamp

```sql
CREATE TABLE IF NOT EXISTS activities (
    activity_id BIGINT NOT NULL COMMENT 'Activity ID',
    description VARCHAR(255) COMMENT 'Description',
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record Time'
) COMMENT 'Activity Records';
```
5. Create a Search Optimized Table with Bloom Filter Index
```sql
CREATE TABLE IF NOT EXISTS search_optimized (
    id BIGINT COMMENT 'ID',
    description VARCHAR(255) COMMENT 'Keyword',
    INDEX bloom_index (id) BLOOMFILTER COMMENT 'Bloom Filter Index'
) COMMENT 'Table for quick lookup';
```
6. Create a Text Analysis Table with an Inverted Index
```sql
CREATE TABLE IF NOT EXISTS text_analysis (
    doc_id BIGINT COMMENT 'Document ID',
    content TEXT COMMENT 'Content',
    INDEX inverted_content (content) INVERTED PROPERTIES ('analyzer' = 'chinese') COMMENT 'Inverted Index'
) COMMENT 'Table for text analysis';
```
7. Create a Sales Data Table with Bucketing and Sorting
```sql
CREATE TABLE IF NOT EXISTS sales_data (
    sale_id BIGINT COMMENT 'Sale ID',
    product_id BIGINT COMMENT 'Product ID',
    quantity_sold INT COMMENT 'Quantity Sold',
    sale_date DATE COMMENT 'Sale Date'
) CLUSTERED BY (product_id)
SORTED BY (sale_date DESC)
INTO 50 BUCKETS COMMENT 'Sales Data Table';
```
8. Create a data retention table with lifecycle management
```sql
CREATE TABLE IF NOT EXISTS historical_prices (
    ticker_symbol VARCHAR(10) COMMENT 'Ticker Symbol',
    trading_date DATE COMMENT 'Trading Date',
    closing_price DECIMAL(10, 2) COMMENT 'Closing Price'
) PROPERTIES (
    'data_lifecycle' = '365',
    'data_retention_days' = '1'
) COMMENT 'Historical Stock Prices Table';
```
9. Create a new table similar to the existing table structure

```sql
CREATE TABLE IF NOT EXISTS new_users LIKE users COMMENT 'New Users Table';
```
10. Create a Table Initialized by Query Results

```sql
CREATE TABLE IF NOT EXISTS recent_sales AS
SELECT * FROM sales WHERE sale_date >= DATE_SUB(CURRENT_DATE, 3);
```
11. Create an Order Details Table Containing Array Types

```sql
CREATE TABLE IF NOT EXISTS order_details (
    order_id BIGINT COMMENT 'Order ID',
    items ARRAY<STRUCT<item_id:BIGINT, quantity:INT, price:DECIMAL(10, 2)>> COMMENT 'Item List'
) COMMENT 'Order Details';
```
12. Create a Customer Feedback Table with JSON Type
```sql
CREATE TABLE IF NOT EXISTS customer_feedback (
    feedback_id BIGINT COMMENT 'Feedback ID',
    feedback JSON COMMENT 'Feedback Content'
) COMMENT 'Customer Feedback Table';
```
# User Guide

### Partitioning and Bucketing

* **Choosing a Partitioning Strategy**: Select appropriate partition fields based on the query pattern. Generally, columns that can effectively narrow the scan range should be chosen as partition keys. For example, a timestamp column is very suitable as a partition key for date range queries.

* **Setting the Number of Buckets**: The number of buckets should be adjusted based on the expected data volume and hardware resource configuration. Typically, each bucket size should be between 256MB and 1GB. Too many or too few buckets will affect the overall performance of the system. To achieve the best results, it is recommended to test the performance under different configurations and make appropriate adjustments accordingly.

* **Choosing Sorting Fields**: When using the `SORTED BY` clause, select columns that frequently appear in filter conditions as the sorting basis. Good sorting can help speed up point queries and range queries, but it also increases the write cost. Therefore, it is important to make a decision after weighing the pros and cons.

### Indexing

Users can create indexes on multiple columns when creating a table. Indexes can also be added after the table is created. If indexes are added during later use and the table already contains data, all data needs to be rewritten, so the time to create the index depends on the current data volume.

### Best Practices for Table Property Settings

* **Enable Data Lifecycle Management**: By setting the `data_lifecycle` property, the system can automatically clean up historical data that is no longer needed. This is very useful for saving storage, especially when dealing with datasets with a clear retention period, such as logs or transaction records.
* **Configure Change Tracking**: If your application scenario involves obtaining data changes in the table, you need to enable `change_tracking`. Common scenarios include [TABLE STREAM](tablestream_summary.md).

> ⚠️ **Note**: `CREATE OR REPLACE TABLE` resets associated Streams. Using `OR REPLACE` to rebuild a table clears the table's history, causing all Table Streams based on that table to immediately become stale and unable to retrieve complete change data. To modify the table structure, prefer using `ALTER TABLE`.

* **Set Data Retention Period for Deleted Data**: This parameter defines the length of time that deleted data is retained, which is very important for scenarios that require historical data queries. For example, features like [table stream](tablestream_summary.md), [restore](restore.md), and [dynamic table](sql_dynamic_table_guide.md) rely on this retention period setting. By default, Lakehouse retains data for one day. Depending on your business needs, you can adjust the `data_retention_days` parameter to extend or shorten the data retention period. Please note that adjusting the data retention period may affect storage costs. Extending the retention period will increase storage requirements, which may increase related costs.

## Related Guides

**Table Creation and Design**

| Document | Description |
|------|------|
| [SQL CREATE TABLE Usage Guide](sql_create_table_guide.md) | Complete guide for table creation options, column types, partitioning, sort columns, and property configuration |
| [Table Design Best Practices](lakehouse_table_design_guide.md) | Comprehensive selection recommendations for partitioning, bucketing, and indexing |
| [Generated Columns Usage Guide](generated_columns_guide.md) | Definition and usage scenarios for virtual and stored columns |
| [Data Types](data-type.md) | Descriptions and usage examples for all supported column types |

**Partitioning and Bucketing**

| Document | Description |
|------|------|
| [Partitioning and Bucketing](partition_table_guide.md) | Selection and design principles for partitioning and bucketing |
| [Partitioned Table Usage Guide](notes-and-guidelines-for-partition-tables.md) | Usage patterns for partition design, partition pruning, and dynamic partitions |
| [Bucketing (CLUSTERED BY)](cluster-table-guide.md) | Hash bucketing to improve Join and aggregation performance |
| [Primary Key](primary-key.md) | Primary key table design, supporting CDC real-time write deduplication |
| [Unique Key](unique-key.md) | Declarative UNIQUE constraint for query optimization |
| [Row-Level Security (Row Filter)](row-filter.md) | Bind a filter function to a table to control row-level data visibility |

**Indexing**

| Document | Description |
|------|------|
| [Bloomfilter Index](bloomfilter-summary.md) | Accelerate equality queries |
| [Inverted Index](inverted-index.md) | Full-text search acceleration, supports Chinese and English tokenization |
| [Vector Index](vector-search.md) | ANN approximate nearest neighbor retrieval |
| [Recommended Sort Columns for Tables](auto-index.md) | Accelerate range queries via sort columns |

**Advanced Table Features**

| Document | Description |
|------|------|
| [Data Lifecycle](data-lifecycle.md) | `data_lifecycle` parameter, automatically expire and delete historical data |
| [ALTER TABLE](alter-table.md) | Modify table structure, properties, partitions, and other operations |
| [Table Stream](tablestream_summary.md) | Capture incremental changes to a table based on `change_tracking` |
| [Time Travel](timetravel-summary.md) | `data_retention_days` parameter, query and restore historical data |
