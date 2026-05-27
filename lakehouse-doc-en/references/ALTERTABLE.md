# Modify Table Properties

## 1. Rename Table

Function: Using the ALTER TABLE command, you can rename an existing table to a new table name.

Syntax:
```SQL
ALTER EXTERAL TABLE name RENAME TO new_table_name;
```
Example:
```SQL
ALTER TABLE old_table_name RENAME TO new_table_name;
```
## 2. Modify Table Comments

Function: Using the ALTER TABLE command, you can add or modify comments for external tables.

Syntax:
```SQL
ALTER TABLE tbname SET COMMENT '';
```
Example:
```SQL
ALTER TABLE new_pepole_delta SET COMMENT 'new_pepole_delta';
```
After executing the above command, you can use the DESC EXTENDED command to view detailed information about the table, including comments:
```SQL
DESC EXTENDED new_pepole_delta;
+------------------------------+--------------------------------------------------------+---------+
|         column_name          |                       data_type                        | comment |
+------------------------------+--------------------------------------------------------+---------+
| id                           | int                                                    |         |
| name                         | string                                                 |         |
| dt                           | string                                                 |         |
| # Partition Information      |                                                        |         |
| # col_name                   | data_type                                              | comment |
| dt                           | string                                                 |         |
|                              |                                                        |         |
| # detailed table information |                                                        |         |
| schema                       | public                                                 |         |
| name                         | new_pepole_delta                                       |         |
| creator                      | UAT_TEST                                               |         |
| created_time                 | 2024-05-24 14:04:17.517                                |         |
| last_modified_time           | 2024-12-30 11:47:32.806                                |         |
| comment                      | new_pepole_delta                                       |         |
| properties                   | ()                                                     |         |
| external                     | true                                                   |         |
| type                         | TABLE                                                  |         |
| clustered_keys               | RANGE (__dt)                                           |         |
| bucket_count                 | 0                                                      |         |
| format                       | delta                                                  |         |
| location                     | "oss://function-compute-my1/delta-format/uploaddelta/" |         |
| connection                   | ql_ws.oss_delta                                        |         |
| statistics                   | NULL rows NULL bytes                                   |         |
+------------------------------+--------------------------------------------------------+---------+
```
## 3. Modify Table Properties

Function: Using the ALTER TABLE command, you can set or modify properties for an external table. Currently reserved parameters.

Syntax:
```
ALTER TABLE table_name SET PROPERTIES("key"="value");
```
Parameters Supported by Tables

The following table lists system properties along with their descriptions and value ranges:

| Parameter Name           | Description                                                                                       | Value Range                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| data\_lifecycle          | Data lifecycle                                                                                    | Positive integer greater than 0, a value of -1 indicates that the lifecycle is not enabled                        |
| data\_retention\_days    | Sets the Time Travel retention period, which determines how long you can access historical data, including using UNDROP, TABLE STREAM, and RESTORE to access and recover historical data | You can set different data retention periods for each table to meet different business needs. The range for num is 0-90, and Lakehouse will charge separate storage fees for Time Travel |