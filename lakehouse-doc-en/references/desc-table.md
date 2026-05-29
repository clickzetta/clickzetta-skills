# View Table Structure

## Description

By using the DESC or DESCRIBE statement, users can view the detailed structure information of a specified table in the Lakehouse database, including field names, data types, nullability, key information, and default values.

## Syntax

```
DESC[RIBE] [TABLE] [EXTENDED] table_name;
```

## Parameter Description

* **DESC[RIBE]**: DESC and DESCRIBE can be used interchangeably; both represent the command to describe table structure.
* **TABLE**: Optional keyword to specify that the object being viewed is a table.
* **EXTENDED**: Optional parameter. When included, additional extended information such as table size and row count is displayed.
* **table_name**: Specifies the name of the table whose structure needs to be viewed. Supports viewing TABLE, VIEW, DYNAMIC TABLE, and MATERIALIZED VIEW.

## Examples

1. View basic table structure:
   ```SQL
   DROP TABLE employees;
   CREATE TABLE employees(id int,name string,skills array<string>);
   INSERT INTO employees (id, name, skills) VALUES
   (1, 'John Doe', ['Java', 'Python', 'SQL']),
   (2, 'Jane Smith', ['C++', 'Hadoop', 'SQL']),
   (3, 'Bob Johnson', ['Python', 'Docker']);
    DESC employees;
   +-------------+---------------+---------+
   | column_name |   data_type   | comment |
   +-------------+---------------+---------+
   | id          | int           |         |
   | name        | string        |         |
   | skills      | array<string> |         |
   +-------------+---------------+---------+
   ```
   The above command displays the basic structure information of the employees table.

2. View extended table information, including table size and row count:
   ```SQL
   DESCRIBE EXTENDED employees;
   +------------------------------+-------------------------+---------+
   |         column_name          |        data_type        | comment |
   +------------------------------+-------------------------+---------+
   | id                           | int                     |         |
   | name                         | string                  |         |
   | skills                       | array<string>           |         |
   |                              |                         |         |
   | # detailed table information |                         |         |
   | schema                       | public                  |         |
   | name                         | employees               |         |
   | creator                      | UAT_TEST                |         |
   | created_time                 | 2024-12-26 20:15:41.902 |         |
   | last_modified_time           | 2024-12-26 20:16:00.901 |         |
   | comment                      |                         |         |
   | properties                   | ()                      |         |
   | type                         | TABLE                   |         |
   | format                       | PARQUET                 |         |
   | statistics                   | 3 rows 2548 bytes       |         |
   +------------------------------+-------------------------+---------+
   ```
   After executing this command, in addition to the basic table structure information, it also displays extended information such as the table's creation statement.

3. View dynamic table information:
   ```SQL
   DESC TABLE aa;
   +------------------------------+----------------------------------------------------------------------------------------------------------+---------+
   |         column_name          |                                                data_type                                                 | comment |
   +------------------------------+----------------------------------------------------------------------------------------------------------+---------+
   | id                           | int                                                                                                      |         |
   | event                        | timestamp_ltz                                                                                            |         |
   | col3                         | int                                                                                                      | comment |
   |                              |                                                                                                          |         |
   | # detailed table information |                                                                                                          |         |
   | schema                       | public                                                                                                   |         |
   | name                         | aa                                                                                                       |         |
   | creator                      | UAT_TEST                                                                                                 |         |
   | created_time                 | 2024-12-11 10:48:17.93                                                                                   |         |
   | last_modified_time           | 2024-12-13 14:53:16.158                                                                                  |         |
   | comment                      |                                                                                                          |         |
   | properties                   | ()                                                                                                       |         |
   | type                         | DYNAMIC TABLE                                                                                            |         |
   | view_text                    | SELECT test_timestamp.id, test_timestamp.event, test_timestamp.col FROM `public`.test_timestamp; |         |
   | view_original_text           | select * from public.test_timestamp;                                                                     |         |
   | source_tables                | [:.public.test_timestamp=1055409697418575788]                                                   |         |
   | query_rewrite                | disabled                                                                                                 |         |
   | refresh_type                 | on schedule                                                                                              |         |
   | refresh_start_time           | 2024-12-11 10:48:17.86                                                                                   |         |
   | refresh_interval_second      | 300                                                                                                      |         |
   | refresh_vcluster             | TEST_ALTER                                                                                       |         |
   | unique_key_is_valid          | false                                                                                                    |         |
   | unique_key_version_info      | unique_key_version: 0, explode_sort_key_version: 0, digest: , unique key infos:[]                        |         |
   | format                       | PARQUET                                                                                                  |         |
   | statistics                   | 17 rows 2976 bytes                                                                                       |         |
   +------------------------------+----------------------------------------------------------------------------------------------------------+---------+
   ```

## Notes

* Ensure you are connected to the correct database before executing the DESC or DESCRIBE command to avoid viewing incorrect table structure information.
* To view detailed information such as the table's creation statement, use the EXTENDED parameter.
