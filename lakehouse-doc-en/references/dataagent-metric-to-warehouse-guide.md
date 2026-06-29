# Data Engineering Agent Metric to Data Warehouse Guide

After metric design is complete, the next step is usually not to create reports directly, but to persist the metric logic into a reusable data model. This allows periodic tasks, dashboards, ad-hoc analysis, and downstream applications to all use the same data definitions, reducing duplicate SQL and logic drift.

This guide explains how to use the Data Engineering Agent to convert metric requirements from a business detail table into Silver / Gold or DWD / DWS layered models, SQL drafts, and Studio task chains. The focus is on "metric logic → layering design → SQL draft → task chain review." It does not cover the full cycle of publishing, backfill, and data quality closure.

## Applicable Scenarios

The following scenarios are suitable for this approach:

* A source table exists but no stable data warehouse layering model has been built yet
* Core metrics have been identified and need to be persisted as reusable aggregation tables
* The same aggregation SQL is used repeatedly in business analysis and should become a periodic task
* The same metric needs to serve both dashboards, analysis queries, and downstream applications simultaneously
* Source table fields have ambiguous logic that needs to be unified at the detail layer first
* A one-time analysis plan needs to be split into a maintainable Studio task chain

If you only need to look up a number temporarily, building a data warehouse model may not be necessary. Only proceed with data warehouse construction when metrics will be used repeatedly, need periodic output, require permission governance, or need to be consumed downstream.

## Recommended Workflow

### Let the Agent Do Read-Only Exploration First

Before modeling, ask the Agent to view the table structure and sample data to identify field roles and logic risks.

Suggested prompt:

> Please perform a metric to data warehouse analysis for `{schema}.{table}`. First do read-only exploration only — view the table structure and a small amount of sample data. Identify dimension fields, metric fields, time fields, filter fields, and system fields. Do not create tasks, write to tables, or modify configurations.

The Agent will typically confirm:

* Which field represents the business date
* Which field is suitable for amount, quantity, or count metrics
* Which fields are suitable as product, customer, region, or channel dimensions
* Whether the ID field is an order ID, order line ID, customer ID, or another business entity ID
* Whether there are status, refund, or validity flag fields for filtering
* Whether the sample data is sufficient to determine null rates, outliers, and enumeration values

### Define Metric Logic First

Do not ask the Agent to write CREATE TABLE SQL directly. Ask it to output metric definitions first, especially calculation logic and statistical granularity.

Example:

| Metric | Logic example | Questions to confirm |
| --- | --- | --- |
| Sales amount | `SUM(sale_amount)` | Whether `sale_amount` is actual payment, list price, or net amount after refund |
| Order count | `COUNT(DISTINCT sale_id)` | Whether `sale_id` is an order ID or order line ID |
| Average order value | `SUM(sale_amount) / COUNT(DISTINCT sale_id)` | Whether the denominator should be order count, customer count, or transaction count |
| Product sales ranking | Aggregate sales amount by product dimension and rank | Whether the ranking is calculated by day, by month, or over the entire period |

Suggested prompt:

> Please output the metric definitions first; do not write SQL. For each metric, explain the business definition, calculation logic, statistical granularity, time scope, available dimensions, and logic risks.

### Split Metrics into Detail Layer and Aggregation Layer

For stable, reusable metrics, you typically need to first create a clean detail table, then generate aggregation tables from that detail layer.

Common split approach:

| Layer | Goal | Typical content |
| --- | --- | --- |
| Silver / DWD | Cleansed detail fact table | Field normalization, type conversion, outlier filtering, business date, source batch |
| Gold / DWS | Theme-level aggregation table | Daily aggregation, product aggregation, customer aggregation, ranking, ratio |
| ADS | Application-specific dataset | Dashboard wide tables, API output tables, fixed report tables |

For sales-type detail tables, a common chain is:

```text
Source table
  -> Silver sales detail table
  -> Gold daily sales aggregation table
  -> Gold product sales ranking table
```

### Ask the Agent to Output SQL Drafts Without Executing

Once the layering plan is confirmed, ask the Agent to output the complete SQL. The first time, only output SQL — do not create tasks or execute.

Suggested prompt:

> Based on the above metric design and layering plan, output the CREATE TABLE SQL and write SQL for the Silver table, Gold daily aggregation table, and Gold product ranking table. Only output SQL; do not create tasks, run SQL, or publish schedules.

When reviewing the SQL, focus on:

* Whether the target table names follow the enterprise naming conventions
* Whether field types are reasonable
* Whether the detail layer retains dimensions and IDs needed for future analysis
* Whether the aggregation layer uses the correct grouping fields
* Whether `COUNT(*)`, `COUNT(id)`, and `COUNT(DISTINCT id)` match the business logic
* Whether the write impact of `INSERT INTO`, `INSERT OVERWRITE`, and `CREATE TABLE AS SELECT` is clear
* Whether there is a risk of overwriting the entire table

### Then Create Studio Draft Tasks

After reviewing the SQL, ask the Agent to create Studio task drafts. Specify the target directory when creating tasks.

Suggested prompt:

> Confirm creating Studio SQL draft tasks following the SQL above. Create all tasks in `{task directory}`. Only create drafts — do not run SQL or publish schedules. Before creating, list the task list, task directory, input table, output table, SQL type, and scope of impact, then request my confirmation.

If the target directory does not exist, create it in the Studio task tree first, then ask the Agent to create the tasks. Directories can be organized by project, business domain, or lifecycle, for example:

```text
Sales Analysis/Metric Build
Data Warehouse Modeling/Sales Analysis
Test Tasks/Temp Development
```

### Check the Task Chain and Pre-Publish Conditions

After draft tasks are created, ask the Agent to review the task chain rather than publishing immediately.

Suggested prompt:

> Please review this set of metric build tasks. For each task, explain the input table, output table, SQL type, upstream/downstream relationship, whether running will write data, and what dependencies, scheduling, retry, timeout, and data quality checks still need to be configured before publishing.

Common check items:

* Whether the Gold task depends on the Silver task completing successfully
* Whether multiple Gold tasks can run in parallel
* Whether date partitioning or incremental write by business date is needed
* Whether automatic retry on failure is appropriate
* Whether a timeout needs to be configured
* Whether data quality rules need to be added, such as non-null, uniqueness, enumeration, or volatility checks
* Whether a test run in a test directory or test schema is needed first

## Example: From Sales Metrics to Silver / Gold Model

The following example uses a sales detail table to show how to decompose from metric logic to a data warehouse task chain.

Source table fields include:

| Field | Meaning |
| --- | --- |
| `sale_id` | Sales record or order identifier |
| `product_name` | Product name |
| `sale_amount` | Sales amount |
| `sale_date` | Sales date |
| `customer_id` | Customer identifier |
| `created_at` | Record creation time |

### Metric Logic

| Metric | Calculation logic | Notes |
| --- | --- | --- |
| Sales amount | `SUM(sale_amount)` | Confirm whether the amount has already excluded refunds, discounts, and taxes |
| Order count | `COUNT(DISTINCT sale_id)` | If `sale_id` is an order line ID, use the actual order ID instead |
| Average order value | `SUM(sale_amount) / COUNT(DISTINCT sale_id)` | If the business definition is the customer average, use customer count as the denominator |
| Product sales ranking | Aggregate sales amount by product and rank | Confirm the ranking period — by day, by month, or over the entire period |

### Silver Detail Layer

The Silver layer forms a clean, reusable sales detail.

Recommended processing:

* Normalize product names, for example remove leading/trailing whitespace
* Filter out records where sales amount is null or less than or equal to 0
* Filter out records where sales date is null
* Add a business date field, for example `dt`
* Add a processing time field, for example `etl_time`
* Retain original ID, customer ID, and creation time for traceability and future expansion

Task example:

```text
build_silver_sales_detail
```

Output table example:

```text
silver_sales_order_detail
```

### Gold Aggregation Layer

The Gold layer produces directly consumable metric tables for specific analysis topics.

Daily aggregation task:

```text
build_gold_sales_daily
```

Output table:

```text
gold_sales_daily_summary
```

Typical fields:

* `dt`
* `sales_amount`
* `order_count`
* `customer_count`
* `avg_order_value`
* `etl_time`

Product ranking task:

```text
build_gold_product_rank
```

Output table:

```text
gold_product_sales_rank
```

Typical fields:

* `dt`
* `product_name`
* `sales_amount`
* `order_count`
* `sales_rank`
* `etl_time`

### Task Chain

Recommended task chain:

```text
public.demo_xe_sales
  -> build_silver_sales_detail
  -> build_gold_sales_daily
  -> build_gold_product_rank
```

If both `build_gold_sales_daily` and `build_gold_product_rank` only depend on the Silver detail layer, both Gold tasks can depend on `build_silver_sales_detail` and run in parallel based on the scheduling system's capabilities.

## Clarify the Write Impact

Metric to data warehouse development typically transitions from "read-only analysis" to "writing data" gradually. The impact at each stage differs:

| Stage | Does it change Lakehouse data? | Notes |
| --- | --- | --- |
| View table structure and sample data | No | Read-only exploration |
| Output metric design and layering plan | No | Generates documentation or plan only |
| Output SQL text | No | Generates SQL but does not run it |
| Create Studio draft tasks | No | Writes Studio task configuration, does not create target tables |
| Manually run CREATE TABLE or write SQL | Yes | May create tables, insert data, or overwrite data |
| Publish scheduled tasks | Yes | Will execute write logic on a periodic basis |

In production environments, treat "create draft," "manual test run," and "publish schedule" as three explicit steps, each with its own impact review.

## FAQ

### The metric design is done — why do we still need to build a Silver layer?

Generating Gold aggregation tables directly from the source table is fast, but field cleansing, outlier filtering, and business date selection will be scattered across multiple tasks. The Silver layer unifies these basic rules, allowing multiple aggregation tasks to reuse the same clean detail data.

### Should the Gold table aggregate by day or by month?

It depends on the consumption scenario. Dashboards and daily monitoring typically need daily granularity; monthly reports can further aggregate from daily aggregations. It is recommended to first retain the finer, stable granularity, and then add monthly aggregation tables based on performance and usage frequency.

### The Agent generated `INSERT OVERWRITE` — can I run it directly?

Do not run it directly. `INSERT OVERWRITE` may overwrite target table data. Before running, confirm the target table, partition range, whether only the current day's partition is overwritten, and whether a backup or rollback method exists.

### After creating draft tasks, will the target table be created automatically?

No. Draft tasks only save the SQL content and task configuration. The SQL will only actually execute after you manually run it or publish a schedule.

### Do I need to create all tasks at once?

Not necessarily. For complex chains, it is recommended to create the Silver draft first, verify it, and then create the Gold drafts. This makes it easier to identify field logic and write impact issues.

## Recommended Prompt Templates

### From metrics to layering plan

> Please design a metric to data warehouse plan for `{schema}.{table}`. First do read-only exploration only — identify field roles and core metrics. Then design a Silver / Gold layering model, explaining the inputs, outputs, field processing logic, metric logic, and logic risks for each layer. Do not create tasks or run SQL.

### Generate SQL drafts

> Based on the plan above, output the complete SQL, including CREATE TABLE SQL and write SQL for the Silver detail table, Gold daily aggregation table, and Gold ranking table. Only output SQL; do not create tasks, run SQL, or publish schedules.

### Create Studio draft tasks

> Confirm creating Studio SQL draft tasks. Task directory is `{task directory}`. First list the task list, input table, output table, dependencies, SQL type, and write impact, then request my confirmation. Only create drafts; do not run SQL or publish schedules.

### Pre-publish review

> Please review whether this set of metric build tasks is ready to enter the publishing phase. Check target table, write method, partition strategy, dependencies, schedule period, retry, timeout, VCluster, data quality checks, and downstream impact. Do not modify configurations.

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Metric Design Guide](dataagent-metric-design-guide.md)
* [Data Pipeline and Data Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
* [Task Development Guide](dataagent-task-development-guide.md)
* [Scheduling and Release Guide](dataagent-scheduling-and-release-guide.md)
* [Pipeline Launch Checklist](dataagent-pipeline-launch-checklist.md)
* [Common Prompt Examples](dataagent-prompt-examples.md)
