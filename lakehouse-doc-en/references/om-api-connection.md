# API Connection

API Connection is used to store authentication information for **third-party function compute services**, enabling External Function invocations.

Currently supported services: Alibaba Cloud Function Compute (FC), Tencent Cloud Serverless Cloud Function (SCF).

## Use Cases

When you need to call custom logic written in Python/Java (External Function) within SQL, you must first create an API Connection to configure the access credentials for the function compute service.

```
SQL Query
  └── External Function (invokes remote function)
        └── API Connection (stores authentication info)
              └── Alibaba Cloud FC / Tencent Cloud SCF
```

## Create Example

```sql
-- Alibaba Cloud Function Compute
CREATE API CONNECTION my_fc_conn
  TYPE cloud_function
  PROVIDER = 'aliyun'
  REGION = 'cn-hangzhou'
  ROLE_ARN = 'acs:ram::138xxxxxxxx:role/czudfrole'
  NAMESPACE = 'my-namespace'
  CODE_BUCKET = 'my-bucket';
```

## Related Documents

- [CREATE API CONNECTION](create-api-connection.md) — full syntax
- [External Function](om-external-function.md) — how to use API Connection to create external functions
- [Connection Overview](connection-guide.md)
