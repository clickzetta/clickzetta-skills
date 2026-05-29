## Description

`SHOW SCHEMAS IN CATALOG` is a SQL command used to display a list of all schemas defined in the specified catalog. Schemas are typically used to organize tables and views in a database, grouping them logically.

## Syntax
```SQL
SHOW SCHEMAS [EXTENDED] IN catalog_name;
```
### Parameter Description

* **catalog\_name**: Specifies the catalog name for listing schemas. The user must ensure that the provided catalog name exists and is accessible in the system.
* **EXTENDED**: Can display more information

## Example

Example 1
```SQL
SHOW SCHEMAS IN my_catalog;
+---------------------------------------------------------------------------+
|                                schema_name                                |
+---------------------------------------------------------------------------+
| air_travel                                                                |
| all_data                                                                  |
| automobile                                                                |
| automv_schema                                                             |
| bigquant                                                                  |
+---------------------------------------------------------------------------+
```
Example 2
```SQL
SHOW SCHEMAS  EXTENDED IN my_catalog;
+---------------------------------------------------------------------------+----------+
|                                schema_name                                |   type   |
+---------------------------------------------------------------------------+----------+
| air_travel                                                                | managed  |
| all_data                                                                  | managed  |
| automobile                                                                | managed  |
| external_hive_schema                                                      | external |
+---------------------------------------------------------------------------+----------+

```

^
