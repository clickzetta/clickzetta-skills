# CREATE ....CLONE

>【Preview Release】This feature is currently in public preview.

In Lakehouse, the clone table operation creates an independent copy of a table that is completely separate from the original table and does not affect each other. Clone tables do not take up additional storage space when created because they share the data version of the original table. However, if the original table data changes and affects the data in the clone table, the clone table will need to pay for the storage costs of these changes. Clone tables have similar functions to regular tables, including operations such as querying, copying, and deleting. Lakehouse supports cloning regular tables and dynamic tables, and allows creating clones of clones, i.e., cloning a table that is already a clone.

## Notes

* The clone operation does not copy the permissions of the original table, and the newly cloned table will have independent permission settings.
* The clone operation does not copy user-set properties, including lifecycle and data time travel retention periods.
* Real-time written and uncommitted data will not be cloned. Therefore, data that has just been written will not be found in the clone table after the clone is completed.
* Cloning external tables is not supported.

## Normal Table Clone
```SQL
CREATE TABLE [ IF NOT EXISTS ] table_name
  CLONE <source_object_name> [TIMESTAMP AS OF timestamp_expression]
```
* You can use `TIMESTAMP AS OF timestamp_expression` to clone the version of the dynamic table at a specified point in time. As long as the point in time is within the **[data retention period](TIMETRAVEL.md)** (`data_retention_days`)
  * `timestamp_expression` can be any of the following:
    * `'2024-10-18T22:15:12.013Z'`, i.e., a string that can be cast to a timestamp
    * `cast('2024-10-18 13:36:32 ' as timestamp)`
    * `'2024-10-18'`, i.e., a date string
    * `current_timestamp() - interval 12 hours`
    * `date_sub(current_date(), 1)`
    * Any other expression that is itself a timestamp or can be cast to a timestamp
```
CREATE TABLE normal_table_clone_version CLONE normal_table_base TIMESTAMP AS OF '2024-10-12 19:23:52.329';
```
## Dynamic Table Cloning
```SQL
CREATE DYNAMIC TABLE dt_name
 [
    refreshOption ::=
    REFRESH [START WITH timestamp_expr] [interval_time] VCLUSTER vcname   
 ]
  CLONE <source_dynamic_table> [TIMESTAMP AS OF timestamp_expression]
```
* The cloned dynamic table is paused by default. You can use `ALTER DYNAMIC TABLE table_name RESUME;` to start the refresh task.
* `DYNAMIC TABLE dt_name`: The name of the dynamic table to be created. `dt_name` is a placeholder that you need to replace with the actual table name.
* `REFRESH`: Specifies the refresh options for the table. When creating a cloned dynamic table, you can specify the refresh options:
  * If refresh options are specified, the refresh strategy of the cloned table is used.
  * If no refresh options are specified, the default refresh strategy is used.
* `START WITH timestamp_expr`: Optional clause that specifies the start time for the table refresh. `timestamp_expr` is a timestamp expression.
* `interval_time`: Specifies the refresh interval time unit. This is of type `INTERVAL` and can be any of the following:
    *  INTERVAL 1 year 
    *  INTERVAL 2 month 
    *  INTERVAL 3 day 
    *  INTERVAL 4 hour 
    *  INTERVAL 5 minute
    *  INTERVAL 30 second
* `VCLUSTER vcname`: Specifies the name of the compute cluster. `vcname` is the actual name of the compute cluster.
* `CLONE <source_dynamic_table>`: Clones from an existing dynamic table `<source_dynamic_table>`.
* `TIMESTAMP AS OF timestamp_expression`: The version of the cloned dynamic table at the specified point in time. `timestamp_expression` can be one of several timestamp expressions. As long as the point in time is within the [data retention period](TIMETRAVEL.md) (`data_retention_days`):
  * `timestamp_expression` can be any of the following:
    * `'2024-10-18T22:15:12.013Z'`, i.e., a string that can be cast to a timestamp
    * `cast('2024-10-18 13:36:32 ' as timestamp)`
    * `'2024-10-18'`, i.e., a date string
    * `current_timestamp() - interval 12 hours`
    * `date_sub(current_date(), 1)`
    * Any other expression that is itself a timestamp or can be cast to a timestamp  

## Permission Requirements

* You need `CREATE TABLE` permission in the current schema to create a cloned table.
* You need `SELECT` permission on the original table.

## Cloned Table Examples

### Clone a Regular Table
```SQL
-- Create a normal table
CREATE TABLE normal_table_base (id BIGINT, col STRING);

-- Clone the normal table
CREATE TABLE normal_table_clone CLONE normal_table_base;

-- Clone the base table at a specific version
CREATE TABLE normal_table_clone_version CLONE normal_table_base TIMESTAMP AS OF '2024-10-12 19:23:52.329';
```
### Clone Dynamic Table
```SQL
-- Create dynamic table
CREATE DYNAMIC TABLE dt_table_base
REFRESH INTERVAL 1 MINUTE
VCLUSTER DEFAULT
AS SELECT * FROM normal_table_base;

-- Clone dynamic table
CREATE DYNAMIC TABLE dt_table_clone CLONE dt_table_base;

-- Specify refresh interval and compute cluster when cloning
CREATE DYNAMIC TABLE dt_table_clone_refresh
REFRESH INTERVAL 2 MINUTE
VCLUSTER DEFAULT
CLONE dt_table_base;

-- Specify the version of the dynamic table when cloning
CREATE DYNAMIC TABLE dt_table_clone_version
CLONE dt_table_base TIMESTAMP AS OF '2024-10-12 20:25:32.247';
```