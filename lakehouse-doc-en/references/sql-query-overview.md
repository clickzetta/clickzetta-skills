# SQL Query Overview

Singdata Lakehouse supports standard SQL SELECT syntax, covering advanced features such as window functions, CTEs, JOINs, semi-structured data queries, and synonyms.

## Contents

| Document | Description |
|------|------|
| [SELECT Syntax Reference](query-syntax.md) | Complete SELECT syntax, parameter descriptions, and usage examples |
| [Window Functions](WINDOWFUNCTION.md) | OVER, PARTITION BY, ROWS/RANGE BETWEEN |
| [JSON Query Syntax](query-json-sy.md) | Native JSON path queries, nested structure access |
| [Join](JOIN.md) | INNER/LEFT/RIGHT/FULL/SEMI/ANTI JOIN |
| [Synonyms](synonym.md) | Create aliases for tables or views to simplify query references |
| [Job Profile](jobprofile-bestpractices.md) | Query execution analysis and performance diagnosis |

## SQL Usage Guides

The following guides provide complete examples for various query scenarios:

**Data Analysis Scenarios**
- [Data Deduplication](SQL_Deduplication_Guide.md)
- [Basic Data Filtering and Sorting](SQL_Filter_Sort_Guide.md)
- [Data Grouping and Aggregation](SQL_Group_Aggregation_Guide.md)
- [Ranking and Percentile Analysis](SQL_Ranking_Guide.md)
- [Time Series Analysis](SQL_TimeSeries_Guide.md)
- [Funnel Analysis and User Behavior](SQL_Funnel_Analysis_Guide.md)
- [String Processing](SQL_String_Processing_Guide.md)
- [Data Pivot and Row-Column Transposition](SQL_Pivot_Guide.md)
- [Missing Value Filling](SQL_Null_Handling_Guide.md)
- [Cumulative Calculation and Running Totals](SQL_Running_Total_Guide.md)
- [BITMAP User Analysis](SQL_Bitmap_Guide.md)
- [Data Sampling Exploration](SQL_Sampling_Guide.md)
- [Data Comparison and Merging](SQL_Set_Operations_Guide.md)
- [Data Type Conversion](SQL_Type_Conversion_Guide.md)

**SQL Syntax Topics**
- [SQL SELECT Usage Guide](SQL_SELECT_Considerations.md)
- [SQL Join Usage Guide](SQL_Join_Guide.md)
- [SQL With CTE Usage Guide](SQL_With_CTE_Guide.md)
