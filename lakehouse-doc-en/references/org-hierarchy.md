# Organization Hierarchy

Singdata Lakehouse uses a four-tier organization structure to manage resources and data: Instance → Catalog → Schema → Data Objects.

![](/.topwrite/assets/20-org-hierarchy.svg)

```
Instance
├── Workspace                          ← Internal Catalog, resource isolation unit
│   ├── Schema                         ← Namespace, organizes tables/views/functions
│   │   └── Tables, Views, Functions, etc.
│   └── External Schema                ← Special Schema that maps an external Hive data source
└── External Catalog                   ← External data catalog, entry point for federated queries
    └── External Schema
        └── External Table
```

## Tier Descriptions

| Tier | Description | Reference |
|------|-------------|-----------|
| Instance | The top-level resource unit, corresponding to one Singdata Lakehouse instance. Instance-level configuration is shared across all Workspaces. | [Managing Instances](managing-instance.md) |
| Workspace | The resource isolation unit within an instance, essentially an internal Catalog. Contains independent users, permissions, compute clusters, and data objects. Different Workspaces are invisible to each other by default. | [Workspace](om-workspace.md) |
| External Catalog | An external data catalog at the same level as a Workspace, mapping external data systems such as Hive, Databricks, and Snowflake for federated queries. | [External Catalog](external-catalog-concept.md) |
| Schema | The namespace within a Workspace, used to organize data objects by business domain or data layer (e.g., `ods`, `dwd`, `ads`). | [Schema](om-schema.md) |
| External Schema | A special Schema within a Workspace that maps an external Hive data source, enabling direct queries without data migration. | [External Schema](external-schema.md) |

## Recommendations

**When to create multiple Workspaces:**
- Isolating development, test, and production environments
- Different business teams need independent permissions and compute resources
- Business units that require separate billing

**When to create multiple Schemas:**
- Dividing by data layer within the same team (ODS / DWD / ADS)
- Dividing by business domain within the same Workspace (orders, users, products)
- Granting permissions to different data collections as a whole

**When to use External Catalog vs. External Schema:**

| Scenario | Recommendation |
|----------|----------------|
| Querying external systems such as Hive, Databricks, or Snowflake | External Catalog |
| Mounting an external Hive database into the current Workspace for direct `schema.table` references | External Schema |
| Federated queries across platforms without data migration | External Catalog |

**In-place data lake acceleration**: Data stays in the original object storage (OSS/COS/S3/HDFS). Connect it to Lakehouse via External Catalog or External Schema, then use Lakehouse directly as a replacement for Spark/Hive for ETL processing, or as a replacement for Presto/Trino for ad-hoc queries — no data migration required, and you immediately gain Lakehouse's performance and SQL capabilities.

## Related Documentation

- [Workspace](om-workspace.md) — Create, manage members, configure roles
- [Schema](om-schema.md) — Create, switch, cross-Schema references
- [External Catalog](external-catalog-concept.md) — Federated queries on external data systems
- [External Schema](external-schema.md) — Map external Hive data sources
- [In-Place Data Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md) — Rapid POC validation, replace Spark/Hive and Presto/Trino without moving data
