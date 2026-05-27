# Description

The ANALYZE TABLE statement is used to collect statistics for a specific table or all tables within a specified schema. Statistics include table size, row count, etc., which the query optimizer uses to generate the best query plan. Although these statistics may become outdated as data changes, the query optimizer can still use this outdated information to generate effective query plans. In Lakehouse, the statistics obtained by executing the desc command may be delayed, so executing the ANALYZE TABLE statement can obtain the latest statistics.

# Syntax
```SQL
-- Collect statistics for a specified table
ANALYZE TABLE table_name
   COMPUTE STATISTICS [NOSCAN | FOR COLUMNS col1 , col2... | FOR ALL COLUMNS ]

-- Collect statistics for all tables in a specified schema
ANALYZE TABLES [IN schema_name] COMPUTE STATISTICS [NOSCAN]
```
# Parameters

Required parameters:

* table_name: The name of the table for which to collect statistics. Supports specifying tables, dynamic tables, materialized views

Optional parameters:

* NOSCAN: Only collect the size of the table (in bytes), without scanning the entire table
* FOR COLUMNS col1, col2, ...: Collect column statistics for each specified column
* FOR ALL COLUMNS: Collect statistics for all columns
* IN schema_name: Specify the name of the schema to execute, if not specified, the current schema is used by default

# Notes
- When executing the ANALYZE TABLE statement, the table may be scanned, which may affect query performance. It is recommended to perform this operation when the system load is low
- When using the [real-time interface](<java_reference/realtime-upload.md>) in append mode, the ANALYZE TABLE statement will not count uncommitted data. Therefore, there may be cases where the result of select count(*) from table is less.

#  Example

1. Collect statistics for a specified table (without scanning the table), only collect the size of the table (in bytes), without scanning the entire table:
```SQL
ANALYZE TABLE sales COMPUTE STATISTICS NOSCAN;
```
2. Collect column statistics for the specified table:
```SQL
ANALYZE TABLE customers COMPUTE STATISTICS FOR COLUMNS customer_id, customer_name;
```
3. Collect statistics for all tables under the specified schema:
```SQL
ANALYZE TABLES IN sales_schema COMPUTE STATISTICS;
```

4. Collect statistics for all columns of the specified table:

```SQL
ANALYZE TABLE orders COMPUTE STATISTICS FOR ALL COLUMNS;
```
。