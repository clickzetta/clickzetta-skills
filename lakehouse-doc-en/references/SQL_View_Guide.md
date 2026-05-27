# Lakehouse View and Materialized View Guide

## Overview

Views and Materialized Views are important tools for encapsulating complex query logic and simplifying data access. A View is a virtual table that computes results dynamically at query time; a Materialized View pre-computes and stores results, supporting query rewrite acceleration. This guide is organized by business scenario to help you quickly master view creation and management methods.

### Quick Navigation

* [Create a Regular View](#create-a-regular-view) -- Encapsulate complex query logic
* [Create a Materialized View](#create-a-materialized-view) -- Pre-compute results to accelerate queries
* [Refresh a Materialized View](#refresh-a-materialized-view) -- Manually update pre-computed data
* [Query Rewrite Verification](#query-rewrite-verification) -- Confirm queries automatically use materialized views
* [Drop Views](#drop-views) -- Clean up views no longer needed

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE VIEW` | Create a logical view | Encapsulate JOIN/aggregation to simplify queries |
| `CREATE MATERIALIZED VIEW` | Create a materialized view | Pre-compute high-frequency query results |
| `REFRESH MATERIALIZED VIEW` | Refresh a materialized view | Update pre-computed data |
| `DROP VIEW` / `DROP MATERIALIZED VIEW` | Drop a view | Clean up abandoned views |

***

## Prerequisites

The following examples use a simulated sales detail table `sales_detail`:

```sql
-- Create source table
CREATE TABLE IF NOT EXISTS sales_detail (
    sale_id INT,
    product_id INT,
    region STRING,
    amount DOUBLE,
    sale_date DATE
);

-- Insert test data
INSERT INTO sales_detail VALUES
(1, 101, 'East', 5000, '2024-06-01'),
(2, 102, 'West', 3000, '2024-06-01'),
(3, 101, 'East', 5000, '2024-06-02');
```

***

## Create a Regular View

Use `CREATE VIEW` to define a logical view. Views do not store data; they dynamically execute the underlying SQL at query time.

```sql
-- Create a view summarizing by region
CREATE VIEW v_region_sales AS
SELECT 
    region,
    COUNT(*) as sale_count,
    SUM(amount) as total_amount
FROM sales_detail
GROUP BY region;
```

**Using the View**:

```sql
SELECT * FROM v_region_sales ORDER BY total_amount DESC;
```

**Result Explanation**:

| region | sale_count | total_amount |
|--------|------------|--------------|
| East | 2 | 10000 |
| West | 1 | 3000 |

> **Tip**: Views are suitable for encapsulating complex logic, but they recompute every query. For high-frequency queries, consider using Materialized Views.

***

## Create a Materialized View

Use `CREATE MATERIALIZED VIEW` to create a pre-computed view. Materialized views store actual data and can be automatically rewritten to by the optimizer at query time.

```sql
-- Create a materialized view summarizing by date
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT 
    sale_date,
    SUM(amount) as daily_total
FROM sales_detail
GROUP BY sale_date;
```

**Query the Materialized View**:

```sql
SELECT * FROM mv_daily_sales ORDER BY sale_date;
```

**Result Explanation**:

| sale_date | daily_total |
|-----------|-------------|
| 2024-06-01 | 8000 |
| 2024-06-02 | 5000 |

> **Note**: Materialized views are not automatically refreshed upon creation; you need to manually execute `REFRESH` or configure scheduled refresh.

***

## Refresh a Materialized View

When source table data changes, use `REFRESH MATERIALIZED VIEW` to update the materialized view.

```sql
-- Insert new data into the source table
INSERT INTO sales_detail VALUES (4, 103, 'South', 4000, '2024-06-03');

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW mv_daily_sales;

-- Verify the refresh result
SELECT * FROM mv_daily_sales WHERE sale_date = '2024-06-03';
```

**Result Explanation**:

| sale_date | daily_total |
|-----------|-------------|
| 2024-06-03 | 4000 |

***

## Query Rewrite Verification

The Singdata Lakehouse optimizer automatically rewrites queries on source tables to use materialized views, thereby accelerating response times.

```sql
-- Query the source table directly (the optimizer may automatically rewrite it to use mv_daily_sales)
SELECT sale_date, SUM(amount) as total
FROM sales_detail
GROUP BY sale_date;
```

> **Tip**: Use `EXPLAIN` to view the execution plan and confirm whether a materialized view rewrite was triggered.

***

## Drop Views

Use `DROP VIEW` or `DROP MATERIALIZED VIEW` to drop views.

```sql
-- Drop a regular view
DROP VIEW v_region_sales;

-- Drop a materialized view
DROP MATERIALIZED VIEW mv_daily_sales;
```

> **Tip**: Dropping a materialized view does not delete the source table data. Materialized views can be recovered via `UNDROP TABLE` within the Time Travel retention period.

***

## Clean Up Test Data

After completing view verification, it is recommended to clean up the test table:

```sql
-- Drop the test table
DROP TABLE IF EXISTS sales_detail;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **View Dependencies**: Dropping a source table will invalidate views that depend on it. Use `DESC VIEW` to check dependency relationships.
2. **Materialized View Refresh**: Materialized views are not auto-refreshed by default. For near-real-time data scenarios, consider using Dynamic Tables.
3. **Query Rewrite Conditions**: The optimizer only rewrites queries when the materialized view's aggregation dimensions exactly match the query.
4. **Storage Cost**: Materialized views consume additional storage space, proportional to the pre-computed result set size.
5. **DROP Syntax**: Dropping a materialized view must use `DROP MATERIALIZED VIEW`, not `DROP VIEW`.

***

## Related Documentation

* [Views](VIEW.md)
* [Materialized Views](materialized_ddl.md)
* [Dynamic Table Development Quick Start](SQL_Dynamic_Table_Guide.md)
