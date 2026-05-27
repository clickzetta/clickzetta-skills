## Description

This command is used to display detailed information about the specified schema, including its structure, fields, indexes, etc., to help users better understand and manage data.

## Syntax
```SQL
DESC[RIBE] SCHEMA [EXTENDED] schema_name;
```
## Parameter Description

1. **DESC[RIBE**]: DESC and DESCRIBE can be used interchangeably, both representing the command to query schema information.
2. **schema_name**: Specifies the name of the schema to be queried.
3. **EXTENDED** (optional): Adding this keyword will display more extended information about the schema, such as default values of fields, index types, etc.

##  Example

1. Query the basic information of the schema named `ods_schema`:
```
DESCRIBE SCHEMA tpch100g;
+--------------------+-------------------------+
|     info_name      |       info_value        |
+--------------------+-------------------------+
| name               | tpch100g                |
| creator            | UAT_TEST                |
| created_time       | 2024-11-29 21:10:11.892 |
| last_modified_time | 2024-11-29 21:10:11.892 |
| comment            |                         |
+--------------------+-------------------------+
```
2. Query detailed information of the schema named `ods_schema` (including default values, indexes, etc.):
```
DESCRIBE SCHEMA EXTENDED tpch100g;
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|     info_name      |                                                                                                                                                                                     |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name               | tpch100g                                                                                                                                                                            |
| creator            | UAT_TEST                                                                                                                                                                            |
| created_time       | 2024-11-29 21:10:11.892                                                                                                                                                             |
| last_modified_time | 2024-11-29 21:10:11.892                                                                                                                                                             |
| comment            |                                                                                                                                                                                     |
| properties         | (("type","hive"),("hive_schema","tpch100g"),("hive_metastore_uris","192.168.20.xxx:9083"),("fs.defaultfs","hdfs://xxxx:9000")                                                       |
| type               | external                                                                                                                                                                            |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```
3. Query the schema named `dws_schema` and use the DESC keyword:
```
DESC SCHEMA tpch100g;
+--------------------+-------------------------+
|     info_name      |       info_value        |
+--------------------+-------------------------+
| name               | tpch100g                |
| creator            | UAT_TEST                |
| created_time       | 2024-11-29 21:10:11.892 |
| last_modified_time | 2024-11-29 21:10:11.892 |
| comment            |                         |
+--------------------+-------------------------+
```