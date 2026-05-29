# ALTER SCHEMA (External Schema)

## Overview

The `ALTER SCHEMA` statement is used to modify the properties of an existing schema, including renaming, modifying comments, and setting property key-value pairs. For external schemas, you can also update connection configurations by modifying properties.

## Syntax

```Plain
-- Rename
ALTER SCHEMA schema_name RENAME TO new_name;

-- Modify comment
ALTER SCHEMA schema_name SET COMMENT 'new_comment';

-- Set properties
ALTER SCHEMA schema_name SET PROPERTIES ( key = 'value' [, ...] );
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `schema_name` | Yes | Name of the schema to modify |
| `new_name` | For RENAME only | New schema name, must be unique within the same workspace |
| `COMMENT 'new_comment'` | No | New comment text, replaces the existing comment |
| `PROPERTIES (key = 'value')` | No | Set custom schema properties as key-value pairs |

## Examples

### Example 1: Rename a Schema

```SQL
ALTER SCHEMA old_schema_name RENAME TO new_schema_name;
```

### Example 2: Modify Schema Comment

```SQL
ALTER SCHEMA doc_test SET COMMENT 'Test schema for documentation verification';
```

Verify after execution using `DESC SCHEMA`:

```SQL
DESC SCHEMA doc_test;
```

Sample output:

```Plain
+--------------------+--------------------------------------+
| info_name          | info_value                           |
+--------------------+--------------------------------------+
| name               | doc_test                             |
| creator            | qiliang                              |
| created_time       | 2026-05-19 20:16:36.263              |
| last_modified_time | 2026-05-19 22:53:21.766              |
| comment            | Test schema for documentation verification, can be cleaned up at any time |
| type               | managed                              |
+--------------------+--------------------------------------+
```

### Example 3: Set Schema Properties

```SQL
ALTER SCHEMA doc_test SET PROPERTIES ('env' = 'prod', 'owner' = 'data-team');
```

### Example 4: Modify Connection Properties of an External Schema

After creating an external schema, you can update certain configurations by modifying `PROPERTIES`:

```SQL
ALTER SCHEMA my_external_schema SET PROPERTIES ('description' = 'Maps the Hive default database');
```

## Notes

- External schemas do not support the `REFRESH` operation. Metadata changes in Hive Metastore (such as newly added tables) are automatically synchronized at query time without manual refresh.
- `SET PROPERTIES` is an incremental update; existing properties are not cleared, and only the specified keys are overwritten.
- After renaming a schema, table names, views, and other objects referencing the schema are not automatically updated; dependencies must be checked manually.

## Permission Requirements

The user executing `ALTER SCHEMA` must have ALTER permission on the corresponding schema.
