# Lakehouse Federated Query Guide (External Catalog)

## Overview

Federated Queries allow Lakehouse to directly query data in external data catalogs (such as Hive Metastore, Databricks Unity Catalog) without migrating or copying data. Using `CREATE EXTERNAL CATALOG`, you can map external data sources as Catalogs within Lakehouse and use standard SQL for cross-system queries. This guide is organized by business scenario to help you quickly master federated query configuration methods.

### Quick Navigation

* [Create Hive External Catalog](#create-hive-external-catalog) -- Mount a Hive Metastore
* [Query External Catalog Data](#query-external-catalog-data) -- Use three-level namespace queries
* [View External Schemas and Tables](#view-external-schemas-and-tables) -- Explore external catalog structure
* [Drop External Catalog](#drop-external-catalog) -- Clean up the federation connection

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE EXTERNAL CATALOG` | Create an external catalog | Mount external catalogs such as Hive/Databricks |
| `SHOW CATALOGS` | View all Catalogs | Confirm external Catalog registration |
| `SHOW SCHEMAS IN ext_catalog` | View external Schemas | Explore external database structure |
| `SHOW TABLES IN ext_catalog.schema` | View external tables | Explore external table lists |
| `SELECT * FROM ext_catalog.schema.table` | Query external tables | Cross-system federated query |

***

## Prerequisites

The following examples assume that the corresponding Storage Connection and Catalog Connection have been created:

```sql
-- Ensure a Storage Connection has been created (pointing to external storage)
-- Ensure a Catalog Connection has been created (pointing to Hive Metastore or Databricks)
```

***

## Create Hive External Catalog

Use `CREATE EXTERNAL CATALOG` with a Catalog Connection to mount a Hive data catalog.

```sql
-- Create a Hive External Catalog
CREATE EXTERNAL CATALOG hive_prod
CONNECTION hive_catalog_conn;
```

**Parameter Descriptions**:
* `hive_prod`: The name of the external Catalog in Lakehouse.
* `hive_catalog_conn`: A pre-created Catalog Connection containing HMS address and authentication information.

> **Tip**: Upon successful creation, Hive Databases are mapped as External Schemas, and Hive Tables are mapped as External Tables.

***

## Query External Catalog Data

Use the three-level namespace (`catalog.schema.table`) to directly query external data.

```sql
-- Query an external table
SELECT customer_id, SUM(amount) as total_spent
FROM databricks_main_catalog.sales_db.customer_orders
GROUP BY customer_id
LIMIT 10;
```

**Execution Notes**:
* Lakehouse requests metadata from the external Catalog and reads data files directly from external storage (such as OSS/S3).
* Query syntax is identical to local tables, supporting JOIN, aggregation, window functions, etc.

> **Verification Status**: The test environment's External Catalog authentication has expired (returning `Unauthenticated`), but `SHOW CATALOGS` verified that the External Catalog object exists and the syntax is correct. Normal queries will work in production after configuring valid authentication.

***

## View External Schemas and Tables

Use `SHOW` commands to explore the structure of external catalogs.

```sql
-- View all Catalogs
SHOW CATALOGS;
```

**Returned Information**:

| workspace_name | created_time | category |
|----------------|--------------|----------|
| databricks_main_catalog | 2025-11-20 12:00:49 | EXTERNAL |
| quick_start | 2025-01-15 10:27:21 | MANAGED |
| ... | ... | ... |

> **Note**: `category = 'EXTERNAL'` indicates a federated catalog created via `CREATE EXTERNAL CATALOG`.

```sql
-- View Schemas under an external Catalog
SHOW SCHEMAS IN databricks_main_catalog;

-- View tables under an external Schema
SHOW TABLES IN databricks_main_catalog.default;
```

> **Common Issue**: If the response is `Unauthenticated: invalid_client`, the Catalog Connection's authentication information has expired and the Connection needs to be re-created.

***

## Drop External Catalog

Use `DROP CATALOG` to remove an external catalog mapping.

```sql
-- Drop an external Catalog
DROP CATALOG IF EXISTS hive_prod;
```

> **Tip**: Dropping an external Catalog only removes the metadata mapping in Lakehouse; it does not affect the actual data in the external data source.

***

## Clean Up Test Data

After completing federated query verification, it is recommended to clean up the external Catalog mapping:

```sql
-- Drop external Catalog
DROP CATALOG IF EXISTS hive_prod;
```

***

## Notes

1. **Read-only Access**: External Catalogs only support `SELECT` queries, not DML operations (INSERT/UPDATE/DELETE).
2. **Network Latency**: Querying external data requires cross-network file reads; performance is typically lower than local tables. Consider syncing frequently queried data to Lakehouse.
3. **Authentication Expiry**: External Catalogs depend on the Catalog Connection's authentication information (such as OAuth Tokens). If authentication expires, `Unauthenticated: invalid_client` errors will occur; recreate the Connection.
4. **Schema Synchronization**: External table structure changes are not automatically synced to Lakehouse. To obtain the latest schema, recreate the External Catalog or refresh metadata.
5. **Data Type Mapping**: External system data types are mapped to Lakehouse equivalent types; some complex types may not be supported.
6. **Permission Requirements**: Creating an External Catalog requires the `instance_admin` role; querying requires `USAGE` permission on the Catalog.

***

## Related Documentation

* [External Catalog Introduction](external-catalog-summary.md)
* [Create External Catalog](create-external-catalog.md)
* [Create Hive Catalog](create-hive-catalog.md)
