# Open Source Projects

Singdata's open source organization on GitHub — [github.com/clickzetta](https://github.com/clickzetta) — maintains a series of open source projects and continuously submits contributions to upstream open source communities. Coverage spans AI Agent tooling, ecosystem connectors, data platform migration examples, and upstream community participation. This document organizes them by category.

## AI Agents and Command-Line Tools

**[clickzetta-skills](https://github.com/clickzetta/clickzetta-skills)**

The official AI Agent skills library for Singdata Lakehouse, designed for AI coding assistants such as Claude Code, Cursor, and Kiro. Packages best practices for Data Integration, data modeling, task development, operations governance, and other scenarios as reusable modules. This is the highest-starred project in the organization on GitHub.

**[cz-cli](https://github.com/clickzetta/cz-cli)**

An AI-Agent-friendly command-line tool and the recommended interface for Agents operating on the Lakehouse and Studio. Provides deterministic command interfaces that support sub-agents, CI/CD, and automation scenarios.

**[incremental-skills](https://github.com/clickzetta/incremental-skills)**

A general-purpose incremental computation skills library for AI Agent incremental data processing scenarios.

**[czcode](https://github.com/clickzetta/czcode)**

Singdata Lakehouse AI Agent — a dedicated AI coding assistant for data teams.

**[cz-tool](https://github.com/clickzetta/cz-tool)** — Command-line toolset for Singdata products.

**[goclickzetta](https://github.com/clickzetta/goclickzetta)** — Go SDK for connecting Go applications to the Lakehouse.

---

## Ecosystem Connectors and Adapters

**[clickzetta-jdbc-stress-tool](https://github.com/clickzetta/clickzetta-jdbc-stress-tool)**

A JDBC stress-testing tool for testing JDBC connection performance and concurrency for the Lakehouse.

**[dbt-clickzetta](https://github.com/clickzetta/dbt-clickzetta)**

The dbt adapter for Singdata Lakehouse, supporting direct operations on Lakehouse tables, Dynamic Tables, and Materialized Views within dbt projects.

**[sqlglot-clickzetta](https://github.com/clickzetta/sqlglot-clickzetta)**

A SQL parsing and transpilation tool (based on sqlglot) for syntax conversion between different SQL dialects. Useful in migration scenarios for automatically converting Snowflake, BigQuery, Databricks, and other platform-specific SQL syntax.

**[mindsdb-clickzetta](https://github.com/clickzetta/mindsdb-clickzetta)**

MindsDB integration for ML/LLM modeling and inference directly on Lakehouse data.

**[metabase-clickzetta](https://github.com/clickzetta/metabase-clickzetta)**

A Lakehouse-adapted version of Metabase — a direct-connection solution for the open source BI tool.

**[data-diff-clickzetta](https://github.com/clickzetta/data-diff-clickzetta)**

A cross-database table comparison tool for comparing data differences between Lakehouse tables or between a Lakehouse table and tables in other databases.

**[sql-formatter-clickzetta](https://github.com/clickzetta/sql-formatter-clickzetta)**

A SQL code formatting tool supporting multiple SQL dialects.

---

## Migration Example Projects

Singdata maintains a series of open source migration example projects. Each project includes both the original code (source platform) and the migrated Lakehouse code, and can be cloned and run directly.

### Migrating from Databricks

| Project | Description |
|------|------|
| [databricks2lakehouse-bootcamp](https://github.com/clickzetta/databricks2lakehouse-bootcamp) | Databricks Bootcamp → Lakehouse: three migration paths for 14 notebooks (ZettaPark / SQL / Studio DAG) |
| [databricks2lakehouse-jobs](https://github.com/clickzetta/databricks2lakehouse-jobs) | Databricks Jobs → Studio task DAG migration |
| [databricks2lakehouse-delta](https://github.com/clickzetta/databricks2lakehouse-delta) | Delta tables → Lakehouse: External Catalog federated queries + full migration paths |
| [databricks2lakehouse-governance](https://github.com/clickzetta/databricks2lakehouse-governance) | Unity Catalog → Lakehouse governance migration (RBAC, column-level masking) |
| [databricks2lakehouse-dlt-apparel](https://github.com/clickzetta/databricks2lakehouse-dlt-apparel) | Databricks DLT pipeline migration example (apparel retail Medallion architecture) |
| [dbt-databricks2lakehouse-blueprint](https://github.com/clickzetta/dbt-databricks2lakehouse-blueprint) | Data pipeline migration blueprint for dbt + Databricks → Lakehouse |

### Migrating from Snowflake

| Project | Description |
|------|------|
| [snowflake2lakehouse-data-engineering](https://github.com/clickzetta/snowflake2lakehouse-data-engineering) | Snowflake data engineering workflow migration |
| [snowflake2lakehouse-dynamic-tables](https://github.com/clickzetta/snowflake2lakehouse-dynamic-tables) | Snowflake Dynamic Tables → Lakehouse Dynamic Table migration (Bronze-Silver-Gold) |
| [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt) | Snowflake + dbt → Lakehouse + dbt migration |

### Migrating from Other Platforms

| Project | Description |
|------|------|
| [spark2lakehouse-formula1](https://github.com/clickzetta/spark2lakehouse-formula1) | PySpark → ZettaPark: Formula 1 data engineering pipeline migration |
| [spark2lakehouse-weblog](https://github.com/clickzetta/spark2lakehouse-weblog) | PySpark → ZettaPark: web log processing migration |
| [spark2lakehouse-medallion](https://github.com/clickzetta/spark2lakehouse-medallion) | Spark SQL → Lakehouse: Medallion architecture (Bronze/Silver/Gold) migration |
| [spark2cz](https://github.com/clickzetta/spark2cz) | Scala migration tool for Spark to Singdata |
| [bigquery2lakehouse-retail](https://github.com/clickzetta/bigquery2lakehouse-retail) | BigQuery + Airflow + dbt → Lakehouse + Studio migration (retail data pipeline) |
| [hive2lakehouse-ecommerce-events](https://github.com/clickzetta/hive2lakehouse-ecommerce-events) | Hive → Lakehouse migration (e-commerce clickstream data) |
| [maxcompute2lakehouse-ecommerce](https://github.com/clickzetta/maxcompute2lakehouse-ecommerce) | MaxCompute + DataWorks → Lakehouse + Studio migration (e-commerce ETL) |
| [pandas2lakehouse-retail](https://github.com/clickzetta/pandas2lakehouse-retail) | pandas → ZettaPark migration (UCI Online Retail, RFM + cohort analysis) |
| [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta) | dbt Jaffle Shop sandbox project — explore dbt + Lakehouse workflows using fictional sandwich-shop data |

---

## Upstream Community Contributions

The Singdata team not only maintains its own open source projects but also continuously submits code changes and feature enhancements to upstream communities. The following contributions are traceable from public PR records (all merged upstream).

### Core Infrastructure

**[Apache Iceberg C++](https://github.com/apache/iceberg-cpp)**

Apache Iceberg is the industry standard for open Lakehouse table formats. Singdata is a **core contributor to the Apache Iceberg C++ implementation** and has been deeply involved in developing the Iceberg C++ client SDK (primary contributors include `wgtmac`). Singdata Lakehouse was built on Iceberg from Day 1 — the team has a sustained code investment in the Iceberg open source ecosystem.

### AI Ecosystem and Agents

**[OpenClaw](https://github.com/openclaw/openclaw)**

OpenClaw is an open source AI assistant engine (the `openclaw` organization maintains 30+ companion tools). SingClaw is built on the OpenClaw core, with enhancements in memory, security, scenario support, and workspaces.

**[langgenius/dify](https://github.com/langgenius/dify) & [langgenius/dify-plugins](https://github.com/langgenius/dify-plugins)**

The Singdata team contributed code to Dify (an open source LLM application development platform), covering vector storage and file storage integrations related to the Lakehouse.

**[Datus-ai](https://github.com/Datus-ai) (Datus-agent / datus-db-adapters)**

The Singdata team contributed database adapters and Agent capability enhancements to Datus (a data engineering Agent).

**[mem0](https://github.com/clickzetta/mem0)**

A general-purpose AI Agent memory layer; the Singdata team participates in maintenance and capability enhancements.

### SQL Engines and Data Processing

**[tobymao/sqlglot](https://github.com/tobymao/sqlglot)**

The Singdata team contributed code to SQLGlot (a Python SQL parsing and transpilation engine) to enhance multi-dialect SQL compatibility and conversion (`clickzetta/sqlglot-clickzetta` is based on this project).

**[datafold/data-diff](https://github.com/datafold/data-diff)**

The Singdata team contributed code to Datafold's cross-database table comparison tool (`clickzetta/data-diff-clickzetta` is based on this project).

### Ecosystem Plugins

**[langgenius/dify](https://github.com/langgenius/dify)** — Open source LLM application development platform

The Singdata team submitted multiple merged contributions to Dify: Singdata Lakehouse vector database integration, Singdata plugin submission, multi-round workflow knowledge retrieval cache fix, and vector store stability improvements. These contributions let Dify users use Singdata Lakehouse directly as a vector and full-text search engine for RAG applications.

**[Datus-ai](https://github.com/Datus-ai)** — Data engineering Agent

The Singdata team submitted multiple merged contributions to Datus: Singdata database type support, Singdata Adapter (execute method and CLI compatibility), and general MCP tool orchestration architecture optimization. Singdata also maintains Datus agent and database adapters adapted for the Lakehouse, enabling the Datus Agent to operate on the Lakehouse via the MCP protocol.

**[datafold/data-diff](https://github.com/datafold/data-diff)** — Cross-database table comparison

The Singdata team contributed Singdata engine support to data-diff (`idling11`: Add support for Clickzetta engine), enabling data-diff to perform data consistency checks between Lakehouse tables and tables in other databases.

### Other

**[Rath-clickzetta](https://github.com/clickzetta/Rath-clickzetta)**

A next-generation automated data exploration and visualization platform; the Singdata team maintains the Lakehouse-adapted version.

**[clickzetta-sql-dashboard](https://github.com/clickzetta/clickzetta-sql-dashboard)**

A Streamlit-based Lakehouse SQL monitoring dashboard.

**[clickzetta-replay](https://github.com/clickzetta/clickzetta-replay)**

A SQL replay tool for reproducing and comparing query behavior in production environments.

## Related Documents

- [cz-cli Installation and Setup](setup_cz_cli.md)
- [cz-cli Agent Integration](cz-cli-agent.md)
- [dbt Integration Guide](eco_integration/dbt.md)
- [dbt Hands-On Series](dbt-practice-series.md)
- [Spark Connector](spark-connector-summary.md)
- [Ecosystem](ecosystem.md)
