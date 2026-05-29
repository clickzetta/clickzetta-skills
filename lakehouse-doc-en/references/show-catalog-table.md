## Description

`SHOW TABLES IN` lists all tables in a specified Catalog and Schema, including regular tables, views, external tables, and dynamic tables.

## Syntax

```SQL
SHOW TABLES IN catalog_name.schema_name;
```

### Parameter Description

* `catalog_name`: The Catalog name, which must exist and be accessible in the system.
* `schema_name`: The Schema name, which must belong to the specified Catalog.

## Return Fields

| Field | Description |
|-------|-------------|
| `schema_name` | Schema name |
| `table_name` | Table name |
| `is_view` | Whether it is a view (`true`/`false`) |
| `is_materialized_view` | Whether it is a materialized view (`true`/`false`) |
| `is_external` | Whether it is an external table (`true`/`false`) |
| `is_dynamic` | Whether it is a dynamic table (`true`/`false`) |

## Example

List all tables in the `tpch_100g` Schema under the shared Catalog `clickzetta_sample_data`:

```SQL
SHOW TABLES IN clickzetta_sample_data.tpch_100g;
+-------------+------------+---------+----------------------+-------------+------------+
| schema_name | table_name | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+------------+---------+----------------------+-------------+------------+
| tpch_100g   | partsupp   | false   | false                | false       | false      |
| tpch_100g   | orders     | false   | false                | false       | false      |
| tpch_100g   | supplier   | false   | false                | false       | false      |
| tpch_100g   | nation     | false   | false                | false       | false      |
| tpch_100g   | customer   | false   | false                | false       | false      |
| tpch_100g   | lineitem   | false   | false                | false       | false      |
| tpch_100g   | part       | false   | false                | false       | false      |
| tpch_100g   | region     | false   | false                | false       | false      |
+-------------+------------+---------+----------------------+-------------+------------+
```

## Notes

* You must use the `catalog_name.schema_name` two-level structure to specify the query scope.
* When querying tables in an external Catalog, ensure the corresponding Catalog Connection is in a connected state.
* Use the three-level structure to query data in tables: `SELECT * FROM catalog_name.schema_name.table_name`.
