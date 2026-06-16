# Alter Table (ALTER TABLE)

`ALTER TABLE` is used to modify the structure and properties of a table, including renaming tables/columns, adding/dropping/modifying columns, and setting comments and properties.

## 1. Rename Table

Rename a table to a new name (the new name only includes the table name, without a schema prefix; the table remains in its original schema):

```Plain
ALTER TABLE <table_name> RENAME TO <new_name>;
```

**Example**: Rename `doc_test.logs` to `system_logs`, then revert:

```SQL
ALTER TABLE doc_test.logs RENAME TO system_logs;
DESC TABLE doc_test.system_logs;
```

```
column_name  | data_type     | comment
-------------|---------------|--------
log_id       | bigint        |
level        | string        |
message      | string        |
created_at   | timestamp_ltz |
```

## 2. Add Column

```Plain
-- Add a single column
ALTER TABLE <table_name> ADD COLUMN [IF NOT EXISTS] <column_name> <data_type>
    [DEFAULT '<value>']
    [COMMENT '<comment>']
    [FIRST | AFTER <existing_column>];

-- Add multiple columns at once
ALTER TABLE <table_name> ADD COLUMNS (<col1> <type1>, <col2> <type2>, ...);
```

- `IF NOT EXISTS`: silently skips if the column already exists without raising an error; suitable for idempotent operations
- `DEFAULT`: default value for the new column; only applies to newly inserted rows — **existing rows have NULL for this column**
- `FIRST` / `AFTER <col>`: controls the position of the new column in the table; appended to the end if not specified
- `ADD COLUMNS` (plural): adds multiple columns at once; does not support IF NOT EXISTS or position control

**Example**: Add a `phone` column to `doc_test.employees`:

```SQL
-- Add a single column with a comment
ALTER TABLE doc_test.employees ADD COLUMN phone STRING COMMENT 'Contact phone';

-- Idempotent add (no error if already exists)
ALTER TABLE doc_test.employees ADD COLUMN IF NOT EXISTS phone STRING;

-- Add at a specific position
ALTER TABLE doc_test.employees ADD COLUMN emp_code STRING AFTER id;

-- Add multiple columns at once
ALTER TABLE doc_test.employees ADD COLUMNS (region STRING, level INT);

-- Add a column with a default value (note: existing rows are NULL, not backfilled)
ALTER TABLE doc_test.employees ADD COLUMN status STRING DEFAULT 'active';
SELECT id, name, status FROM doc_test.employees LIMIT 2;
```

```
+----+-------+--------+
| id | name  | status |
+----+-------+--------+
| 1  | Alice | NULL   |
| 2  | Bob   | NULL   |
+----+-------+--------+
```

New columns are appended at the end of the table by default. The column value for existing rows is NULL (when no DEFAULT is specified).

> ⚠️ **Note**: `DEFAULT` values are not backfilled to historical data; existing rows have NULL for the new column. To backfill, run `UPDATE ... SET status = 'active' WHERE status IS NULL`.

## 3. Drop Column

```Plain
-- Drop a single column
ALTER TABLE <table_name> DROP COLUMN [IF EXISTS] <column_name>;

-- Drop multiple columns at once
ALTER TABLE <table_name> DROP COLUMNS (<col1>, <col2>, ...);
```

- `IF EXISTS`: silently skips if the column does not exist without raising an error
- `DROP COLUMNS` (plural): drops multiple columns at once

> ⚠️ **Note**: After dropping a column, the historical data of that column cannot be recovered. Confirm that the column data is no longer needed before execution.

**Example**: Drop the `phone` column:

```SQL
-- Drop a single column
ALTER TABLE doc_test.employees DROP COLUMN phone;

-- Idempotent drop (no error if not exists)
ALTER TABLE doc_test.employees DROP COLUMN IF EXISTS phone;

-- Drop multiple columns at once
ALTER TABLE doc_test.employees DROP COLUMNS (region, level);
```

## 4. Rename Column

```Plain
ALTER TABLE <table_name> RENAME COLUMN <old_name> TO <new_name>;
```

**Example**:

```SQL
ALTER TABLE doc_test.employees RENAME COLUMN dept TO department;
DESC TABLE doc_test.employees;
```

## 5. Modify Column Type

Change the data type of a column:

```Plain
ALTER TABLE <table_name> ALTER COLUMN <column_name> TYPE <new_data_type>;
```

Type changes must be compatible; incompatible conversions will raise an error. Common compatible conversions:

| Source Type | Can Convert To | Notes |
|---|---|---|
| `DECIMAL(10,2)` | `DECIMAL(15,2)` | Expand precision, allowed |
| `INT` | `BIGINT` | Expand range, allowed |
| `DECIMAL(15,2)` | `DECIMAL(10,2)` | Reduce precision, error |
| `DECIMAL` | `STRING` | Incompatible, error |
| `STRING` | `VARCHAR(100)` | Incompatible, error |

**Example**: Expand the precision of `doc_test.employees.salary` from `DECIMAL(10,2)` to `DECIMAL(15,2)`:

```SQL
-- Expand DECIMAL precision
ALTER TABLE doc_test.employees ALTER COLUMN salary TYPE DECIMAL(15,2);

-- Expand INT to BIGINT
ALTER TABLE doc_test.employees ALTER COLUMN id TYPE BIGINT;

-- Incompatible type (error example)
ALTER TABLE doc_test.employees ALTER COLUMN salary TYPE STRING;
-- Error: Cannot change data type from decimal(15,2) to string, types are incompatible or conversion may cause data loss
```

## 6. Modify Column Comment

Add or modify the comment for a column:

```Plain
ALTER TABLE <table_name> ALTER COLUMN <column_name> COMMENT '<comment_text>';
```

**Example**: Add a comment to the `doc_test.employees.name` column:

```SQL
ALTER TABLE doc_test.employees ALTER COLUMN name COMMENT 'Employee Name';
ALTER TABLE doc_test.employees ALTER COLUMN id COMMENT 'Employee ID';
DESC TABLE doc_test.employees;
```

```
column_name  | data_type | comment
-------------|-----------|--------
id           | bigint    | Employee ID
name         | string    | Employee Name
...
```

## 7. Add Generated Column

A generated column's value is automatically computed from an expression; no manual write is needed.

```Plain
ALTER TABLE <table_name> ADD COLUMN <column_name> <data_type>
    GENERATED ALWAYS AS (<expression>);
```

**Example**:

```SQL
ALTER TABLE doc_test.employees ADD COLUMN name_upper STRING GENERATED ALWAYS AS (UPPER(name));

SELECT id, name, name_upper FROM doc_test.employees LIMIT 2;
```

```
+----+-------+------------+
| id | name  | name_upper |
+----+-------+------------+
| 1  | Alice | ALICE      |
| 2  | Bob   | BOB        |
+----+-------+------------+
```

See [Generated Columns Guide](generated_columns_guide.md) for detailed usage.

## 8. Partition Operations

For tables created with `PARTITIONED BY`, dropping partitions is supported:

```Plain
ALTER TABLE <table_name> DROP [IF EXISTS] PARTITION (<col>='<val>', ...);
```

- Partitions can only be created automatically by writing data to the table; `ADD PARTITION` for manual creation is not supported
- `IF EXISTS`: silently skips if the partition does not exist without raising an error

**Example**:

```SQL
CREATE TABLE IF NOT EXISTS events (
    id INT,
    name STRING
) PARTITIONED BY (dt STRING);

INSERT INTO events VALUES (1, 'login', '2024-01'), (2, 'logout', '2024-02');
SHOW PARTITIONS events;
```

```
+----------+
| dt       |
+----------+
| 2024-01  |
| 2024-02  |
+----------+
```

```SQL
-- Drop a specific partition (partition data is also deleted)
ALTER TABLE events DROP PARTITION (dt='2024-01');

-- Idempotent drop (no error if not exists)
ALTER TABLE events DROP IF EXISTS PARTITION (dt='2024-01');

SHOW PARTITIONS events;
```

```
+----------+
| dt       |
+----------+
| 2024-02  |
+----------+
```

> ⚠️ **Note**: Dropping a partition also deletes all data under that partition and cannot be recovered.

## 9. Modify Table Comment

Add or modify the comment for a table:

```Plain
ALTER TABLE <table_name> SET COMMENT '<comment_text>';
```

To clear a comment: `SET COMMENT ''` (set to empty string).

**Example**: Set a comment for `doc_test.products`:

```SQL
ALTER TABLE doc_test.products SET COMMENT 'Product information table';
SHOW CREATE TABLE doc_test.products;
```

```
CREATE TABLE quick_start.doc_test.products(
  `product_id` int,
  `name` string,
  `price` decimal(10,2),
  `stock` int,
  `category` string)
USING PARQUET
COMMENT 'Product information table';
```

```SQL
-- Clear comment: set to empty string
ALTER TABLE doc_test.products SET COMMENT '';
```

## 10. Modify Table Properties

Set or modify table properties such as data lifecycle (TTL) and Time Travel retention period:

```Plain
-- Set properties
ALTER TABLE <table_name> SET PROPERTIES ('<key>'='<value>');

-- Remove properties
ALTER TABLE <table_name> UNSET PROPERTIES ('<key>');
```

`SET TBLPROPERTIES` and `SET PROPERTIES` are equivalent; both are supported.

**Supported Built-in Properties**:

| Property | Description | Value Range |
|---|---|---|
| `data_lifecycle` | Data lifecycle (TTL). Data not updated within the period is automatically reclaimed | Positive integer greater than 0; -1 means disabled |
| `data_retention_days` | Time Travel retention period, which determines how far back historical data can be accessed | 0-90 days |

**Example**:

```sql
-- Set data lifecycle to 30 days
ALTER TABLE doc_test.logs SET PROPERTIES ('data_lifecycle'='30');

-- Set Time Travel retention period to 7 days (note: longer retention increases storage costs)
ALTER TABLE doc_test.logs SET PROPERTIES ('data_retention_days'='7');

-- Remove a property
ALTER TABLE doc_test.logs UNSET PROPERTIES ('data_lifecycle');

-- View properties
SHOW PROPERTIES IN TABLE doc_test.logs;
```

```
info_name            | info_value
---------------------|----------
data_retention_days  | 7
```

## Notes

- **Dynamic Tables Do Not Support ALTER for SQL Definitions**: Dynamic Tables do not support modifying query definitions via `ALTER TABLE`. To modify a dynamic table's SQL logic, refresh interval, or compute cluster, use `CREATE OR REPLACE DYNAMIC TABLE`.

- **Column Operation Limitations**: When adding a column, the new column defaults to NULL for existing data (DEFAULT values are not backfilled to historical rows). Column data cannot be recovered after dropping.

- **Type Conversion Limitations**: `STRING` and `VARCHAR` cannot be converted to each other; type reduction (e.g., `DECIMAL(15,2)` → `DECIMAL(10,2)`) will raise an error.

- **DESC TABLE to View Structure**: Use `DESC TABLE <table_name>` to view the full structure of a table, including column names, data types, and comments.

## Related Documents

- [CREATE TABLE](create-table-ddl.md)
- [DROP TABLE](drop-table.md)
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md)
- [SQL CREATE TABLE Guide](sql_create_table_guide.md): Complete usage guide for table creation options, column types, partitioning, and sort columns
- [Generated Columns Guide](generated_columns_guide.md): Defining and modifying virtual and stored columns
