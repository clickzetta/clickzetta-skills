# Overview

Singdata Lakehouse is a next-generation cloud lakehouse independently developed by Singdata Technology. Built on an incremental computation engine, it delivers up to 10× performance improvement over traditional open-source architectures (such as Spark), enabling full-chain, low-cost, real-time processing of massive data. The platform supports integration, storage, and computation of all data types, providing solid data infrastructure for AI innovation and helping enterprises upgrade from traditional Spark architectures to the AI era.

For enterprises with existing data lakes (OSS / S3 / COS), Singdata Lakehouse can directly mount existing object storage and federate queries over Hive, Iceberg, Delta Lake, and other formats via External Catalog — no data migration required, with high-performance SQL analytics immediately available. This is the lowest-cost path from data lake to lakehouse.

Supports seven global clouds, already live in multiple Asia-Pacific regions, and supports private deployment. Infrastructure costs reduced to 1/5–1/3 of traditional solutions, with near-zero operations overhead.

<table style="width:100%;">
<tr>
<td style="width:25%; vertical-align:top; overflow-wrap:break-word;"><strong>Migrating from Spark / Databricks</strong><br>
<small><a href="tutorial_migration.md">Migration Guide</a> · <a href="migrate-spark-data-engineering-best-practices-to-lakehouse.md">Migration Best Practices</a> · <a href="sql-reference.md">SQL Syntax Comparison</a> · <a href="spark-connector-summary.md">Spark Connector</a> · <a href="benchmark_guide.md">Performance Testing</a></small></td>
<td style="width:25%; vertical-align:top; overflow-wrap:break-word;"><strong>Lake Acceleration (existing data lake)</strong><br>
<small><a href="lakehouse-acceleration-guide.md">In-Place Lake Acceleration Guide</a> · <a href="external-catalog-summary.md">External Catalog Federation</a> · <a href="external-table-guide.md">External Tables</a> · <a href="external_volume.md">Object Storage Mount</a> · <a href="benchmark_guide.md">Performance Testing</a></small></td>
<td style="width:25%; vertical-align:top; overflow-wrap:break-word;"><strong>AI Data Infrastructure</strong><br>
<small><a href="LakehouseAI-overview.md">Lakehouse AI Overview</a> · <a href="server-data-for-ai.md">AI Data Readiness</a> · <a href="vector_search_ai.md">Vector Search</a> · <a href="AIGateway.md">AI Gateway</a> · <a href="datagpt_introduction.md">Data Analytics Agent</a></small></td>
<td style="width:25%; vertical-align:top; overflow-wrap:break-word;"><strong>Cloud Platforms and Deployment</strong><br>
<small><a href="Supported-Cloud-Platforms.md">Supported Cloud Platforms and Regions</a> · <a href="pricing.md">Pricing and Billing</a></small></td>
</tr>
</table>

---

## First Time Here?

<table style="width:100%; table-layout:auto;">
<tr>
<td style="vertical-align:top; text-align:center; padding:12px; overflow-wrap:break-word;">
<strong>① Set Up Your Account</strong><br>
<small>5 minutes</small><br><br>
Register an account, activate a service instance, complete initialization<br><br>
<a href="logging-in.md">Get Started →</a>
</td>
<td style="vertical-align:top; text-align:center; padding:12px; overflow-wrap:break-word;">
<strong>② Quick Start Experience</strong><br>
<small>30 minutes</small><br><br>
Run through data ingestion, SQL queries, and Dynamic Table incremental computation<br><br>
<a href="lakehouse-quick-experience_guide.md">Start Experience →</a>
</td>
<td style="vertical-align:top; text-align:center; padding:12px; overflow-wrap:break-word;">
<strong>③ Go Deeper by Role</strong><br>
<small>As needed</small><br><br>
Dedicated paths for data engineers, analysts, AI engineers, and administrators<br><br>
<a href="tutorials.md">Choose Your Path →</a>
</td>
</tr>
</table>

---

## Who Am I, What Do I Want to Do

<table style="width:100%;">
<tr>
<td style="width:22%; vertical-align:top; overflow-wrap:break-word;"><strong>Data Integration / Data Sync</strong><br><small>Data ingestion, CDC sync, file import, streaming writes</small></td>
<td style="vertical-align:top; overflow-wrap:break-word;">

[Studio Data Integration](data-integration.md) (visual configuration for 40+ data sources) · [Real-time Sync Tasks](realtime_sync.md) (full-database CDC for MySQL / PG / Oracle) · [Batch Sync Tasks](batch_sync.md) (scheduled batch sync) · [Pipe Continuous Ingestion](pipe-introduction.md) (auto-write from object storage / Kafka) · [COPY INTO](copy-into-table.md) (one-time file import) · [Complete Data Ingestion Guide](a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md)

</td>
</tr>
<tr>
<td style="width:22%; vertical-align:top; overflow-wrap:break-word;"><strong>Data Engineer</strong><br><small>Build data pipelines, ETL processing, manage data warehouse layers</small></td>
<td style="vertical-align:top; overflow-wrap:break-word;">

[Dynamic Table Incremental Computation](incremental-computing.md) · [Dynamic Table Overview](dynamic_table_summary.md) · [Real-time Data Pipeline](streaming_data_pipeline_overview.md) · [Studio Task Development and Scheduling](task-develop.md) · [Task Parameters](task_param.md) · [CREATE TABLE Syntax Reference](create-table-ddl.md) · [SQL Syntax Reference](sql-reference.md) · [COPY INTO](copy-into-table.md) · [cz-cli Command-Line Tool](setup_cz_cli.md) · [TPC-DS Performance Testing](tpcds-benchmark.md)

</td>
</tr>
<tr>
<td style="width:22%; vertical-align:top; overflow-wrap:break-word;"><strong>Data Analyst</strong><br><small>SQL queries, BI connections, ad-hoc analysis</small></td>
<td style="vertical-align:top; overflow-wrap:break-word;">

[Run Your First SQL Query](quick_start_sql_query.md) · [Connect BI Tools](tutorial_connect_to_lakehouse.md) · [Data Analytics Agent (natural language queries)](datagpt_introduction.md) · [Semantic View](semantic-view-overview.md) · [Pricing and Billing](pricing.md) · [SSB Performance Testing](ssb-benchmark.md) · [TPC-H Performance Testing](tpch-benchmark.md)

</td>
</tr>
<tr>
<td style="width:22%; vertical-align:top; overflow-wrap:break-word;"><strong>AI / ML Engineer</strong><br><small>Vector search, RAG, AI functions, model invocation</small></td>
<td style="vertical-align:top; overflow-wrap:break-word;">

[AI Data Readiness](server-data-for-ai.md) · [Vector Search](vector_search_ai.md) · [AI Functions (AI\_COMPLETE / AI\_EMBEDDING)](ai_function_in_sql.md) · [AI Gateway](aigateway.md) · [Python SDK (SQL interface)](python_reference/connector.md) · [ZettaPark (DataFrame API)](lakehousepython-zettapark.md)

</td>
</tr>
<tr>
<td style="width:22%; vertical-align:top; overflow-wrap:break-word;"><strong>Platform Administrator</strong><br><small>User management, permission configuration, compute clusters, cost control</small></td>
<td style="vertical-align:top; overflow-wrap:break-word;">

[Account and Service Instance Setup](logging-in.md) · [User and Permission Management](authority-management.md) · [Compute Cluster Management](virtual-cluster.md) · [Pricing and Billing](pricing.md)

</td>
</tr>
<tr>
<td style="width:22%; vertical-align:top; overflow-wrap:break-word;"><strong>AI Agent / Automation</strong><br><small>Deterministic interface calls, semantic layer queries, automated data pipelines</small></td>
<td style="vertical-align:top; overflow-wrap:break-word;">

[cz-cli Command-Line Tool](setup_cz_cli.md) (deterministic interface, ideal for Agent calls) · [Semantic View](semantic-view-overview.md) (business semantic layer, natural-language friendly) · [Python SDK (SQL interface)](python_reference/connector.md) · [ZettaPark (DataFrame API)](lakehousepython-zettapark.md) · [Data Analytics Agent](datagpt_introduction.md)

</td>
</tr>
</table>

---

## Core Capabilities

<table style="width:100%; table-layout:auto;">
<tr>
<td style="width:50%; vertical-align:top; padding:0 16px 16px 16px; overflow-wrap:break-word;">

**Data Ingestion**

40+ data sources out of the box: full-database CDC real-time sync for MySQL / PG / Oracle, Kafka streaming writes, continuous import from OSS / S3 / COS files, one-time batch import via COPY INTO.

[Data Ingestion Guide](a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md) · [Studio Data Integration](data-integration.md) · [Pipe](pipe-introduction.md) · [COPY INTO](copy-into-table.md)

</td>
<td style="width:50%; vertical-align:top; padding:0 0 16px 16px; overflow-wrap:break-word;">

**Lakehouse Unification**

Existing data lakes (OSS / S3 / COS) require no migration — mount existing object storage directly and federate queries over Hive, Iceberg, Delta Lake formats via External Catalog for high-performance SQL analytics.

[External Catalog](external-catalog-summary.md) · [External Volume](external_volume.md) · [Lake Acceleration Guide](lakehouse-acceleration-guide.md)

</td>
</tr>
<tr>
<td style="width:50%; vertical-align:top; padding:0 16px 16px 16px; overflow-wrap:break-word;">

**Incremental Computation**

Define transformation logic with standard SQL. Dynamic Table automatically detects upstream changes and incrementally refreshes, replacing manual scheduling scripts to build low-latency data pipelines.

[Incremental Computation Mechanism](incremental-computing.md) · [Dynamic Table Overview](dynamic_table_summary.md) · [Real-time Data Pipeline](streaming_data_pipeline_overview.md)

</td>
<td style="width:50%; vertical-align:top; padding:0 0 16px 16px; overflow-wrap:break-word;">

**High-Performance SQL Analytics**

Vectorized execution engine. Leading industry performance on TPC-DS / TPC-H / SSB benchmarks. Supports OLAP multi-dimensional analysis and ad-hoc queries — up to 10× faster than traditional Spark architectures.

[Performance Testing](benchmark_guide.md) · [SQL Usage Guide](considerations-for-using-sql.md) · [TPC-H Sample Experience](get-started-with-sample-data.md)

</td>
</tr>
<tr>
<td style="width:50%; vertical-align:top; padding:0 16px 0 16px; overflow-wrap:break-word;">

**AI-Native**

Vector indexes, full-text search, AI Functions (AI\_COMPLETE / AI\_EMBEDDING), and Semantic Views are built into the data platform. Build RAG knowledge bases and AI-enhanced analytics without external services. Data Analytics Agent supports natural language conversational data queries.

[Lakehouse AI Overview](lakehouseai-overview.md) · [Vector Search](vector_search_ai.md) · [AI Functions](ai_function_in_sql.md) · [Semantic View](semantic-view-overview.md) · [Data Analytics Agent](datagpt_introduction.md)

</td>
<td style="width:50%; vertical-align:top; padding:0 0 0 16px; overflow-wrap:break-word;">

**Studio and AI Agent Integration**

Built-in IDE, task scheduling, data integration, data quality, and operations monitoring — one-stop data development. cz-cli provides a deterministic command interface; Semantic Views provide a business semantic layer; both support AI Agents calling data capabilities directly.

[Studio User Guide](studio_manual.md) · [cz-cli Installation and Usage](setup_cz_cli.md) · [Semantic View](semantic-view-overview.md)

</td>
</tr>
</table>

---

## What's New

→ [Release Notes](release-notes.md)

---

## This Section

| Page | Description |
|------|-------------|
| [Before You Begin](setup.md) | Ways to access Lakehouse: Studio, CLI, drivers and connectors |
| [Account Signup and Setup](logging-in.md) | Register an account, activate a service instance, complete initialization |
| [Supported Cloud Platforms](supported-cloud-platforms.md) | Supported cloud providers and available regions |
| [Pricing and Billing](pricing.md) | Billing model and cost breakdown |
| [Trial Account Quotas and Limits](trial-account-quotas-and-limits.md) | Resource quota limits during the trial period |
