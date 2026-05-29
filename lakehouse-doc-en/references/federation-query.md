# Federation Query

Federation Query lets you query data in external data systems (Hive, Databricks, Iceberg, Snowflake, etc.) directly using standard SQL — no data migration or copying required. By creating an `EXTERNAL CATALOG`, you map an external data catalog into Lakehouse for unified cross-system queries.

---

## Supported External Data Sources

| External System | Connection Method | Typical Use Case |
|---------|---------|---------|
| Apache Hive | Hive Metastore URIs | In-place acceleration of existing Hive warehouses, replacing Presto/Trino |
| Databricks Unity Catalog | Databricks API | Cross-platform federated analytics without moving Databricks data |
| Iceberg REST Catalog | Iceberg REST API | Query any data lake compatible with the Iceberg REST protocol |
| Snowflake Open Catalog | Iceberg REST API + OAuth | Access Iceberg tables managed by Snowflake |

---

## Core Concepts

**External Catalog** is the entry point for federation queries. It maps the metadata catalog of an external data system into Lakehouse, accessed using three-level naming: `catalog.schema.table`.

**External Schema** is an alternative approach that mounts an external Hive database into the current workspace, using two-level naming `schema.table`. It is better suited for integrating a Hive database into an existing workspace.

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
|------|------|
| [External Object User Guide](external_object_user_guide.md) | Complete operations for creating, querying, and managing External Catalog / Schema / Table |
| [Query Snowflake OpenCatalog Iceberg Tables](query-snowflake-open-catalog-iceberg-table.md) | Federated queries on Snowflake-managed Iceberg data via Iceberg REST API |
| [Databricks Cross-Platform Data Federation](databricks_yunqi_integration_guide_v2.md) | Best practices for cross-platform federation between Databricks Unity Catalog and Singdata Lakehouse |

---

## Related Documentation

- [External Catalog Overview](external-catalog-summary.md) — Feature introduction, supported data sources, permission details
- [External Catalog Federation Query Guide](external-catalog-concept.md) — Detailed operation examples and architecture principles
- [Create External Catalog](create-external-catalog.md) — DDL syntax reference
- [Create Hive Catalog](create-hive-catalog.md) — Hive connection configuration details
- [In-Place Lake Acceleration Guide](lakehouse-acceleration-guide.md) — Complete guide for replacing Spark/Hive and Presto/Trino without moving data