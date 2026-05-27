## Description

In database management, understanding the structure of a table is fundamental for data analysis and data operations. The `DESC TABLE` command allows users to view the detailed structure of a specified catalog, schema, and table, including column names, data types, and column descriptions.

## Syntax
```SQL
DESC TABLE catalog_name.schema_name.table_name;
```
### Parameter Description

- **catalog_name**: Specifies the name of the catalog containing the target table.
- **schema_name**: Specifies the name of the schema containing the target table.
- **table_name**: Specifies the name of the table whose structure you want to view.



## Example
```SQL
DESC TABLE my_catalog.my_schema.my_table;
```
The above command will display the structure of the `my_table` table under `my_schema` in `my_catalog`.

## Notes

- Users need to ensure that the catalog, schema, and table names are correctly specified before executing the command.
- Users need to have sufficient permissions to access the specified catalog, schema, and table, otherwise, the command may fail due to insufficient permissions.
- Currently, using the `USE` statement to directly switch to a specific catalog is not supported; the three-level naming syntax mentioned above must be used to query the table structure.