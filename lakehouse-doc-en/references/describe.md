# DESC Command Reference

## Description

Displays the detailed structure or properties of a specified object in Singdata Lakehouse. `DESCRIBE` can be abbreviated as `DESC`.

## Syntax

```sql
DESC[RIBE] <object_type> [ EXTENDED ] <object_name>
```

### Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `<object_type>` | The type of object to describe, such as `TABLE`, `SCHEMA`, `VCLUSTER`, etc. | Yes |
| `EXTENDED` | Display more detailed information | No |
| `<object_name>` | The object name, may include a schema prefix | Yes |

## Supported Object Types

| Object Type | Syntax Example | Description |
|-------------|---------------|-------------|
| Regular Table | `DESC TABLE <name>` | Show table structure (column names, types, comments) |
| Dynamic Table | `DESC DYNAMIC TABLE <name>` | Show dynamic table structure and refresh configuration |
| Materialized View | `DESC MATERIALIZED VIEW <name>` | Show materialized view structure |
| View | `DESC VIEW <name>` | Show view definition |
| External Table | `DESC EXTERNAL TABLE <name>` | Show external table structure |
| Table Stream | `DESC TABLE STREAM <name>` | Show Stream configuration and schema |
| Schema | `DESC SCHEMA <name>` | Show Schema information |
| External Schema | `DESC EXTERNAL SCHEMA <name>` | Show external Schema configuration |
| External Catalog | `DESC CATALOG <name>` | Show External Catalog information |
| Compute Cluster | `DESC VCLUSTER <name>` | Show VCluster specifications and status |
| Connection | `DESC CONNECTION <name>` | Show Connection configuration |
| Data Share | `DESC SHARE <name>` | Show Share configuration |
| Index | `DESC INDEX <name>` | Show index information |
| Job | `DESC JOB <job_id>` | Show job execution information |
| History Version | `DESC HISTORY <name>` | Show table history versions |
| Function | `DESC FUNCTION <name>` | Show function definition |
| Synonym | `DESC SYNONYM <name>` | Show synonym mapping |

## Required Permissions

Executing `DESC` statements typically only requires basic view permissions (`USAGE` or `SELECT`) on the target object.

## Notes

- `DESCRIBE` and `DESC` are equivalent and can be used interchangeably.
- Some object types support the `EXTENDED` parameter to display more information.
- `DESC HISTORY` can view history version information for tables, dynamic tables, and materialized views.

## Syntax Reference

### Data Objects
- [DESC TABLE](desc-table.md)
- [DESC DYNAMIC TABLE](desc-dynamic-table.md)
- [DESC MATERIALIZED VIEW](desc-materialized-view.md)
- [DESC VIEW](desc-view.md)
- [DESC EXTERNAL TABLE](desc-external-table.md)
- [DESC TABLE STREAM](desc-table-stream.md)

### Schema and Catalog
- [DESC SCHEMA](desc-schemas.md)
- [DESC EXTERNAL SCHEMA](desc-external-schemas.md)
- [DESC CATALOG](desc-catalog.md)

### Compute and Connections
- [DESC VCLUSTER](desc-vcluster.md)
- [DESC CONNECTION](desc-connection.md)
- [DESC SHARE](desc-share.md)

### Indexes and Jobs
- [DESC INDEX](desc-index.md)
- [DESC JOB](desc-job.md)

### Others
- [DESC HISTORY](desc-history.md)
- [DESC FUNCTION](desc-function.md)
- [DESC SYNONYM](synonym.md)
