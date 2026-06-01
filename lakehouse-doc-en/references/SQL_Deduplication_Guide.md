# Lakehouse Data Deduplication Guide

## Overview

In data warehouse construction, data deduplication is one of the most common requirements. Singdata Lakehouse provides multiple deduplication approaches, from simple `DISTINCT` to complex window function-based deduplication, meeting the needs of various business scenarios. This guide categorizes usage by scenario to help you quickly select and implement the optimal deduplication approach.

### Quick Navigation

* [Completely Duplicate Row Deduplication](#completely-duplicate-row-deduplication) -- Use `DISTINCT` for quick deduplication
* [Keep the Latest Record](#keep-the-latest-record) -- Use `ROW_NUMBER()` + `QUALIFY` to keep the latest data
* [Multi-Field Combination Deduplication](#multi-field-combination-deduplication) -- Use `GROUP BY` + aggregate functions
* [Physical Deduplication (Rewrite Table)](#physical-deduplication-rewrite-table) -- Write deduplicated results to a new table or overwrite the original

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `SELECT DISTINCT` | Remove completely duplicate rows | Duplicate data where all fields are identical |
| `ROW_NUMBER() OVER (...)` | Generate unique sequence numbers for each group | Need to keep specific rows by time/priority |
| `QUALIFY` | Directly filter window function results | Substitute for subqueries, simplifies SQL |
| `GROUP BY` + `MAX/MIN/ANY_VALUE` | Group aggregation deduplication | Only need to keep some fields or any one row |
| `INSERT OVERWRITE` | Overwrite with deduplicated data | Physically clean duplicate data |

***

## Prerequisites

The following examples use a simulated order table `orders_with_dupes` containing duplicate data:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS orders_with_dupes (
    order_id STRING,
    customer_id INT,
    amount DOUBLE,
    order_time TIMESTAMP
);

-- Insert test data (including duplicates)
INSERT INTO orders_with_dupes VALUES
('O001', 101, 100.0, '2024-06-01 10:00:00'),
('O001', 101, 100.0, '2024-06-01 10:00:00'),  -- Completely duplicate
('O002', 102, 200.0, '2024-06-01 11:00:00'),
('O002', 102, 200.0, '2024-06-01 11:05:00'),  -- Same order ID, different time
('O003', 103, 300.0, '2024-06-01 12:00:00');
```

***

## Completely Duplicate Row Deduplication

When all fields in a row are exactly the same, using `DISTINCT` is the simplest and most efficient approach.

```sql
-- Query deduplicated results
SELECT DISTINCT *
FROM orders_with_dupes;
```

**Result**:

| order_id | customer_id | amount | order_time |
|----------|-------------|--------|------------|
| O001 | 101 | 100 | 2024-06-01 10:00:00 |
| O002 | 102 | 200 | 2024-06-01 11:00:00 |
| O002 | 102 | 200 | 2024-06-01 11:05:00 |
| O003 | 103 | 300 | 2024-06-01 12:00:00 |

> ⚠️ **Note**: `DISTINCT` performs hash comparison on all columns. For very large data volumes, filter before applying `DISTINCT`.

***

## Keep the Latest Record

In business scenarios, it is often necessary to keep the latest record based on a timestamp (e.g., duplicate log reports, order statuses updated multiple times). Lakehouse recommends using `ROW_NUMBER()` with the `QUALIFY` clause for cleaner syntax.

```sql
-- Keep the record with the latest order_time for each order_id
SELECT 
    order_id,
    customer_id,
    amount,
    order_time
FROM orders_with_dupes
WINDOW w AS (PARTITION BY order_id ORDER BY order_time DESC)
QUALIFY ROW_NUMBER() OVER w = 1;
```

**Result**:

| order_id | customer_id | amount | order_time |
|----------|-------------|--------|------------|
| O001 | 101 | 100 | 2024-06-01 10:00:00 |
| O002 | 102 | 200 | 2024-06-01 11:05:00 |
| O003 | 103 | 300 | 2024-06-01 12:00:00 |

### Syntax Advantages

Using `QUALIFY` avoids nested subqueries, making SQL more readable:

```sql
-- Traditional approach (nested subquery)
SELECT order_id, customer_id, amount, order_time
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_time DESC) as rn
    FROM orders_with_dupes
) t
WHERE rn = 1;

-- Lakehouse recommended approach (QUALIFY)
SELECT order_id, customer_id, amount, order_time
FROM orders_with_dupes
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_time DESC) = 1;
```

***

## Multi-Field Combination Deduplication

When duplicate data differs only in some fields (e.g., different timestamps) and you only need to keep key fields, use `GROUP BY` with aggregate functions.

```sql
-- Group by order_id, keep the max amount and latest time
SELECT 
    order_id,
    customer_id,
    MAX(amount) as max_amount,
    MAX(order_time) as latest_time
FROM orders_with_dupes
GROUP BY order_id, customer_id;
```

**Applicable Scenarios**:
* Only need dimensional statistics, not concerned with which specific record.
* Data volume is very large and window function performance is worse than aggregate functions.

***

## Physical Deduplication (Rewrite Table)

Query-level deduplication is only logical. To physically clean duplicate data, write deduplicated results back to the original table or a new table.

### Option 1: Write to a New Table (Recommended)

```sql
-- Create a new deduplicated table
CREATE TABLE orders_deduped AS
SELECT *
FROM orders_with_dupes
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_time DESC) = 1;
```

### Option 2: Overwrite Original Table

```sql
-- Overwrite original table data (use with caution)
INSERT OVERWRITE TABLE orders_with_dupes
SELECT *
FROM orders_with_dupes
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_time DESC) = 1;
```

***

## Clean Up Test Data

After completing deduplication verification, it is recommended to clean up test tables to free storage space:

```sql
-- Drop test tables
DROP TABLE IF EXISTS orders_with_dupes;
DROP TABLE IF EXISTS orders_deduped;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Performance Optimization**:
   * For large table deduplication, first use `WHERE` to filter out obviously invalid data.
   * If the table is partitioned, deduplicating by partition can significantly reduce computation.

2. **NULL Value Handling**:
   * `DISTINCT` treats multiple `NULL` values as the same, keeping only one row.
   * When sorting with `ROW_NUMBER()`, `NULL` values default to last (in `DESC`) or first (in `ASC`), controllable via `NULLS FIRST/LAST`.

3. **Dynamic Table Deduplication**:
   * If deduplication logic is used for a Dynamic Table, prefer the `GROUP BY` approach, as incremental computation support is more complete.
   * `QUALIFY` is fully supported in Dynamic Tables, but complex window functions may cause the refresh mode to switch to full.

***

## Related Documentation

* [SELECT Basic Syntax](query-syntax.md)
* [Window Functions](windowfunction.md)
* [QUALIFY Clause](sql-qualify.md)
* [INSERT OVERWRITE Behavior](sql_dml_considerations.md)
