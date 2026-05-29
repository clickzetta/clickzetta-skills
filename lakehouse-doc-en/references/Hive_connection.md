## Feature Overview

The Hive storage connection is used to access and manage existing Hive metadata services. By configuring this connection, you can:

1. Seamlessly integrate with existing data warehouse infrastructure.
2. Reuse already-built table structures and metadata information.
3. Centrally manage data catalogs to achieve cross-platform data asset consolidation.

This configuration approach is particularly suitable for enterprises to achieve smooth migration and system coexistence during data platform upgrades or integration. You can fully leverage the advantages of both systems without migrating existing data.

## Limitations

* Ensure network connectivity between Lakehouse and the Hive cluster is established before use.
* Currently, the Singdata Lakehouse external Catalog feature supports the following external data sources:
  * Hive on OSS (Alibaba Cloud Object Storage Service)
  * Hive on COS (Tencent Cloud Object Storage Service)
  * Hive on S3 (AWS Object Storage Service)
  * Hive on GCS (Google Cloud Object Storage Service)
* Both read and write operations are supported. Write formats include Parquet, ORC, and Text file formats.

### Creating an External Catalog

**Steps to Create a Hive Catalog**

1.  **Create a Storage Connection**: First, create a storage connection to access the object storage service.
2.  **Create a Catalog Connection**: Use the storage connection information and Hive Metastore address to create a Catalog Connection.
3.  **Create an External Catalog**: Use the Catalog Connection to create an external Catalog for accessing external data within the data lake.

#### Creating a Storage Connection

For creating a storage connection, refer to the document [Creating a STORAGE CONNECTION](aliyun_storage_connection.md).

```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss
    type OSS
    ACCESS_ID='LTAIxxxxxxxxxxxx'
    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'
    ENDPOINT='oss-cn-hangzhou-internal.aliyuncs.com';
```

#### Creating a Catalog Connection

```SQL
CREATE CATALOG CONNECTION if not exists catalog_api_connection
    type hms
    hive_metastore_uris='xxx:9083'
    storage_connection='catalog_storage_oss';
```

^
