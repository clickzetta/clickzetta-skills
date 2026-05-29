# Getting Started

Choose your onboarding path by role. Most scenarios can be completed in 30 minutes.

---

<table style="width:100%; table-layout:auto; min-width:0;">
<tr>
<td style="width:50%; vertical-align:top; padding:0 16px 0 0; overflow-wrap:break-word;">

## Data Engineer

**Goal: Ingest data and run through an ODS → DWD → ADS processing pipeline**

**Step 1 — Run through core features** (30 minutes)

[Lakehouse Quick Start Experience](lakehouse-quick-experience_guide.md)

**Step 2 — Ingest your data**

| Data source | Recommended approach |
|-------------|----------------------|
| MySQL / PG / Oracle, real-time CDC | [Studio Real-time Sync Tasks](realtime_sync.md) |
| Full-database migration, multi-table sync | [Multi-table Real-time Sync](multitable_realtime_sync_sop.md) |
| Object storage files (OSS / S3 / COS) | [Pipe Continuous Ingestion](pipe-introduction.md) · [COPY INTO](quickstart-with-copy-command.md) |
| Kafka message streams | [Kafka Pipe](pipe-introduction.md) |
| Local CSV / Excel files | [Upload Local Data](quick_start_upload_data.md) |

**Step 3 — Build your data processing pipeline**

[Dynamic Table Incremental Computation](incremental-computing.md) · [Studio Task Development and Scheduling](task-develop.md) · [End-to-End CDC Complete Example](czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables.md)

**Step 4 — Connect external tools**

[JDBC Driver](JDBC-Driver.md) · [cz-cli Command Line](setup_cz_cli.md) · [SQLAlchemy](sqlalchemy.md) · [Python SDK](python_reference/connector.md)

</td>
<td style="width:50%; vertical-align:top; padding:0 0 0 16px; overflow-wrap:break-word;">

## Data Analyst

**Goal: Connect to data, run SQL, use AI-assisted analysis**

**Step 1 — Run your first SQL query** (5 minutes)

[Run Your First SQL Query](quick_start_sql_query.md)

**Step 2 — Connect your tools**

| Tool type | Connection method |
|-----------|-------------------|
| BI tools (FineBI / PowerBI / Tableau, etc.) | [JDBC Driver](JDBC-Driver.md) |
| Database clients (DataGrip / DBeaver / Navicat, etc.) | [MySQL Protocol](use-mysql-client.md) |
| Python scripts | [SQLAlchemy](sqlalchemy.md) |
| Terminal command line | [Command-Line Client](connect-with-cli.md) |

**Step 3 — Advanced analysis**

[Data Analytics Agent (DataGPT)](LakehouseDataGPT-tour.md) · [SQL Usage Guide](considerations-for-using-sql.md) · [Experience Performance with TPC-H Sample Data](get-started-with-sample-data.md)

</td>
</tr>
<tr>
<td style="width:50%; vertical-align:top; padding:16px 16px 0 0; overflow-wrap:break-word;">

## AI / ML Engineer

**Goal: Build vector search, RAG knowledge bases, AI-enhanced analytics**

**Step 1 — Understand Lakehouse AI capabilities**

[Lakehouse AI Overview](LakehouseAI-overview.md)

**Step 2 — Choose your scenario**

| Scenario | Entry point |
|----------|-------------|
| Semantic search / RAG knowledge base | [AI Data Readiness](server-data-for-ai.md) · [Vector Search](vector_search_ai.md) |
| Call LLMs in SQL | [AI Functions (AI\_COMPLETE / AI\_EMBEDDING)](AI_function_in_SQL.md) |
| Manage and switch between multiple LLM models | [AI Gateway](AIGateway.md) |
| Natural language conversational data analysis | [Data Analytics Agent](datagpt_introduction.md) |
| Python data processing + AI inference | [Zettapark Quick Start](zettapark-quick-start.md) |

</td>
<td style="width:50%; vertical-align:top; padding:16px 0 0 16px; overflow-wrap:break-word;">

## Platform Administrator

**Goal: Set up accounts, assign permissions, configure environments**

1. [Manage Users](quick_start_user_management.md) — Create users, assign roles
2. [Create and Use Workspaces](quick_start_create_workspace.md) — Workspace isolation and configuration
3. [Manage Workspace Users](quick_start_workspace_user.md) — Workspace-level permission management
4. [Build a Data Development Environment Using Workspaces](quick_start_workspace.md) — Set up a complete data development environment for your team
5. [Configure Monitoring and Alerting Rules](quick_start_monitoring_and_alerting.md) — Alerts for task failures and performance anomalies

</td>
</tr>
<tr>
<td colspan="2" style="vertical-align:top; padding:16px 0 0 0; border-top:1px solid #e8e8e8; overflow-wrap:break-word;">

## AI Agent / Automation

**Goal: Call data capabilities through deterministic interfaces, build automated data pipelines**

<table style="width:100%; table-layout:auto;">
<tr>
<td style="width:50%; vertical-align:top; padding:0 16px 0 0; overflow-wrap:break-word;">

| Scenario | Recommended approach |
|----------|----------------------|
| SQL execution and result retrieval | [cz-cli sql](setup_cz_cli.md) · [Python connector](python_reference/connector.md) |
| Task scheduling and triggering | [cz-cli task / runs refill](setup_cz_cli.md) |
| Studio task development and data source management | [cz-cli task create/save](setup_cz_cli.md) · [Studio Task Development](task-develop.md) · [Studio Data Integration](data-integration.md) |

</td>
<td style="width:50%; vertical-align:top; padding:0 0 0 16px; overflow-wrap:break-word;">

| Scenario | Recommended approach |
|----------|----------------------|
| Python data read/write | [Zettapark](zettapark-quick-start.md) · [clickzetta-connector](python_reference/connector.md) |
| Business semantic layer queries | [Semantic View](semantic-view-overview.md) |
| Collaborate with a specialized data sub-agent | [cz-cli agent run](setup_cz_cli.md) |

</td>
</tr>
</table>

</td>
</tr>
</table>

---

## Quick Start by Feature

<table style="width:100%; table-layout:auto;">
<tr>
<td style="width:50%; vertical-align:top; padding:0 16px 0 0; overflow-wrap:break-word;">

| What I want to do | Entry point |
|-------------------|-------------|
| Experience core product features quickly | [Lakehouse Quick Start Experience](lakehouse-quick-experience_guide.md) |
| Understand the Studio interface layout | [Lakehouse Studio Tour](LakehouseStudio-tour.md) |
| Upload a local CSV file | [Upload Local Data](quick_start_upload_data.md) |
| Real-time CDC sync from MySQL / PG | [Studio Real-time Sync Tasks](realtime_sync.md) |
| Create a scheduled sync task | [Create Sync Task to Import Data](quick_start_batch_sync_data.md) |
| Mount OSS / S3 / COS object storage | [External Volume](external_volume.md) |
| Configure ETL scheduling workflow | [Configure ETL Orchestration and Scheduling](quick_start_etl.md) |
| Federate queries over data lake (Hive / Iceberg) | [External Catalog Federation](external-catalog-summary.md) |

</td>
<td style="width:50%; vertical-align:top; padding:0 0 0 16px; overflow-wrap:break-word;">

| What I want to do | Entry point |
|-------------------|-------------|
| Configure data quality rules | [Configure Data Quality Rules](quick_start_data_quality.md) |
| Configure monitoring and alerting | [Configure Monitoring and Alerting Rules](quick_start_monitoring_and_alerting.md) |
| Experience engine performance (TPC-H) | [Experience Performance with TPC-H Sample Data](get-started-with-sample-data.md) |
| Write complex business analytics SQL | [SQL Usage Guide](considerations-for-using-sql.md) |
| Use AI to analyze data conversationally | [Data Analytics Agent (DataGPT)](LakehouseDataGPT-tour.md) |
| Build vector search / RAG knowledge base | [Vector Search](vector_search_ai.md) |
| Process data with Python (Zettapark) | [Zettapark Quick Start](zettapark-quick-start.md) |
| Migrate from Spark to Lakehouse | [Migration Guide](tutorial_migration.md) |

</td>
</tr>
</table>
