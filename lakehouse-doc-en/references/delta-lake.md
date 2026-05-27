## DELTA LAKE
Delta Lake is an open-source big data framework that provides reliability and performance on data lakes. It is built on top of Apache Spark and other big data processing engines, offering a structured storage layer for data stored in data lakes, making data lakes as easy to use as data warehouses. Lakehouse provides a way to access this format data through external tables.

## Create External Table in DELTA Format

[Create External Table Syntax](<create-external-table.md>)

### **Example**
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
## Delete External Table
```SQL
DROP TABLE [ IF EXISTS ] [schema_name.]<table_name>
```
**Parameter Description**

* `IF EXISTS`: Optional, if the specified table does not exist, the system will not report an error.
* `schema_name`: Optional, specifies the name of the schema. If not specified, the current user's schema is used by default.
* `table_name`: The name of the table to be deleted.

**Description**

* Deleting an external table will not delete the data, as the data is stored in an external system. Deleting will only remove the table's mapping information.

**Example**
```SQL
-- Delete the already created external table
DROP TABLE sales_data;
-- Delete the table named sales_data, if the table does not exist, do not report an error:
DROP TABLE IF EXISTS sales_data;
-- Delete the sales_data table under the schema named my_schema
DROP TABLE my_schema.my_table;
```
## View External Table Details
```SQL
DESC[RIBE] [TABLE] [EXTENDED] table_name;
```
**Parameter Description**

* **DESC\[RIBE]**: DESC and DESCRIBE can be used interchangeably, both representing the command to describe the table structure.
* **TABLE**: Optional parameter, used to specify the type of table structure to view, such as BASE TABLE or VIEW, etc.
* **EXTENDED**: Optional parameter, adding this keyword can display more extended information, such as the table creation statement and Location information, etc.
* **table\_name**: Specifies the name of the table whose structure needs to be viewed.

## Modify External Table

### Rename Table

You can rename an existing table to a new table name using the ALTER TABLE command.

**Syntax**
```SQL
ALTER TABLE name RENAME TO new_table_name;
```
**Example**
```SQL
ALTER TABLE old_table_name RENAME TO new_table_name;
```
### Modify Table Comments

Using the ALTER TABLE command, you can add or modify comments for a table.

**Syntax**
```SQL
ALTER TABLE tbname SET COMMENT '';
```
**Example**
```SQL
ALTER TABLE scores SET COMMENT 'This is a scores table';
```
## **External Table Billing**

* **Storage Fees**: External tables do not incur storage fees because the data is not stored in the Lakehouse.
* **Computation Fees**: Using external tables for computation will consume computational resources, thus incurring computation fees.

## **External Table Permissions**

External tables have the same permission points as internal tables. Operations such as insert\update\truncate\delete\undrop cannot be performed externally, so there are no corresponding operations.

* **Creation Permission**: Requires permission to create tables (create table).
* **Deletion Permission**: Requires permission to delete (drop).
* **Read Permission**: Requires permission to select (select).

## **Usage Notes**

* **Connection Configuration**: When creating a connection, ensure the endpoint is configured correctly so that the Lakehouse can connect successfully. If the Lakehouse and the object storage are in the same cloud service and in the same region, usually an internal network address can be used to achieve network connectivity. If they are not in the same network environment, it is recommended to use the public address of the object storage.

## Specific Cases

### Connecting to Alibaba Cloud Oss
```SQL
--Create connection for object storage
CREATE STORAGE CONNECTION  oss_delta
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com'
    access_id = 'xxxxxx'
    access_key = 'xxxxxx'
    comments = 'delta'
    ;
--Create external table using the above connection information
CREATE    EXTERNAL TABLE pepole_delta (id int, name string,dt string) 
USING DELTA 
CONNECTION oss_delta 
PARTITIONED BY (dt ) 
LOCATION 'oss://bucketmy/delta-format/uploaddelta/' 
### Connect to Google GCS

When Lakehouse connects to Google Cloud Storage (GCS), it uses a service account key for authentication. Please follow the steps below:

1. **Obtain the service account key**:

   - Log in to the Google Cloud Console.
   - Follow the instructions in the *[Google Cloud documentation](https://cloud.google.com/docs/authentication/getting-started)* to create and download the JSON key file for the service account.

2. **Configure the ****`private_key`**** parameter**:

   - Open the downloaded JSON key file and copy the entire content of the private key.

3. **Note**:

   - When configuring the `private_key`, you must add an 'r' at the beginning. The 'r' indicates that the string is case-sensitive, and special characters and unicode characters will not be escaped.
```SQL
-- Create connection for connecting to object storage
CREATE STORAGE CONNECTION oss_delta
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
-- Use the above connection information to create an external table
CREATE EXTERNAL TABLE pepole_delta (id int, name string, dt string) 
USING DELTA 
CONNECTION oss_delta 
PARTITIONED BY (dt) 
LOCATION 'gs://bucketmy/delta-format/uploaddelta/' 
COMMENT 'edelta-external';
```