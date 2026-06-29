# Data Engineering Agent Metric Design Guide

Metric design is an important step before data engineering enters modeling and development. It clarifies fields, business logic, statistical granularity, time scope, and naming conventions early — preventing inconsistencies in task development, data warehouse modeling, dashboard construction, and data analysis down the line.

The Data Engineering Agent can help identify field roles, design metric logic, surface logic risks, and give recommendations for persisting metrics to the data warehouse or semantic layer — all based on table structure, sample data, and business objectives.

## Applicable Scenarios

The following scenarios are suitable for metric design first:

* Taking over an unfamiliar business table and needing to determine which fields are suitable as dimensions, metrics, and filters
* Preparing to build sales, operations, customer, product, or financial topic metrics
* Multiple fields with similar meanings that could easily lead to incorrect statistical logic
* Preparing to build DWD / DWS / ADS or Silver / Gold layered models
* Preparing to persist metrics to a BI tool, semantic layer, or analytics application
* Business teams have different understandings of the same metric and need to agree on a unified definition

Do not ask the Agent to create tasks when field meanings and metric logic are unclear. Completing metric design first reduces rework and incorrect data outputs.

## Recommended Workflow

### Do Read-Only Exploration First

Ask the Agent to view the table structure and a small amount of sample data first. Do not create tasks, write to tables, or modify configurations.

Suggested prompt:

> Please perform a metric design for `{schema}.{table}`. First do read-only exploration only — view the table structure and a small amount of sample data. Do not create tasks, write to tables, or modify configurations.

The Agent will typically focus on:

* Field names and types
* Whether there is a primary key or order line ID
* Which fields are suitable as dimensions
* Which fields are suitable as measures
* Which fields are suitable as time scope
* Which fields look more like system or audit fields
* Null values, outliers, date ranges, and enumeration values in the sample data

### Identify Field Roles

The first step in metric design is to clarify field roles.

| Field role | Meaning | Examples |
| --- | --- | --- |
| Dimension fields | Used for grouping, slicing, and comparison | Product, customer, region, channel |
| Metric fields | Used for sum, count, average, ratio calculations | Amount, quantity, duration, cost |
| Time fields | Used for daily, weekly, monthly, and quarterly statistics | Sales date, order time, partition date |
| Filter fields | Used to define business scope | Status, type, whether valid, whether refunded |
| System fields | Used for data governance or technical tracking | Created time, updated time, batch ID |

For time fields, distinguish between business event time and system processing time. For example, sales analysis typically uses the sales date, not the data write time.

### Design Metric Logic

When asking the Agent to output metric definitions, include at least the following:

* Metric name
* Business definition
* Calculation logic
* Data source
* Statistical granularity
* Available dimensions
* Time scope
* Filter conditions
* Logic risks

Example metrics:

| Metric | Business definition | Common calculation logic |
| --- | --- | --- |
| Sales amount | Total sales amount for valid orders in a given time range | `SUM(sale_amount)` |
| Order count | Number of orders in a given time range | `COUNT(order_id)` or `COUNT(DISTINCT order_id)` |
| Average order value | Average spending per order or customer | `SUM(amount) / COUNT(DISTINCT order_id)` |
| Product sales ranking | Aggregate sales amount by product and rank | `SUM(amount) GROUP BY product_name` |
| Daily average sales amount | Average daily sales amount over a time range | `SUM(amount) / COUNT(DISTINCT sale_date)` |

Order count and average order value especially need business confirmation. If the table only has an order line ID and no order header ID, `COUNT(*)` may be counting order lines rather than orders.

## Logic Risk Review

Metric design should not only output a list of metrics — it should also surface logic risks.

Common risks include:

* It is unclear whether an amount field represents the actual payment, list price, amount including tax, or net amount after refund
* Missing order status, refund flag, or validity flag makes it impossible to determine which records should be included in the metric
* `created_at`, `updated_at`, `biz_date`, and `sale_date` are used interchangeably
* An ID field may be an order line ID rather than an order ID
* The same table has multiple similar amount fields or date fields
* Too little sample data to determine enumeration values, null rates, and outliers
* Metrics have different logic when calculated at the customer, order, product, or store level

Suggested prompt:

> Please identify the most ambiguous aspects of these metrics, including amount fields, time fields, ID fields, status fields, and statistical granularity. Provide a list of questions that need business confirmation.

## Metric Naming Recommendations

Metric names should be stable, readable, and maintainable. Use a consistent naming convention, for example:

```text
{business_domain}_{metric_meaning}_{aggregation_method}
```

Examples:

| Metric | Suggested name | Notes |
| --- | --- | --- |
| Total sales amount | `sales_amount_total` | Sum of sales amount |
| Order count | `sales_order_count` | Number of orders |
| Average order value | `sales_avg_order_value` | Average order value |
| Product sales ranking | `sales_product_rank` | Product-level ranking |
| Customer order count | `sales_customer_order_count` | Customer-level order count |

If the enterprise already has a metric naming standard, ask the Agent to follow the existing standard rather than inventing a new naming scheme.

## Persisting to the Data Warehouse and Semantic Layer

After metric design is complete, you can continue into modeling and development.

Common persistence approaches:

* Retain cleansed detail data in the DWD or Silver layer
* Pre-aggregate by day, product, customer, channel, and other dimensions in the DWS or Gold layer
* Produce wide tables for dashboards or applications in the ADS layer
* Register measures, dimensions, time fields, and business descriptions in the semantic layer
* Persist metric definitions, applicable scenarios, and exception rules in a knowledge base or metric catalog

Suggested prompt:

> Based on this metric design, design a DWD / DWS / ADS three-layer model. First output the goal, input table, output table, field processing logic, and metric logic for each layer. Do not create tasks.

## Recommended Prompt Templates

### Generate metric design

> Please perform a metric design for `{schema}.{table}`. First do read-only exploration only — view the table structure and a small amount of sample data. Then identify dimension fields, metric fields, time fields, filter fields, and system fields. Then design a set of core metrics, explaining the metric name, business definition, calculation logic, statistical granularity, available dimensions, and logic risks. Do not create tasks, write to tables, or modify configurations.

### Check for logic risks

> Please check which fields in `{schema}.{table}` are most likely to cause metric logic confusion, focusing on amount fields, date fields, ID fields, status fields, and statistical granularity. Output a list of questions that need business confirmation.

### Generate a metric requirements document

> Please organize the metric design just completed into a metric requirements document, including metric name, business definition, calculation logic, data source, statistical granularity, time scope, filter conditions, logic risks, and modeling recommendations.

### Move to data warehouse modeling

> Based on this metric design, design a Silver / Gold or DWD / DWS / ADS layering plan. First output the plan and the inputs/outputs of each layer. Do not create tasks or run SQL.

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Basic Usage Scenarios](dataagent-basic-usage-scenarios.md)
* [Metric to Data Warehouse Guide](dataagent-metric-to-warehouse-guide.md)
* [Data Pipeline and Data Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
* [Task Development Guide](dataagent-task-development-guide.md)
* [Common Prompt Examples](dataagent-prompt-examples.md)
