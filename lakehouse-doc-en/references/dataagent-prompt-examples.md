# Data Engineering Agent Prompt Examples

This guide provides commonly used prompt templates for the Data Engineering Agent. Copy templates directly and replace table names, task names, field names, task directories, and time ranges with your own business objects. For change operations involving scheduling and publishing, rerun/backfill, data quality rule creation, or data source sync, have the Agent output the impact scope and request confirmation first.

Complete execution prompts typically include six types of information:

- **Goal**: query, model, create task, configure scheduling, publish, diagnose, or govern
- **Object**: which catalog, schema, table, task, task group, or job instance is involved
- **Location**: when creating Studio tasks, specify the existing task directory or folder
- **Scope**: time range, partition range, business filter conditions, whether historical data is included
- **Output**: plan only, create draft only, run query, create target table, publish schedule, or return diagnostic report
- **Constraints**: whether query execution is allowed, whether table creation/write is allowed, whether publishing is allowed, whether confirmation is required first

This does not mean all users need to provide all this information upfront in one go.

The more natural approach is:

- Use exploratory questions first to confirm objects and scope
- Then use complete execution prompts to drive tasks to completion

## Explore First, Execute Later

These questions work better as an opening, helping the Agent clarify the problem.

### Explore the current environment and objects

> Please first view which data tables, Studio task directories, and recently run tasks are in the current workspace. Read-only exploration only; do not create tasks; do not modify configuration.

### Explore where to start for a requirement

> I want to create a daily order report. Please first check which tables and existing tasks might be relevant, then tell me whether the next step should be to run a query, create a draft task, or first confirm the metric definitions.

### Explore whether tasks can be reused

> Please check whether there are existing tasks in the current task directory related to `{requirement}` that can be reused. If so, provide the task name, directory, current state, and whether it is published. Do not create new tasks yet.

### Explore what a task is currently missing

> Please check what configuration task `{task_name}` is currently missing before it can enter execution or publishing. Do not modify configuration yet.

### Explore the most recent run status

> Please check the most recent run status of task `{task_name}`. If there are failures or timeouts, tell me which instance or log to investigate next.

## Confirm What the Agent Can Do First

Use this when entering the Data Engineering Agent for the first time, or when unsure what tools and permissions are open in the current environment.

> Please describe what data engineering work you can currently help me with, which operations only read information, and which operations modify Studio tasks, scheduling configuration, data sources, or data tables. Distinguish between "can execute directly," "execute after my confirmation," and "must be done manually in the interface."

To confirm the current context:

> Please first view the current workspace, available catalog/schema, Studio task directories, and available tools. Read-only exploration only; do not create tasks; do not modify configuration.

## Ad-hoc Data Query

Suited for quickly confirming a data result without needing to formalize it as a periodic task.

> Help me query `{schema}.{table}` for `{time_range}`, aggregating `{metrics}` by `{dimensions}`. Read-only query only; do not create tasks; do not write to tables.

Example:

> Help me query `public.demo_xe_sales` for daily sales and order count by product for each of the last 7 days. Read-only query only; do not create tasks; do not write to tables.

## Explain Table Schema and Field Meanings

Suited for taking over an unfamiliar table, or when field names are similar and easy to misuse.

> Please view the table schema and a small amount of sample data for `{schema}.{table}`. Explain the possible business meaning of each field and identify which fields are easy to confuse. Do not create tasks; do not write data.

If you already know the business definitions, add context:

> `{field_a}` is the order amount; `{field_b}` is the net amount after refunds. Use `{field_b}` for sales figures in this analysis. Generate the query SQL based on this definition.

## Metric Definition Design

Suited for unifying business definitions before modeling and development, avoiding inconsistencies across tasks, dashboards, and analysis results.

> Please run a metric definition design based on `{schema}.{table}`. Read-only exploration only — view the table schema and a small amount of sample data; then identify dimension fields, metric fields, time fields, filter fields, and system fields; then design a set of core metrics describing metric name, business definition, calculation logic, aggregation granularity, available dimensions, and definition risks. Do not create tasks; do not write to tables; do not modify configuration.

If business definitions are potentially ambiguous, follow up:

> Please check which metrics have the most ambiguous definitions, focusing on amount fields, date fields, ID fields, status fields, and aggregation granularity. Output a list of questions that need business confirmation.

## Create an SQL Draft Task

Suited for formalizing a query or transformation into a Studio task without publishing yet.

Always specify the task directory when creating a task — do not let the Agent guess. If the target directory does not yet exist, create it in the Studio task tree first, then have the Agent create the task draft.

> Based on `{schema}.{source_table}`, create an SQL task draft named `{task_name}` under Studio task directory `{task_directory}`. Logic: `{transformation or aggregation logic}`. Only create a draft. Do not execute SQL. Do not create target tables. Do not publish schedules. If the directory does not exist, stop and tell me — I'll create it in Studio first. Before creating, describe the task name, directory, SQL type, and impact scope, and request my confirmation.

Example:

> Based on `public.demo_xe_sales`, create an SQL task draft named `sales_product_daily_summary` under Studio task directory `Sales Analytics/Daily Summary`. If the directory does not exist, stop and tell me — I'll create it in Studio first. Aggregate total sales, order count, and average order value for the last 7 days by `sale_date` and `product_name`. Only create a draft. Do not execute SQL. Do not create target tables. Do not publish schedules. Before creating, describe the task name, directory, SQL type, and impact scope, and request my confirmation.

For feature testing, use a temp directory with more conservative constraints:

> Please create an SQL draft task named `{task_name}` under Studio task directory `Test Tasks/Temp Development`. Generate draft only. Do not execute SQL. Do not configure scheduling. Do not publish. If the directory does not exist, stop and tell me — I'll create it in Studio first.

## Review a Draft Task

Suited for checking the Agent's generated SQL after task creation.

> Please view the draft content of task `{task_id or task_name}`. Return the task directory, task type, SQL summary, input tables, output tables, whether it will write data, whether scheduling is configured, and whether it is published. Do not modify the task.

To have the Agent explain the SQL:

> Please explain the SQL logic of task `{task_name}` section by section, describing each CTE/subquery's purpose, aggregation granularity, filter conditions, and potential data quality risks. Do not execute the task; do not modify the task.

## Create Layered Data Pipeline Drafts

Suited for having the Agent generate a warehouse layer plan first, then create multiple task drafts.

> Based on `{schema}.{source_table}`, design a `{Bronze/Silver/Gold or ODS/DWD/DWS/ADS}` layer plan. `{layer requirements}`. Show the plan and each layer's input/output first, then create SQL draft tasks. Create all tasks under Studio task directory `{task_directory}`. If the directory does not exist, stop and tell me — I'll create it in Studio first. Do not publish schedules; do not execute write SQL.

Example:

> Based on `public.demo_xe_sales`, design a small Silver/Gold layer plan. Silver does field standardization and basic cleaning; Gold aggregates total sales, order count, and average order value for the last 7 days by date and product. Show the plan and each layer's input/output first, then create two SQL draft tasks. Create all tasks under Studio task directory `Sales Analytics/SilverGold Drafts`. If the directory does not exist, stop and tell me — I'll create it in Studio first. Do not publish schedules; do not execute write SQL.

## Create a Composite Task

Suited for creating multi-node tasks, reviewing canvas structure, or validating task group capabilities.

To create a composite task itself:

> Please create a composite task draft named `{task_name}` under Studio task directory `{task_directory}`. Only create the object; do not execute; do not publish. After creation, return the task ID, directory, current DAG node count, and whether it is published.

To understand how task group configuration works:

> Please create a composite task and explain whether the `task group` field should be set to "Yes" or "No," and which additional fields need to be filled in after selecting. Do not submit the creation yet.

To add nodes and bind dependencies in a composite task:

> Please add two nodes to composite task `{task_id or task_name}` and configure the second node to depend on the first. After completion, return the node list and dependency edges, and explicitly state whether the DAG is empty. Do not execute; do not publish.

## Review Composite Task and DAG

Suited for confirming that nodes and dependencies actually exist on the canvas after creating a composite task or Flow.

> Please check the actual DAG of composite task `{task_id or task_name}`. Return node count, node names, node types, a SQL or code summary for each node, and dependency edges between nodes. Explicitly state whether the DAG is empty. Do not execute; do not publish; do not modify configuration.

If you suspect the Agent only created the object but did not build the graph:

> Please do not just return "creation succeeded." Use the actual Studio canvas results as the source of truth and tell me whether you actually see nodes and connections.

## From Metrics to Warehouse

Suited for converting metric definitions into Silver/Gold or DWD/DWS task pipelines after metric design is complete.

> Please design a metric-to-warehouse plan based on `{schema}.{table}`. Read-only exploration only — identify field roles and core metrics; then design a Silver/Gold layer model describing each layer's input, output, field processing logic, metric definitions, and definition risks. Do not create tasks; do not execute SQL.

If SQL output is needed after the plan is confirmed:

> Please generate complete SQL based on the plan above, including CREATE TABLE and INSERT SQL for the Silver detail table, Gold daily summary table, and Gold ranking table. Output SQL only; do not create tasks; do not execute SQL; do not publish schedules.

If Studio draft tasks need to be created:

> Confirmed — create Studio SQL draft tasks. Task directory: `{task_directory}`. First list the task inventory, input tables, output tables, dependencies, SQL type, and write impact, and request my confirmation. Only create drafts; do not execute SQL; do not publish schedules. If the directory does not exist, stop and tell me — I'll create it in Studio first.

## Configure Scheduling and Dependencies

Suited for draft tasks that have passed review and need configuration before entering periodic runs. These operations modify task configuration or publish state — confirm impact scope first.

> Please configure task `{task_name}` to run `{schedule interval}`, retry on failure `{count}` times with `{interval}` between retries. If scheduling, dependencies, or publishing need to be modified, show the configuration changes first and request my confirmation.

Example:

> Please configure task `gold_product_daily_summary` to run daily at 2:00 AM, triggered after `silver_order_clean` completes successfully, with 2 retries on failure and 10-minute intervals between retries. Before publishing, show the scheduling configuration and dependencies that will be changed, and request my confirmation.

To save scheduling configuration without entering the scheduling system:

> Please configure scheduling parameters for task `{task_id}`, but do not publish the task yet. Requirements: `{schedule interval}`, `{count}` retries on failure, `{minutes}` minute timeout, depend on `{dependency task or no dependency}`. Do not execute the task; do not publish; do not run immediately. Before configuring, describe what will be changed, whether it will enter the scheduling system, and whether it will produce run instances — and request my confirmation.

After saving configuration, confirm:

> Please return the current task status, cron, retry, timeout, VCluster, whether published, and whether there is a next scheduled run time. Explain the difference between saving scheduling configuration and publishing a task.

## Pre-Publishing Check

Suited for a final check before a task goes live.

> Please check whether task `{task_name}` meets go-live conditions, including SQL type, target table, scheduling configuration, dependency relationships, retry strategy, compute cluster, recent run history, and downstream impact. Do not modify configuration; return check results and risk recommendations only.

For data output tasks, add:

> Please specifically check whether the run will create, insert, or overwrite tables, and whether data quality rules need to be added.

Confirm scheduling impact separately before publishing:

> Please prepare to publish task `{task_id}` to the scheduling system. Before publishing, describe task name, directory, SQL type, cron, retry, timeout, VCluster, dependencies, whether it will run immediately after publishing, next scheduled run time, and how to pause or unpublish. Request my confirmation first; do not publish directly.

When confirming publication:

> Confirmed — publish task `{task_id}`. After publishing, return the publish state, current version, and next scheduled run time. Do not manually run the task.

For validation only:

> This is a test task. After publishing, do not run manually; after returning the publish state, I will immediately request unpublish.

## Check Task Status and Run History

Suited for confirming whether a task is published, has run, or has a next scheduled run.

> Please view the current status of task `{task_id or task_name}`. Return task directory, task type, whether published, current version, recent run records, next scheduled run time, and the most recent failure reason. Do not modify configuration.

For scheduling status only:

> Please only check the publish state and scheduling information for task `{task_id}`. Return publish state, cron, VCluster, and next scheduled run time. Do not publish, unpublish, or execute the task.

## Unpublish and Clean Up Test Tasks

Suited when a task is published but subsequent scheduled triggers need to stop, or test artifacts need cleanup.

Confirm impact before unpublishing:

> Please unpublish task `{task_id}` using `undeploy` to remove it from the scheduling system. Do not delete the task draft. Do not execute the task. Do not affect other tasks. Before the operation, describe the action, whether it will cancel the next scheduled run, whether the task draft is preserved, and request my confirmation.

Confirm unpublishing:

> Confirmed — execute `undeploy` on task `{task_id}` only. Do not delete drafts; do not execute tasks; do not affect other tasks. After completion, return the current publish state and whether the next scheduled run has been cancelled.

Before cleanup:

> Please check whether task `{task_id}` is published. If it is, unpublish it first; after confirming the task has been removed from the scheduling system, tell me I can delete the draft from the interface. Do not delete other tasks.

After manually deleting in the interface:

> I have deleted test task `{task_id}` from the interface. Please confirm whether this task name or ID still exists in the task tree.

## Review VCluster and Run Impact

Suited for confirming the compute cluster and run impact before scheduling and publishing.

> Please view the current task details for task `{task_id}`. Return schema, VCluster, cron, retry count, timeout, whether published, and next scheduled run time. Do not modify configuration.

If the Agent returns inconsistent VCluster values:

> You returned different VClusters before and after. Please re-read the task details and explain which VCluster the task will actually use after publishing. Do not publish or execute the task.

For read-only queries, also confirm:

> Please state whether this task will only read data when run, or whether it will create, insert, update, delete, or overwrite any tables. Base your answer on the SQL content.

## Operations Diagnosis

Suited for task failure, timeout, empty results, or unexpected output.

> Please analyze the failure cause of job instance `{job_id or instance_id}`, focusing on the error log, SQL Profile, stage/operator information, and upstream dependencies. Return root cause judgment, impact scope, and fix recommendations. Do not rerun the task unless I confirm.

If you don't know the specific instance:

> Please view the run history of task `{task_name}` in the last 24 hours. If there are failures or timeouts, list the instance ID, failure time, error summary, and recommended next steps.

With run instance and execution instance IDs:

> Please diagnose the failed run of task `{task_id}`. The scheduling instance ID is `{schedule_instance_id}` and the execution instance ID is `{execute_instance_id}`. Return run status, error summary, root cause judgment, evidence, impact scope, whether rerun is recommended, and fix recommendations. Do not publish, do not rerun, do not modify the task.

Before rerunning:

> Please assess whether this failed task is suitable for rerunning. First check whether the root cause has been fixed, whether there was partial writing, whether downstream tasks are affected, and whether rerunning would produce duplicate data. Do not rerun directly.

## Data Quality Rule Recommendations

Suited for pre-go-live checks or data anomaly investigation. Have the Agent output rule recommendations first; confirm rule type, blocking behavior, and impact scope before creating, modifying, or deleting rules.

> Based on the table schema and business meaning of `{schema}.{table}`, design data quality check rules. Focus on null values, uniqueness, amount ranges, date partition completeness, enum value validity, and data volume fluctuation. Output rule recommendations only; do not create rules.

To proceed with creating rules:

> Confirmed — create these data quality rules. Before creating, explain the difference between strong rules and weak rules, and whether failures will block tasks.

To query existing rules first:

> Read-only operations only: list the DQC data quality rules associated with `{schema}.{table}`, or confirm none exist. Return rule name, rule type, check target, weak/strong/blocking level, and trigger method. Do not create, modify, or delete any rules.

To create a low-risk test rule:

> Please create a DQC rule for `{schema}.{table}` for testing purposes only. Rule name: `{rule_name}`. Requirements: check `{rule_condition}`, use `{weak rule/strong rule}`, trigger method `{REST/manual}`. Do not bind to production tasks. Do not execute the rule. Do not publish schedules. Do not modify data. After creation, return the rule ID, rule type, check target, threshold, weak/strong/blocking level, and trigger method.

To delete a test rule and confirm cleanup:

> Please delete the test DQC rule just created, with rule ID `{rule_id}`. Only delete this test rule; do not delete other rules. After deletion, query the DQC rules for `{schema}.{table}` again to confirm the cleanup.

## Run Monitoring and Empty State Explanation

Suited for understanding why the monitoring page has no data, or first confirming whether there are actually instances to diagnose.

> Read-only operations only: view the run monitoring information for the current workspace in the last 24 hours. Return recently run tasks/instances, status breakdown, whether there are failed instances, whether there are backfill tasks, and what details can be viewed next. Do not rerun, terminate, mark success/failure, or create backfill tasks.

If the last 24 hours are empty:

> Please expand the run monitoring range to the last 30 days and check whether there are any run instances, failed instances, scheduling instances, or backfill tasks. If still empty, explain whether this is because there is no run history or because the query range or workspace selection is incorrect. Do not take any action.

To determine whether an empty state is normal:

> Please explain why the current workspace has no run instances in the last 24 hours or 30 days. Distinguish between "no run history," "tasks not published," and "query time range is incorrect." Do not take any action.

## Data Source and Sync Troubleshooting

Suited for data ingestion, sync delay, or sync failure scenarios. Data source creation, sync task creation, and sync configuration changes are change operations — output the plan and request confirmation first.

> Please check the sync status of data source `{datasource_name}` in the last 24 hours, including sync delay, failure records, error summary, and affected target tables. Do not modify sync configuration; return diagnostic results only.

Before creating a sync task:

> Please design a sync plan from `{source}` to `{target}`. Describe whether full sync, incremental, or CDC is appropriate, how to set the sync frequency, and what primary key, time field, and permission requirements might exist. Output the plan only; do not create tasks.

## MCP, CLI, and SDK Configuration Review

Suited for troubleshooting external tool connections, automation integration, or local development environment configuration.

> Please view the MCP Servers, CLI, or SDK configuration in the current workspace and describe which integration scenarios each is suited for. Only view configuration; do not add, delete, or modify connections.

To prepare an integration plan:

> I want to integrate Data Engineering Agent capabilities through `{MCP / CLI / SDK}`. Please first describe what authentication, network conditions, permission scope, and security considerations are needed. Output the integration checklist only; do not modify any configuration.

## High-Impact Operation Confirmation

Before delete, unpublish, backfill, rerun, modify dependencies, or modify scheduling interval — use stricter confirmation templates. Whether deletion operations can be completed directly by the Agent depends on the open tool capabilities; if direct deletion is not possible, perform the operation manually in the interface.

> I am planning to `{operation}` on `{object}`. Please first check whether it is published, has downstream dependencies, has run history, belongs to a task group, and whether it will affect business output. Return the impact scope only; do not execute the operation.

After confirming:

> Confirmed — execute, operating on `{object}` only. Do not modify other objects. After execution, return the result and verify whether the state matches expectations.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Basic Usage Scenarios](dataagent-basic-usage-scenarios.md)
- [Safe Operation Guide](dataagent-safe-operation-guide.md)
- [End-to-End Tutorial](dataagent-end-to-end-tutorial.md)
- [Metric Design Guide](dataagent-metric-design-guide.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
- [Task Directory and Governance Guide](dataagent-task-directory-governance-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Pipeline Launch Checklist](dataagent-pipeline-launch-checklist.md)
- [Data Pipeline and Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
- [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
- [DQC Data Quality Rules Guide](dataagent-dqc-guide.md)
- [Operations Monitoring Guide](dataagent-monitoring-guide.md)
- [Common Misunderstandings](dataagent-common-misunderstandings.md)
