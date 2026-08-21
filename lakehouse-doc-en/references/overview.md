# Overview

Singdata Lakehouse is a cloud lakehouse platform developed by Singdata. Built on an incremental computing engine, it delivers up to 10x better performance than traditional open-source architectures such as Spark, enabling end-to-end, low-cost, real-time processing for large-scale data. The platform supports the integration, storage, and computation of all data types, providing the data infrastructure enterprises need to move from Spark-based systems to AI-ready data platforms.    
 
For enterprises with existing data lakes (S3 / OSS / COS), Singdata Lakehouse can mount existing object storage and query Hive, Iceberg, Delta Lake, and other data formats through External Catalog. This provides high-performance SQL analytics without data migration and offers a low-cost path from a data lake to a unified lakehouse.

Singdata Lakehouse supports seven cloud providers worldwide, is available in multiple Asia-Pacific regions, and also supports private deployment. Deployment costs can be reduced to 1/5-1/3 of traditional solutions, with operations costs close to zero.


<div style="display:flex; flex-wrap:wrap; gap:8px; margin:16px 0">
<div style="flex:1 1 160px; min-width:0; border-radius:8px; padding:12px 16px">
<strong>Migrate from Spark / Databricks</strong><br>
<small><a href="tutorial_migration.md">Migration Guide</a> · <a href="migrate-spark-data-engineering-best-practices-to-lakehouse.md">Migration Best Practices</a> · <a href="sql-reference.md">SQL Syntax Comparison</a> · <a href="spark-connector-summary.md">Spark Connector</a> · <a href="benchmark_guide.md">Performance Benchmarks</a></small>
</div>
<div style="flex:1 1 160px; min-width:0; border-radius:8px; padding:12px 16px">
<strong>Accelerate on Existing Data Lake</strong><br>
<small><a href="lakehouse-acceleration-guide.md">On-Site Acceleration Implementation Guide</a> · <a href="external-catalog-summary.md">External Catalog Federation Query</a> · <a href="external-table-guide.md">External Tables</a> · <a href="external_volume.md">Object Storage Mount</a> · <a href="benchmark_guide.md">Performance Benchmarks</a></small>
</div>
<div style="flex:1 1 160px; min-width:0; border-radius:8px; padding:12px 16px">
<strong>AI Data Infrastructure</strong><br>
<small><a href="lakehouseai-overview.md">Lakehouse AI Overview</a> · <a href="server-data-for-ai.md">AI Data Preparation</a> · <a href="vector_search_ai.md">Vector Search</a> · <a href="aigateway.md">AI Gateway</a> · <a href="datagpt_introduction.md">Data Analytics Agent</a> · <a href="dataagent.md">Data Engineering Agent</a></small>
</div>
<div style="flex:1 1 160px; min-width:0; border-radius:8px; padding:12px 16px">
<strong>Cloud Platforms & Deployment</strong><br>
<small><a href="supported-cloud-platforms.md">Supported Cloud Platforms and Regions</a> · <a href="pricing.md">Pricing and Billing</a></small>
</div>
</div>


![](/.topwrite/assets/anim-40-product-architecture.svg)

---
## First Time Here?
```youtube
<iframe width="560" height="315" src="https://www.youtube.com/embed/GzTn207fDTc?si=trTDDGVcV4XGOE0r" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
```

<div style="display:flex; flex-wrap:wrap; gap:8px; margin:8px 0">
<div style="flex:1 1 200px; min-width:0; border:1px solid #E5E7EB; border-radius:8px; padding:16px 20px; text-align:center">
<div style="font-size:22px; font-weight:700; color:#2563EB; margin-bottom:4px">①</div>
<strong>Create Your Account</strong><br>
<small>5 minutes</small><br><br>
Register an account, activate a service instance, and complete initial setup<br><br>
<a href="logging-in.md">Get Started →</a>
</div>
<div style="flex:1 1 200px; min-width:0; border:1px solid #E5E7EB; border-radius:8px; padding:16px 20px; text-align:center">
<div style="font-size:22px; font-weight:700; color:#2563EB; margin-bottom:4px">②</div>
<strong>Quick Start Experience</strong><br>
<small>30 minutes</small><br><br>
Walk through data ingestion, SQL querying, and Dynamic Table incremental computing<br><br>
<a href="lakehouse-quick-experience_guide.md">Start Exploring →</a>
</div>
<div style="flex:1 1 200px; min-width:0; border:1px solid #E5E7EB; border-radius:8px; padding:16px 20px; text-align:center">
<div style="font-size:22px; font-weight:700; color:#2563EB; margin-bottom:4px">③</div>
<strong>Go Deeper by Role</strong><br>
<small>On demand</small><br><br>
Dedicated paths for data engineers, analysts, AI engineers, and administrators<br><br>
<a href="tutorials.md">Choose Your Path →</a>
</div>
</div>
---
![](/.topwrite/assets/anim-40-product-architecture.svg)
---
## Who Are You and What Do You Want to Do? 

<table style="width:100%">
<tr><th>Role / Scenario</th><th>Recommended Starting Point</th></tr>
<tr><td><strong>Data Integration / Data Sync</strong><br><small>Data ingestion, CDC sync, file import, streaming writes</small></td><td><a href="data-integration.md">Studio Data Integration</a> (visual configuration for 40+ data sources) · <a href="realtime_sync.md">Real-time Sync Tasks</a> (MySQL / PG / Oracle full-database CDC) · <a href="batch_sync.md">Batch Sync Tasks</a> (scheduled batch sync) · <a href="pipe-introduction.md">Pipe Continuous Ingestion</a> (object storage / Kafka automatic writes) · <a href="COPY-INTO-table.md">COPY INTO</a> (one-time file import) · <a href="a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md">Complete Data Integration Guide</a></td></tr>
<tr><td><strong>Data Engineer</strong><br><small>Build data pipelines, process ETL jobs, and manage data warehouse layers</small></td><td><a href="incremental-computing.md">Dynamic Table Incremental Computing</a> · <a href="dynamic_table_summary.md">Dynamic Table Overview</a> · <a href="streaming_data_pipeline_overview.md">Streaming Data Pipeline</a> · <a href="cz-cli-studio-tasks.md">Studio Task Development & Scheduling</a> · <a href="create-table-ddl.md">DDL Syntax Reference</a> · <a href="sql-reference.md">SQL Reference</a> · <a href="setup_cz_cli.md">cz-cli Command Line Tool</a> · <a href="dataagent.md">Data Engineering Agent</a> · <a href="tpcds-benchmark.md">TPC-DS Benchmark</a></td></tr>
<tr><td><strong>Data Analyst</strong><br><small>SQL queries, BI connections, ad-hoc analysis</small></td><td><a href="quick_start_sql_query.md">Run Your First SQL Query</a> · <a href="tutorial_connect_to_lakehouse.md">Connect BI Tools</a> · <a href="datagpt_introduction.md">Data Analytics Agent (natural language queries)</a> · <a href="semantic-view-overview.md">Semantic Views</a> · <a href="ssb-benchmark.md">SSB Benchmark</a> · <a href="tpch-benchmark.md">TPC-H Benchmark</a></td></tr>
<tr><td><strong>AI / ML Engineer</strong><br><small>Vector search, RAG, AI functions, model invocation</small></td><td><a href="server-data-for-ai.md">AI Data Preparation</a> · <a href="vector_search_ai.md">Vector Search</a> · <a href="AI_function_in_SQL.md">AI Functions (AI_COMPLETE / AI_EMBEDDING)</a> · <a href="aigateway.md">AI Gateway</a> · <a href="python_reference/connector.md">Python SDK</a> · <a href="lakehousepython-zettapark.md">ZettaPark (DataFrame API)</a></td></tr>
<tr><td><strong>Platform Administrator</strong><br><small>User management, permissions, compute clusters, cost control</small></td><td><a href="logging-in.md">Account and Service Instance Setup</a> · <a href="authority-management.md">User and Permission Management</a> · <a href="virtual-cluster.md">Compute Cluster Management</a> · <a href="pricing.md">Pricing and Billing</a></td></tr>
<tr><td><strong>AI Agent / Automation</strong><br><small>Deterministic API calls, semantic layer queries, automated data pipelines</small></td><td><a href="setup_cz_cli.md">cz-cli Command Line Tool</a> (deterministic interface, suitable for Agent calls) · <a href="semantic-view-overview.md">Semantic Views</a> (business semantic layer) · <a href="python_reference/connector.md">Python SDK</a> · <a href="lakehousepython-zettapark.md">ZettaPark</a> · <a href="datagpt_introduction.md">Data Analytics Agent</a> · <a href="dataagent.md">Data Engineering Agent</a> · <a href="https://www.singclaw.ai/">Singclaw</a></td></tr>
</table>

---

## Core Capabilities

<div style="display:flex; flex-wrap:wrap; gap:12px; margin:8px 0">
<div style="flex:1 1 240px; min-width:0; border-left:3px solid #2563EB; padding:0 0 0 14px; display:flex; flex-direction:column">

**Data Integration**

<div style="flex:1">40+ data sources are supported out of the box: MySQL / PG / Oracle full-database CDC real-time sync, Kafka streaming writes, S3 / OSS / COS continuous file ingestion, and COPY INTO one-time batch import.</div>

<small>[Data Integration Guide](a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md) · [Studio Data Integration](data-integration.md) · [Pipe](pipe-introduction.md) · [COPY INTO](COPY-INTO-table.md)</small>

</div>
<div style="flex:1 1 240px; min-width:0; border-left:3px solid #2563EB; padding:0 0 0 14px; display:flex; flex-direction:column">

**Unified Lakehouse**

<div style="flex:1">For existing data lakes (S3 / OSS / COS), no migration is required. Mount existing object storage directly and query Hive, Iceberg, and Delta Lake data through External Catalog to gain high-performance SQL analytics.</div>

<small>[External Catalog](external-catalog-summary.md) · [External Volume](external_volume.md) · [On-Site Acceleration Guide](lakehouse-acceleration-guide.md)</small>

</div>
<div style="flex:1 1 240px; min-width:0; border-left:3px solid #2563EB; padding:0 0 0 14px; display:flex; flex-direction:column">

**Incremental Computing**

<div style="flex:1">Define transformation logic in standard SQL. Dynamic Table automatically detects upstream changes and refreshes incrementally, replacing manual scheduling scripts for low-latency data pipelines.</div>

<small>[Incremental Computing](incremental-computing.md) · [Dynamic Table Overview](dynamic_table_summary.md) · [Streaming Data Pipeline](streaming_data_pipeline_overview.md)</small>

</div>
<div style="flex:1 1 240px; min-width:0; border-left:3px solid #2563EB; padding:0 0 0 14px; display:flex; flex-direction:column">

**High-Performance SQL Analytics**

<div style="flex:1">A vectorized execution engine supports OLAP multidimensional analysis and ad-hoc queries. On TPC-DS / TPC-H / SSB benchmarks, performance can be up to 10x faster than traditional Spark architectures.</div>

<small>[TPC Benchmark Reports](benchmark_guide.md) · [SQL Usage Guide](considerations-for-using-sql.md)</small>

</div>
<div style="flex:1 1 240px; min-width:0; border-left:3px solid #2563EB; padding:0 0 0 14px; display:flex; flex-direction:column">

**AI Native**

<div style="flex:1">Vector indexes, full-text search, AI functions (AI_COMPLETE / AI_EMBEDDING), and Semantic Views are built into the data platform. Build RAG knowledge bases and AI-enhanced analytics without external services. Data Analytics Agent supports conversational data queries in natural language; Data Engineering Agent supports ETL development in natural language.</div>

<small>[Lakehouse AI Overview](lakehouseai-overview.md) · [Vector Search](vector_search_ai.md) · [AI Functions](AI_function_in_SQL.md) · [Semantic Views](semantic-view-overview.md) · [Data Analytics Agent](datagpt_introduction.md) · [Data Engineering Agent](dataagent.md)</small>

</div>
<div style="flex:1 1 240px; min-width:0; border-left:3px solid #2563EB; padding:0 0 0 14px; display:flex; flex-direction:column">

**Studio & AI Agent Integration**

<div style="flex:1">Built-in IDE, task scheduling, data integration, data quality, and operations monitoring provide a unified data development platform. cz-cli provides a deterministic command interface, and Semantic Views provide a business semantic layer so AI Agents can call data capabilities directly.</div>

<small>[Studio User Manual](studio_manual.md) · [cz-cli Installation and Usage](setup_cz_cli.md) · [Semantic Views](semantic-view-overview.md)</small>

</div>
</div>

---

## What's New

→ [Product Updates](releasenotes.md)

---

## In This Section

<table style="width:100%">
<tr><th>Page</th><th>Description</th></tr>
<tr><td><a href="setup.md">Before You Begin</a></td><td>Ways to access Lakehouse: Studio, CLI, drivers and connectors</td></tr>
<tr><td><a href="logging-in.md">Account Signup and Setup</a></td><td>Register an account, activate a service instance, and complete initialization</td></tr>
<tr><td><a href="supported-cloud-platforms.md">Cloud Services and Regions</a></td><td>Supported cloud providers and available regions</td></tr>
<tr><td><a href="trial-account-quotas-and-limits.md">Trial Account Quotas and Limits</a></td><td>Resource quotas during the trial period</td></tr>
</table>
