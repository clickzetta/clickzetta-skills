# Organization Hierarchy

Singdata Lakehouse uses a three-tier organization structure to manage resources and data: Instance → Workspace → Schema.

| Tier | Description | Reference |
|------|------|---------|
| Workspace | The basic unit for isolating resources and users, containing independent compute, storage, and permission configurations | [Workspace](workspace-introduction.md) |
| Schema | A database namespace for organizing data objects such as tables and views | [Schema](SCHEMA.md) |
| External Schema | A Schema that maps to an external data source | [External Schema](external-schema.md) |
| External Catalog | An external data catalog for federated queries | [External Catalog](external-catalog-summary.md) |
