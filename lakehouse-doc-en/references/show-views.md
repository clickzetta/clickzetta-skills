# View All Views (SHOW VIEWS)

## Description

By using the `SHOW TABLES` command with the `WHERE is_view=true` condition, you can list all views under a specified schema.

## Syntax

```Plain
SHOW TABLES [ IN schema_name ] [ LIKE 'pattern' | WHERE expr ] [ LIMIT num ]
```

## Parameter Description

| Parameter | Required | Description |
|---|---|---|
| `IN schema_name` | No | Specifies the schema to query. If not specified, the current schema is used by default. |
| `LIKE 'pattern'` | No | Performs case-insensitive fuzzy filtering by object name. Supports `%` (matches any number of characters) and `_` (matches a single character). Cannot be used together with `WHERE`. |
| `WHERE expr` | No | Filters by the values of returned columns. Cannot be used together with `LIKE`. |
| `LIMIT num` | No | Limits the number of returned records. |

## Return Column Description

| Column Name | Type | Description |
|---|---|---|
| `schema_name` | string | The name of the schema where the view resides. |
| `table_name` | string | The name of the view. |
| `is_view` | boolean | Whether the object is a regular view. Returns `true` for views. |
| `is_materialized_view` | boolean | Whether the object is a materialized view. Returns `false` for regular views. |
| `is_external` | boolean | Whether the object is an external table. Returns `false` for views. |
| `is_dynamic` | boolean | Whether the object is a dynamic table. Returns `false` for views. |

## Examples

### Example 1: View All Views in the Current Schema

```SQL
SHOW TABLES WHERE is_view=true;
```

### Example 2: View All Views in a Specified Schema

```SQL
SHOW TABLES IN doc_test WHERE is_view=true;
```

Example result:

```
+-------------+------------------+---------+----------------------+-----------+------------+
| schema_name | table_name       | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+------------------+---------+----------------------+-----------+------------+
| doc_test    | v_test_employees | true    | false                | false     | false      |
+-------------+------------------+---------+----------------------+-----------+------------+
```

### Example 3: Fuzzy Filter Views by Name

```SQL
SHOW TABLES IN doc_test LIKE '%test%';
```

### Example 4: Filter by Both Name and Type in the WHERE Clause

```SQL
SHOW TABLES IN doc_test WHERE table_name LIKE '%test%' AND is_view=true;
```

## Notes

- `LIKE` and `WHERE` cannot be used together. To filter by both name and type, include the name condition in the `WHERE` clause: `WHERE table_name LIKE '%pattern%' AND is_view=true`.
- `SHOW TABLES` returns all types of table objects (regular tables, views, materialized views, external tables, dynamic tables). Use `WHERE is_view=true` to display only regular views.

## Related Commands

- [CREATE VIEW](create-view.md): Creates a view.
- [DROP VIEW](drop-view.md): Drops a view.
- [SHOW CREATE TABLE](show-create-external-table.md): Views the DDL statement of a view.
