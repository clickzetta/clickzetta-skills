# Manage Semantic View

## DROP SEMANTIC VIEW

Deletes the specified semantic view.

**Syntax**:

```sql
DROP SEMANTIC VIEW [ IF EXISTS ] <view_name>;
```

`IF EXISTS` prevents errors when the view does not exist. It is recommended to always include it in scripts.

**Example**:

```sql
DROP SEMANTIC VIEW IF EXISTS doc_test.emp_dept_analysis;
```

## ALTER SEMANTIC VIEW

`ALTER SEMANTIC VIEW` supports three types of operations: `RENAME TO` for renaming, `SET PROPERTIES` for setting properties, and `UNSET PROPERTIES` for removing properties. It still **does not support** dynamically adding/removing dimensions, metrics, or modifying comments via SQL, and **does not support `CREATE OR REPLACE SEMANTIC VIEW`** (which returns `only view/stream/materialized view support replace`). To modify dimension / metric / logical table structure, you must `DROP` and rebuild.

### RENAME TO

**Syntax**:

```sql
ALTER SEMANTIC VIEW <view_name> RENAME TO <new_name>;
```

The new name must not include a schema prefix; after renaming, the view remains in the original schema.

**Example**:

```sql
ALTER SEMANTIC VIEW emp_dept_analysis RENAME TO emp_dept_v2;
```

### SET / UNSET PROPERTIES

Set or remove custom key-value properties on a Semantic View. Properties can be read back via the `properties` row in `DESC EXTENDED` output and are commonly used to store metadata or authoritative definitions alongside the view object itself.

**Syntax**:

```sql
ALTER SEMANTIC VIEW <view_name> SET PROPERTIES ( '<key>' = '<value>' [ , ... ] );
ALTER SEMANTIC VIEW <view_name> UNSET PROPERTIES ( '<key>' [ , ... ] );
```

`SET PROPERTIES` uses merge (upsert) semantics — it updates only the specified keys and does not affect other existing keys. To remove a key, use `UNSET PROPERTIES`. `CREATE SEMANTIC VIEW` does not support a `PROPERTIES` clause; properties can only be set after creation via `ALTER ... SET PROPERTIES`.

**Examples**:

```sql
ALTER SEMANTIC VIEW emp_dept_analysis SET PROPERTIES ('owner' = 'analytics_team', 'spec_version' = '2');
ALTER SEMANTIC VIEW emp_dept_analysis UNSET PROPERTIES ('spec_version');
```

> ⚠️ **Note**: The `properties` output in `DESC EXTENDED` is descriptive and **drops single quotes from property values** (for example, storing `COMMENT = 'x'` reads back as `COMMENT = x`); newlines are also rendered as the literal `\n`. If a property value contains quotes or newlines — such as a full DDL or JSON snippet — **base64-encode it first** before storing. Base64 uses only `[A-Za-z0-9+/=]` and can round-trip byte-for-byte.

## SHOW SEMANTIC VIEWS

Lists all semantic views under the specified schema, returning two columns: `schema_name` and `table_name`.

**Syntax**:

```sql
SHOW SEMANTIC VIEWS [ IN <schema_name> ];
```

It is recommended to always include `IN <schema_name>`. Without it, views under the current default schema are returned.

**Example**:

```sql
SHOW SEMANTIC VIEWS IN doc_test;
```

```
+-------------+-------------------+
| schema_name |    table_name     |
+-------------+-------------------+
| doc_test    | emp_dept_analysis |
+-------------+-------------------+
```

You can also query via `information_schema.tables` to get additional metadata:

```sql
SELECT table_name, comment, create_time, last_modify_time
FROM information_schema.tables
WHERE table_schema = 'doc_test'
  AND table_type = 'SEMANTIC_VIEW';
```

## DESC EXTENDED

View the complete definition of a semantic view, including logical table structures, primary/foreign key relationships, dimension metadata, and metric definitions.

**Note**: `DESC <view_name>` (without `EXTENDED`) returns an empty result set. You must include `EXTENDED`.

**Syntax**:

```sql
DESC EXTENDED <view_name>;
```

**Example**:

```sql
DESC EXTENDED doc_test.emp_dept_analysis;
```

Returned content includes:
- Basic view information: workspace, schema, creator, created_time, last_modified_time, comment
- Logical table list: alias, full physical table name, primary key, foreign key
- Dimension list: name, expression, `isUnique`, `isTime`, `enumValues`, comment
- Metric list: name, aggregation expression, comment

## Access Control

Semantic views support standard GRANT/REVOKE permission management, but only read-only permissions (`SELECT`, `ALL`) are supported. `INSERT`, `UPDATE`, and `DELETE` are not supported.

### GRANT

```sql
-- Grant query permission to a role
GRANT SELECT ON SEMANTIC VIEW doc_test.emp_dept_analysis TO ROLE test_readonly_role;

-- Grant all permissions (equivalent to SELECT)
GRANT ALL ON SEMANTIC VIEW doc_test.emp_dept_analysis TO ROLE workspace_dev;
```

### REVOKE

```sql
REVOKE SELECT ON SEMANTIC VIEW doc_test.emp_dept_analysis FROM ROLE test_readonly_role;
```

### SHOW GRANTS

View the permission grants on a semantic view:

```sql
SHOW GRANTS ON SEMANTIC VIEW doc_test.emp_dept_analysis;
```

Returned columns: `granted_type`, `privilege`, `granted_on` (value is `SEMANTIC_VIEW`), `object_name`, `granted_to`, `grantee_name`, `grantor_name`, `grant_option`, `granted_time`.

## Command Quick Reference

| Command | Description |
|------|------|
| `DROP SEMANTIC VIEW IF EXISTS` | Delete a semantic view |
| `ALTER SEMANTIC VIEW ... RENAME TO` | Rename |
| `ALTER SEMANTIC VIEW ... SET PROPERTIES` | Set properties (merge semantics) |
| `ALTER SEMANTIC VIEW ... UNSET PROPERTIES` | Remove properties |
| `SHOW SEMANTIC VIEWS [ IN schema ]` | List semantic views |
| `DESC EXTENDED` | View full structure (must include EXTENDED) |
| `GRANT SELECT ON SEMANTIC VIEW` | Grant query permission |
| `REVOKE SELECT ON SEMANTIC VIEW` | Revoke query permission |
| `SHOW GRANTS ON SEMANTIC VIEW` | View permissions |

## Related Documents

- [Create Semantic View](semantic-view-create.md)
- [Best Practices](semantic-view-best-practices.md)
