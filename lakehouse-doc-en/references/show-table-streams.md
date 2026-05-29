## Description

This command is used to view information about all Table Streams under the current database schema. Table Streams are a type of real-time data stream that allows you to perform real-time analysis and processing of data in the table.

## Syntax
```SQL
SHOW TABLE STREAMS [IN schema_name] [LIKE 'pattern' | WHERE expr]
```
## Parameter Description

1. IN schema_name (optional): Specifies the schema name to view. If not specified, the default schema of the current user is viewed.
2. LIKE pattern (optional): Filters the command output by object name using case-insensitive pattern matching. Supports SQL wildcards (`%` and `_`). Note: Cannot be used with the WHERE clause.
3. WHERE expr (optional): Supports filtering based on the fields displayed by show table streams.

## Example

1. View all table streams under the current schema:
   ```
   SHOW TABLE STREAMS;
   ```
Result:
   ```
   +-------------------------+-------------+--------------+------------+-------------+---------+
   |       create_time       | schema_name |     name     | table_name |    mode     | comment |
   +-------------------------+-------------+--------------+------------+-------------+---------+
   | 2023-11-24 21:44:07.261 | public      | event_stream | event      | APPEND_ONLY |         |
   +-------------------------+-------------+--------------+------------+-------------+---------+
   ```
2. View all table streams under the specified schema:

   ```
   SHOW TABLE STREAMS IN my_schema;
   ```
3. View the streams of tables under the current schema that contain "test" in their names:

   ```
   SHOW TABLE STREAMS LIKE '%test%';
   ```
4. View table streams that meet specific conditions with the WHERE clause:
   ```
   SHOW TABLE STREAMS WHERE mode = 'APPEND_ONLY';
   ```