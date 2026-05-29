## Description

The `SHOW CREATE TABLE` command is used to obtain the creation statement of a specified table, materialized view, or view. Therefore, this article uses SHOW CREATE TABLE to view the creation statement of a materialized view.
## Syntax
```
SHOW CREATE TABLE object_name;
```
**Parameter Description**

* `object_name`: Specifies the name of the database object to query. This can be a table, materialized view, or view.

## Usage Example


**1. View the creation statement of a materialized view**

If you want to view the creation statement of a materialized view named `mv`, you can use the following command:
```
SHOW CREATE TABLE mv;
```
The system will return output similar to the following:
```
+--------------------------------------------------------+
|                          sql                           |
+--------------------------------------------------------+
| CREATE MATERIALIZED VIEW example.`public`.mv(
  `i` ,
  `j` )
REFRESH ON DEMAND
USING PARQUET
OPTIONS(
  'cz.storage.parquet.block.size'='134217728',
  'cz.storage.parquet.dictionary.page.size'='20971 |
+--------------------------------------------------------+
```