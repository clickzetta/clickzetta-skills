# Data Pipe

A Pipe is a continuous data ingestion object in Singdata Lakehouse, supporting continuous data ingestion from object storage and Kafka.

| Data Source | Mode | Reference |
|--------|------|---------|
| Object Storage (OSS/COS/S3) | LIST_PURGE scan or event notification | [Continuous Ingestion from Object Storage](pipe-storage-object.md) |
| Kafka | READ_KAFKA function for continuous consumption | [Continuous Ingestion from Kafka](pipe-kafka.md) |

For detailed Pipe SQL commands, see [Pipe SQL Reference](pipe-syntax.md).
