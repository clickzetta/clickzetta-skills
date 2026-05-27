## Description

Using the UNDROP TABLE statement, you can restore deleted tables, dynamic tables, and materialized views. Whether a deleted object can be restored depends on the data [retention period](TIMETRAVEL.md).
**Data Retention Period**:
The ability to restore historical objects depends on the data retention period. The current preview version has a default data retention period of 7 days, which will be adjusted to 1 day in the future. You can adjust the retention period by executing the [ALTER command](TIMETRAVEL.md). Please note that modifying the retention period may increase storage costs. Supported objects include tables (TABLE), dynamic tables (DYNAMIC TABLE), and materialized views.

## Syntax
```sql
UNDROP TABLE tablename;
```
## Parameter Description

* **tablename**: Specifies the name of the table to be deleted. Supports dynamic tables, internal tables, and materialized views.

## Examples

 Example 1: Recover immediately after deleting the table
```sql
-- Create table
CREATE TABLE mytable(id int, name string);
INSERT INTO mytable VALUES(1, 'aaa');
-- Drop table
DROP TABLE mytable;
-- View table deletion records, you can see the deletion time
SHOW TABLES HISTORY;
+---------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| schema_name  | table_name | create_time            | creator  | rows | bytes | comment | retention_time | delete_time             |
+---------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| undrop_schema | mytable    | 2023-06-06 12:22:57.642 | UAT_TEST | 1    | 1348  |         | 1              | 2023-07-18 17:49:26.374 |
+---------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
-- Restore table
UNDROP TABLE mytable;
```
Example 2: Create a table with the same name after deletion for recovery
```sql
-- Create table
CREATE TABLE mytable(id int, name string);
INSERT INTO mytable VALUES(1, 'aaa');
-- Drop table
DROP TABLE mytable;
-- View table deletion records
SHOW TABLES HISTORY;
-- Create table again
CREATE TABLE mytable(col1 int, col2 string);
-- View table deletion records, the delete_time of tables that have not been deleted is null
SHOW TABLES HISTORY;
+---------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| schema_name  | table_name | create_time            | creator  | rows | bytes | comment | retention_time | delete_time             |
+---------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| undrop_schema | mytable    | 2023-07-18 17:51:25.978 | UAT_TEST | 0    | 0     |         | 1              |                          |
| undrop_schema | mytable    | 2023-06-06 12:22:57.642 | UAT_TEST | 1    | 1348  |         | 1              | 2023-07-18 17:49:26.374 |
+---------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
-- Rename the table that has not been deleted
ALTER TABLE mytable RENAME TO mytable_back;
-- Restore table
UNDROP TABLE mytable;
```
Example 3: Restore Dynamic Table
```sql
-- Create a base table
DROP TABLE IF EXISTS dy_base_a;
CREATE TABLE dy_base_a (i int, j int);
INSERT INTO dy_base_a VALUES
(1, 10),
(2, 20),
(3, 30),
(4, 40);
-- Process using dynamic table
DROP DYNAMIC TABLE IF EXISTS change_table;
CREATE DYNAMIC TABLE change_table
(i, j)
AS SELECT * FROM dy_base_a;
-- Refresh dynamic table
REFRESH DYNAMIC TABLE change_table;
-- Query data
SELECT * FROM change_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
DROP DYNAMIC TABLE IF EXISTS change_table;
UNDROP TABLE change_table;
SELECT * FROM change_table;
```
Example 4: Restore Materialized View
```SQL
DROP      TABLE mv_base_a;

DROP MATERIALIZED VIEW mv1;

-- Create a base table
CREATE    TABLE mv_base_a (i int, j int);

INSERT    INTO mv_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

-- Use dynamic table for processing
CREATE MATERIALIZED VIEW mv1 (i, j) AS
SELECT    *
FROM      mv_base_a;

-- Refresh dynamic table
REFRESH   MATERIALIZED VIEW mv1;

-- Query data
SELECT * FROM mv1;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
DROP MATERIALIZED VIEW mv1;
SHOW TABLES HISTORY WHERE     table_name = 'mv1';
+-------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| schema_name | table_name |       create_time       | creator  | rows | bytes | comment | retention_time |       delete_time       |
+-------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| public      | mv1        | 2024-12-18 16:57:35.916 | UAT_TEST | 4    | 2467  |         | 1              | 2024-12-18 16:57:58.427 |
+-------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
UNDROP TABLE mv1;

SELECT * FROM mv1;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
```
## Precautions

* Please ensure that the recovery operation is performed within the data retention period, otherwise the deleted table cannot be restored.
* Before restoring the table, make sure that there is no table with the same name. If there is a table with the same name, please rename or delete the table with the same name.