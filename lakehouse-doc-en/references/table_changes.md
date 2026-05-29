# Description

`table_changes` is a table function used to query data changes in Lakehouse tables, dynamic tables, and materialized views. By specifying a time interval, this function can return data changes within that interval without the need to create a table stream. When using `table_changes`, you need to ensure that the `change_tracking` feature is enabled. Enable it by executing `ALTER TABLE tbname SET PROPERTIES ('change_tracking'='true');` on the table. Whether you can view the operation history of objects depends on the data retention period. The default data retention period is seven days.

# Syntax
```SQL
TABLE_CHANGES(table_str, start_timestamp, end_timestamp)
```
**Parameter Requirements**:

* `table_str`: The name of an existing table, dynamic table, or materialized view, provided as a string. Supports 'schema.tbname' and 'tbname' format strings. If the schema is not specified, the current schema, i.e., `current_schema`, is used by default.
* `start_timestamp`: The start time of the query's time version, provided as a standard timestamp type expression.
* `end_timestamp`: The end time of the query's time version, provided as a standard timestamp type expression.
* options: Optional parameters, currently supporting map('TABLE\_STREAM\_MODE', 'ORIGINAL'). When this parameter is added, it indicates that the original records of table changes are obtained. If this parameter is not added, for example, if a record is inserted and then deleted between start\_timestamp and end\_timestamp, the query will not find it. If the ORIGINAL parameter is added, the insert and delete records will be displayed.

**Notes**:

* The specified `start_timestamp` cannot be earlier than the table creation time, nor can it exceed the data retention period.
* `start_timestamp` and `end_timestamp` represent the start and end times of the query, respectively. The query result does not include the data at the `start_timestamp` moment but includes the data at the `end_timestamp` moment. The query time interval is (start\_timestamp, end\_timestamp], with the left side being an open interval and the right side being a closed interval.

# Example

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
Example 2: View Dynamic Table Changes

```SQL
-- Create a test table to store employee information
CREATE TABLE customer(id INT, name STRING, phone BIGINT, email STRING);
-- Insert data
INSERT INTO customer VALUES
(1, 'Alice', 1234567890, 'alice@example.com'),
(2, 'Bob', 2345678901, 'bob@example.com'),
(3, 'Carol', 3456789012, 'carol@example.com'),
(4, 'Dave', 4567890123, 'dave@example.com'),
(5, 'Eve', 5678901234, 'eve@example.com');
-- Create a dynamic table to process data
CREATE DYNAMIC TABLE customer_masked AS
SELECT id, name, MASK_OUTER(phone, 3, 4) AS phone, MASK_INNER(email, 0, 12) AS email
FROM customer;
-- Enable change_tracking
ALTER TABLE customer_masked SET PROPERTIES ('change_tracking'='true');
-- Refresh the dynamic table
REFRESH DYNAMIC TABLE customer_masked;
-- Insert data into the base table
INSERT INTO customer VALUES
(6, 'Alaac', 1234567890, 'alabcce@example.com');
-- Refresh the dynamic table
REFRESH DYNAMIC TABLE customer_masked;
-- View historical versions
DESC HISTORY customer_masked;
-- View data changes in the dynamic table, you can see a new record has been added
SELECT * FROM TABLE_CHANGES('customer_masked', TIMESTAMP '2024-01-24 20:14:19.726', TIMESTAMP '2024-01-24 20:55:43.049');
+---------------+------------------+-------------------------+----+-------+------------+---------------------+
| __change_type | __commit_version |   __commit_timestamp    | id | name  |   phone    |        email        |
+---------------+------------------+-------------------------+----+-------+------------+---------------------+
| INSERT        | 4                | 2024-01-24 20:55:43.049 | 6  | Alaac | XXX456XXXX | XXXXXXX@example.com |
+---------------+------------------+-------------------------+----+-------+------------+---------------------+
```
Example 3:Display Original Records
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
-- Show original records
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
-- Show compressed records
select * from table_changes('students_change',timestamp '2024-09-29 20:03:50.58',current_timestamp());
+---------------+------------------+-------------------------+-------+-------+
| __change_type | __commit_version |   __commit_timestamp    | name  | class |
+---------------+------------------+-------------------------+-------+-------+
| DELETE        | 3                | 2024-09-29 20:03:50.399 | Alice | A     |
+---------------+------------------+-------------------------+-------+-------+
```
# Precautions

1. When using the `table_changes` function, please ensure that the `change_tracking` feature is enabled.
2. The specified `start_timestamp` cannot be earlier than the table creation time, nor can it exceed the data retention period.
3. The query results do not include the data at the `start_timestamp` moment, but include the data at the `end_timestamp` moment.