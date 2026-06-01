# SQL Query Overview

Singdata Lakehouse supports standard SQL SELECT syntax, covering advanced features such as window functions, CTEs, JOINs, semi-structured data queries, and synonyms.

## Contents

| Document | Description |
|------|------|
| [SELECT Syntax Reference](query-syntax.md) | Complete SELECT syntax, parameter descriptions, and usage examples |
| [Window Functions](windowfunction.md) | OVER, PARTITION BY, ROWS/RANGE BETWEEN |
| [JSON Query Syntax](query-json-sy.md) | Native JSON path queries, nested structure access |
| [Join](join.md) | INNER/LEFT/RIGHT/FULL/SEMI/ANTI JOIN |
| [Synonyms](synonym.md) | Create aliases for tables or views to simplify query references |
| [Job Profile](jobprofile-bestpractices.md) | Query execution analysis and performance diagnosis |

## SQL Usage Guides

The following guides provide complete examples for various query scenarios:

**Data Analysis Scenarios**
- [Data Deduplication](sql_deduplication_guide.md)
- [Basic Data Filtering and Sorting](sql_filter_sort_guide.md)
- [Data Grouping and Aggregation](sql_group_aggregation_guide.md)
- [Ranking and Percentile Analysis](sql_ranking_guide.md)
- [Time Series Analysis](sql_timeseries_guide.md)
- [Funnel Analysis and User Behavior](sql_funnel_analysis_guide.md)
- [String Processing](sql_string_processing_guide.md)
- [Data Pivot and Row-Column Transposition](sql_pivot_guide.md)
- [Missing Value Filling](sql_null_handling_guide.md)
- [Cumulative Calculation and Running Totals](sql_running_total_guide.md)
- [BITMAP User Analysis](sql_bitmap_guide.md)
- [Data Sampling Exploration](sql_sampling_guide.md)
- [Data Comparison and Merging](sql_set_operations_guide.md)
- [Data Type Conversion](sql_type_conversion_guide.md)

**SQL Syntax Topics**
- [SQL SELECT Usage Guide](sql_select_considerations.md)
- [SQL Join Usage Guide](sql_join_guide.md)
- [SQL With CTE Usage Guide](sql_with_cte_guide.md)
