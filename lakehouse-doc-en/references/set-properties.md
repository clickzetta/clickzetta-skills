# SET / UNSET / SHOW PROPERTIES

`SET PROPERTIES` sets persistent properties on data objects (tables, schemas, workspaces). Properties are written to metadata and **take effect permanently** until explicitly removed.

> Different from [SET](set-command.md) (session parameters): `SET PROPERTIES` modifies the persistent configuration of an object, not a temporary session-level parameter.

## SET PROPERTIES

### Syntax

```Plain
ALTER TABLE [schema_name.]table_name SET PROPERTIES ('key1'='value1' [, 'key2'='value2' ...]);
ALTER SCHEMA schema_name SET PROPERTIES ('key1'='value1' [, ...]);
ALTER WORKSPACE workspace_name SET PROPERTIES ('key1'='value1' [, ...]);
```

### Examples

```SQL
-- Set compression and auto-refresh properties on a table
ALTER TABLE sales_records SET PROPERTIES ('compression'='zstd', 'auto_refresh'='true');

-- Set data retention period on a schema
ALTER SCHEMA reporting SET PROPERTIES ('data_retention_days'='90');

-- Set a property on a workspace
ALTER WORKSPACE analytics_ws SET PROPERTIES ('aa'='bb');
```

## UNSET PROPERTIES

Removes properties that have been set on a data object, restoring the system default configuration.

### Syntax

```Plain
ALTER TABLE [schema_name.]table_name UNSET PROPERTIES (key1 [, key2 ...]);
ALTER SCHEMA schema_name UNSET PROPERTIES (key1 [, ...]);
ALTER WORKSPACE workspace_name UNSET PROPERTIES (key1 [, ...]);
```

### Examples

```SQL
-- Remove a single property from a table
ALTER TABLE sales_records UNSET PROPERTIES ('compression');

-- Remove multiple properties at once
ALTER TABLE customer_feedback UNSET PROPERTIES ('auto_refresh', 'compression');

-- Remove a schema property
ALTER SCHEMA reporting UNSET PROPERTIES ('data_retention_days');
```

> ⚠️ **Note**: Removing a property that does not exist succeeds silently without an error.

## SHOW PROPERTIES

View all properties currently set on a data object.

### Syntax

```Plain
SHOW PROPERTIES IN TABLE [schema_name.]table_name;
SHOW PROPERTIES IN SCHEMA schema_name;
SHOW PROPERTIES IN WORKSPACE workspace_name;
```

### Examples

```SQL
SHOW PROPERTIES IN TABLE sales_data;
SHOW PROPERTIES IN SCHEMA reporting;
SHOW PROPERTIES IN WORKSPACE data_science;
```

### Return Format

```
+------------------+----------------+
| property_key     | property_value |
+------------------+----------------+
| compression      | zstd           |
| auto_refresh     | true           |
+------------------+----------------+
```

---

## Supported Table Properties

| Property | Description | Valid Values |
|----------|-------------|--------------|
| `data_lifecycle` | Data lifecycle in days; -1 means disabled | Positive integer or -1 |
| `data_retention_days` | Time Travel retention period; affects UNDROP, TABLE STREAM, and RESTORE | 0–90 |
| `cz.storage.write.max.string.bytes` | Maximum write length for STRING type; default 16 MB | Positive integer (bytes) |
| `cz.storage.write.max.binary.bytes` | Maximum write length for BINARY type; default 16 MB | Positive integer (bytes) |
| `cz.storage.write.max.json.bytes` | Maximum write length for JSON type; default 16 MB | Positive integer (bytes) |

**Example: increase the maximum STRING length to 32 MB**

```SQL
ALTER TABLE my_table SET PROPERTIES ("cz.storage.write.max.string.bytes"="33554432");
```

---

## Notes

- Requires `ALTER` permission on the corresponding object.
- Workspace-level property changes typically take effect within about 1 minute.
- You can set or remove multiple properties in a single command.

## Related Documentation

- [SET (session parameters)](set-command.md)
- [ALTER TABLE](alter-table.md)
- [ALTER SCHEMA](ALTER-SCHEMA.md)
- [ALTER WORKSPACE](alter-workspace.md)
