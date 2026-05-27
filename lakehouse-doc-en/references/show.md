# SHOW Command Reference

## Description

List existing objects of the specified type in Singdata Lakehouse.

## Syntax

```sql
SHOW <object_type_plural> 
    [ IN <scope_object_name> ] 
    [ LIKE '<pattern>' | WHERE <expression> ]
    [ LIMIT <num> ]
```

### Parameters

| Parameter | Description | Required |
|------|------|---------|
| `<object_type_plural>` | The type of object to list (plural form), e.g., `TABLES`, `SCHEMAS`, etc. | Yes |
| `IN <scope>` | Limits the scope level of the objects | No |
| `LIKE '<pattern>'` | Matches object names using wildcard patterns (supports `%` and `_`) | No |
| `WHERE <expression>` | Performs complex filtering based on object properties (mutually exclusive with LIKE) | No |
| `LIMIT <num>` | Limits the number of returned results | No |

### Scope Specification

| Object Type | Scope Format | Example |
|---------|-----------|------|
| TABLE/VIEW/MATERIALIZED VIEW/SYNONYM/VOLUME/TABLE STREAM/PIPE | `IN schema_name` | `SHOW TABLES IN sales` |
| Jobs | `IN VCLUSTER vc_name` | `SHOW JOBS IN VCLUSTER prod` |
| Indexes/Columns | `IN table_name` | `SHOW COLUMNS IN orders` |
| SCHEMA/VCLUSTER/USERS/ROLES | `IN workspace_name` | `SHOW SCHEMAS IN my_workspace` |
| Partitions | `IN` not supported | `SHOW PARTITIONS table_name` |
| CONNECTION/SHARE/FUNCTION | Scope specification not supported | `SHOW CONNECTIONS` |

### Result Filtering

- **`LIKE '<pattern>'`**: Matches object names using wildcard patterns
  ```sql
  SHOW TABLES LIKE 'temp%'  -- matches tables starting with "temp"
  ```

- **`WHERE <expression>`**: Performs complex filtering based on object properties (supports combined queries across all fields)
  ```sql
  SHOW TABLES WHERE is_view = false AND table_name LIKE '%taxi%';
  ```

  Object types that support WHERE filtering: `TABLE`, `TABLE STREAM`, `CONNECTION`, `VCLUSTER`, `JOB`, `SHARE`, `SYNONYM`, `PIPE`, `SCHEMA`

### Special Syntax

Index and column objects support using `FROM` instead of `IN TABLE`:
```sql
SHOW INDEXES FROM customers       -- equivalent to SHOW INDEXES IN TABLE customers
SHOW COLUMNS FROM order_details   -- equivalent to SHOW COLUMNS IN TABLE order_details
```

## Notes

1. `LIKE` and `WHERE` are mutually exclusive -- only one can be used at a time
2. Pattern matching is case-sensitive
3. The `WHERE` clause supports standard SQL expression syntax
4. `DROP SCHEMA` will cascade-delete all objects under that schema
5. CONNECTION and SHARE do not support scope specification

## Syntax Reference

### Users and Privileges
- [SHOW USERS](show-users.md)
- [SHOW ROLES](SHOWROLES.md)
- [SHOW GRANTS (User)](show-grants-user.md)
- [SHOW GRANTS (Role)](SHOWGRANTS.md)

### Schema and Catalog
- [SHOW SCHEMAS](show-schemas.md)
- [SHOW EXTERNAL SCHEMAS](show-external-schemas.md)
- [SHOW CATALOGS](show-catalog.md)

### Data Objects
- [SHOW TABLES](show-tables.md)
- [SHOW VIEWS](show-views.md)
- [SHOW MATERIALIZED VIEWS](show-materialized-view.md)
- [SHOW DYNAMIC TABLES](show-dynamic-table.md)
- [SHOW EXTERNAL TABLES](show-external-table.md)
- [SHOW TABLE STREAMS](show-table-streams.md)
- [SHOW COLUMNS](show-columns.md)
- [SHOW PARTITIONS](list-partition.md)

### Indexes and Synonyms
- [SHOW INDEX](SHOW-INDEX.md)
- [SHOW SYNONYMS](show-synonyms.md)

### Pipes and Volumes
- [SHOW PIPES](pipe-syntax.md)
- [SHOW VOLUMES](show-volume.md)

### Compute and Jobs
- [SHOW VCLUSTERS](show-vclusters.md)
- [SHOW JOBS](show-jobs.md)
- [SHOW DYNAMIC TABLE REFRESH HISTORY](refresh-history.md)

### Connections and Shares
- [SHOW CONNECTIONS](SHOWCONNECTIONS.md)
- [SHOW SHARES](show-shares.md)
