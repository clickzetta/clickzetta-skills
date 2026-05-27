# ALTER VOLUME

Modifies Volume properties or refreshes the file directory metadata of a Volume.

## Syntax

```Plain
ALTER VOLUME [schema_name.]<volume_name> REFRESH;
```

> Subject to actual execution results; future versions may support additional ALTER VOLUME subcommands.

## Parameters

| Parameter | Description |
|---|---|
| `schema_name` | Name of the owning schema; current schema is used if omitted |
| `volume_name` | Name of the Volume to modify |
| `REFRESH` | Re-scan the external storage path and update the Volume's file directory metadata |

## Examples

1. Manually refresh External Volume file metadata:

```SQL
ALTER VOLUME my_oss_vol REFRESH;
```

2. Specify the schema to refresh a Volume:

```SQL
ALTER VOLUME my_schema.my_oss_vol REFRESH;
```

## Notes

- `REFRESH` only applies to External Volumes (mounting external storage); Named Volumes (internal storage) do not require refreshing
- When files in the external object storage are added, deleted, or modified, `REFRESH` must be executed so that Lakehouse can detect the latest file list
- If `DIRECTORY.auto_refresh = true`, the system will refresh automatically and no manual execution is needed

## Required Privileges

| Privilege | Description |
|---|---|
| `ALTER VOLUME` | Modify Volume properties (e.g., execute REFRESH) |

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [External Volume](external_volume.md)
- [Using Internal Volume](internal_volume.md)
