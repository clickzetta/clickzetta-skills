# Studio

Studio is both the web management console for Singdata Lakehouse and a serverless data services platform. The data sync jobs, SQL scheduling tasks, and Python scripts you configure in the UI are automatically executed by Singdata-managed serverless infrastructure — no compute resources to manage. Data engineers, analysts, and administrators can handle the full pipeline from data ingestion to data consumption in a single interface, without switching between tools.

![](/.topwrite/assets/28-studio-overview.svg)

## Data Agent — AI Assistant

Studio has a built-in Data Agent — a fully AI-driven interaction layer built on top of Lakehouse, covering the full lifecycle of development, operations, and governance. You can tell the Agent what to do in natural language, and it operates the platform on your behalf — shifting from "person operates platform" to "person directs Agent."

Typical use cases:

- **ETL development assistance**: Describe your data processing requirements, and the Agent generates SQL tasks and configures scheduling
- **Natural language data retrieval**: Ask "What are the order amounts by region for the last 7 days?" and the Agent translates it to SQL and returns results
- **Day-to-day operations Q&A**: Ask "Which tasks are currently failing?" and the Agent queries and provides remediation suggestions
- **Data insight generation**: Upload data or specify a table, and the Agent automatically generates an analysis report

> 💡 **Tip**: Click "Data Agent" at the top of the menu bar to launch this feature. See [Data Agent](dataagent.md) for details.

> 💡 **AI Agent integration**: If you are building your own AI Agent or automation pipeline, you can programmatically invoke Studio capabilities via [cz-cli](setup_cz_cli.md) — cz-cli is the command-line interface for AI Agents to control Lakehouse & Studio, covering all major Studio modules.

## Six Core Modules

<table>
<tr>
<td style="width:33%; vertical-align:top; overflow-wrap:break-word;">

**Data Sync**<br>
Visually configure real-time CDC sync and offline batch sync for 40+ data sources — no code required. Supports MySQL, PostgreSQL, Oracle, Kafka, and other mainstream sources.

→ [Data Sync Overview](data-integration.md)

</td>
<td style="width:33%; vertical-align:top; overflow-wrap:break-word;">

**Task Development (IDE)**<br>
Built-in SQL / Python / Shell editors with support for composite tasks, loop tasks, and conditional branching — develop your data transformation logic end-to-end in one place.

→ [Task Development and Scheduling](task-develop.md)

</td>
<td style="width:33%; vertical-align:top; overflow-wrap:break-word;">

**Task Scheduling**<br>
Cron-based scheduling with upstream/downstream dependency management, support for historical backfill, and real-time visibility into task execution status.

→ [Task Scheduling Dependencies](task_scheduling_dependency.md)

</td>
</tr>
<tr>
<td style="width:33%; vertical-align:top; overflow-wrap:break-word;">

**Workspace (SQL Query)**<br>
Interactive SQL editor with multi-tab support, result visualization, and query history — ideal for ad-hoc analysis and data exploration.

→ [Workspace](worksheet.md)

</td>
<td style="width:33%; vertical-align:top; overflow-wrap:break-word;">

**Operations & Monitoring**<br>
View task run history, logs, and failure reasons. Configure alert notifications and stay on top of your data pipeline health.

→ [Task and Instance Operations](task-instance-maintenance.md)

</td>
<td style="width:33%; vertical-align:top; overflow-wrap:break-word;">

**Data Catalog**<br>
Browse and manage table schemas, column comments, and data lineage. Supports permission requests and approval workflows.

→ [Data Catalog](data_catalog.md)

</td>
</tr>
</table>

> 💡 **Tip**: **Studio vs cz-cli** — Studio is the web GUI, suited for manual operations and visual configuration. [cz-cli](setup_cz_cli.md) is the command-line interface, suited for scripting, CI/CD pipelines, and programmatic AI Agent calls. Both cover the same feature set.

---

## I want to sync external data in

**Recommended: Data Sync module** — supports 40+ data sources with visual configuration, no code required.

| Scenario | Approach | Reference |
|------|------|---------|
| Relational databases (MySQL / PG / Oracle, etc.), real-time sync | Real-time sync task (CDC) | [Real-time Sync Task](realtime_sync.md) |
| Full database sync, migrating multiple tables at once | Multi-table real-time sync | [Multi-table Real-time Sync Guide](multitable_realtime_sync_sop.md) |
| Offline periodic sync (T+1 or hourly) | Offline sync task | [Offline Sync Task](batch_sync.md) |
| Not sure which data source to use | Check supported sources | [Data Source Support](data-sources.md) |

> Configuring a data source for the first time? Start with [Data Source Management](config-datasource.md), then look up your database type in the [Data Source Configuration Guide](datasource-config-guide.md).

---

## I want to develop data processing tasks

**Recommended: Task Development module (IDE)** — supports SQL, Python, and Shell with composable orchestration.

| Scenario | Approach | Reference |
|------|------|---------|
| SQL-based data transformation | SQL task | [Task Development and Scheduling](task-develop.md) |
| Python processing logic | Python task | [Python Task](python-task.md) |
| Multiple tasks in sequence with dependencies | Composite task | [Composite Task](composite_task.md) |
| Loop over multiple partitions or objects | For each loop task | [For Each Loop Task](foreach.md) |
| Conditional branching (if/else logic) | Branch task | [Branch Task](if_else_task.md) |
| Incremental computation with auto-maintained result tables | Dynamic table task | [Dynamic Table Task](dynamic_table_task.md) |

---

## I want to configure scheduled execution

**Recommended: Task Scheduling module** — supports Cron expressions and upstream/downstream dependency management.

| Scenario | Reference |
|------|---------|
| Set up timed task execution | [Task Scheduling and Instance Execution](f6fc6447ee.md) |
| Configure dependencies between tasks | [Task Scheduling Dependencies](task_scheduling_dependency.md) |
| Backfill historical data | [Data Backfill](backfilling_data.md) |

---

## I want to check task run status / troubleshoot issues

**Recommended: Operations & Monitoring module.**

| Scenario | Reference |
|------|---------|
| View task run history and logs | [Task and Instance Operations](task-instance-maintenance.md) |
| Configure alert notifications | [Monitoring and Alerting](monitoring_and_alerting.md) |
| Understand monitoring metric definitions | [Monitoring Metric Specifications](monitoring_item_specification.md) |

---

## I want to query and analyze data

| Scenario | Approach | Reference |
|------|------|---------|
| Interactive SQL queries | Workspace | [Workspace](worksheet.md) |
| Visualize query results | Analysis (Notebook) | [Analysis](Notebook.md) |
| View and manage table schemas | Data Catalog | [Data Catalog](data_catalog.md) |

---

## I want to manage compute resources

| Scenario | Reference |
|------|---------|
| Create, start, or stop a VCluster | [Compute Clusters](virtual-cluster.md) |
| View historical job resource consumption | [Job History](web-job-history.md) |
| Understand cluster size codes | [Compute Cluster Size Reference](vcluster_size_description.md) |

---

## I want to manage permissions and approvals

| Scenario | Reference |
|------|---------|
| Request data access permissions | [Permission Requests](permission-application.md) |
| Process approval tickets | [Approval Tickets](approval-list.md) |

---

## New to Studio?

Follow this sequence to get started:

1. [Lakehouse Studio Quick Tour](LakehouseStudio-tour.md) — 5-minute overview of the interface layout
2. [Lakehouse Studio Getting Started Guide](lakehouse-studio-101.md) — complete your first end-to-end workflow
3. [Studio Overview](studio_overview.md) — deep dive into each module's capabilities
