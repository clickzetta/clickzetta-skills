# External Catalog and External Schema

External Catalog and External Schema are the **federated query entry points** in Lakehouse, letting you query external data sources (Hive, Databricks, Iceberg REST Catalog, etc.) directly with standard SQL — no data copying required.

Think of them as a "looking glass" into Lakehouse: data stays in the external system, but you can query or JOIN it directly from within Lakehouse. External Catalog is an independent top-level catalog (three-part naming: `catalog.schema.table`), suited for managing multiple external systems in one place. External Schema is a shortcut mounted into the current workspace (two-part naming: `schema.table`), better suited for everyday queries.

## Core Features

**Zero storage overhead**: Data stays in the external system (OSS/S3/HDFS). Lakehouse only reads metadata and data files — no storage costs are incurred.

**Read-only access**: Tables under External Catalog and External Schema support only SELECT queries and view creation. INSERT/UPDATE/DELETE are not supported.

**Live metadata**: Metadata is fetched in real time via HMS (Hive Metastore) or the Databricks API. External table schema changes are automatically synchronized.

## External Catalog vs External Schema

| Dimension | External Catalog | External Schema |
|---|---|---|
| **Naming** | Three-part: `catalog.schema.table` | Two-part: `schema.table` |
| **Position** | Independent top-level catalog | Schema mounted into the current workspace |
| **Use Case** | Unified management of multiple external systems | Integrating a single external database into an existing workspace |
| **Query Example** | `SELECT * FROM hive_catalog.sales_db.orders` | `SELECT * FROM hive_sales.orders` |
| **Supported Sources** | Hive, Databricks, Iceberg REST Catalog, Snowflake Open Catalog | Hive, Databricks |

### When to Use External Catalog?

| Scenario | Reason |
|---|---|
| Unified management of multiple external systems | Three-part naming is clear and well-suited for multi-catalog management |
| Cross-platform federated queries | Query Hive, Databricks, Snowflake, and other external systems simultaneously |
| Incremental data migration | Maintain business continuity during migration and validate data consistency |

### When to Use External Schema?

| Scenario | Reason |
|---|---|
| Everyday queries against external Hive data | Two-part naming is more concise — query like a local table |
| Integrating an external database into an existing workspace | Mount into the current schema without switching catalogs |
| Historical data queries | Data stays in Hive; query on demand without importing into Lakehouse |

### When Not to Use Federated Queries?

| Scenario | Recommended Alternative | Reason |
|---|---|---|
| Frequent queries or data processing | Sync data to a local Lakehouse table | Federated queries are subject to network latency; local tables perform better |
| Need to modify external data | Data sync job | Federated queries are read-only |

## Quick Examples

### External Catalog: Three-Part Naming Query

```sql
-- Step 1: Create a storage connection (pointing to OSS)
CREATE STORAGE CONNECTION oss_conn
    TYPE OSS
    ACCESS_ID = 'LTAI...'
    ACCESS_KEY = 'T8Ge...'
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com';

-- Step 2: Create a catalog connection (pointing to Hive Metastore)
CREATE CATALOG CONNECTION hive_conn
    TYPE HMS
    HIVE_METASTORE_URIS = 'thrift://192.168.1.100:9083'
    STORAGE_CONNECTION = 'oss_conn';

-- Step 3: Create an External Catalog
CREATE EXTERNAL CATALOG hive_catalog
    CONNECTION hive_conn;

-- Step 4: Query the external table (three-part naming)
SELECT * FROM hive_catalog.sales_db.orders LIMIT 5;
+----------+---------+--------+---------------------+
| order_id | user_id | amount | order_date          |
+----------+---------+--------+---------------------+
| 1001     | 501     | 199.00 | 2024-01-15 10:30:00 |
| 1002     | 502     | 299.00 | 2024-01-16 14:20:00 |
+----------+---------+--------+---------------------+
```

### External Schema: Two-Part Naming Query

```sql
-- Steps 1-2: Same as above (create Storage Connection and Catalog Connection)

-- Step 3: Create an External Schema (mapping Hive's `sales_db` database)
CREATE EXTERNAL SCHEMA hive_sales
    CONNECTION hive_conn
    OPTIONS (SCHEMA = 'sales_db');

-- Step 4: Query the external table (two-part naming, like a local table)
SELECT * FROM hive_sales.orders LIMIT 5;
-- Results same as above
```

## Frequently Asked Questions

### FAQ 1: Running DML Operations Under External Catalog/Schema

**Problem**: Attempting `INSERT INTO hive_catalog.sales_db.orders VALUES (...)`.

**Symptom**: Error `External table does not support DML operations`.

**Solution**:
- Tables under External Catalog/Schema support read-only queries only.
- To write data, first import it into a local table: `INSERT INTO local_table SELECT ... FROM hive_catalog.sales_db.orders`

### FAQ 2: Creating or Dropping Tables Under External Schema

**Problem**: Attempting `CREATE TABLE hive_sales.new_table (...)` or `DROP TABLE hive_sales.old_table`.

**Symptom**: Error `Cannot create/drop table in external schema`.

**Solution**:
- External Schema is a direct mapping of an external database; table structure is managed by the external system.
- To modify table structure, do so in the external system (e.g., Hive).

### FAQ 3: Cannot Grant Permissions on Individual External Tables

**Problem**: Attempting to grant permissions on a specific table under External Schema.

**Symptom**: Grant fails or has no effect.

**Solution**:
- Currently, tables under External Schema do not support per-table grants; only `ALL TABLES`-level grants are supported.
- For fine-grained access control, sync the data to a local Lakehouse table.

## Cost Implications

### Storage Cost

- External Catalog/Schema itself only stores metadata mappings — nearly zero storage cost.
- External data stays in OSS/S3/HDFS and is billed at the cloud provider's standard rates.

### Compute Cost

- Querying external tables consumes VCluster CRU.
- Cross-network queries against external data may be slower than local queries; consider syncing frequently queried data to local tables.

> 💡 For detailed billing rules, see the [Billing documentation](billing.md).

## Lifecycle Management

```
Create Storage Connection → Create Catalog Connection → Create External Catalog/Schema → Query/JOIN → Drop
        ↓                        ↓                        ↓                              ↓
  Configure storage credentials  Configure metadata service address  Map external system/Database  Remove mapping (external data unaffected)
```

### Create and Drop

```sql
-- Create External Catalog
CREATE EXTERNAL CATALOG hive_catalog
    CONNECTION hive_conn;

-- Create External Schema
CREATE EXTERNAL SCHEMA hive_sales
    CONNECTION hive_conn
    OPTIONS (SCHEMA = 'sales_db');

-- List all External Schemas (using EXTENDED + WHERE filter)
SHOW SCHEMAS EXTENDED WHERE type = 'external';

-- View External Schema details
DESC SCHEMA EXTENDED hive_sales;

-- Drop External Catalog (external data is unaffected)
DROP CATALOG hive_catalog;

-- Drop External Schema (external Hive database is unaffected)
DROP SCHEMA hive_sales;
```

## Related Documentation

- [Lakehouse On-Site Acceleration Implementation Guide](lakehouse-acceleration-guide.md) — POC quick validation, complete three-step implementation process
- [External Catalog Overview](external-catalog-summary.md) — Full External Catalog concepts
- [External Catalog Federated Queries](external-catalog-concept.md) — Detailed usage guide, operation examples, architecture principles
- [CREATE EXTERNAL CATALOG](create-external-catalog.md) — CREATE EXTERNAL CATALOG syntax
- [CREATE EXTERNAL SCHEMA](create-external-schema.md) — Full syntax and per-cloud-platform parameters
- [Using External Schema](use-external-schema.md) — Detailed operation guide
- [Organization Hierarchy](org-hierarchy.md) — External Catalog vs External Schema selection guide
