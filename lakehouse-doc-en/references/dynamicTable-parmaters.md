# Parameterized Definition Dynamic Table Creation Syntax

When the dynamic table is a partitioned table, parameters can be passed. Parameters are defined through SESSION\_CONFIGS()\['dt.arg.xx']. SESSION\_CONFIGS() is a built-in system function. For non-partitioned tables, if parameterized definitions are used and the passed parameter values remain unchanged, the system will perform incremental refresh. However, once the parameter values change, the system will perform a full refresh, as this is equivalent to changing the table definition. For partitioned tables, the partition key must be a parameter field, but these parameter fields are not required to be partition columns of the table.

## Creation Statement

The parameterized definition of a Dynamic Table allows users to define parameters through `SESSION_CONFIGS()['dt.arg.xx']`. These parameters are referenced when creating the table, thereby dynamically affecting the content of the table.

* `SESSION_CONFIGS()`：A built-in system function used to read parameters from the configuration.
* `'dt.arg.xx'`：The name of the DT parameter, which must start with `dt.arg.` to avoid conflicts with internal system fields.

### Example Code
```sql
CREATE dynamic table  event_gettime_pt 
partitioned by(event_day)
AS SELECT
  event,
  process,
  YEAR(event_time) event_year,
  MONTH(event_time) event_month,
  DAY(event_time) event_day
FROM event_tb_pt
where day(event_time)=SESSION_CONFIGS()['dt.args.event_day'];
set dt.args.event_day=19;
refresh dynamic table event_gettime_pt partition(event_day=19);
```
In this example, `dt.args.event_day` is a DT parameter, which is read from the configuration using the `SESSION_CONFIGS()` function. If non-string type parameters are needed, the `CAST` function can be used for type conversion.

## Refresh Statement

The refresh behavior of a parameterized Dynamic Table depends on whether the table is partitioned.

### Non-Partitioned Table Refresh Syntax
```sql
REFRESH DYNAMIC TABLE dt;
```
* The parameter values of non-partitioned tables remain unchanged and will be incrementally refreshed.
* The parameter values of non-partitioned tables change, and a full refresh will occur.

### Partitioned Table Refresh Syntax
```sql
REFRESH DYNAMIC TABLE dt PARTITION partition_spec;
```
When refreshing a partitioned table, the `partition_spec` must be specified in the order of the table's partition hierarchy. This means that if the table is partitioned by multiple fields, these fields need to be specified from the highest level to the lowest level.

### Example Description

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
## Precautions

* Parameter and Partition Consistency
  When performing a refresh operation on a Dynamic Table, you must ensure that the parameter values passed in are consistent with the specified partition values to be refreshed. If there is any inconsistency, the system will report an error during execution.

  * **Error Example**：
    ```SQL
    set dt.args.event_day=11; 
    refresh dynamic table event_gettime_pt partition(event_day=19);
    ```
    
    In the above situation, although the parameter event_day is set to 11, the refresh command attempts to write to partition event_day=19. This will cause the actual calculated partition result to be inconsistent with the specified partition, resulting in errors.
    
* **Correct Example**:
  ```sql
  set dt.args.event_day=19;
  refresh dynamic table event_gettime_pt partition(event_day=19);
  ```
* Concurrent Refresh Tasks
  In these commands, the parameter values match the partition values, so they can be executed concurrently without conflicts. As long as there are no conflicts between partitions, the system allows multiple partition refresh tasks to be executed simultaneously.
```sql
-- Set parameters for partition event_day=19 and refresh
set dt.args.event_day=19;
refresh dynamic table event_gettime_pt partition(event_day=19);

-- Set parameters for partition event_day=20 and refresh
set dt.args.event_day=20;
refresh dynamic table event_gettime_pt partition(event_day=20);
```
## Full Refresh and Incremental Refresh

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
REFRESH DYNAMIC TABLE T; -- Parameter x=1 remains unchanged, incremental refresh

-- Partitioned table
SET dt.args.pt=1;
SET dt.args.x=1;
REFRESH DYNAMIC TABLE T PARTITION (pt = 1); -- Parameter x=1 remains unchanged, incremental refresh for partition pt = 1
```
## Scenario Case

**Case 1: Converting Offline Tasks to Incremental Tasks**
This section will guide users on how to convert existing offline tasks into incremental tasks for more efficient data processing. The following are specific operational steps based on a "traditional database," suitable for scenarios where business logic is aligned and scheduled for daily refresh.

* Step 1: Parameterize the original SQL. The original SQL is as follows
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
First, all parameters `${bizdate}` passed in by the scheduling engine in the original SQL need to be replaced with `SESSION_CONFIGS()['dt.args.bizdate']`. This step will allow the parameter values to be dynamically passed in through configuration, rather than being hard-coded in the SQL.

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
* Step 2: Schedule Refresh Command
  During each scheduling, the parameter `dt.args.bizdate` needs to be set to a specific date value, and the refresh command should be executed.

  Example of scheduling refresh command
```sql
SET dt.args.bizdate=20241130; -- ${bizdate} is replaced by Studio with a specific value each time
REFRESH DYNAMIC TABLE DT PARTITION (pt ='20241130');
```
**Case 2: Incremental Task Data Supplementation, in some cases, users may need to supplement data to existing partitions**.

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

* Data directly inserted into DT will participate in downstream calculations of DT. If the downstream old partitions do not require this data, please do not schedule REFRESH tasks involving these partitions.
* Other unaffected partitions can still be incrementally refreshed.

**Case Three: Executing incremental tasks in different VCs. For parameterized partitioned DT, refresh tasks for different partitions can be executed simultaneously. Users can allocate different REFRESH tasks to different Virtual Clusters (VC) as needed**.
Steps

1. Allocate different REFRESH tasks to different VCs based on timeliness requirements and resource needs.
2. For example, for new partitions with high timeliness requirements, their REFRESH tasks can be executed in large VCs with more resources.
3. For supplementary tasks of other old partitions, their REFRESH tasks can be executed in smaller VCs with fewer resources.

^