# Materialized View Creation and Usage

## Description

Creates a new materialized view in the current or specified schema based on a query against existing tables, and populates the view with the query data.

A materialized view is like an auto-updating query cache -- the optimizer automatically recognizes and uses it to replace slow queries without requiring any application code changes.

For more details, see [Materialized View](MATERIALIZEDVIEW.md).

## How to Choose: Materialized View vs Dynamic Table vs View

| Object | Use Case | Reference Method |
|------|----------|----------|
| **Materialized View** | Transparently accelerate existing queries; optimizer auto-rewrites without application code changes | Optimizer auto-replaces; application code is unaware |
| **Dynamic Table** | Build data pipelines (ODS->DWD->ADS); requires explicit reference to the result table | Explicitly query the dynamic table name |
| **View** | Logical encapsulation; no data stored; real-time execution on each query | Explicitly query the view name |

## Syntax

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

1. mv_name: Specifies the name of the materialized view.
2. AS query: The query statement that the materialized view encapsulates.

**Optional Parameters**

1. IF NOT EXISTS: Optional. If a materialized view with the specified name already exists, no error is raised, but the materialized view will not be created. Cannot be used together with OR REPLACE.

2. OR REPLACE: In traditional databases, this option is used to replace an old object with a new one within the same transaction and delete the old object's data. However, in the Lakehouse, to support add, drop, and modify operations on materialized views, we retain both data and metadata permission information. This means that even when modifying table structure or SQL logic, existing data is not lost. This feature is especially useful for adding or dropping columns, adjusting SQL processing logic, and changing data types. Note that you must use the BUILD DEFERRED ... DISABLE QUERY REWRITE syntax when making modifications. This syntax disables the materialized view rewrite feature. If the user's change is not a simple drop column / add column (where the added column definition must be simply SELECT-passed through from the table without participating in any computation affecting other columns, such as join key, group key, etc.), then after Create Or Replace, the REFRESH task will degenerate into a full refresh. If you want to experience incremental computation, please use [DYNAMIC TABLE](dynamic-table-introduce.md).

```
  -- Modify refresh interval
-- Original table
CREATE MATERIALIZED VIEW  mv_table
REFRESH interval 10 minute vcluster default
AS select * from student02;
-- After modification
CREATE OR REPLACE MATERIALIZED VIEW  mv_table
BUILD DEFERRED
REFRESH
interval 20 minute vcluster default
DISABLE QUERY REWRITE
AS select * from student02;

-- Modify compute cluster
-- Original table
CREATE MATERIALIZED VIEW  mv_table
REFRESH
interval 10 minute vcluster default
AS select * from student02;
-- After modification
CREATE OR REPLACE MATERIALIZED VIEW  mv_table
BUILD DEFERRED 
REFRESH interval 10 minute vcluster alter_vc
DISABLE QUERY REWRITE
AS select * from student02;

-- Add a column
-- Create a base table
DROP TABLE  IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
-- Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;

CREATE MATERIALIZED VIEW mv_table (i, j) AS
SELECT    *
FROM      mv_base_a;

-- Refresh the MATERIALIZED VIEW
REFRESH   MATERIALIZED VIEW mv_table;

-- Query data
SELECT * FROM mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
-- Add a column "col"
CREATE OR REPLACE MATERIALIZED VIEW mv_table 
(i, j, col) 
BUILD DEFERRED DISABLE QUERY REWRITE AS
SELECT    i,
          j,
          j * 1
FROM      mv_base_a;

-- The next refresh will be a full refresh because new processing logic was added
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
+---+----+-----+

-- Drop a column
DROP      TABLE IF EXISTS mv_base_a;

CREATE    TABLE mv_base_a (i int, j int);

INSERT    INTO mv_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

-- Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;

CREATE MATERIALIZED VIEW mv_table (i, j) AS
SELECT    *
FROM      mv_base_a;

-- Refresh the MATERIALIZED VIEW
REFRESH   MATERIALIZED VIEW mv_table;

-- Query data
SELECT    *  FROM      mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+

-- Materialized view modification: drop a column
CREATE OR REPLACE MATERIALIZED VIEW mv_table 
(i, j) 
BUILD DEFERRED DISABLE QUERY REWRITE AS
SELECT    i,
          j
FROM      mv_base_a;

-- The table query will have one fewer column; the refresh will be incremental.
SELECT    *
FROM      mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+

-- Modify SQL syntax definition
-- Create a base table
DROP TABLE  IF EXISTS mv_base_a;
CREATE TABLE mv_base_a (i int, j int);
INSERT INTO mv_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
-- Process using MATERIALIZED VIEW
DROP MATERIALIZED VIEW IF EXISTS mv_table;
CREATE MATERIALIZED VIEW mv_table (i, j) AS
SELECT    *
FROM      mv_base_a;
-- Refresh the MATERIALIZED VIEW
REFRESH   MATERIALIZED VIEW mv_table;
-- Query data
SELECT    *    FROM      mv_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
-- Modify WHERE filter condition
CREATE OR REPLACE MATERIALIZED VIEW mv_table
(i,j)
BUILD DEFERRED DISABLE QUERY REWRITE
AS select * from mv_base_a where i>3;
-- This refresh will perform a full refresh
refresh MATERIALIZED VIEW mv_table;
select * from mv_table;
+---+----+
| i | j  |
+---+----+
| 4 | 40 |
+---+----+
```

3. <column_list>:
   * You can specify column names or add comment information to the materialized view's columns. You can specify column names but not column types; types are inferred from the SELECT results in `AS <query>`. If you want to specify a type, you can explicitly CAST in the SELECT results.
   * If any column in the table is based on an expression, it is recommended to provide a name for each column, or use aliases in `AS <query>`.
   ```SQL
     -- Specify column comments; when there are expressions, specifying column names is recommended
     CREATE MATERIALIZED VIEW mv
     (i,j_dd comment 'test')
     AS select i,j+1 from mv_base_a;
     +-------------+-----------+---------+
     | column_name | data_type | comment |
     +-------------+-----------+---------+
     | i           | int       |         |
     | j_dd        | int       | test    |
     +-------------+-----------+---------+
     -- Use alias approach when there are column computation expressions
     CREATE  MATERIALIZED VIEW mv
     AS select i,j+1 as j_add from mv_base_a;
     +-------------+-----------+---------+
     | column_name | data_type | comment |
     +-------------+-----------+---------+
     | i           | int       |         |
     | j_add       | int       |         |
     +-------------+-----------+---------+
   ```

4. PARTITIONED BY (<col>): Specifies a partition, using a column from <column_list> as the partition. Partitioning is a method of speeding up queries by grouping similar rows together at write time. It enables data pruning and query optimization.

   ```SQL
      CREATE MATERIALIZED VIEW mv
      (i,j_dd comment 'test')
      partitioned by(j_dd)
      AS select i,j+1 from mv_base_a;
   ```

5. CLUSTERED BY: Optional. Specifies a Hash Key. The Lakehouse will hash the specified column and distribute data across data buckets based on the hash value. To avoid data skew and hot spots and improve parallel execution, it is recommended to choose columns with a wide range of values and few duplicate keys as the Hash Key. This is typically effective during JOIN operations. It is recommended to use CLUSTERED BY in scenarios with large data volumes, generally with a bucket size between 128MB and 1GB. If no bucketing is specified, the default is 256 buckets.

* SORTED BY: Optional. Specifies the sort order of fields within a bucket. It is recommended to keep SORTED BY and CLUSTERED BY consistent for better performance. When the SORTED BY clause is specified, row data will be sorted according to the specified columns.
  ```SQL
  -- Create a bucketed table
  CREATE MATERIALIZED VIEW mv (i, j_dd COMMENT 'test') 
  CLUSTERED BY (j_dd) INTO 16 BUCKETS AS
  SELECT    i,
            j + 1
  FROM      mv_base_a;
  -- Create a bucketed table with sorting
  CREATE MATERIALIZED VIEW mv
  (i, j_dd COMMENT 'test')
  CLUSTERED BY (j_dd) SORTED BY (j_dd)  INTO 16 BUCKETS  
  AS
  SELECT    i,
            j + 1
  FROM      mv_base_a;
  ```

6. COMMENT: Specifies the comment information for the materialized view.

7. BUILD DEFERRED: This is a creation mode for materialized views. Unlike `BUILD IMMEDIATE`, which generates data immediately, `BUILD DEFERRED` allows the materialized view to be created without immediately generating data. The default value is BUILD IMMEDIATE. When using the CREATE OR REPLACE syntax, BUILD DEFERRED is required.

8. refreshOption: Optional. Refresh options.
   * START WITH timestamp_expr: Specifies the start time, supporting a timestamp expression. If START WITH is not written, the refresh starts from the current time.
     * `timestamp_expression` returns a result that is a standard timestamp type expression. The earliest timestamp specified by TIMESTAMP AS OF depends on the [TIME TRAVEL](TIMETRAVEL.md)(data_retention_days) parameter. If the specified version does not exist, an error is returned. If not specified, the current timestamp version data is used. For example:
       * `'2023-11-07 14:49:18'`, i.e., a string coercible to timestamp.
       * `cast('2023-11-07 14:49:18 Asia/Shanghai' as timestamp)`.
       * `current_timestamp() - interval '12' hours`.
       * Any other expression that is itself a timestamp or coercible to timestamp.
     ```
     -- Start refreshing from the next day, with a refresh interval of 20 hours
     CREATE MATERIALIZED VIEW mydt
          (i,j)
          REFRESH
          START WITH current_timestamp() +INTERVAL '1' DAY
          INTERVAL '20' HOUR
         vcluster test_alter AS
         SELECT    *
         FROM      mv_base_a;
     ```
   * interval_time: Specifies the time interval. Supports [interval time types](INTERVAL.md). If interval_time is not written but START WITH is, it will only refresh once at the time specified by START WITH. The interval_time intervals are as follows:

| Syntax                                  | Description                           | Example                                                        |
| ----------------------------------- | ---------------------------- | --------------------------------------------------------- |
| INTERVAL '[+ | -]' DAY            | Specify DAY interval only                     | INTERVAL '1' DAY means 1 day                                      |
| INTERVAL '[+ | -]' HOUR           | Specify HOUR interval only                    | INTERVAL '23' HOUR means 23 hours                                  |
| INTERVAL '[+ | -]' MINUTE         | Specify MINUTE interval only                  | INTERVAL '59' MINUTE means 59 minutes                                |
| INTERVAL '[+ | -]' SECOND         | Specify SECOND interval only                  | INTERVAL '59.999' SECOND means 59.999 seconds                         |
| INTERVAL '[+ | -] ' DAY TO HOUR   | Specify both DAY and HOUR intervals               | INTERVAL '1 23' DAY TO HOUR means 1 day 23 hours                       |
| INTERVAL '[+ | -] ' DAY TO MINUTE | Specify DAY, HOUR, and MINUTE intervals        | INTERVAL '1 23:59' DAY TO MINUTE means 1 day 23 hours 59 minutes              |
| INTERVAL '[+ | -] ' DAY TO SECOND | Specify DAY, HOUR, MINUTE, and SECOND intervals | INTERVAL '1 23:59:59.999' DAY TO SECOND means 1 day 23 hours 59 minutes 59.999 seconds |

day: Value range [0, 2147483647]. hour: Value range [0, 23]. minute: Value range [0, 59]. second: Value range [0, 59.999999999].

* The minimum INTERVAL value is 1 minute, which can be expressed as 60 SECOND or 1 MINUTE.
  * INTERVAL supports quoted or unquoted forms; the following are equivalent:
    * INTERVAL "60 SECOND"
    * INTERVAL '60 SECOND'
    * INTERVAL 60 SECOND
  * INTERVAL supported units: SECOND, MINUTE, HOUR, DAY
  * INTERVAL units are case-insensitive; HOUR and hour are equivalent.

* Specify the compute cluster in `refreshOption`. Automatic refresh consumes resources, so the compute cluster must be explicitly specified. If not specified, the current session's compute cluster is used by default. You can check the current session's compute cluster using `SELECT current_vcluster()`.

  ```SQL
  CREATE MATERIALIZED VIEW my_mv (i, j)
  REFRESH   interval '1' MINUTE vcluster test AS
  SELECT    *
  FROM      mv_base_a;
  ```

9. DISABLE QUERY REWRITE: This means the materialized view does not support the query rewrite feature. Query rewrite is when the database optimizer automatically determines whether a query against the base table of a materialized view can be satisfied by querying the materialized view instead, thereby avoiding aggregation or join operations and reading directly from the pre-computed materialized view.

## Notes

* Incremental refresh of materialized views is based on historical versions of the base table. Historical versions depend on the [TIME TRAVEL](TIMETRAVEL.md)(data_retention_days) parameter; if the specified version does not exist, an error is returned. This parameter defines how long deleted data is retained. The Lakehouse retains data for one day by default. Based on your business requirements, you can adjust the `data_retention_days` parameter to extend or shorten the data retention period. Note that adjusting the data retention period may affect storage costs. Extending the retention period increases storage requirements and may increase associated costs.

## Examples

### Example 1: Simple Materialized View

This example demonstrates how to create a table (`inventory`) and a materialized view (`mv_inventory_basic`) based on that table. Then, a row of data is inserted, followed by selecting data from the materialized view, refreshing it, and selecting again to observe the effect of manual refresh.

```SQL
-- Create a table named inventory with product_ID, wholesale_price, and description fields
CREATE TABLE inventory (product_ID INTEGER, wholesale_price FLOAT, description VARCHAR);

-- Create materialized view mv_inventory_basic if it does not exist, selecting product_ID, wholesale_price, and description from inventory
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_inventory_basic AS
SELECT product_ID, wholesale_price, description
FROM inventory;

-- Insert a row of data into the inventory table:
INSERT INTO inventory (product_ID, wholesale_price, description) VALUES 
    (1, 1.00, 'cog');

-- Select product_ID and wholesale_price from the materialized view mv_inventory_basic to see its content after the insert
SELECT product_ID, wholesale_price FROM mv_inventory_basic;

-- Refresh the materialized view mv_inventory_basic to keep its content consistent with the base table
REFRESH MATERIALIZED VIEW mv_inventory_basic;

-- Select product_ID and wholesale_price from mv_inventory_basic again to see the refreshed content
SELECT product_ID, wholesale_price FROM mv_inventory_basic;
```

The above SQL statements demonstrate how to create and use a materialized view. In practice, materialized views can significantly improve query performance, especially for complex computations or large data volumes. Refreshing the materialized view ensures its data stays consistent with the source table, providing the latest query results. **Note: Since no scheduling parameters were used when creating the materialized view, a manual refresh is performed here.**

### Example 2: Materialized View with Column List and Comment

```SQL
CREATE MATERIALIZED VIEW mv_inventory_with_comment
(product_ID, wholesale_price, description)
COMMENT 'This is a materialized view for inventory'
AS
SELECT product_ID, wholesale_price, description
FROM inventory;
```

### Example 3: Materialized View with Partitioning and Clustering

```SQL
CREATE MATERIALIZED VIEW mv_inventory_partitioned_clustered

(product_ID, wholesale_price, description)

PARTITIONED BY (product_ID)

CLUSTERED BY (product_ID)

AS

SELECT product_ID, wholesale_price, description

FROM inventory;
```

### Example 4: Materialized View with Refresh Options and Virtual Compute Cluster

```SQL
CREATE MATERIALIZED VIEW mv_inventory_refresh

REFRESH START WITH current_timestamp INTERVAL '1 HOUR' VCLUSTER default

AS

SELECT product_ID, wholesale_price, description

FROM inventory;
```

Modify the refresh interval of a materialized view with refresh options:

```SQL
CREATE OR REPLACE MATERIALIZED VIEW mv_inventory_refresh

BUILD DEFERRED

REFRESH START WITH current_timestamp INTERVAL '1 MINUTE' VCLUSTER default

DISABLE QUERY REWRITE

AS

SELECT product_ID, wholesale_price, description

FROM inventory;
```

View the modification result:

```SQL
DESC EXTENDED mv_inventory_refresh;
```

You can see that the value of refresh_interval_second is now 60, indicating that the refresh interval was successfully modified.
For materialized views that auto-refresh on a schedule, to pause or resume automatic refresh, please refer to:
[Alter Materialized View](alter-materialized-view.md)

### Example 5: Comprehensive Example

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

### Example 6: Create Materialized View and Add Comment

Re-creating a MATERIALIZED VIEW can reuse the previous result. The scenario includes adding a column, where the previous MV can be reused and the newly added column shows null for old data.

**Example**

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

-- Create a materialized view storing employee count and average salary per department
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

-- Add a column to departments
ALTER     TABLE departments ADD COLUMN col1 string;

INSERT    INTO employees
VALUES    (1001, 'aa', 10, 5000);

-- Use create or replace syntax to add a column. To avoid re-computation, the previous result is reused. You can see the previous MV table used directly in the job profile.
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

-- The query result contains the previous results
SELECT    *
FROM      dept_emp_stats;
```

## Related Guides

- [Views and Materialized Views](SQL_View_Guide.md): Comparison of view and materialized view usage scenarios, refresh strategies, and typical query acceleration patterns
