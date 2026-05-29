# Create Catalog Connection

Catalog Connection stores the authentication information needed to access external metadata services (Hive Metastore, Databricks Unity Catalog, Iceberg REST Catalog, etc.) and is used by External Catalogs and External Schemas.

## Supported Types

| Type Value | Data Source | Authentication |
|---|---|---|
| `HMS` | Apache Hive | Storage key (+ optional Kerberos) |
| `databricks` | Databricks Unity Catalog | OAuth M2M (CLIENT_ID / CLIENT_SECRET) |
| `ICEBERG_REST` | Generic Iceberg REST Catalog (including Snowflake Open Catalog) | No auth or OAuth |

> ⚠️ **Note**: Databricks storage (S3/OSS/COS) must be on the same cloud platform as the Lakehouse instance.

---

## HMS (Hive Metastore)

### Syntax

```Plain
CREATE CATALOG CONNECTION [IF NOT EXISTS] <connection_name>
    TYPE HMS
    HIVE_METASTORE_URIS = '<thrift://host:port>'
    STORAGE_CONNECTION = '<storage_connection_name>'
    [AUTH_TYPE = 'kerberos'
     KERBEROS_CLIENT_PRINCIPAL = '<principal>'
     KERBEROS_SERVICE_PRINCIPAL = '<principal>'
     KERBEROS_KRB5_CONFIG_PATH  = '<volume_path>'
     KERBEROS_KEYTAB_PATH       = '<volume_path>'];
```

### Parameter Description

- `HIVE_METASTORE_URIS`: The Hive Metastore service address, in the format `thrift://host:9083`. The port is typically 9083.
- `STORAGE_CONNECTION`: The name of an existing storage connection, used to read Hive data files (OSS/COS/S3/HDFS).
- `AUTH_TYPE`: Authentication type. Defaults to no authentication if omitted. Set to `'kerberos'` to enable Kerberos authentication.
- Kerberos parameters are only required when `AUTH_TYPE = 'kerberos'`. The config file and keytab file must be uploaded to User Volume in advance using the `PUT` command.

### Examples

**Hive ON OSS (Alibaba Cloud)**

```SQL
-- Step 1: Create storage connection
CREATE STORAGE CONNECTION IF NOT EXISTS oss_conn
    TYPE OSS
    ACCESS_ID = 'LTAIxxxxxxxxxxxx'
    ACCESS_KEY = 'T8Gexxxxxxmtxxxxxx'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';

-- Step 2: Create Catalog Connection
-- Ensure the server where HMS is located has network connectivity to Lakehouse. Refer to: Create Alibaba Cloud Endpoint Service
CREATE CATALOG CONNECTION IF NOT EXISTS hive_oss_conn
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://192.168.1.100:9083'
    STORAGE_CONNECTION = 'oss_conn';
```

**Hive ON COS (Tencent Cloud)**

```SQL
CREATE STORAGE CONNECTION IF NOT EXISTS cos_conn
    TYPE COS
    ACCESS_KEY = '<access_key>'
    SECRET_KEY = '<secret_key>'
    REGION = 'ap-shanghai'
    APP_ID = '1310000503';

CREATE CATALOG CONNECTION IF NOT EXISTS hive_cos_conn
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://192.168.1.100:9083'
    STORAGE_CONNECTION = 'cos_conn';
```

**Hive ON S3 (AWS)**

```SQL
CREATE STORAGE CONNECTION IF NOT EXISTS s3_conn
    TYPE S3
    ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
    SECRET_KEY = '7kfheDrmq***'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';

CREATE CATALOG CONNECTION IF NOT EXISTS hive_s3_conn
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://192.168.1.100:9083'
    STORAGE_CONNECTION = 's3_conn';
```

**Hive + Kerberos Authentication**

```SQL
-- Upload authentication files to User Volume first
PUT '/etc/krb5.conf' TO USER VOLUME FILE 'krb5.conf';
PUT '/path/to/hive.keytab' TO USER VOLUME FILE 'hive.keytab';

CREATE CATALOG CONNECTION IF NOT EXISTS hive_kerberos_conn
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://your-hms-host:9083'
    STORAGE_CONNECTION = 'oss_conn'
    AUTH_TYPE = 'kerberos'
    KERBEROS_CLIENT_PRINCIPAL = 'hive/localhost@YOUR-REALM.COM'
    KERBEROS_SERVICE_PRINCIPAL = 'hive/localhost@YOUR-REALM.COM'
    KERBEROS_KRB5_CONFIG_PATH = 'volume:user//~/krb5.conf'
    KERBEROS_KEYTAB_PATH = 'volume:user//~/hive.keytab';
```

---

## Databricks Unity Catalog

### Syntax

```Plain
CREATE CATALOG CONNECTION [IF NOT EXISTS] <connection_name>
    TYPE databricks
    HOST = '<https://workspace-url>'
    CLIENT_ID = '<oauth_client_id>'
    CLIENT_SECRET = '<oauth_client_secret>'
    ACCESS_REGION = '<region>';
```

### Parameter Description

- `HOST`: The Databricks workspace URL, in the format `https://dbc-xxxxx.cloud.databricks.com`.
- `CLIENT_ID / CLIENT_SECRET`: OAuth M2M authentication credentials. Obtain these by creating a Service Principal in the Databricks console. Refer to the [Databricks OAuth M2M documentation](https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html).
- `ACCESS_REGION`: The region where the Databricks workspace is located, such as `us-west-2`.

### Databricks Pre-configuration

1. Create a Service Principal and obtain the `CLIENT_ID` and `CLIENT_SECRET`.
2. Enable External Data Access on the Metastore.
3. Grant permissions to the Service Principal:
   ```SQL
   GRANT EXTERNAL USE SCHEMA ON SCHEMA <catalog>.<schema> TO `<service_principal_id>`;
   ```

### Example

```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS my_databricks_conn
    TYPE databricks
    HOST = 'https://dbc-12345678-9abc.cloud.databricks.com'
    CLIENT_ID = '12345678-9abc-def0-1234-56789abcdef0'
    CLIENT_SECRET = 'abcdef1234567890abcdef1234567890'
    ACCESS_REGION = 'us-west-2';
```

Verify the connection:

```SQL
CREATE EXTERNAL CATALOG my_databricks_catalog
    CONNECTION my_databricks_conn
    OPTIONS ('catalog' = 'main');

SHOW SCHEMAS IN my_databricks_catalog;
```

---

## Iceberg REST Catalog

The Iceberg REST protocol is an open standard. Any service compatible with this protocol (self-hosted Iceberg REST services, Polaris, Dremio, Snowflake Open Catalog, etc.) uses the same `TYPE ICEBERG_REST`. The difference is whether OAuth authentication is required.

### Syntax

```Plain
CREATE CATALOG CONNECTION [IF NOT EXISTS] <connection_name>
    TYPE ICEBERG_REST
    URI = '<catalog_endpoint>'
    [ACCESS_REGION = '<region>']
    [OAUTH_CLIENT_ID = '<client_id>'
     OAUTH_CLIENT_SECRET = '<client_secret>'
     OAUTH_SCOPE = '<scope>'
     NAMESPACE = '<namespace>'
     WAREHOUSE = '<warehouse>']
    [WITH PROPERTIES ('<key>' = '<value>', ...)];
```

### Parameter Description

- `URI`: The API endpoint of the Iceberg REST Catalog (required).
- `ACCESS_REGION`: The cloud storage region where the underlying data files are located.
- `OAUTH_CLIENT_ID / OAUTH_CLIENT_SECRET`: OAuth authentication credentials. Required for services that need OAuth, such as Snowflake Open Catalog.
- `OAUTH_SCOPE`: OAuth authorization scope. For Snowflake Open Catalog, this is fixed as `'PRINCIPAL_ROLE:ALL'`.
- `NAMESPACE`: The Iceberg namespace (database name). Required by some services.
- `WAREHOUSE`: The catalog name. Required by some services (such as Snowflake Open Catalog).
- `WITH PROPERTIES`: Additional underlying configuration, such as `'io-impl'` (specifies the file IO implementation).

> ⚠️ **Note**: Do not add `=` after `TYPE`, and do not add commas between parameters. Writing `TYPE = ICEBERG_REST` will cause a syntax error.

### Example: Generic Iceberg REST Catalog (No Authentication)

```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS iceberg_conn
    TYPE ICEBERG_REST
    URI = 'https://your-iceberg-rest-catalog/api/catalog'
    ACCESS_REGION = 'cn-hangzhou';

-- Create External Catalog (no OPTIONS needed)
CREATE EXTERNAL CATALOG iceberg_catalog
    CONNECTION iceberg_conn;
```

### Example: Snowflake Open Catalog (OAuth)

Snowflake Open Catalog is a managed service based on the Iceberg REST protocol and requires additional OAuth parameters.

```SQL
CREATE CATALOG CONNECTION IF NOT EXISTS snow_opencatalog_conn
    TYPE ICEBERG_REST
    URI = 'https://<account>.snowflakecomputing.com/polaris/api/catalog'
    ACCESS_REGION = 'ap-southeast-1'
    OAUTH_CLIENT_ID = '<client_id>'
    OAUTH_CLIENT_SECRET = '<client_secret>'
    OAUTH_SCOPE = 'PRINCIPAL_ROLE:ALL'
    NAMESPACE = '<your_database>'
    WAREHOUSE = '<your_catalog>'
    WITH PROPERTIES (
        'client.region' = 'ap-southeast-1',
        'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO'
    );

-- Create External Catalog (no OPTIONS needed; the connection already contains namespace information)
CREATE EXTERNAL CATALOG snow_catalog
    CONNECTION snow_opencatalog_conn;
```

For detailed configuration steps, refer to: [Accessing Iceberg Tables in Snowflake Open Catalog](query-snowflake-open-catalog-iceberg-table.md)

---

## Manage Catalog Connection

```SQL
-- List all connections
SHOW CONNECTIONS;

-- View connection details
DESC CONNECTION my_conn;

-- Drop a connection (drop any dependent External Catalogs first)
DROP CONNECTION my_conn;
```

## Related Documentation

- [Create External Catalog](create-external-catalog.md) — Create an External Catalog based on a Catalog Connection
- [Create External Schema](create-external-schema.md) — Mount an external database into the current workspace
- [Create Storage Connection](create-storage-connection.md) — Storage Connection required by HMS
- [Accessing Iceberg Tables in Snowflake Open Catalog](query-snowflake-open-catalog-iceberg-table.md)
