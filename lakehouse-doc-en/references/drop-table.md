# Drop Table (DROP TABLE)

## Usage

The `DROP TABLE` command is used to delete a regular table in the Lakehouse. After execution, the table and its data will be removed.

> **Data Recovery**: Singdata Lakehouse provides Time Travel functionality. Within the data retention period (default 1 day, configurable up to 90 days), a deleted table can be restored using the `UNDROP TABLE` command. See [UNDROP TABLE](UNDROP-TABLE.md) for details.

## Syntax

```sql
DROP TABLE [ IF EXISTS ] [schema_name.]<table_name>
```

### Parameter Description

| Parameter | Description |
|---|---|
| `IF EXISTS` | Optional. If the specified table does not exist, no error is raised |
| `schema_name` | Optional. The name of the schema. If not specified, the current schema is used by default |
| `table_name` | The name of the table to drop |

## Examples

### Example 1: Drop a table in the current schema

```sql
DROP TABLE my_table;
```

### Example 2: Safe drop (no error if the table does not exist)

```sql
DROP TABLE IF EXISTS my_table;
```

### Example 3: Drop a table in a specified schema

```sql
DROP TABLE my_schema.my_table;
```

### Example 4: Drop and restore

```sql
-- Drop the table
DROP TABLE my_schema.orders;

-- Restore the table
UNDROP TABLE my_schema.orders;

-- Verify restoration
SELECT COUNT(*) FROM my_schema.orders;
```

## Notes

- **Object Type Matching**: `DROP TABLE` can only drop regular tables. To drop a dynamic table, use `DROP DYNAMIC TABLE`. To drop a materialized view, use `DROP MATERIALIZED VIEW`. Using the wrong command will result in an error.

- **Data Recovery**: After dropping a table, it can be restored via `UNDROP TABLE` within the `data_retention_days` retention period. A table with the same name must not exist at the time of restoration.

- **Dependent Objects**: Before dropping a table, confirm whether other objects depend on it:
  - **Views** referencing the table will become invalid
  - **Dynamic tables** that use the table as a source will fail to refresh
  - **Table Streams** bound to the table will be unable to consume
  - **Downstream ETL tasks** that depend on the table will fail to execute

- **Dropping a Source Table Invalidates Associated Streams**: When `DROP TABLE` removes a source table, all Table Streams based on that table will immediately become invalid and can no longer consume change data. If you need to preserve Stream data, consume all changes in the Stream before dropping the source table.

- **Cascading Deletion**: Use `DROP SCHEMA` to cascade-delete all tables under a schema without dropping them individually.
