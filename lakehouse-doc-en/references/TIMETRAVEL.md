## Introduction to Lakehouse Time Travel Functionality

The Time Travel functionality of Lakehouse allows users to access historical data at any point within a defined time period, including data that has been changed or deleted. Currently, this feature is in Preview version and offers a free seven-day data retention period. During this period, users can query data within seven days. After the retention period, Lakehouse will charge storage fees for the Time Travel functionality separately and will adjust the default retention period to one day.

## Application Scenarios

1. Recover data that may have been accidentally or intentionally deleted.
2. Copy and back up critical data from the past.
3. Analyze data changes within a specified time period.

##  Syntax
```sql
SELECT 
    table_identifier TIMESTAMP AS OF timestamp_expression
```
By using the TIMESTAMP AS OF clause, users can specify a specific point in time to query the exact position in the table's history within the retention period or the data just before the specified point. The timestamp_expression is a parameter that returns a timestamp type expression, for example:

* `'2023-11-07 14:49:18'`, a string that can be cast to a timestamp.
* `CAST('2023-11-07 14:49:18' AS TIMESTAMP)`.
* `CURRENT_TIMESTAMP() - INTERVAL 12 HOURS`. The version from 12 hours ago.
* Any expression that is itself a timestamp type or can be cast to a timestamp.

## Query Description

* By specifying a point in time, users can query the version data at the specified time.
* The specified point in time cannot be earlier than the table creation time, nor can it exceed the data retention period. If the specified point in time is out of range, an error will be reported.
* If the timestamp_expression is a future time, an error will also be reported because future data is not available.

## Permission Requirements

* Users need to have SELECT permissions on the table.

## Usage Restrictions

* Views do not support Time Travel queries.
* External schemas are not supported.
* The data retention period is currently seven days. After the retention period, queries cannot be performed.
* RealtimeStream real-time writes of uncommitted data do not support Time Travel queries. This is because RealtimeStream prioritizes writing to a temporary area to facilitate quick queries for real-time query functionality. Time Travel queries rely on querying committed records, so it is currently not possible to query uncommitted data written by RealtimeStream.

## Example

### Analyzing Data Within a Specified Time Period

```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');

-- Insert more data
INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (5, 'Hummingbird', 8.2, 'Green'),
    (6, 'Penguin', 99.5, 'Black", "White'),
    (7, 'Eagle', 200.8, 'Brown'),
    (8, 'Owl', 105.3, 'Gray'),
    (9, 'Flamingo', 150.6, 'Pink'),
    (10, 'Pelican', 180.4, 'White');
-- View version
DESC HISTORY birds;
+---------+-------------------------+------------+-------------+----------+----+
| version |          time           | total_rows | total_bytes |   user   |  o |
+---------+-------------------------+------------+-------------+----------+----+
| 3       | 2024-12-23 16:41:47.831 | 10         | 5786        | UAT_TEST | IN |
| 2       | 2024-12-23 16:36:04.426 | 4          | 2859        | UAT_TEST | IN |
| 1       | 2024-12-23 16:36:04.233 | 0          | 0           | UAT_TEST | CR |
+---------+-------------------------+------------+-------------+----------+----+
-- Query after waiting for five minutes
SELECT * FROM birds TIMESTAMP AS OF timestamp'2024-12-23 16:36:04.426';
+----+----------+-------------+-------------+
| id |   name   | wingspan_cm |   colors    |
+----+----------+-------------+-------------+
| 1  | Sparrow  | 15.5        | Brown       |
| 2  | Blue Jay | 20.2        | Blue        |
| 3  | Cardinal | 22.1        | Red         |
| 4  | Robin    | 18.7        | Red","Brown |
+----+----------+-------------+-------------+
```
### Join data of a specified version with other tables
```
DROP TABLE students;
DROP TABLE scores;
CREATE TABLE students (name string, class string);
INSERT INTO students (name, class) VALUES
('Alice', 'A'),
('Bob', 'B');
CREATE TABLE scores (name string, score int);
INSERT INTO scores (name, score) VALUES
('Alice', 90),
('Bob', 80),
('Carol', 85),
('David', 95);

--Wait 1 minute to insert
INSERT INTO students (name, class) VALUES
('Carol', 'A'),
('David', 'C');
--View version
DESC HISTORY  students;
+---------+-------------------------+------------+-------------+----------+----+
| version |          time           | total_rows | total_bytes |   user   |  o |
+---------+-------------------------+------------+-------------+----------+----+
| 3       | 2024-12-23 16:17:01.792 | 4          | 3884        | UAT_TEST | IN |
| 2       | 2024-12-23 16:15:22.957 | 2          | 1939        | UAT_TEST | IN |
| 1       | 2024-12-23 16:15:22.829 | 0          | 0           | UAT_TEST | CR |
+---------+-------------------------+------------+-------------+----------+----+
--Current version query
SELECT students.name, students.class, scores.score
FROM students 
INNER JOIN scores
ON students.name = scores.name;
+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Carol | A     | 85    |
| Bob   | B     | 80    |
| David | C     | 95    |
| Alice | A     | 90    |
+-------+-------+-------+
--Use students version from 2024-12-23 16:15:22.957
SELECT students.name, students.class, scores.score
FROM students timestamp as of '2024-12-23 16:15:22.957'
INNER JOIN scores
ON students.name = scores.name;
+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Alice | A     | 90    |
| Bob   | B     | 80    |
+-------+-------+-------+

```
### Restore Data That May Have Been Accidentally or Intentionally Deleted

Simulate data deletion:
```sql
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');

-- Delete data
TRUNCATE TABLE birds;

-- Check if the data still exists
SELECT * FROM birds; -- Data has been deleted
```
Viewing the truncate time of the running history:
```
DESCRIBE HISTORY birds;
```

Restoring data:
```sql
-- View the data before deletion, set the time travel version according to the execution time of the above run history
SELECT * FROM birds TIMESTAMP AS OF '2023-11-07 14:49:18';

-- Restore data
INSERT OVERWRITE TABLE birds
SELECT * FROM birds TIMESTAMP AS OF '2023-11-07 14:49:18';
```
## Copy and Backup Data from Past Key Points.

You can back up data from a specified point in time to another table.
```
CREATE    TABLE birds_backup AS
SELECT    *
FROM      birds TIMESTAMP AS OF '2023-11-20 15:48:40';

SELECT    *
FROM      birds_backup;

```