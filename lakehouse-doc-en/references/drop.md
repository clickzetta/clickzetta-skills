# DROP Command Reference

## Description

Deletes various database objects in Singdata Lakehouse.

## Syntax

```sql
DROP <object_type> [ IF EXISTS ] <identifier>
```

### Parameters

| Parameter | Description | Required |
|------|------|---------|
| `<object_type>` | The type of object to delete, such as `TABLE`, `DYNAMIC TABLE`, `VIEW`, etc. | Yes |
| `IF EXISTS` | Silently skip if the object does not exist, without raising an error | No |
| `<identifier>` | Object name, may include a schema prefix | Yes |

## Supported Object Types

| Object Type | Drop Syntax | Recoverable | Recovery Syntax |
|---------|---------|--------|---------|
| Regular Table | `DROP TABLE <name>` | Yes | `UNDROP TABLE <name>` |
| Dynamic Table | `DROP DYNAMIC TABLE <name>` | Yes | `UNDROP TABLE <name>` |
| Materialized View | `DROP MATERIALIZED VIEW <name>` | Yes | `UNDROP TABLE <name>` |
| Table Stream | `DROP TABLE STREAM <name>` | Yes | `UNDROP TABLE <name>` |
| View | `DROP VIEW <name>` | No | -- |
| External Table | `DROP EXTERNAL TABLE <name>` | No | -- |
| Schema | `DROP SCHEMA <name>` | No | -- |
| External Schema | `DROP EXTERNAL SCHEMA <name>` | No | -- |
| Compute Cluster | `DROP VCLUSTER <name>` | No | -- |
| Connection | `DROP CONNECTION <name>` | No | -- |
| Data Share | `DROP SHARE <name>` | No | -- |
| Index | `DROP INDEX <name>` | No | -- |
| Function | `DROP FUNCTION <name>` | No | -- |
| External Function | `DROP EXTERNAL FUNCTION <name>` | No | -- |
| Synonym | `DROP SYNONYM <name>` | No | -- |
| User | `DROP USER <name>` | No | -- |
| Role | `DROP ROLE <name>` | No | -- |

## Permission Requirements

Executing a `DROP` operation requires one of the following permissions:
- `OWNERSHIP` permission on the target object
- Workspace-level `ADMIN` role
- Having been granted the corresponding `DROP` permission (via the `GRANT` command)

## Notes

- **Object type must match**: Dropping a dynamic table requires `DROP DYNAMIC TABLE`, and dropping a materialized view requires `DROP MATERIALIZED VIEW`. Using the wrong type will result in an error.
- **Data recoverability**: Regular tables, dynamic tables, materialized views, and Table Streams can be recovered with `UNDROP TABLE` within the Time Travel retention period.
- **Cascading deletion**: `DROP SCHEMA` cascades to delete all objects under that Schema; no additional `CASCADE` specification is needed.
- **Dependency check**: Before dropping a table, check whether any views, dynamic tables, Table Streams, or ETL tasks depend on that object.

## Syntax Reference

### Table Related
- [DROP TABLE](drop-table.md)
- [DROP DYNAMIC TABLE](drop-dynamic-table.md)
- [DROP MATERIALIZED VIEW](drop-materialized-view.md)
- [DROP VIEW](drop-view.md)
- [DROP EXTERNAL TABLE](drop-external-table.md)
- [DROP TABLE STREAM](drop-table-stream.md)
- [UNDROP TABLE](undrop-table.md)

### Schema Related
- [DROP SCHEMA](drop-schema.md)
- [DROP EXTERNAL SCHEMA](drop-external-schema.md)

### Compute and Connection
- [DROP VCLUSTER](drop-vcluster.md)
- [DROP CONNECTION](drop-connection.md)
- [DROP SHARE](drop-share.md)

### Index and Function
- [DROP INDEX](drop-index.md)
- [DROP FUNCTION](drop-function.md)

### Other Objects
- [DROP SYNONYM](drop-synonym.md)
- [DROP USER](drop-user.md)
- [DROP ROLE](drop-role.md)
