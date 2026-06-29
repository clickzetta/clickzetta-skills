# Data Engineering Agent Task Development Guide

This guide covers how to use the Data Engineering Agent to create Studio task drafts and review task content before publishing. Task development is one of the most common uses of the Data Engineering Agent — suited for SQL development, data cleaning, metric aggregation, data warehouse layering, and formalizing ad-hoc engineering work.

## When to Use This

You can ask the Data Engineering Agent to:

- Generate SQL task drafts from natural language
- Design cleaning or aggregation logic based on existing table schemas
- Create SQL task drafts and help generate Python / Shell / Flow / JDBC task content
- Write code, parameters, and descriptions for tasks
- Check whether a task is saved, scheduled, or published
- Explain the impact of running a task before publishing

If you only need to check a result one time, have the Agent run a read-only query first. If this logic needs to run repeatedly, produce data output, or enter scheduling, have the Agent create a Studio task.

## Explore First, Then Create Tasks

Task development is not always suited to immediately asking the Agent to create tasks.

The more natural approach is:

- Explore which tables, directories, and existing tasks are available first
- Decide whether this is better as a one-time query, SQL draft, Python task, or composite task
- Once the object and goal are clear, actually create the task

Scenarios better suited to exploring first:

- You don't yet know which directory the task should go in
- You are unsure whether the current directory has reusable tasks
- You are unsure whether SQL, Python, Shell, or Flow is the better fit
- You are unsure whether this requirement is worth formalizing into a task

Better opening questions:

- Help me check which directories are suitable for this task.
- Help me check whether there are existing tasks in the current directory that can be reused.
- Help me decide whether this requirement is better as an SQL task or Python task.

Once the directory, task type, and goal are clear, moving into creation is more stable.

## Recommended Workflow

### State Goal and Boundaries First

Before creating tasks, tell the Agent clearly:

- What type of task to create
- Which Studio task directory to put it in
- Which source tables to use
- What result to produce
- Whether to only create a draft or allow execution, table creation, publishing
- Whether confirmation is needed first

Example:

> Based on `public.demo_xe_sales`, create an SQL task draft that aggregates total sales, order count, and average order value for the last 7 days by `sale_date` and `product_name`. Only create a draft. Do not execute SQL. Do not create target tables. Do not publish schedules. Before creating, describe which task will be created and request my confirmation.

For team collaboration or production projects, also specify the task directory:

> Please create the task under Studio task directory `Marketing Analytics/Sales Summary`. If the directory does not exist, tell me first — I'll create it in Studio; do not create in the default directory.

If this information is not yet fully clear, ask first:

> I want to formalize this requirement into a Studio task. Please first check which directories are suitable, whether there are reusable tasks, and whether SQL, Python, or another task type is better suited. Do not create tasks yet.

### Allow the Agent to Do Read-Only Exploration

To generate more accurate tasks, the Agent typically needs to view table schema, sample data, or existing task configuration first. This read-only exploration does not change the environment and is important for task generation quality.

If you already know the field meanings, include field descriptions in your question to reduce the chance the Agent selects the wrong field.

This step is essentially the exploration phase before task creation. For unfamiliar tables, unfamiliar directories, and projects with many existing tasks, it is generally worth doing first.

### Create Draft Tasks First

For production tasks, create drafts first. Draft tasks appear in the Studio IDE task tree but do not run automatically and do not enter scheduling. When creating, specify the task directory and check that the task landed in the correct directory.

After creating a draft, the Agent typically returns:

- Task ID
- Task name
- Task path or folder
- Whether published or scheduled
- Whether SQL was executed
- Whether a target table was created or modified

For composite tasks or Flow-type objects, after creation check not only whether the task appears in the task tree, but also whether the nodes and dependencies on the canvas actually exist.

### Review Code in the IDE

After creating a draft, open the task in the IDE and check:

- Whether the task is in the correct directory
- Whether SQL references the correct catalog, schema, and tables
- Whether field meanings are correct; whether there are same-name or similar fields being misused
- Whether filter conditions, time range, and grouping dimensions align with business definitions
- Whether SQL is a read-only query or a write operation like `CREATE TABLE AS SELECT`, `INSERT INTO`, or `INSERT OVERWRITE`
- Whether the target table name follows naming and layering conventions
- Whether partition fields, cleaning timestamps, or source markers need to be added

A draft itself does not create target tables, but if SQL is a CREATE TABLE or write SQL, subsequent manual execution will actually run it.

For composite tasks, Flows, or multi-node tasks, also check:

- Whether expected nodes actually appear on the canvas
- Whether node names correspond to expected tasks
- Whether dependency edges are connected
- Whether the DAG is empty
- Whether node content was written into the correct node rather than being created as standalone SQL tasks

Do not rely only on the Agent's verbal description. Use the actual objects in the Studio canvas and task tree as the source of truth.

## Composite Tasks and Task Groups

Composite task and task group operations should be treated separately — do not conflate them with regular SQL draft tasks.

The entry point in the Studio new task menu is:

```text
Other → Composite Task
```

The composite task creation dialog includes at least:

- `Task name`
- `Folder`
- `Task group`

The `task group` field may default to `No`. When switched to `Yes`, the interface shows an additional `Please select a task group` field. This means these are three different actions:

- Create a composite task itself
- Treat an object as a task group
- Add a task to an existing task group

When asking the Agent for help with composite tasks, clarify your intent:

- Whether to create a new composite task container
- Or add a regular task to an existing task group
- Or add nodes and bind dependencies in a composite task canvas

Recommended question:

> Please create a composite task draft and explicitly state whether you are creating a new composite task or adding a task to an existing task group. After creation, return the task ID, directory, canvas node count, node list, and dependency relationships. Do not execute; do not publish.

If the composite task contains nodes, also follow up:

> Please check the actual DAG of this composite task. Return node names, node types, a content summary for each node, and dependency edges between nodes. Do not return only the task creation result.

### Decide Whether to Run or Publish

After confirming the code is correct, decide on the next step:

- Ad-hoc validation: run a read-only `SELECT`
- Table creation validation: run `CREATE TABLE AS SELECT`
- Periodic output: configure scheduling, dependencies, retry, and timeout, then publish
- Production go-live: add data quality checks, go-live checks, and run monitoring

## Typical Task Draft Scenarios

### Create a Single SQL Summary Task Draft

You can ask the Agent to create an unscheduled SQL draft task based on a source table — for example, aggregating sales by date and product for the last 7 days.

The Agent describes what it will create, requests confirmation, then creates the task in the IDE with the SQL content written. Task status is unscheduled. You can open and review it in the IDE. In practice, also ask the Agent to return the task directory to confirm the task was not created in the default or wrong directory.

### Create Silver / Gold Layered Task Drafts

You can ask the Agent to generate a simple data pipeline draft based on a source table. For example:

- Silver layer: read from the raw table, do field standardization and basic cleaning
- Gold layer: read from the Silver table, aggregate order count, sales, and average order value by date and product

In this scenario, the Agent can create two SQL draft tasks:

- Silver cleaning task: uses `TRIM(product_name)` to standardize product names, filters invalid amounts, null dates, and null product names, and adds a cleaning timestamp field
- Gold aggregation task: reads from the Silver table, aggregates total sales, order count, and average order value for the last 7 days by `sale_date` and `product_name`

This shows the Data Engineering Agent can complete the full task development flow: "understand source table → design layer plan → create multi-task drafts → write to IDE."

## Draft vs. Run vs. Publish

| Phase | Meaning | Changes data? | Enters scheduling? |
|---|---|---|---|
| Draft | Create task in IDE and write code | Does not automatically change data | No |
| Run | User or Agent executes task code | Depends on SQL type: query does not write; CREATE TABLE/INSERT changes data | Not necessarily |
| Publish | Publish task to scheduling system | Does not necessarily change data immediately, but runs per schedule | Yes |

When using the Agent to create tasks, specify which phase you want to stop at.

## Task Directory Guidelines

When creating Studio tasks, always specify the task directory. Task directories are not optional extras — they are the foundation of task governance, collaboration, and subsequent operations.

The Studio task tree supports directory management. Users can create directories by project, business domain, environment, or lifecycle, and rename, move, and delete directories. When creating tasks through the Data Engineering Agent, specify the target directory explicitly. If the directory does not yet exist, create it in Studio first, then have the Agent create the task draft.

To prevent directory sprawl, do not improvise directory names when creating tasks, and do not let tasks fall into the default directory automatically. Teams should agree on directory planning before creating tasks.

Recommended task directory organization:

| Organization method | When to use | Example |
|---|---|---|
| By business domain | Multiple departments sharing a workspace | `Sales Domain/Daily Summary`, `Finance Domain/Reconciliation` |
| By project | Project-based or special delivery | `Member Growth Project/Data Prep` |
| By layer | Many data warehouse layer tasks | `ODS`, `DWD`, `DWS`, `ADS` |
| By environment | Test and production coexist | `Test Tasks/Temp Dev`, `Production Tasks/Sales Reports` |
| By lifecycle | Temporary tasks needing periodic cleanup | `Ad-hoc Queries/2026Q2` |

Before creating tasks, ask the Agent to confirm:

- Whether the target task directory is clearly specified and already exists
- Whether the directory already exists
- Whether task creation is allowed in that directory
- Whether multiple tasks need to be created in the same directory
- Whether test tasks should go in a cleanable directory

Recommended question:

> Please create an SQL draft task under Studio task directory `Test Tasks/Temp Development`. If that directory does not exist, tell me first — I'll create it in Studio; do not create in the default directory or any other directory.

Not recommended:

> Help me create an SQL task.

Without specifying a task directory, the Agent may choose the current directory, default directory, or most recently used directory, making future lookup and cleanup much harder.

## Common Risks

### Only wanted to review logic but got a CREATE TABLE SQL

If you ask the Agent to "generate a data pipeline" or "write to the target table," it may generate `CREATE TABLE AS SELECT` or `INSERT` SQL. This is valid engineering code, but running it creates or writes to tables.

If you only want to review logic, ask:

> Please generate a read-only `SELECT` version first; do not generate CREATE TABLE or write SQL.

### Unclear field meanings lead to wrong field selection

When a table or multiple tables have similar fields, the Agent may select the wrong one. Include field meanings in your question, or ask the Agent to explain its field selection rationale first.

Example:

> If there are multiple amount fields, first state which field you will use as sales amount and why.

### Multi-task pipelines require checking upstream/downstream

If the Agent creates multiple tasks (e.g., Silver and Gold), check whether the tasks are in the same project directory or clearly organized layer directories, and whether Gold references the correct Silver output table. Before publishing, configure dependencies to prevent Gold from running before Silver.

## Recommended Prompt Templates

### Explore before deciding to create

> I want to formalize this requirement into a Studio task. Please first check which directories are suitable, whether there are reusable tasks, and whether SQL, Python, or another task type is better suited. Do not create tasks yet.

### Create a read-only SQL query

> Help me query `public.demo_xe_sales` for daily sales and order count by product for each of the last 7 days. Read-only query only; do not create tasks; do not write to tables.

### Create an SQL draft task

> Based on `public.demo_xe_sales`, create an SQL task draft that aggregates total sales, order count, and average order value for the last 7 days by `sale_date` and `product_name`. Only create a draft. Do not execute SQL. Do not create target tables. Do not publish schedules. Before creating, describe the task name and impact scope, and request my confirmation.

> Create this draft task under Studio task directory `Test Tasks/Temp Development`. If the directory does not exist, tell me first — I'll create it in Studio; do not create in any other directory.

### Create layered task drafts

> Based on `public.demo_xe_sales`, design a small Silver/Gold layer plan. Silver does field standardization and basic cleaning; Gold aggregates total sales, order count, and average order value for the last 7 days by date and product. Generate the plan first, then create two SQL draft tasks. Do not publish schedules; do not execute write SQL.

> Create both draft tasks under Studio task directory `Sales Analytics/SilverGold Drafts` and return the directory path of each task after creation.

### Review a draft task

> Please check the SQL content of task {task_id}. Describe whether it is a read-only query, CREATE TABLE, INSERT, or overwrite write. List which tables will be affected when it runs, and identify risks to check before publishing.

### Review a composite task or Flow

> Please check the actual canvas content of composite task `{task_id or task_name}`. Return node count, node names, node types, a SQL or code summary for each node, and dependency edges between nodes. Explicitly state whether the DAG is empty. Do not execute, do not publish, do not modify configuration.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Basic Usage Scenarios](dataagent-basic-usage-scenarios.md)
- [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
- [Metric Design Guide](dataagent-metric-design-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Data Pipeline and Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
