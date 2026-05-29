# Dynamic Table Support for DML Statements to Modify Data

Dynamic Table (DT) provides direct data modification capabilities through DML (Data Manipulation Language) statements for inserting, updating, and deleting data. However, for safety reasons, these operations are disabled by default to prevent accidental data corruption. To enable DML operations, the user must explicitly set the system parameter: `set cz.optimizer.incremental.backfill.enabled=true;`. All non-refresh data modifications are considered backfill operations.

Once enabled, DT supports the following DML operations:

*   **Insert Operations**: Support for `INSERT` and `INSERT OVERWRITE` statements.
*   **Delete Operations**: Support for `DELETE` and `TRUNCATE` statements.

**Important Notes**

*   **Full Refresh**: Once DML modifications have been made to a DT, the next data refresh will automatically switch to a full refresh. This is because the state of intermediate computation results becomes unpredictable; to ensure data consistency and accuracy, the system will recalculate all data.
*   **Parameterized Partitioned DTs**: For parameterized DTs with partitions, if only some partitions are modified, the unmodified partitions can still maintain incremental refresh.

## Inserting Data

```SQL
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
insert into  event_gettime values('event-update',20,2024,9,19);
select * from event_gettime;
```

## Deleting Data

```SQL
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
set cz.optimizer.incremental.backfill.enabled=true;
delete  from event_gettime  where event_day=19;
select * from event_gettime;
```
