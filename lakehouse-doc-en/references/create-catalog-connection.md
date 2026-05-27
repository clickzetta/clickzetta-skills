# Create Catalog Connection
Catalog Connection is a key component used to manage connection information with third-party Catalogs. Its core function is to provide access authentication for External Catalogs, ensuring that the Lakehouse platform can securely and seamlessly access and manage data resources in storage services.
# Supported Catalogs
- Hive Catalog: By connecting to the Hive Metastore, or metadata services compatible with Hive Metastore, Lakehouse can automatically retrieve Hive's database and table information and perform data queries.
- Databricks Unity Catalog: Unity Catalog is Databricks' unified governance solution for data and AI assets. In Unity Catalog, all metadata is registered in the metastore. The hierarchy of database objects in any Unity Catalog metastore is divided into three levels, and when you reference tables, views, volumes, models, and functions, they are represented as a three-level namespace. By connecting to Databricks' Unity Catalog, Lakehouse can automatically retrieve Databricks' database and table information and perform data queries.

# Create Hive Catalog Syntax
```SQL
CREATE CATALOG CONNECTION if not exists connection_name
    type hms
    hive_metastore_uris='metastore_uris'
    storage_connection='storage_connection';
```
**Parameter Description**

* **connection\_name**: The name of the connection, which must be unique.
* **type**: The type of connection, here it is `hms` (Hive Metastore Service).
* **hive\_metastore_uris**: The service address of the Hive Metastore, in the format `host:port`. The port is usually 9083.
* **storage_connection**: The name of the created storage connection, used to access object storage or HDFS services. For details, refer to [CREATE STORAGE CONNECTION](<create-storage-connection.md>).

## Steps to Create Hive Catalog Connection

1. **Create Storage Connection**: First, you need to create a storage connection to access the object storage service. The user specifies the location of the hive data storage, currently only object storage oss, cos, s3 are supported.
2. **Create Catalog Connection**: Use the storage connection information and Hive Metastore address to create a Catalog Connection.

### Create Storage Connection
```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss    type OSS    ACCESS_ID='LTAIxxxxxxxxxxxx'    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'    ENDPOINT='oss-cn-hangzhou-internal.aliyuncs.com';
```
### Create Catalog Connection
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    type hms    hive_metastore_uris='47.95.221.23:9083'    storage_connection='catalog_storage_oss';
```
### Case Studies
Case Study 1: Hive ON OSS
- Create a storage connection
```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss   
 type OSS    
 ACCESS_ID='LTAIxxxxxxxxxxxx'    
 ACCESS_KEY='T8Gexxxxxxmtxxxxxx'   
 ENDPOINT='oss-cn-hangzhou-internal.aliyuncs.com';
```
- Create Catalog Connection
Please ensure that the network between the server where HMS is located and the Lakehouse is connected. For specific connection methods, please refer to [Creating Alibaba Cloud Endpoint Service](<creating_alicloud_privatelinkservice.md>)
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_oss';
```
Case 2: Hive ON COS
- Create Storage Connection
```sql
CREATE STORAGE CONNECTION catalog_storage_cos 
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';
```
**Parameters**:
    * **TYPE**: The object storage type, for Tencent Cloud, fill in `COS` (case insensitive)
    * **ACCESS\_KEY / SECRET\_KEY**: The access keys for Tencent Cloud, refer to: [Access Keys](https://cloud.tencent.com/document/product/598/40488)
    * **REGION**: Refers to the region where Tencent Cloud Object Storage COS data center is located. When Singdata Lakehouse accesses Tencent Cloud COS within the same region, the COS service will automatically route to internal network access. For specific values, please refer to Tencent Cloud documentation: [Regions and Access Domains](https://cloud.tencent.com/document/product/436/6224).

- Create Catalog Connection
Please ensure the network between the server where HMS is located and Lakehouse is connected. For specific connection methods, refer to [Creating Tencent Cloud PrivateLink Service](<creating_tencentcloud_privatelinkservice.md>)
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_cos';
```
Case Three: Hive ON S3
- Create a storage connection
```
CREATE STORAGE CONNECTION catalog_storage_s3
    TYPE S3
    ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
    SECRET_KEY = '7kfheDrmq***************************'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';
```
**Parameters**:
* TYPE: The object storage type, AWS should be filled in as S3 (case insensitive)
* ACCESS\_KEY / SECRET\_KEY: The access key for AWS, refer to: [Access Keys](https://docs.aws.amazon.com/zh_cn/IAM/latest/UserGuide/id_credentials_access-keys.html) for how to obtain it
* ENDPOINT: The service address for S3, AWS China is divided into Beijing and Ningxia regions. The service address for S3 in the Beijing region is `s3.cn-north-1.amazonaws.com.cn`, and for the Ningxia region is `s3.cn-northwest-1.amazonaws.com.cn`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html) to find the endpoints for the Beijing and Ningxia regions -> Amazon S3 corresponding endpoints
* REGION: AWS China is divided into Beijing and Ningxia regions. The region values are: Beijing region `cn-north-1`, Ningxia region `cn-northwest-1`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html)

- Create Catalog Connection
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_s3';
```
# Create Databricks Unity Catalog
```SQL
CREATE CATALOG CONNECTION if not exists connection_name
    type databricks
    host='metastore_uris'
    client_id='storage_connection'
    client_secret=''
    access_region='';
```
# Create Databricks Unity Catalog Connection

---

## **Overview**
This document details how to create a Databricks Unity Catalog connection using SQL statements. Through this connection, users can integrate external systems with the Databricks Unity Catalog to achieve data management and sharing. This document covers syntax, parameter descriptions, and configuration requirements.

---

## **Syntax**
```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS connection_name
    TYPE databricks
    HOST = 'host_value'
    CLIENT_ID = 'client_id_value'
    CLIENT_SECRET = 'client_secret_value'
    ACCESS_REGION = 'access_region_value';
```
**Parameter Description**
- **`connection_name`**: The name of the connection, used to identify the Databricks Unity Catalog connection. The name must be unique and follow naming conventions.
- **`TYPE databricks`**: Specifies the connection type as Databricks Unity Catalog.
- **`HOST`**: The URL address of the Databricks workspace. The usual format is `https://<workspace-url>`. Example: `https://dbc-12345678-9abc.cloud.databricks.com`
- **`CLIENT_ID`**: The client ID used for OAuth 2.0 machine-to-machine (M2M) authentication. Refer to the [Databricks OAuth M2M Authentication Documentation](https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html) to create an OAuth 2.0 application and obtain the `CLIENT_ID`.
- **`CLIENT_SECRET`**: The client secret used for OAuth 2.0 machine-to-machine (M2M) authentication. Refer to the [Databricks OAuth M2M Authentication Documentation](https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html) to create an OAuth 2.0 application and obtain the `CLIENT_SECRET`.
- **`ACCESS_REGION`**: The region where the Databricks workspace is located, such as `us-west-2` or `east-us`.

## **Example**
**step1: Databricks Preparation**
1. Create a service principal. Refer to the [Databricks Documentation](<https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html#language-Java>) to obtain the principal and its client id/client secret.
2. Enable external data access in Metastore.
![](.topwrite/assets/image_1739256232288.png)
![](.topwrite/assets/image_1739256275537.png)
3. Authorize the service principal.
```SQL
GRANT EXTERNAL USE SCHEMA ON SCHEMA quick_start.default TO `cf752cce-e2ca-4d03-8cdc-9f8f8aac43fc`; using the service principal's id
```
Below is a complete example showing how to create a Databricks Unity Catalog connection:
```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS my_databricks_conn
    TYPE databricks
    HOST = 'https://dbc-12345678-9abc.cloud.databricks.com'
    CLIENT_ID = '12345678-9abc-def0-1234-56789abcdef0'
    CLIENT_SECRET = 'abcdef1234567890abcdef1234567890'
    ACCESS_REGION = 'us-west-2';
```
**step2 : Lakehouse**
The following is a complete example showing how to create a Databricks Unity Catalog connection:
```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS my_databricks_conn    
 TYPE databricks   
 HOST = 'https://dbc-12345678-9abc.cloud.databricks.com'    
 CLIENT_ID = '12345678-9abc-def0-1234-56789abcdef0' 
 CLIENT_SECRET = 'abcdef1234567890abcdef1234567890' 
 ACCESS_REGION = 'us-west-2';
```
**Frequently Asked Questions**

Q1: How to verify if the connection is successful?
* After creating the connection, you can verify the connection status by querying the Schema or table data under the Catalog.
* Example:
  ```SQL
    CREATE EXTERNAL CATALOG external_db_cat
    CONNECTION my_databricks_conn
    OPTIONS ('catalog'='quick_start');
    show schemas in external_db_cat;
    select * from external_db_cat.default.student;
  ```
Q2: Possible reasons for connection failure?

* `HOST` address is incorrect or inaccessible.
* `CLIENT_ID` or `CLIENT_SECRET` is invalid or lacks sufficient permissions.
* `ACCESS_REGION` does not match the Databricks workspace region.

 Q3: How to update connection configuration?

* Delete the existing connection and recreate it:
  ```SQL
  DROP CATALOG CONNECTION my_databricks_conn;
  ```