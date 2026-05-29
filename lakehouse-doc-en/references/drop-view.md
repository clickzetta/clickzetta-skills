# Drop View (DROP VIEW)

## Description

The `DROP VIEW` command is used to drop a view from the current schema or a specified schema.

Views do not store data themselves; they only store query definitions, so dropping a view does not affect the data in the underlying tables. **Note: Dropped views cannot be restored via `UNDROP`**. To recover, you must re-execute the `CREATE VIEW` statement.

## Syntax

```Plain
DROP VIEW [ IF EXISTS ] [schema_name.]<view_name>
```

## Parameter Description

| Parameter | Required | Description |
|---|---|---|
| `IF EXISTS` | No | If the specified view does not exist, no error is raised; the operation is silently skipped |
| `schema_name` | No | The name of the schema. If not specified, the current schema is used by default |
| `view_name` | Yes | The name of the view to drop |

## Return Value

`DROP VIEW` returns no result set on success. If the view does not exist and `IF EXISTS` is not used, it returns an error:

```
CZLH-42P01: NotFound: Object not found - Type[TABLE], ...
```

## Examples

### Example 1: Drop a view in the current schema

```SQL
DROP VIEW myview;
```

### Example 2: Drop a view in a specified schema

```SQL
DROP VIEW my_schema.myview;
```

### Example 3: Safe drop (no error if the view does not exist)

```SQL
DROP VIEW IF EXISTS my_schema.myview;
```

## Notes

- **Views Cannot Be Recovered**: Unlike tables (`UNDROP TABLE`) or dynamic tables, views cannot be restored after being dropped via the `UNDROP` command. Before dropping, confirm that you have saved the view's creation statement, which can be obtained using `SHOW CREATE TABLE <view_name>`.

- **Only the Definition Is Removed**: Views do not store data, so dropping a view does not affect any data in the underlying tables.

- **Dependency Impact**: If other views or queries depend on the dropped view, those dependent objects will error when queried. Please check dependencies in advance.

## Related Commands

- [CREATE VIEW](create-view.md): Create a view
- [SHOW CREATE TABLE](show-create-external-table.md): View the creation statement of a view
- [SHOW TABLES WHERE is_view=true](show-views.md): List all views
