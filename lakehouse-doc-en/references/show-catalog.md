## Description

`SHOW CATALOGS` lists all accessible Catalogs in the current workspace, including locally managed Catalogs and External Catalogs.

## Syntax

```SQL
SHOW CATALOGS;
```

This command does not accept any parameters.

## Return Fields

| Field | Description |
|------|------|
| `workspace_name` | Catalog name |
| `created_time` | Catalog creation time |
| `category` | Catalog type: `MANAGED` (locally managed), `SHARED` (shared dataset), `EXTERNAL` (external catalog, e.g., Hive, Databricks) |

## Examples

```SQL
SHOW CATALOGS;
+----------------------------+-------------------------+----------+
|       workspace_name       |      created_time       | category |
+----------------------------+-------------------------+----------+
| clickzetta_sample_data     | 2025-01-15 10:27:21.738 | SHARED   |
| databricks_main_catalog    | 2025-11-20 12:00:49.498 | EXTERNAL |
+----------------------------+-------------------------+----------+
```

View the list of Schemas in an external Catalog:

```SQL
SHOW SCHEMAS IN clickzetta_sample_data;
```

## Notes

* Only Catalogs that the current user has permission to access are displayed. Catalogs without permission will not appear in the results.
* External Catalogs (`EXTERNAL` type) must be registered in advance via `CREATE EXTERNAL CATALOG`, and the corresponding Catalog Connection must be in a connected state to be accessed normally.
* To view Schemas and tables within a Catalog, use `SHOW SCHEMAS IN catalog_name` and `SHOW TABLES IN catalog_name.schema_name`.
