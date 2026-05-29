# Delta Lake External Table

## DELTA LAKE

Delta Lake is an open-source big data framework that provides reliability and performance on data lakes. Built on top of Apache Spark and other big data processing engines, it introduces a structured storage layer for data stored in data lakes, making them as easy to use as a data warehouse. Singdata Lakehouse supports accessing Delta Lake format data through external tables.


## Creating a Delta Format External Table

[Create External Table Syntax](<create-external-table.md>)

### **Example**

```SQL
--Create a connection
CREATE STORAGE CONNECTION if not exists oss_delta
    TYPE oss
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
    access_id = 'xxx'
    access_key = 'xxxx'
    comments = 'delta';

--Create an external table using the connection above
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

## Dropping an External Table

```SQL
DROP TABLE [ IF EXISTS ] [schema_name.]<table_name>
```

**Parameter Description**

* `IF EXISTS`: Optional. If specified, no error is raised when the table does not exist.
* `schema_name`: Optional. Specifies the schema name. If not specified, the current user's schema is used by default.
* `table_name`: The name of the table to drop.

**Notes**

* Dropping an external table does not delete the underlying data, because the data is stored in an external system. The drop operation only removes the table's mapping metadata.

**Example**

```SQL
--Drop an existing external table
DROP TABLE sales_data;
--Drop the table named sales_data; no error if the table does not exist:
DROP TABLE IF EXISTS sales_data;
--Drop the sales_data table under the schema my_schema
DROP TABLE my_schema.my_table;
```

## Viewing External Table Details

```SQL
DESC[RIBE] [TABLE] [EXTENDED] table_name;
```

**Parameter Description**

* **DESC\[RIBE]**: `DESC` and `DESCRIBE` are interchangeable; both describe the table structure.
* **TABLE**: Optional. Specifies the type of object to describe, such as `BASE TABLE` or `VIEW`.
* **EXTENDED**: Optional. When included, additional extended information is displayed, such as the table's creation statement and Location.
* **table\_name**: The name of the table whose structure you want to view.

## Modifying an External Table

### Renaming a Table

You can use the `ALTER TABLE` command to rename an existing table.

**Syntax**

```SQL
ALTER TABLE name RENAME TO new_table_name;
```

**Example**

```SQL
ALTER TABLE old_table_name RENAME TO new_table_name;
```

### Modifying Table Comments

You can use the `ALTER TABLE` command to add or update a comment on a table.

**Syntax**

```SQL
ALTER TABLE tbname SET COMMENT '';
```

**Example**

```SQL
ALTER TABLE scores SET COMMENT 'This is a scores table';
```

## **External Table Billing**

* **Storage cost**: External tables do not incur storage costs because the data is not stored in Singdata Lakehouse.
* **Compute cost**: Querying an external table consumes compute resources and therefore incurs compute costs.

## **External Table Permissions**

External tables share the same permission model as internal tables. Because external tables do not support `INSERT`, `UPDATE`, `TRUNCATE`, `DELETE`, or `UNDROP` operations, there are no corresponding permission points for those operations.

* **Create permission**: Requires the `create table` privilege.
* **Drop permission**: Requires the `DROP` privilege.
* **Read permission**: Requires the `SELECT` privilege.

## **Usage Notes**

* **Connection configuration**: When creating a connection, make sure the `endpoint` is configured correctly so that Singdata Lakehouse can connect successfully. If Singdata Lakehouse and the object storage are in the same cloud service and the same region, you can typically use the internal network address for connectivity. If they are in different network environments, use the public endpoint of the object storage.

## Examples

### Connecting to Alibaba Cloud OSS

```SQL
--Create a connection to object storage
CREATE STORAGE CONNECTION  oss_delta
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com'
    access_id = 'xxxxxx'
    access_key = 'xxxxxx'
    comments = 'delta'
    ;
--Create an external table using the connection above
CREATE    EXTERNAL TABLE pepole_delta (id int, name string,dt string) 
USING DELTA 
CONNECTION oss_delta 
PARTITIONED BY (dt ) 
LOCATION 'oss://bucketmy/delta-format/uploaddelta/' 
COMMENT 'edelta-external';
```

### Connecting to Google GCS

When Singdata Lakehouse connects to Google Cloud Storage (GCS), it uses a service account key for authentication. Follow the steps below:

1. **Obtain the service account key**:

   - Log in to the Google Cloud Console.
   - Follow the *[Google Cloud documentation](https://cloud.google.com/docs/authentication/getting-started)* to create and download a JSON key file for your service account.

2. **Configure the `private_key` parameter**:

   - Open the downloaded JSON key file and copy the full private key content.

3. **Note**:

   - When configuring `private_key`, you must prefix the value with `r`. The `r` prefix means the string is treated as a raw string, so special characters and Unicode characters will not be escaped.

```SQL
--Create a connection to object storage
CREATE STORAGE CONNECTION  oss_delta
    TYPE gcs
    private_key=r'{
  "type": "service_account",
  "project_id": "PROJECT_ID",
  "private_key_id": "KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nPRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "SERVICE_ACCOUNT_EMAIL",
  "client_id": "CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
}';
--Create an external table using the connection above
CREATE    EXTERNAL TABLE pepole_delta (id int, name string,dt string) 
USING DELTA 
CONNECTION oss_delta 
PARTITIONED BY (dt ) 
LOCATION 'gs://bucketmy/delta-format/uploaddelta/' 
COMMENT 'edelta-external';
```
