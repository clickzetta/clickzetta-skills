# Alter Table (ALTER TABLE)

The `ALTER TABLE` command is used to modify the structure and properties of a table, including renaming tables, adding/dropping/modifying columns, and modifying comments and properties.

## 1. Rename Table

Rename a table to a new name (the new name only includes the table name, without a schema prefix; the table remains in its original schema):

```Plain
ALTER TABLE <schema>.<old_name> RENAME TO <new_name>;
```

**Example**: Rename `doc_test.logs` to `system_logs`, then revert:

```SQL
-- Rename
ALTER TABLE doc_test.logs RENAME TO system_logs;

-- Verify
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

```SQL
-- Revert to original name
ALTER TABLE doc_test.system_logs RENAME TO logs;
```

## 2. Add Column

Add a new column to a table:

```Plain
ALTER TABLE <table_name> ADD COLUMN <column_name> <data_type>;
```

**Example**: Add a `phone` column to `doc_test.employees`:

```SQL
ALTER TABLE doc_test.employees ADD COLUMN phone STRING;

-- Verify
DESC TABLE doc_test.employees;
```

```
column_name  | data_type      | comment
-------------|----------------|--------
id           | int            |
name         | string         | Employee Name
dept         | string         |
salary       | decimal(15,2)  |
hire_date    | date           |
is_active    | boolean        |
phone        | string         |
```

New columns are appended at the end of the table. The column value for existing rows is NULL (when no DEFAULT is specified).

## 3. Drop Column

Remove a column from a table:

```Plain
ALTER TABLE <table_name> DROP COLUMN <column_name>;
```

> Warning: After dropping a column, the historical data of that column cannot be recovered. Confirm that the column data is no longer needed before execution.

**Example**: Drop the newly added `phone` column:

```SQL
ALTER TABLE doc_test.employees DROP COLUMN phone;

-- Verify
DESC TABLE doc_test.employees;
```

```
column_name  | data_type      | comment
-------------|----------------|--------
id           | int            |
name         | string         | Employee Name
dept         | string         |
salary       | decimal(15,2)  |
hire_date    | date           |
is_active    | boolean        |
```

## 4. Modify Column Type

Change the data type of a column:

```Plain
ALTER TABLE <table_name> ALTER COLUMN <column_name> TYPE <new_data_type>;
```

> Warning: Type changes must be compatible (e.g., `DECIMAL(10,2)` to `DECIMAL(15,2)` can expand precision, but reducing it in reverse will error). Incompatible type conversions (e.g., `DECIMAL` to `DOUBLE`) will also error.

**Example**: Expand the precision of `doc_test.employees.salary` from `DECIMAL(10,2)` to `DECIMAL(15,2)`:

```SQL
ALTER TABLE doc_test.employees ALTER COLUMN salary TYPE DECIMAL(15,2);

-- Verify
DESC TABLE doc_test.employees;
```

```
column_name  | data_type      | comment
-------------|----------------|--------
id           | int            |
name         | string         | Employee Name
dept         | string         |
salary       | decimal(15,2)  |
hire_date    | date           |
is_active    | boolean        |
```

## 5. Modify Table Comment

Add or modify the comment for a table:

```Plain
ALTER TABLE <table_name> SET COMMENT '<comment_text>';
```

**Example**: Set a comment for `doc_test.products`:

```SQL
ALTER TABLE doc_test.products SET COMMENT 'Product information table';

-- Verify (the comment appears in SHOW CREATE TABLE output)
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

## 6. Modify Column Comment

Add or modify the comment for a column:

```Plain
ALTER TABLE <table_name> ALTER COLUMN <column_name> COMMENT '<comment_text>';
```

**Example**: Add a comment to the `doc_test.employees.name` column:

```SQL
ALTER TABLE doc_test.employees ALTER COLUMN name COMMENT 'Employee Name';

-- Verify
DESC TABLE doc_test.employees;
```

```
column_name  | data_type      | comment
-------------|----------------|--------
id           | int            |
name         | string         | Employee Name
dept         | string         |
salary       | decimal(15,2)  |
hire_date    | date           |
is_active    | boolean        |
```

## 7. Modify Table Properties

Set or modify table properties such as data lifecycle (TTL) and Time Travel retention period:

```Plain
ALTER TABLE <table_name> SET PROPERTIES ('key'='value');
```

**Supported Properties**:

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

-- Disable data lifecycle
ALTER TABLE doc_test.logs SET PROPERTIES ('data_lifecycle'='-1');
```

Check the result of modifying `data_retention_days`:

```SQL
SHOW PROPERTIES IN TABLE doc_test.logs;
```

```
info_name            | info_value
---------------------|----------
data_retention_days  | 7
```

## Notes

- **Dynamic Tables Do Not Support ALTER for SQL Definitions**: Dynamic Tables do not support modifying query definitions via `ALTER TABLE`. To modify a dynamic table's SQL logic, refresh interval, or compute cluster, use `CREATE OR REPLACE DYNAMIC TABLE`.

- **Column Operation Limitations**: When adding a column, the new column defaults to NULL for existing data (unless a DEFAULT value is specified). Column data cannot be recovered after dropping.

- **DESC TABLE to View Structure**: Use `DESC TABLE <table_name>` to view the full structure of a table, including column names, data types, and comments. The `DESC TABLE ... EXTENDED` parameter is not supported (regular tables can use `DESC EXTENDED` for additional information).

## Related Documents

- [CREATE TABLE](create-table-ddl.md)
- [DROP TABLE](drop-table.md)
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md)
- [SQL CREATE TABLE Guide](SQL_CREATE_TABLE_GUIDE.md): Complete usage guide for table creation options, column types, partitioning, and sort columns
- [Generated Columns Guide](generated_columns_guide.md): Defining and modifying virtual and stored columns
