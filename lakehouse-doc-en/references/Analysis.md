# Data Analysis and SQL Guide

Singdata Lakehouse analytical capabilities span five areas: interactive SQL queries and analysis, data writing and modification, real-time and incremental processing, object and storage management, and SQL syntax and function reference.

---

## Data Querying and Analysis

Write SQL directly in Studio with support for standard SQL syntax, including window functions, CTEs, JOINs, subqueries, and more.

**Entry document**: [Data Querying and Analysis](sql_query_analysis_guide.md)

| Scenario | Reference |
|----------|-----------|
| Data deduplication (ROW_NUMBER / DISTINCT / BITMAP) | [Data Deduplication](sql_deduplication_guide.md) |
| Basic filtering and sorting | [Basic Data Filtering and Sorting](sql_filter_sort_guide.md) |
| Group aggregation (GROUP BY / ROLLUP / CUBE) | [Data Group Aggregation](sql_group_aggregation_guide.md) |
| Ranking and percentile analysis (RANK / NTILE / PERCENTILE) | [Ranking and Percentile Analysis](sql_ranking_guide.md) |
| Time series analysis (YoY / MoM / sliding window) | [Time Series Analysis](sql_timeseries_guide.md) |
| Funnel analysis and user behavior paths | [Funnel Analysis and User Behavior](sql_funnel_analysis_guide.md) |
| Session analysis (Sessionization) | [Session Analysis](sql_sessionization_guide.md) |
| Retention and cohort analysis | [Retention and Cohort Analysis](sql_retention_cohort_guide.md) |
| Marketing attribution analysis (first/last/linear/time decay) | [Marketing Attribution Analysis](sql_attribution_guide.md) |
| Hierarchical queries (org chart / BOM) | [Hierarchical Query Workaround](sql_hierarchy_workaround_guide.md) |
| String processing | [String Processing](sql_string_processing_guide.md) |
| Data pivoting (rows to columns / columns to rows) | [Data Pivoting and Transposition](sql_pivot_guide.md) |
| Missing value filling and handling | [Missing Value Handling](sql_null_handling_guide.md) |
| Data type conversion | [Data Type Conversion](sql_type_conversion_guide.md) |
| JSON data parsing | [JSON Data Parsing](sql_json_parsing_guide.md) |
| Cumulative calculations and running totals | [Cumulative Calculations and Running Totals](sql_running_total_guide.md) |
| BITMAP user segmentation and analysis | [BITMAP User Analysis](sql_bitmap_guide.md) |
| Data sampling and exploration | [Data Sampling and Exploration](sql_sampling_guide.md) |
| Data comparison and merging (UNION / INTERSECT / EXCEPT) | [Data Comparison and Merging](sql_set_operations_guide.md) |
| Semi-structured data analysis | [Semi-structured Data Analysis](json_analyze.md) |

---

## Data Writing and Modification

**Entry document**: [Data Writing and Modification](sql_write_change_guide.md)

| Scenario | Reference |
|----------|-----------|
| Batch data insertion (INSERT / INSERT OVERWRITE) | [Batch Data Insertion](sql_batch_insert_guide.md) |
| Upsert operations (MERGE INTO) | [Upsert Operations](sql_upsert_guide.md) |
| Data updates and cleanup (UPDATE / DELETE) | [Data Updates and Cleanup](sql_update_delete_guide.md) |
| Table cloning and quick backup (zero-copy clone) | [Table Cloning and Quick Backup](sql_clone_guide.md) |

---

## Real-time and Incremental Processing

**Entry document**: [Real-time and Incremental Processing](sql_realtime_guide.md)

| Scenario | Reference |
|----------|-----------|
| Declarative incremental computation (Dynamic Table) | [Dynamic Table Development Guide](sql_dynamic_table_guide.md) |
| Row-level change capture CDC (Table Stream) | [Table Stream Change Data Capture](sql_table_stream_guide.md) |
| Continuous data ingestion (Pipe) | [Continuous Data Ingestion](sql_pipe_guide.md) |

---

## Object and Storage Management

**Entry document**: [Object and Storage Management](sql_object_storage_guide.md)

| Scenario | Reference |
|----------|-----------|
| Views and materialized views | [Views and Materialized Views](sql_view_guide.md) |
| Semantic views (business term queries) | [Semantic View Usage Guide](semantic_view.md) |
| Volume file management | [Volume File Management](sql_volume_guide.md) |
| Bulk file import/export (COPY INTO) | [Bulk File Import/Export](sql_copy_into_guide.md) |
| External table queries (Parquet / ORC / CSV) | [External Table Queries](sql_external_table_guide.md) |
| Federated queries (Hive / Databricks / Snowflake) | [Federated Queries](sql_external_catalog_guide.md) |
| Cross-instance data sharing | [Cross-instance Data Sharing](sql_share_guide.md) |
| Query acceleration indexes (Bloomfilter / inverted / vector) | [Query Acceleration Indexes](sql_index_guide.md) |
| Historical data lookback (Time Travel) | [Historical Data Lookback](sql_time_travel_guide.md) |

---

## SQL Syntax and Optimization

**Entry document**: [SQL Syntax and Optimization](sql_syntax_guide.md)

| Scenario | Reference |
|----------|-----------|
| CREATE TABLE syntax | [SQL CREATE TABLE Guide](sql_create_table_guide.md) |
| DML considerations | [SQL DML Guide](sql_dml_considerations.md) |
| SELECT considerations | [SQL SELECT Guide](sql_select_considerations.md) |
| JOIN patterns and optimization | [SQL Join Guide](sql_join_guide.md) |
| CTE patterns | [SQL With CTE Guide](sql_with_cte_guide.md) |
| Partitioned table usage | [Partitioned Table Guide](notes-and-guidelines-for-partition-tables.md) |
| Generated columns | [Generated Columns Guide](generated_columns_guide.md) |
| JSON query syntax | [JSON Query Syntax](query-json-sy.md) |
| JSON data processing | [JSON Data Processing Guide](json_data_process_guide.md) |
| VECTOR data processing | [VECTOR Data Processing Guide](vector_data_process_guide.md) |
| Execution plan analysis (EXPLAIN) | [Execution Plan Analysis](sql_explain_guide.md) |
| Small file compaction optimization | [Small File Compaction Optimization](sql_optimize_guide.md) |

---

## SQL Function Usage Guide

**Entry document**: [SQL Function Usage Guide](sql_functions_guide.md)

| Scenario | Reference |
|----------|-----------|
| Array and Map processing | [Array and Map Processing in Practice](sql_array_map_processing_guide.md) |
| Approximate aggregate functions (HyperLogLog / KLL) | [Approximate Aggregate Functions in Practice](sql_approx_aggregate_functions_guide.md) |
| Array expansion and flattening (EXPLODE / UNNEST) | [Array Expansion and Flattening in Practice](sql_array_explode_guide.md) |
| Full-text search and text analysis | [Full-text Search and Text Analysis in Practice](sql_fulltext_search_guide.md) |
| Vector search and RAG applications | [Vector Search and RAG Applications in Practice](sql_vector_search_guide.md) |

---

## Connecting BI Tools for Reporting

Most mainstream BI tools connect via JDBC / ODBC.

| BI Tool | Reference |
|---------|-----------|
| FineBI | [FineBI Connection Guide](finebi.md) |
| PowerBI | [PowerBI Connection Guide](powerbi.md) |
| Tableau | [Tableau Connection Guide](tableau-connect-to-lakehouse.md) |
| Superset | [Superset Connection Guide](eco_integration/superset.md) |
| Other tools | [Ecosystem Integration Overview](ecosystem-all.md) |

---

## Analyzing Data with AI

| Scenario | Solution | Reference |
|----------|----------|-----------|
| Ask questions in natural language, AI auto-generates SQL | Data Analytics Agent (DataGPT) | [DataGPT Introduction](datagpt_intro.md) · [DataGPT Tutorial](lakehousedatagpt-tour.md) |
| Semantic search / RAG applications | Vector search | [Vector Search](vector-search.md) · [Vector Search and RAG Applications in Practice](sql_vector_search_guide.md) |
| Call large language models in SQL | AI functions | [AI Function Usage Guide](ai_function_in_sql.md) |
| Query using business terms (no JOIN needed) | Semantic views | [Semantic View Overview](semantic-view-overview.md) |

---

## Query Performance Optimization

| Scenario | Solution | Reference |
|----------|----------|-----------|
| High-frequency complex queries are slow | Materialized views (pre-computation + query rewriting) | [Materialized Views](materializedview.md) |
| Cache repeated query results | Result Cache | [Performance Optimization](performance_optimization.md) |
| Large table scans are slow | Sort columns / partition design | [Table Design Best Practices](lakehouse_table_design_guide.md) |
| Too many small files affecting performance | Small file compaction | [Small File Compaction Optimization](sql_optimize_guide.md) |
| Slow queries, want to locate bottlenecks | Job Profile diagnostics | [Job History Analysis](jobprofile-bestpractices.md) |
