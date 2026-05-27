# Lakehouse Batch Insert Guide

## Overview

Inserting data into tables is a fundamental operation in data warehouse construction. Singdata Lakehouse supports multiple data insertion methods, including single-row inserts, multi-row inserts, query result inserts, and overwrite inserts. This guide categorizes insertion methods by business scenario to help you quickly master efficient data loading techniques.

### Quick Navigation

* [Single-Row and Multi-Row Insert](#single-row-and-multi-row-insert) -- Insert small amounts of data using VALUES
* [Query Result Insert](#query-result-insert) -- Batch import using INSERT INTO ... SELECT
* [Overwrite Insert](#overwrite-insert) -- Refresh partitions or entire tables using INSERT OVERWRITE
* [Specified Column Insert](#specified-column-insert) -- Insert only certain columns; others use defaults or NULL

***

## SQL Commands Covered

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `INSERT INTO ... VALUES` | Insert literal data | Test data, configuration tables, small record counts |
| `INSERT INTO ... SELECT` | Insert query results | ETL data transfer, batch import |
| `INSERT OVERWRITE` | Overwrite write | Refresh partition data, rebuild table data |

***

## Prerequisites

The following examples use a simulated product table `products`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS products (
    product_id INT,
    product_name STRING,
    category STRING,
    price DOUBLE,
    stock INT
);
```

***

## Single-Row and Multi-Row Insert

Use the `VALUES` clause to insert one or more rows. Suitable for test data or small batches of configuration data.

```sql
-- Insert a single row
INSERT INTO products VALUES (1, 'iPhone 15', 'Phone', 8000, 100);

-- Insert multiple rows
INSERT INTO products VALUES
(2, 'MacBook Pro', 'Laptop', 15000, 50),
(3, 'AirPods', 'Audio', 1200, 200);
```

**Verify Results**:

```sql
SELECT * FROM products ORDER BY product_id;
```

| product_id | product_name | category | price | stock |
|------------|--------------|----------|-------|-------|
| 1 | iPhone 15 | Phone | 8000 | 100 |
| 2 | MacBook Pro | Laptop | 15000 | 50 |
| 3 | AirPods | Audio | 1200 | 200 |

> **Note**: The `VALUES` method is suitable for small data volumes under 100 rows. For large batch data import, `COPY INTO` or `INSERT INTO ... SELECT` is recommended.

***

## Query Result Insert

Use `INSERT INTO ... SELECT` to batch insert query results into the target table, the most common data writing method in ETL pipelines.

```sql
-- Create target table
CREATE TABLE IF NOT EXISTS phone_products (
    product_id INT,
    product_name STRING,
    price DOUBLE
);

-- Filter and insert from source table
INSERT INTO phone_products
SELECT product_id, product_name, price
FROM products
WHERE category = 'Phone';
```

**Verify Results**:

```sql
SELECT * FROM phone_products;
```

| product_id | product_name | price |
|------------|--------------|-------|
| 1 | iPhone 15 | 8000 |

***

## Overwrite Insert

Use `INSERT OVERWRITE` to overwrite existing data in the target table (or partition). Commonly used for daily data refreshes or rebuilding a specific partition.

```sql
-- Overwrite entire table data
INSERT OVERWRITE TABLE products
SELECT * FROM products WHERE stock > 0;
```

> **Note**:
> * For **non-partitioned tables**, `INSERT OVERWRITE` clears all table data before writing new data.
> * For **partitioned tables**, `INSERT OVERWRITE` only overwrites matching partitions; other partitions are unaffected.

***

## Specified Column Insert

When only certain columns need to be inserted, explicitly specify column names. Unspecified columns will use default values or `NULL`.

```sql
-- Insert only some columns
INSERT INTO products (product_id, product_name, category)
VALUES (4, 'iPad Air', 'Tablet');
```

**Verify Results**:

```sql
SELECT product_id, product_name, category, price, stock 
FROM products 
WHERE product_id = 4;
```

| product_id | product_name | category | price | stock |
|------------|--------------|----------|-------|-------|
| 4 | iPad Air | Tablet | NULL | NULL |

***

## Clean Up Test Data

After completing insert verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS phone_products;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **Large Batch Import**: For imports exceeding ten thousand rows, use `COPY INTO` from a Volume or use data sync tasks.
2. **Type Matching**: Data types in `VALUES` must match the table definition. Types like DATE, TIME, JSON require literal syntax (e.g., `DATE '2024-06-01'`).
3. **Dynamic Table Limitation**: Dynamic Tables do not support direct `INSERT INTO`; data is refreshed automatically by upstream table changes.
4. **Transactionality**: A single `INSERT` operation is atomic -- either all rows succeed or all fail.

***

## Related Documentation

* [INSERT INTO](INSERT.md)
* [COPY INTO Import](copy-into-table.md)
* [Data Import Overview](data-load-summary.md)
