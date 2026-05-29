## Description

By using the DESC or DESCRIBE statement, users can view detailed structural information of a specified external table in the Lakehouse database, including field names, data types, whether null values are allowed, key information, and default values.

## Syntax
```
DESC[RIBE] [EXTENDED] table_name;
```
## Parameter Description

* **DESC\[RIBE**]: DESC and DESCRIBE can be used interchangeably, both representing the command to describe the table structure.
* **EXTENDED**: (Optional) Adding this keyword will display more extended information, such as file location information.
* **table\_name**: Specifies the name of the external table whose structure needs to be viewed. Supports viewing EXTERNAL TABLE, VIEW, DYNAMIC TABLE, and materialized view.

##  Example

1. **View the basic structure of an external table**:
   ```sql
   DESC my_external_table;
   +-------------------------+-----------+---------+
   |       column_name       | data_type | comment |
   +-------------------------+-----------+---------+
   | id                      | int       |         |
   | name                    | string    |         |
   | dt                      | string    |         |
   | # Partition Information |           |         |
   | # col_name              | data_type | comment |
   | dt                      | string    |         |
   +-------------------------+-----------+---------+
   ```
2. **View the Extended Structure Information of External Tables**:
   ```sql
   DESC EXTENDED my_external_table;
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
   | name                         | my_external_table                                      |         |
   | creator                      | UAT_TEST                                               |         |
   | created_time                 | 2024-05-24 14:04:17.517                                |         |
   | last_modified_time           | 2024-05-24 14:04:17.537                                |         |
   | comment                      | edelta-external                                        |         |
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

^
