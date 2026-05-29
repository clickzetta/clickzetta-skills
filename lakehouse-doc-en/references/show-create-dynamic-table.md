## Description

The `SHOW CREATE TABLE` command is used to obtain the creation statement of a specified table, materialized view, or view. Therefore, this article uses SHOW CREATE TABLE to view the dynamic table creation statement.

## Syntax
```
SHOW CREATE TABLE object_name;
```
**Parameter Description**

* `object_name`: Specifies the name of the database object to query. This can be a table, materialized view, or view.

##  Example

1. **View the creation statement of a dynamic table**

If you want to view the creation statement of a dynamic table named `change_table`, you can use the following command:
```
SHOW CREATE TABLE change_table;
```
The system will return output similar to the following:
```
+--------------------------------------------------------+
|                          sql                           |
+--------------------------------------------------------+
| CREATE DYNAMIC TABLE wb.`public`.change_table(
  `i` ,
  `j` )
REFRESH ON DEMAND
USING PARQUET
OPTIONS(
  'cz.storage.parquet.block.size'='134217728',
  'cz.storage.parquet.dictionary.page.size'= |
+--------------------------------------------------------+
1 row selected (0.118 seconds)

```