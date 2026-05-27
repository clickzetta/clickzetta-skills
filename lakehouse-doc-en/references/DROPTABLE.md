## Features

The `DROP TABLE` command is used to delete a table in the database. Please note that after performing this operation, the table and data will be deleted. If you want to recover it, please use the [UNDROP](<UNDROP-TABLE.md>) command, and ensure that the deleted object is within the [TIME TRAVEL](<timetravel-summary.md>) retention period, otherwise it cannot be recovered.

## Syntax
```SQL
DROP TABLE [ IF EXISTS ] [schema_name.]<table_name>
```
**Parameter Description**

- `IF EXISTS`: Optional, if the specified table does not exist, the system will not report an error.
- `schema_name`: Optional, specifies the name of the schema. If not specified, the current user's schema is used by default.
- `table_name`: The name of the table to be deleted.

## Example

1. Delete the table named `my_table` under the current schema:
```SQL
DROP TABLE my_table;
```
```markdown
2. Delete the table named `my_table` without reporting an error if the table does not exist:
```
```SQL
DROP TABLE IF EXISTS my_table;
```
3. Delete the `my_table` table under the `my_schema` schema:
```SQL
DROP TABLE my_schema.my_table;
```
```markdown
4. Delete the `my_table` table under the schema named `my_schema`, do not report an error if the table does not exist:
```
```SQL
DROP TABLE IF EXISTS my_schema.my_table;
```
## Precautions

- Please ensure that you have backed up the data in the table before executing the `DROP TABLE` command to prevent data loss.
- Before deleting the table, make sure that the table is no longer referenced by other database objects (such as views, TABLE STREAM, etc.), otherwise it may cause errors.