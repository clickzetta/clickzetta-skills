# Data Transformation

Singdata Lakehouse covers four data transformation patterns: auto-incremental refresh pipelines (Dynamic Table), scheduled batch ETL (Studio task scheduling), change data capture (Table Stream), and query acceleration (Materialized View). Choose based on your latency requirements and trigger model.

---

## I want to build a data pipeline (ODS → DWD → ADS)

**Recommended: Dynamic Table**, define a SQL query and the system automatically computes incremental updates and maintains the result — no manual scheduling required.

| Scenario | Approach | Reference |
|------|------|---------|
| Multi-layer pipeline with automatic incremental refresh | Dynamic Table | [Dynamic Table Overview](dynamic-table.md) · [Create Dynamic Table](create-dynamic-table.md) |
| End-to-end real-time ETL example | Dynamic Table tutorial | [Real-time ETL with Dynamic Tables](tutorials-streaming-data-pipeline-with_dynamic-table.md) |
| Near-real-time incremental processing pipeline | Dynamic Table + Table Stream | [Build a Near-Real-Time Incremental Pipeline with Dynamic Tables](streaming_pipeline_with_dynamic_table.md) |
| CDC data processing (real-time database change processing) | Multi-table real-time sync + Dynamic Table | [Complete CDC and Data Processing Example](sql_table_stream_guide.md) |
| Implement SCD (Slowly Changing Dimensions) | Table Stream + task | [SCD Implementation Guide](slowly-changing-dimensions-with-streams-and-tasks.md) |

> **Dynamic Table vs. Materialized View**: Dynamic Tables are designed for data processing pipelines where results don't need to be instantly up-to-date. Materialized Views are designed for query acceleration and require data to always be current to support query rewriting. See [Dynamic Table Overview](dynamic-table.md) for details.

---

## I want to run scheduled batch ETL (T+1 / hourly)

**Recommended: Studio SQL task + scheduling**, write SQL in Studio, configure a Cron schedule, and monitor run status visually.

| Scenario | Approach | Reference |
|------|------|---------|
| SQL transformation task + periodic scheduling | Studio SQL task | [Task Development and Scheduling](task-develop.md) · [Quick ETL Setup](quick_start_etl.md) |
| Multi-task orchestration (with dependencies) | Composite task / task group | [Composite Task](composite_task.md) · [Task Group](task_group.md) |
| Python processing required (pandas / custom logic) | Studio Python task | [Python Task Development](python-task-dev.md) |
| Data modeling with dbt | dbt + Lakehouse | [Incremental Development with dbt on Lakehouse](use-dbt-dev.md) |

---

## I want to detect table data changes (CDC / incremental-driven)

**Recommended: Table Stream**, captures INSERT / UPDATE / DELETE changes on a table to drive downstream incremental processing.

| Scenario | Approach | Reference |
|------|------|---------|
| Capture table changes to drive downstream processing | Table Stream | [Table Stream Overview](table_stream.md) · [Create Table Stream](create-table-stream.md) |
| Table Stream best practices | — | [Table Stream Best Practices](lakehouse-table-stream-best-practices.md) |

---

## I want to accelerate queries (pre-computation / cached results)

**Recommended: Materialized View**, pre-computes and stores query results with automatic query rewriting for transparent acceleration.

| Scenario | Approach | Reference |
|------|------|---------|
| Pre-compute high-frequency complex queries | Materialized View | [Materialized View Overview](materializedview.md) · [Create Materialized View](create-materialized-view.md) |
| Query rewriting (transparent acceleration) | Materialized View + query rewriting | [Query Rewriting](materializedview.md) |

---

## I want to do SQL data transformation (cleansing / aggregation / joining)

| Scenario | Reference |
|------|---------|
| SQL transformation basics | [SQL Data Transformation Basics](sql_data_transform_basic.md) |
| Window functions (YoY / MoM / ranking) | [Data Transformation with Window Functions](sql_data_transform_windows.md) |
| Complex queries with CTEs | [Data Transformation with CTEs](sql_data_transform_cte.md) |
| Nested data types (Array / Map / Struct) | [Nested Data Type Transformation](sql_data_transfom_nesteddatatypes.md) |
| JSON data processing | [JSON Processing Guide for Complex Business Cases](json_guide_for_complex_biz_cases.md) |
| Practical tips | [SQL Transformation Tips](sql_data_transform_tips.md) |
| Funnel analysis and user behavior | [Funnel Analysis Guide](sql_funnel_analysis_guide.md) |
| Session analysis (Sessionization) | [Session Analysis Guide](sql_sessionization_guide.md) |
| Retention and cohort analysis | [Retention and Cohort Analysis Guide](sql_retention_cohort_guide.md) |
| Marketing attribution analysis | [Attribution Analysis Guide](sql_attribution_guide.md) |
| Hierarchical queries (org charts / BOM) | [Hierarchical Query Workaround](sql_hierarchy_workaround_guide.md) |
| Data deduplication | [Data Deduplication Guide](sql_deduplication_guide.md) |
| Data pivoting (rows to columns / columns to rows) | [Data Pivot and Transpose Guide](sql_pivot_guide.md) |
| Cumulative calculations and running totals | [Running Total Guide](sql_running_total_guide.md) |

---

## I want to ensure data quality

**Recommended: Studio Data Quality Rules (DQC)**, configure validation rules to automatically intercept anomalous data before processing.

| Scenario | Approach | Reference |
|------|------|---------|
| Configure data quality check rules | Studio DQC | [Quick Data Quality Rule Setup](quick_start_data_quality.md) |
| Complete data quality guide | DQC rule configuration | [Data Quality](data-quality.md) |

---

## I want to monitor pipeline run status

**Recommended: Studio Operations Monitoring**, visually view task run status, logs, and alerts.

| Scenario | Approach | Reference |
|------|------|---------|
| View task run logs | Studio Operations Center | [Quick Monitoring and Alerting Setup](quick_start_monitoring_and_alerting.md) |
| Troubleshoot task failures | Job Profile diagnostics | [Job History Analysis](jobprofile-bestpractices.md) |
| DataOps production practices | Complete operations guide | [DataOps Data Safety and Stability Practices](dataops_practice.md) |

---

## Not sure which tool to use?

```
What is your transformation requirement?
├── Need continuously auto-refreshed results (data pipeline)
│   ├── Data freshness is not critical (minutes acceptable) → Dynamic Table
│   └── Data must always be current to support query rewriting → Materialized View
├── Periodic batch runs (T+1 / hourly) → Studio SQL task + scheduling
├── Need to detect row-level changes (INSERT/UPDATE/DELETE) → Table Stream
└── One-time data cleansing / transformation → Write SQL directly (INSERT INTO ... SELECT)
```

For a complete tool selection guide, see: [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md)
