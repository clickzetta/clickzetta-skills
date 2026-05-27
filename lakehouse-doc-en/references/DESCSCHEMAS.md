## Description

The `DESCRIBE` or `DESC` command is used to display the attribute information of a specified database schema (SCHEMA). Mastering this command is crucial for understanding the structure and metadata of the database schema. By using the `EXTENDED` keyword, users can obtain more detailed information, such as permission settings, creation time, etc.

## Syntax 
```SQL
DESCRIBE  SCHEMA [EXTENDED] schema_name;
```
## Parameter Details

- `DESCRIBE` / `DESC`: These two keywords are interchangeable in this command and are used to query the attributes of the database schema.
- `EXTENDED`: This is an optional keyword used to display more detailed information, such as permissions, creation time, etc.
- `schema_name`: Specifies the name of the database schema whose attributes need to be queried.

##  Example

Here are some usage examples of the `DESCRIBE` command:

1. Query the basic attribute information of the database schema named `ods_schema`:
   ```SQL
   DESCRIBE SCHEMA ods_schema;
   ```
2. Query detailed attribute information of the database schema named `ods_schema`, including creator, creation time, modification time, and permission settings:
   ```SQL
   DESCRIBE  SCHEMA EXTENDED ods_schema;
   ```
## Expected Output Result

After executing the `DESCRIBE SCHEMA EXTENDED ods_schema;` command, the expected output result may be as follows:
```Plain
+--------------------+------------------------+
|      info_name      |       info_value        |
+--------------------+------------------------+
| name               | ods_schema              |
| creator            | db_administrator        |
| created_time       | 2023-04-01 10:00:00    |
| last_modified_time | 2023-04-02 15:30:00    |
| comment            | Operational Data Store  |
+--------------------+------------------------+
```
In this output, users can not only see the basic information of the database schema but also learn detailed information such as the creator, creation time, and last modification time.

## Permission Requirements

The user executing the DESC\[RIBE] SCHEMA statement must have the permission to query the specified SCHEMA attributes.

Through the DESC\[RIBE] SCHEMA command, users can gain detailed insights into the configuration and status of the SCHEMA, which is crucial for database management and maintenance. Ensure that you have obtained the necessary permissions before executing this command.