# Lakehouse Query Acceleration Index Guide

## Overview

In large-scale data query scenarios, full table scans can be time-consuming. Singdata Lakehouse provides multiple index types, including Bloom filters (for equality query acceleration), inverted indexes (for full-text search), and vector indexes (for similarity search). This guide is organized by business scenario to help you quickly master index creation, building, and management methods.

### Quick Navigation

* [Create Bloom Filter Index](#create-bloom-filter-index) -- Accelerate equality filtering on high-cardinality columns
* [Create Inverted Index](#create-inverted-index) -- Support full-text search on text fields
* [Build Index for Existing Data](#build-index-for-existing-data) -- Generate indexes for existing data
* [View and Drop Indexes](#view-and-drop-indexes) -- Manage index lifecycle
* [Index Effectiveness Verification](#index-effectiveness-verification) -- Confirm queries are using index acceleration

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE BLOOMFILTER INDEX` | Create Bloom filter index | Equality queries on high-cardinality columns (e.g., ID, phone number) |
| `CREATE INVERTED INDEX` | Create inverted index | Full-text search on text fields (e.g., logs, comments) |
| `BUILD INDEX` | Build index for existing data | Generate indexes for historical data |
| `SHOW INDEX` | View index list | Monitor index status |
| `DROP INDEX` | Drop index | Clean up unused indexes |

***

## Prerequisites

The following examples use a simulated log table `app_logs_idx`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS app_logs_idx (
    log_id BIGINT,
    user_id STRING,
    content STRING,
    log_time TIMESTAMP
);

-- Insert test data
INSERT INTO app_logs_idx VALUES
(1, 'U1001', 'User logged in successfully', '2024-06-01 10:00:00'),
(2, 'U1002', 'Failed to load dashboard', '2024-06-01 10:05:00'),
(3, 'U1001', 'Clicked on settings page', '2024-06-01 10:10:00');
```

***

## Create Bloom Filter Index

Bloom filters are suitable for equality filtering (`=`, `IN`) on high-cardinality columns, significantly reducing the amount of data scanned.

```sql
-- Create a Bloom filter index on the user_id column
CREATE BLOOMFILTER INDEX idx_user_id_bloom 
ON TABLE app_logs_idx(user_id);
```

> **Note**: Bloom filter indexes only take effect for data written after creation. Existing data requires `BUILD INDEX`.

***

## Create Inverted Index

Inverted indexes are suitable for full-text search on text fields, supporting Chinese word segmentation and multiple matching modes.

```sql
-- Create an inverted index on the content column
CREATE INVERTED INDEX idx_content_inverted 
ON TABLE app_logs_idx(content)
PROPERTIES('analyzer' = 'chinese');
```

**Analyzer Options**:
* `chinese`: Chinese word segmentation
* `english`: English word segmentation
* `keyword`: No segmentation, exact match

***

## Build Index for Existing Data

Newly created indexes do not automatically scan historical data. Use `BUILD INDEX` to generate indexes for existing data.

```sql
-- Build the inverted index (to take effect on existing data)
BUILD INDEX idx_content_inverted ON app_logs_idx;
```

> **Tip**: `BUILD INDEX` is a synchronous operation that consumes compute resources. It is recommended to execute during off-peak hours or build by partition in batches.

***

## View and Drop Indexes

Use `SHOW INDEX` to view all indexes on a table, and `DROP INDEX` to clean up indexes no longer needed.

```sql
-- View indexes on the table
SHOW INDEX IN app_logs_idx;

-- Drop an index
DROP INDEX idx_user_id_bloom;
```

***

## Index Effectiveness Verification

Once created, queries automatically leverage indexes for acceleration without modifying SQL syntax.

```sql
-- Equality query (automatically uses the Bloom filter)
SELECT * FROM app_logs_idx WHERE user_id = 'U1001';

-- Full-text search (automatically uses the inverted index)
SELECT * FROM app_logs_idx 
WHERE match_any(content, 'dashboard settings', map('analyzer', 'chinese'));
```

> **Tip**: Use `EXPLAIN` to view the execution plan and confirm whether the query hit the index.

***

## Clean Up Test Data

After completing index verification, it is recommended to clean up the test table:

```sql
-- Drop the test table (indexes are automatically dropped with the table)
DROP TABLE IF EXISTS app_logs_idx;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Bloom Filter Limitations**: Does not support `LIKE`, range queries (`>`, `<`), or complex types (ARRAY/MAP/STRUCT).
2. **Inverted Index Building**: `BUILD INDEX` is only effective for inverted indexes and vector indexes; Bloom filters do not support historical data building.
3. **Storage Overhead**: Indexes consume additional storage space, typically 5%-20% of the original table.
4. **Write Performance**: Indexes slightly increase `INSERT`/`UPDATE` latency because the index structure must be updated simultaneously.
5. **Automatic Application**: The query optimizer automatically determines whether to use an index; no explicit specification is needed in SQL.

***

## Related Documentation

* [Bloom Filter Index](bloomfilter-summary.md)
* [Inverted Index](inverted-index.md)
* [Vector Index](vector-search.md)
