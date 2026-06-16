# Data Ingestion

Singdata Lakehouse supports three categories of data ingestion: real-time database sync, file import, and message queue ingestion. Choose based on your data source.

***

## I have a relational database (MySQL / PostgreSQL / SQL Server, etc.)

**Recommended: Studio Data Sync Tasks** — visual configuration, supports full load + real-time incremental sync, no coding required.

| Scenario                                                 | Approach                          | Reference                                                           |
| -------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------- |
| Single table or a few tables, real-time sync             | Studio real-time sync task (CDC)  | [Real-time Sync Task](realtime_sync.md)                             |
| Full database sync, mirroring a source DB into Lakehouse | Studio multi-table real-time sync | [Multi-table Real-time Sync Guide](multitable_realtime_sync_sop.md) |
| Offline periodic sync (T+1 or H+1)                       | Studio offline sync task          | [Offline Sync Task](batch_sync.md) · [FAQ](batch_sync_sop.md)       |
| Oracle database real-time sync                           | Bluepipe integration              | [Oracle Real-time Sync](bluepipe-oracle-lakehouse-datasync.md)      |
| Sync over private network (VPC / Private Link)           | Studio + Private Link             | [RDS Sync over VPC](studio-di-privatelink-vpc-from-rds.md)          |

> **End-to-end example**: [Complete workflow from MySQL to BI reports](quick_start_bi_analysis.md)

***

## I have files (CSV / Parquet / JSON, etc.)

| Scenario                                                 | Approach                         | Reference                                                                                         |
| -------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------- |
| Files are local, quick import                            | Studio upload or PUT + COPY INTO | [Import Local Data](load-data-local.md) · [Quick Upload](quick_start_upload_data.md)              |
| Files are on OSS / S3 / COS, one-time import             | COPY INTO + Volume               | [Bulk Import from Object Storage](load-data-oss.md)                                               |
| Files are continuously uploaded to OSS / S3, auto-ingest | Pipe (object storage mode)       | [Pipe Continuous Ingestion](pipe-introduction.md) · [Object Storage Pipe](pipe-storage-object.md) |
| Feishu spreadsheet / online spreadsheet import           | Feishu data import               | [How to Import Feishu Spreadsheets](import-feishu-data.md)                                        |

> **Choosing between the two continuous ingestion modes**: Use `LIST_PURGE` if you don't need to keep the source files after upload. Use `EVENT_NOTIFICATION` if you need to retain the source files or require near-real-time triggering. See [Pipe Continuous Ingestion](pipe-introduction.md) for details.

***

## I have a Kafka message stream

| Scenario                                                | Approach                            | Reference                                                         |
| ------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------- |
| Continuously consume a Kafka topic and write to a table | Pipe (Kafka mode)                   | [Kafka Pipe](pipe-kafka.md)                                       |
| Configure Kafka sync visually via Studio                | Studio real-time sync task          | [Kafka Real-time Sync](realtime_sync.md)                          |
| Complex message processing before ingestion             | Kafka external table + Table Stream | [Kafka External Table + Table Stream](pipe-kafka-table-stream.md) |

***

## I have a custom data source or need programmatic ingestion

| Scenario                                               | Approach                | Reference                                                        |
| ------------------------------------------------------ | ----------------------- | ---------------------------------------------------------------- |
| Java application bulk write                            | Java SDK BulkLoad       | [Java SDK Bulk Upload](use-java-sdk-upload-data-local.md)        |
| Java application real-time write (millisecond latency) | Java SDK RealtimeStream | [Java SDK Real-time Upload](use-java-sdk-realtime-uploaddata.md) |
| Python application bulk write                          | Python SDK              | [Python SDK Upload](use-python-sdk-upload-data.md)               |
| Python data processing tasks                           | Studio Python task      | [Python Task Development](python-task-dev.md)                    |
| Write from Flink                                       | Flink Connector         | [Flink Write to Lakehouse](flink-write-connector.md)             |
| Use open-source ETL tools                              | Airbyte / DataX         | [Ecosystem Integrations](ecosystem-all.md)                       |

***

## I'm migrating from another data warehouse

| Source                                 | Reference                                                                                |
| -------------------------------------- | ---------------------------------------------------------------------------------------- |
| Migrating from Snowflake               | [Snowflake ETL Pipeline Migration Guide](migrate-snowflake-realtime-etl-to-lakehouse.md) |
| Migrating from Spark data engineering  | [Spark Best Practices Migration Guide](spark-lakehouse-iceberg-rest.md)                  |
| Migrating from Alibaba Cloud Data Lake | [Alibaba Cloud Data Lake Migration Guide](ingesting-data-from-alibaba-cloud-datalake.md) |

***

## Not sure which approach to use?

Use this decision tree:

```
What is your data source?
├── Relational database (MySQL / PG / SQL Server)
│   ├── Need real-time sync → Studio multi-table real-time sync
│   └── Offline periodic sync → Studio offline sync task
├── Files (CSV / Parquet / JSON)
│   ├── One-time import → COPY INTO
│   └── Continuous auto-ingest → Pipe (object storage mode)
├── Kafka message stream
│   ├── Simple consume and ingest → Pipe (Kafka mode)
│   └── Complex processing → Kafka external table + Table Stream
└── Custom / programmatic ingestion → SDK or Python task
```

For a full comparison of all approaches, see: [A Comprehensive Guide to Ingesting Data into Singdata Lakehouse](a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md)
