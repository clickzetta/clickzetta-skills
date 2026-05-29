# Modify Materialized View
Support using the ALTER statement for the operational management of MATERIALIZED VIEW, including pausing and starting the scheduling tasks refreshed by the Lakehouse system. When creating a MATERIALIZED VIEW, using the refreshOption syntax, you can control the execution status of the task with the following statements.

For more details, please refer to [Materialized View](<MATERIALIZEDVIEW.md>).

# Modify Materialized View
The Lakehouse system supports using the `ALTER` statement for the operational management of materialized views:
* **Pause and start scheduling tasks**: Control the scheduling tasks automatically refreshed by the Lakehouse system.
* **Table comments**: Update the description information of the materialized view.
* **Column names**: Modify the names of existing columns.

For modifications involving **SQL query logic changes** (i.e., the `SELECT` processing process in the materialized view definition), the `CREATE OR REPLACE` syntax must be used. This is because dynamic tables are different from ordinary tables, as their definitions include data processing logic, not just static structures. The following modifications require using the CREATE OR REPLACE syntax:
* **Scheduling cycle**: Adjust the execution frequency of the scheduling tasks.
* **Compute cluster**: Specify the computing resources used to process the materialized view.
* **Add column**: Adding columns to the materialized view involves changes to the SQL syntax structure.
* **Remove column**: Removing columns from the materialized view involves changes to the SQL syntax structure.
* **Modify column type**: Involves changes to the SQL syntax structure.
* **Modify SQL syntax definition in the materialized view**: Involves changes to the SQL syntax structure.

# Syntax

## Pause scheduling tasks refreshed by the Lakehouse system
```
-- Pause the scheduling task of refreshing the Lakehouse system
ALTER MATERIALIZED VIEW dt_name SUSPEND;
```
## Start the Lakehouse System Refresh Scheduling Task
```
-- Start the scheduling task to refresh the Lakehouse system
ALTER MATERIALIZED VIEW mv_name RESUME;
```
## Modify the table's comment
```SQL
-- Modify the comment of the table
ALTER TABLE mv_name SET COMMENT 'comment';
```
## Modify the Column Name in a Materialized View
```
ALTER TABLE mv_name RENAME COLUMN column_name TO new_column_name;
```
Cases
```
ALTER TABLE change_table  RENAME COLUMN i TO ii;
```
## Modify the comment of a column in a materialized view
```
ALTER TABLE table_name CHANGE COLUMN column_name_identifier COMMENT 'comment'
```
Cases
```
ALTER TABLE change_table  CHANGE COLUMN ii COMMENT 'comment';
```
## Modify Table Properties

Function: Using the ALTER TABLE command, you can set or modify properties for an external table. Currently reserved parameters.

Syntax:
```
ALTER TABLE table_name SET PROPERTIES("key"="value");
```
## Modify Scheduling Period
```SQL
--Original table
CREATE MATERIALIZED VIEW  mv_table
REFRESH interval 10 minute vcluster default
AS select * from student02;
--Modified
CREATE OR REPLACE MATERIALIZED VIEW  mv_table
BUILD DEFERRED 
REFRESH
interval 20 minute vcluster default
DISABLE QUERY REWRITE
AS select * from student02;--Modify compute cluster
--Original table
CREATE MATERIALIZED VIEW  mv_table
REFRESH
interval 10 minute vcluster default
AS select * from student02;
--Modified
CREATE OR REPLACE MATERIALIZED VIEW  mv_table
BUILD DEFERRED 
REFRESH interval 10 minute vcluster alter_vc
DISABLE QUERY REWRITE
AS select * from student02;
```
## Add Column
```SQL
-- Create a base table
DROP TABLE  IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
-- Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW   IF EXISTS mv_table;
CREATE  MATERIALIZED VIEW mv_table
(i,j)
AS select * from mv_base_a;
-- Refresh MATERIALIZED VIEW
refresh MATERIALIZED VIEW mv_table;
-- Query data
select * from mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
-- Add a column col
CREATE OR REPLACE MATERIALIZED VIEW mv_table
(i,j,col)
BUILD DEFERRED DISABLE QUERY REWRITE
AS select i,j,j*1 from mv_base_a;
-- The next refresh will be a full refresh because new processing logic was added
refresh MATERIALIZED VIEW mv_table;
SELECT * FROM mv_table;
+---+----+-----+
| i | j  | col |
+---+----+-----+
| 1 | 10 | 10  |
| 2 | 20 | 20  |
| 3 | 30 | 30  |
| 4 | 40 | 40  |
+---+----+-----+ 
```
## Reduce Column
```SQL
DROP TABLE  IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
--Processing using MATERIALIZED VIEW
DROP MATERIALIZED VIEW  IF EXISTS mv_table;
CREATE  MATERIALIZED VIEW mv_table
(i,j)
AS select * from mv_base_a;
--Refresh MATERIALIZED VIEW
refresh MATERIALIZED VIEW mv_table;
--Query data
select  * from mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
--Materialized view modification: reduce columns
CREATE OR REPLACE MATERIALIZED VIEW mv_table
(i,j)
BUILD DEFERRED DISABLE QUERY REWRITE
AS select i,j from mv_base_a;
--At this time, the query in the table will have one less column, and the refresh will be incremental.
select * from mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
```
## Modify SQL Syntax Definition
```SQL
-- Create a base table
DROP TABLE IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
-- Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;
CREATE MATERIALIZED VIEW mv_table
(i,j)
AS select * from mv_base_a;
-- Refresh MATERIALIZED VIEW
refresh MATERIALIZED VIEW mv_table;
-- Query data
select * from mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
-- Modify where filter condition
CREATE OR REPLACE MATERIALIZED VIEW mv_table
(i,j)
BUILD DEFERRED DISABLE QUERY REWRITE
AS select * from mv_base_a where i>3;
-- At this point, refreshing will perform a full refresh
refresh MATERIALIZED VIEW mv_table;
select * from mv_table;
+---+----+
| i | j  |
+---+----+
| 4 | 40 |
+---+----+
```