## Description

The `SHOW TABLES HISTORY` command is used to view the history of tables, including the deletion time of deleted tables. For tables that have not been deleted, the deletion time will be displayed as null. This feature is particularly useful for recovering accidentally deleted tables through UNDROP.

## Syntax 
```
SHOW TABLES HISTORY [IN schema_name] [LIKE 'pattern' ]
```
## Parameter Description

* `LIKE pattern`: Optional parameter used to filter by object name. Supports case-insensitive pattern matching and can use SQL wildcards `%` and `_`. Note that this parameter cannot be used simultaneously with the WHERE condition.
* `IN schema_name`: Optional parameter used to specify the schema name, thereby listing the table history under the specified schema.

##  Examples

**Example 1: View Table History**
```SQL
SHOW TABLES HISTORY;
+-------------+------------------------------------------+-------------------------+-------------+----------+------------+---------+----------------+-------------------------+
| schema_name |                table_name                |       create_time       |   creator   |   rows   |   bytes    | comment | retention_time |       delete_time       |
+-------------+------------------------------------------+-------------------------+-------------+----------+------------+---------+----------------+-------------------------+
| public      | mv                                       | 2024-12-13 09:34:26.683 | UAT_TEST    | 4        | 2467       |         | 1              |                         |
| public      | mv_base_a                                | 2024-12-13 09:34:05.076 | UAT_TEST    | 4        | 1970       |         | 1              |                         |
| public      | mv_base_a                                | 2023-09-22 03:41:28.011 | UAT_TEST    | 5        | 1406       |         | 1              | 2024-12-13 09:34:04.946 |
+-------------+------------------------------------------+-------------------------+-------------+----------+------------+---------+----------------+-------------------------+
```
Executing this command will list the history of all tables in the current database.

**Example 2: View table history by schema**
```SQL
SHOW TABLES HISTORY IN my_schema;
```
The command will only display the table history under the `my_schema` schema.

**Example 3: Filter table history for a specific schema**
```SQL
SHOW TABLES HISTORY LIKE '%test%';
```
This command will list the table history that contains "test" in the name.

**Example 4: Restore accidentally deleted table**
```SQL
-- Create table and insert data
CREATE TABLE mytable (id INT, name STRING);
INSERT INTO mytable VALUES (1, 'aaa');

-- Drop table
DROP TABLE mytable;

-- View table drop history
SHOW TABLES HISTORY;

-- Undrop table
UNDROP TABLE mytable;
```
**Example 5: Create a table with the same name after deleting the table and try to restore**
```SQL
-- Create table and insert data
CREATE TABLE mytable (id INT, name STRING);
INSERT INTO mytable VALUES (1, 'aaa');

-- Drop table
DROP TABLE mytable;

-- View table deletion history
SHOW TABLES HISTORY;

-- Recreate table
CREATE TABLE mytable (col1 INT, col12 STRING);

-- View table deletion history, delete_time is null for tables not deleted
SHOW TABLES HISTORY;

-- Rename table that has not been deleted
ALTER TABLE mytable RENAME TO mytable_back;

-- Restore table
UNDROP TABLE mytable;
```

^
