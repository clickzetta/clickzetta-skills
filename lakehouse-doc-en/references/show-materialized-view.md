# Show Materialized Views (SHOW MATERIALIZED VIEWS)

## Description

The `SHOW TABLES` command with the `WHERE is_materialized_view=true` condition lists all materialized views under a specified schema.

For more details, see [Materialized Views](MATERIALIZEDVIEW.md).

## Syntax

```Plain
SHOW TABLES [ IN schema_name ] [ LIKE 'pattern' | WHERE expr ] [ LIMIT num ]
```

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `IN schema_name` | No | Specifies the schema name to query. If omitted, uses the current schema |
| `LIKE 'pattern'` | No | Case-insensitive fuzzy filter on object name. Supports `%` (matches any number of characters) and `_` (matches a single character). Cannot be used together with `WHERE` |
| `WHERE expr` | No | Filters by return column values. Cannot be used together with `LIKE` |
| `LIMIT num` | No | Limits the number of returned records |

## Return Columns

| Column | Type | Description |
|---|---|---|
| `schema_name` | string | Name of the schema containing the materialized view |
| `table_name` | string | Name of the materialized view |
| `is_view` | boolean | Whether it is a regular view; `false` for materialized views |
| `is_materialized_view` | boolean | Whether it is a materialized view; `true` for materialized views |
| `is_external` | boolean | Whether it is an external table; `false` for materialized views |
| `is_dynamic` | boolean | Whether it is a dynamic table; `false` for materialized views |

## Examples

### Example 1: View all materialized views in the default schema

```SQL
SHOW TABLES WHERE is_materialized_view = true;
```

### Example 2: View all materialized views in a specified schema

```SQL
SHOW TABLES IN doc_test WHERE is_materialized_view = true;
```

Sample result:

```
+-------------+---------------+---------+----------------------+-------------+------------+
| schema_name | table_name    | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+---------------+---------+----------------------+-------------+------------+
| doc_test    | mv_test_sales | false   | true                 | false       | false      |
+-------------+---------------+---------+----------------------+-------------+------------+
```

### Example 3: Fuzzy filter materialized views by name

```SQL
SHOW TABLES IN doc_test LIKE '%sales%';
```

### Example 4: Filter by both name and type in the WHERE clause

```SQL
SHOW TABLES IN doc_test WHERE table_name LIKE '%test%' AND is_materialized_view = true;
```

## Notes

- `LIKE` and `WHERE` cannot be used together. To filter by both name and type, put the name condition inside the `WHERE` clause: `WHERE table_name LIKE '%pattern%' AND is_materialized_view=true`.
- `SHOW TABLES` returns all types of table objects. Use `WHERE is_materialized_view=true` to show only materialized views.

## Related Commands

- [CREATE MATERIALIZED VIEW](create-materialized-view.md): Create a materialized view
- [DROP MATERIALIZED VIEW](drop-materialized-view.md): Drop a materialized view
- [REFRESH MATERIALIZED VIEW](REFRESH.md): Refresh a materialized view
- [DESC MATERIALIZED VIEW](desc-materialized-view.md): View the structure of a materialized view
