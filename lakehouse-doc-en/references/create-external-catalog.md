# Create External Catalog

Steps to create a Hive External Catalog:

1. [Create Storage Connection](create-storage-connection.md): First, you need to create a storage connection to access the object storage service.
2. [Create Catalog Connection](create-catalog-connection.md): Use the storage connection information and Hive Metastore address to create a Catalog Connection.
3. Create External Catalog: Use the Catalog Connection to create an external Catalog to access external data in the data lake.

## Syntax
```SQL
CREATE EXTERNAL CATALOG catalog_name
    CONNECTION catalog_api_connection;
```
**Parameter Description**

* **catalog_api_connection**: The name of the Catalog Connection. Supports HMS (Hive), Databricks Unity Catalog, Iceberg REST Catalog, and other types. [Refer to creating Catalog Connection](create-catalog-connection.md)

### Examples

**Case 1: Hive ON OSS (Read and Write Supported)**

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
* Create Catalog
```SQL
CREATE EXTERNAL CATALOG my_external_catalog
    CONNECTION catalog_api_connection;
```
* Verify connectivity to Hive Catalog
```SQL
-- Verify reading metadata
SHOW SCHEMAS IN my_external_catalog;
+---------------------------------------------------------------------------+
|                                schema_name                                |
+---------------------------------------------------------------------------+
| air_travel                                                                |
| all_data                                                                  |
| automobile                                                                |
| automv_schema                                                             |
| bigquant                                                                  |
+---------------------------------------------------------------------------+

-- Verify reading data, STORAGE CONNECTION permission will be used when reading data
SELECT * FROM my_external_catalog.my_schema.my_table;
```

**Case 2: Hive ON COS (Read and Write Supported)**

* Create storage connection
```sql
CREATE STORAGE CONNECTION catalog_storage_cos 
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';
```
**Parameters**:
\* **TYPE**: The object storage type, for Tencent Cloud, fill in `COS` (case insensitive)
\* **ACCESS\_KEY / SECRET\_KEY**: The access keys for Tencent Cloud, refer to: [Access Keys](https://cloud.tencent.com/document/product/598/40488)
\* **REGION**: Refers to the region where the Tencent Cloud Object Storage COS data center is located. When Singdata Lakehouse accesses Tencent Cloud COS within the same region, the COS service will automatically route to internal network access. For specific values, please refer to the Tencent Cloud documentation: [Regions and Access Domains](https://cloud.tencent.com/document/product/436/6224).

* Create Catalog Connection
  Please ensure that the network between the HMS server and Lakehouse is connected. For specific connection methods, refer to [Create Tencent Cloud Endpoint Service](creating_tencentcloud_privatelinkservice.md)
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_cos';
```
* Create Catalog
```SQL
CREATE EXTERNAL CATALOG my_external_catalog
    CONNECTION catalog_api_connection;
```
* Verify connectivity to Hive Catalog
```SQL
-- Verify reading metadata
SHOW SCHEMAS IN my_external_catalog;
+---------------------------------------------------------------------------+
|                                schema_name                                |
+---------------------------------------------------------------------------+
| air_travel                                                                |
| all_data                                                                  |
| automobile                                                                |
| automv_schema                                                             |
| bigquant                                                                  |
+---------------------------------------------------------------------------+

-- Verify reading data, STORAGE CONNECTION permission will be used when reading data
SELECT * FROM my_external_catalog.my_schema.my_table;
```

**Case 3: Hive ON S3 (Read and Write Supported)**

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
* ENDPOINT: The service address for S3, AWS China is divided into Beijing and Ningxia regions. The service address for S3 in the Beijing region is `s3.cn-north-1.amazonaws.com.cn`, and for the Ningxia region, it is `s3.cn-northwest-1.amazonaws.com.cn`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html) to find the endpoints for the Beijing and Ningxia regions -> Amazon S3 corresponding endpoints
* REGION: AWS China is divided into Beijing and Ningxia regions, the region values are: Beijing region `cn-north-1`, Ningxia region `cn-northwest-1`. Refer to: [China Region Endpoints](https://docs.amazonaws.cn/aws/latest/userguide/endpoints-arns.html)
* Create Catalog Connection
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection    
type hms    
hive_metastore_uris='xxxx:9083'    
storage_connection='catalog_storage_s3';
```
* Create Catalog
```SQL
CREATE EXTERNAL CATALOG my_external_catalog
    CONNECTION catalog_api_connection;
```
* Verify connectivity to Hive Catalog
```SQL
-- Verify reading metadata
SHOW SCHEMAS IN my_external_catalog;
+---------------------------------------------------------------------------+
|                                schema_name                                |
+---------------------------------------------------------------------------+
| air_travel                                                                |
| all_data                                                                  |
| automobile                                                                |
| automv_schema                                                             |
| bigquant                                                                  |
+---------------------------------------------------------------------------+

-- Verify reading data, STORAGE CONNECTION permission will be used when reading data
SELECT * FROM my_external_catalog.my_schema.my_table;
```

**Case 4: Hive ON HDFS (Read Support)**

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

* **Create Catalog**

  ```sql
  CREATE EXTERNAL CATALOG my_external_catalog
      CONNECTION catalog_api_connection;
  ```

* **Verify Connectivity to Hive Catalog**

  ```sql
  -- Verify metadata reading
  SHOW SCHEMAS IN my_external_catalog;

  -- Verify data reading; data is read using the permissions of the STORAGE CONNECTION
  SELECT * FROM my_external_catalog.my_schema.my_table;
  ```

> Lakehouse supports connecting to Hive Metastore and HDFS clusters with Kerberos authentication enabled.
>
> **Step 0: Prerequisites**
>
> 1. **Kerberos environment**: Ensure your Hive Metastore and HDFS cluster have Kerberos authentication enabled.
> 2. **Authentication files**: Prepare the following required Kerberos authentication files:
>
>   * `krb5.conf`: Kerberos configuration file
>   * `hive.keytab`: Keytab file for the service principal
>
> 3. **Network connectivity**: Ensure Singdata Lakehouse can access the Kerberos KDC and Hive Metastore services.
>
> **Step 1**: Upload the Kerberos config file and keytab file to a Volume using a [client tool](comprehensive_guide_to_ingesting_dbv_sql_put.md):
>
> ```
> -- upload krb5.conf
> PUT '/etc/krb5.conf' TO USER VOLUME FILE 'krb5.conf';
>
> -- upload keytab 
> PUT '/path/to/hive.keytab' TO USER VOLUME FILE 'hive.keytab';
> ```
>
> **Step 2**: Create a Catalog Connection with Kerberos authentication using the following syntax:
>
> ```
> CREATE CATALOG CONNECTION conn_hms_kerberos_auth
> TYPE HMS
> AUTH_TYPE = 'kerberos'
> KERBEROS_CLIENT_PRINCIPAL = 'hive/localhost@YOUR-REALM.COM'
> KERBEROS_SERVICE_PRINCIPAL = 'hive/localhost@YOUR-REALM.COM'
> KERBEROS_KRB5_CONFIG_PATH = 'volume:user//~/krb5.conf'
> KERBEROS_KEYTAB_PATH = 'volume:user//~/hive.keytab'
> HIVE_METASTORE_URIS = 'thrift://your-hms-host:9083'
> STORAGE_CONNECTION = 'oss_conn_hz';
> ```
>
> | Parameter Name | Required | Description | Example |
> | -------------- | -------- | ----------- | ------- |
> | AUTH_TYPE | Yes | Authentication type, set to 'kerberos' | 'kerberos' |
> | KERBEROS\_CLIENT\_PRINCIPAL | Yes | Kerberos client principal | 'hive/localhost\@CZ.COM' |
> | KERBEROS\_SERVICE\_PRINCIPAL | Yes | Kerberos service principal | 'hive/localhost\@CZ.COM' |
> | KERBEROS\_KRB5\_CONFIG\_PATH | Yes | Path to krb5.conf file | 'volume://vol\_name/krb5.conf' |
> | KERBEROS\_KEYTAB\_PATH | Yes | Path to keytab file | 'volume://vol\_name/hive.keytab' |
>
> Connection parameters:
>
> `TYPE:` The connection type, set to `HMS`
>
> `HIVE_METASTORE_URIS:` The Hive Metastore service address `'thrift://host:9083'`
>
> `STORAGE_CONNECTION:` The associated storage connection name `'your_storage_conn'`
>
> ^
>
> **Step 3**: Create an External Schema based on the Kerberos-authenticated Catalog Connection
>
> ```
> CREATE EXTERNAL SCHEMA ext_kerberos_hms_sch 
> CONNECTION conn_hms_kerberos_auth 
> OPTIONS ('schema'='default');
> ```

^

# Create Databricks External Catalog

Steps to create Databricks External Catalog:

1. [Create Catalog Connection](create-catalog-connection.md): Store Databricks' Unity Catalog connection authentication information.
2. Create External Catalog: Use Catalog Connection to create an external Catalog to access external data in the data lake.

## Syntax
```SQL
CREATE EXTERNAL CATALOG catalog_name
    CONNECTION catalog_api_connection
    OPTIONS ('catalog'='catalog_name');
```
**Parameter Description**
- **`catalog_name`**: The name of the external Catalog. This name is used to identify the Catalog, and it must be unique and comply with naming conventions.
- **`CONNECTION catalog_api_connection`**: Specifies the connection to the external Catalog. `catalog_api_connection` is the name of a pre-created connection used to access the external Catalog.
- **`OPTIONS ('catalog'='catalog_name')`**: Specifies the configuration options for the external Catalog. `'catalog'='catalog_name'`: Indicates the name of the external Catalog, `catalog_name` is the name of the target Catalog.

^

## Related Guides

- [Federated Query](SQL_External_Catalog_Guide.md): Complete examples for querying external data sources such as Hive and Databricks through External Catalog.
- [Databricks Unity Catalog Federated Query Practice](databricks-external-catalog-practice.md) — Complete examples from Databricks-side configuration, permissions, common errors, and federated query scenarios