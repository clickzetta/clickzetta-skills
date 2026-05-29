# DESC VOLUME

Views detailed information about a Volume, including creator, creation time, storage path, connection name, and directory configuration.

## Syntax

```Plain
DESC VOLUME [schema_name.]<volume_name>;
```

`DESCRIBE VOLUME` and `DESC VOLUME` are equivalent.

## Parameters

| Parameter | Description |
|---|---|
| `schema_name` | Name of the owning schema; current schema is used if omitted |
| `volume_name` | Name of the Volume to view |

## Examples

1. View External Volume details:

```SQL
DESC VOLUME my_oss_vol;
```

Sample output:

```Plain
+------------------------+--------------------------------+
| info_name              | info_value                     |
+------------------------+--------------------------------+
| name                   | my_oss_vol                     |
| creator                | qiliang                        |
| created_time           | 2026-05-20 00:23:49.074        |
| last_modified_time     | 2026-05-20 00:23:49.074        |
| external               | true                           |
| url                    | oss://mcp-data-hangzhou/test/  |
| connection_name        | quick_start.oss_conn           |
| recursive              | true                           |
| directory_enabled      | true                           |
| directory_auto_refresh | true                           |
+------------------------+--------------------------------+
```

2. View Named Volume details:

```SQL
DESC VOLUME my_named_vol;
```

3. View a Volume under a specific schema:

```SQL
DESC VOLUME my_schema.my_oss_vol;
```

## Output Field Descriptions

| Field | Description |
|---|---|
| `name` | Volume name |
| `creator` | Creator username |
| `created_time` | Creation time |
| `last_modified_time` | Last modification time |
| `external` | Whether it is external storage (`true` means external storage mount, `false` means internal storage) |
| `url` | Object storage path (only has a value for External Volumes) |
| `connection_name` | Associated Storage Connection name (only has a value for External Volumes) |
| `recursive` | Whether to recursively scan subdirectories |
| `directory_enabled` | Whether the directory feature is enabled |
| `directory_auto_refresh` | Whether to automatically refresh file metadata |

## Required Privileges

| Privilege | Description |
|---|---|
| `READ METADATA` | View Volume object metadata |

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [External Volume](external_volume.md)
- [Using Internal Volume](internal_volume.md)
