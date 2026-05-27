# Description

This command is used to query all CONNECTION objects in the current Workspace

# Syntax
```SQL
SHOW CONNECTIONS WHRER <expr>;
```
* `WHERE expr`: This option is an optional parameter that allows users to filter based on the fields displayed by the `SHOW CONNECTIONS` command. Users can filter the results using expressions to more accurately find the required database objects. The fields that support filtering are `name`, `category`, `type`, `enabled`, `created_time`.

# Usage Example

1. Query all CONNECTIONS in the current workspace:
   ```SQL
   SHOW CONNECTIONS;
   +------------------------+----------+----------------+---------+-------------------------+
   |          name          | category |      type      | enabled |      created_time       |
   +------------------------+----------+----------------+---------+-------------------------+
   | my_funciton_connection | API      | CLOUD_FUNCTION | ENABLED | 2024-12-31 17:36:05.104 |
   +------------------------+----------+----------------+---------+-------------------------+

   ```
 2. Filter According to WHERE Conditions

```
   SHOW CONNECTIONS WHERE created_time>TIMESTAMP'2024-12-30 17:36:05.104';
+------------------------+----------+----------------+---------+-------------------------+
|          name          | category |      type      | enabled |      created_time       |
+------------------------+----------+----------------+---------+-------------------------+
| my_funciton_connection | API      | CLOUD_FUNCTION | ENABLED | 2024-12-31 17:36:05.104 |
+------------------------+----------+----------------+---------+-------------------------+
```