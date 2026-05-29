# Drop Dynamic Table (DROP DYNAMIC TABLE)

## Description

The `DROP DYNAMIC TABLE` command is used to delete an existing Dynamic Table.

A dynamic table is a data object that automatically refreshes incrementally based on a query definition, refreshing its results periodically based on changes in the source tables. When a dynamic table is no longer needed, you can use this command to delete it.

## Syntax

```Plain
DROP DYNAMIC TABLE [ IF EXISTS ] [schema_name.]<dt_name>
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `IF EXISTS` | No | If the specified dynamic table does not exist, the system will silently skip without raising an error |
| `schema_name` | No | The name of the schema. If not specified, the current schema is used by default |
| `dt_name` | Yes | The name of the dynamic table to delete |

## Usage Examples

### Example 1: Drop a dynamic table

```SQL
DROP DYNAMIC TABLE sales_summary;
```

### Example 2: Safe deletion (no error if the table does not exist)

```SQL
DROP DYNAMIC TABLE IF EXISTS sales_summary;
```

### Example 3: Drop a dynamic table in a specific schema

```SQL
DROP DYNAMIC TABLE IF EXISTS analytics.daily_report;
```

### Example 4: Recover after dropping

```SQL
-- Drop the dynamic table
DROP DYNAMIC TABLE analytics.daily_report;

-- Recover the dynamic table (note: use UNDROP TABLE, not UNDROP DYNAMIC TABLE)
UNDROP TABLE analytics.daily_report;
```

## Notes

- **Use the correct DROP command**: You must use `DROP DYNAMIC TABLE` to delete a dynamic table. Using `DROP TABLE` will raise an error:
  ```
  The operation 'DROP TABLE' requires a 'TABLE'.
  But 'xxx' is a DYNAMIC TABLE, please use 'DROP DYNAMIC TABLE' instead.
  ```

- **Data is recoverable**: Deleting a dynamic table is not irreversible. Within the `data_retention_days` retention period (default 1 day, configurable up to 90 days), it can be recovered using `UNDROP TABLE`. After recovery, the dynamic table retains its dynamic table properties (incremental refresh configuration, etc.).

- **Name conflict handling**: If a new table with the same name is created after deletion, rename or drop the new table first before recovering the old one:
  ```SQL
  ALTER TABLE daily_report RENAME TO daily_report_backup;
  UNDROP TABLE daily_report;
  ```

- **Downstream impact**: Before dropping a dynamic table, confirm whether other dynamic tables or queries depend on it. If the deleted dynamic table serves as a source for other dynamic tables, downstream refreshes will fail.

## Related Commands

- [CREATE DYNAMIC TABLE](create-dynamic-table.md): Create a dynamic table
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md): Modify a dynamic table
- [UNDROP TABLE](UNDROP-TABLE.md): Recover a dropped table/dynamic table/materialized view
- [SHOW DYNAMIC TABLE REFRESH HISTORY](refresh-history.md): View dynamic table refresh history
