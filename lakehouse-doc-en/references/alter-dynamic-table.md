# Modify dynamic table

The Lakehouse system supports the use of `ALTER` statements for the operational management of dynamic tables:

* **Pause and start scheduling tasks**: Control the scheduling tasks automatically refreshed by the Lakehouse system.
* **Table comments**: Update the description information of the dynamic table.
* **Column names**: Modify the names of existing columns.

For modifications involving **SQL query logic changes** (i.e., the `SELECT` processing process in the dynamic table definition), the `CREATE OR REPLACE` syntax must be used. This is because dynamic tables are different from ordinary tables; their definitions include data processing logic, not just static structures. The following modifications require the use of CREATE OR REPLACE syntax. Note that if the user is not simply deleting columns / adding columns, the column definitions can only be passed through from the table via SELECT and cannot participate in any calculations that affect other columns, such as join key, group key, etc. After Create Or Replace occurs, the REFRESH task will degrade to a full refresh.

* **Scheduling cycle**: Adjust the execution frequency of scheduling tasks.
* **Compute cluster**: Specify the computing resources used to process the dynamic table.
* **Add columns**: Adding columns to the dynamic table involves changes to the SQL syntax structure.
* **Remove columns**: Adding or removing columns from the dynamic table involves changes to the SQL syntax structure.
* **Modify column types**: Involves changes to the SQL syntax structure.
* **Modify SQL syntax definitions in dynamic tables**: Involves changes to the SQL syntax structure.

# Syntax

## Pause the scheduling tasks refreshed by the Lakehouse system
```
-- Pause the refresh scheduling task of the Lakehouse system
ALTER DYNAMIC TABLE dt_name SUSPEND;
```
## Start the Lakehouse System Refresh Scheduling Task
```
-- Start the scheduling task to refresh the Lakehouse system
ALTER DYNAMIC TABLE dt_name RESUME;
```
## Modify Table Comment
```SQL
-- Modify the comment of the table
ALTER DYNAMIC TABLE dt_name SET COMMENT 'comment';
```
## Modify Column Names in Dynamic Tables
```
ALTER DYNAMIC TABLE dt_name RENAME COLUMN column_name TO new_column_name;
```
Cases
```
ALTER DYNAMIC TABLE change_table  RENAME COLUMN i TO ii;
```
## Modify the comment of a column in a dynamic table
```
ALTER DYNAMIC TABLE table_name CHANGE COLUMN column_name_identifier COMMENT 'comment'
```
Cases
```
ALTER DYNAMIC TABLE change_table  CHANGE COLUMN ii COMMENT 'comment';
```
## Modify Table Properties

Function: Using the ALTER TABLE command, you can set or modify properties for external tables. Currently reserved parameters.

Syntax:
```
ALTER TABLE table_name SET PROPERTIES("key"="value");
```
## Modify Scheduling Period

Use the OR REPLACE syntax, as shown in the example below
```
--Original Table
CREATE dynamic TABLE dt_name
REFRESH   interval 10 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;

--After Modification
CREATE OR  REPLACE dynamic TABLE dt_name
REFRESH   interval 20 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;
```
## Modify Compute Cluster

Use the OR REPLACE syntax, as shown in the example below
```
--Original Table
CREATE dynamic TABLE dt_name
REFRESH   interval 10 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;

--Modified
CREATE OR   REPLACE dynamic TABLE dt_name
REFRESH   interval 10 MINUTE vcluster alter_vc AS
SELECT    *
FROM      student02;
```
## Add Column
```SQL
-- Create a base table
DROP TABLE  IF EXISTS dy_base_a;
CREATE TABLE dy_base_a (i int, j int);
INSERT INTO dy_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
-- Use dynamic table for processing
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

-- Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;

-- Query data
SELECT    *
FROM      change_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+

-- Add a column col
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j, col) AS
SELECT    i,
          j,
          j * 1
FROM      dy_base_a;

-- The next refresh will be a full refresh because new processing logic was added
REFRESH   DYNAMIC TABLE change_table;
+---+----+-----+
| i | j  | col |
+---+----+-----+
| 1 | 10 | 10  |
| 2 | 20 | 20  |
| 3 | 30 | 30  |
| 4 | 40 | 40  |
+---+----+-----+

```
## Reduce List
```
DROP      TABLE IF EXISTS dy_base_a;

CREATE    TABLE dy_base_a (i int, j int);

INSERT    INTO dy_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

-- Use dynamic table for processing
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

-- Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;

-- Query data
SELECT    *
FROM      change_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
 -- Reduce columns
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j) AS
SELECT    i,
          j
FROM      dy_base_a;

-- At this point, querying the table will have one less column, refresh as incremental refresh.
SELECT    *
FROM      change_table;
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
DROP      TABLE IF EXISTS dy_base_a;

CREATE    TABLE dy_base_a (i int, j int);

INSERT    INTO dy_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);
-- Process using dynamic table
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

-- Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;
-- Query data
SELECT    *
FROM      change_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+

-- Modify where filter condition
CREATE OR  REPLACE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a
WHERE     i > 3;

-- At this point, a full refresh will occur
REFRESH   DYNAMIC TABLE change_table;

SELECT    *
FROM      change_table;
+---+----+
| i | j  |
+---+----+
| 4 | 40 |
+---+----+


```
## Modify Column Type

If it is a compatible type, for example, changing int to bigint. For specific compatible types, you can [refer to Modify Column Type](ALTER-TABLE-COLUMN.md) which will incrementally refresh.
```SQL
-- Create a base table
DROP      TABLE IF EXISTS dy_base_a;

CREATE    TABLE dy_base_a (i int, j int);

INSERT    INTO dy_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

-- Use dynamic table for processing
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

-- Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;

-- Query data
SELECT    *
FROM      change_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+

-- Modify column type,
CREATE OR  REPLACE DYNAMIC TABLE change_table (i, j) AS
SELECT    cast(i AS bigint),
          j
FROM      dy_base_a;

REFRESH   DYNAMIC TABLE change_table;

DESC change_table;
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| i           | bigint    |         |
| j           | int       |         |
+-------------+-----------+---------+

```
## Usage Example

1. Pause the scheduling task of the dynamic table named "dynamic\_sales":
```SQL
ALTER DYNAMIC TABLE dynamic_sales SUSPEND;
```
2. Start the scheduling task for the dynamic table named "dynamic_inventory":
```SQL
ALTER DYNAMIC TABLE dynamic_inventory RESUME;
```
3. For the dynamic table dt_name with refreshOption set, modify the computing resources used by the refresh task
```SQL
CREATE dynamic TABLE dt_name
REFRESH   interval 10 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;

CREATE OR  REPLACE dynamic TABLE dt_name
REFRESH   interval 10 MINUTE vcluster alter_vc AS
SELECT    *
FROM      student02;
```

4. Modify Existing Dynamic Table Comment

```
ALTER DYNAMIC TABLE bulk_order_items_dt SET COMMENT 'comment';
```

