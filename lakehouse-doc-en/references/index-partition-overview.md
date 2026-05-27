# Indexes and Partitions

Singdata Lakehouse provides a variety of index and partition mechanisms to accelerate queries and optimize storage layout.

## Indexes

| Type | Applicable Scenario | Reference |
|------|---------|---------|
| Bloomfilter Index | Equality filtering, quickly skip non-matching data blocks | [Bloomfilter Index](bloomfilter-summary.md) |
| Inverted Index | Full-text search, keyword matching | [Inverted Index](inverted-index.md) |
| Vector Index | Vector similarity search (ANN) | [Vector Index](vector-search.md) |

## Partitions and Bucketing

| Type | Applicable Scenario | Reference |
|------|---------|---------|
| Partition | Prune data by time or business dimension | [Partition](partition_table_guide.md) |
| Bucketing | Distribute data evenly, optimize Join performance | [Bucketing](cluster-table-guide.md) |

For best practices, see [Index Usage Best Practices](lakehouse-index-best-practice.md).
