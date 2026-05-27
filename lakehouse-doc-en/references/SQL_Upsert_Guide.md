# Lakehouse Upsert Operation Guide (MERGE INTO)

## Overview

In data warehouses, it is often necessary to update or insert data into a target table based on source data (i.e., Upsert operations). Singdata Lakehouse provides the `MERGE INTO` statement, which supports handling both matching row updates and non-matching row inserts in a single SQL statement. This guide categorizes usage by business scenario to help you quickly master efficient data merging methods.

### Quick Navigation

* [Basic Upsert](#basic-upsert) -- Update on match, insert on non-match
* [Conditional Update](#conditional-update) -- Update only when specific conditions are met
* [Insert New Data Only](#insert-new-data-only) -- Ignore existing records
* [Delete Orphaned Data](#delete-orphaned-data) -- Delete on match, insert on non-match
* [Multi-Condition Matching](#multi-condition-matching) -- Use complex ON conditions

***

## SQL Commands Covered

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `MERGE INTO ... WHEN MATCHED THEN UPDATE` | Update on match | Data synchronization, status updates |
| `MERGE INTO ... WHEN NOT MATCHED THEN INSERT` | Insert on non-match | New data writing |
| `MERGE INTO ... WHEN MATCHED THEN DELETE` | Delete on match | Clean up invalid data |

***

## Prerequisites

The following examples use a simulated inventory table `inventory` (target) and `daily_stock` (source):

```sql
-- Create target table
CREATE TABLE IF NOT EXISTS inventory (
    product_id INT,
    product_name STRING,
    stock INT,
    last_updated DATE
);

-- Create source table
CREATE TABLE IF NOT EXISTS daily_stock (
    product_id INT,
    new_stock INT,
    update_date DATE
);

-- Insert initial data
INSERT INTO inventory VALUES
(1, 'iPhone 15', 100, '2024-06-01'),
(2, 'MacBook Pro', 50, '2024-06-01');

-- Insert daily stock data
INSERT INTO daily_stock VALUES
(1, 120, '2024-06-02'),  -- Update existing product
(3, 200, '2024-06-02');  -- New product
```

***

## Basic Upsert

The most common scenario: match by primary key, update if exists, insert if not.

```sql
-- Merge daily stock data into the inventory table
MERGE INTO inventory AS target
USING daily_stock AS source
ON target.product_id = source.product_id
WHEN MATCHED THEN 
    UPDATE SET 
        target.stock = source.new_stock,
        target.last_updated = source.update_date
WHEN NOT MATCHED THEN 
    INSERT (product_id, product_name, stock, last_updated)
    VALUES (source.product_id, 'New Product', source.new_stock, source.update_date);
```

**Verify Result**:

```sql
SELECT * FROM inventory ORDER BY product_id;
```

| product_id | product_name | stock | last_updated |
|------------|--------------|-------|--------------|
| 1 | iPhone 15 | 120 | 2024-06-02 |
| 2 | MacBook Pro | 50 | 2024-06-01 |
| 3 | New Product | 200 | 2024-06-02 |

> **Note**: The `WHEN MATCHED` clause must be written before `WHEN NOT MATCHED`.

***

## Conditional Update

Perform update operations only when specific conditions are met, avoiding unnecessary writes.

```sql
-- Update only when new stock is greater than old stock
MERGE INTO inventory AS target
USING daily_stock AS source
ON target.product_id = source.product_id
WHEN MATCHED AND source.new_stock > target.stock THEN 
    UPDATE SET 
        target.stock = source.new_stock,
        target.last_updated = source.update_date
WHEN NOT MATCHED THEN 
    INSERT (product_id, product_name, stock, last_updated)
    VALUES (source.product_id, 'New Product', source.new_stock, source.update_date);
```

**Result**:
* `product_id = 1`: New stock 120 > old stock 120 (already updated last time), condition not met, no update.
* `product_id = 3`: No match, insert new record.

***

## Insert New Data Only

Ignore existing records and only insert new data from the source table (similar to `INSERT IGNORE`).

```sql
-- Insert only non-matching records
MERGE INTO inventory AS target
USING daily_stock AS source
ON target.product_id = source.product_id
WHEN NOT MATCHED THEN 
    INSERT (product_id, product_name, stock, last_updated)
    VALUES (source.product_id, 'New Product', source.new_stock, source.update_date);
```

***

## Delete Orphaned Data

When source data is marked for deletion, remove the corresponding records from the target table.

```sql
-- Assume stock = 0 in daily_stock means delisted
MERGE INTO inventory AS target
USING daily_stock AS source
ON target.product_id = source.product_id
WHEN MATCHED AND source.new_stock = 0 THEN DELETE
WHEN NOT MATCHED THEN 
    INSERT (product_id, product_name, stock, last_updated)
    VALUES (source.product_id, 'New Product', source.new_stock, source.update_date);
```

***

## Multi-Condition Matching

Use complex `ON` conditions for matching, suitable for composite primary keys or business logic matching.

```sql
-- Match by product ID and date
MERGE INTO inventory AS target
USING daily_stock AS source
ON target.product_id = source.product_id 
   AND target.last_updated < source.update_date
WHEN MATCHED THEN 
    UPDATE SET 
        target.stock = source.new_stock,
        target.last_updated = source.update_date
WHEN NOT MATCHED THEN 
    INSERT (product_id, product_name, stock, last_updated)
    VALUES (source.product_id, 'New Product', source.new_stock, source.update_date);
```

***

## Clean Up Test Data

After completing Upsert verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS daily_stock;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Clause Order**: `WHEN MATCHED` must come before `WHEN NOT MATCHED`, otherwise a syntax error occurs.
2. **Uniqueness Requirement**: The `ON` condition should ensure each source row matches at most one target row; otherwise non-deterministic results may occur.
3. **Dynamic Table Limitation**: Dynamic Tables do not support direct `MERGE INTO`; use `DELETE + INSERT` as an alternative.
4. **Performance Optimization**: Ensure columns in the `ON` condition have indexes or partitions to significantly improve matching efficiency.

***

## Related Documentation

* [MERGE INTO](MERGE.md)
* [INSERT INTO](INSERT.md)
* [UPDATE](UPDATE.md)
