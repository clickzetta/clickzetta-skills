# External Catalog

External Catalog is the federated query entry point in Lakehouse, mapping the metadata catalogs of external data systems (Hive, Databricks, Snowflake, etc.) into Lakehouse, allowing you to query external data directly with standard SQL — no data copying required.

**Difference from External Schema**: External Catalog is an independent top-level catalog accessed with three-level naming `catalog.schema.table`; External Schema is a Schema mounted into the current workspace, accessed with two-level naming `schema.table`, which is better suited for integrating Hive databases into an existing workspace. See [Organization Hierarchy](org-hierarchy.md).

## Supported Data Sources

| Data Source | Connection Method |
|--------|---------|
| Apache Hive | Hive Metastore URIs |
| Databricks Unity Catalog | Databricks API |
| Iceberg REST Catalog | Iceberg REST API |
| Snowflake Open Catalog | Iceberg REST API + OAuth |

## Use Cases

- **Cross-platform federated queries**: Query Lakehouse local data and Hive/Databricks data simultaneously — no ETL required
- **In-place data lake acceleration**: Keep data in OSS/HDFS and use Lakehouse to replace Spark/Hive for ETL or Presto/Trino for ad-hoc queries
- **Gradual migration**: Maintain business continuity through External Catalog during migration; switch over after verifying data consistency

## Permissions

Currently, only the `instance_admin` role can query the created External Catalog.

## Related Documentation

- [In-Place Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md) — Rapid POC validation, replacing Spark/Hive and Presto/Trino without moving data
- [External Catalog Federated Queries](external-catalog-concept.md) — Detailed usage guide, operation examples, architecture principles
- [Create External Catalog](create-external-catalog.md) — CREATE EXTERNAL CATALOG syntax
- [Create Hive Catalog](create-hive-catalog.md) — Hive connection configuration
- [External Schema](external-schema.md) — Mount an external Hive database into a workspace
- [Organization Hierarchy](org-hierarchy.md) — External Catalog vs External Schema selection guide
