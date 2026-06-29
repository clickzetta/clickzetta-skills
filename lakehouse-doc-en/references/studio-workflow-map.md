# Getting Things Done with Studio

Many users' first question when they encounter Studio is: "For what I want to do, where should I start?" This document maps common goals to their corresponding paths so you can find the right entry point by goal.

---

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Ingest Data and Keep It in Sync
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
Connect external data sources such as MySQL, PostgreSQL, Oracle, Kafka, and object storage into the Lakehouse and keep them continuously synced in real-time or batch mode.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. Confirm the data source type and network connectivity
2. Create and test the data source connection
3. Choose between batch sync, real-time sync, or multi-table sync
4. Configure the sync task
5. Monitor the first run result and ongoing sync status

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [Data Integration Overview](data-integration-intro.md)
- [Data Source Management](config-datasource.md)
- [Supported Data Sources](data-sources.md)
- [Batch Sync Tasks](batch_sync.md)
- [Real-Time Sync Tasks](realtime_sync.md)

</td>
</tr>
</table>

&nbsp;

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Build a Data Pipeline
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
You already have raw data and want to clean, transform, aggregate, and write it to tables, then chain multiple tasks into a stable running pipeline.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. Organize development objects in the task directory
2. Create SQL, Python, Shell, or JDBC tasks
3. Configure composite tasks, loop tasks, and branch tasks as needed
4. Set up parameters, resources, and input/output relationships
5. Configure scheduling and dependencies
6. Publish and observe instance runs

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [Task Development Concepts](task_development.md)
- [Task Development and Scheduling](task-develop.md)
- [Composite Tasks](composite_task.md)
- [For Each Loop Tasks](foreach.md)
- [Task Scheduling Dependencies](task_scheduling_dependency.md)

</td>
</tr>
</table>

&nbsp;

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Build a Data Warehouse
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
Build a stable data system around subject domains, layered models, and metric definitions, forming a continuously evolving data asset.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. Organize source tables, subject domains, and core metric definitions
2. Plan task directories, table layers, and task boundaries
3. Develop layered processing tasks
4. Orchestrate dependencies and scheduling pipelines
5. Continuously monitor runs, data quality, and downstream consumption

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [Data Engineering Agent](dataagent.md)
- [Task Directory and Governance Guide](dataagent-task-directory-governance-guide.md)
- [Data Pipeline and Data Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
- [Pipeline Launch Checklist](dataagent-pipeline-launch-checklist.md)

</td>
</tr>
</table>

&nbsp;

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Use the Agent to Help with Studio Operations
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
You know what you want to accomplish and want to reduce manual searching and clicking. You need the Agent to first confirm object status and impact scope before deciding on the next step.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. Describe the object, action, scope, and expected result
2. Have the Agent do a read-only check or plan first
3. Confirm the execution boundary for high-impact actions
4. Execute the corresponding changes
5. Return results and do a second review

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [How to Get the Agent to Operate Studio Accurately](studio-agent-operation-guide.md)
- [High-Impact Operations Guide](studio-high-impact-operations-guide.md)
- [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md)

</td>
</tr>
</table>

&nbsp;

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Launch a Stably Running Task
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
Task development is complete and you are ready to move into stable operation. You want to identify common gaps and risk points before going live.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. Check object status, configuration completeness, and dependencies
2. Check scheduling cycle, resources, and parameters
3. Publish the task
4. Monitor instance generation and run results
5. When anomalies occur, follow a consistent troubleshooting path

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [Launch Check and Troubleshooting Guide](studio-launch-check-and-troubleshooting-guide.md)
- [High-Impact Operations Guide](studio-high-impact-operations-guide.md)
- [Task and Instance Operations](task-instance-maintenance.md)

</td>
</tr>
</table>

&nbsp;

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Troubleshoot a Failed Task or Anomalous Pipeline
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
Failed instances, delays, empty runs, missed runs, or dependency anomalies have already occurred. You need to quickly identify which layer the problem is at.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. First identify the anomalous object and time range
2. Look at instance status, logs, and error information
3. Check scheduling, dependencies, and upstream readiness
4. Backfill, re-run, or adjust configuration as needed
5. Review the impact scope and recovery status

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [Launch Check and Troubleshooting Guide](studio-launch-check-and-troubleshooting-guide.md)
- [Task and Instance Operations](task-instance-maintenance.md)
- [Scheduling Instance Configuration](task_instance.md)

</td>
</tr>
</table>

&nbsp;

<table style="width:100%; table-layout:auto; border-collapse:separate; border-spacing:0 0;">
<tr>
<td colspan="2" style="background:#F8FAFC; border:1px solid #E2E8F0; border-bottom:2px solid #2563EB; font-weight:700; font-size:13px; padding:10px 16px; border-radius:8px 8px 0 0; overflow-wrap:break-word; color:#1E293B;">
Govern and Browse Data Assets
</td>
</tr>
<tr>
<td colspan="2" style="border:1px solid #E2E8F0; border-top:none; border-bottom:none; padding:8px 16px 10px; font-size:12px; color:#64748B; overflow-wrap:break-word;">
View table, field, quality, permission, approval, and lineage information, and progressively turn development output into governable, reusable data assets.
</td>
</tr>
<tr>
<td style="width:55%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-right:none; border-radius:0 0 0 8px; padding:10px 16px; overflow-wrap:break-word;">

**Typical steps**

1. View tables and metadata in the data catalog
2. Handle permission requests and approval workflows
3. Monitor data quality and governance information
4. Return to the development or scheduling phase for corrections as needed

</td>
<td style="width:45%; vertical-align:top; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 8px 0; padding:10px 16px; overflow-wrap:break-word;">

**Reference**

- [Data Catalog](data_catalog.md)
- [Data Quality](data-quality.md)
- [Permission Requests](permission-application.md)
- [Approval Tickets](approval-list.md)

</td>
</tr>
</table>

---

If you are facing a complete goal, start from this document to locate the entry point, then go into the detailed documentation for the corresponding module. If you already know you are working on a task, instance, dependency, backfill, or publish issue, you can go directly to the relevant topic document.

To get an overview of what modules Studio has, see [Studio Overview](studio_overview.md).
