# Description

`table_changes` is a table function used to query data changes in Lakehouse tables, dynamic tables, and materialized views. By specifying a time interval, this function can return the data changes within that interval without creating a table stream. When using `table_changes`, ensure that the `change_tracking` feature is enabled. Execute `ALTER TABLE tbname SET PROPERTIES ('change_tracking'='true');` on the table to enable it. The ability to view object operation history depends on the data retention period. The default data retention period is seven days.

# Syntax

```SQL
TABLE_CHANGES(table_str, start_timestamp, end_timestamp)
```

**Parameters**:

* `table_str`: The name of an existing table, dynamic table, or materialized view, provided in string format. Supports `'schema.tbname'` and `'tbname'` format strings. If no schema is specified, the current schema (`current_schema`) is used by default.
* `start_timestamp`: The starting time of the query time version, provided as a standard timestamp type expression.
* `end_timestamp`: The ending time of the query time version, provided as a standard timestamp type expression.
* options: Optional parameter, currently supports `map('TABLE_STREAM_MODE', 'ORIGINAL')`. When this parameter is added, it retrieves the original records of table changes. When this parameter is not added, for example if a record is first inserted and then deleted between `start_timestamp` and `end_timestamp`, the record will not appear in the query results without this parameter. If the `ORIGINAL` parameter is added, both the insert record and the delete record will be displayed.

**Notes**:

* The specified `start_timestamp` cannot be earlier than the table creation time, and cannot exceed the data retention period.
* `start_timestamp` and `end_timestamp` represent the start and end times of the query respectively. The query result does not include data at the moment of `start_timestamp`, but includes data at the moment of `end_timestamp`. The query time interval is (start_timestamp, end_timestamp], left-open and right-closed.

# Examples

Example 1: View table changes

```SQL
-- Create table
CREATE TABLE students_change(name STRING, class STRING) PARTITIONED BY (class);
-- Enable change_tracking
ALTER TABLE students_change SET PROPERTIES ('change_tracking'='true');
-- Insert data
INSERT INTO students_change (name, class) VALUES
('Alice', 'A'),
('Bob', 'B'),
('Carol', 'A'),
('David', 'C');
-- Insert data
INSERT INTO students_change (name, class) VALUES ('person', 'c');
-- View history versions
DESC HISTORY students_change;
+---------+-------------------------+------------+-------------+----------+-------------+-------------------------------+
| version |          time           | total_rows | total_bytes |   user   |  operation  |            job_id             |
+---------+-------------------------+------------+-------------+----------+-------------+-------------------------------+
| 7       | 2024-02-01 17:53:42.945 | 4          | 7640        | UAT_TEST | INSERT_INTO | 202402010953426415k3g3xp367p7 |
| 6       | 2024-01-29 11:15:41.396 | 3          | 5087        | N/A      |             |                               |
+---------+-------------------------+------------+-------------+----------+-------------+-------------------------------+
-- View data changes between two versions
SELECT * FROM TABLE_CHANGES('students_change', TIMESTAMP '2024-01-29 11:15:41.396', TIMESTAMP '2024-02-01 17:53:42.945');
+---------------+------------------+-------------------------+------+--------+-------+
| __change_type | __commit_version |   __commit_timestamp    | col1 |  name  | class |
+---------------+------------------+-------------------------+------+--------+-------+
| INSERT        | 7                | 2024-02-01 17:53:42.945 | null | person | c     |
+---------------+------------------+-------------------------+------+--------+-------+
```

Example 2: View dynamic table changes

```SQL
-- Create test table to store employee information
CREATE TABLE customer(id INT, name STRING, phone BIGINT, email STRING);
-- Insert data
INSERT INTO customer VALUES
(1, 'Alice', 1234567890, 'alice@example.com'),
(2, 'Bob', 2345678901, 'bob@example.com'),
(3, 'Carol', 3456789012, 'carol@example.com'),
(4, 'Dave', 4567890123, 'dave@example.com'),
(5, 'Eve', 5678901234, 'eve@example.com');
-- Create dynamic table to process data
CREATE DYNAMIC TABLE customer_masked AS
SELECT id, name, MASK_OUTER(phone, 3, 4) AS phone, MASK_INNER(email, 0, 12) AS email
FROM customer;
-- Enable change_tracking
ALTER TABLE customer_masked SET PROPERTIES ('change_tracking'='true');
-- Refresh dynamic table
REFRESH DYNAMIC TABLE customer_masked;
-- Insert data into base table
INSERT INTO customer VALUES
(6, 'Alaac', 1234567890, 'alabcce@example.com');
-- Refresh dynamic table
REFRESH DYNAMIC TABLE customer_masked;
-- View history versions
DESC HISTORY customer_masked;
-- View data changes in the dynamic table, a new record has been added
SELECT * FROM TABLE_CHANGES('customer_masked', TIMESTAMP '2024-01-24 20:14:19.726', TIMESTAMP '2024-01-24 20:55:43.049');
+---------------+------------------+-------------------------+----+-------+------------+---------------------+
| __change_type | __commit_version |   __commit_timestamp    | id | name  |   phone    |        email        |
+---------------+------------------+-------------------------+----+-------+------------+---------------------+
| INSERT        | 4                | 2024-01-24 20:55:43.049 | 6  | Alaac | XXX456XXXX | XXXXXXX@example.com |
+---------------+------------------+-------------------------+----+-------+------------+---------------------+
```

Example 3: Display original records

```SQL
-- Create table
CREATE TABLE students_change(name STRING, class STRING) PARTITIONED BY (class);
-- Enable change_tracking
ALTER TABLE students_change SET PROPERTIES ('change_tracking'='true');
-- Insert data
INSERT INTO students_change (name, class) VALUES
('Alice', 'A'),
('Bob', 'B'),
('Carol', 'A'),
('David', 'C');
-- Update data
UPDATE students_change SET class = lower(class) WHERE name='Alice'; 
UPDATE students_change SET class = lower(class) WHERE name='Alice'; 
DELETE FROM students_change WHERE name = 'Alice';
-- Display original records
select * from table_changes('students_change',timestamp '2024-09-29 20:03:50.58',current_timestamp(),map('TABLE_STREAM_MODE', 'ORIGINAL'));
+---------------+------------------+-------------------------+-------+-------+
| __change_type | __commit_version |   __commit_timestamp    | name  | class |
+---------------+------------------+-------------------------+-------+-------+
| UPDATE_BEFORE | 3                | 2024-09-29 20:03:50.399 | Alice | A     |
| UPDATE_AFTER  | 5                | 2024-09-29 20:05:16.443 | Alice | a     |
| UPDATE_BEFORE | 5                | 2024-09-29 20:05:16.443 | Alice | a     |
| UPDATE_AFTER  | 6                | 2024-09-29 20:05:46.118 | Alice | a     |
| DELETE        | 6                | 2024-09-29 20:05:46.118 | Alice | a     |
+---------------+------------------+-------------------------+-------+-------+
-- Display compressed records
select * from table_changes('students_change',timestamp '2024-09-29 20:03:50.58',current_timestamp());
+---------------+------------------+-------------------------+-------+-------+
| __change_type | __commit_version |   __commit_timestamp    | name  | class |
+---------------+------------------+-------------------------+-------+-------+
| DELETE        | 3                | 2024-09-29 20:03:50.399 | Alice | A     |
+---------------+------------------+-------------------------+-------+-------+
```

# Notes

1. When using the `table_changes` function, ensure that the `change_tracking` feature is enabled.
2. The specified `start_timestamp` cannot be earlier than the table creation time, and cannot exceed the data retention period.
3. The query result does not include data at the moment of `start_timestamp`, but includes data at the moment of `end_timestamp`.
4. `start_timestamp` and `end_timestamp` must be literal timestamp constants. Function expressions (such as `current_timestamp()`, `now() - INTERVAL ...`, `to_timestamp(...)`, etc.) are not supported.
5. `start_timestamp` and `end_timestamp` are parsed according to the current session time zone. The time returned by `DESC HISTORY` is in UTC. Using it directly will cause time range validation to fail; it must be converted to the local time corresponding to the session time zone before filling in. For example, if the session time zone is Asia/Shanghai (UTC+8), add 8 hours to the UTC time. You can check the current session time zone with `SELECT current_timezone()`.
