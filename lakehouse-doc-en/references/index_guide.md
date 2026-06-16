# Indexes

Index commands are used to create, build, inspect, and drop indexes on Lakehouse tables to accelerate specific query patterns.

---

## Index Types

Lakehouse provides three index types — choose based on your query pattern:

| Index Type | Applicable Queries | Typical Use Case |
|---|---|---|
| **Bloom Filter Index** | Equality filters on high-cardinality columns (`=`, `IN`) | Queries by user ID, order number, phone number |
| **Inverted Index** | Full-text search on text fields, supports Chinese tokenization | Log search, comment retrieval, keyword matching |
| **Vector Index** | Vector similarity search (ANN) | Semantic search, image similarity, recommendation systems |

> ⚠️ **Note**: A newly created index only applies to data written after the index is created. For existing data, run `BUILD INDEX` to backfill.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [Bloom Filter Index](bloomfilter-summary.md) | Bloom filter principles, creation, and usage |
| [CREATE BLOOMFILTER INDEX](create-bloomfilter-index.md) | Full syntax for creating a bloom filter index |
| [Inverted Index](inverted-index.md) | Inverted index principles, analyzer configuration, and usage |
| [CREATE INVERTED INDEX](create-inverted-index.md) | Full syntax for creating an inverted index |
| [Vector Index](vector-search.md) | Vector search principles, index types, and usage |
| [CREATE VECTOR INDEX](create-vector-index.md) | Full syntax for creating a vector index |
| [BUILD INDEX](build-index.md) | Build an index for existing data |
| [DESC INDEX](desc-index.md) | View index details |
| [DROP INDEX](drop-index.md) | Drop an index |
| [SHOW INDEX](show-index.md) | List all indexes on a table |

---

## Common Operations

### Create a Bloom Filter Index

```SQL
-- Create a bloom filter on a high-cardinality column to accelerate equality queries
CREATE BLOOMFILTER INDEX idx_user_id ON TABLE orders(user_id);
```

### Create an Inverted Index

```SQL
-- Create an inverted index on a text column to support full-text search
CREATE INVERTED INDEX idx_content ON TABLE app_logs(content)
PROPERTIES('analyzer' = 'chinese');
```

### Build an Index for Existing Data

```SQL
-- A new index does not cover historical data; trigger a build manually
BUILD INDEX idx_content ON app_logs;
```

### View and Drop Indexes

```SQL
-- List all indexes on a table
SHOW INDEX IN orders;

-- Drop an index
DROP INDEX idx_user_id;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [Index Usage Guide](sql_index_guide.md) | Complete examples for creating and validating indexes by scenario |
| [Full-Text Search Guide](fulltext_indexes_guide.md) | Detailed usage of inverted index full-text search |
| [Lakehouse Index Best Practices](lakehouse-index-best-practice.md) | Index selection, maintenance, and performance tuning recommendations |
