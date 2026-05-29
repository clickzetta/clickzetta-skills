# Lakehouse Time Travel

Lakehouse Time Travel allows users to access historical data at any point within a defined retention period, including data that has been changed or deleted.

## Overview

Time Travel is implemented on top of Lakehouse's MVCC (Multi-Version Concurrency Control) mechanism — every data change generates a new version. Users can query historical data by specifying a timestamp or version number.

> ⚠️ **Note**: Time Travel incurs storage fees. The default retention period is **1 day** (24 hours). Setting a longer retention period increases storage costs.

## Application Scenarios

1. **Recover accidentally deleted or modified data**: Restore a dropped table with `UNDROP TABLE`, or roll back to a specific point in time with `RESTORE TABLE`
2. **Data comparison and analysis**: Compare data changes between different points in time
3. **Audit and compliance**: Trace historical data states

## Time Travel Retention Period

The default retention period for Lakehouse table history is **1 day** (24 hours). To retain history longer, set it per table:

```sql
-- Set retention period to 7 days
ALTER TABLE tablename SET PROPERTIES ('data_retention_days'='7');

-- Specify retention period at table creation
CREATE TABLE orders (id INT, amount DECIMAL(10,2))
PROPERTIES ('data_retention_days'='30');
```

Retention period range: **0–90 days**. Setting to 0 disables version history.

## Query Syntax

```sql
SELECT * FROM <table_name> TIMESTAMP AS OF <timestamp_expression>;
```

`timestamp_expression` supports the following forms:

- Timestamp string literal: `'2024-01-15 14:49:18'`
- CAST conversion: `CAST('2024-01-15 14:49:18' AS TIMESTAMP)`

> ⚠️ **Note**: `timestamp_expression` only accepts **constant literals**. Runtime expressions such as `CURRENT_TIMESTAMP() - INTERVAL 12 HOURS` or `NOW() - INTERVAL 1 HOUR` are NOT supported. To query data from "N hours ago", first check the version timestamp with `DESC HISTORY`, then use the specific timestamp literal.

## View Version History

```sql
DESC HISTORY <table_name>;
```

Returns version number (`version`), timestamp (`time`), row count (`total_rows`), and operation type (`operation`).

## Usage Examples

### Example 1: Query Historical Data

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

INSERT INTO birds VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue');

-- Insert more data
INSERT INTO birds VALUES
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red,Brown');

-- View version history
DESC HISTORY birds;
+---------+-------------------------+------------+-------------+----------+----+
| version |          time           | total_rows | total_bytes |   user   | op |
+---------+-------------------------+------------+-------------+----------+----+
| 3       | 2024-12-23 16:41:47.831 | 4          | 5786        | UAT_TEST | IN |
| 2       | 2024-12-23 16:36:04.426 | 2          | 2859        | UAT_TEST | IN |
| 1       | 2024-12-23 16:36:04.233 | 0          | 0           | UAT_TEST | CR |
+---------+-------------------------+------------+-------------+----------+----+

-- Query data at version 2 (2 rows)
SELECT * FROM birds TIMESTAMP AS OF '2024-12-23 16:36:04.426';
+----+----------+-------------+---------+
| id |   name   | wingspan_cm | colors  |
+----+----------+-------------+---------+
| 1  | Sparrow  | 15.5        | Brown   |
| 2  | Blue Jay | 20.2        | Blue    |
+----+----------+-------------+---------+
```

### Example 2: Historical Data JOIN

```sql
-- Current version query (4 students)
SELECT s.name, s.class, sc.score
FROM students s
INNER JOIN scores sc ON s.name = sc.name;

-- Query historical version (2 students)
SELECT s.name, s.class, sc.score
FROM students TIMESTAMP AS OF '2024-12-23 16:15:22.957' s
INNER JOIN scores sc ON s.name = sc.name;
```

### Example 3: Restore TRUNCATE'd Data

```sql
-- Create table and insert data
CREATE TABLE birds (id INT, name VARCHAR(50));
INSERT INTO birds VALUES (1, 'Sparrow'), (2, 'Blue Jay');

-- Truncate the table
TRUNCATE TABLE birds;

-- Query data before truncation via Time Travel
SELECT * FROM birds TIMESTAMP AS OF '2024-01-15 10:00:00';

-- Restore data
INSERT OVERWRITE TABLE birds
SELECT * FROM birds TIMESTAMP AS OF '2024-01-15 10:00:00';
```

### Example 4: Back Up Historical Data to a New Table

```sql
CREATE TABLE birds_backup AS
SELECT * FROM birds TIMESTAMP AS OF '2024-01-15 10:00:00';
```

## Usage Restrictions

- **Views** do not support Time Travel queries
- **External schemas** do not support Time Travel
- **RealtimeStream uncommitted data** does not support Time Travel queries
- The query timestamp cannot be earlier than the table creation time, nor exceed the data retention period
- Future timestamps cannot be queried

## Permission Requirements

Users need `SELECT` permission on the table.

## Related Documentation

- [UNDROP TABLE](UNDROP-TABLE.md): Restore a dropped table
- [RESTORE TABLE](restore.md): Roll back a table to a specific point in time
- [Data Lifecycle](data-lifecycle.md): Configure automatic data cleanup
- [Time Travel Guide](SQL_Time_Travel_Guide.md): Typical Time Travel use cases including data recovery, historical snapshot comparison, and RESTORE operations
