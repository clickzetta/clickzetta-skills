## Overview

The `DESCRIBE` or `DESC` command displays property information for a specified database schema. Mastering this command is essential for understanding the structure and metadata of a database schema. By using the `EXTENDED` keyword, users can obtain more detailed information such as privilege settings, creation time, etc.

## Syntax

```SQL
DESCRIBE  SCHEMA [EXTENDED] schema_name;
```

## Parameters

* `DESCRIBE` / `DESC`: These two keywords are interchangeable in this command, used to query the properties of a database schema.
* `EXTENDED`: This is an optional keyword that displays more detailed information, such as privileges, creation time, etc.
* `schema_name`: Specifies the name of the database schema whose properties are to be queried.

## Examples

Here are some usage examples of the `DESCRIBE` command:

1. Query basic property information for the schema named `ods_schema`:

   ```SQL
   DESCRIBE SCHEMA ods_schema;
   ```

2. Query detailed property information for the schema named `ods_schema`, including creator, creation time, modification time, and privilege settings:

   ```SQL
   DESCRIBE  SCHEMA EXTENDED ods_schema;
   ```

## Expected Output

After executing `DESCRIBE  SCHEMA EXTENDED ods_schema;`, the expected output may be as follows:

```Plain
+---------------------+-------------------------+
|      info_name      |       info_value        |
+---------------------+-------------------------+
| name                | testshareschema         |
| creator             | UAT_TEST                |
| created_time        | 2023-12-20 22:54:17.162 |
| last_modified_time  | 2023-12-20 22:54:17.162 |
| comment             |                         |
| properties          | ()                      |
| type                | shared                  |
| origin_share_schema | public                  |
| origin_share        | billing.testshareschema |
+---------------------+-------------------------+
```

In this output, users can see not only the basic information of the database schema but also detailed information such as the creator, creation time, and last modification time.

## Required Privileges

The user executing the DESC\[RIBE] SCHEMA statement must have the privilege to query the properties of the specified SCHEMA.

With the DESC\[RIBE] SCHEMA command, users can gain a detailed understanding of SCHEMA configuration and status, which is essential for database management and maintenance. Ensure you have obtained the necessary privileges before executing this command.
