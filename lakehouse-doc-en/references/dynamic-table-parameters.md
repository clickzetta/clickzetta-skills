# Dynamic Table Supports Parameterized Definitions

The parameterized definition of a Dynamic Table consists of two parts.

* When creating a partitioned dynamic table, parameters are defined through SESSION_CONFIGS()['dt.args.xx'] and written into the SQL processing logic to represent the query source table. SESSION_CONFIGS() is a built-in system function. 'dt.args.xx': The name of the DT parameter must start with `dt.arg.` to avoid conflicts with internal system fields. The meaning expressed is equivalent to `select * from source_table where pt=${bizdate}` in traditional scheduling; `SESSION_CONFIGS()['dt.args.pt']` is equivalent to `pt=${bizdate}`. The return type of SESSION_CONFIGS()['dt.args.xx'] is String. If parameters of other types are needed, use the CAST function for conversion, for example `cast(SESSION_CONFIGS()['dt.args.xx'] as int)`. Example:

```sql
-- Source table
CREATE    TABLE source_table (col1 string, col2 string, pt string) PARTITIONED BY (pt);

-- Define dynamic table
CREATE dynamic TABLE incremental_dt (col1, col2, pt) PARTITIONED BY (pt) AS
SELECT    col1,
          nvl(col2, col1),
          pt
FROM      source_table
WHERE     pt = SESSION_CONFIGS () ['dt.args.pt'];
```

* When refreshing, specify the partition value through `refresh dynamic table target_table partition(pt=${bizdate});`, where `pt=${bizdate}`. This corresponds to the traditional `insert overwrite target_table partition(pt=${bizdate})`.

```sql
-- The partition field of the dynamic table defined above is pt. Therefore, pass pt=${bizdate} when refreshing. Assume bizdate is 2024-11-13. Use the following syntax when refreshing
-- Pass 2024-11-13 into SESSION_CONFIGS()['dt.args.pt'] in the creation statement, replacing it with 2024-11-13 to filter data in source_table
SET dt.args.pt = 2024-11-13;
-- Specifying pt=2024-11-13 when refreshing means writing to the 2024-11-13 partition of the dynamic table
REFRESH   dynamic TABLE incremental_dt PARTITION (pt = '2024-11-13');
```



## Full Refresh and Incremental Refresh

### Full Refresh

Full refresh occurs in the following situations:

1. **Non-partitioned tables**:

   - If the parameter `SESSION_CONFIGS()['dt.args.event_day']` is used in a non-partitioned table, the system determines the refresh method based on whether the parameter value changes.
   - If the parameter value remains unchanged, the system will perform an **incremental refresh**.
   - If the parameter value changes, the system will perform a **full refresh**, because a change in the parameter value is equivalent to changing the table definition.

2. **Partitioned tables**:

   * If the partition already exists but the current refresh parameter is different from the previous refresh parameter, a full refresh is performed, because a change in the parameter value will cause a change in the SQL processing logic.
   * If the partition does not exist (i.e., the first refresh of a partition), a full refresh is performed.
    

```sql
-- Create source table
CREATE    TABLE source_table (col1 string, col2 string, pt string) PARTITIONED BY (pt);

-- Create dynamic table
CREATE dynamic TABLE incremental_dt (col1, col2, pt) PARTITIONED BY (pt) AS
SELECT    col1,
          nvl(col2, col1),
          pt
FROM      source_table
WHERE     pt = SESSION_CONFIGS () ['dt.args.pt'];

-- Example 1: First time setting parameter value to 2024-11-13
SET dt.args.xxx = 1;
SET dt.args.pt = 2024-11-13;
-- Refresh is a full refresh
REFRESH   dynamic TABLE incremental_dt PARTITION (pt = '2024-11-13');

-- Example 2: If the first refresh of a partition corresponds to one parameter value, and later the same partition's corresponding parameter changes, it is equivalent to the dt definition for this partition being modified, so it will be refreshed again, as shown below
SET dt.args.xxx = 2;
SET dt.args.pt = 2024-11-14;
-- Refresh dynamic table, specifying partition pt=2024-11-14
-- The system will perform a full refresh because the parameter value changed
REFRESH   dynamic TABLE incremental_dt PARTITION (pt = '2024-11-14');

```

### Incremental Refresh

Incremental refresh occurs in the following situations:

* The parameter value of a non-partitioned table remains unchanged.
* The parameter value of a partitioned table remains unchanged, and the partition condition has not changed.

**Example Code**:

```SQL

-- Create source table
CREATE    TABLE source_table (col1 string, col2 string, pt string) PARTITIONED BY (pt);

-- Define dynamic table
CREATE dynamic TABLE incremental_dt (col1, col2, pt) PARTITIONED BY (pt) AS
SELECT    col1,
          nvl(col2, col1),
          pt
FROM      source_table
WHERE     pt = SESSION_CONFIGS () ['dt.args.pt'];

-- Example 1: First time setting parameter value to 2024-11-13
SET dt.args.pt = 2024-11-13;

-- Refresh dynamic table, specifying partition pt=2024-11-13, full refresh
REFRESH   dynamic TABLE target_table PARTITION (pt = '2024-11-13');

-- Example 2: Parameter value and partition value unchanged, refresh again
SET dt.args.pt = 2024-11-13;

-- Refresh dynamic table, specifying partition pt=2024-11-13
-- The system will continue to perform incremental refresh
REFRESH   dynamic TABLE target_table PARTITION (pt = '2024-11-13');
```

## Refresh Statements

The refresh behavior of a parameterized Dynamic Table depends on whether the table is partitioned.

### **Non-Partitioned Table Refresh Syntax**:

```SQL
REFRESH DYNAMIC TABLE dt;。
```

* If the parameter value of a non-partitioned table remains unchanged, an incremental refresh is performed. If the parameter value of a non-partitioned table changes, a full refresh is performed.

### **Partitioned Table Refresh Syntax**:

```SQL
REFRESH DYNAMIC TABLE dt PARTITION partition_spec;
```

When refreshing a partitioned table, `partition_spec` must be specified according to the table's partition level order. This means that if the table is partitioned by multiple fields, these fields need to be specified in order from the highest level to the lowest level.
* For multi-level partitions, partition\_spec needs to be specified in order of partition levels. For example, if a table has three levels of partitions (day, hour, min), they must be specified from high to low in order; skipping a partition is not allowed. Specifying day and hour is valid; lower-level partitions can be omitted without declaring all. Specifying day and min is invalid because it skips hour.

  * ```SQL
    -- Invalid
    set dt.args.day = 1;
    set dt.args.min = 1;
    REFRESH   dynamic TABLE incremental_dt PARTITION (DAY = 1, MIN = 1);

    -- Valid
    set dt.args.day = 1;
     set dt.args.hour = 1;
    REFRESH   dynamic TABLE incremental_dt PARTITION (DAY = 1, HOUR = 1);
    ```
**Example**:

Assume a table is partitioned by `day`, `hour`, and `min` at three levels. The correct way to specify `partition_spec` is as follows:

* **Valid Specification**: Higher-level and some lower-level partitions can be specified, but no intermediate-level partitions can be skipped.

```SQL
set dt.args.day=2024-11-13;
set dt.args.hour=23;
REFRESH DYNAMIC TABLE dt PARTITION (day='2024-11-13', hour=23); 
```

In this example, `day` and `hour` are specified, while the `min` partition can be ignored.

* **Invalid Specification**: Skipping any intermediate-level partition is not allowed.

```SQL
set dt.args.day=2024-11-13
set dt.args.hour=30
REFRESH DYNAMIC TABLE dt PARTITION (day='2024-11-13', min=30); 
```

## **Notes**

* **Parameter and Partition Consistency**: When executing a Dynamic Table refresh operation, you must ensure that the partition parameter values used in the SQL computation logic are consistent with the partition values specified in the REFRESH statement. If there is inconsistency, the system will report an error during execution.

```SQL
CREATE dynamic TABLE incremental_dt (col1, col2, pt) PARTITIONED BY (pt) AS
SELECT    col1,
          nvl(col2, col1),
          pt
FROM      source_table
WHERE     pt = SESSION_CONFIGS () ['dt.args.pt'];

-- For example, select col1, nvl(col2, col1), pt from source_table where pt = SESSION_CONFIGS()['dt.args.pt']; filters out the corresponding partition field result as 9. The system will report an error during execution.
set dt.args.event_day = 9;

REFRESH   dynamic TABLE event_gettime_pt PARTITION (event_day = 19);

```

* **Concurrent Refresh Tasks**: In these commands, the parameter values match the partition values, so they can be executed concurrently without conflicts. As long as there are no conflicts between partitions, the system allows simultaneous execution of multiple partition refresh tasks.

```SQL
-- Set parameters and refresh for partition event_day=19
set dt.args.event_day = 19;

REFRESH   dynamic TABLE event_gettime_pt PARTITION (event_day = 19);

-- Set parameters and refresh for partition event_day=20
set dt.args.event_day = 20;

REFRESH   dynamic TABLE event_gettime_pt PARTITION (event_day = 20);
```

## Use Cases

* Dynamic table partition field matches the source table field

```sql
CREATE TABLE event_tb_pt (
    event STRING,
    process DOUBLE,
    event_time TIMESTAMP
  );
INSERT INTO event_tb_pt VALUES
  ('event-0', 20.0, TIMESTAMP '2024-09-20 14:43:13'),
  ('event-0', 20.0, TIMESTAMP '2024-09-19 11:40:13'),
 ('event-1', 20.0, TIMESTAMP '2024-09-19 11:40:13');
-- Create dynamic table
CREATE dynamic table  event_gettime_pt 
partitioned by(event)
AS SELECT
  event,
  process,
  YEAR(event_time) event_year,
  MONTH(event_time) event_month,
  DAY(event_time) event_day
FROM event_tb_pt
where event=SESSION_CONFIGS()['dt.args.event'];
-- Refresh dynamic table
set dt.args.event = event-0;
REFRESH   dynamic TABLE event_gettime_pt PARTITION (event = 'event-0');
SELECT *FROM event_gettime_pt;
```

* Dynamic table partition field name does not match the source table field. The filter condition needs to filter based on the `event` field, while the dynamic table's partition field is `event_year`.

```sql
DROP      TABLE IF EXISTS event_tb_pt;
CREATE TABLE event_tb_pt (
    event STRING,
    process DOUBLE,
    event_time TIMESTAMP
  );
INSERT INTO event_tb_pt VALUES
  ('event-0', 20.0, TIMESTAMP '2024-09-20 14:43:13'),
  ('event-0', 20.0, TIMESTAMP '2024-09-19 11:40:13'),
 ('event-1', 20.0, TIMESTAMP '2024-09-19 11:40:13');
-- Create dynamic table
DROP dynamic TABLE IF EXISTS event_gettime_pt;
CREATE dynamic table  event_gettime_pt 
partitioned by(event_year)
AS SELECT
  event,
  process,
  YEAR(event_time) event_year,
  MONTH(event_time) event_month,
  DAY(event_time) event_day
FROM event_tb_pt
where event=SESSION_CONFIGS()['dt.args.event'];
-- Refresh dynamic table
set dt.args.event = event-0;
REFRESH   dynamic TABLE event_gettime_pt PARTITION (event_year = 2024);
SELECT * FROM  event_gettime_pt;
```

* Multi-level partition refresh

```sql
DROP      TABLE IF EXISTS event_tb_pt;
CREATE TABLE event_tb_pt (
    event STRING,
    process DOUBLE,
    event_time TIMESTAMP
  );
INSERT INTO event_tb_pt VALUES
  ('event-0', 20.0, TIMESTAMP '2024-09-20 14:43:13'),
  ('event-0', 20.0, TIMESTAMP '2024-09-19 11:40:13'),
 ('event-1', 20.0, TIMESTAMP '2024-09-19 11:40:13');
-- Create dynamic table
DROP dynamic TABLE IF EXISTS event_gettime_pt;
CREATE dynamic table  event_gettime_pt 
partitioned by(event_year,event_month,event_day)
AS SELECT
  event,
  process,
  YEAR(event_time) event_year,
  MONTH(event_time) event_month,
  DAY(event_time) event_day
FROM event_tb_pt
where event=SESSION_CONFIGS()['dt.args.event'];
-- Multi-level partition refresh, specifying high-level partitions
set dt.args.event = event-0;
REFRESH   dynamic TABLE event_gettime_pt PARTITION (event_year = 2024,event_month =9);
```

## Scenario Cases

**Case 1: Converting Offline Tasks to Incremental Tasks**

This section guides users on how to convert existing offline tasks to incremental tasks for more efficient data processing. The following is a specific operation procedure based on "traditional scheduling", applicable to scenarios where business logic is aligned by day and scheduled for daily refresh.

* Step 1: Parameterize the original SQL. The original SQL is as follows:

  ```sql
  with tmp_channel as (
    select
      channel_code,
      channel_name,
      channel_type,
      channel_uid
    from dim.dim_shop_sales_channel_main
    where pt = '${bizdate}'
  ), tmp_bac_misc as (
    select
      mini_number,
      bac_no
    from dim.dim_customer_bac_misc_df
    where pt = '${bizdate}'
  ), tmp_fxiaoke as (
    select
      case
        when record_type in ('dealer__c') then nvl(bac_no, account_no)
        else account_no
      end as channel_code,
      id,
      account_no
    from ods.ods_account_obj as a
    left join tmp_bac_misc on a.account_no = tmp_bac_misc.mini_number
    where pt = '${bizdate}' and account_no is not null
  --  and is_deleted = 0
  --  and life_status not in ('invalid', 'ineffective')
  )
  insert overwrite table dim.dim_shop_sales_channel_misc partition(pt='${bizdate}')
  select
    tmp_channel.channel_code,
    channel_name,
    channel_type,
    channel_uid,
    id as fxiaoke_id,
    account_no as fxiaoke_account_no
  from tmp_channel
  left join tmp_fxiaoke on tmp_channel.channel_code = tmp_fxiaoke.channel_code ;
  ```

  First, replace all `${bizdate}` parameters passed by the scheduling engine in the original SQL with `SESSION_CONFIGS()['dt.args.bizdate']`. This step allows parameter values to be dynamically passed through configuration rather than being hardcoded in SQL.

  **Original SQL Parameter Replacement**:
  Replace all `${bizdate}` with `SESSION_CONFIGS()['dt.args.bizdate']`:

  ```sql
  create dynamic table im.dim_shop_sales_channel_misc
  partitioned by(pt)
  with tmp_channel as (
    select
      channel_code,
      channel_name,
      channel_type,
      channel_uidfrom dim.dim_shop_sales_channel_main
      where pt = SESSION_CONFIGS()['dt.args.bizdate']
  ), tmp_bac_misc as (
    select
      mini_number,
      bac_nofrom dim.dim_customer_bac_misc_df
      where pt = SESSION_CONFIGS()['dt.args.bizdate']
  ), tmp_fxiaoke as (
    select
      case
        when record_type in ('dealer__c') then nvl(bac_no, account_no)
        else account_noend as channel_code,
      id,
      account_nofrom ods.ods_account_obj as aleft join tmp_bac_misc on a.account_no = tmp_bac_misc.mini_number
      where pt = SESSION_CONFIGS()['dt.args.bizdate'] and account_no is not null
  )
  select
    tmp_channel.channel_code,
    channel_name,
    channel_type,
    channel_uid,
    id as fxiaoke_id,
    account_no as fxiaoke_account_no,
    pt
  from tmp_channel
  left join tmp_fxiaoke on tmp_channel.channel_code = tmp_fxiaoke.channel_code
  ;
  ```

* Step 2: Schedule the refresh command
  At each scheduling, the parameter `dt.args.bizdate` needs to be set to a specific date value and the refresh command executed.

  Example scheduling refresh command:

  ```sql
  SET dt.args.bizdate=20241130; -- ${bizdate} is replaced by Studio with a specific value each time
  REFRESH DYNAMIC TABLE DT PARTITION (pt ='20241130');
  ```

**Case 2: Backfilling Data for Incremental Tasks**

In some cases, users may need to supplement data into existing partitions.

* Method 1: Supplement data into the source table. Users can directly insert or update data into the source table. This supplemented data will be automatically reflected in the Dynamic Table (DT) through the corresponding REFRESH task.

  Steps:

  1. Directly insert or update data into the source table.
  2. Execute the REFRESH task to synchronize changes to the DT.
* Method 2: Use DML statements to directly supplement data into the DT. Users can also use DML statements to directly insert data into specific partitions of the DT.
  Steps:
  1. Use DML statements to insert data into specific partitions of the DT.
  2. Note that directly modifying the DT will cause the next full refresh of that partition. If users do not want the result of a full refresh, they should avoid scheduling the REFRESH task for that partition.
     Example Code:
  ```sql
  INSERT INTO DYNAMIC TABLE incremental_dt VALUES (...);
  ```

**Notes**:

* Data directly inserted into the DT will participate in downstream computations of the DT. If downstream old partitions do not need this data, do not schedule REFRESH tasks involving those partitions.
* Other unaffected partitions can still undergo incremental refresh.

**Case 3: Executing Incremental Tasks in Different VCs**

For parameterized, partitioned DTs, refresh tasks for different partitions can be executed simultaneously. Users can assign different REFRESH tasks to different virtual clusters (VCs) as needed.
**Steps**:
1. Based on timeliness requirements and resource needs, assign different REFRESH tasks to different VCs.
2. For example, for new partitions with higher timeliness requirements, their REFRESH tasks can be placed in a larger VC with more resources.
3. For supplementary tasks of other old partitions, their REFRESH tasks can be placed in a smaller VC with fewer resources.
