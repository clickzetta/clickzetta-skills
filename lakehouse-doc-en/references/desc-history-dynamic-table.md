# Description

The `DESCRIBE HISTORY` command is used to obtain historical information about tables, dynamic tables, or materialized views. Through these historical records, users can perform rollback operations or query table data at specific points in time. Whether the operation history of an object can be viewed depends on the data [retention period](<TIMETRAVEL.md>).


# Syntax 
```SQL
DESCRIBE HISTORY object_name;
```
Parameter Description:

- `object_name`: Supported types include table, dynamic table, and materialized view.

#  Example

Example 1: View the history of a dynamic table
```SQL
DESC HISTORY public.event_gettime;
```
After executing this command, the history of the `public.event_gettime` dynamic table will be returned, as shown below:
```
+---------+-------------------------+------------+-------------+----------+-----------+-------------------------------+------------------------------------------------------------------------------------+
| version |          time           | total_rows | total_bytes |   user   | operation |            job_id             |                                                      source_tables                 |
+---------+-------------------------+------------+-------------+----------+-----------+-------------------------------+------------------------------------------------------------------------------------+
| 3       | 2024-01-31 17:49:28.814 | 5          | 7578        |          | REFRESH   | 202401310949284215k3g3xp367rm | [{"table_name":"event_tb","workspace":"ql_ws","schema":"public","version":"3","com |
| 2       | 2024-01-31 17:48:11.862 | 4          | 3820        |          | REFRESH   | 2024013109481169177wieyw9xl51 | [{"table_name":"event_tb","workspace":"ql_ws","schema":"public","version":"2","com |
| 1       | 2024-01-31 17:48:11.656 | 0          | 0           |          | CREATE    | 2024013109481148777wieyw9xkqo | [{"table_name":"event_tb","workspace":"ql_ws","schema":"public}]                  |
+---------+-------------------------+------------+-------------+----------+-----------+-------------------------------+------------------------------------------------------------------------------------+

SELECT * FROM public.event_gettime TIMESTAMP AS OF '2024-01-31 17:48:11.862';

+---------+---------+------------+-------------+-----------+------------+--------------+
|  event  | process | event_year | event_month | event_day | event_hour | event_minute |
+---------+---------+------------+-------------+-----------+------------+--------------+
| event-0 | 20.0    | 2023       | 9           | 20        | 14         | 43           |
| event-0 | 20.0    | 2023       | 9           | 19        | 11         | 40           |
| event-1 | 21.0    | 2023       | 9           | 19        | 14         | 30           |
| event-1 | 22.0    | 2023       | 9           | 20        | 14         | 20           |
+---------+---------+------------+-------------+-----------+------------+--------------+
```
# Precautions

- When using the `DESCRIBE HISTORY` command, make sure that `object_name` is a valid table, dynamic table, or materialized view name.
- When querying data at a specific point in time, ensure that the provided time format is correct.