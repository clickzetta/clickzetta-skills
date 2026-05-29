## Features
`SHOW CACHED STATUS` command is used to view the status of tables cached in the current database. It is important to note that this command can only display tables that have been manually added to the cache using the `CACHE` command, and cannot display tables that are automatically cached by the system.

## Syntax
```
SHOW CACHED STATUS;
```
## Instructions
- After using the `SHOW CACHED STATUS` command, all tables currently being cached and their related information will be listed.
- This command will not display tables cached due to the system's automatic caching mechanism, only those explicitly added by the user through the `CACHE` command.

## Example
```
-- Add the partition tables part and nation from tpch100g to the cache
CACHE TABLE tpch100g.part, nation;

-- View the current status of cached tables
SHOW CACHED STATUS;
```
After executing the above command, a result similar to the following will be displayed:
```
+----------------+--------+-------+
| Table           | Refs   | Cache |
+----------------+--------+-------+
| tpch100g.part  | 10     | YES   |
| tpch100g.nation| 5      | YES   |
+----------------+--------+-------+
```
In this result, the `Table` column shows the name of the table, the `Refs` column shows the number of references to the table, and the `Cache` column shows whether the table is being cached.