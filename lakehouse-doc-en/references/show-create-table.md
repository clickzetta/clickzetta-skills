## Description

The `SHOW CREATE TABLE` command is used to obtain the creation statement of a specified table, materialized view, or view. With this command, users can easily view and copy the table creation syntax of existing database objects.

## Syntax
```
SHOW CREATE TABLE object_name;
```
**Parameter Description**

* `object_name`: Specifies the name of the database object to query. This can be a table, materialized view, or view.

##  Examples

**1. View the creation statement of a table**

To view the creation statement of a table named `t0`, you can execute the following command:
```
SHOW CREATE TABLE dy_base_a;
```
After executing this command, the system will return an output similar to the following:
```
+--------------------------------------------------------+
|                          sql                           |
+--------------------------------------------------------+
| CREATE TABLE wb.`public`.dy_base_a(
  `i` int,
  `j` int)
USING PARQUET
OPTIONS(
  'cz.storage.parquet.block.size'='134217728',
  'cz.storage.parquet.dictionary.page.size'='2097152',
  'cz.storag |
+--------------------------------------------------------+

```
**2. View the Creation Statement of the Materialized View**

If you want to view the creation statement of the materialized view named `mv`, you can use the following command:
```
SHOW CREATE TABLE mv;
```
The system will return output similar to the following:
```
+--------------------------------------------------------+
|                          sql                           |
+--------------------------------------------------------+
| CREATE MATERIALIZED VIEW qingyun.`public`.mv(
  `i` ,
  `j` )
REFRESH ON DEMAND
USING PARQUET
OPTIONS(
  'cz.storage.parquet.block.size'='134217728',
  'cz.storage.parquet.dictionary.page.size'='20971 |
+--------------------------------------------------------+
```
**3. View the Creation Statement of a View**

To view the creation statement of a view named `v0`, you can execute the following command:
```
SHOW CREATE TABLE v0;
```
The system will return output similar to the following:
```
CREATE VIEW `v0` AS
SELECT t1.id, t1.name
FROM table1 AS t1
WHERE t1.age > 18;
```
4. **View the Creation Statement of a Dynamic Table**

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