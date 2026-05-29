# ALTER Command Reference

## Description

Modifies the definition, properties, or configuration of an existing object in Singdata Lakehouse.

## Syntax

```sql
ALTER <object_type> <object_name> <actions>
```

### Parameter Description

| Parameter | Description | Required |
|-----------|-------------|----------|
| `<object_type>` | The type of object to modify, e.g., `TABLE`, `SCHEMA`, `VCLUSTER` | Yes |
| `<object_name>` | The name of the object, which may include a schema prefix | Yes |
| `<actions>` | The specific operation, e.g., `ADD COLUMN`, `SET COMMENT`, `RENAME TO` | Yes |

## Supported Object Types

| Object Type | Syntax Example | Description |
|-------------|---------------|-------------|
| Workspace | `ALTER WORKSPACE <name> SET ...` | Modify workspace configuration |
| Compute Cluster | `ALTER VCLUSTER <name> ...` | Modify VCluster specification/status |
| Data Share | `ALTER SHARE <name> ...` | Modify Share configuration |
| Schema | `ALTER SCHEMA <name> ...` | Modify Schema properties |
| External Schema | `ALTER EXTERNAL SCHEMA <name> ...` | Modify external Schema configuration |
| Regular Table | `ALTER TABLE <name> ...` | Modify table properties, add/drop columns, etc. |
| Table Column | `ALTER TABLE <name> ALTER COLUMN ...` | Column-level structural changes |
| Dynamic Table | `ALTER DYNAMIC TABLE <name> ...` | Suspend/resume/rename a dynamic table |
| Materialized View | `ALTER MATERIALIZED VIEW <name> ...` | Modify materialized view properties |
| External Table | `ALTER EXTERNAL TABLE <name> ...` | Modify external table configuration |
| Pipe | `ALTER PIPE <name> ...` | Modify Pipe scheduling configuration |
| User | `ALTER USER <name> ...` | Modify user properties |

## Permission Requirements

Executing an `ALTER` operation generally requires `OWNERSHIP` or corresponding administrative privileges on the target object. Some operations (e.g., modifying VCLUSTER configuration) also require workspace-level administrative privileges.

## Notes

- The `ALTER` statement is used to modify existing objects without the need to drop and recreate them.
- `ALTER TABLE COLUMN` is specifically for column-level structural changes (add, drop, modify columns).
- Dynamic tables do not support modifying their SQL definition via `ALTER`; use `CREATE OR REPLACE` instead.

## Syntax Reference

### Instances and Workspaces
- [ALTER WORKSPACE](alter-workspace.md)

### Compute and Sharing
- [ALTER VCLUSTER](alter-vcluster.md)
- [ALTER SHARE](alter-share.md)

### Schema and Catalog
- [ALTER SCHEMA](ALTER-SCHEMA.md)
- [ALTER EXTERNAL SCHEMA](alter-external-schema.md)

### Data Objects
- [ALTER TABLE](alter-table.md)
- [ALTER TABLE COLUMN](ALTER-TABLE-COLUMN.md)
- [ALTER DYNAMIC TABLE](alter-dynamic-table.md)
- [ALTER MATERIALIZED VIEW](alter-materialized-view.md)
- [ALTER EXTERNAL TABLE](ALTER-EXTERNAL-TABLE.md)

### Pipes and Connections
- [ALTER PIPE](pipe-syntax.md)

### Users and Roles
- [ALTER USER](alter-user.md)
