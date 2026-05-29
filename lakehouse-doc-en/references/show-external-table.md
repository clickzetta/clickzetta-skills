# Show External Tables (SHOW EXTERNAL TABLES)

## Description

The `SHOW TABLES` command with the `WHERE is_external=true` condition lists all external tables under a specified schema.

## Syntax

```Plain
SHOW TABLES [ IN schema_name ] [ WHERE is_external=true ] [ LIMIT num ]
```

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `IN schema_name` | No | Specifies the schema name to query. If omitted, uses the current schema |
| `WHERE is_external=true` | No | Filter condition that restricts results to external tables only |
| `LIMIT num` | No | Limits the number of returned records |

## Return Columns

| Column | Type | Description |
|---|---|---|
| `schema_name` | string | Name of the schema containing the external table |
| `table_name` | string | Name of the external table |
| `is_view` | boolean | Whether it is a regular view; `false` for external tables |
| `is_materialized_view` | boolean | Whether it is a materialized view; `false` for external tables |
| `is_external` | boolean | Whether it is an external table; `true` for external tables |
| `is_dynamic` | boolean | Whether it is a dynamic table; `false` for external tables |

## Examples

### Example 1: List all external tables in the current schema

```SQL
SHOW TABLES WHERE is_external=true;
```

### Example 2: List all external tables in a specified schema

```SQL
SHOW TABLES IN doc_test WHERE is_external=true;
```

Sample result:

```
+-------------+-----------------+---------+----------------------+-------------+------------+
| schema_name | table_name      | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+-----------------+---------+----------------------+-------------+------------+
| doc_test    | ext_orders_v2   | false   | false                | true        | false      |
+-------------+-----------------+---------+----------------------+-------------+------------+
```

### Example 3: Limit the number of returned records

```SQL
SHOW TABLES IN doc_test WHERE is_external=true LIMIT 10;
```

## Notes

- `SHOW TABLES` returns all types of table objects. Use `WHERE is_external=true` to show only external tables.
- External table data is stored in external storage (such as OSS, S3). Dropping an external table does not delete the underlying data files.
- To view the full DDL of an external table (including `LOCATION` and `CONNECTION` information), use `SHOW CREATE TABLE <table_name>`.

## Related Commands

- [CREATE EXTERNAL TABLE](create-external-table.md): Create an external table
- [DROP EXTERNAL TABLE](drop-external-table.md): Drop an external table
- [SHOW CREATE TABLE](show-create-external-table.md): View the DDL of an external table
