# Description

This command is used to query all CONNECTION objects in the current Workspace.

# Syntax

```SQL
SHOW CONNECTIONS [ LIKE '<pattern>' | WHERE <expr>];
```

## Parameter Description
1. `LIKE pattern`: This option is optional and is used to filter by object name. It supports case-insensitive pattern matching and can use the SQL wildcards `%` (matches any number of characters) and `_` (matches a single character). Example: `LIKE '%testing%'`. Note that this filter cannot be used simultaneously with the `WHERE` clause.


2. `WHERE expr`: This option is optional and allows users to filter based on the fields displayed by the `SHOW CONNECTIONS` command. Users can filter results using expressions for more precise lookup of the desired database objects. The supported filter fields are:
  `name`, `category`, `type`, `enabled`, `created_time`


# Examples

1. Query all CONNECTIONS in the current workspace:

   ```SQL
   SHOW CONNECTIONS;
   +------------------------+----------+----------------+---------+-------------------------+
   |          name          | category |      type      | enabled |      created_time       |
   +------------------------+----------+----------------+---------+-------------------------+
   | my_funciton_connection | API      | CLOUD_FUNCTION | ENABLED | 2024-12-31 17:36:05.104 |
   +------------------------+----------+----------------+---------+-------------------------+

   ```

2. Filter using WHERE condition:

   ```
   SHOW CONNECTIONS WHERE created_time>TIMESTAMP'2024-12-30 17:36:05.104';
+------------------------+----------+----------------+---------+-------------------------+
|          name          | category |      type      | enabled |      created_time       |
+------------------------+----------+----------------+---------+-------------------------+
| my_funciton_connection | API      | CLOUD_FUNCTION | ENABLED | 2024-12-31 17:36:05.104 |
+------------------------+----------+----------------+---------+-------------------------+
```
