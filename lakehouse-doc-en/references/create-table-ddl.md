# CREATE TABLE

## Description

This statement is used to create a new table. In the Lakehouse, a table is the basic unit for storing data. By creating a table, you can organize and manage data according to a specified structure.

## Syntax
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
[ COMMENT 'table_comment' ]
[PROPERTIES('data_lifecycle'='day_num')];


```
### column\_definition Description

#### Syntax
```
column_name column_type 
{ NOT NULL |
  PRIMARY KEY|
  IDENTITY[(seed)]|
  GENERATED ALWAYS AS ( expr ) |
  DEFAULT default_expression |
  COMMENT column_comment |   
}
```
#### Column Type column\_type

* **column\_type** Column type, supports the following types:
```SQL
TINYINT: 1-byte integer, range -128 to 127.
SMALLINT: 2-byte integer, range -32,768 to 32,767.
INT: 4-byte integer, range -2,147,483,648 to 2,147,483,647.
BIGINT: 8-byte integer, range -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807.
FLOAT: 4-byte floating point number.
DOUBLE: 8-byte floating point number.
DECIMAL: Variable-length exact numeric type, supports specified precision and scale.
VARCHAR: Variable-length string, maximum length limit is 65,533 characters.
CHAR: Fixed-length string, length range from 1 to 255 characters.
DATE: Date, format is YYYY-MM-DD.
DATETIME: Date and time, format is YYYY-MM-DD HH:MM:SS.
BINARY: Fixed-length binary string.
BOOLEAN: Boolean value, true or false.
ARRAY: Ordered collection of elements of the same type. For example: ARRAY<INT>
MAP: Collection of key-value pairs, keys must be of the same type, values can be of the same or different types. For example: MAP<STRING,INT>
STRUCT: Record type with fields of different types. For example: struct<company_name:string,employee_count:int>
JSON: A lightweight data interchange format.
VECTOR: Numeric vector type, used to store a series of numbers.
```
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

* **PRIMARY KEY**: In the Lakehouse architecture, for tables with a defined primary key, the system will automatically deduplicate data based on the primary key value during real-time data ingestion. Once a primary key is set, you will not be able to perform insert, delete, or update operations through SQL statements, nor can you add or remove columns. You need to handle data through the [real-time data interface](java_reference/realtime-upload.md). This can only be specified when creating the table. For more details, refer to the [Primary Key Introduction](primary-key.md).
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
#### Auto-increment Column (IDENTITY\[(seed)])

* **IDENTITY\[(seed**)]: Supports specifying auto-increment. It cannot guarantee that the values in the sequence are continuous (gapless), nor can it guarantee that the sequence values are allocated in a specific order. This is because other concurrent inserts may occur in the table. These limitations are part of the design to improve performance. For specific usage, refer to the [IDENTITY Column documentation](IDENTITY-Column.md)
```
CREATE    TABLE identity_test (id bigint IDENFIRY(1), col string);
```
#### Generated Columns (GENERATED ALWAYS AS)

* **GENERATED ALWAYS AS (expr)**: Automatically generates the value of a column through the expression `expr`. The expression can include constants and built-in scalar deterministic SQL functions. Non-deterministic functions such as (current\_date, random, current\_timestamp, context functions) or operators are not supported. Aggregate functions, window functions, or table functions are also not supported. Partition columns using generated columns are supported.
```
CREATE TABLE t_genet (col1 TIMESTAMP,pt STRING GENERATED ALWAYS AS (date_format(col1, 'yyyy-MM-dd'))) PARTITIONED BY (pt);
```
#### Default Values (DEFAULT)

* **DEFAULT default\_expression**: Defines a default value for a newly added column. If the value of this column is not specified in INSERT, UPDATE, or MERGE operations, this default value will be automatically used. For data rows that existed before the column was added, the column will be filled with null. Supports non-deterministic functions such as (current\_date\random\current\_timestamp\context functions) and constant values.
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

**index\_type**: Index type, currently supports [bloomfilter](CREATE-BLOOMFILTER-INDEX.md), [inverted](inverted-index.md), [vector](create-vector-index.md)

**COMMENT**: Specifies the description information of the index

**PROPERTIES**: Specifies the parameters of the INDEX, different indexes support different parameters, refer to the corresponding index documentation for details

### Partitioned By (PARTITIONED BY) {#partitioned-by}

Partitioning is a method of speeding up queries by grouping similar rows together at the time of writing. Using partitioning can achieve data pruning and optimize queries. When querying a table, use the WHERE clause to query the specified partition to avoid full table scans, improve processing efficiency, and reduce computing resources. For details, refer to [Partition Introduction](partition_table.md)
Two writing methods are supported
The first method declares the partition fields and types when creating the table, just declare the fields in the PARTITIONED BY clause
```SQL
CREATE TABLE prod.db.sample (
id bigint,
category string，
data string,
)
PARTITIONED BY(category)
```
The second type of partition field and type is written in the PARTITIONED BY statement.
```SQL
CREATE TABLE prod.db.sample (
id bigint,
data string,
category string)
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
### PROPERTIES

* Supports setting the lifecycle 'data\_lifecycle'='day\_num' [Refer to lifecycle introduction](data-lifecycle.md)
* Enabling [TABLE STREAM](tablestream_summary.md), specifying 'change\_tracking' = 'true' when creating a table will not take effect, please use alter to enable it
  ALTER table test\_table set PROPERTIES ('change\_tracking' = 'true');
* Set the table's caching policy. partiton.cache.policy.latest.count=num sets the table's caching policy. The computing cluster can configure `preload_table` to periodically or be triggered to pull the table data specified in `preload_table` to the local SSD hard drive of the computing cluster for caching. You can also set the caching policy on the table.
  For example, `partition.cache.policy.latest.count=10` means caching the latest 10 partitions. When new partitions are added, the cache of old partitions will become invalid. This parameter can also be added via the alter command.
  For example, ALTER table test\_table set PROPERTIES ('partition.cache.policy.latest.count' =10);
* Set the table's retention period 'data\_retention\_days'='num', configure the data retention period for Time Travel to determine the length of time data is retained in the time travel window.
```
-- Set data lifecycle and data retention period for table deletion
CREATE TABLE historical_prices (
    ticker_symbol STRING,
    trading_date DATE,
    closing_price DECIMAL(10, 2)
) PROPERTIES (
    'data_lifecycle' = '365',
    'data_retention_days' = '7'
);
-- Modify the lifecycle of an existing table
ALTER TABLE historical_prices SET PROPERTIES(    'data_lifecycle' = '1')
```
### Using LIKE Statement to Create a Table
```SQL
CREATE TABLE [ IF NOT EXISTS ] table_name
LIKE source_table
[ COMMENT 'table_comment' ];
```
When creating a new table using the LIKE statement, the target table will have the same table structure as the source table, but the data will not be copied.

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
```markdown
4. Create an activity record table with a default value of the current timestamp
```
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
```markdown
6. Create a Text Analysis Table with an Inverted Index
```
```sql
CREATE TABLE IF NOT EXISTS text_analysis (
    doc_id BIGINT COMMENT 'Document ID',
    content TEXT COMMENT 'Content',
    INDEX inverted_content (content) INVERTED PROPERTIES ('analyzer' = 'chinese') COMMENT 'Inverted Index'
) COMMENT 'Table for text analysis';
```
```markdown
7. Create a Sales Data Table with Bucketing and Sorting
```
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
```markdown
8. Create a data retention table with lifecycle management
```
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
```markdown
12. Create a Customer Feedback Table with JSON Type
```
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
* **Set Data Retention Period for Deleted Data**: This parameter defines the length of time that deleted data is retained, which is very important for scenarios that require historical data queries. For example, features like [table stream](tablestream_summary.md), [restore](restore.md), and [dynamic table](dynamic-table-introduce.md) rely on this retention period setting. By default, Lakehouse retains data for one day. Depending on your business needs, you can adjust the `data_retention_days` parameter to extend or shorten the data retention period. Please note that adjusting the data retention period may affect storage costs. Extending the retention period will increase storage requirements, which may increase related costs.