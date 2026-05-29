# CREATE EXTERNAL VOLUME

Mounts external object storage (Alibaba Cloud OSS, Tencent Cloud COS, Amazon S3) and creates an External Volume object in Lakehouse.

## Prerequisites

Before creating an External Volume, you need to create the corresponding Storage Connection:

```SQL
-- Create an Alibaba Cloud OSS storage connection
CREATE STORAGE CONNECTION IF NOT EXISTS oss_conn
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_ID = 'your_access_key_id'
    ACCESS_KEY = 'your_access_key_secret';
```

## Syntax

```Plain
CREATE EXTERNAL VOLUME [IF NOT EXISTS] [schema_name.]<volume_name>
    LOCATION '<storage_url>'
    USING CONNECTION <connection_name>
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
| `LOCATION` | Object storage path, format: `oss://bucket_name/path/`, `cos://bucket_name/path/`, `s3://bucket_name/path/` |
| `USING CONNECTION` | The Storage Connection name to reference |
| `DIRECTORY.enable` | Whether to enable the directory feature; recommended to set to `true` |
| `DIRECTORY.auto_refresh` | Whether to automatically refresh file metadata |
| `RECURSIVE` | Whether to recursively scan subdirectories |

## Examples

1. Mount an Alibaba Cloud OSS bucket:

```SQL
CREATE EXTERNAL VOLUME my_oss_vol
    LOCATION 'oss://mcp-data-hangzhou/test/'
    USING CONNECTION oss_conn
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

2. Mount a Tencent Cloud COS bucket:

```SQL
CREATE EXTERNAL VOLUME my_cos_vol
    LOCATION 'cos://my-bucket-1234567890/data/'
    USING CONNECTION cos_conn
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

3. Mount an Amazon S3 bucket:

```SQL
CREATE EXTERNAL VOLUME my_s3_vol
    LOCATION 's3://my-s3-bucket/data/'
    USING CONNECTION s3_conn
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

4. Create under a specific schema with `IF NOT EXISTS`:

```SQL
CREATE EXTERNAL VOLUME IF NOT EXISTS my_schema.my_oss_vol
    LOCATION 'oss://mcp-data-hangzhou/test/'
    USING CONNECTION oss_conn
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

## Notes

- External Volumes only store path metadata; actual data is stored in the external cloud storage, so there are no additional storage costs on the Lakehouse side
- Cross-cloud creation is not supported: Alibaba Cloud instances can only create OSS Connections, Tencent Cloud instances can only create COS Connections, etc.
- Deleting an External Volume does not delete the actual files in the external storage

## Required Privileges

| Privilege | Description |
|---|---|
| `CREATE VOLUME` | Create a Volume under the current schema |

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [External Volume](external_volume.md)
- [Using Internal Volume](internal_volume.md)
