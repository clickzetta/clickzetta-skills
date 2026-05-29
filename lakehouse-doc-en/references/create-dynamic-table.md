# Create Dynamic Table

## Description

A Dynamic Table is a special type of table that can update data in real-time based on query statements. Dynamic Tables allow you to handle data more flexibly and improve query efficiency. For more usage methods, refer to [Dynamic Table Introduction](dynamic-table-introduce.md) and [Incremental Calculation Section](dynamic-table.md)

## Syntax 
```SQL

CREATE [ OR REPLACE ｜IF NOT EXISTS ] DYNAMIC TABLE dtname
[ (column_list ) ]
[PARTITIONED BY (column_name) ]
[CLUSTERED BY (column_name)]
[COMMENT view_comment]
[refreshOption]
AS <query>;  

refreshOption ::=
    REFRESH 
    [START WITH timestamp_expr]  [interval_time] VCLUSTER vcname
```
**Required Parameters**

1. dtname: Specify the dynamic table name.
2. AS query: The query statement contained in the dynamic table.

**Optional Parameters**

1. IF NOT EXISTS: Optional. If the specified materialized view name exists, the system will not report an error, but the materialized view will not be created successfully. Cannot be used with OR REPLACE at the same time.

2. OR REPLACE: In traditional databases, this option is used to replace the old object with a new one within the same transaction and delete the old object's data. However, in Lakehouse, to support the addition, deletion, and modification operations of Dynamic Tables, we retain data and metadata permission information. This means that even when modifying table structures or SQL logic, the original data will not be lost. This feature is particularly suitable for adding or deleting columns, adjusting SQL processing logic, and changing data types. It should be noted that if the user is not simply deleting columns / adding columns
Adding column definitions: It can only be passed through the table via SELECT and cannot participate in any calculations that affect other columns, such as join key, group key, etc. After Create Or Replace occurs, the REFRESH task will degrade to a full refresh.
```
--Modify the scheduling cycle
--Original table
CREATE DYNAMIC TABLE dt_name
REFRESH   interval 10 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;

--After modification
CREATE OR  REPLACE DYNAMIC TABLE dt_name
REFRESH   interval 20 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;

--Modify the computing cluster
--Original table
CREATE DYNAMIC TABLE dt_name
REFRESH   interval 10 MINUTE vcluster DEFAULT AS
SELECT    *
FROM      student02;

--After modification
CREATE OR  REPLACE DYNAMIC TABLE dt_name
REFRESH   interval 10 MINUTE vcluster alter_vc AS
SELECT    *
FROM      student02;

--Add column
--Create a base table
DROP      TABLE IF EXISTS dy_base_a;

CREATE    TABLE dy_base_a (i int, j int);

INSERT    INTO dy_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

--Process using dynamic table
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

--Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;

--Query data
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
--Add a column col
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j, col) AS
SELECT    i,
          j,
          j * 1
FROM      dy_base_a;

--The next refresh will be a full refresh because new processing logic has been added
REFRESH   DYNAMIC TABLE change_table;
   +---+----+-----+
   | i | j  | col |
   +---+----+-----+
   | 1 | 10 | 10  |
   | 2 | 20 | 20  |
   | 3 | 30 | 30  |
   | 4 | 40 | 40  |
   +---+----+-----+

--Remove column
DROP      TABLE IF EXISTS dy_base_a;
CREATE    TABLE dy_base_a (i int, j int);
INSERT    INTO dy_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);
--Process using dynamic table
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

--Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;

--Query data
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
--Remove column
CREATE OR  REPLACE DYNAMIC TABLE change_table (i, j) AS
SELECT    i,
          j
FROM      dy_base_a;
--At this time, the query in the table will have one less column, and the refresh will be incremental.
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

--Modify SQL syntax definition
--Create a base table
DROP      TABLE IF EXISTS dy_base_a;

CREATE    TABLE dy_base_a (i int, j int);

INSERT    INTO dy_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

--Process using dynamic table
DROP DYNAMIC TABLE IF EXISTS change_table;

CREATE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a;

--Refresh dynamic table
REFRESH   DYNAMIC TABLE change_table;
--Query data
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
--Modify where filter condition
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j) AS
SELECT    *
FROM      dy_base_a
WHERE     i > 3;

--At this time, the refresh will be a full refresh once
REFRESH   DYNAMIC TABLE change_table;
SELECT    *
FROM      change_table;
   +---+----+
   | i | j  |
   +---+----+
   | 4 | 40 |
   +---+----+
```
3. <column\_list>：
   * You can specify the column names or add comment information to the columns of the dynamic table. You can specify the column names but cannot specify the column types. The types are inferred from the SELECT results in `AS <query>`. If you want to specify the types, you can explicitly use CAST conversion in the SELECT results.
   * If any column in the table is based on an expression, it is recommended to provide a name for each column. Alternatively, use aliases in the \<query>.
```SQL
  --Specify column comment, it is recommended to specify column name when there is an expression
CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test') AS
SELECT    i,
          j + 1
FROM      dy_base_a;
  +-------------+-----------+---------+
  | column_name | data_type | comment |
  +-------------+-----------+---------+
  | i           | int       |         |
  | j_dd        | int       | test    |
  +-------------+-----------+---------+
  --Use alias method when there is a column operation expression
CREATE DYNAMIC TABLE change_table_dy AS
SELECT    i,
          j + 1 AS j_add
FROM      dy_base_a;
  +-------------+-----------+---------+
  | column_name | data_type | comment |
  +-------------+-----------+---------+
  | i           | int       |         |
  | j_add       | int       |         |
  +-------------+-----------+---------+
```
4. partitioned by (\<col> ): Specify partitions, using the columns in \<column\_list> as partitions. Partitioning is a method to speed up queries by grouping similar rows together during writing. Using partitions can achieve data pruning and optimize queries.
   ```SQL
   CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test') PARTITIONED BY (j_dd) AS
   SELECT    i,
             j + 1
   FROM      dy_base_a;
   ```
4. CLUSTERED BY: Optional, specifies the Hash Key. Lakehouse will perform a hash operation on the specified column and distribute the data into various data buckets based on the hash value. To avoid data skew and hotspots, and to improve parallel execution efficiency, it is recommended to choose columns with a large range of values and few duplicate key values as the Hash Key. This usually has a noticeable effect when performing join operations. It is recommended to use CLUSTERED BY in scenarios with large amounts of data, generally with a bucket size between 128MB and 1GB. If no buckets are specified, the default is 256 buckets.

* SORTED BY: Optional, specifies the sorting method for fields within the Bucket. It is recommended to keep SORTED BY consistent with CLUSTERED BY for better performance. When the SORTED BY clause is specified, row data will be sorted according to the specified columns.
```SQL

CREATE DYNAMIC TABLE change_table_dy (i, j_dd COMMENT 'test') 
CLUSTERED BY (j_dd) INTO 16 BUCKETS AS
SELECT    i,
          j + 1
FROM      dy_base_a;

CREATE DYNAMIC TABLE change_table_dy 
(i, j_dd COMMENT 'test') 
CLUSTERED BY (j_dd) SORDERD BY (j_dd)  INTO 16 BUCKETS  
AS
SELECT    i,
          j + 1
FROM      dy_base_a;
```
5. comment: Specify dynamic comment information

6. refreshOption (optional), refresh options
   * START WITH timestamp\_exp Specify the start time, supporting a timestamp expression. If START WITH is not written, the refresh starts from the current time.
     * The `timestamp_expression` returns a standard timestamp type expression. The earliest timestamp specified by TIMESTAMP AS OF depends on the [TIME TRAVEL](TIMETRAVEL.md) (data\_retention\_days) parameter. If the specified version does not exist, an error will be reported. If not specified, the version data of the current timestamp will be used, for example:
       \* `'2023-11-07 14:49:18'`, which can be forcibly converted to a timestamp string.
       \* `cast('2023-11-07 14:49:18 Asia/Shanghai' as timestamp)`.
       \* `current_timestamp() - interval '12' hours`.
       \* Any other expression that is itself a timestamp or can be forcibly converted to a timestamp.
```
-- Specify to start refreshing the next day, with a refresh interval of 20 hours
CREATE DYNAMIC TABLE mydt (i, j)
REFRESH   START
WITH      current_timestamp() + INTERVAL '1' DAY INTERVAL '20' HOUR vcluster test_alter AS
SELECT    *
FROM      dy_base_a;
```
* `interval_time` specifies the time interval and supports [interval types](INTERVAL.md). If `interval_time` is not specified but `START WITH` is, it will only refresh once at the time specified by `START WITH`. The `interval_time` intervals are as follows:

| Syntax                                | Description                    | Example                                                      |
| ------------------------------------- | ------------------------------ | ------------------------------------------------------------ |
| INTERVAL '\[+ \| -]' DAY              | Specifies only DAY interval    | INTERVAL '1' DAY means 1 day                                  |
| INTERVAL '\[+ \| -]' HOUR             | Specifies only HOUR interval   | INTERVAL '23' HOUR means 23 hours                             |
| INTERVAL '\[+ \| -]' MINUTE           | Specifies only MINUTE interval | INTERVAL '59' MINUTE means 59 minutes                         |
| INTERVAL '\[+ \| -]' SECOND           | Specifies only SECOND interval | INTERVAL '59.999' SECOND means 59.999 seconds                 |
| INTERVAL '\[+ \| -] ' DAY TO HOUR     | Specifies both DAY and HOUR intervals | INTERVAL '1 23' DAY TO HOUR means 1 day and 23 hours          |
| INTERVAL '\[+ \| -] ' DAY TO MINUTE   | Specifies DAY, HOUR, and MINUTE intervals | INTERVAL '1 23:59' DAY TO MINUTE means 1 day, 23 hours, and 59 minutes |
| INTERVAL '\[+ \| -] ' DAY TO SECOND   | Specifies DAY, HOUR, MINUTE, and SECOND intervals | INTERVAL '1 23:59:59.999' DAY TO SECOND means 1 day, 23 hours, 59 minutes, and 59.999 seconds |

day: The range is \[0, 2147483647]. hour: The range is \[0, 23]. minute: The range is \[0, 59]. second: The range is \[0, 59.999999999].

* The minimum value for INTERVAL is 1 minute, which can be represented as 60 SECOND or 1 MINUTE.
  * INTERVAL can be specified with or without quotes, and the following are equivalent:
    * INTERVAL "60 SECOND"
    * INTERVAL '60 SECOND'
    * INTERVAL 60 SECOND
  * Supported units for INTERVAL: SECOND, MINUTE, HOUR, DAY
  * INTERVAL units are case-insensitive, so HOUR and hour are equivalent.

* Specify the compute cluster in `refreshOption`. Automatic refresh consumes resources, so you need to explicitly specify the compute cluster. If not specified, the current session's compute cluster will be used by default. You can check the current session's compute cluster with `SELECT current_vcluster()`.
  ```SQL
  CREATE DYNAMIC TABLE mydt (i, j)
  REFRESH   interval '1' MINUTE vcluster test AS
  SELECT    *
  FROM      dy_base_a;
  ```
### Notes

* The incremental refresh of dynamic tables is based on the historical versions of the base table. Historical versions depend on the [TIME TRAVEL](TIMETRAVEL.md)(data\_retention\_days) parameter, and an error will occur if the specified version does not exist. This parameter defines the length of time that deleted data is retained, with the Lakehouse defaulting to retaining data for one day. Depending on your business needs, you can adjust the `data_retention_days` parameter to extend or shorten the data retention period. Please note that adjusting the data retention period may affect storage costs. Extending the retention period will increase storage requirements, which may increase associated costs.

## Parameterized Definition Dynamic Table Creation Syntax

When the dynamic table is a partitioned table, parameters can be passed in. Parameters are defined through SESSION\_CONFIGS()\['dt.arg.xx']. SESSION\_CONFIGS() is a built-in system function. For non-partitioned tables, if parameterized definitions are used and the passed parameter values remain unchanged, the system will perform an incremental refresh. However, once the parameter values change, the system will perform a full refresh, as this is equivalent to changing the table definition. For partitioned tables, the partition key must be a parameter field, but these parameter fields are not required to be partition columns of the table.

### Creation Statement

The parameterized definition of Dynamic Table allows users to define parameters through `SESSION_CONFIGS()['dt.arg.xx']`. These parameters are referenced when creating the table, thereby dynamically affecting the content of the table.

* `SESSION_CONFIGS()`: A built-in system function used to read parameters from the configuration.
* `'dt.arg.xx'`: The name of the DT parameter, which must start with `dt.arg.` to avoid conflicts with internal system fields.

#### Example Code
```sql
CREATE DYNAMIC TABLE event_gettime_pt PARTITIONED BY (event_day) AS
SELECT    event,
          process,
          YEAR(event_time) event_year,
          MONTH(event_time) event_month,
          DAY(event_time) event_day
FROM      event_tb_pt
WHERE     day(event_time) = SESSION_CONFIGS () ['dt.args.event_day'];

set dt.args.event_day = 19;

REFRESH   DYNAMIC TABLE event_gettime_pt PARTITION (event_day = 19);
```
In this example, `dt.args.event_day` is a DT parameter, which is read from the configuration using the `SESSION_CONFIGS()` function. If non-string type parameters are needed, the `CAST` function can be used for type conversion.

### Refresh Statement

The refresh behavior of a parameterized Dynamic Table depends on whether the table is partitioned.

#### Non-Partitioned Table Refresh Syntax
```sql
REFRESH DYNAMIC TABLE dt;
```
* The parameter values of non-partitioned tables remain unchanged and will be incrementally refreshed.
* The parameter values of non-partitioned tables change and will be fully refreshed.

#### Partitioned Table Refresh Syntax
```sql
REFRESH DYNAMIC TABLE dt PARTITION partition_spec;
```
When refreshing a partitioned table, the `partition_spec` must be specified in the order of the table's partition hierarchy. This means that if the table is partitioned by multiple fields, these fields need to be specified from the highest level to the lowest level.

#### Example Description

Assuming a table is partitioned by `day`, `hour`, and `min` in three levels, the correct way to specify the `partition_spec` is as follows:

**Valid Specification**: You can specify higher-level and some lower-level partitions, but you cannot skip any intermediate level partitions.
```sql
set dt.args.day=2024-11-13;
set dt.args.hour=23;
REFRESH DYNAMIC TABLE dt PARTITION (day='2024-11-13', hour=23); 
```
In this example, `day` and `hour` are specified, while the `min` partition can be ignored.

**Invalid Specification**: Skipping the specification of any intermediate level partitions is not allowed.
```sql
set dt.args.day=2024-11-13;
set dt.args.hour=30;
REFRESH DYNAMIC TABLE dt PARTITION (day='2024-11-13', min=30); 
```
### Precautions

* Parameter and Partition Consistency
  When performing a refresh operation on a Dynamic Table, you must ensure that the parameter values passed in are consistent with the specified partition values to be refreshed. If there is any inconsistency, the system will report an error during execution.

  * **Error Example**:
    ```SQL
    set dt.args.event_day=11; 
    refresh dynamic table event_gettime_pt partition(event_day=19);
    ```
    
    In the above situation, although the parameter event_day is set to 11, the refresh command attempts to write to partition event_day=19. This will cause the actual calculated partition result to be inconsistent with the specified partition, resulting in errors.

* **Correct Example**:
  ```sql
  set dt.args.event_day=19;
  REFRESH   DYNAMIC TABLE event_gettime_pt PARTITION (event_day = 19);
  ```
* Concurrent Refresh Tasks
  In these commands, the parameter values match the partition values, so they can be executed concurrently without conflicts. As long as there are no conflicts between partitions, the system allows multiple partition refresh tasks to be executed simultaneously.
```sql
-- Set parameters for partition event_day=19 and refresh
set dt.args.event_day=19;
REFRESH   DYNAMIC TABLE event_gettime_pt PARTITION (event_day = 19);

-- Set parameters for partition event_day=20 and refresh
set dt.args.event_day=20;
REFRESH   DYNAMIC TABLE event_gettime_pt PARTITION (event_day = 20);
```
### Full Refresh and Incremental Refresh

* Full Refresh
  Full refresh occurs in the following situations:
  * The parameter values of a non-partitioned table change.
  * The parameter values of a partitioned table change, causing the partition conditions to change.
    Example code
```sql
-- Non-partitioned table
SET dt.args.x=1;
REFRESH DYNAMIC TABLE T; -- First time creating DT, parameter x=1, full refresh
SET dt.args.x=2;
REFRESH DYNAMIC TABLE T; -- Parameter value changes, full refresh
-- Partitioned table
SET dt.args.pt=1;
SET dt.args.x=1;
REFRESH DYNAMIC TABLE T PARTITION (pt = 1); -- First time creating DT pt=1, parameter x=1, full refresh
SET dt.args.x=3;
REFRESH DYNAMIC TABLE T PARTITION (pt = 1); -- Parameter value changes, full refresh partition pt = 1
```
* Incremental Refresh
  Incremental refresh occurs in the following situations:
  * The parameter values of the non-partitioned table remain unchanged.
  * The parameter values of the partitioned table remain unchanged, and the partition conditions have not changed.
    Example code
```sql
-- Non-partitioned table
SET dt.args.x=1;
REFRESH DYNAMIC TABLE T; -- Parameter x=1 unchanged, incremental refresh

-- Partitioned table
SET dt.args.pt=1;
SET dt.args.x=1;
REFRESH DYNAMIC TABLE T PARTITION (pt = 1); -- Parameter x=1 unchanged, incremental refresh partition pt = 1
```
### Scenario Case

**Case 1: Converting Offline Tasks to Incremental Tasks**
This section will guide users on how to convert existing offline tasks into incremental tasks to achieve more efficient data processing. Below are specific operational steps based on a "traditional database," suitable for scenarios where business logic is aligned and refreshed daily.

* Step 1: Parameterize the original SQL. The original SQL is as follows
  ```sql
  WITH      tmp_channel AS (
            SELECT    channel_code,
                      channel_name,
                      channel_type,
                      channel_uid
            FROM      dim.dim_shop_sales_channel_main
            WHERE     pt = '${bizdate}'
            ),
            tmp_bac_misc AS (
            SELECT    mini_number,
                      bac_no
            FROM      dim.dim_customer_bac_misc_df
            WHERE     pt = '${bizdate}'
            ),
            tmp_fxiaoke AS (
            SELECT    CASE
                                WHEN record_type IN ('dealer__c') THEN nvl(bac_no, account_no)
                                ELSE account_no
                      END AS channel_code,
                      id,
                      account_no
            FROM      ods.ods_account_obj AS a
            LEFT JOIN tmp_bac_misc ON a.account_no = tmp_bac_misc.mini_number
            WHERE     pt = '${bizdate}' AND      
                      account_no IS NOT NULL
                      --  and is_deleted = 0
                      --  and life_status not in ('invalid', 'ineffective')
            )
  INSERT    OVERWRITE TABLE dim.dim_shop_sales_channel_misc PARTITION (pt = '${bizdate}')
  SELECT    tmp_channel.channel_code,
            channel_name,
            channel_type,
            channel_uid,
            id AS fxiaoke_id,
            account_no AS fxiaoke_account_no
  FROM      tmp_channel
  LEFT JOIN tmp_fxiaoke ON tmp_channel.channel_code = tmp_fxiaoke.channel_code;
  ```
First, all parameters `${bizdate}` passed in by the scheduling engine in the original SQL need to be replaced with `SESSION_CONFIGS()['dt.args.bizdate']`. This step will allow the parameter values to be dynamically passed through configuration, rather than hard-coded in the SQL.

  **Original SQL Parameter Replacement**:
  Replace all `${bizdate}` with `SESSION_CONFIGS()['dt.args.bizdate']`:
  ```sql
  CREATE dynamic TABLE im.dim_shop_sales_channel_misc
  PARTITIONED BY (pt)
  WITH      tmp_channel AS (
            SELECT    channel_code,
                      channel_name,
                      channel_type,
                      channel_uidfrom dim.dim_shop_sales_channel_main
            WHERE     pt = SESSION_CONFIGS () ['dt.args.bizdate']
            ),
            tmp_bac_misc AS (
            SELECT    mini_number,
                      bac_nofrom dim.dim_customer_bac_misc_df
            WHERE     pt = SESSION_CONFIGS () ['dt.args.bizdate']
            ), 
           tmp_fxiaoke AS (    
            SELECT    CASE
                                WHEN record_type IN ('dealer__c') THEN nvl(bac_no, account_no)
                                ELSE account_no
                      END AS channel_code,
                      id,
                      account_no
            FROM      ods.ods_account_obj AS a
            LEFT JOIN tmp_bac_misc ON a.account_no = tmp_bac_misc.mini_number
      WHERE pt = SESSION_CONFIGS()['dt.args.bizdate'] and account_no is not null
  )
  SELECT    tmp_channel.channel_code,
            channel_name,
            channel_type,
            channel_uid,
            id AS fxiaoke_id,
            account_no AS fxiaoke_account_no,
            pt
  FROM      tmp_channel
  LEFT JOIN tmp_fxiaoke ON tmp_channel.channel_code = tmp_fxiaoke.channel_code
  ;
  ```
* Step 2: Schedule Refresh Command
  During each scheduling, the parameter `dt.args.bizdate` needs to be set to a specific date value, and the refresh command should be executed.

  Example of scheduling refresh command
Sure, here is the translated content:

```sql
SET dt.args.bizdate=20241130; -- ${bizdate} is replaced by Studio with a specific value each time
REFRESH DYNAMIC TABLE DT PARTITION (pt ='20241130');
```
**Case 2: Incremental Task Data Supplement, in some cases, users may need to supplement data to existing partitions**.

* Method 1: Supplement data to the source table, users can directly supplement data to the source table. These supplemented data will be automatically reflected in the Dynamic Table (DT) through the corresponding REFRESH task.

  Operation Steps

  1. Directly insert or update data in the source table.
  2. Execute the REFRESH task to synchronize the changes to the DT.
* Method 2: Use DML statements to directly supplement data to the DT, users can also use DML statements to insert data into specific partitions of the DT.
  Operation Steps
  1. Use DML statements to insert data into specific partitions of the DT.
  2. Note that directly modifying the DT will result in a full refresh of that partition the next time. If users do not want a full refresh result, they should avoid scheduling the REFRESH task for that partition.
     Example Code
  ```sql
  INSERT INTO DYNAMIC TABLE incremental_dt VALUES (...);
  ```
**Notes**

* Data directly inserted into DT will participate in downstream calculations of DT. If the downstream old partitions do not need this data, please do not schedule REFRESH tasks for partitions involving this data.
* Other unaffected partitions can still be incrementally refreshed.

**Case 3: Executing Incremental Tasks in Different VCs. For parameterized partitioned DT, refresh tasks for different partitions can be executed simultaneously. Users can allocate different REFRESH tasks to different Virtual Clusters (VC) as needed**.
Operation Steps

1. Allocate different REFRESH tasks to different VCs based on timeliness requirements and resource needs.
2. For example, for new partitions with high timeliness requirements, their REFRESH tasks can be executed in large VCs with more resources.
3. For supplementary tasks of other old partitions, their REFRESH tasks can be executed in smaller VCs with fewer resources.

## Reference Documents

* [Dynamic Table Visualization Interface Development](dynamic_table_task.md)
* [View Dynamic Table Details](desc-dynamic-table.md)
* [View All Dynamic Tables Under Schema](show-dynamic-table.md)
* [Modify Dynamic Table](alter-dynamic-table.md)
* [Delete Dynamic Table](drop-dynamic-table.md)
* [View Dynamic Table Refresh History](refresh-history.md)
* [View Dynamic Table Creation Statement](show-create-table.md)
* [Restore Deleted Dynamic Table](UNDROP-TABLE.md)
* [Restore Dynamic Table to Specified Version](restore.md)
* [View Dynamic Table Version History](desc-history.md)
* [View Data of Specified Version of Dynamic Table](TIMETRAVEL.md)
* [Introduction to Dynamic Table](dynamic-table-introduce.md)