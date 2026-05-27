# TABLESAMPLE - Data Sampling

## Overview

TABLESAMPLE is an efficient data sampling method provided by the Singdata Lakehouse platform, supporting random sampling based on probability or a fixed number of rows. With two different sampling strategies (SYSTEM and ROW), you can flexibly balance between performance and accuracy to meet a variety of needs, from rapid data exploration to precise statistical analysis.

### Core Features

* **Flexible Sampling Methods**: Supports percentage-based sampling and fixed-row-count sampling
* **Dual Sampling Strategies**: Provides both file-level (SYSTEM) and row-level (ROW) modes
* **High-Performance Design**: SYSTEM mode is optimized for big data scenarios
* **Precise Control**: ROW mode delivers accurate random sampling results

### Typical Use Cases

| Scenario | Recommended Mode | Description |
| -------- | ------ | -------------- |
| Quick data preview | SYSTEM | High performance, suitable for quickly browsing large tables |
| Data quality check | SYSTEM | Rapidly sample data to verify quality |
| Machine learning training set | ROW | Precise random sampling to ensure sample representativeness |
| Statistical analysis | ROW | Accurate probability sampling meeting statistical requirements |
| Development/test data generation | ROW | Generate small-scale test datasets |
| Large-scale data analysis | SYSTEM | Efficient sampling of datasets with millions of rows or more |

***

## Syntax

```sql
SELECT <column_list>
FROM <table_name>
TABLESAMPLE [ROW | SYSTEM] ( { <percentage> | <num> ROWS } )
[ LIMIT <n> ]
[ ...other clauses... ]
```

### Parameter Description

#### Sampling Type

| Type | Description | Applicable Scenarios | Performance |
| ---------- | ------------------------------ | ------------------------------ | ---------- |
| **ROW** | **Row-level random sampling** - Each row is independently evaluated for sampling, with precise result row counts | Small to medium datasets (< 1 million rows); scenarios requiring precise randomness | Slower, needs to scan all rows |
| **SYSTEM** | **File-level random sampling** - Randomly selects storage file blocks for higher performance | Large datasets (> 1 million rows); quick data exploration | Extremely fast, only reads partial files |
| **Default** | Automatically uses SYSTEM mode when not specified | General purpose | High performance |

#### Sampling Quantity Specification

| Format | Description | Example | Notes |
| -------------- | --------------- | ----------------- | --------- |
| `<percentage>` | Sample by percentage, range 0-100 | `30` means sample 30% | Actual row count may fluctuate |
| `<num> ROWS` | Specify an exact number of rows to sample | `5 ROWS` means sample 5 rows | More precise in ROW mode |

⚠️ **Important Notes**:

* Percentage-based sampling in SYSTEM mode may be imprecise (especially for small datasets)
* It is recommended to add a `LIMIT` clause to the query to optimize performance
* Sampling results are random; each execution may return different data

***

## Usage Examples

### Prepare Test Data

```sql
-- Create a test view
CREATE OR REPLACE VIEW test(id, name) AS
VALUES ( 1, 'Lisa'),
       ( 2, 'Mary'),
       ( 3, 'Evan'),
       ( 4, 'Fred'),
       ( 5, 'Alex'),
       ( 6, 'Mark'),
       ( 7, 'Lily'),
       ( 8, 'Lucy'),
       ( 9, 'Eric'),
       (10, 'Adam');

-- Create a test table
CREATE TABLE employee (id INT, name STRING);

INSERT INTO employee VALUES
       ( 1, 'Lisa'),
       ( 2, 'Mary'),
       ( 3, 'Evan'),
       ( 4, 'Fred'),
       ( 5, 'Alex'),
       ( 6, 'Mark'),
       ( 7, 'Lily'),
       ( 8, 'Lucy'),
       ( 9, 'Eric'),
       (10, 'Adam');
```

### Basic Sampling Examples

#### 1. Percentage Sampling (SYSTEM Mode)

```sql
-- Randomly sample 30% of the data (default SYSTEM mode)
SELECT * FROM test TABLESAMPLE (30) LIMIT 50;

-- Result: approximately returns 3 rows (30% x 10 rows)
-- Note: on small datasets, SYSTEM mode may return all data or be imprecise
```

#### 2. Fixed-Row Sampling (SYSTEM Mode)

```sql
-- Randomly sample 5 rows of data
SELECT * FROM test TABLESAMPLE (5 ROWS) LIMIT 50;

-- Result: approximately returns 5 rows
-- Sample output:
-- | id | name |
-- |----|------|
-- |  1 | Lisa |
-- |  2 | Mary |
-- |  3 | Evan |
-- |  4 | Fred |
-- |  5 | Alex |
```

#### 3. Precise Row-Level Sampling (ROW Mode)

```sql
-- Precisely random sample 5 rows (ROW mode)
SELECT * FROM employee TABLESAMPLE ROW (5 ROWS) LIMIT 50;

-- Result: exactly returns 5 random rows
-- Sample output:
-- | id | name |
-- |----|------|
-- | 10 | Adam |
-- |  1 | Lisa |
-- |  8 | Lucy |
-- |  6 | Mark |
-- |  3 | Evan |
```

### Real-World Application Scenarios

#### Scenario 1: Quick Data Preview (SYSTEM Recommended)

```sql
-- Quickly view sample data from the orders table
SELECT
    order_id,
    customer_id,
    order_date,
    amount
FROM doc_test.orders
TABLESAMPLE SYSTEM (50)  -- 50% sampling (for small table demonstration)
LIMIT 100;

-- Applicable for: quickly understanding data structure and content
```

#### Scenario 2: Data Quality Check (SYSTEM Recommended)

```sql
-- Rapidly sample from the orders table to check for abnormal data
SELECT order_id, amount, status
FROM doc_test.orders
TABLESAMPLE SYSTEM (50)
WHERE amount < 0
LIMIT 50;

-- Applicable for: quickly discovering data quality issues
```

#### Scenario 3: Generating Machine Learning Training Sets (ROW Recommended)

```sql
-- Randomly sample training data from the user behavior table
SELECT
    user_id,
    behavior_type,
    item_id,
    timestamp
FROM user_behavior
TABLESAMPLE ROW (20)  -- Precise 20% random sampling
LIMIT 1000000;

-- Applicable for: ensuring randomness and representativeness of samples
```

#### Scenario 4: Statistical Analysis Sampling (ROW Recommended)

```sql
-- Estimate average order amount
SELECT
    AVG(total_amount) as avg_order_amount,
    COUNT(*) as sample_count
FROM large_orders_table
TABLESAMPLE ROW (5)  -- 5% precise sampling
LIMIT 1000000;

-- Applicable for: scenarios requiring statistically rigorous random sampling
```

#### Scenario 5: Development Environment Test Data

```sql
-- Generate small-scale test data
CREATE TABLE test_customers AS
SELECT *
FROM production_customers
TABLESAMPLE ROW (1000 ROWS)  -- Precisely 1000 rows
LIMIT 1000;

-- Applicable for: preparing data for development and testing environments
```

### Advanced Usage

#### Combining with WHERE Conditions

```sql
-- TABLESAMPLE must immediately follow the table name, and WHERE conditions come after
SELECT order_id, customer_id, amount, status
FROM doc_test.orders
TABLESAMPLE SYSTEM (50)
WHERE status = 'completed'
LIMIT 50;
```

#### Combining with Aggregate Analysis

```sql
-- Perform aggregate analysis on sampled data
SELECT
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as order_count,
    AVG(total_amount) as avg_amount
FROM large_orders
TABLESAMPLE SYSTEM (5)
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month
LIMIT 50;
```

#### Multi-Table Sampling with JOIN

```sql
-- Sample multiple large tables and then JOIN
SELECT
    o.order_id,
    c.customer_name,
    o.total_amount
FROM orders o
TABLESAMPLE SYSTEM (10)
JOIN customers c
TABLESAMPLE SYSTEM (10)
ON o.customer_id = c.customer_id
LIMIT 100;
```

***

## In-Depth Comparison of Sampling Strategies

### SYSTEM Mode Details

**How It Works**:

* Randomly selects at the file/data block level
* If a file is selected, all rows within that file are returned
* Does not read unselected files, resulting in extremely high performance

**Performance Characteristics**:

* ⚡ **Extremely fast**: Only reads partial files, low I/O overhead
* 📊 **Suitable for big data**: The larger the data volume, the more obvious the performance advantage
* 💾 **Memory friendly**: No need to cache all data

**Applicable Scenarios**:

* ✅ Large tables (millions of rows or more)
* ✅ Quick data exploration and preview
* ✅ Scenarios with low precision requirements
* ✅ Data quality checks

**Caveats**:

* ⚠️ Small datasets may produce imprecise results (may return all or no data)
* ⚠️ If data storage is skewed, sampling may be biased
* ⚠️ Result row count may differ significantly from expectations

### ROW Mode Details

**How It Works**:

* Evaluates each row independently for sampling (based on a pseudo-random algorithm)
* Each row has an independent probability of being selected
* Requires scanning all data rows

**Performance Characteristics**:

* 🐢 **Slower**: Needs to read and evaluate all rows
* 🎯 **Precise**: Result row count is close to expectations
* 💡 **Statistically rigorous**: Meets the statistical requirements for random sampling

**Applicable Scenarios**:

* ✅ Small to medium tables (under 1 million rows)
* ✅ Machine learning training set generation
* ✅ Statistical analysis and scientific computing
* ✅ Scenarios requiring precise randomness

**Caveats**:

* ⚠️ High performance overhead on large tables
* ⚠️ Still requires scanning the entire table
* ✅ Result row count is more predictable

### Performance Comparison

| Data Size | SYSTEM Mode | ROW Mode | Recommendation |
| --------- | --------- | ------- | -------------- |
| < 10K rows | ~10ms | ~15ms | ROW (precision matters more) |
| 10K-100K rows | ~50ms | ~200ms | ROW or SYSTEM |
| 100K-1M rows | ~100ms | ~2s | SYSTEM (noticeable performance difference) |
| > 1M rows | ~200ms | ~10s+ | SYSTEM (huge performance advantage) |

*Note: Actual performance depends on hardware, data distribution, and other factors*

***

## Best Practices

### 1. How to Choose a Sampling Mode

```
Data size < 1 million rows?
|-- Yes -> Need precise randomness?
|     |-- Yes -> Use ROW mode
|     |-- No -> Use SYSTEM mode (faster)
|-- No -> Use SYSTEM mode (performance first)
```

### 2. Performance Optimization Tips

#### ✅ Recommended Practices

```sql
-- 1. Always add a LIMIT clause
SELECT * FROM large_table
TABLESAMPLE (10)
LIMIT 1000;  -- ✅ Limit the final number of returned rows

-- 2. Prioritize SYSTEM on large tables
SELECT * FROM billion_rows_table
TABLESAMPLE SYSTEM (1)  -- ✅ 1% sampling is sufficient
LIMIT 10000;

-- 3. Sample first, then JOIN (reduce JOIN data volume)
SELECT a.*, b.*
FROM (
    SELECT * FROM large_table_a
    TABLESAMPLE (5)
    LIMIT 100000
) a
JOIN large_table_b b ON a.id = b.id
LIMIT 1000;
```

#### ❌ Practices to Avoid

```sql
-- 1. Using SYSTEM on small tables expecting precise results
SELECT * FROM small_table_10_rows
TABLESAMPLE SYSTEM (30);  -- ❌ May return 0 rows or 10 rows

-- 2. Using ROW on large tables without LIMIT
SELECT * FROM billion_rows_table
TABLESAMPLE ROW (10);  -- ❌ Extremely poor performance, may return 100 million rows

-- 3. Excessive sampling (close to 100%)
SELECT * FROM large_table
TABLESAMPLE (95);  -- ❌ Nearly a full table scan, defeats the purpose of sampling
```

### 3. Sampling Accuracy Recommendations

| Requirement | Recommended Sampling Ratio | Description |
| ------ | --------- | ------------- |
| Quick preview | 0.1% - 1% | Sufficient for understanding data structure |
| Data quality check | 5% - 10% | Balances performance and coverage |
| Statistical estimation | 10% - 20% | Ensures statistical significance |
| Machine learning training | 20% - 50% | Adjust based on data volume and model complexity |

### 4. Frequently Asked Questions

**Q1: What happens if the sampling ratio exceeds 100%?**

```sql
SELECT * FROM test TABLESAMPLE (150) LIMIT 50;
-- A: An error will be reported! Singdata requires the sampling ratio to be between 0 and 100.
-- Error message: tablesample percentage number should be greater than 0 and less than 100
```

**Q2: What happens if the sampled row count exceeds the total number of rows in the table?**

```sql
SELECT * FROM test TABLESAMPLE (100 ROWS) LIMIT 50;  -- Table only has 10 rows
-- A: The entire table data (10 rows) will be returned
```

**Q3: What does sampling from an empty table return?**

```sql
SELECT * FROM empty_table TABLESAMPLE (50) LIMIT 50;
-- A: Returns an empty result set without errors
```

**Q4: Is there a difference between sampling views and tables?**

```sql
-- Both are supported, but views may have slightly lower performance (need to be materialized first)
SELECT * FROM my_view TABLESAMPLE ROW (10) LIMIT 50;
```

**Q5: How to obtain repeatable sampling results?**

```sql
-- TABLESAMPLE does not support SEED. For repeatable sampling:
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY id) as rn
    FROM my_table
) WHERE rn % 10 = 0  -- Take 1 row out of every 10
LIMIT 50;
```

***

## Limitations and Notes

### Usage Restrictions

1. **Unsupported Scenarios**
   * ❌ Cannot be used in the WHERE clause of a subquery
   * ❌ Cannot be used in CTE (WITH clause) definitions
   * ❌ Cannot be used in materialized view definitions

2. **Syntax Limitations**
   * ⚠️ Must immediately follow the table name in the FROM clause
   * ⚠️ TABLESAMPLE must come before the WHERE clause
   * ⚠️ Cannot be used together with `FOR UPDATE`
   * ⚠️ The percentage sampling range must be between 0 and 100 (exclusive of 0 and 100)

3. **Performance Notes**
   * ⚠️ ROW mode can be very slow on extremely large tables (> 10 million rows)
   * ⚠️ Even with 1% sampling, ROW mode needs to scan the entire table

### Data Consistency

* 🔄 **Non-deterministic**: Each execution returns different results
* 📊 **Statistical bias**: SYSTEM mode may have bias when data distribution is uneven
* ⏱️ **Timeliness**: Sampling reflects the data snapshot at the time of query

### Best Practices Summary

| Scenario | Data Volume | Recommended Mode | Sampling Ratio | LIMIT |
| ----- | ------ | ------ | ------ | ---------- |
| Data preview | Any | SYSTEM | 1-5% | 100-1000 |
| Quality check | Any | SYSTEM | 5-10% | 1000-10000 |
| Statistical analysis | < 1M | ROW | 10-20% | As appropriate |
| Statistical analysis | > 1M | SYSTEM | 5-10% | As appropriate |
| ML training set | < 1M | ROW | 20-50% | As appropriate |
| ML training set | > 1M | SYSTEM | 10-30% | As appropriate |

***

## Related References

* **Data Exploration**: Combine with [DESCRIBE](desc-table.md) and [SHOW](show.md) commands to understand table structure
* **Performance Optimization**: Use with partitioned tables and `WHERE` conditions to improve sampling efficiency
* **Data Analysis**: Combine with [aggregate functions and window functions](window-function-summary.md)

^
