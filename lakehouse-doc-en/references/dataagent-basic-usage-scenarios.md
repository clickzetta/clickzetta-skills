# Data Engineering Agent — Basic Usage Scenarios

This guide targets first-time users of the Data Engineering Agent and introduces the most common, most accessible basic scenarios. Compared to full data pipelines, scheduling and publishing, and operations diagnosis, these scenarios are better suited to getting familiar with the Agent's interaction style, capability boundaries, and entry points.

The core usage pattern behind these basic scenarios is not "state all requirements upfront in one go," but rather:

- Ask an exploratory question first
- Narrow down objects and scope based on what the Agent returns
- Then move to querying, creating drafts, executing, or diagnosing

For first-time users, this approach is usually more natural and easier to turn into a stable habit.

## Who This Guide Is For

- Data engineers using the Data Engineering Agent for the first time
- Users who need to quickly understand the state of data, tasks, and jobs in Lakehouse
- Users who want to complete SQL queries, task drafts, and tool configuration queries through natural language
- Teams that want to start with low-risk operations to experience the Agent

## Basic Interaction Entry Point

After entering Lakehouse, you can open the agent through the Data Agent entry point on the page, or type directly into the input box in the bottom right. The input box supports continuous conversation — ask a simple question first, then follow up based on the Agent's response.

Usage notes:

- The bottom-right input box is for on-the-spot questions; no need to navigate to complex configuration pages first
- The remaining context or token count is displayed next to the input box as a prompt for how much context the current session can still hold
- Some buttons and states on the page have hover tooltips; mouse over to see meanings
- For low-risk operations like read-only queries, table schema exploration, and documentation queries, the Agent can usually complete them directly
- For change operations like creating tasks, publishing schedules, writing data, and rerunning tasks, the Agent should explain the impact scope and request confirmation first

## Explore First, Execute Later

For first-time users, the easiest way to get started is usually not to immediately have the Agent create tasks, publish schedules, or rerun jobs, but to start with exploratory questions.

Scenarios that are better suited to exploring first:

- You don't yet know which tables, tasks, directories, or jobs exist
- You are unsure what tools and permissions are open in the current environment
- You don't know why a task didn't run
- You are unsure whether an existing object can be reused

Good opening questions for these:

- Help me see what task directories and data tables are in the current workspace.
- Help me decide whether this requirement is better as a one-time query or should be formalized into a task.
- Help me check the most recent run status for this task.

Once objects and scope are clear, moving into execution is more stable:

- Create a SQL draft task in the `Test Tasks/Temp Development` directory.
- Save the SQL I'm about to give you into it.
- If the execution result looks correct, continue to publish.

## Scenario 1: Ask the Agent What It Can Do

The first time you use the Agent, have it describe its capability scope.

Recommended question:

> What data engineering capabilities do you have? Please explain by category: SQL development, task development, scheduling and publishing, operations diagnosis, data source sync, data quality, MCP/CLI integration.

Good information to get:

- What work types the Agent supports
- Which capabilities are read-only queries
- Which capabilities modify the environment
- Which operations require confirmation
- What tool capabilities are open in the current workspace

This scenario is suited to building an overall understanding of the Data Engineering Agent before running any high-impact operations.

## Scenario 2: View Table Schema and Sample Data

When you are unfamiliar with a table, have the Agent view the schema and a small amount of sample data first, then explain field meanings.

Recommended question:

> Please view the table schema and a small amount of sample data for `public.demo_xe_sales`. Explain the possible business meaning of each field and identify which fields are suited for dimensions and which for metrics. Do not create tasks. Do not write data.

Good information to get:

- Field names and types
- Possible business meaning of each field
- Fields suited for filtering, grouping, sorting, or aggregation
- Fields that may be ambiguous or need business confirmation

This type of read-only exploration is the foundation for subsequent SQL development, task development, and data warehouse modeling.

## Scenario 3: Run a Simple Read-Only Query

If you just need to confirm a data result on an ad-hoc basis, have the Agent generate and run a read-only query directly.

Recommended question:

> Help me query `public.demo_xe_sales` for total sales and order count by product for each of the last 7 days. Only run a read-only query. Do not create tasks. Do not write to tables.

Good information to get:

- The SQL the Agent generates
- Query results
- Description of the query definition
- Whether it's worth formalizing into a task later

If the query is slow or the data volume is large, narrow the time range, add filter conditions, or first have the Agent explain the query plan and potential performance risks.

If you are unsure whether it's worth formalizing into a task, follow up:

> If this query needs to run every day going forward, would it be better to keep as an ad-hoc query or create a Studio task draft?

## Scenario 4: Formalize a Query into a Studio Task Draft

When a query needs to run repeatedly or may enter scheduling later, have the Agent create a Studio task draft.

Recommended question:

> Based on `public.demo_xe_sales`, create a SQL task draft named `sales_product_daily_summary` in Studio task directory `Test Tasks/Temp Development`. If the directory doesn't exist, tell me first — I'll create it in Studio; do not create in the default directory. Aggregate total sales, order count, and average order value for the last 7 days by `sale_date` and `product_name`. Only create a draft. Do not execute SQL. Do not create the target table. Do not publish schedules. Before creating, describe the task name, directory, SQL type, and impact scope, and request my confirmation.

After creation, check:

- Whether the task appears under the specified task directory
- Whether the task status is unscheduled
- Whether the SQL matches expectations
- Whether the SQL is a read-only query, CREATE TABLE, INSERT, or overwrite write
- Whether it references the correct catalog, schema, and table

A draft task does not run automatically, but if the SQL is a CREATE TABLE or write SQL, manually running or publishing it later will actually affect data.

## Scenario 5: Have the Agent Explain a Task Draft

After creating a task draft, have the Agent explain the task content and risk points.

Recommended question:

> Please check the SQL content of task `{task_name}`, describe whether it is a read-only query, CREATE TABLE, INSERT, or overwrite write. List which tables will be affected when it runs, and identify risks to check before publishing.

Good information to get:

- SQL type
- Input and output tables
- Whether running it will create or write data
- Whether task dependencies need to be configured
- Whether data quality checks should be added
- Whether it is suited to publish as a periodic task

This scenario is suited for use before a task moves from draft to run or publish.

## Scenario 6: View Job History and Run Status

If you have already executed SQL or tasks, have the Agent help view job history and run status.

Recommended question:

> Please view the job history I submitted in the last 24 hours, grouped by success, failure, and running. If there are failed jobs, list the job ID, failure time, and error summary. Do not rerun tasks.

Good information to get:

- Recent job run summary
- Count by success / failure / running
- Failed job IDs
- Error summaries
- Whether further SQL Profile or log review is needed

To diagnose a specific failed job, follow up:

> Please analyze the failure cause of job `{job_id}`, focusing on the error log, SQL Profile, and stage/operator information. Return diagnostic results only; do not rerun.

## Scenario 7: Query MCP / CLI / SDK Configuration

The Data Engineering Agent is also suited for querying Lakehouse external integration methods, such as MCP Server, CLI, JDBC, and Python SDK.

Recommended question:

> Please explain how to configure MCP Server for the current Lakehouse and how to connect through CLI or SDK. Provide setup steps and important notes. Do not modify any environment configuration.

Good information to get:

- MCP Server entry point and purpose
- CLI/SDK connection methods
- Authentication and permission requirements
- Common configuration errors
- Related product documentation

This type of question is generally instructional and does not directly modify the environment.

## Scenario 8: Have the Agent Run Pre-Operation Checks

Before executing high-impact operations such as create, publish, rerun, backfill, unpublish, or delete, have the Agent run a check first.

Recommended question:

> I am planning to `{operation}` on task `{task_name}`. Please first check whether it is published, whether it has downstream dependencies, whether it has run history, whether it belongs to a task group, and whether it will affect business output. Return the impact scope only; do not execute the operation.

Good information to get:

- Whether the task is published
- Whether downstream dependencies exist
- Whether there is run history
- Whether it belongs to a task group or pipeline chain
- Which business outputs the operation may affect
- Whether continuing with the operation is recommended

Whether deletion operations can be completed directly by the Agent depends on the open tool capabilities. If the Agent cannot perform deletion directly, perform the operation manually in the product interface and have the Agent assist in confirming the impact scope.

## Basic Usage Recommendations

When first using the Data Engineering Agent, follow this order:

- Ask about capability scope first to understand what it can do
- Perform read-only exploration first to understand table schemas and sample data
- Then run read-only queries to validate SQL and results
- Then create task drafts to formalize reusable logic
- Check task directory, SQL type, and impact scope in the IDE
- Before publishing, scheduling, rerunning, or backfilling, have the Agent perform an impact check first

Low-risk operations are suited to direct natural language completion. High-impact operations should be preceded by reviewing the impact scope before confirming execution.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
