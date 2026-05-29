#  Description

The `DROP TABLE` command is used to remove a table from the database. In Lakehouse, using `DROP TABLE` can delete external tables. This operation does not delete the actual data in the table, only the metadata objects in the Lakehouse.

# Syntax
```sql
DROP TABLE [ IF EXISTS ] [ schema_name. ] table_name;
```
# Parameter Description

- **IF EXISTS**: (Optional) If the specified table does not exist, using this option can prevent the system from throwing an error.
- **schema_name**: (Optional) Specifies the schema name of the table to be deleted. If not specified, the current user's schema will be used by default.
- **table_name**: The name of the table to be deleted.

# Example

1. **Delete a table under the current schema**:
   ```sql
   DROP TABLE my_table;
   ```
2. **Delete the table, no error if it does not exist**:
   ```sql
   DROP TABLE IF EXISTS my_table;
   ```
3. **Delete tables under a specific schema**:
   ```sql
   DROP TABLE my_schema.my_table;
   ```
4. **Delete tables under a specific schema without reporting an error if they do not exist**:
   ```sql
   DROP TABLE IF EXISTS my_schema.my_table;
   ```