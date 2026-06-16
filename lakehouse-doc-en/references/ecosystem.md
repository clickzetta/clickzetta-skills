# Ecosystem

Singdata Lakehouse is compatible with mainstream data integration, BI, AI, and development tools, and is deployed on seven public clouds including Alibaba Cloud, Tencent Cloud, and AWS. This document summarizes verified third-party tools and connection solutions organized by category.

If the tool you need is not on the list, that does not mean it is unsupported — Lakehouse provides standard access via JDBC, MySQL protocol, and Python/Java SDKs, and any tool compatible with these protocols can connect directly. If you want to develop a new connector or integration solution based on Lakehouse, feel free to contact our partner team.

## Cloud Platforms (CSP)

Lakehouse is deployed on seven clouds: Alibaba Cloud, Tencent Cloud, AWS, GCP, Huawei Cloud, Baidu AI Cloud, and Volcengine. Alibaba Cloud, Tencent Cloud, and AWS provide complete dedicated documentation (including storage connections, private network connections, and permission configuration); the configuration approach is consistent across all other cloud platforms. BYOS (Bring Your Own Storage) deployment is also supported — data is stored under the user's own cloud account and does not pass through the Singdata platform. See [Supported Cloud Platforms](supported-cloud-platforms.md) and [Private Storage Overview](byos_general.md) for details.

***

## Data Integration

The following data integration tools are compatible with Lakehouse, covering offline batch, real-time CDC, message streaming, and log collection scenarios. Lakehouse also supports [50+ data sources](data-sources.md) (MySQL, Oracle, PostgreSQL, MongoDB, Hive, MaxCompute, etc.) via Studio Data Sync for direct access without third-party tools:

| Tool         | Connection         | Description                                                   | Reference                                                    |
| ------------ | ------------------ | ------------------------------------------------------------- | ------------------------------------------------------------ |
| Apache Kafka | Kafka Connector    | Real-time message stream writing to Lakehouse                 | [Kafka Data Source](DataSource_Kafka.md)                     |
| AutoMQ       | Kafka Protocol     | Next-generation message queue, compatible with Kafka protocol | [AutoMQ Data Source](DataSource_AutoMQ.md)                   |
| Airbyte      | JDBC               | Open-source ELT platform with a rich connector ecosystem      | [Airbyte Integration Guide](airbyte.md)                      |
| DataX        | Plugin-based       | Alibaba open-source tool, suitable for batch data sync        | [DataX Integration Guide](eco_integration/datax.md)          |
| Apache Flink | Flink Connector    | Stream processing engine for real-time writes to Lakehouse    | [Flink Connector](flink-write-connector.md)                  |
| Apache Spark | Spark Connector    | Large-scale data reads and writes for Lakehouse tables        | [Spark Connector](spark-connector-summary.md)                |
| Logstash     | Logstash Connector | Import log data into Lakehouse                                | [Logstash Integration Guide](Logstash.md)                    |
| Bluepipe     | Native integration | Real-time CDC sync from Oracle to Lakehouse                   | [Bluepipe Sync Guide](bluepipe-oracle-lakehouse-datasync.md) |

***

## BI and Visualization

The following BI tools are compatible with Lakehouse. Any BI tool supporting JDBC, ODBC, or MySQL protocol can connect directly and is not limited to the list below:

| Tool            | Connection     | Description                                                      | Reference                                                        |
| --------------- | -------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| FineBI          | JDBC / MySQL   | Leading domestic BI tool                                         | [JDBC Connection](FineBI.md) · [MySQL Protocol](finebi-mysql.md) |
| Tableau         | JDBC           | Suitable for complex visualizations and exploratory analysis     | [Tableau Connection Guide](tableau-connect-to-lakehouse.md)      |
| Power BI        | MySQL Protocol | Connect via MySQL protocol                                       | [Power BI Connection Guide](PowerBI.md)                          |
| Apache Superset | SQLAlchemy     | Open-source, suitable for self-service analytics                 | [Superset Connection Guide](eco_integration/superset.md)         |
| Metabase        | JDBC           | Open-source, easy to deploy, suitable for small and medium teams | [Metabase Connection Guide](metabase.md)                         |
| Apache Zeppelin | JDBC           | Notebook-style data exploration                                  | [Zeppelin Connection Guide](eco_integration/Zeppelin.md)         |
| Rath            | JDBC           | Open-source intelligent analytics with automatic insight support | [Rath Connection Guide](eco_integration/rath.md)                 |
| Streamlit       | Python SDK     | Rapidly build data apps for data science teams                   | [Streamlit Connection Guide](eco_integration/streamlit.md)       |

***

## Transformation and Compute Engines

The following data transformation tools and compute engines are compatible with Lakehouse:

| Tool         | Connection             | Description                                                              | Reference                                       |
| ------------ | ---------------------- | ------------------------------------------------------------------------ | ----------------------------------------------- |
| dbt          | dbt-clickzetta adapter | Data modeling and transformation, supports Dynamic Table materialization | [dbt Integration Guide](eco_integration/dbt.md) |
| Apache Spark | Spark Connector        | Large-scale batch processing and machine learning                        | [Spark Connector](spark-connector-summary.md)   |
| Apache Flink | Flink Connector        | Real-time stream processing                                              | [Flink Connector](flink-write-connector.md)     |

The **dbt documentation series** covers all scenarios from quick start to migration practice: jaffle-shop experience, Snowflake/BigQuery migration, incremental processing, real-time pipelines, and data quality testing. See [DBT Practice Series](dbt-practice-series.md).

***

## AI and Machine Learning

The following AI frameworks and platforms are compatible with Lakehouse, supporting vector storage, RAG applications, and AI workflow scenarios:

| Tool            | Integration      | Description                                      | Reference                                                                  |
| --------------- | ---------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| LangChain       | Python SDK       | Vector storage and RAG application development   | [LangChain Integration](langchain_integration.md)                          |
| LlamaIndex      | Python SDK       | Data indexing and retrieval                      | [LlamaIndex Integration](llama-index.md)                                   |
| Dify            | MCP Server / SDK | Vector database + file storage                   | [Dify Integration Overview](dify_yunqilakehouse_integration_overview.md)   |
| N8N             | MCP Server       | Unified AI workflows                             | [N8N Integration](N8N_AI_Workflow_Integration.md)                          |
| MindsDB         | JDBC             | ML/LLM modeling and prediction on Lakehouse data | [MindsDB Integration](JDBC_MindsDB_ML_LLM.md)                              |
| Datus           | MCP Server       | Data engineering agent                           | [Datus Integration](Datus_Lakehouse_Integrated_Guide.md)                   |
| Zilliz          | Joint solution   | Vector database joint solution                   | [Zilliz Joint Solution](lakehouse-zilliz-make-data-ready-for-bi-and-ai.md) |
| Unstructured.io | SDK              | Unstructured document parsing and vectorization  | [Unstructured.io Integration](unstructured-io.md)                          |

Lakehouse also provides an [MCP Server](LakehouseMCPServer.md) that can be called by any AI Agent supporting the MCP protocol.

***

## Programmatic Interfaces

Lakehouse provides the following native programming interfaces and SDKs:

| Interface      | Language   | Description                                                 | Reference                                                  |
| -------------- | ---------- | ----------------------------------------------------------- | ---------------------------------------------------------- |
| JDBC Driver    | Java / JVM | Standard JDBC interface, compatible with all JVM ecosystems | [JDBC Driver](JDBC-Driver.md)                              |
| MySQL Protocol | All        | No client dependency, compatible with MySQL ecosystem       | [MySQL Protocol Connection](use-mysql-client.md)           |
| Python SDK     | Python     | PEP 249 compatible, supports batch/real-time writes         | [Python SDK](python_reference/python-sdk-summary.md)       |
| Java SDK       | Java       | Supports BulkLoad and real-time stream writes               | [Java SDK Batch Upload](use-java-sdk-upload-data-local.md) |
| SQLAlchemy     | Python     | Standard Python ORM / SQL toolkit                           | [SQLAlchemy Connection](sqlalchemy.md)                     |
| cz-cli         | Shell      | Command-line client: SQL + Studio Tasks + AI Agent          | [cz-cli Guide](cz-cli.md)                                  |

***

## SQL Clients and Database Management Tools

These tools connect via JDBC or MySQL protocol, compatible with standard SQL operations:

| Tool            | Connection     | Description                                                                                            | Reference                                                                       |
| --------------- | -------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| DBeaver         | JDBC           | Open-source and free, community edition is sufficient, suitable for daily queries and data exploration | [DBeaver Connection Guide](eco_integration/dbeaver-lakehouse.md)                |
| DataGrip        | JDBC           | JetBrains product with strong code completion and SQL analysis                                         | [DataGrip Connection Guide](eco_integration/datagrip-lakehouse.md)              |
| SQL Workbench/J | JDBC           | Lightweight, basic SQL execution                                                                       | [SQL Workbench/J Connection Guide](eco_integration/sqlworkbench-j-lakehouse.md) |
| Navicat         | MySQL Protocol | Visual management with intuitive operations                                                            | [Navicat Connection Guide](navicat-mysql.md)                                    |

***

## Data Lake Formats

Lakehouse is **natively based on Apache Iceberg** — tables are stored in Iceberg format, supporting time travel, partition evolution, schema evolution, and cross-engine access. Delta Lake and Hudi formats are also supported via external tables:

| Format         | Relationship   | Description                                                     | Reference                                                    |
| -------------- | -------------- | --------------------------------------------------------------- | ------------------------------------------------------------ |
| Apache Iceberg | Native format  | Underlying format for all Lakehouse tables, cross-engine access | [Spark + Iceberg Analytics](spark-lakehouse-iceberg-rest.md) |
| Delta Lake     | External table | Open table format from the Databricks ecosystem                 | [Delta Lake External Table](delta-lake.md)                   |
| Apache Hudi    | External table | Open table format optimized for streaming writes                | [Hudi External Table](external-hudi-table.md)                |

**Federated Queries**: Query Iceberg tables in Hive, Databricks, and Snowflake OpenCatalog directly via External Catalog, without data migration. See [Federated Query](federation-query.md).

***

## Modern Data Stack

The following solution combinations show how to build a complete data platform using Lakehouse and ecosystem tools:

| Solution           | Toolchain                            | Reference                                                                   |
| ------------------ | ------------------------------------ | --------------------------------------------------------------------------- |
| ELT-oriented       | Airbyte → Lakehouse → dbt → Metabase | [ELT Modern Data Stack](ELTModernDataStack.md)                              |
| Analytics-oriented | Lakehouse ← dbt → Superset           | [Analytics Modern Data Stack](analytics-modern-data-stack.md)               |
| BI + AI            | Lakehouse + Zilliz                   | [BI + AI Joint Solution](lakehouse-zilliz-make-data-ready-for-bi-and-ai.md) |

***

> 💡 **Tip**: The list above contains verified and compatible third-party tools. Lakehouse provides standard access via JDBC, MySQL protocol, and Python/Java SDKs — any tool compatible with these protocols can be used directly. If the tool you need is not on the list, it can still connect normally.

## Quick Navigation

* **Understand product concepts**: [Key Concepts](key-concepts.md) · [Incremental Computing](incremental-computing.md)
* **Start ingesting data**: [Data Integration](#data-integration) · [50+ Data Source Support](data-sources.md)
* **Connect BI tools**: [BI and Visualization](#bi-and-visualization)
* **Data modeling**: [dbt Integration Guide](eco_integration/dbt.md) · [DBT Practice Series](dbt-practice-series.md)
* **Programmatic access**: [Programmatic Interfaces](#programmatic-interfaces)
* **AI application development**: [AI and Machine Learning](#ai-and-machine-learning)

^
