# CREATE VOLUME

Creates a Named Volume using Lakehouse internal storage. Named Volumes must be explicitly created by users and are suitable for scenarios such as cross-team resource sharing.

> **Note**: Although Named Volumes use internal storage, they fall under the External Volume category and differ from automatically created User Volumes and Table Volumes.

## Syntax

```Plain
CREATE VOLUME [IF NOT EXISTS] [schema_name.]<volume_name>
    DIRECTORY = (
        enable = { true | false },
        auto_refresh = { true | false }
    )
    RECURSIVE = { true | false };
```

## Parameters

| Parameter | Description |
|---|---|
| `IF NOT EXISTS` | If the Volume already exists, skip without error |
| `schema_name` | Name of the owning schema; current schema is used if omitted |
| `volume_name` | Volume name, must be unique within the same schema |
| `DIRECTORY.enable` | Whether to enable the directory feature; recommended to set to `true` |
| `DIRECTORY.auto_refresh` | Whether to automatically refresh file metadata |
| `RECURSIVE` | Whether to recursively scan subdirectories |

## Examples

1. Create a Named Volume using internal storage:

```SQL
CREATE VOLUME my_named_vol
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

2. Create a Named Volume under a specific schema:

```SQL
CREATE VOLUME IF NOT EXISTS my_schema.shared_vol
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

## Notes

- Named Volume storage costs are charged at the Lakehouse storage standard rate
- Named Volumes do not support `ALTER VOLUME ... REFRESH` (only External Volumes support this)
- Deleting a Named Volume does not delete the actual files in internal storage; to delete files, first use the `REMOVE` command

## Required Privileges

| Privilege | Description |
|---|---|
| `CREATE VOLUME` | Create a Volume under the current schema |

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [External Volume](external_volume.md)
- [Using Internal Volume](internal_volume.md)
- [Volume File Management](SQL_Volume_Guide.md): Complete usage scenarios for uploading, querying, importing, and exporting Volume files
