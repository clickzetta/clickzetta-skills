# External Catalog Federation Query

External Catalog is Singdata Lakehouse's federation query feature, allowing you to directly query data in external data sources (Hive, Databricks, Snowflake Iceberg, etc.) within the Lakehouse without copying data.

## What Is an External Catalog

An External Catalog is a securable object in the Lakehouse that maps the database structure of an external data system. Through an External Catalog, users can:

- Execute read-only queries in the Lakehouse to access external data
- Import external data into the Lakehouse to build a unified data lake
- Centrally manage metadata from multiple data sources

**Key Features**:
- **Read-Only Access**: External Catalog only supports queries; external data cannot be modified
- **No Copying Required**: Data stays in the external system; the Lakehouse only reads metadata and data files
- **Unified Entry Point**: Query external data through standard SQL as if querying local tables

## Architecture

```
Lakehouse                            External Data Source
+------------------------+           +---------------------------+
|                        |           |                           |
|  SQL Query Engine      |           |  Hive Metastore           |
|                        |           |  or Iceberg               |
|  SELECT * FROM         |--- query ->  REST Catalog             |
|  ext_catalog.schema    |           |  or Databricks            |
|  .table                |           |                           |
|                        |           |                           |
|  Catalog Connection    |--- auth -->  Data Files               |
|  (credentials)         |           |  (OSS/S3/HDFS)            |
+------------------------+           +---------------------------+
```

## Comparison with Data Synchronization

| Dimension | External Catalog | Data Synchronization |
|---|---|---|
| Data Location | Remains in the external system | Copied to the Lakehouse |
| Query Latency | Depends on network and data source performance | Local query, better performance |
| Storage Cost | Does not consume Lakehouse storage | Consumes Lakehouse storage |
| Data Consistency | Real-time (directly reads external data) | Has latency (depends on sync frequency) |
| Applicable Scenarios | Ad-hoc query, data exploration, federation analysis | Frequent queries, data processing, warehouse construction |

## Supported Data Sources

| Data Source | Connection Method | Description |
|---|---|---|
| **Apache Hive** | Hive Metastore URIs | Access Hive tables via Hive Metastore |
| **Databricks Unity Catalog** | Databricks API | Access tables in Databricks |
| **Iceberg REST Catalog** | Iceberg REST Catalog API | Connect to any external catalog that conforms to the Iceberg REST Catalog standard |
| **Snowflake Open Catalog** | Iceberg REST Catalog + OAuth | Access Iceberg tables in Snowflake |

### General Iceberg REST Catalog Description

The Lakehouse supports connecting **any external catalog service conforming to this standard** via the Iceberg REST Catalog protocol, not limited to Snowflake. Common application scenarios include:

- Connecting to self-built Iceberg REST Catalog services
- Connecting to third-party data platforms' Iceberg Catalogs
- Connecting to other services supporting the Iceberg REST API, such as Dremio, Polaris, Unity Catalog, etc.

**Connection Architecture**:

```
Lakehouse                                    Iceberg REST Catalog
+------------------------+                   +----------------------------------+
|                        |                   |                                  |
|  SQL Query Engine      |                   |  Any Iceberg REST Catalog        |
|                        |                   |  (self-hosted / third-party)     |
|  SELECT * FROM         |--- REST API ----->  Iceberg Metadata                 |
|  iceberg_catalog       |                   |                                  |
|  .schema.table         |                   |                                  |
|                        |                   |                                  |
|  Catalog Connection    |--- Auth --------->  Data Files                       |
|  (credentials)         |                   |  (OSS/S3/HDFS/GCS)               |
+------------------------+                   +----------------------------------+
```

**Connection Steps**:

1. Create a Storage Connection (specify the underlying storage type: OSS/S3/HDFS, etc.)
2. Create a Catalog Connection (`TYPE ICEBERG_REST`, configure URI and authentication information)
3. Create an External Catalog

**Detailed Configuration Guide**: [Access Snowflake OpenCatalog Iceberg Tables via External Catalog](query-snowflake-open-catalog-iceberg-table.md)

### Snowflake Open Catalog Description

Snowflake Open Catalog is a concrete implementation based on the Iceberg REST Catalog protocol. The Lakehouse connects to Snowflake Open Catalog via the Iceberg REST Catalog protocol to enable cross-platform data federation queries.

**Connection Architecture**:

```
Lakehouse                                    Snowflake Open Catalog
+------------------------+                   +----------------------------------+
|                        |                   |                                  |
|  SQL Query Engine      |                   |  Polaris Catalog (Iceberg REST)  |
|                        |                   |                                  |
|  SELECT * FROM         |--- REST API ----->  Iceberg Metadata                 |
|  snowflake_catalog     |                   |                                  |
|  .schema.table         |                   |                                  |
|                        |                   |                                  |
|  Catalog Connection    |--- OAuth --------->  S3 Data Files                   |
|  (OAuth credentials)   |                   |  (Snowflake managed storage)     |
+------------------------+                   +----------------------------------+
```

**Usage Restrictions**:
- Only read-only queries are supported; write and update operations are not supported
- External table names must exactly match the source table names in Snowflake (lowercase)
- Credential Vending must be enabled on the Snowflake side

**Detailed Configuration Guide**: [Access Snowflake OpenCatalog Iceberg Tables via External Catalog](query-snowflake-open-catalog-iceberg-table.md)


**Key Configuration Parameters**:

| Parameter | Description | Example |
|------|------|------|
| TYPE | Connection type, fixed as `ICEBERG_REST` | `ICEBERG_REST` |
| URI | Polaris API endpoint or custom REST Catalog address | `https://account.snowflakecomputing.com/polaris/api/catalog` |
| OAUTH_CLIENT_ID | OAuth client ID | Obtained when creating the Service Connection |
| OAUTH_CLIENT_SECRET | OAuth client secret | Obtained when creating the Service Connection |
| NAMESPACE | Catalog namespace | `my_catalog.my_schema` |
| WAREHOUSE | Catalog name | `my_warehouse` |

**Usage Restrictions**:
- Only read-only queries are supported; write and update operations are not supported
- External table names must exactly match the source table names in Snowflake (lowercase)
- Credential Vending must be enabled on the Snowflake side

**Detailed Configuration Guide**: [Access Snowflake OpenCatalog Iceberg Tables via External Catalog](query-snowflake-open-catalog-iceberg-table.md)

## Core Concepts

### Catalog Connection

A Catalog Connection is a securable object for connecting to external data sources, containing:
- The access address of the external data source
- Authentication information (Access Key, Secret Key, OAuth Token, etc.)
- Network configuration (whether PrivateLink is required)

### External Catalog

An External Catalog is a catalog object created based on a Catalog Connection, mirroring the database structure of the external data source:
- External Catalog -> External database/namespace
- External Schema -> External Schema
- External Table -> External Table

### External Schema

An External Schema is a namespace within an External Catalog, corresponding to a Schema/Database in the external data source.

### External Table

An External Table is a table object within an External Schema, corresponding to a table in the external data source. When querying an External Table, the Lakehouse:
1. Retrieves the table's metadata (column definitions, storage location, etc.) from the external Metastore
2. Reads data files directly from external storage (OSS/S3/HDFS)
3. Performs query computation in the Lakehouse engine

## Typical Application Scenarios

### Scenario 1: Historical Data Query

An enterprise retains historical data in Hive and queries it through an External Catalog:
- No need to import large amounts of historical data into the Lakehouse
- Query on demand, saving storage costs
- Unified SQL interface, no need to learn new tools

### Scenario 2: Cross-Platform Data Federation

Simultaneously query local Lakehouse data and data in Databricks:
```sql
-- Join query of local table and external table
SELECT l.order_id, l.amount, e.customer_name
FROM local_orders l
JOIN databricks_catalog.sales_schema.customers e
  ON l.customer_id = e.customer_id;
```

### Scenario 3: Pre-Migration Verification

Before migrating data from an external system to the Lakehouse:
- Verify data completeness through the External Catalog
- Compare data consistency before and after migration
- Confirm data quality before executing the migration

## Operation Flow

```
1. Create Storage Connection
            |
            v
2. Create Catalog Connection
            |
            v
3. Create External Catalog
            |
            v
4. Query external data: SELECT * FROM ext_catalog.schema.table
```

## Permission Management

- Currently, only the `instance_admin` role can query a created External Catalog
- Authentication information through the Catalog Connection is required to access the external data source
- The external data source itself also needs corresponding access permissions configured

## Notes

- **Read-Only Access**: External Catalog does not support INSERT/UPDATE/DELETE operations
- **Performance Considerations**: Querying external data across networks may be slower than local queries
- **Authentication Security**: Catalog Connection contains sensitive authentication information and must be properly safeguarded
- **Network Connectivity**: Ensure network connectivity between the Lakehouse and the external data source

## Typical Operation Examples

The following examples are based on a real environment execution, using `clickzetta_sample_data` (SHARED type) and `databricks_main_catalog` (EXTERNAL type) to demonstrate common operations.

### 1. View All Catalogs

```SQL
SHOW CATALOGS;
+----------------------------+-------------------------+----------+
|       workspace_name       |      created_time       | category |
+----------------------------+-------------------------+----------+
| clickzetta_sample_data     | 2025-01-15 10:27:21.738 | SHARED   |
| databricks_main_catalog    | 2025-11-20 12:00:49.498 | EXTERNAL |
| ns227206                   | 2025-01-15 10:29:17.425 | MANAGED  |
+----------------------------+-------------------------+----------+
```

`category` field description: `MANAGED` is a locally managed Catalog, `SHARED` is a shared dataset, `EXTERNAL` is an External Catalog.

### 2. View External Catalog Details

```SQL
DESC CATALOG databricks_main_catalog;
+--------------------+-------------------------+
|     info_name      |       info_value        |
+--------------------+-------------------------+
| name               | databricks_main_catalog |
| creator            | qiliang                 |
| created_time       | 2025-11-20 12:00:49.498 |
| last_modified_time | 2025-11-20 12:00:49.498 |
| comment            |                         |
| type               | external                |
| connection_name    | qiliang_databricks_conn |
| origin_catalog     | main                    |
+--------------------+-------------------------+
```

`connection_name` is the name of the Catalog Connection used by this Catalog, and `origin_catalog` is the corresponding Catalog name in the external system.

### 3. Browse Catalog Structure

```SQL
-- View the schema list under a Catalog
SHOW SCHEMAS IN clickzetta_sample_data;
+---------------------------+
|        schema_name        |
+---------------------------+
| ecommerce_events_history  |
| tpcds_10tb                |
| tpch_100g                 |
| nyc_taxi_tripdata         |
+---------------------------+

-- View the table list under a Schema
SHOW TABLES IN clickzetta_sample_data.tpch_100g;
```

### 4. Query Tables in an External Catalog

Use the three-level naming structure `catalog_name.schema_name.table_name` to directly query external data:

```SQL
SELECT * FROM clickzetta_sample_data.tpch_100g.region LIMIT 5;
+-------------+-------------+------------------------------------------------------+
| r_regionkey |   r_name    |                      r_comment                       |
+-------------+-------------+------------------------------------------------------+
|           0 | AFRICA      | lar deposits. blithely final packages cajole. reg... |
|           1 | AMERICA     | hs use ironic, even requests. s                      |
|           2 | ASIA        | ges. thinly even pinto beans ca                      |
|           3 | EUROPE      | ly final courts cajole furiously final excuse        |
|           4 | MIDDLE EAST | uickly special accounts cajole carefully blithely... |
+-------------+-------------+------------------------------------------------------+
```

### 5. Cross-Catalog Federation Join

Join tables from an external Catalog with local Lakehouse tables without copying data in advance:

```SQL
-- Join the region and nation tables from the external Catalog to count nations per continent
SELECT
    r.r_name        AS region_name,
    COUNT(n.n_nationkey) AS nation_count
FROM clickzetta_sample_data.tpch_100g.region r
JOIN clickzetta_sample_data.tpch_100g.nation n
  ON r.r_regionkey = n.n_regionkey
GROUP BY r.r_name
ORDER BY nation_count DESC;
```

Cross-platform federation query example (local table JOIN external Catalog table):

```SQL
-- Join a local Lakehouse orders table with a customer dimension table from an external Catalog
SELECT
    o.order_id,
    o.amount,
    c.c_name   AS customer_name,
    c.c_nation AS customer_nation
FROM local_schema.orders o
JOIN ext_hive_catalog.sales_schema.customers c
  ON o.customer_id = c.c_custkey
WHERE o.order_date >= '2024-01-01'
LIMIT 10;
-- Note: ext_hive_catalog must be registered in advance via CREATE EXTERNAL CATALOG
```

## Related Documents

- [External Catalog Introduction](external-catalog-summary.md)
- [Create External Catalog](create-external-catalog.md)
- [Create Hive Catalog](create-hive-catalog.md)
- [Databricks Federation Query](databricks_yunqi_integration_guide_v2.md)
- [SHOW CATALOGS](show-catalog.md)
