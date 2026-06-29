# Accessing Snowflake Open Catalog Iceberg Tables via External Catalog

## Overview

Lakehouse supports connecting to third-party Iceberg REST APIs through the Catalog Integration feature, enabling seamless integration with external data catalogs. This document describes how to connect to and use Snowflake's Open Catalog feature.

**Features**:

* **Unified Data Access**: Access Iceberg tables in Snowflake Open Catalog through a unified interface
* **Real-Time Data Sync**: Read the latest data directly from Snowflake without data copying
* **Metadata Mapping**: Automatically map table schemas and metadata information from Snowflake
* **OAuth Authentication**: Supports secure OAuth 2.0 authentication

## Environment Setup

Snowflake Open Catalog provides two types of catalogs:

**Internal Catalog**:

* **Features**: Lakehouse supports full read and write operations
* **Data Management**: Supports table schema changes, data insertion, updates, deletions, and other full lifecycle operations

**External Catalog**:

* **Features**: Lakehouse supports read-only operations only
* **Data Access**: Supports complex queries and join analysis, but does not support data modification

To prepare Iceberg tables in Snowflake and register them in Snowflake Open Catalog, refer to the [Snowflake official documentation](https://docs.snowflake.com/en/user-guide/tables-iceberg-open-catalog-sync).

Expected result: A table hosted in the Snowflake engine is registered in Snowflake Open Catalog with the following details:

* Database name: ICEBERG\_TABLES\_DB\_FLATTEN
* Schema name: ICEBERG\_SCHEMA
* Iceberg table name: czcustomer (must be lowercase; use double quotes in Snowflake DDL to prevent the table name from being auto-converted to uppercase)

> ⚠️ **Note**: When creating a Database in the Snowflake engine, include the `CATALOG_SYNC_NAMESPACE_MODE` and `CATALOG_SYNC_NAMESPACE_FLATTEN_DELIMITER` parameters to adjust the catalog hierarchy. With the configuration below, the Database and Schema are merged into a single level in Snowflake Open Catalog: `"ICEBERG_TABLES_DB_FLATTEN_ICEBERG_SCHEMA"`
>
> ```SQL
> CREATE OR REPLACE DATABASE iceberg_tables_db_flatten
> CATALOG_SYNC_NAMESPACE_MODE = 'FLATTEN'
> CATALOG_SYNC_NAMESPACE_FLATTEN_DELIMITER = '_';
> ```

## Configuration Steps

### Step 1: Create a Catalog Connection

Use the following SQL to create a connection to Snowflake Open Catalog:

```SQL
CREATE CATALOG CONNECTION snow_opencatalog 
    TYPE ICEBERG_REST 
    URI='https://lhnrdre-derekmeng.snowflakecomputing.com/polaris/api/catalog'
    ACCESS_REGION = 'ap-southeast-1' 
    OAUTH_CLIENT_ID='d3r3cuhHitrI+fUpFtvXxxxxxxx'
    OAUTH_CLIENT_SECRET='gY3ZWOGoSMM1tKK7QaqQYKpSdTcPY1ruVv7xxxxxxx'
    OAUTH_SCOPE='PRINCIPAL_ROLE:ALL'
    NAMESPACE='ICEBERG_TABLES_DB_FLATTEN_ICEBERG_SCHEMA'
    WAREHOUSE='singdata'
    WITH PROPERTIES (
        'client.region'='ap-southeast-1',
        'io-impl'='org.apache.iceberg.aws.s3.S3FileIO'
    );
```

| Parameter             | Description                                          | Example                                                               |
| --------------------- | ---------------------------------------------------- | --------------------------------------------------------------------- |
| TYPE                  | Connection type, fixed as `ICEBERG_REST`             | `ICEBERG_REST`                                                        |
| URI                   | Snowflake Polaris API endpoint                       | https://account.snowflakecomputing.com/polaris/api/catalog            |
| ACCESS_REGION         | Region where the target object resides               | `ap-southeast-1`                                                      |
| OAUTH_CLIENT_ID       | OAuth client ID                                      | Obtained when creating a Service connection in Snowflake Open Catalog |
| OAUTH_CLIENT_SECRET   | OAuth client secret                                  | Obtained when creating a Service connection in Snowflake Open Catalog |
| OAUTH_SCOPE           | OAuth authorization scope                            | `PRINCIPAL_ROLE:ALL`                                                  |
| NAMESPACE             | Second-level namespace in Snowflake Open Catalog     | `ICEBERG_TABLES_DB_FLATTEN_ICEBERG_SCHEMA`                            |
| WAREHOUSE             | Catalog name in Snowflake Open Catalog               | `singdata`                                                            |

### Step 2: Create an External Table

Create an external table to map the table in Snowflake Open Catalog:

```SQL
-- Create external table mapped to the table in Snowflake Open Catalog (names must match)
CREATE EXTERNAL TABLE IF NOT EXISTS `czcustomer`
USING ICEBERG 
CONNECTION snow_opencatalog;
```

> ⚠️ **Note**: The external table name must exactly match the table name in Snowflake.

### Step 3: Verify and Query

Verify the table schema and query data:

```SQL
-- View table schema
DESC EXTENDED `czcustomer`;

-- Query data
SELECT * FROM `czcustomer` LIMIT 10;
```

## Limitations

* Write and update operations are not supported when connecting to S3-based Snowflake-managed Iceberg tables
* The external table name must exactly match the source table name in Snowflake
* Only lowercase table names are currently supported
* Table name conversion is not supported
* Credential Vending must be enabled on the target catalog service side
