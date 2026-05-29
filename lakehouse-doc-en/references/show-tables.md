## Description

Lists all tables, views, materialized views, external tables, and dynamic tables under the specified Schema.

## Syntax

```Plain
SHOW TABLES [IN schema_name] [LIKE 'pattern' | WHERE expr] [LIMIT num]
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `IN schema_name` | No | Specifies the Schema to query. If not specified, the current Schema is used |
| `LIKE 'pattern'` | No | Filters by table name, supports `%` (any string) and `_` (single character), case-insensitive. Cannot be used together with `WHERE` |
| `WHERE expr` | No | Filters by return fields; supported fields: `table_name`, `is_view`, `is_materialized_view`, `is_external`, `is_dynamic` |
| `LIMIT num` | No | Limits the number of rows returned |

## Return Field Description

| Field | Description |
|-------|-------------|
| `schema_name` | Schema name |
| `table_name` | Table name |
| `is_view` | Whether it is a view |
| `is_materialized_view` | Whether it is a materialized view |
| `is_external` | Whether it is an external table |
| `is_dynamic` | Whether it is a dynamic table |

## Usage Examples

1. Query all tables under the `doc_test` Schema:

   ```SQL
   SHOW TABLES IN doc_test;
   +-------------+-------------+---------+----------------------+-------------+------------+
   | schema_name | table_name  | is_view | is_materialized_view | is_external | is_dynamic |
   +-------------+-------------+---------+----------------------+-------------+------------+
   | doc_test    | departments | false   | false                | false       | false      |
   | doc_test    | employees   | false   | false                | false       | false      |
   | doc_test    | logs        | false   | false                | false       | false      |
   | doc_test    | orders      | false   | false                | false       | false      |
   | doc_test    | products    | false   | false                | false       | false      |
   +-------------+-------------+---------+----------------------+-------------+------------+
   ```

2. Show only regular tables (exclude views, materialized views, external tables, and dynamic tables):

   ```SQL
   SHOW TABLES IN doc_test WHERE is_view=false AND is_materialized_view=false AND is_external=false AND is_dynamic=false;
   ```

3. Fuzzy filter by name:

   ```SQL
   SHOW TABLES IN doc_test LIKE '%emp%';
   ```

4. View all views under the current Schema:

   ```SQL
   SHOW TABLES WHERE is_view=true;
   ```

5. Exact filter by name (WHERE mode, strings must be quoted):

   ```SQL
   SHOW TABLES IN doc_test WHERE table_name='employees';
   ```

## Notes

- `LIKE` and `WHERE` cannot be used together.
- String values in `WHERE` must be quoted, e.g., `WHERE table_name='employees'` (do not write `WHERE table_name=employees`).
- The result includes all types of table objects, differentiated by the `is_*` fields.
