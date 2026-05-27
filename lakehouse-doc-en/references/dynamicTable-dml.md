# Dynamic Table Supports DML Statements to Modify Data

Dynamic Table (DT) provides the ability to directly modify data through DML (Data Manipulation Language) statements, enabling operations such as inserting, updating, and deleting data. However, for safety reasons, these operations are disabled by default to prevent accidental data corruption. To enable DML operations, users must explicitly set the system parameter: SET cz.sql.dt.allow\.dml = true;

Once enabled, DT will support the following DML operations:

* **Insert Operation**: Supports `INSERT` and `INSERT OVERWRITE` statements.
* **Delete Operation**: Supports `DELETE` and `TRUNCATE` statements.

**Notes**

* **Full Refresh**: Once a DML modification is made to DT, the next data refresh will automatically switch to a full refresh. This is because the state of intermediate calculation results will become unpredictable. To ensure data consistency and accuracy, the system will recalculate all data.
* **Parameterized Partitioned DT**: For parameterized DTs with partitions, if only some partitions are modified, the unmodified partitions can still maintain incremental refresh.

Insert Data
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
# Delete Data

Delete Data
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
set cz.sql.dt.allow.dml=true;
delete  from event_gettime  where event_day=19;
select * from event_gettime;
```