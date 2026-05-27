# Materialized View Creation and Usage

## Function Introduction

Based on the query of existing tables, create a new materialized view in the currently specified Schema and populate the view with query data.

For more detailed information, please refer to [Materialized View](MATERIALIZEDVIEW.md).

## Syntax Description
```SQL
CREATE [OR REPLACE | IF NOT EXISTS] MATERIALIZED VIEW mv_name
[ (column_list) ] 
[CLUSTERED BY (column_name)]
[PARTITIONED BY (column_name)]
[ COMMENT view_comment ] 
[BUILD DEFERRED|BUILD IMMEDIATE]
[refreshOption]
[DISABLE QUERY REWRITE]
AS <query>;  

refreshOption ::=
    REFRESH 
    [START WITH timestamp_expr]  [interval_time] VCLUSTER vcname
```
**Required Parameters**

1. dtname: Specifies the name of the materialized view.
2. AS query: The query statement contained in the materialized view.

**Optional Parameters**

1. IF NOT EXISTS: Optional. If the specified materialized view name exists, the system will not report an error, but the materialized view will not be created successfully. Cannot be used simultaneously with OR REPLACE.

2. OR REPLACE: In traditional databases, this option is used to replace the old object with a new one within the same transaction and delete the old object's data. However, in Lakehouse, to support the addition, deletion, and modification operations of materialized views, we retain data and metadata permission information. This means that even when modifying table structures or SQL logic, the original data will not be lost. This feature is particularly suitable for adding or deleting columns, adjusting SQL processing logic, and changing data types. Please note that you must use the BUILD DEFERRED ...DISABLE QUERY REWRITE syntax when modifying, which will disable the materialized view rewrite function. If the user is not simply deleting columns / adding columns, adding column definitions: it can only be passed through from the table via SELECT, and cannot participate in any calculations that affect other columns such as join key, group key, etc.
Then after Create Or Replace occurs, the REFRESH task will degrade to a full refresh. If you want to experience incremental computing features, please use [DYNAMIC TABLE](dynamic-table-introduce.md)
```
  --Modify scheduling cycle
--Original table
CREATE MATERIALIZED VIEW  mv_table
REFRESH interval 10 minute vcluster default
AS select * from student02;
--After modification
CREATE OR REPLACE MATERIALIZED VIEW  mv_table
BUILD DEFERRED 
REFRESH
interval 20 minute vcluster default
DISABLE QUERY REWRITE
AS select * from student02;--Modify computing cluster
--Original table
CREATE MATERIALIZED VIEW  mv_table
REFRESH
interval 10 minute vcluster default
AS select * from student02;
--After modification
CREATE OR REPLACE MATERIALIZED VIEW  mv_table
BUILD DEFERRED 
REFRESH interval 10 minute vcluster alter_vc
DISABLE QUERY REWRITE
AS select * from student02;

--Add column
--Create a base table
DROP TABLE  IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
--Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;

CREATE MATERIALIZED VIEW mv_table (i, j) AS
SELECT    *
FROM      mv_base_a;

--Refresh MATERIALIZED VIEW
REFRESH   MATERIALIZED VIEW mv_table;

--Query data
SELECT * FROM mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
--Add a column col
CREATE OR REPLACE MATERIALIZED VIEW mv_table 
(i, j, col) 
BUILD DEFERRED DISABLE QUERY REWRITE AS
SELECT    i,
          j,
          j * 1
FROM      mv_base_a;

--Next refresh will be a full refresh because new processing logic is added
REFRESH   MATERIALIZED VIEW mv_table;
SELECT    *
FROM      mv_table;
+---+----+-----+
| i | j  | col |
+---+----+-----+
| 1 | 10 | 10  |
| 2 | 20 | 20  |
| 3 | 30 | 30  |
| 4 | 40 | 40  |
+---+----+-----+ --Remove column
DROP      TABLE IF EXISTS mv_base_a;

CREATE    TABLE mv_base_a (i int, j int);

INSERT    INTO mv_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

--Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;

CREATE MATERIALIZED VIEW mv_table (i, j) AS
SELECT    *
FROM      mv_base_a;

--Refresh MATERIALIZED VIEW
REFRESH   MATERIALIZED VIEW mv_table;

--Query data
SELECT    *  FROM      mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
--Materialized view modification: Remove column
--Materialized view modification: Remove column
CREATE OR REPLACE MATERIALIZED VIEW mv_table 
(i, j) 
BUILD DEFERRED DISABLE QUERY REWRITE AS
SELECT    i,
          j
FROM      mv_base_a;

--At this time, the query in the table will have one less column, and the refresh will be incremental.
SELECT    *
FROM      mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+--Modify SQL syntax definition
--Create a base table
DROP TABLE  IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
--Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;
CREATE MATERIALIZED VIEW mv_table (i, j) AS
SELECT    *
FROM      mv_base_a;
--Refresh MATERIALIZED VIEW
REFRESH   MATERIALIZED VIEW mv_table;
--Query data
SELECT    *    FROM      mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
--Modify where filter condition
CREATE OR REPLACE MATERIALIZED VIEW mv_table
(i,j)
BUILD DEFERRED DISABLE QUERY REWRITE
AS select * from mv_base_a where i>3;
--At this time, the refresh will be a full refresh once
refresh MATERIALIZED VIEW mv_table;
select * from mv_table;
+---+----+
| i | j  |
+---+----+
| 4 | 40 |
+---+----+
```
3. \<column\_list>:

* You can specify the column names or add comment information to the columns of the materialized view. You can specify the column names but cannot specify the column types. The types are inferred from the SELECT results in `AS <query>`. If you want to specify the types, you can explicitly use CAST conversion in the SELECT results.
* If any column in the table is based on an expression, it is recommended to provide a name for each column. Alternatively, use aliases in \<query>.
```SQL
--Specify the comment for the column, it is recommended to specify the column name when there is an expression
CREATE MATERIALIZED VIEW mv
(i,j_dd comment'test')
AS select i,j+1 from mv_base_a;
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| i           | int       |         |
| j_dd        | int       | test    |
+-------------+-----------+---------+
--Use alias when there is a column operation expression
CREATE MATERIALIZED VIEW mv
AS select i,j+1 as j_add from mv_base_a;
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| i           | int       |         |
| j_add       | int       |         |
+-------------+-----------+---------+
```

4. partitioned by (\<col> ): Specify partitioning, using the columns in \<column\_list> as partitions. Partitioning is a method to speed up queries by grouping similar rows together at the time of writing. Using partitions can achieve data pruning and optimize queries.

   ```SQL
      CREATE MATERIALIZED VIEW mv
      (i,j_dd comment'test')
      partitioned by(j_dd)
      AS select i,j+1 from mv_base_a;
   ```
5. CLUSTERED BY: Optional, specifies the Hash Key. Lakehouse will perform a hash operation on the specified column and distribute the data into various data buckets based on the hash value. To avoid data skew and hotspots, and to improve parallel execution efficiency, it is recommended to choose columns with a large range of values and few duplicate key values as the Hash Key. This usually has a noticeable effect when performing join operations. It is recommended to use CLUSTERED BY in scenarios with large amounts of data, generally with a bucket size between 128MB and 1GB. If no bucketing is specified, the default is 256 buckets.

* SORTED BY: Optional, specifies the sorting method of fields within the Bucket. It is recommended to keep SORTED BY consistent with CLUSTERED BY for better performance. When the SORTED BY clause is specified, the row data will be sorted according to the specified columns.

```SQL
--Create a bucketed table
CREATE MATERIALIZED VIEW mv (i, j_dd COMMENT 'test') 
CLUSTERED BY (j_dd) INTO 16 BUCKETS AS
SELECT    i,
          j + 1
FROM      mv_base_a;
--Create a bucketed table and specify sorting
CREATE MATERIALIZED VIEW mv 
(i, j_dd COMMENT 'test') 
CLUSTERED BY (j_dd) SORDERD BY (j_dd) INTO 16 BUCKETS  
AS
SELECT    i,
          j + 1
FROM      mv_base_a;
```
6. COMMENT: Specify the comment information of the materialized view

7. BUILD DEFERRED: This is a way to create a materialized view. Unlike `BUILD IMMEDIATE` which generates data immediately, `BUILD DEFERRED` allows the creation of the materialized view without generating data immediately. The default value is BUILD IMMEDIATE, and when using the CREATE OR REPLACE syntax, it must be BUILD DEFERRED

 8. refreshOption Optional, refresh option
   * START WITH timestamp\_exp Specifies the start time, supports specifying a timestamp expression. If START WITH is not written, the refresh starts from the current time
     * The `timestamp_expression` returns a standard timestamp type expression. The earliest timestamp specified by TIMESTAMP AS OF depends on the [TIME TRAVEL](TIMETRAVEL.md)(data\_retention\_days) parameter. If the specified version does not exist, an error will be reported. If not specified, the version data of the current timestamp will be used, for example:
       \* `'2023-11-07 14:49:18'`, a string that can be forcibly converted to a timestamp.
       \* `cast('2023-11-07 14:49:18 Asia/Shanghai' as timestamp)`.
       \* `current_timestamp() - interval '12' hours`.
       \* Any other expression that is itself a timestamp or can be forcibly converted to a timestamp.
```
-- Specify to start refreshing the next day, with a refresh interval of 20 hours
CREATE MATERIALIZED VIEW mydt
     (i,j)
     REFRESH
     START WITH current_timestamp() +INTERVAL '1' DAY
     INTERVAL '20' HOUR
    vcluster test_alter AS
    SELECT    *
    FROM      mv_base_a;
```
* `interval_time` specifies the time interval and supports [interval types](INTERVAL.md). If `interval_time` is not specified but `START WITH` is provided, the refresh will only occur once at the time specified by `START WITH`. The `interval_time` intervals are as follows:

| Syntax                               | Description                    | Example                                                     |
| ------------------------------------ | ------------------------------ | ----------------------------------------------------------- |
| INTERVAL '\[+ \| -]' DAY             | Specifies only the DAY interval | INTERVAL '1' DAY means 1 day                                 |
| INTERVAL '\[+ \| -]' HOUR            | Specifies only the HOUR interval | INTERVAL '23' HOUR means 23 hours                            |
| INTERVAL '\[+ \| -]' MINUTE          | Specifies only the MINUTE interval | INTERVAL '59' MINUTE means 59 minutes                        |
| INTERVAL '\[+ \| -]' SECOND          | Specifies only the SECOND interval | INTERVAL '59.999' SECOND means 59.999 seconds                |
| INTERVAL '\[+ \| -] ' DAY TO HOUR    | Specifies both DAY and HOUR intervals | INTERVAL '1 23' DAY TO HOUR means 1 day and 23 hours         |
| INTERVAL '\[+ \| -] ' DAY TO MINUTE  | Specifies DAY, HOUR, and MINUTE intervals | INTERVAL '1 23:59' DAY TO MINUTE means 1 day, 23 hours, and 59 minutes |
| INTERVAL '\[+ \| -] ' DAY TO SECOND  | Specifies DAY, HOUR, MINUTE, and SECOND intervals | INTERVAL '1 23:59:59.999' DAY TO SECOND means 1 day, 23 hours, 59 minutes, and 59.999 seconds |

day: The range is \[0, 2147483647]. hour: The range is \[0, 23]. minute: The range is \[0, 59]. second: The range is \[0, 59.999999999].

* The minimum value for INTERVAL is 1 minute, which can be represented as 60 SECOND or 1 MINUTE.
  * INTERVAL supports both quoted and unquoted formats. The following are equivalent:
    * INTERVAL "60 SECOND"
    * INTERVAL '60 SECOND'
    * INTERVAL 60 SECOND
  * Supported units for INTERVAL: SECOND, MINUTE, HOUR, DAY
  * INTERVAL units are case-insensitive, so HOUR and hour are equivalent.

* Specify the compute cluster in `refreshOption`. Automatic refresh consumes resources, so you need to explicitly specify the compute cluster. If not specified, the current session's compute cluster will be used by default. You can check the current session's compute cluster with `SELECT current_vcluster()`.
  ```SQL
  CREATE MATERIALIZED VIEW my_mv (i, j)
  REFRESH   interval '1' MINUTE vcluster test AS
  SELECT    *
  FROM      mv_base_a;
  ```
8. DISABLE QUERY REWRITE: This means that the materialized view does not support the query rewrite feature. Query rewrite refers to the database optimizer automatically determining whether the result can be obtained by querying the materialized view when querying the base table of the materialized view. If possible, it avoids aggregation or join operations and directly reads data from the already calculated materialized view.

## Notes

* The incremental refresh of the materialized view is based on the historical version of the base table. The historical version depends on the [TIME TRAVEL](TIMETRAVEL.md) (data_retention_days) parameter. If the specified version does not exist, an error will be reported. This parameter defines the length of time that deleted data is retained. By default, Lakehouse retains data for one day. Depending on your business needs, you can extend or shorten the data retention period by adjusting the `data_retention_days` parameter. Please note that adjusting the data retention period may affect storage costs. Extending the retention period will increase storage requirements, which may increase related costs.

## Examples

**Example 1 Simple Materialized View**

This example demonstrates how to create a table (`inventory`) and how to create a materialized view (`mv_inventory_basic`) based on that table. Then, a piece of data is inserted, data is selected from the materialized view, the materialized view is refreshed, and finally, data is selected from the materialized view again to observe the effect of manually refreshing the materialized view.
```SQL
-- Create a table named inventory, including fields product_ID, wholesale_price, and description
CREATE TABLE inventory (product_ID INTEGER, wholesale_price FLOAT, description VARCHAR);

-- If the materialized view mv_inventory_basic does not exist, create the view, selecting the fields product_ID, wholesale_price, and description from the inventory table
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_inventory_basic AS
SELECT product_ID, wholesale_price, description
FROM inventory;

-- Insert a data entry into the inventory table:
INSERT INTO inventory (product_ID, wholesale_price, description) VALUES 
    (1, 1.00, 'cog');

-- Select the fields product_ID and wholesale_price from the materialized view mv_inventory_basic to view the content of the view after the data insertion
SELECT product_ID, wholesale_price FROM mv_inventory_basic;

-- Refresh the materialized view mv_inventory_basic to ensure the view content is consistent with the base table
REFRESH MATERIALIZED VIEW mv_inventory_basic;

-- Select the fields product_ID and wholesale_price from the materialized view mv_inventory_basic again to view the content of the view after the refresh
SELECT product_ID, wholesale_price FROM mv_inventory_basic;
```
The above SQL statements demonstrate how to create and use materialized views. In practice, materialized views can significantly improve query performance, especially when dealing with complex calculations or large amounts of data. By refreshing the materialized view, you ensure that the view data remains consistent with the source table data, providing the latest query results. **Note: Since no scheduling parameters were used when creating the materialized view, manual refresh is required here**.

**Example 2 Materialized View with Column List and Comments**
```SQL
CREATE MATERIALIZED VIEW mv_inventory_with_comment
(product_ID, wholesale_price, description)
COMMENT 'This is a materialized view for inventory'
AS
SELECT product_ID, wholesale_price, description
FROM inventory;
```
**Example 3 Materialized View with Partitioning and Clustering**
```SQL
CREATE MATERIALIZED VIEW mv_inventory_partitioned_clustered

(product_ID, wholesale_price, description)

PARTITIONED BY (product_ID)

CLUSTERED BY (product_ID)

AS

SELECT product_ID, wholesale_price, description

FROM inventory;
```
**Example 4 Materialized View with Refresh Option and Virtual Compute Cluster**
```SQL
CREATE MATERIALIZED VIEW mv_inventory_refresh

REFRESH START WITH current_timestamp INTERVAL '1 HOUR' VCLUSTER default

AS

SELECT product_ID, wholesale_price, description

FROM inventory;
```
Modify the refresh period of a materialized view with refresh options:
```SQL
CREATE OR REPLACE MATERIALIZED VIEW mv_inventory_refresh

BUILD DEFERRED

REFRESH START WITH current_timestamp INTERVAL '1 MINUTE' VCLUSTER default

DISABLE QUERY REWRITE

AS

SELECT product_ID, wholesale_price, description

FROM inventory;
```
View and modify results:
```SQL
DESC EXTENDED mv_inventory_refresh;
```
You can see that the value of `refresh_interval_second` is already 60, indicating that the table name modification refresh cycle was successful.
For materialized views that automatically refresh periodically, if you need to pause or resume automatic refreshing, please refer to:
[Modify Materialized View](alter-materialized-view.md)

**Example 5 Comprehensive Example**
```SQL
CREATE MATERIALIZED VIEW mv_inventory_full
(product_ID, wholesale_price, description)
COMMENT 'Materialized view with partition, clustering, and refresh options'
PARTITIONED BY (product_ID)
CLUSTERED BY (wholesale_price)
REFRESH START WITH current_timestamp INTERVAL '1 day' VCLUSTER 'default_ap'
AS
SELECT product_ID, wholesale_price, description
FROM inventory;

```
**Example 6: Create a Materialized View and Add Comments**

Rebuilding MATERIALIZED VIEW can reuse the last result. The scenario includes adding columns, which can reuse the previous mv, and the new columns will show old data as null.

**Case**
```SQL
CREATE    TABLE employees (
          emp_id int,
          emp_name varchar,
          dept_id int,
          salary int
          );

-- Create a test table to store department information
CREATE    TABLE departments (
          dept_id int,
          dept_name varchar,
          LOCATION varchar
          );

-- Insert some data into the employees table
INSERT    INTO employees
VALUES    (1001, 'Zhang San', 10, 5000),
          (1002, 'Li Si', 20, 6000),
          (1003, 'Wang Wu', 10, 7000),
          (1004, 'Zhao Liu', 30, 8000),
          (1005, 'Sun Qi', 40, 9000);

-- Insert some data into the departments table
INSERT    INTO departments
VALUES    (10, 'Sales', 'Beijing'),
          (20, 'R&D', 'Shanghai'),
          (30, 'Finance', 'Guangzhou'),
          (40, 'HR', 'Shenzhen');

-- Create a materialized view to store the number of employees and average salary for each department
CREATE materialized VIEW dept_emp_stats AS
SELECT    d.dept_id,
          d.dept_name,
          d.location,
          count(e.emp_id) AS emp_count,
          avg(e.salary) AS avg_salary
FROM      departments d
JOIN      employees e ON d.dept_id = e.dept_id
GROUP BY  d.dept_id,
          d.dept_name,
          d.location;

SELECT    *
FROM      departments;

-- Add a column to the departments table
ALTER     TABLE departments ADD COLUMN col1 string;

INSERT    INTO employees
VALUES    (1001, 'aa', 10, 5000);

-- Use create or replace syntax to add a column. Adding a column to avoid recalculation will reuse the last result, you can see the table used in the job profile directly from the last mv
CREATE OR       
REPLACE materialized VIEW dept_emp_stats build deferred disable QUERY rewrite AS
SELECT    d.dept_id,
          d.dept_name,
          d.location,
          any_value (d.col1) col1,
          count(e.emp_id) AS emp_count,
          avg(e.salary) AS avg_salary
FROM      departments d
JOIN      employees e ON d.dept_id = e.dept_id
GROUP BY  d.dept_id,
          d.dept_name,
          d.location;

-- The query result contains the last result
SELECT    *
FROM      dept_emp_stats;
```