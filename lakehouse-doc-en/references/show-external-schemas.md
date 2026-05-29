## Overview

The `SHOW SCHEMAS EXTENDED` statement is used to view the list of schemas under the current workspace, with the `EXTENDED` keyword showing each schema's type (managed or external). The `WHERE` clause can be used to filter for external schemas.

## Syntax

```Plain
SHOW SCHEMAS [ EXTENDED [ WHERE expr ] ];
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `EXTENDED` | No | Adds a `type` column to the result, showing the schema type |
| `WHERE expr` | No | Filters by returned columns; only effective when `EXTENDED` is used |

## Return Columns

### Without EXTENDED

| Column Name | Type | Description |
|-------------|------|-------------|
| `schema_name` | STRING | Schema name |

### With EXTENDED

| Column Name | Type | Description |
|-------------|------|-------------|
| `schema_name` | STRING | Schema name |
| `type` | STRING | Schema type: `managed`, `external`, or `shared` |

## Examples

### Example 1: View All Schemas

```SQL
SHOW SCHEMAS;
```

Sample output:

```Plain
+------------------+
| schema_name      |
+------------------+
| doc_test         |
| information_schema |
| public           |
+------------------+
```

### Example 2: View All Schemas and Their Types

```SQL
SHOW SCHEMAS EXTENDED;
```

Sample output:

```Plain
+--------------------+---------+
| schema_name        | type    |
+--------------------+---------+
| doc_test           | managed |
| information_schema | shared  |
| public             | managed |
+--------------------+---------+
```

### Example 3: Filter External Schemas

```SQL
SHOW SCHEMAS EXTENDED WHERE type = 'external';
```

Sample output (when external schemas exist):

```Plain
+--------------------+----------+
| schema_name        | type     |
+--------------------+----------+
| my_external_schema | external |
+--------------------+----------+
```

### Example 4: Filter Managed Schemas

```SQL
SHOW SCHEMAS EXTENDED WHERE type = 'managed';
```

Sample output (partial):

```Plain
+------------------+---------+
| schema_name      | type    |
+------------------+---------+
| doc_test         | managed |
| public           | managed |
+------------------+---------+
```

## Notes

- The `WHERE` clause can only reference columns returned in `EXTENDED` mode (`schema_name`, `type`).
- Possible values for `type` are `managed` (managed schema), `external` (external schema), and `shared` (shared schema introduced via SHARE).
- If no external schemas exist under the current workspace, `WHERE type='external'` will return an empty result set.
