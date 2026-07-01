# Getting Started

Choose an onboarding path based on your role. Most starter scenarios can be completed within 30 minutes.

---

<div style="display:flex; flex-wrap:wrap; gap:16px; margin:8px 0">
<div style="flex:1 1 280px; min-width:0; border:1px solid #DBEAFE; border-radius:8px; padding:20px 24px">

## Data Engineer

**Goal: Ingest data and complete an ODS → DWD → ADS processing pipeline**

**Step 1 — Try the core features** (30 minutes)

[Lakehouse Quick Start Experience](lakehouse-quick-experience_guide.md)

**Step 2 — Ingest your data**

<table style="width:100%">
<tr><th>Data Source</th><th>Recommended Method</th></tr>
<tr><td>MySQL / PG / Oracle, real-time CDC</td><td><a href="realtime_sync.md">Studio Real-time Sync Tasks</a></td></tr>
<tr><td>Full-database migration, multiple tables at once</td><td><a href="multitable_realtime_sync_sop.md">Multi-table Real-time Sync</a></td></tr>
<tr><td>Object storage (S3 / OSS / COS)</td><td><a href="pipe-introduction.md">Pipe Continuous Ingestion</a> · <a href="copy-into-table.md">COPY INTO</a></td></tr>
<tr><td>Kafka message streams</td><td><a href="pipe-introduction.md">Kafka Pipe</a></td></tr>
<tr><td>Local CSV / Excel files</td><td><a href="quick_start_upload_data.md">Upload Local Data</a></td></tr>
</table>

**Step 3 — Build data processing pipelines**

[Dynamic Table Incremental Computation](incremental-computing.md) · [Studio Task Development and Scheduling](task-develop.md) · [Data Engineering Agent](dataagent.md) (ETL development and task management in natural language) · [End-to-End CDC Example](sql_table_stream_guide.md)

**Step 4 — Connect external tools**

[JDBC Driver](jdbc-driver.md) · [cz-cli Command Line](setup_cz_cli.md) · [SQLAlchemy](sqlalchemy.md) · [Python SDK](python_reference/connector.md)

</div>
<div style="flex:1 1 280px; min-width:0; border:1px solid #DBEAFE; border-radius:8px; padding:20px 24px">

## Data Analyst

**Goal: Connect to data, run SQL, use AI-assisted analysis**

**Step 1 — Run your first SQL** (5 minutes)

[How to Run Your First SQL Query](quick_start_sql_query.md)

**Step 2 — Connect your tools**

<table style="width:100%">
<tr><th>Tool Type</th><th>Connection Method</th></tr>
<tr><td>FineBI / Power BI / Tableau and other BI tools</td><td><a href="jdbc-driver.md">JDBC Driver</a></td></tr>
<tr><td>DataGrip / DBeaver / Navicat and other clients</td><td><a href="use-mysql-client.md">MySQL Protocol</a></td></tr>
<tr><td>Python scripts</td><td><a href="sqlalchemy.md">SQLAlchemy</a></td></tr>
<tr><td>Terminal command line</td><td><a href="connect-with-cli.md">Command-Line Client</a></td></tr>
</table>

**Step 3 — Advanced analysis**

[Data Analytics Agent](lakehousedatagpt-tour.md) · [SQL Usage Guide](considerations-for-using-sql.md) · [TPC-H Sample Data Performance Walkthrough](get-started-with-sample-data.md)

</div>
</div>

<div style="display:flex; flex-wrap:wrap; gap:16px; margin:16px 0">
<div style="flex:1 1 280px; min-width:0; border:1px solid #DBEAFE; border-radius:8px; padding:20px 24px">

## AI / ML Engineer

**Goal: Build vector search, RAG knowledge bases, AI-enhanced analytics**

**Step 1 — Learn about Lakehouse AI capabilities**

[Lakehouse AI Overview](lakehouseai-overview.md)

**Step 2 — Choose your scenario**

<table style="width:100%">
<tr><th>Scenario</th><th>Entry Point</th></tr>
<tr><td>Semantic search / RAG knowledge base</td><td><a href="server-data-for-ai.md">AI Data Preparation</a> · <a href="vector_search_ai.md">Vector Search</a></td></tr>
<tr><td>Call LLMs from SQL</td><td><a href="ai_function_in_sql.md">AI Functions (AI_COMPLETE / AI_EMBEDDING)</a></td></tr>
<tr><td>Manage and switch between multiple LLM models</td><td><a href="aigateway.md">AI Gateway</a></td></tr>
<tr><td>Conversational data analysis in natural language</td><td><a href="datagpt_introduction.md">Data Analytics Agent</a></td></tr>
<tr><td>ETL development, task management, and operations diagnostics in natural language</td><td><a href="dataagent.md">Data Engineering Agent</a></td></tr>
<tr><td>Python data processing + AI inference</td><td><a href="zettapark-quick-start.md">ZettaPark Quick Start</a></td></tr>
</table>

</div>
<div style="flex:1 1 280px; min-width:0; border:1px solid #DBEAFE; border-radius:8px; padding:20px 24px">

## Platform Administrator

**Goal: Set up accounts, grant permissions, and configure environments**

1. [Quickly Add and Manage Users](quick_start_user_management.md) — Create users and assign roles
2. [Quickly Create and Use Workspaces](quick_start_create_workspace.md) — Workspace isolation and configuration
3. [Quickly Manage Workspace Users](quick_start_workspace_user.md) — Workspace-level permission management
4. [Build a Data Development Environment with Workspaces](quick_start_workspace.md) — Set up a complete data development environment for your team
5. [Quickly Configure and Use Monitoring and Alerting Rules](quick_start_monitoring_and_alerting.md) — Task failure and performance anomaly alerts

</div>
</div>

---

## AI Agent / Automation

**Goal: Use deterministic interfaces to call data capabilities and build automated data pipelines**

<div style="display:flex; flex-wrap:wrap; gap:16px; margin:8px 0">
<div style="flex:1 1 280px; min-width:0">

<table style="width:100%">
<tr><th>Scenario</th><th>Recommended Integration</th></tr>
<tr><td>SQL execution and result retrieval</td><td><a href="setup_cz_cli.md">cz-cli sql</a> · <a href="python_reference/connector.md">Python connector</a></td></tr>
<tr><td>Task scheduling and triggering</td><td><a href="setup_cz_cli.md">cz-cli task / runs refill</a></td></tr>
<tr><td>Studio task development and data source management</td><td><a href="setup_cz_cli.md">cz-cli task create/save</a> · <a href="task-develop.md">Studio Task Development</a> · <a href="data-integration.md">Studio Data Integration</a></td></tr>
</table>

</div>
<div style="flex:1 1 280px; min-width:0">

<table style="width:100%">
<tr><th>Scenario</th><th>Recommended Integration</th></tr>
<tr><td>Python data read/write</td><td><a href="zettapark-quick-start.md">ZettaPark</a> · <a href="python_reference/connector.md">clickzetta-connector</a></td></tr>
<tr><td>Business semantic layer queries</td><td><a href="semantic-view-overview.md">Semantic Views</a></td></tr>
<tr><td>Collaborate with specialized data sub-agents</td><td><a href="setup_cz_cli.md">cz-cli agent run</a></td></tr>
<tr><td>Browser automation Web Agent</td><td><a href="https://www.singclaw.ai/">Singclaw</a></td></tr>
</table>

</div>
</div>

---

## Quick Start by Feature

<table style="width:100%">
<tr><th>What I Want to Do</th><th>Entry Point</th></tr>
<tr><td>Quickly experience core product features</td><td><a href="lakehouse-quick-experience_guide.md">Lakehouse Quick Start Experience</a></td></tr>
<tr><td>Learn the Studio interface layout</td><td><a href="lakehousestudio-tour.md">Lakehouse Studio Quick Tour</a></td></tr>
<tr><td>Upload a local CSV file</td><td><a href="quick_start_upload_data.md">Quickly Upload and Import Local Data</a></td></tr>
<tr><td>Real-time CDC sync from MySQL / PG</td><td><a href="realtime_sync.md">Studio Real-time Sync Tasks</a></td></tr>
<tr><td>Create a scheduled sync task</td><td><a href="quick_start_batch_sync_data.md">Quickly Create Sync Tasks to Import Data</a></td></tr>
<tr><td>Mount S3 / OSS / COS object storage</td><td><a href="external_volume.md">External Volume</a></td></tr>
<tr><td>Configure ETL scheduling workflows</td><td><a href="quick_start_etl.md">Quickly Configure and Schedule ETL Workflows</a></td></tr>
<tr><td>Run federated queries on a data lake (Hive / Iceberg)</td><td><a href="external-catalog-summary.md">External Catalog Federated Query</a></td></tr>
<tr><td>Configure data quality rules</td><td><a href="quick_start_data_quality.md">Quickly Configure and Use Data Quality Rules</a></td></tr>
<tr><td>Configure monitoring and alerting</td><td><a href="quick_start_monitoring_and_alerting.md">Quickly Configure and Use Monitoring and Alerting Rules</a></td></tr>
<tr><td>Experience engine performance (TPC-H)</td><td><a href="get-started-with-sample-data.md">Experience Engine Performance with TPC-H Sample Data</a></td></tr>
<tr><td>Write complex business analysis SQL</td><td><a href="considerations-for-using-sql.md">SQL Usage Guide</a></td></tr>
<tr><td>Use AI to analyze data conversationally</td><td><a href="lakehousedatagpt-tour.md">Data Analytics Agent</a></td></tr>
<tr><td>Use AI to develop ETL / manage tasks</td><td><a href="dataagent.md">Data Engineering Agent</a></td></tr>
<tr><td>Build vector search / RAG knowledge base</td><td><a href="vector_search_ai.md">Vector Search</a></td></tr>
<tr><td>Process data with Python (ZettaPark)</td><td><a href="zettapark-quick-start.md">ZettaPark Quick Start</a></td></tr>
<tr><td>Migrate from Spark to Lakehouse</td><td><a href="tutorial_migration.md">Migration Guide</a></td></tr>
</table>
