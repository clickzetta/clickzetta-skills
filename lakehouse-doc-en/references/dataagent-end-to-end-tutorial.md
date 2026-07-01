# Data Engineering Agent End-to-End Tutorial

This tutorial shows how to complete one full cycle from data exploration to task diagnosis using the typical Data Engineering Agent flow. The tutorial uses a sales analytics scenario as an example, focusing on what to ask the Agent at each step, what the user should confirm, and when to move to the next step.

The complete flow includes:

- Data exploration
- Metric definition design
- Build the data warehouse
- Create a pipeline
- Task diagnosis

## Explore First, Then Work Through the Full Flow

While this is an end-to-end tutorial, in actual usage you do not need to know the complete path from the start.

The more natural approach is:

- First have the Agent help you review tables, existing tasks, directories, and current state
- Based on this information, decide whether to confirm metric definitions first, create a layer design plan, or create draft tasks first
- After each step is confirmed, continue to the next

If you are not yet familiar with this table, the current directory, or existing tasks, start by asking:

> Please first view the table schema and a small amount of sample data for `public.demo_xe_sales`, and check whether there are any related tasks in the current directory. Tell me how this requirement is best approached; do not create tasks yet.

This type of exploratory start is generally more stable than immediately requesting the entire flow.

## Scenario Goal

Assume a sales detail table:

```text
public.demo_xe_sales
```

The goal is to:

- Understand the table schema and field meanings
- Design core metrics for sales analytics
- Design a Silver/Gold or DWD/DWS layer plan
- Create Studio SQL draft tasks
- Configure scheduling and run pre-publishing checks
- Locate the cause of failures when they occur and decide whether to rerun

## Data Exploration

Have the Agent do read-only exploration. Do not create tasks; do not write data.

Recommended question:

> Please view the table schema and a small amount of sample data for `public.demo_xe_sales`. Describe field meanings, fields suited for dimensions or metrics, time fields, and possible data quality risks. Read-only exploration only; do not create tasks, do not write to tables.

Users should pay attention to:

- Which fields are amounts, quantities, times, customers, and products
- Whether null values or anomalies exist
- Whether date fields are business time or system time
- Whether status fields, refund fields, or validity flags exist

After completing data exploration, move to metric design.

## Metric Definition Design

Have the Agent design metric definitions based on field meanings.

Recommended question:

> Please run a metric definition design based on `public.demo_xe_sales`. Identify dimension fields, metric fields, time fields, filter fields, and system fields. Design core metrics including total sales, order count, average order value, and product sales ranking. Describe the business definition, calculation logic, aggregation granularity, and definition risks for each metric. Do not create tasks.

Users should confirm:

- Which amount field to use for total sales
- Whether order count is order line count or order count
- Whether average order value is per order or per customer
- Which date field to use for business analytics
- Whether to exclude refund, cancelled, or invalid records

Do not enter production modeling without confirming metric definitions.

## Build the Data Warehouse

After metric definitions are confirmed, have the Agent design the layer plan.

Recommended question:

> Based on the metric definitions just discussed, design a Silver/Gold layer plan. Silver does field standardization and basic cleaning; Gold aggregates total sales, order count, and average order value by date and product. Output the plan and each layer's input/output first; do not create tasks.

Users should check:

- Whether each layer's goal is clear
- Whether input and output tables are correct
- Whether cleaning rules align with business definitions
- Whether aggregation granularity meets analytics requirements
- Whether tables need to be written
- Whether scheduling dependencies are needed

After confirming the plan, have the Agent create task drafts.

## Create a Pipeline

Before creating a pipeline, prepare the task directory. Test tasks can go in:

```text
Test Tasks/Temp Development
```

Production tasks should go in a stable business domain or project directory.

If you are unsure whether the directory is appropriate or whether there are existing tasks to reuse, ask first:

> Before creating drafts, please first help me check which directories are suitable for this task set and whether any related drafts already exist. Do not create tasks yet.

Recommended question:

> Confirmed — create two SQL draft tasks per this plan. Create all tasks under Studio task directory `{task_directory}`. Only create drafts. Do not execute SQL. Do not create target tables. Do not publish schedules. After creation, return task ID, task name, task path, and whether any environment was modified.

After drafts are created, check in the IDE:

- Whether tasks are in the correct directory
- Whether SQL references the correct tables
- Whether SQL is read-only, CREATE TABLE, INSERT, or overwrite write
- Whether target table names follow naming conventions
- Whether Gold references the correct Silver output

If creating composite tasks, Flows, or multi-node tasks, also check:

- Whether the expected nodes appear on the canvas
- Whether dependency edges exist between nodes
- Whether the DAG is empty
- Whether node content truly belongs to the composite task rather than being scattered as standalone tasks

Take the actual Studio canvas results as the source of truth for this step — do not assume success based solely on the Agent's "dependency created" response.

## Configure Scheduling and Pre-Publishing Checks

Save and check scheduling configuration before publishing; do not publish directly.

If you are unsure whether this task set is ready to enter the scheduling and publishing phase, ask first:

> Please first assess whether this task set currently meets the conditions to enter scheduling and publishing. If not, describe what checks are still missing.

Recommended question:

> Please check whether task `{task_id}` meets publishing conditions, including SQL type, target table, scheduling config, dependency relationships, retry strategy, timeout, VCluster, recent run history, and downstream impact. Do not modify configuration; return check results and risk recommendations only.

Before publishing, confirm:

- Cron expression
- VCluster
- Retry and timeout
- Upstream/downstream dependencies
- Whether the task runs immediately after publishing
- The next scheduled run time
- How to unpublish

After confirming everything, publish:

> Confirmed — publish task `{task_id}`. After publishing, return the publish state, current version, and next scheduled run time. Do not manually run the task.

## Task Diagnosis

When a task fails, do not rerun immediately. Have the Agent diagnose first.

If you don't know which instance to start from, checking the most recent run status is generally the most stable approach.

If you know the instance ID:

> Please diagnose the failed run of task `{task_id}`. The scheduling instance ID is `{schedule_instance_id}` and the execution instance ID is `{execute_instance_id}`. Return run status, error summary, root cause judgment, evidence, impact scope, whether rerun is recommended, and fix recommendations. Do not publish, do not rerun, do not modify the task.

If you don't know the instance ID:

> Please view the run history of task `{task_name}` in the last 24 hours. If there are failures or timeouts, list the scheduling instance ID, execution instance ID, failure time, error summary, and recommended next steps. Do not rerun tasks; do not modify configuration.

A diagnostic report should answer:

- At which phase the failure occurred
- Whether it was SQL, permissions, missing table, resource, scheduling dependency, or data anomaly
- Whether data was already written
- Whether downstream is affected
- Whether rerun is recommended
- What the fix steps are

## When Monitoring Is Empty

In new workspaces, test workspaces, or workspaces that have not run for a long time, there may be no instance data in the run monitoring view. This does not indicate a feature anomaly — it means:

- No tasks ran within the recent time window
- No failed instances exist
- No backfill tasks exist

If there is no data in the last 24 hours, consider also checking:

- Whether there are run records in the last 30 days
- Whether tasks were only created as drafts but never executed or published
- Whether the current workspace is used only for development and validation

An empty monitoring view is a normal result and should not be treated as an anomaly.

## Clean Up Test Tasks

Clean up test tasks after they are done.

Before cleanup, confirm:

- Whether the task is published
- Whether it has downstream dependencies
- Whether run records need to be preserved
- Whether the draft can be deleted from the Studio UI

Recommended question:

> Please check whether test task `{task_id}` is published, has downstream dependencies, and has run history. If it can be cleaned up, tell me the cleanup steps. Do not delete directly.

## Next Steps

- [Data Engineering Agent](dataagent.md)
- [Basic Usage Scenarios](dataagent-basic-usage-scenarios.md)
- [Metric Design Guide](dataagent-metric-design-guide.md)
- [Data Pipeline and Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
- [Safe Operation Guide](dataagent-safe-operation-guide.md)
