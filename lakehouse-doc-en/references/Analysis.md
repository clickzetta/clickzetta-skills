# Data Analysis and SQL Guide

Singdata Lakehouse covers six analytical capabilities: interactive SQL queries, BI tool connectivity for reporting, direct querying of object storage files, cross-system federated queries, AI-powered conversational analysis, and query performance optimization.

---

## I want to query and analyze data with SQL

**Recommended: write SQL directly in Studio**, which supports standard SQL syntax including window functions, CTEs, JOINs, and subqueries.

| Scenario | Reference |
|------|---------|
| SQL query syntax basics | [SQL Query Syntax](query-syntax.md) |
| Year-over-year / period-over-period / ranking (window functions) | [Data Transformation with Window Functions](sql_data_transform_windows.md) |
| Complex multi-step queries (CTEs) | [Data Transformation with CTEs](sql_data_transform_cte.md) |
| Funnel analysis / retention analysis | [SQL Transformation Tips](sql_data_transform_tips.md) |
| Sessionization | [Sessionization Guide](SQL_Sessionization_Guide.md) — event stream splitting, session duration, bounce rate, user paths |
| Marketing attribution analysis | [Attribution Modeling Guide](SQL_Attribution_Guide.md) — First-Touch / Last-Touch / Linear / Time-Decay / U-Shape models |
| Deduplication / BITMAP user segmentation | [Data Deduplication](SQL_Deduplication_Guide.md) · [BITMAP User Analysis](SQL_Bitmap_Guide.md) |
| Pivot (rows to columns / columns to rows) | [Data Pivoting and Transposition](SQL_Pivot_Guide.md) |
| Cumulative calculations / running totals | [Cumulative Calculations and Running Totals](SQL_Running_Total_Guide.md) |
| Hierarchy queries (org charts / BOM) | [Hierarchy Query Workaround](SQL_Hierarchy_Workaround_Guide.md) — materialized path, closure table, fixed-depth JOIN |
| JSON / nested data processing | [JSON Processing Guide for Complex Business Cases](json_guide_for_complex_biz_cases.md) |

---

## I want to connect a BI tool for reporting

**Recommended: JDBC / ODBC connections**, supported by all major BI tools.

| BI Tool | Reference |
|--------|---------|
| FineBI | [FineBI Connection Guide](FineBI.md) |
| PowerBI | [PowerBI Connection Guide](PowerBI.md) |
| Tableau | [Tableau Connection Guide](tableau-connect-to-lakehouse.md) |
| Superset | [Superset Connection Guide](eco_integration/superset.md) |
| Other tools | [Ecosystem Integration Overview](ecosystem-all.md) |

---

## I want to analyze data lake files (OSS / S3 / COS)

**Recommended: Volume + direct SQL query** — no need to import data into a table first. Query Parquet, CSV, and JSON files on object storage directly.

| Scenario | Reference |
|------|---------|
| Query object storage files directly | [Data Lake File Analytics](datalake_volume_analytics.md) |
| Manage and mount object storage | [Volume Management](volume-introduction.md) |

---

## I want to query external data sources (without migrating data)

**Recommended: External Catalog federated queries** — query Hive, Databricks, Snowflake, and other external systems directly without data migration.

| Scenario | Reference |
|------|---------|
| Federated query overview | [Federated Queries](federation-query.md) |
| Query Hive / Hadoop data | [External Catalog](external-catalog-summary.md) |

---

## I want to analyze data with AI

| Scenario | Approach | Reference |
|------|------|---------|
| Ask questions in natural language, AI generates SQL automatically | Data Analytics Agent (DataGPT) conversational analysis | [Data Analytics Agent (DataGPT) Introduction](datagpt_intro.md) · [Data Analytics Agent (DataGPT) Tutorial](LakehouseDataGPT-tour.md) |
| Semantic search / RAG applications | Vector search | [Vector Search](vector-search.md) · [Vector Search and RAG Applications in Practice](SQL_Vector_Search_Guide.md) |
| Call large language models from SQL | AI functions | [AI Functions in SQL](AI_function_in_SQL.md) |
| Query using business terms (no JOINs needed) | Semantic views | [Semantic View Overview](semantic-view-overview.md) |

---

## I want to optimize query performance

| Scenario | Approach | Reference |
|------|------|---------|
| High-frequency complex queries are slow | Materialized views (pre-computation + query rewriting) | [Materialized Views](MATERIALIZEDVIEW.md) |
| Cache repeated query results | Result Cache | [Performance Optimization](performance_optimization.md) |
| Large table scans are slow | Sort columns / partition design | [Table Design Best Practices](lakehouse_table_design_guide.md) |
| Too many small files affecting performance | Small file compaction | [Performance Optimization](performance_optimization.md) |
| Query is slow, want to identify the bottleneck | Job Profile diagnostics | [Job History Analysis](jobprofile-bestpractices.md) |

---

## Not sure which approach to use?

```Plain
What is your analysis need?
├── Data is already in Lakehouse tables
│   ├── One-off query / report → write SQL directly
│   ├── High-frequency complex queries need acceleration → materialized views
│   └── Ask questions in natural language → Data Analytics Agent (DataGPT)
├── Data is in object storage (OSS / S3 / COS)
│   ├── No long-term retention needed → query directly via Volume
│   └── Need ongoing analysis → import into a table first, then query
└── Data is in another system (Hive / Snowflake, etc.)
    ├── Don't want to migrate data → External Catalog federated queries
    └── Need long-term analysis → sync to Lakehouse first
```
