# View Connection Details

This feature allows users to query the detailed information of the created Connection object, including its properties, configurations, etc.

## Syntax
```SQL
{ DESC | DESCRIBE } CONNECTION [ EXTENDED ] connection_name
```
## Parameter Description

* **EXTENDED**: Optional keyword used to display property information when creating a Connection. Adding this keyword will include more detailed property information in the query results.
* **connection\_name**: The name of the created Connection.

## Usage Example

1. Query the basic information of the Connection named `my_connection`:
   ```SQL
   DESC CONNECTION catalog_storage_oss;
   +--------------------+---------------------------------------+
   |     info_name      |              info_value               |
   +--------------------+---------------------------------------+
   | name               | catalog_storage_oss                   |
   | creator            | UAT_TEST                              |
   | created_time       | 2024-12-14 20:09:40.146               |
   | last_modified_time | 2024-12-14 20:09:40.146               |
   | comment            |                                       |
   | properties         | ()                                    |
   | type               | OSS                                   |
   | enabled            | ENABLED                               |
   | ACCESS_ID          | xxxxxt7xb8NouiqLrjfnC1xx              |
   | ENDPOINT           | oss-cn-hangzhou-internal.aliyuncs.com |
   +--------------------+---------------------------------------+
   10 rows selected (0.274 seconds)

   ```