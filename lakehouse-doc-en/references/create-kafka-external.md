# Create DELTA and HUDI External Tables

## Description

The external table feature allows Lakehouse to query and analyze data stored in external storage systems such as object storage. Users can directly operate on external data without importing it into Lakehouse's internal storage, providing flexibility and convenience in data processing.

**Other commands for external tables**:

* **Delete external table**: Delete an external table using the `DROP TABLE` syntax.
* **View external table details**: Use the `DESC TABLE` syntax to quickly view the structure and details of an external table.
* **Modify external table**: Modify an external table using `ALTER TABLE`.
* **View external table creation statement**: Use the `SHOW CREATE TABLE` statement.
* **Reference cases**: For specific operations on external tables, refer to the [Delta Lake](delta-lake.md) external table usage guide.

## Supported Scope

* Supports Alibaba Cloud Object Storage OSS, Tencent Cloud Object Storage COS, and AWS Object Storage S3.

## **Syntax**
```SQL
CREATE EXTERNAL TABLE [ IF NOT EXISTS ] table_name
(
  column_definition [, column_definition, ...]
)
[PARTITIONED BY (col_name col_type [, col_name col_type, ...] )]
USING DELTA|HUDI
CONNECTION connection_name
LOCATION 'file_path'
[COMMENT 'table_comment']
```
## **Parameter Description**

**Required Parameters**:

* `CREATE EXTERNAL TABLE`: Declare the creation of an external table.

* `table_name`: The name of the external table.

* `column_definition`: Column definition, specifying the name and data type of the column. It must be consistent with the types and names in delta and hudi. Refer to the [data types](data-type.md) supported by Lakehouse.

* `USING DELTA|HUDI`: Specify the file format, currently supporting Delta Lake and Hudi formats.

* `CONNECTION connection_name`: Authentication information for connecting to an external data source, where `connection_name` is the name of the connection object defined in Lakehouse. It is used for authentication connection information and connection object storage. For specific creation documentation, refer to [Object Storage Connection (STORAGE CONNECTION)](Datalake_StorageConnection.md).
  * Create oss connection
  ```
  CREATE STORAGE CONNECTION my_conn 
    TYPE COS
    ACCESS_KEY = '<access_key>'
    SECRET_KEY = '<secret_key>'
    REGION = 'ap-shanghai'
    APP_ID = '1310000503';
  ```
* Create cos connection
  ```
  CREATE STORAGE CONNECTION my_conn 
    TYPE COS
    ACCESS_KEY = '<access_key>'
    SECRET_KEY = '<secret_key>'
    REGION = 'ap-shanghai'
    APP_ID = '1310000503';
  ```
* Create s3 connection
  ```
  CREATE STORAGE CONNECTION aws_bj_conn
      TYPE S3
      ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
      SECRET_KEY = '7kfheDrmq***************************'
      ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
      REGION = 'cn-north-1';
  ```
* `LOCATION 'file_path'`: Use the `LOCATION 'file_path'` directive to specify the path of the data file to be read, supporting multiple cloud storage formats. For Delta Lake tables, the external table will scan the transaction log files in that location (such as `_delta_log/00000000000000000000.json` or `_delta_log/00000000000000000010.checkpoint.parquet`) to determine the latest Parquet files.
  * file\_path is a case-sensitive string representing the location or prefix (i.e., folder) of the files in cloud storage, used to limit the set of files to be loaded. Tencent Cloud Object Storage (COS): cos\://bucketname/path, Alibaba Cloud Object Storage (OSS): oss//bucketname/path, AWS S3 Object Storage: s3://bucketname/path

  * The path specified in file\_path must contain only the data files and metadata of a single Delta Lake or Hudi table. That is, each storage location can only correspond to one directory.

  * When reading data from file\_path, the permissions and authentication information in the connection will be used. Authorization for GetObject, ListObjects, PutObject, and DeleteObject permissions is required.

  * Each read will re-parse the Delta Lake transaction log to ensure the latest metadata is obtained. Therefore, metadata will not be cached.

**Optional Parameters**:

* `IF NOT EXISTS`: Creates the external table if it does not exist; if it already exists, no action is taken.
* `PARTITIONED BY (col_name col_type [, col_name col_type, ...])`: Specifies the partition columns and their data types for data partitioning. If DELTA and HUID are partitioned tables, this must be specified.
* `COMMENT 'table_comment'`: Provides a descriptive comment for the external table.

## Usage Instructions

* External tables cannot access archived files; these data need to be restored before they can be retrieved.
* External tables do not support TIME TRAVEL.
* Deleting an external table only deletes the definition of the external table, not the files in object storage.

## **Examples**

1. Create a delta external table on OSS
Step 1: Create an OSS connection. Refer to the specific documentation [Tencent Cloud Storage Connection Creation](cos_storage_connection.md)
Step 2: Create an external table and specify the location of the external table
```SQL
--Create connection
CREATE STORAGE CONNECTION if not exists oss_delta
    TYPE oss
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
    access_id = 'xxx'
    access_key = 'xxxx'
    comments = 'delta';

--Create external table using the above connection information
CREATE EXTERNAL TABLE IF NOT EXISTS sales_data
(
  order_id INT,
  product_id STRING,
  sale_amount DOUBLE
)
PARTITIONED BY (dt STRING)
USING DELTA
CONNECTION oss_delta
LOCATION 'oss://my-bucket/data/sales'
COMMENT 'External table for sales data stored in OSS';
```

2. Create Delta External Table on COS
 Step 1: Create a COS connection. Refer to the specific documentation [Aliyun Storage Connection Creation](aliyun_storage_connection.md)

Step 2: Create an external table and specify the location of the external table
```
```SQL
--Create connection
CREATE STORAGE CONNECTION my_conn 
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';

--Create external table using the above connection information
CREATE EXTERNAL TABLE IF NOT EXISTS sales_data
(
  order_id INT,
  product_id STRING,
  sale_amount DOUBLE
)
PARTITIONED BY (dt STRING)
USING DELTA
CONNECTION oss_delta
LOCATION 'cos://cz-volume-sh-1311343935/sales';
```
3. Create Delta External Table on S3
 3.1 Create a COS Connection
Step 1: You need to create a COS connection. Refer to the specific documentation [Amazon Cloud Storage Connection Creation](aws_storage_connection.md)

3.2 Create an External Table and Specify the Location of the External Table
```
CREATE STORAGE CONNECTION aws_bj_conn
    TYPE S3
    ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
    SECRET_KEY = '7kfheDrmq***************************'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';


CREATE EXTERNAL TABLE IF NOT EXISTS sales_data
(
  order_id INT,
  product_id STRING,
  sale_amount DOUBLE
)
PARTITIONED BY (dt STRING)
USING DELTA
CONNECTION oss_delta
LOCATION 's3://cz-udf-user/sales'
COMMENT 'External table for sales data stored in OSS';

```

# Create Kafka External Table

First, you need to create a storage connection to connect to the Kafka server. Before connecting, ensure that your Kafka and Lakehouse networks are connected. For network connection methods, refer to [Private Link](private_link.md). This article introduces how to create a Kafka storage connection and a Kafka external table.

**Other commands for external tables**:

* **Delete external table**: Use the `DROP TABLE` syntax to delete the external table.
* **View external table details**: Use the `DESC TABLE` syntax to quickly view the structure and detailed information of the external table.
* **Modify external table**: Modify the external table using `ALTER TABLE`.
* **View external table creation statement**: Use the `SHOW CREATE TABLE` statement.
* **Reference cases**: For specific operations on external tables, refer to the external table usage guide for [Delta Lake](delta-lake.md).

## Create Kafka Storage Connection

### Syntax
```SQL
CREATE STORAGE CONNECTION connection_name
    TYPE kafka
    BOOTSTRAP_SERVERS = ['server1:port1', 'server2:port2', ...]
    SECURITY_PROTOCOL = 'PLAINTEXT';
```
### Parameter Description

* **connection\_name**: The name of the connection, used for subsequent references.
* **TYPE**: The type of connection, here it is `kafka`.
* **BOOTSTRAP\_SERVERS**: The address list of the Kafka cluster, formatted as `['host1:port1', 'host2:port2', ...]`.
* **SECURITY\_PROTOCOL**: Security protocol, currently only supports `PLAINTEXT`. **SSL** or **SASL\_SSL** are not supported.

### Example
```SQL
CREATE STORAGE CONNECTION test_kafka_conn
    TYPE kafka
    BOOTSTRAP_SERVERS = ['47.99.48.62:9092']
    SECURITY_PROTOCOL = 'PLAINTEXT';
```
## Create Kafka External Table

After creating the storage connection, you can define an external table to read data from Kafka.

### Syntax
```SQL
CREATE EXTERNAL TABLE IF NOT EXISTS external_table_name (
 `topic` string,
 `partition` int,
 `offset` bigint,
 `timestamp` timestamp_ltz,
 `timestamp_type` string,
`headers` map<string, string>,
 `key` binary, `value` binary)
USING kafka
CONNECTION connection_name;
OPTIONS (
    'group_id' = 'consumer_group',
    'topics' = 'topic_name',
    'starting_offset' = 'earliest',  -- Optional, default value is earliest
    'ending_offset' = 'latest',      -- Optional, default value is latest
    'cz.kafka.seek.timeout.ms' = '2000', -- Kafka default value
    'cz.kafka.request.retry.times' = '1', -- Kafka default value
    'cz.kafka.request.retry.intervalMs' = '2000' -- Kafka default value
) 
```
### Parameter Description

* **external\_table\_name**: The name of the external table.
* **Field Description**

| Field            | Meaning                                                                            | Type                   |
| ---------------- | ---------------------------------------------------------------------------------- | ---------------------- |
| topic            | Kafka topic name                                                                   | STRING                 |
| partition        | Data partition ID                                                                  | INT                    |
| offset           | Offset in the Kafka partition                                                      | BIGINT                 |
| timestamp        | Kafka message timestamp                                                            | TIMESTAMP\_LTZ         |
| timestamp\_type  | Kafka message timestamp type                                                       | STRING                 |
| headers          | Kafka message headers                                                              | MAP\<STRING, BINARY>   |
| key              | Column name of the message key, type is `binary`. You can convert the binary type to a readable string using type conversion methods such as `cast(key_column as string)` | BINARY                 |
| value            | Column name of the message body, type is `binary`. You can convert the binary type to a readable string using type conversion methods such as `cast(key_column as string)` | BINARY                 |

* **USING kafka**: Specify using Kafka as the data source.
* **OPTIONS**:
  * **group\_id**: Kafka consumer group ID.
  * **topics**: Kafka topic name.
  * **starting\_offset**: Starting offset, default is earliest, can be `earliest` or `latest`.
  * **ending\_offset**: Ending offset, default is `latest`, can be `earliest` or `latest`.
  * **cz.kafka.seek.timeout.ms**: Kafka seek timeout (milliseconds).
  * **cz.kafka.request.retry.times**: Kafka request retry times.
  * **cz.kafka.request.retry.intervalMs**: Kafka request retry interval time (milliseconds).
* **CONNECTION**: Specify the previously created storage connection name.

## Usage Example
```
CREATE storage connection test_kafka_conn 
TYPE kafka 
bootstrap_servers = [
'1.1.1.1:9092,1.1.1.1:9092,1.1.1.1:9092'
];

CREATE    EXTERNAL TABLE IF NOT EXISTS test_kafka_table (
          `topic` string,
          `partition` int,
          `offset` bigint,
          `timestamp` timestamp_ltz,
          `timestamp_type` string,
          `headers` map < string,string >,
          `key` binary,
          `value` binary
          ) USING kafka OPTIONS (
          'topics' = 'topic_test_kafka_pipe_loading',
          'group_id' = 'group_test_kafka_pipe_loading'
          ) connection test_kafka_conn;

-- Query data
SELECT    cast(key AS string),
          cast(value AS string)
FROM      test_kafka_table
LIMIT     10;

-- Convert to JSON to extract a specific field
SELECT    cast(key AS string),
          parse_json (cast(value AS string)) ['id'] AS id,
          parse_json (cast(value AS string)) ['id'] AS name
FROM      test_kafka_table
LIMIT     10;
```


