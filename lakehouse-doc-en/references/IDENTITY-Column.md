# Auto-increment Column IDENTITY

Lakehouse supports identifying columns when creating tables, defining fields as auto-increment fields.

Configure the auto-increment sequence. The following table creation uses auto-increment
```Plain
CREATE TABLE tablename (
    id bigint identity
);
```
## Syntax
```SQL
IDENTITY[(seed)]
```
* seed: The value to be loaded into the first row of the table. If not specified, the default starting value is 0

## Behavior Description

* It cannot be guaranteed that the values in the sequence are continuous (gapless), nor can it be guaranteed that the sequence values are allocated in a specific order. This is because other concurrent inserts may occur in the table. These limitations are part of the design to improve performance, as they are acceptable in many common scenarios.

##  Example
```SQL
-- Create a table with two fields: id and col.
CREATE TABLE identity_test
(
    id bigint identity (1),
    col string
);

-- In the insert statement, insert data into the col field.
INSERT INTO identity_test (col)
VALUES ('1'),('2'),('3'),('4'),('5');
-- Query data
SELECT * FROM identity_test;
+----+-----+
| id | col |
+----+-----+
| 1  | 1   |
| 2  | 2   |
| 3  | 3   |
| 4  | 4   |
| 5  | 5   |
+----+-----+
-- Insert another piece of data, cannot guarantee the continuity of auto-increment.
INSERT INTO identity_test (col)
VALUES ('6');
+----+-----+
| id | col |
+----+-----+
| 11 | 6   |
| 1  | 1   |
| 2  | 2   |
| 3  | 3   |
| 4  | 4   |
| 5  | 5   |
+----+-----+
-- Check if there is an auto-increment column
SHOW CREATE TABLE identity_test;
```
# Limitations and Constraints

* Currently does not support writing through the Ingest Service streaming interface, only supports identity column writing at the SQL syntax level
* Does not support specifying step size, the default step size is 1
* Does not support adding auto-increment to existing tables through alter
* Does not support setting auto-increment for external tables, dynamic tables, and materialized views

^