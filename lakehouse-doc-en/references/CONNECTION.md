# CONNECTION

A CONNECTION object stores authentication information and access credentials for third-party services, so Lakehouse can process data without exposing sensitive information in plain text. CONNECTION also supports STS (Security Token Service) authentication, allowing cross-account authorization to access external services.

## CONNECTION Types

| Type | Purpose | Supported External Services |
|------|---------|----------------------------|
| [API Connection](create-api-connection.md) | Stores authentication information for third-party application services; used with Remote Functions | Alibaba Cloud Function Compute (FC), Tencent Cloud SCF |
| [Storage Connection](create-storage-connection.md) | Stores authentication information for object storage or message queues; used for VOLUMEs, external tables, and data import/export | Alibaba Cloud OSS, Tencent Cloud COS, AWS S3, Kafka, HDFS |
| [Catalog Connection](create-catalog-connection.md) | Stores connection information for external metadata services; used for federated queries | Hive Metastore, Databricks Unity Catalog |

## Syntax Reference

- [CREATE API CONNECTION](create-api-connection.md)
- [CREATE STORAGE CONNECTION](create-storage-connection.md)
- [CREATE CATALOG CONNECTION](create-catalog-connection.md)
- [SHOW CONNECTIONS](show-connections.md)
- [DESC CONNECTION](desc-connection.md)
- [DROP CONNECTION](drop-connection.md)

## Notes

* CONNECTION objects are stored at the workspace level and can be shared by all users within the same workspace.
* Before dropping a CONNECTION, confirm that no VOLUME, external table, or Catalog is referencing it; otherwise those objects will become inaccessible.
* Cross-cloud-provider Storage Connections are not supported: Alibaba Cloud instances can only create OSS Connections, and Tencent Cloud instances can only create COS Connections.
