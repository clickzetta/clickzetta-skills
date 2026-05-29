# Create External Table

## **OVERVIEW**

The external table feature allows Lakehouse to query and analyze data stored in external storage systems such as object storage. Users can directly manipulate external data without the need to import data into Lakehouse's internal storage, providing flexibility and convenience for data processing.

## Supported Scope

* Supports Alibaba Cloud Object Storage OSS, Tencent Cloud Object Storage COS, Google Cloud Object Storage GCS, and AWS Object Storage S3.
* Currently, only supports Delta Lake format.

## **Syntax**

```SQL
CREATE EXTERNAL TABLE [ IF NOT EXISTS ] table_name
(
  column_definition [, column_definition, ...]
)
[PARTITIONED BY (col_name col_type [, col_name col_type, ...])]
USING DELTA|HUDI
CONNECTION connection_name
LOCATION 'file_path'
[COMMENT 'table_comment']
```

## **Parameter Description**

**Required Parameters**:

* `CREATE EXTERNAL TABLE`: Declares the creation of an external table.

* `table_name`: The name of the external table.

* `column_definition`: Column definition, specifying the name and data type of the column.

* `USING DELTA`: Currently, the supported file formats include Delta Lake and Hudi.

* `CONNECTION connection_name`: Authentication information for connecting to an external data source. `connection_name` is the name of the connection object defined in Lakehouse. It is used for authentication connection information and connecting to the object storage.

* `LOCATION 'file_path'`: Specifies the path of the data file to be read, supporting various cloud storage path formats.

  * Google Cloud object storage format: gs://bucketname/path
  * Tencent Cloud object storage format: cos://bucketname/path
  * Alibaba Cloud object storage format: oss://bucketname/path
  * AWS object storage supports Alibaba Fish object storage format: s3://bucketname/path

**Optional Parameters**:

* `IF NOT EXISTS`: If the external table does not exist, create it; if it already exists, do nothing.
* `PARTITIONED BY (col_name col_type [, col_name col_type, ...])`: Specifies partition columns and their data types for data partitioning.
* `COMMENT 'table_comment'`: Provides a descriptive comment for the external table.

## **Example**

```SQL
-- Create a connection
CREATE STORAGE CONNECTION if not exists oss_delta
    TYPE oss
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
    access_id = 'xxx'
    access_key = 'xxxx'
    comments = 'delta';

-- Create an external table using the above connection information
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