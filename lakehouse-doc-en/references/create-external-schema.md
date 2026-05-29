# CREATE EXTERNAL SCHEMA

## Overview

The `CREATE EXTERNAL SCHEMA` statement maps an external data source (Hive Metastore or Databricks Unity Catalog) as a schema in Lakehouse, allowing users to query external data directly in Lakehouse without migrating the data.

## Usage Restrictions

The following external data sources are currently supported:

- Hive on OSS (Alibaba Cloud Object Storage, read and write supported)
- Hive on COS (Tencent Cloud Object Storage, read and write supported)
- Hive on S3 (AWS Object Storage, read and write supported)
- Hive on HDFS (Preview, read-only, contact Lakehouse support)
- Databricks Unity Catalog

Write formats supported: Parquet, ORC, Text.

## Syntax

```Plain
CREATE EXTERNAL SCHEMA [ IF NOT EXISTS ] schema_name
    CONNECTION connection_name
    [ OPTIONS ( option_key = 'option_value' [, ...] ) ];
```

## Parameters

| Parameter | Required | Description |
|------|----------|------|
| `schema_name` | Yes | Name of the external schema, must be unique within the current workspace |
| `IF NOT EXISTS` | No | If the schema already exists, skip without error |
| `CONNECTION connection_name` | Yes | Pre-created Catalog Connection name; see [Create Catalog Connection](create-catalog-connection.md) |
| `OPTIONS` | No | Additional configuration options for specifying the database or catalog name in the external data source |

### Common OPTIONS

| Option | Applicable Scenario | Description |
|--------|----------|------|
| `SCHEMA` | Hive | The Hive database name to map. Defaults to `schema_name` if not specified |
| `catalog` | Databricks | The Databricks Unity Catalog name |
| `schema` | Databricks | The Databricks Unity Catalog schema name |

## Creation Process

### Hive External Schema (HMS)

Creating a Hive External Schema requires three steps: Create Storage Connection -> Create Catalog Connection -> Create External Schema.

**Step 1: Create Storage Connection**

```SQL
CREATE STORAGE CONNECTION IF NOT EXISTS catalog_storage_oss
    TYPE OSS
    ACCESS_ID = 'LTAIxxxxxxxxxxxx'
    ACCESS_KEY = 'T8Gexxxxxxmtxxxxxx'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

**Step 2: Create Catalog Connection**

Ensure that the HMS server network is connected with the Lakehouse network. See [Creating Alibaba Cloud PrivateLink Endpoint Service](creating_alicloud_privatelinkservice.md).

```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS catalog_api_connection
    TYPE hms
    hive_metastore_uris = 'xxxx:9083'
    storage_connection = 'catalog_storage_oss';
```

**Step 3: Create External Schema**

```SQL
CREATE EXTERNAL SCHEMA IF NOT EXISTS my_external_schema
    CONNECTION catalog_api_connection
    OPTIONS (SCHEMA = 'default');
```

**Verify Connectivity**

```SQL
-- Verify metadata reading
SHOW TABLES IN my_external_schema;

-- Verify data reading
SELECT * FROM my_external_schema.my_table LIMIT 10;
```

### Databricks Unity Catalog External Schema

**Step 1: Create Catalog Connection**

See [Create Databricks Catalog](create-catalog-connection.md).

```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS conn_databricks
    TYPE databricks
    HOST = 'https://dbc-12345678-9abc.cloud.databricks.com'
    CLIENT_ID = 'client_id_value'
    CLIENT_SECRET = 'client_secret_value'
    ACCESS_REGION = 'us-west-2';
```

**Step 2: Create External Schema**

```SQL
CREATE EXTERNAL SCHEMA IF NOT EXISTS external_db_sch
    CONNECTION conn_databricks
    OPTIONS ('catalog' = 'quick_start', 'schema' = 'default');
```

**Verify Connectivity**

```SQL
SHOW TABLES IN external_db_sch;
```

## Cloud Platform Storage Connection Parameters

### Hive on COS (Tencent Cloud)

```SQL
CREATE STORAGE CONNECTION catalog_storage_cos
    TYPE COS
    ACCESS_KEY = '<access_key>'
    SECRET_KEY = '<secret_key>'
    REGION = 'ap-shanghai'
    APP_ID = '1310000503';
```

- `REGION`: COS data center region. See [Regions and Access Endpoints](https://cloud.tencent.com/document/product/436/6224).
- For network connectivity, see [Creating Tencent Cloud PrivateLink Endpoint Service](creating_tencentcloud_privatelinkservice.md).

### Hive on S3 (AWS)

```SQL
CREATE STORAGE CONNECTION catalog_storage_s3
    TYPE S3
    ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
    SECRET_KEY = '7kfheDrmq***'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';
```

- `ENDPOINT`: Beijing region `s3.cn-north-1.amazonaws.com.cn`, Ningxia region `s3.cn-northwest-1.amazonaws.com.cn`.
- `REGION`: Beijing region `cn-north-1`, Ningxia region `cn-northwest-1`.

### Hive on HDFS (Preview)

```SQL
CREATE STORAGE CONNECTION hdfs_conn
    TYPE HDFS
    NAME_NODE = 'zetta-cluster'
    NAME_NODE_RPC_ADDRESSES = ['11.110.239.148:8020'];
```

- `NAME_NODE`: Corresponds to `dfs.nameservices` in HDFS configuration, i.e., the logical cluster name.
- `NAME_NODE_RPC_ADDRESSES`: Corresponds to `dfs.namenode.rpc-address`, format: `[<host>:<port>]`.

## Notes

- A corresponding Catalog Connection must be created before creating an External Schema.
- When the `SCHEMA` parameter in `OPTIONS` is not specified, Lakehouse defaults to mapping `schema_name` to the Hive database.
- Hive on HDFS is currently in Preview and only supports reads; contact Lakehouse support if needed.
- Data in an External Schema is stored in the external system; deleting an External Schema does not delete the underlying data.
