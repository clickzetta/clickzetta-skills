## Overview

In the data lake architecture, Hive Catalog is a key component used to associate the data lake with external metadata storage (such as Hive Metastore). By creating a Hive Catalog, users can achieve unified management and access to metadata, thereby directly reading data stored in external systems. Apache Hive has become the core of the data warehouse ecosystem, not only as a SQL engine for big data analysis and ETL but also as a data management platform for discovering, defining, and evolving data. Meanwhile, Lakehouse supports writing and reading Hive data.

## Usage Restrictions

* Please ensure that the network between the lakehouse and the hive cluster is connected before use.
* Currently, Singdata Lakehouse's external catalog feature supports the following external data sources:
  * Hive on OSS (Alibaba Cloud Object Storage Service)
  * Hive on COS (Tencent Cloud Object Storage Service)
  * Hive on S3 (AWS Object Storage Service)
  * Hive on GCS (Google Cloud Object Storage Service)
* Supports both writing and reading. Write formats support parquet, orc, and text file formats.

### Create External Catalog

**Steps to Create Hive Catalog**

1. **Create Storage Connection**: First, you need to create a storage connection to access the object storage service.
2. **Create Catalog Connection**: Use the storage connection information and Hive Metastore address to create a Catalog Connection.
3. **Create External Catalog**: Use the Catalog Connection to create an external Catalog to access external data in the data lake.

#### Create Storage Connection

For creating a storage connection, refer to the document, [Create STORAGE CONNECTION](<aliyun_storage_connection.md>)
```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss
    type OSS
    ACCESS_ID='LTAIxxxxxxxxxxxx'
    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'
    ENDPOINT='oss-cn-hangzhou-internal.aliyuncs.com';
```
#### Create Catalog Connection
```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection
    type hms
    hive_metastore_uris='xxx:9083'
    storage_connection='catalog_storage_oss';
```
#### Create External Catalog
```SQL
CREATE EXTERNAL CATALOG test_external_catalog
    CONNECTION catalog_catalog_connection;
```
#### Using Catalog
```SQL
-- List schemas under the catalog
show schemas in test_external_catalog;
-- List all tables under the catalog
show tables in test_external_catalog.my_external_test;
-- Query tables under the catalog
select * from test_external_catalog.my_external_test.test;
-- View table structure under the catalog
desc test_external_catalog.my_external_test.test;
```
#### Use Hive Tables and Lakehouse Tables for Join Queries
Among them, test_external_catalog.my_external_test.test is a table in Hive, and public.test is an internal table in Lakehouse.
```
select * from 
test_external_catalog.my_external_test.test a
left join 
public.test b 
on a.id=b.id;
```