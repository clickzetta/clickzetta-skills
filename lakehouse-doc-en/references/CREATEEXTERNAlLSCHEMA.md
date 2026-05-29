Lakehouse introduces a powerful feature that maps external databases to Lakehouse through `EXTERNAL SCHEMA`, allowing users to query external data directly in Lakehouse storage without migrating data. This feature greatly enhances the convenience of cross-data source operations and queries, providing users with a more flexible data integration solution.

# Usage Restrictions

* Currently, Singdata Lakehouse's external schema mapping feature supports the following external data sources:
  * Hive on OSS (Alibaba Cloud Object Storage Service)
  * Hive on COS (Tencent Cloud Object Storage Service)
  * Hive on S3 (AWA Object Storage Service)
  * Hive on HDFS (Preview, please contact Lakehouse support)
  * Databricks Unity Catalog    
* Supports both writing and reading. Write formats support parquet, orc, text file formats

# Create Hive External Schema
## Syntax
### Create Storage Connection

First, you need to create a storage connection to connect to the external object storage service.
```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss
    type OSS
    ACCESS_ID='LTAIxxxxxxxxxxxx'
    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'
    ENDPOINT='xxx';
```
### Create Hive Catalog Connection

Next, create a Catalog connection pointing to the Hive metadata storage service (Hive Metastore).
```SQL
CREATE CATALOG CONNECTION if not exists connection_name
    type hms
    hive_metastore_uris='metastore_uris'
    storage_connection='storage_connection';
```
### Create External Schema
Finally, create an External Schema to map the external data source to the Lakehouse.
```SQL
CREATE EXTERNAL SCHEMA if not exists schema_name
    CONNECTION connection_name
    options(SCHEMA='hive_database_name');
```
* `connection`: Required parameter, specifies the name of the Catalog Connection.
* `SCHEMA`: Optional parameter, used to map the database name of Hive. If not specified, Lakehouse will automatically map the created `schema_name` to the database in Hive.

### Examples

Example 1: Hive ON OSS

* Create storage connection
```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss   
 type OSS    
 ACCESS_ID='LTAIxxxxxxxxxxxx'    
 ACCESS_KEY='T8Gexxxxxxmtxxxxxx'   
 ENDPOINT='oss-cn-hangzhou-internal.aliyuncs.com';
```
* Create Catalog Connection
  Please ensure that the network between the server where HMS is located and the Lakehouse is connected. For specific connection methods, please refer to [Creating Alibaba Cloud Endpoint Service](creating_alicloud_privatelinkservice.md)
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_oss';
```
* Create External Schema
```SQL
CREATE EXTERNAL SCHEMA if not exists my_external_schema
    CONNECTION catalog_api_connection
    options(SCHEMA='default');
```
* Verify if the Hive Catalog is connected
```SQL
--Verify reading metadata
SHOW TABLES IN my_external_schema;

--Verify reading data, STORAGE CONNECTION permission will be used when reading data
SELECT * FROM my_external_schema.my_table;
```
```markdown
Case 2: Hive ON COS

* Create storage connection
```
```sql
CREATE STORAGE CONNECTION catalog_storage_cos 
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';
```
**Parameters**:
* **TYPE**: For object storage type, fill in `COS` for Tencent Cloud (case insensitive)
* **ACCESS\_KEY / SECRET\_KEY**: These are the access keys for Tencent Cloud. For how to obtain them, refer to: [Access Keys](https://cloud.tencent.com/document/product/598/40488)
* **REGION**: Refers to the region where the Tencent Cloud Object Storage COS data center is located. When Singdata Lakehouse accesses Tencent Cloud COS within the same region, the COS service will automatically route to internal network access. For specific values, please refer to the Tencent Cloud documentation: [Regions and Access Domain Names](https://cloud.tencent.com/document/product/436/6224).

* Create Catalog Connection
  Please ensure that the network between the server where HMS is located and Lakehouse is connected. For specific connection methods, you can refer to [Create Tencent Cloud Endpoint Service](creating_tencentcloud_privatelinkservice.md)
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_cos';
```
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_oss';
```
* Create External Schema
```SQL
CREATE EXTERNAL SCHEMA if not exists my_external_schema
    CONNECTION catalog_api_connection
    options(SCHEMA='default');
```
* Verify if the Hive Catalog is connected
```SQL
--Verify reading metadata
SHOW TABLES IN my_external_schema;

--Verify reading data, STORAGE CONNECTION permission will be used when reading data
SELECT * FROM my_external_schema.my_table;
```
Case 3: Hive ON S3

* Create storage connection
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
* REGION: AWS China is divided into Beijing and Ningxia regions, the region values are: Beijing region `cn-north-1`, Ningxia region `cn-northwest-1`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html)
* Create Catalog Connection
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_s3';
```
* Create External Schema
```SQL
CREATE EXTERNAL SCHEMA if not exists my_external_schema
    CONNECTION catalog_api_connection
    options(SCHEMA='default');
```
* Verify if the Hive Catalog is connected
```SQL
--Verify reading metadata
SHOW TABLES IN my_external_schema;

--Verify reading data, STORAGE CONNECTION permission will be used when reading data
SELECT * FROM my_external_schema.my_table;
```
Case 4: Hive ON HDFS (Read Support)

* **Create Storage Connection**

  ```sql
  CREATE STORAGE CONNECTION hdfs_conn
  TYPE HDFS
  NAME_NODE='zetta-cluster'
  NAME_NODE_RPC_ADDRESSES=['11.110.239.148:8020'];
  ```

  * `TYPE HDFS`: Specifies the connection type as HDFS.
  * `NAME_NODE`: Corresponds to `dfs.nameservices` in the [HDFS configuration](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithNFS.html), which is the logical name of the HDFS cluster, such as `zetta-cluster`.
  * `NAME_NODE_RPC_ADDRESSES`: Corresponds to `dfs.namenode.rpc-address` in the [HDFS configuration](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithNFS.html), which is the RPC address of the NameNode, formatted as `[<host>:<port>]`, such as `['11.110.239.148:8020']`.

* **Create Catalog Connection**

  ```sql
  CREATE CATALOG CONNECTION if not exists catalog_api_connection    
  type hms    
  hive_metastore_uris='xxxx:9083'    
  storage_connection='hdfs_conn';
  ```

* **Create External Schema**

  ```sql
  CREATE EXTERNAL SCHEMA if not exists my_external_schema
      CONNECTION catalog_api_connection
      options(SCHEMA='default');
  ```

* **Verify Connectivity to Hive Catalog**

  ```sql
  -- Verify metadata reading
  SHOW TABLES IN my_external_schema;

  -- Verify data reading; data is read using the permissions of the STORAGE CONNECTION
  SELECT * FROM my_external_schema.my_table;
  ```
# Create Databricks External Schema
## Syntax
### Create Databricks Catalog Connection
Create a Catalog connection pointing to the Databricks metadata storage service. For specific usage, refer to [Create Databricks Catalog](<create-catalog-connection.md>)
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

### Create External Schema
```sql
CREATE EXTERNAL SCHEMA schema_name 
   CONNECTION connection_name    
OPTIONS ('catalog'='catalog_value', 'schema'='schema_value');
```
**Parameter Description**
- `schema_name` : The name of the external schema. This name is used to identify the external schema, and it must be unique and comply with naming conventions.
- `CONNECTION connection_name` : Specifies the connection to the external schema. `connection_name` is the name of a pre-created connection used to access the external schema.
- `OPTIONS` : Specifies the configuration options for the external schema.
    - `'catalog'='catalog_value'` : Specifies the Catalog name of the external schema.
    - `'schema'='schema_value'` : Specifies the Schema name of the external schema.
**Example**
```sql
CREATE EXTERNAL SCHEMA external_db_sch   
 CONNECTION conn_db    
 OPTIONS ('catalog'='quick_start', 'schema'='default');
```
**Example Analysis**：
* **`external_db_sch`**: The name of the created external schema.
* **`conn_db`**: The name of the connection used to connect to the external schema.
* **`OPTIONS`**:
  * `catalog='quick_start'`: Specifies the Catalog name of the external schema.
  * `schema='default'`: Specifies the Schema name of the external schema.
* Verify connectivity to Databricks Unity Catalog
```
--Verify reading metadata
SHOW TABLES IN external_db_sch;
```