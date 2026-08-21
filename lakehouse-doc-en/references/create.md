# CREATE Command Reference

## Description

Creates various database objects in Singdata Lakehouse.

## Syntax

```sql
CREATE <object_type> [ IF NOT EXISTS ] <object_name>
    [ COMMENT '<string_literal>' ]
```

### Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `<object_type>` | The type of object to create, such as `TABLE`, `VIEW`, `SCHEMA`, etc. | Yes |
| `IF NOT EXISTS` | Silently skip if the object already exists, no error | No |
| `<object_name>` | The object name, may include a schema prefix | Yes |
| `COMMENT` | Object description/comment | No |

## Supported Object Types

| Object Type | Syntax Example | Description |
|-------------|---------------|-------------|
| Regular Table | `CREATE TABLE <name> (col1 TYPE, ...)` | Structured two-dimensional data |
| External Table | `CREATE EXTERNAL TABLE <name> USING <format>` | Data stored in external systems |
| View | `CREATE VIEW <name> AS SELECT ...` | Virtual table, does not store data |
| Dynamic Table | `CREATE DYNAMIC TABLE <name> REFRESH INTERVAL ...` | Data object with automatic incremental refresh |
| Materialized View | `CREATE MATERIALIZED VIEW <name> AS SELECT ...` | Pre-computed query results |
| Table Stream | `CREATE TABLE STREAM <name> ON TABLE <table>` | Captures table-level changes (CDC) |
| Schema | `CREATE SCHEMA <name>` | Namespace |
| External Schema | `CREATE EXTERNAL SCHEMA <name> CONNECTION <conn>` | Mount an external Schema |
| External Catalog | `CREATE EXTERNAL CATALOG <name> CONNECTION <conn>` | Mount an external catalog |
| Connection | `CREATE STORAGE/CATALOG/API CONNECTION <name> ...` | Storage/catalog/API connection configuration |
| Pipe | `CREATE PIPE <name> ... AS COPY INTO ...` | Continuous data ingestion pipeline |
| Compute Cluster | `CREATE VCLUSTER <name> ...` | Virtual compute cluster |
| Data Share | `CREATE SHARE <name>` | Cross-instance data sharing |
| Synonym | `CREATE SYNONYM <name> FOR <object>` | Object alias |
| SQL Function | `CREATE SQL FUNCTION <name> AS ...` | User-defined SQL function |
| External Function | `CREATE EXTERNAL FUNCTION <name> ...` | Function that invokes external services |
| Workspace User | `CREATE USER <name> ...` | Add an existing instance user to the current workspace |
| Role | `CREATE ROLE <name>` | Permission role |

## Required Permissions

Executing `CREATE` operations requires the corresponding creation permission (such as `CREATE TABLE`, `CREATE VIEW`, etc.) on the target Schema or workspace. See the syntax documentation for each object type for specific permission requirements.

## Notes

- Most `CREATE` statements support the `IF NOT EXISTS` clause, suitable for use in scripts or automated workflows.
- You can attach a description using the `COMMENT` clause when creating an object.
- Different object types have their own required and optional parameters; see the syntax reference below for details.

## Syntax Reference

### Data Objects
- [CREATE TABLE](create-table-ddl.md)
- [CREATE EXTERNAL TABLE](create-external-table.md)
- [CREATE VIEW](create-view.md)
- [CREATE DYNAMIC TABLE](create-dynamic-table.md)
- [CREATE MATERIALIZED VIEW](create-materialized-view.md)
- [CREATE TABLE STREAM](create-table-stream.md)

### Indexes and Synonyms
- [CREATE BLOOMFILTER INDEX](create-bloomfilter-index.md)
- [CREATE INVERTED INDEX](create-inverted-index.md)
- [CREATE VECTOR INDEX](create-vector-index.md)
- [CREATE SYNONYM](create-synonym.md)

### Schema and Catalog
- [CREATE SCHEMA](create-schema.md)
- [CREATE EXTERNAL SCHEMA](create-external-schema.md)
- [CREATE EXTERNAL CATALOG](create-external-catalog.md)

### Connections and Pipes
- [CREATE STORAGE CONNECTION](create-storage-connection.md)
- [CREATE CATALOG CONNECTION](create-catalog-connection.md)
- [CREATE API CONNECTION](create-api-connection.md)
- [CREATE PIPE](pipe-syntax.md)

### Compute and Sharing
- [CREATE VCLUSTER](create_cluster.md)
- [CREATE SHARE](create-share.md)

### Functions
- [CREATE SQL FUNCTION](create-sql-function.md)
- [CREATE EXTERNAL FUNCTION](create_external_function.md)

### Users and Permissions
- [CREATE USER](create-user.md)
- [CREATE ROLE](create-role.md)
