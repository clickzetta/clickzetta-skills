# CONNECTION

CONNECTION objects are used to store authentication credentials and access credentials for third-party services, allowing Lakehouse to process data without exposing sensitive information in plaintext. CONNECTION also supports STS (Security Token Service) authentication, enabling cross-account authorized access to external services.

## Types of CONNECTION

| Type | Purpose | Supported External Services |
|------|------|--------------|
| [API Connection](create-api-connection.md) | Stores authentication credentials for third-party application services, used in conjunction with Remote Function | Alibaba Cloud Function Compute FC, Tencent Cloud SCF |
| [Storage Connection](create-storage-connection.md) | Stores authentication credentials for object storage or message queues, used for VOLUME, external tables, data import/export | Alibaba Cloud OSS, Tencent Cloud COS, AWS S3, Kafka, HDFS |
| [Catalog Connection](create-catalog-connection.md) | Stores connection information for external metadata services, used for federated queries | Hive Metastore, Databricks Unity Catalog |

## Viewing CONNECTION

List all CONNECTIONs in the current workspace:

```SQL
SHOW CONNECTIONS;
+------------------+----------+---------+---------+-------------------------+
|       name       | category |  type   | enabled |      created_time       |
+------------------+----------+---------+---------+-------------------------+
| oss_sh_conn_ak   | STORAGE  | OSS     | ENABLED | 2025-05-11 09:36:51.548 |
| kafka_prod_conn  | STORAGE  | KAFKA   | ENABLED | 2025-03-20 14:22:10.312 |
| hms_catalog_conn | CATALOG  | HMS     | ENABLED | 2025-04-01 08:15:33.901 |
+------------------+----------+---------+---------+-------------------------+
```

View details of a specific CONNECTION:

```SQL
DESC CONNECTION oss_sh_conn_ak;
+----------------------+------------------------------------------+
|      info_name       |               info_value                 |
+----------------------+------------------------------------------+
| name                 | oss_sh_conn_ak                           |
| type                 | OSS                                      |
| enabled              | ENABLED                                  |
| creator              | qiliang                                  |
| created_time         | 2025-05-11T09:36:51.548Z                 |
| last_modified_time   | 2025-05-11T09:36:51.548Z                 |
| ACCESS_ID            | LTAI5t**************                     |
| ENDPOINT             | oss-cn-shanghai-internal.aliyuncs.com    |
+----------------------+------------------------------------------+
```

## Dropping CONNECTION

```SQL
DROP CONNECTION [IF EXISTS] connection_name;
```

## Notes

* CONNECTION objects are stored at the workspace level, allowing users within the same workspace to share and use them.
* Before dropping a CONNECTION, verify that no VOLUME, external table, or Catalog is referencing it, otherwise the related objects will become inaccessible.
* Cross-cloud Storage Connection creation is not supported: Alibaba Cloud instances can only create OSS Connections, and Tencent Cloud instances can only create COS Connections.
