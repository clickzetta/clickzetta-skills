# Dynamic Table (DT)

Dynamic Table (DT) provides the ability to directly modify data through DML (Data Manipulation Language) statements to perform insert, update, and delete operations. However, for security reasons, these operations are disabled by default to prevent accidental data corruption.

## Enabling DML Operations

To enable DML operations, users must explicitly set the system parameter: `SET cz.sql.dt.allow\.dml = true;`

Once enabled, DT will support the following DML operations:

* **Insert Operations**: Supports `INSERT` and `INSERT OVERWRITE` statements.
* **Delete Operations**: Supports `DELETE` and `TRUNCATE` statements.

**Notes**

* **Full Refresh**: Once DML modifications are made to DT, the next data refresh will automatically switch to a full refresh. This is because the state of intermediate calculation results will become unpredictable. To ensure data consistency and accuracy, the system will recalculate all data.
* **Parameterized Partitioned DT**: For parameterized DTs with partitions, if only some partitions are modified, the unmodified partitions can still maintain incremental refresh.

## Inserting Data

<Notes>

## Permalink
```SQL
CREATE dynamic TABLE event_gettime AS
SELECT    event,
          process,
          YEAR(event_time) event_year,
          MONTH(event_time) event_month,
          DAY(event_time) event_dayFROM event_tb;

set cz.sql.dt.allow.dml = TRUE;

INSERT    INTO event_gettime
VALUES    ('event-update', 20, 2024, 9, 19);

SELECT    *
FROM      event_gettime;
```
# Delete Data
```SQL
CREATE dynamic TABLE event_gettime AS
SELECT    event,
          process,
          YEAR(event_time) event_year,
          MONTH(event_time) event_month,
          DAY(event_time) event_dayFROM event_tb;

set cz.sql.dt.allow.dml = TRUE;

DELETE
FROM      event_gettime
WHERE     event_day = 19;

SELECT    *
FROM      event_gettime;
```

^
