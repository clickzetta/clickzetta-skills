# Accessing Iceberg Tables in Snowflake Open Catalog via External Catalog

## **Overview**

Lakehouse supports connecting to third-party Iceberg REST APIs through the Catalog Integration feature, enabling seamless integration with external data catalogs. This document describes how to connect to and use Snowflake's Open Catalog feature.

**Features**:

* **Unified data access**: Access Iceberg tables in Snowflake Open Catalog through a unified interface
* **Real-time data synchronization**: Directly read the latest data in Snowflake without data replication
* **Metadata mapping**: Automatically map table structures and metadata from Snowflake
* **OAuth authentication**: Support for secure OAuth 2.0 authentication mechanism

## **Environment Preparation**

Snowflake Open Catalog provides two types of catalogs:

**Internal Catalog**:

* **Features**: Lakehouse supports full read and write operations
* **Data management**: Supports full lifecycle operations including table structure changes, data inserts, updates, and deletes

**External Catalog**:

* **Features**: Lakehouse only supports read-only operations
* **Data access**: Supports complex queries and cross-table analysis, but does not support data modification operations

Prepare Iceberg tables in Snowflake and register them in Snowflake Open Catalog. Please refer to the [Snowflake official documentation](https://docs.snowflake.com/en/user-guide/tables-iceberg-open-catalog-sync)

Result: A table in the Snowflake engine is registered in Snowflake Open Catalog:

* Database name: ICEBERG_TABLES_DB_FLATTEN
* Schema name: ICEBERG_SCHEMA
* Iceberg table name: czcustomer (lowercase required. In Snowflake's CREATE TABLE DDL, use double quotes to prevent the table name from being automatically converted to uppercase)

> Note: When creating a Database in the Snowflake engine, add the `CATALOG_SYNC_NAMESPACE_MODE` and `CATALOG_SYNC_NAMESPACE_FLATTEN_DELIMITER` parameters to adjust the Catalog hierarchy. With the following configuration, in Snowflake Open Catalog, Database and Schema are merged into a single level: "`ICEBERG_TABLES_DB_FLATTEN_ICEBERG_SCHEMA`"
>
> ```
> CREATE OR REPLACE DATABASE iceberg_tables_db_flatten
> CATALOG_SYNC_NAMESPACE_MODE = 'FLATTEN'
> CATALOG_SYNC_NAMESPACE_FLATTEN_DELIMITER = '_';
> ```

![](.topwrite/assets/20250901-112722.jpeg)

## **Configuration Steps**

### Step 1: Create a Catalog Connection

Use the following SQL statement to create a connection to Snowflake Open Catalog:

```
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

| Parameter             | Description                                    | Example                                                       |
| --------------------- | ---------------------------------------------- | ------------------------------------------------------------- |
| TYPE                  | Connection type, fixed as `ICEBERG_REST`       | `ICEBERG_REST`                                                |
| URI                   | Snowflake Polaris API endpoint                 | <https://account.snowflakecomputing.com/polaris/api/catalog>  |
| ACCESS_REGION         | Region where the accessed object is located    | `ap-southeast-1`                                              |
| OAUTH_CLIENT_ID       | OAuth client ID                                | Obtained when creating a Service connection in Snowflake Open Catalog |
| OAUTH_CLIENT_SECRET   | OAuth client secret                            | Obtained when creating a Service connection in Snowflake Open Catalog |
| OAUTH_SCOPE           | OAuth authorization scope                      | `PRINCIPAL_ROLE:ALL`                                          |
| NAMESPACE             | The second level in Snowflake Open Catalog     | `ICEBERG_TABLES_DB_FLATTEN_ICEBERG_SCHEMA`                    |
| WAREHOUSE             | Snowflake Open Catalog's Catalog name          | `singdata`                                                    |

### Step 2: Create an External Table

Create an external table to map tables in Snowflake Open Catalog:

```SQL
-- Create external table mapping to the table in Snowflake Open Catalog (table name must match)
CREATE EXTERNAL TABLE IF NOT EXISTS `czcustomer`
USING ICEBERG
CONNECTION snow_opencatalog;
```

> **Note**: The external table name must exactly match the table name in Snowflake.

### Step 3: Verify and Query

Verify the table structure and query data:

```SQL
-- View table structure
DESC EXTENDED `czcustomer`;

-- Query data
SELECT * FROM `czcustomer` LIMIT 10;
```

![](.topwrite/assets/opencatalog_3.jpeg)

## Usage Limitations

* When connecting to S3-based Snowflake-managed Iceberg tables, write and update operations are not supported
* External table names must exactly match the source table names in Snowflake
* Currently only lowercase table names are supported
* Table name conversion is not supported
* Credential Vending must be enabled on the target Catalog service side

![](.topwrite/assets/credentials_vending.jpeg)
