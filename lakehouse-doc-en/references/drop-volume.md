# DROP VOLUME

Deletes a Volume object in Lakehouse (including External Volume and Named Volume).

## Syntax

```Plain
DROP VOLUME [IF EXISTS] [schema_name.]<volume_name>;
```

## Parameters

| Parameter | Description |
|---|---|
| `IF EXISTS` | If the Volume does not exist, skip without error |
| `schema_name` | Name of the owning schema; current schema is used if omitted |
| `volume_name` | Name of the Volume to delete |

## Examples

1. Delete an External Volume:

```SQL
DROP VOLUME my_oss_vol;
```

2. Use `IF EXISTS` to avoid errors:

```SQL
DROP VOLUME IF EXISTS my_oss_vol;
```

3. Delete a Volume under a specific schema:

```SQL
DROP VOLUME IF EXISTS my_schema.my_named_vol;
```

## Notes

- Deleting an External Volume only removes the metadata reference in Lakehouse and **does not delete** the actual files in the external object storage
- Deleting a Named Volume only removes the metadata reference in Lakehouse and **does not delete** the actual files in internal storage; to delete files, first use the `REMOVE` command
- The delete operation is irreversible; confirm that the Volume is no longer in use before executing

## Required Privileges

| Privilege | Description |
|---|---|
| `DROP VOLUME` | Delete the specified Volume object |

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [External Volume](external_volume.md)
- [Using Internal Volume](internal_volume.md)
