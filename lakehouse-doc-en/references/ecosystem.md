# Ecosystem

Singdata Lakehouse integrates with mainstream data integration, BI, AI, and development tools, and is available on seven public clouds, including AWS, Alibaba Cloud, and Tencent Cloud. This page summarizes verified third-party tools and integration options by category.

If the tool you need is not listed, it may still be supported. Lakehouse provides standard access through JDBC, the MySQL protocol, and Python/Java SDKs. Any tool compatible with these protocols can connect directly. If you want to build a new connector or integration for Lakehouse, contact the Singdata partner team.

The following diagram shows where Singdata Lakehouse fits in an enterprise AI and data stack. Data sources are on the left, model providers are on the right, consumers such as AI Agents, business users, and application systems are at the top, cloud infrastructure is at the bottom, and the Singdata product matrix is in the middle.

![](.topwrite/assets/anim-41-ai-data-stack.svg)

## Cloud Platforms (CSP)

Lakehouse is deployed on seven clouds: AWS, Alibaba Cloud, Tencent Cloud, GCP, Huawei Cloud, Baidu AI Cloud, and Volcengine. AWS, Alibaba Cloud, and Tencent Cloud provide dedicated documentation for storage connections, private network connections, and permission configuration. The configuration approach is consistent across the other cloud platforms. BYOS (Bring Your Own Storage) deployment is also supported: data is stored in your own cloud account and does not pass through the Singdata platform. See [Supported Cloud Platforms](supported-cloud-platforms.md) and [Private Storage Overview](byos_general.md) for details.

***

## Data Integration

The following data integration tools work with Lakehouse and cover batch sync, real-time CDC, message streaming, and log collection. Lakehouse also supports [50+ data sources](data-sources.md), including MySQL, Oracle, PostgreSQL, MongoDB, Hive, and MaxCompute, through Studio Data Sync without third-party tools:

| Tool         | Connection         | Description                                                   | Reference                                                    |
| ------------ | ------------------ | ------------------------------------------------------------- | ------------------------------------------------------------ |
| Apache Kafka | Kafka Connector    | Real-time message stream writing to Lakehouse                 | [Kafka Data Source](datasource_kafka.md)                     |
| AutoMQ       | Kafka Protocol     | Next-generation message queue, compatible with Kafka protocol | [AutoMQ Data Source](datasource_automq.md)                   |
| Airbyte      | JDBC               | Open-source ELT platform with a rich connector ecosystem      | [Airbyte Integration Guide](airbyte.md)                      |
| DataX        | Plugin-based       | Alibaba open-source tool, suitable for batch data sync        | [DataX Integration Guide](eco_integration/datax.md)          |
| Apache Flink | Flink Connector    | Stream processing engine for real-time writes to Lakehouse    | [Flink Connector](flink-write-connector.md)                  |
| Apache Spark | Spark Connector    | Large-scale data reads and writes for Lakehouse tables        | [Spark Connector](spark-connector-summary.md)                |
| Logstash     | Logstash Connector | Import log data into Lakehouse                                | [Logstash Integration Guide](logstash.md)                    |
| Bluepipe     | Native integration | Real-time CDC sync from Oracle to Lakehouse                   | [Bluepipe Sync Guide](comprehensive_guide_to_ingesting_3rd_tools.md) |

***

## BI and Visualization

The following BI tools are compatible with Lakehouse. Any BI tool supporting JDBC, ODBC, or MySQL protocol can connect directly and is not limited to the list below:

| Tool            | Connection     | Description                                                      | Reference                                                        |
| --------------- | -------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| FineBI          | JDBC / MySQL   | China-based BI platform                                          | [JDBC Connection](finebi.md) · [MySQL Protocol](finebi-mysql.md) |
| Tableau         | JDBC           | Suitable for complex visualizations and exploratory analysis     | [Tableau Connection Guide](tableau-connect-to-lakehouse.md)      |
| Power BI        | MySQL Protocol | Connect via MySQL protocol                                       | [Power BI Connection Guide](powerbi.md)                          |
| Apache Superset | SQLAlchemy     | Open-source, suitable for self-service analytics                 | [Superset Connection Guide](eco_integration/superset.md)         |
| Metabase        | JDBC           | Open-source, easy to deploy, suitable for small and medium teams | [Metabase Connection Guide](metabase.md)                         |
| Apache Zeppelin | JDBC           | Notebook-style data exploration                                  | [Zeppelin Connection Guide](eco_integration/zeppelin.md)         |
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

The following AI frameworks and platforms work with Lakehouse for vector storage, RAG applications, and AI workflows:

| Tool            | Integration      | Description                                      | Reference                                                                  |
| --------------- | ---------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| LangChain       | Python SDK       | Vector storage and RAG application development   | [LangChain Integration](langchain_integration.md)                          |
| LlamaIndex      | Python SDK       | Data indexing and retrieval                      | [LlamaIndex Integration](llama-index.md)                                   |
| Dify            | MCP Server / SDK | Vector database + file storage                   | [Dify Integration Overview](dify_yunqilakehouse_integration_overview.md)   |
| n8n             | MCP Server       | Unified AI workflows                             | [n8n Integration](n8n_ai_workflow_integration.md)                          |
| MindsDB         | JDBC             | ML/LLM modeling and prediction on Lakehouse data | [MindsDB Integration](jdbc_mindsdb_ml_llm.md)                              |
| Datus           | MCP Server       | Data engineering agent                           | [Datus Integration](datus_lakehouse_integrated_guide.md)                   |
| Zilliz          | Joint solution   | Vector database joint solution                   | [Zilliz Joint Solution](lakehouse-zilliz-make-data-ready-for-bi-and-ai.md) |
| Unstructured.io | SDK              | Unstructured document parsing and vectorization  | [Unstructured.io Integration](unstructured-io.md)                          |

Lakehouse also provides an [MCP Server](lakehousemcpserver.md) that can be called by any AI Agent that supports the MCP protocol.

***

## LLM Providers

Singdata AI Gateway provides unified access to mainstream LLM providers, including model routing, API key management, and usage tracking. After you connect through AI Gateway, products that call AI capabilities, such as Data Engineering Agent, Data Analytics Agent, and Lakehouse AI Functions, do not need separate model connections.

| Provider         | Description                                         |
| ---------------- | --------------------------------------------------- |
| OpenAI           | GPT-4o, o1, and Embeddings                          |
| Anthropic        | Claude 3.5 / 4 series                               |
| Azure OpenAI     | Enterprise deployment with tenant-isolated data     |
| Google Vertex AI | Gemini, PaLM, and Embeddings                        |
| Alibaba Cloud Bailian | Qwen series for China-compliant deployments     |
| Volcengine       | Doubao series for China-compliant deployments       |
| Self-hosted      | Private deployments such as Ollama and vLLM         |

AI Gateway acts as a unified enterprise LLM egress layer. You can switch model providers without changing application code. See [AI Gateway](aigateway.md).

***

## AI Agents

The following Agents can operate Lakehouse and Studio directly through cz-cli or MCP Server for data engineering and data analysis tasks.

**cz-cli is the recommended integration path** because it provides a deterministic command interface for Sub-Agents, CI/CD, and automation. Any AI coding Agent that supports shell tool calls, including the examples below, can use cz-cli to operate Lakehouse and Studio.

### Built-in Agents

| Agent | Description | Reference |
| ----- | ----------- | --------- |
| Data Engineering Agent | Build and operate data pipelines, task schedules, and DAG orchestration through natural language | [Data Engineering Agent](dataagent.md) |
| Data Analytics Agent | Query, analyze, forecast, and build dashboards through natural language | [Data Analytics Agent](datagpt_introduction.md) |

### AI Coding Agents Integrated via cz-cli

The following Agents can operate Lakehouse and Studio through cz-cli:

| Agent | Description |
| ----- | ----------- |
| OpenClaw | Supports cz-cli tool calls for data engineering automation |
| Hermes Agent | Supports cz-cli tool calls for Lakehouse data pipeline management |
| Claude Code (Anthropic) | Supports cz-cli tool calls for code generation and data engineering |
| Kiro (Amazon) | Supports cz-cli tool calls for data engineering and analysis tasks |
| Kilo Code | Supports cz-cli tool calls for data pipeline development |
| Codex (OpenAI) | Supports cz-cli tool calls for SQL generation and data engineering |

Any AI Agent that supports shell tool calls can integrate through cz-cli. See [cz-cli Agent Integration](cz-cli-agent.md).

### AI Platforms Integrated via MCP Server

| Platform | Description | Reference |
| -------- | ----------- | --------- |
| Dify | AI workflow platform that calls Lakehouse data and vector capabilities | [Dify Integration](dify_integrated_with_lakehousemcpserver.md) |
| n8n | Automation workflow platform for AI and data workflows | [n8n Integration](n8n_integrated_with_lakehousemcpserver.md) |
| Datus | Data engineering agent | [Datus Integration](datus_lakehouse_integrated_guide.md) |
| Other MCP-compatible Agents | Any Agent that supports the MCP protocol can connect | [MCP Server](lakehousemcpserver.md) |

***

## Programmatic Interfaces

Lakehouse provides the following native programming interfaces and SDKs:

| Interface      | Language   | Description                                                 | Reference                                                  |
| -------------- | ---------- | ----------------------------------------------------------- | ---------------------------------------------------------- |
| JDBC Driver    | Java / JVM | Standard JDBC interface, compatible with all JVM ecosystems | [JDBC Driver](jdbc-driver.md)                              |
| MySQL Protocol | All        | No client dependency, compatible with MySQL ecosystem       | [MySQL Protocol Connection](use-mysql-client.md)           |
| Python SDK     | Python     | PEP 249 compatible, supports batch/real-time writes         | [Python SDK](python_reference/python-sdk-summary.md)       |
| Java SDK       | Java       | Supports BulkLoad and real-time stream writes               | [Java SDK Batch Upload](use-java-sdk-upload-data-local.md) |
| SQLAlchemy     | Python     | Standard Python ORM / SQL toolkit                           | [SQLAlchemy Connection](sqlalchemy.md)                     |
| ZettaPark      | Python     | DataFrame API similar to pandas and PySpark; translates Python operations into distributed SQL execution | [ZettaPark Guide](lakehousepython-zettapark.md) |
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
| ELT-oriented       | Airbyte → Lakehouse → dbt → Metabase | [ELT Modern Data Stack](eltmoderndatastack.md)                              |
| Analytics-oriented | Lakehouse ← dbt → Superset           | [Analytics Modern Data Stack](analytics-modern-data-stack.md)               |
| BI + AI            | Lakehouse + Zilliz                   | [BI + AI Joint Solution](lakehouse-zilliz-make-data-ready-for-bi-and-ai.md) |

***

> **Tip**: The list above contains verified compatible third-party tools. Lakehouse provides standard access through JDBC, the MySQL protocol, and Python/Java SDKs. Any tool compatible with these protocols can connect directly. If the tool you need is not listed, it may still work normally.

## Quick Navigation

* **Understand product concepts**: [Key Concepts](key-concepts.md) · [Incremental Computing](incremental-computing.md)
* **Start ingesting data**: [Data Integration](#data-integration) · [50+ Data Source Support](data-sources.md)
* **Connect BI tools**: [BI and Visualization](#bi-and-visualization)
* **Data modeling**: [dbt Integration Guide](eco_integration/dbt.md) · [DBT Practice Series](dbt-practice-series.md)
* **Programmatic access**: [Programmatic Interfaces](#programmatic-interfaces)
* **AI application development**: [AI and Machine Learning](#ai-and-machine-learning)
