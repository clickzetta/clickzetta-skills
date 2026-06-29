# Storage Connection

A Storage Connection stores authentication credentials for **object storage services**, enabling External Volumes and External Tables to securely access cloud storage.

## Use Cases

When creating an External Volume or external table, you need to first create a Storage Connection to configure cloud storage access keys, avoiding exposing credentials in plaintext within SQL.

```
External Volume / External Table
  └── Storage Connection (stores access credentials)
        └── OSS / COS / S3
```

## Creation Examples

```sql
-- Alibaba Cloud OSS
CREATE STORAGE CONNECTION my_oss_conn
  TYPE OSS
  access_id  = 'LTAIxxxxxxxxxxxx'
  access_key = 'T8Gexxxxxxxx'
  ENDPOINT   = 'oss-cn-hangzhou-internal.aliyuncs.com';

-- Tencent Cloud COS
CREATE STORAGE CONNECTION my_cos_conn
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION     = 'ap-shanghai'
  APP_ID     = '1310000503';

-- Amazon S3
CREATE STORAGE CONNECTION my_s3_conn
  TYPE S3
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION     = 'us-east-1';
```

> ⚠️ A Storage Connection must be in the same cloud provider as the Lakehouse instance. An Alibaba Cloud instance cannot create COS/S3 connections.

## Related Documentation

- [CREATE STORAGE CONNECTION](create-storage-connection.md) — Full syntax
- [External Volume](om-external-volume.md) — Mount object storage using a Storage Connection
- [Connection Overview](create-connection.md)
