# Lakehouse Dynamic Table Development Quick Start Guide

## Overview

Dynamic Tables are the core vehicle for incremental computation in Singdata Lakehouse. You simply declaratively define the query logic, and the system automatically detects upstream data changes and incrementally refreshes results, eliminating the need to manually write complex incremental ETL logic. This guide is organized by development workflow to help you quickly master dynamic table creation, refresh, and monitoring methods.

### Quick Navigation

* [Create Dynamic Table](#create-dynamic-table) -- Declaratively define incremental computation logic
* [Manual Refresh](#manual-refresh) -- Use REFRESH to trigger computation immediately
* [View Refresh History](#view-refresh-history) -- Monitor refresh status and mode
* [View Dynamic Table Structure](#view-dynamic-table-structure) -- Use DESC to view definition
* [Drop Dynamic Table](#drop-dynamic-table) -- Use DROP DYNAMIC TABLE to clean up

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE DYNAMIC TABLE ... AS SELECT` | Create dynamic table | Declaratively define incremental computation logic |
| `REFRESH DYNAMIC TABLE` | Manual refresh trigger | Compute latest results immediately |
| `SHOW DYNAMIC TABLE REFRESH HISTORY` | View refresh history | Monitor refresh status |
| `DESC DYNAMIC TABLE` | View dynamic table structure | View definition and configuration |
| `DROP DYNAMIC TABLE` | Drop dynamic table | Clean up dynamic tables no longer needed |

***

## Prerequisites

The following examples use simulated orders table `orders_dt` and products table `products_dt`:

```sql
-- Create orders table
CREATE TABLE IF NOT EXISTS orders_dt (
    order_id INT,
    product_id INT,
    quantity INT,
    order_date DATE
);

-- Create products table
CREATE TABLE IF NOT EXISTS products_dt (
    product_id INT,
    product_name STRING,
    category STRING
);

-- Insert test data
INSERT INTO products_dt VALUES
(1, 'iPhone 15', 'Phone'),
(2, 'MacBook Pro', 'Laptop'),
(3, 'AirPods', 'Audio');

INSERT INTO orders_dt VALUES
(1, 1, 2, '2024-06-01'),
(2, 2, 1, '2024-06-01'),
(3, 1, 1, '2024-06-02');
```

***

## Create Dynamic Table

Use `CREATE DYNAMIC TABLE` to declaratively define computation logic. The system automatically handles incremental computation.

```sql
-- Create a dynamic table summarizing by product category
CREATE DYNAMIC TABLE dt_category_sales
    REFRESH INTERVAL 10 MINUTE VCLUSTER default
AS
SELECT 
    p.category,
    COUNT(*) as order_count,
    SUM(o.quantity) as total_quantity
FROM orders_dt o
JOIN products_dt p ON o.product_id = p.product_id
GROUP BY p.category;
```

**Parameter Descriptions**:
* `REFRESH INTERVAL 10 MINUTE`: Automatically refresh every 10 minutes.
* `VCLUSTER default`: Specifies the compute cluster used for the refresh.

> ⚠️ **Note**: After creation, it is recommended to immediately execute `REFRESH` once to reset the refresh time baseline.

***

## Manual Refresh

Use `REFRESH DYNAMIC TABLE` to trigger computation immediately without waiting for scheduled refresh.

```sql
-- Manually trigger refresh
REFRESH DYNAMIC TABLE dt_category_sales;
```

**Result Verification**:

```sql
SELECT * FROM dt_category_sales ORDER BY category;
```

| category | order_count | total_quantity |
|----------|-------------|----------------|
| Laptop | 1 | 1 |
| Phone | 2 | 3 |

> 💡 **Tip**: After inserting new data into the source table, execute `REFRESH` to see the incremental computation results.

***

## View Refresh History

Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to monitor refresh status and determine whether it was an incremental or full refresh.

```sql
-- View the last 5 refresh records
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'dt_category_sales' LIMIT 5;
```

**Key Field Descriptions**:
* `state`: Refresh status (SUCCEED / FAILED / RUNNING)
* `refresh_mode`: Refresh mode (INCREMENTAL / FULL)
* `refresh_trigger`: Trigger method (MANUAL / SYSTEM_SCHEDULED)

***

## View Dynamic Table Structure

Use `DESC DYNAMIC TABLE` to view the dynamic table's definition and configuration.

```sql
-- View dynamic table structure
DESC DYNAMIC TABLE dt_category_sales;
```

**Returned Information**:
* Table structure (column names, types)
* Refresh interval
* VCluster used
* Underlying SQL definition

***

## Incremental Computation Verification

Insert new data into the source table to verify the dynamic table's incremental refresh capability.

```sql
-- Insert a new order
INSERT INTO orders_dt VALUES (4, 3, 5, '2024-06-03');

-- Manual refresh
REFRESH DYNAMIC TABLE dt_category_sales;

-- View updated results
SELECT * FROM dt_category_sales ORDER BY category;
```

**Result Explanation**:

| category | order_count | total_quantity |
|----------|-------------|----------------|
| Audio | 1 | 5 |
| Laptop | 1 | 1 |
| Phone | 2 | 3 |

> ⚠️ **Note**: The Audio category changed from 0 to 1, demonstrating that incremental computation correctly captured the new data.

***

## Drop Dynamic Table

Use `DROP DYNAMIC TABLE` to drop a dynamic table. Note that you must use `DROP DYNAMIC TABLE`, not `DROP TABLE`.

```sql
-- Drop dynamic table
DROP DYNAMIC TABLE dt_category_sales;
```

> 💡 **Tip**: Dropped dynamic tables can be recovered via `UNDROP TABLE` within the Time Travel retention period.

***

## Clean Up Test Data

After completing dynamic table verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS orders_dt;
DROP TABLE IF EXISTS products_dt;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **VCluster Selection**: Use `GENERAL` type VClusters (such as `default`), not `ANALYTICS` type.
2. **Refresh Frequency**: Higher frequency leads to higher CRU consumption. Use `1 DAY` for T+1 scenarios, `1 HOUR` for hourly.
3. **Non-deterministic Functions**: Avoid using non-deterministic functions like `CURRENT_TIMESTAMP()`, `RAND()` in Dynamic Tables.
4. **DROP Syntax**: You must use `DROP DYNAMIC TABLE`; using `DROP TABLE` will produce an error.
5. **Incremental Limitations**: Some complex queries (such as outer JOINs with non-equi conditions) may not execute incrementally; the system will automatically fall back to full refresh.

***

## Related Documentation

* [Dynamic Table Introduction](dynamic-table-introduce.md)
* [CREATE DYNAMIC TABLE](create-dynamic-table.md)
* [View Refresh History](refresh-history.md)
* [Incremental Computation Mechanism](incremental-computing.md)
