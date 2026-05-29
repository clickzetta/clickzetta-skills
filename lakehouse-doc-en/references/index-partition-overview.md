# Indexes and Partitions

Indexes are the mechanism Lakehouse uses to **reduce data scan volume and improve query performance**. They record additional metadata inside data files so the query engine can quickly filter at the file level, without changing the physical storage layout of the data.

> Partitions and bucketing are the physical organization methods for data and complement indexes. See [Partitions and Bucketing](partition_table_guide.md).

## Selection Guide

### Index Type Comparison

| Index type | Applicable queries | Applicable column types | Typical scenarios |
|------------|-------------------|------------------------|-------------------|
| **Bloomfilter Index** | Equality filters (`=`, `IN`) | High-cardinality columns (user IDs, order numbers, device IDs) | Point lookups by ID, skipping data files that don't contain the target value |
| **Inverted Index** | Full-text search (`MATCH`), keyword matching | Text columns (STRING, VARCHAR) | Log search, product name lookup, JSON field filtering |
| **Vector Index** | Approximate nearest neighbor search (ANN) | VECTOR type columns | Semantic search, image similarity, RAG retrieval |

**Selection rules:**
- ID fields, status codes, frequent equality queries → **Bloomfilter Index**
- Text content requiring keyword or phrase search → **Inverted Index**
- Vector embeddings requiring semantic similarity retrieval → **Vector Index**
- All three types can coexist on the same table without conflict.

> ⚠️ **Note**: Indexes are not a universal solution. Bloomfilter indexes are ineffective for range queries (`>`, `BETWEEN`); inverted indexes are only triggered by the `MATCH` function — ordinary `LIKE` does not use the inverted index; vector indexes require the corresponding ANN function at query time.

## Core Mechanisms

### Hidden Partitions

Lakehouse partitions work similarly to Apache Iceberg's **hidden partition** mechanism:
- Partition information is stored in metadata; you do not need to manually specify partition conditions in SQL queries.
- Supports transform partition functions (`years`/`months`/`days`/`hours`/`bucket`/`truncate`) for automatic time-based partitioning.
- Partition strategies can be modified without affecting existing data (Hive's static partitions do not support this).

> ⚠️ **Note**: Lakehouse's transform partition functions use plural forms (`years`/`months`/`days`/`hours`), which differ from common date function names — be careful not to confuse them.

### How Bloomfilter Works

A Bloomfilter is a probabilistic data structure that records the presence of column values at the data file level:
- A value is **definitely absent**: 100% accurate — the file is skipped entirely.
- A value **may be present**: the file must be read to verify (false positives are extremely rare).

Because of this, Bloomfilter indexes are only effective for equality queries; range queries cannot benefit from them.

## Quick Example

```sql
-- Create a table with partitions and multiple indexes at the same time
CREATE TABLE events (
    event_id   BIGINT,
    user_id    BIGINT,
    message    STRING,
    event_time TIMESTAMP,
    INDEX idx_user (user_id) USING BLOOMFILTER,
    INDEX idx_msg  (message) USING INVERTED
)
PARTITIONED BY (days(event_time));

-- Insert data (partitions are created automatically, no manual specification needed)
INSERT INTO events VALUES
    (1, 1001, 'user login failed', TIMESTAMP '2024-06-01 10:00:00'),
    (2, 1002, 'connection timeout', TIMESTAMP '2024-06-01 11:00:00'),
    (3, 1001, 'user login success', TIMESTAMP '2024-06-02 09:00:00');

-- Uses partition pruning: only scans data files for 2024-06-01
SELECT * FROM events WHERE event_time >= '2024-06-01' AND event_time < '2024-06-02';

-- Uses Bloomfilter index: skips files that don't contain user_id=1001
SELECT * FROM events WHERE user_id = 1001;

-- Uses inverted index: full-text search on the message column
SELECT * FROM events WHERE match_any(message, 'login');
```

## Common Issues

### Issue 1: Creating a Bloomfilter index on a low-cardinality column

**Problem**: Creating a Bloomfilter index on columns like gender, status, or enum values.

**Symptom**: Almost no improvement in query performance, but the index data consumes additional storage.

**Solution**: Bloomfilter indexes are only effective on high-cardinality columns (such as user IDs and order numbers). For low-cardinality columns, consider partitioning (e.g., partition by status) or simply rely on a full table scan.

### Issue 2: Existing large tables need BUILD after adding an index

**Problem**: After using `ALTER TABLE ... ADD INDEX` to add an index to a table with existing data, the old data has no index coverage.

**Solution**: After adding the index, run `BUILD INDEX` to build the index for historical data:

```sql
ALTER TABLE events ADD INDEX idx_new (user_id) USING BLOOMFILTER;
-- Must explicitly build; otherwise old data won't use the index
BUILD INDEX idx_new ON TABLE events;
```

> ⚠️ `BUILD INDEX` is a time-consuming operation. Building an index on a large table consumes significant VCluster CRU during the process. It is recommended to run this during off-peak hours.

### Issue 3: Partition granularity too fine causes too many small files

**Problem**: Data volume is not large, but the table is partitioned by hour (`hours(event_time)`).

**Symptom**: Metadata overhead for queries is high; `SHOW PARTITIONS` returns a large number of partitions, which actually slows down queries.

**Solution**: Match partition granularity to data volume — use `days` for GB-scale daily data, and consider `hours` for TB-scale data. Each partition should ideally contain at least 128 MB of data.

## Cost Impact

### Storage Cost

- Index data is stored in separate files and occupies additional storage space.
- Bloomfilter indexes are small (probabilistic structure, typically less than 1% of the original data).
- Inverted indexes are larger (a dictionary is built after tokenization, typically 20%–100% of the original column data).
- Vector indexes are the largest (HNSW graph structure, typically comparable in size to the original vector data).

### Compute Cost

- `BUILD INDEX` consumes VCluster CRU (one-time cost).
- Once the index is built, queries scan less data, reducing CRU consumption.
- Partitions incur no additional compute cost; they reduce I/O through metadata-based pruning.

## In This Section

| Page | Description |
|------|-------------|
| [Index Overview](index-overview.md) | Comparison of three index types and selection recommendations |
| [Bloomfilter Index](om-bloomfilter.md) | Equality filter acceleration, quickly skip files for high-cardinality columns |
| [Inverted Index](om-inverted-index.md) | Full-text search acceleration, MATCH queries |
| [Index Best Practices](lakehouse-index-best-practice.md) | Multi-index combinations, AI scenarios, operational recommendations |

## Related Documentation

| Document | Description |
|----------|-------------|
| [Table Design](om-table.md) | Partitions and indexes are core design decisions when creating a table |
| [BUILD INDEX](build-index.md) | Build indexes on historical data |
| [DROP INDEX](drop-index.md) | Delete an index |
| [SHOW INDEX](show-index.md) | View indexes on a table |
