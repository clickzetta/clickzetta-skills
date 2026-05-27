# Lakehouse Data Sampling Exploration Guide

## Overview

When working with large-scale datasets, full table scans are often time-consuming. Data sampling allows you to quickly obtain a representative subset of data for exploratory analysis, model training, or query debugging. Singdata Lakehouse provides multiple sampling methods, including random sampling, fixed-row sampling, and bucket sampling. This guide categorizes usage by business scenario to help you quickly master efficient data sampling methods.

### Quick Navigation

* [Fixed Row Sampling](#fixed-row-sampling) -- Use LIMIT to get the first N rows
* [Random Sampling](#random-sampling) -- Use ORDER BY RAND() to get random samples
* [Percentage Sampling](#percentage-sampling) -- Use TABLESAMPLE for proportional sampling
* [Bucket Sampling](#bucket-sampling) -- Use HASH function for evenly distributed sampling

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `LIMIT n` | Limit the number of returned rows | Quick view of table structure, first few rows |
| `ORDER BY RAND()` | Random ordering | Get random samples, suitable for small datasets |
| `TABLESAMPLE` | Table-level sampling | Fast sampling for large data volumes, best performance |
| `col % N = k` | Modulo bucketing | Uniform sampling, guarantees repeatability |

***

## Prerequisites

The following examples use a simulated large table `large_events` (approximately 1000 rows):

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS large_events (
    event_id INT,
    event_type STRING,
    user_id INT,
    amount DOUBLE,
    event_time TIMESTAMP
);

-- Insert 1000 rows of test data
INSERT INTO large_events
SELECT 
    seq,
    CASE seq % 3 WHEN 0 THEN 'click' WHEN 1 THEN 'view' ELSE 'purchase' END,
    seq % 100,
    ROUND(RAND() * 100, 2),
    TIMESTAMP '2024-06-01 00:00:00' + INTERVAL (seq % 1440) MINUTE
FROM (SELECT SEQUENCE(1, 1000) AS seqs) t, EXPLODE(t.seqs) AS seq;
```

***

## Fixed Row Sampling

Use `LIMIT` to quickly get the first N rows of data, suitable for viewing table structure and data distribution overview.

```sql
-- View the first 5 rows
SELECT * FROM large_events LIMIT 5;
```

**Result**:

| event_id | event_type | user_id | amount | event_time |
|----------|------------|---------|--------|------------|
| 1 | view | 1 | 34.56 | 2024-06-01 00:01:00 |
| 2 | purchase | 2 | 78.90 | 2024-06-01 00:02:00 |
| ... | ... | ... | ... | ... |

> **Note**: Without `ORDER BY`, the return order of `LIMIT` is not guaranteed to be stable and may vary with the query execution plan.

***

## Random Sampling

Use `ORDER BY RAND()` to obtain random samples. Suitable for unbiased sample requirements, but performance is poor with large data volumes.

```sql
-- Randomly get 10 rows
SELECT * FROM large_events
ORDER BY RAND()
LIMIT 10;
```

**Applicable Scenarios**:
* Datasets are small (under a million rows)
* Strict randomness is required
* Model training data partitioning

> **Tip**: For datasets over tens of millions of rows, `ORDER BY RAND()` triggers a full sort. Use `TABLESAMPLE` or hash bucketing instead.

***

## Percentage Sampling

Use `TABLESAMPLE` for fixed-ratio sampling with optimal performance, suitable for quick exploration of large data volumes.

```sql
-- Sample 10% of the data
SELECT * FROM large_events TABLESAMPLE(10);
```

**Result**:
* The actual number of returned rows is approximately 10% of the total (with slight variation).
* Sampling is based on underlying data blocks and is extremely fast with no full table scan required.

> **Note**: The `TABLESAMPLE` syntax in Lakehouse may vary slightly by version. If `PERCENT` is not supported, try `TABLESAMPLE(10 ROWS)` or hash bucketing.

***

## Bucket Sampling

Use modulo operation to divide data into buckets and take one bucket as a sample. Ensures uniformity and repeatability of sampling.

```sql
-- Split into 2 buckets by user_id, take bucket 0 (about 50% of data)
SELECT * FROM large_events
WHERE user_id % 2 = 0;
```

**Advantages**:
* **Repeatable**: The same conditions return the same sample each time, facilitating debugging and comparison.
* **Uniform**: Hash functions ensure even sample distribution.
* **Efficient**: No sorting required, filter directly.

***

## Clean Up Test Data

After completing sampling verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS large_events;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **LIMIT Order Instability**: `LIMIT` without `ORDER BY` does not guarantee return order; add sorting for stable results.
2. **RAND() Performance**: `ORDER BY RAND()` requires a full table scan and sort; avoid for large data volumes.
3. **TABLESAMPLE Precision**: Based on data block sampling, the returned row count may fluctuate by 5%-10%.
4. **Sampling and Partitions**: If a table is partitioned, sampling spans all partitions. To sample a single partition, add a `WHERE` filter on the partition column first.

***

## Related Documentation

* [TABLESAMPLE Sampling](tablesample.md)
* [SELECT Basic Syntax](query-syntax.md)
