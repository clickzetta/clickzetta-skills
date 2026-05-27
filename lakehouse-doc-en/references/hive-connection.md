## Overview

The Hive storage connection is used to access and manage existing Hive metadata services. By configuring this connection, you can:

1. Seamlessly integrate with existing data warehouse infrastructure.
2. Reuse already-built table structures and metadata information.
3. Centrally manage data catalogs for cross-platform data asset integration.

This configuration approach is especially suitable for enterprises during data platform upgrade or integration processes, enabling a smooth transition and system coexistence. You can fully leverage the advantages of both systems without needing to migrate existing data.

## Usage Restrictions

* Before use, ensure that the network between the Lakehouse and the Hive cluster is connected.
* Currently, the External Catalog feature of Singdata Lakehouse supports the following external data sources:
  * Hive on OSS (Alibaba Cloud Object Storage Service)
  * Hive on COS (Tencent Cloud Object Storage Service)
  * Hive on S3 (AWS Object Storage Service)
  * Hive on GCS (Google Cloud Object Storage Service)
* Both read and write are supported. Write operations support Parquet, ORC, and Text file formats.

### Create External Catalog

**Steps to Create a Hive Catalog**

1.  **Create Storage Connection**: First, create a storage connection to access the object storage service.
2.  **Create Catalog Connection**: Use the storage connection information and Hive Metastore address to create a Catalog Connection.
3.  **Create External Catalog**: Use the Catalog Connection to create an External Catalog for accessing external data in the data lake.

#### Create Storage Connection

For creating a storage connection, refer to the document [Create STORAGE CONNECTION](aliyun_storage_connection.md).

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

^
