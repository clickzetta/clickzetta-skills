# CREATE SCHEMA

## Overview

The `CREATE SCHEMA` statement creates a new schema within the current workspace. A schema is a logical namespace for database objects (tables, views, functions, etc.), used to group and manage data.

## Syntax

```Plain
CREATE SCHEMA [ IF NOT EXISTS ] schema_name [ COMMENT 'comment' ];
```

## Parameters

| Parameter | Required | Description |
|------|----------|------|
| `schema_name` | Yes | Name of the new schema, must be unique within the same workspace |
| `IF NOT EXISTS` | No | If the schema already exists, skip without error |
| `COMMENT 'comment'` | No | Add a descriptive comment for the schema |

## Examples

### Example 1: Create a basic schema

```SQL
CREATE SCHEMA sales_data;
```

### Example 2: Create a schema with a comment

```SQL
CREATE SCHEMA customer_data COMMENT 'Customer-related data';
```

### Example 3: Use IF NOT EXISTS to avoid duplicate creation errors

```SQL
CREATE SCHEMA IF NOT EXISTS doc_test_qiliang COMMENT 'Schema for documentation testing';
```

After execution, verify the result using `SHOW SCHEMAS`:

```SQL
SHOW SCHEMAS;
```

Sample output (partial):

```Plain
+------------------+
| schema_name      |
+------------------+
| doc_test         |
| doc_test_qiliang |
| public           |
+------------------+
```

### Example 4: View schema details

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
| comment            | Test schema for documentation, can be cleaned up anytime |
| type               | managed                              |
+--------------------+--------------------------------------+
```

## Notes

- Schema names must be unique within the same workspace. Duplicate creation will cause an error, so using `IF NOT EXISTS` is recommended.
- Schema names support letters, digits, and underscores, are case-insensitive, and lowercase letters are recommended.
- After creating a schema, you can use `ALTER SCHEMA` to modify its comment or properties, and `DROP SCHEMA` to delete it.

## Required Privileges

The user executing `CREATE SCHEMA` must have the privilege to create a schema in the current workspace.
