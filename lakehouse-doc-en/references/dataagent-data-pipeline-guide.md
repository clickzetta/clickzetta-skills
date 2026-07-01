# Data Engineering Agent Data Pipeline and Warehouse Modeling Guide

This guide covers how to use the Data Engineering Agent to help design data pipelines and data warehouse layers, and generate Studio task drafts. It focuses on the "design + SQL draft task" phase and does not cover the full picture of scheduling and publishing, backfill, DQC, and operations closeout.

## Applicable Scenarios

The Data Engineering Agent can assist with the following data pipeline and modeling work:

- Design Bronze/Silver/Gold layer plans based on source tables
- Design ODS/DWD/DWS/ADS layer plans based on business goals
- Generate SQL drafts for cleaning, standardization, aggregation, and wide-table processing
- Split a pipeline into multiple Studio task drafts
- Explain input, output, field processing logic, and upstream/downstream dependencies for each layer
- Help check SQL type, target tables, task directories, dependency relationships, and run risks before publishing

If tasks have entered the production publishing phase, further checks are needed for scheduling, dependencies, retry, timeout, data quality rules, and run monitoring.

## Explore First, Then Design Pipelines

Data pipelines and data warehouse modeling typically do not involve creating tasks from the very start.

The more natural approach is:

- Explore source table schema, sample data, and key field meanings first
- Check whether reusable tasks or existing layer results already exist
- Then output the layer design plan
- Finally create draft tasks

Scenarios better suited to exploring first:

- You don't yet know whether the source table fields are sufficient to support the target modeling
- You are unsure whether Silver/Gold or ODS/DWD/DWS is a better fit
- You are unsure whether there are similar pipeline drafts in the current directory that can be reused

Better opening questions:

- Help me first check whether this table is suited for Silver/Gold layering.
- Help me check whether there are related data pipeline tasks in the current directory that can be reused.
- Help me decide which layering path is better for this requirement.

## Recommended Workflow

### Have the Agent Understand the Source Table First

Before modeling, the Agent typically needs to view the table schema, field names, field types, and a small amount of sample data. This read-only exploration is for understanding the data and does not modify the environment.

You can ask:

> Please view the table schema and a small amount of sample data for `public.demo_xe_sales` and explain how it is suited for Silver/Gold layering. Output the analysis only; do not create tasks.

If you already know the key field meanings, specify them directly:

> `sale_amount` is order sales amount, `sale_date` is sales date, `product_name` is product name. Please design aggregation logic based on these fields.

If you are not sure whether the table is ready for direct modeling, ask first:

> Please assess whether this table is ready for layered modeling, or whether further metric definition confirmation or upstream data preparation is needed.

### Output the Layer Design Plan First

Do not immediately have the Agent create tasks. Ask it to output the plan first, including:

- The goal for each layer
- Input and output tables for each layer
- Which Studio task directory each task should be in
- Which fields each layer processes
- Cleaning, filtering, deduplication, and standardization rules
- Aggregation dimensions and metrics
- Whether to write to tables
- Whether scheduling dependencies are needed

Example:

> Design a small Silver/Gold layer plan based on `public.demo_xe_sales`. Silver does field standardization and basic cleaning; Gold aggregates total sales, order count, and average order value for the last 7 days by date and product. Show the plan and each layer's input/output first; do not create tasks.

### Create SQL Draft Tasks

After confirming the plan, have the Agent create task drafts. Draft tasks are written into the Studio IDE but do not run automatically, create tables, or publish schedules. Before creating, specify the Studio task directory clearly to avoid multi-layer tasks being scattered in the default directory or the wrong business directory. If the directory does not yet exist, create it in the Studio task tree first, then have the Agent create the task drafts.

Specify the boundaries clearly:

> Confirmed — create two SQL draft tasks per this plan. Only create drafts. Do not execute SQL. Do not create target tables. Do not publish schedules. After creation, return task ID, task name, task path, and whether any environment was modified.

> Create both tasks under Studio task directory `Sales Analytics/SilverGold Drafts`. If the directory does not exist, tell me first — I'll create it in Studio; do not create in the default directory.

### Check SQL in the IDE

After creating drafts, focus on checking:

- Whether tasks are in the correct directory
- Whether SQL references the correct source tables
- Whether output table names follow layer naming conventions
- Whether field cleaning rules meet business requirements
- Whether filter conditions might accidentally delete data
- Whether aggregation dimensions and metrics are correct
- Whether the Gold layer references the correct Silver layer output
- Whether the SQL is a read-only query, CREATE TABLE, INSERT, or overwrite write

If SQL is `CREATE TABLE AS SELECT`, `INSERT INTO`, or `INSERT OVERWRITE`, running it will modify data or create target tables. The draft phase does not execute these SQL statements, but you must confirm the impact scope before publishing or manual execution.

## Example: Silver / Gold Sales Summary Pipeline

The following example shows how to have the Agent view source table context, generate a Silver/Gold plan, create SQL draft tasks, and check SQL content and unscheduled state in the IDE. Scheduling, publishing, and run output should be confirmed separately after entering the publishing phase.

Source table: `public.demo_xe_sales`

Goal:

- Silver layer: standardize and clean order detail fields
- Gold layer: aggregate total sales, order count, and average order value for the last 7 days by `sale_date` and `product_name`

### Silver Layer Design

The Silver layer holds raw order details and performs the most basic reusable cleaning. The Agent's generated draft logic includes:

- Retain order ID, product name, sales amount, sales date, customer ID, and creation time
- `TRIM` `product_name` to remove leading and trailing whitespace
- Filter records where `sale_amount <= 0`
- Filter records where `sale_date` is null
- Filter records where product name is null
- Add `cleaned_at` field to record the cleaning time
- Add `source_layer` field to identify the data source layer

This type of task is well named:

```text
silver_order_clean
```

### Gold Layer Design

The Gold layer is for business analytics and uses the cleaned Silver layer data for aggregation. The Agent's generated draft logic includes:

- Read from the Silver output table
- Filter data from the last 7 days
- Group by `sale_date` and `product_name`
- Calculate order count `order_count`
- Calculate total sales `sales_amount`
- Calculate average order value `avg_order_value`
- Add `summary_at` field to record the aggregation time

This type of task is well named:

```text
gold_product_daily_summary
```

### Task Pipeline

This pipeline should have the following dependencies:

```text
public.demo_xe_sales
  -> silver_order_clean
  -> gold_product_daily_summary
```

If the pipeline enters the scheduling phase, configure the Gold task to depend on the Silver task completing successfully before running, to avoid Gold reading unrefreshed or nonexistent Silver data.

## Layer Design Guidelines

### Bronze Layer

The Bronze layer typically holds raw data or near-raw ingestion results, emphasizing traceability, minimal processing, and preservation of source information.

Suited for:

- Raw data ingestion
- Original field preservation
- Recording source system, import time, and batch number
- Basic format compatibility

### Silver Layer

The Silver layer forms reusable detail data, emphasizing cleaning, standardization, and business consistency.

Suited for:

- Field standardization
- Null and anomaly filtering
- Type conversion
- Deduplication
- Dimension table joins
- Unified basic business rules

### Gold Layer

The Gold layer is oriented toward specific analytics themes, metrics, or applications, emphasizing direct business consumability.

Suited for:

- Metric aggregation
- Wide-table processing
- Subject domain datasets
- Dashboard and report support tables
- Data output for downstream services or applications

## Task Directory Organization

A data pipeline typically contains multiple tasks. Task directories should reflect the project, business domain, or layer relationship for easier subsequent publishing, dependency configuration, permission management, and bulk cleanup.

Common organization patterns:

| Organization method | Example | Suited for |
|---|---|---|
| By business domain | `Sales Domain/Silver`, `Sales Domain/Gold` | Long-term business domain maintenance |
| By project | `Member Growth Project/Data Pipeline` | Project-based development |
| By layer | `DWD/Orders`, `DWS/Sales Summary` | Large numbers of warehouse tasks |
| By environment | `Test Tasks/Temp Dev`, `Production Tasks/Sales` | Isolation between test and production |

For multi-task pipelines like Silver/Gold, put all tasks in the same business directory or clearly organized subdirectories by layer. Do not let the Agent create some tasks in the current directory and some in the default directory — this makes dependency configuration and test task cleanup much harder.

## What to Tell the Agent When Designing Pipelines

To reduce rework, include the following in your questions:

- The catalog and schema for source and target tables
- Target layering, e.g., Silver/Gold or DWD/DWS
- Studio task directory
- Target table name for each layer
- Key field meanings
- Filter conditions and time range
- Metric definitions
- Whether to write to tables
- Whether to create drafts only
- Whether executing SQL or publishing schedules is allowed

Example:

> Source table is `public.demo_xe_sales`. `sale_date` is sales date, `sale_amount` is sales amount, `product_name` is product name. Design a Silver/Gold two-layer pipeline: Silver cleans invalid sales amounts and null product names; Gold aggregates total sales, order count, and average order value by date and product. Output the plan first; do not create tasks or execute SQL.

> If creating tasks, put all draft tasks under Studio task directory `Sales Analytics/SilverGold Drafts`.

## FAQ

### Why create drafts first rather than running directly?

Data pipelines typically create tables, write to tables, or affect downstream tasks. Creating drafts first lets engineers review SQL, naming, field definitions, target tables, and dependencies, reducing the risk of accidental data writes and accidental publishing.

### If the Agent generated `CREATE TABLE AS SELECT`, does that mean a table was created?

No. A table is only created when the SQL is executed. Creating a task draft only writes the SQL into the IDE. The target table is only created when the user manually runs it, publishes the schedule, or asks the Agent to execute it.

### Will multi-layer tasks have dependencies configured automatically?

Creating draft tasks does not mean scheduling dependencies are configured. Before entering the publishing phase, explicitly ask the Agent to configure dependencies, such as "the Gold task depends on the Silver task completing successfully before running."

### How to avoid field misuse?

When a table has similar fields, have the Agent explain field meanings and the selection rationale first. You can also specify key fields directly in your question, for example: "use `net_sales_amount` for sales amount; do not use `gross_sales_amount`."

## Recommended Prompt Templates

### Generate layer design only

> Design a `{Silver/Gold or DWD/DWS}` layer plan based on `{schema}.{source_table}`. Explain the goal, input table, output table, field processing logic, aggregation metrics, and dependencies for each layer. Output the plan only; do not create tasks or execute SQL.

### Create layered draft tasks

> Confirmed — create SQL draft tasks per the plan above. Only create drafts. Do not execute SQL. Do not create target tables. Do not publish schedules. After creation, return task ID, task name, task path, and whether any environment was modified.

> Create all tasks under Studio task directory `{task_directory}`. If the directory does not exist, tell me first — I'll create it in Studio; do not create in the default directory or any other directory.

### Check pipeline drafts

> Please check this set of pipeline draft tasks. Describe each task's input, output, SQL type, which tables will be affected when run, and what dependencies and checks need to be configured before publishing.

### Ready to enter scheduling and publishing

> Please design a scheduling plan for this task set. Describe each task's run interval, upstream/downstream dependencies, failure retry, timeout, and pre-publishing risks. Output the plan only; do not modify configuration.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Metric Design Guide](dataagent-metric-design-guide.md)
- [Metric to Warehouse Guide](dataagent-metric-to-warehouse-guide.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
