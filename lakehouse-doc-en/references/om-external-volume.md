# External Volume

External Volume is used to **mount external object storage** (Alibaba Cloud OSS, Tencent Cloud COS, Amazon S3), allowing Lakehouse to directly access files within using SQL without first copying data in.

## Creating an External Volume

Prerequisite: Create a Storage Connection (storage authentication configuration) first.

```sql
-- Step 1: Create Storage Connection
CREATE STORAGE CONNECTION my_oss_conn
  TYPE OSS
  access_id = 'LTAIxxxx'
  access_key = 'T8Gexxxx'
  ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';

-- Step 2: Mount OSS path as External Volume
CREATE EXTERNAL VOLUME my_oss_volume
  LOCATION 'oss://my-bucket/data/'
  USING CONNECTION my_oss_conn
  DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
  RECURSIVE = TRUE;
```

## Main Operations

```sql
-- View files in the Volume
SELECT * FROM DIRECTORY(VOLUME my_oss_volume);

-- Query files directly (no import needed)
SELECT * FROM VOLUME my_oss_volume
USING PARQUET SUBDIRECTORY 'orders/2024/';

-- Import data into a table
COPY INTO orders FROM VOLUME my_oss_volume
USING CSV OPTIONS('header'='true');

-- Refresh the directory (after uploading new files)
ALTER VOLUME my_oss_volume REFRESH;
```

> Note: After uploading new files, `SHOW VOLUME DIRECTORY` may not display them immediately. If `AUTO_REFRESH` is not enabled, manually execute `ALTER VOLUME name REFRESH`.

## Supported Cloud Storage

| Cloud Provider | Type | Notes |
|--------|------|------|
| Alibaba Cloud | OSS | Must be in the same cloud as the Lakehouse instance |
| Tencent Cloud | COS | Must be in the same cloud as the Lakehouse instance |
| Amazon | S3 | Must be in the same cloud as the Lakehouse instance |

## Related Documents

- [CREATE EXTERNAL VOLUME](create-external-volume.md)
- [External Volume Details](external_volume.md)
- [Storage Connection](om-storage-connection.md)
