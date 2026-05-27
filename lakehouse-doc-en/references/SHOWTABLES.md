## Description
This command is used to query the list of all tables, views, and materialized views under the current database schema. By using different filter conditions, users can quickly locate the required database objects.

## Syntax 
```SQL
SHOW TABLES [IN schema_name] [LIKE 'pattern' | WHERE expr]
```
## Parameter Details

1. `LIKE pattern`: This option is optional and is used to filter by object name. It supports case-insensitive pattern matching and can use SQL wildcards `%` (representing any number of characters) and `_` (representing a single character). Example: `LIKE '%testing%'`. Note that this filter cannot be used simultaneously with the `WHERE` condition.

2. `IN schema_name`: This option is optional and allows the user to specify a particular schema name, thereby listing all database objects under that schema.

3. `WHERE expr`: This option is optional and supports users in filtering based on the fields displayed by the `SHOW TABLES` command. Users can filter the results through expressions to more accurately find the required database objects. The fields that support filtering are `table_name`, `is_view`, `is_materialized_view`, `is_external`, `is_dynamic`.
    ```
       SHOW TABLES WHERE table_name=base_a_dt;
    ```
## Usage Example

1. Query all tables under the current schema:
   ```SQL
   SHOW TABLES WHERE is_view=false AND is_materialized_view=false;
   ```
2. Query all views under the specified schema:
   ```SQL
   SHOW TABLES IN my_schema WHERE is_view=true;
   ```
3. Query tables and views under the current schema that contain "test" in their names:
   ```SQL
   SHOW TABLES LIKE '%test%';
   ```
4. Query all materialized views under the current schema:
   ```SQL
   SHOW TABLES WHERE is_materialized_view=true;
   ```
5. Query all dynamic tables under the current schema:
   ```SQL
   SHOW TABLES WHERE is_dynamic=true;
   ```