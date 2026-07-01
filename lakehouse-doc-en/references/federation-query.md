# Federation Query

Federation Query lets you query data in external data systems (Hive, Databricks, Iceberg, Snowflake, etc.) directly using standard SQL — no data migration or copying required. By creating an `EXTERNAL CATALOG`, you map an external data catalog into Lakehouse for unified cross-system queries.

---

## Supported External Data Sources

| External System | Connection Method | Typical Use Case |
|-----------------|-------------------|------------------|
| Apache Hive | Hive Metastore URIs | In-place acceleration of existing Hive warehouses, replacing Presto/Trino |
| Databricks Unity Catalog | Databricks API | Cross-platform federated analytics without moving Databricks data |
| Iceberg REST Catalog | Iceberg REST API | Query any data lake compatible with the Iceberg REST protocol |
| Snowflake Open Catalog | Iceberg REST API + OAuth | Access Iceberg tables managed by Snowflake |

---

## Core Concepts

There are three independent approaches to access external data, each suited to different scenarios:

### External Catalog (Recommended)

Maps an external data system (Hive/Databricks/Snowflake/Iceberg REST) as a top-level catalog; the Schemas and Tables underneath automatically correspond to the external system's structure:

```
External Catalog                ← Top-level catalog, maps the external system
  └── External Schema           ← Corresponds to a Schema/Database in the external system
        └── External Table      ← Corresponds to an actual table in the external system
```

Queries use three-level naming: `external_catalog.schema.table`

```sql
SELECT * FROM databricks_catalog.table_types_demo.orders_external;
```

Supports: Hive, Databricks Unity Catalog, Iceberg REST (including Snowflake Open Catalog)

### External Schema (Standalone)

Without going through an External Catalog, directly mounts an external Hive Database into the **current Workspace's internal Catalog**, using two-level naming `schema.table` (equivalent to `<current internal catalog>.schema.table`). Direct HMS mapping — all tables under the entire Database are immediately queryable, and newly added tables are automatically visible without per-table definitions.

```sql
SELECT * FROM hive_orders.order_detail LIMIT 100;
```

Supports: Hive (OSS/COS/GCS/HDFS). Read-only; DML is not supported.

### External Table (Standalone)

Creates a single table pointing to external storage under an ordinary Schema in the **current Workspace's internal Catalog**, using two-level naming `schema.table`. Unlike External Schema: column names and types can be customized, and renaming and modifying comments are supported.

```sql
CREATE EXTERNAL TABLE my_schema.delta_orders
    LOCATION 's3://bucket/orders/'
    USING DELTA;
```

Supports: Kafka, Delta Lake, Hudi. Read-only; DML is not supported.

### Comparison of the Three Approaches

| | External Catalog | External Schema (Standalone) | External Table (Standalone) |
|---|---|---|---|
| Catalog location | Independent external Catalog | Current Workspace's internal Catalog | Current Workspace's internal Catalog |
| Naming | Three-level `catalog.schema.table` | Two-level `schema.table` | Two-level `schema.table` |
| Use case | Cross-platform federated analytics | Mount an entire Hive database into the workspace | Custom mapping for a single external table |
| Supported sources | Hive, Databricks, Iceberg REST, Snowflake | Hive | Kafka, Delta Lake, Hudi |
| Schema definition | Auto-mapped from external system | Auto-mapped from HMS | Manually define column names and types |
| New external tables visible | Requires re-mapping | Automatically visible | Must be created one by one |

Selection guide: [External Catalog vs External Schema](org-hierarchy.md)

---

## Quick Start

External Catalog depends on a pre-created Catalog Connection (Storage Connection → Catalog Connection → External Catalog). For the complete configuration steps, see the [External Object User Guide](external_object_user_guide.md).

Once configured, use standard SQL to query:

```sql
-- 1. Create an External Catalog (requires a Catalog Connection first)
CREATE EXTERNAL CATALOG hive_prod
CONNECTION hive_catalog_conn;

-- 2. View all Catalogs (including external ones)
SHOW CATALOGS;
-- category = 'EXTERNAL' indicates a federated catalog

-- 3. View Schemas and tables in the external Catalog
SHOW SCHEMAS IN hive_prod;
SHOW TABLES IN hive_prod.default;

-- 4. Query directly without migrating data
SELECT * FROM hive_prod.default.orders LIMIT 100;

-- 5. Cross-system JOIN
SELECT o.order_id, u.name
FROM hive_prod.default.orders o
JOIN my_lakehouse_table u ON o.user_id = u.id;
```

---

## This Section

| Page | Description |
|------|-------------|
| [External Object User Guide](external_object_user_guide.md) | Complete operations for creating, querying, and managing External Catalog / Schema / Table |
| [Query Snowflake OpenCatalog Iceberg Tables](query-snowflake-open-catalog-iceberg-table.md) | Federated queries on Snowflake-managed Iceberg data via Iceberg REST API |
| [Databricks Unity Catalog Federation Query Practice](databricks-external-catalog-practice.md) | Full step-by-step setup guide with verified results and common error troubleshooting |

---

## Related Documentation

- [External Catalog Overview](external-catalog-summary.md) — Feature introduction, supported data sources, permission details
- [External Catalog Federation Query Guide](external-catalog-concept.md) — Detailed operation examples and architecture principles
- [Create External Catalog](create-external-catalog.md) — DDL syntax reference
- [Create Hive Catalog](create-hive-catalog.md) — Hive connection configuration details
- [In-Place Lake Acceleration Guide](lakehouse-acceleration-guide.md) — Complete guide for replacing Spark/Hive and Presto/Trino without moving data
- [Databricks Unity Catalog Federation Query Practice](databricks-external-catalog-practice.md) — Full step-by-step setup guide with verified results
