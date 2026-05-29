# Streaming Data Pipeline Overview

## Incremental Computing Overview

A streaming data pipeline is a set of tasks that continuously collects, processes, and transforms real-time data to produce result data that meets business timeliness requirements. Streaming data processing is the foundation for analysts and business applications to perform real-time insights and real-time decision-making.

Unlike periodic offline processing (batch data pipeline), a streaming data pipeline continuously produces real-time updated results by orchestrating real-time data ingestion tasks and SQL tasks that support incremental data processing. Incremental processing techniques are used throughout to improve efficiency and reduce costs.

The overall processing flow for a Singdata Lakehouse streaming data pipeline is shown below:

![](.topwrite/assets/image_1709520998068.png)

The product features of streaming data processing include:

| Feature | Description |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Real-time Data Loading | **Real-time Data Loading Service**: Provides a Streaming API via SDK/Connector, supporting real-time append/update writes with second-level visibility, as a system-managed service. You can use the SDK or Flink Connector to write data to the target table. **Studio Data Integration Service**: A built-in data integration tool that supports real-time extraction from multiple real-time data sources (such as Kafka, database CDC, etc.) and writes to the Lakehouse target table in real time via the Streaming API. |
| Incremental Data Processing | **Dynamic Table**: Declaratively defines data processing logic through dynamic tables, supporting any SQL syntax and operators. The system automatically reads incremental changes from the base table and adaptively optimizes processing efficiency using incremental or full-refresh algorithms. You can create one or more dynamic tables with scheduling policies, and the system automatically identifies dependencies and continuously schedules execution, greatly simplifying real-time data processing development. Note: The minimum supported scheduling interval is currently 1 minute. |
| Change Data Capture | **Table Stream**: Table Stream is a built-in SQL object type. A Table Stream is created on top of a specified table and records the data change (CDC) information for that table. Table Stream supports SQL queries to retrieve change records between two specified data versions — for example, changes from 5 minutes ago to the present. Through Table Stream, downstream SQL ETL jobs can easily read and process table change data, or synchronize change results to external systems. |
| Continuous Scheduling | The system provides two scheduling modes: **Dynamic Table self-defined scheduling cycle**: When defining via materialized view DDL, you can set the scheduling cycle using the INTERVAL keyword. **Studio task scheduling**: Create SQL tasks in the Web IDE and set the task scheduling cycle. This mode supports scheduling both dynamic tables and SQL ETL jobs that use Table Stream. Note: Using the Studio scheduling system provides better task execution observability and operational alerting capabilities. |

---

## Next Steps

Choose the ingestion and processing approach that matches your data source and scenario:

**Data Ingestion**

| Data Source | Approach | Documentation |
|--------|------|------|
| Database CDC (MySQL / PG / Oracle, etc.) | Studio real-time sync task | [Real-time Sync Task](realtime_sync.md) |
| Full database migration | Studio multi-table real-time sync | [Multi-table Real-time Sync](multitable_realtime_sync.md) |
| Kafka / AutoMQ message streams | Kafka Pipe or Studio Kafka sync | [Pipe Continuous Ingestion](pipe-introduction.md) |
| OSS / S3 / COS files | Pipe | [Pipe Continuous Ingestion](pipe-introduction.md) |

**Incremental Data Processing**

- [Dynamic Table](dynamic-table.md) — Declaratively define transformation logic; the system automatically refreshes incrementally
- [Table Stream](table-stream-title.md) — Capture incremental changes on a table to drive downstream CDC consumption
- [Studio Workflow](composite_task.md) — Orchestrate multiple tasks into a DAG for unified scheduling and monitoring

**End-to-End Examples**

- [Real-time Data Pipeline: Kafka → Lakehouse → Real-time Analytics](realtime_sync_and_analysis_practice.md)
- [Build a Streaming Data Pipeline with Dynamic Tables](streaming_pipeline_with_dynamic_table.md)
