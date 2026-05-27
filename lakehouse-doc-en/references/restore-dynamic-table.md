## Description

**Historical Version Recovery**:
Using this command, you can restore an undeleted table or dynamic table to a specified historical version. With the time travel feature, you can easily roll back the table state to a past moment to recover data when needed.

**Data Retention Period**:
The historical recovery capability of objects depends on the data retention period. The current preview version has a default data retention period of 7 days, which will be adjusted to 1 day in the future. You can adjust the retention period by executing the [ALTER command](TIMETRAVEL.md). Please note that modifying the retention period may increase storage costs. Supported tables (TABLE) and dynamic tables (DYNAMIC TABLE) do not support materialized views.

## Syntax 
```SQL
RESTORE TABLE table_name TO time_travel_version;
time_travel_version ::= 
    TIMESTAMP AS OF timestamp_expression;
```
## Parameter Description

1. **table\_name**: Specifies the name of the table that has not been deleted. It can be a TABLE, DYNAMIC TABLE, or MATERIALIZED VIEW. If the table has been deleted, please use the [UNDROP](UNDROP-TABLE.md) command to restore it.
2. **time\_travel\_version**: Specifies the version of the table to be restored. First, use DESC HISTORY table\_name to view the version time points, then use the `TIMESTAMP AS OF` clause to specify the exact time point. timestamp\_expression is a parameter that returns an expression of timestamp type, for example:

* `'2023-11-07 14:49:18'`, a string that can be forcibly converted to a timestamp.
* `CAST('2023-11-07 14:49:18' AS TIMESTAMP)`.
* `CURRENT_TIMESTAMP() - INTERVAL 12 HOURS`. The version from 12 hours ago.
* Any expression that is itself a timestamp type or can be forcibly converted to a timestamp.

# Description

**Case 1: Use the RESTORE command to restore a regular table to a specified version**
```SQL
-- View the change history of the table
DESC HISTORY json_table;

-- Use the RESTORE command to revert to a specified version
RESTORE TABLE json_table TO TIMESTAMP AS OF '2024-01-26 17:44:45.349';
SELECT * FROM json_table;

-- Query results
+----------------------------------+
|                j                 |
+----------------------------------+
| {"id":1,"value":"200"}           |
| {"id":2,"value":"300"}           |
| {"extra":1,"id":3,"value":"400"} |
| {"value":"100"}                  |
+----------------------------------+
```
**Case 2: Use the RESTORE Command to Restore Dynamic Table to a Specified Version**

* Note that if the data of the tables that the dynamic table depends on has not changed, the dynamic table will be refreshed to the original result next time.
```
DROP TABLE  IF EXISTS dy_base_a;
CREATE TABLE dy_base_a (i int, j int);
INSERT INTO dy_base_a VALUES
(1,10),
(2,20),
(3,30),
(4,40);
-- Use dynamic table for processing
DROP DYNAMIC TABLE  IF EXISTS change_table;
CREATE  DYNAMIC TABLE change_table
(i,j)
AS select * from dy_base_a;
-- Refresh dynamic table
refresh DYNAMIC TABLE change_table;
-- Query table data
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
-- Insert data into the base table
INSERT INTO dy_base_a VALUES(5,10);
-- Refresh dynamic table
refresh DYNAMIC TABLE change_table;
-- Query table data
SELECT    *
FROM      change_table;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
| 5 | 10 |
+---+----+
-- Restore to the initial version
DESC HISTORY change_table;
+---------+-------------------------+------------+-------------+----------+-----------+-------------------------------+------------------------------------------------------------------------------------+
| version |          time           | total_rows | total_bytes |   user   | operation |            job_id             |                                                       source_tables                |
+---------+-------------------------+------------+-------------+----------+-----------+-------------------------------+------------------------------------------------------------------------------------+
| 3       | 2024-12-27 12:04:20.738 | 5          | 4950        | UAT_TEST | REFRESH   | 2024122712042034961pl5i9617jc | [{"table_name":"dy_base_a","workspace":"qingyun","schema":"public","version":"3"," |
| 2       | 2024-12-27 12:01:33.349 | 4          | 2501        | UAT_TEST | REFRESH   | 2024122712013303061pl5i9617dk | [{"table_name":"dy_base_a","workspace":"qingyun","schema":"public","version":"2"," |
| 1       | 2024-12-27 12:01:33.078 | 0          | 0           | UAT_TEST | CREATE    | 2024122712013279961pl5i9616do | [{"table_name":"dy_base_a","workspace":"qingyun","schema":"public"}]               |
+---------+-------------------------+------------+-------------+----------+-----------+-------------------------------+------------------------------------------------------------------------------------+
-- Restore to the specified version
RESTORE TABLE change_table TO TIMESTAMP AS OF '2024-12-27 12:01:33.349';
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
```
# Notes

1. Please ensure that the specified point in time for executing the RESTORE command is within the table's retention period.
2. After executing the RESTORE command, the table's data will be restored to the specified historical version, but subsequent historical versions will not be deleted.
3. Use the RESTORE command with caution to avoid the risk of data loss or inconsistency. It is recommended to back up relevant data before performing this operation.