# Bloomfilter Index

Bloomfilter Index is an **equality filter acceleration index** in Lakehouse. It records the presence of column values at the data file level, allowing the query engine to quickly skip files that do not contain the target value before scanning, reducing I/O.

## How It Works

Bloomfilter is a probabilistic data structure that quickly determines "whether a value may exist in a certain data block":
- **Not present**: 100% accurate, the data block is skipped directly
- **May be present**: needs actual read to verify (very low probability of false positives)

## Applicable Scenarios

| Scenario | Effect |
|------|------|
| Equality filtering on high-cardinality columns (e.g., `user_id = 12345`) | Significantly reduces the number of scanned files |
| Point queries (look up single record by ID) | Greatly improves query speed |
| Range queries (`BETWEEN`, `>`, `<`) | **Ineffective**, not suitable |
| Low-cardinality columns (e.g., gender, status) | Limited benefit, not recommended |

## Create Example

```sql
-- Create Bloomfilter Index at table creation
CREATE TABLE orders (
    order_id BIGINT,
    user_id  BIGINT,
    amount   DECIMAL(10,2),
    INDEX idx_user_id (user_id) USING BLOOMFILTER
);

-- Add to an existing table
ALTER TABLE orders ADD INDEX idx_order_id (order_id) USING BLOOMFILTER;
```

## Related Documents

- [Bloomfilter Index Details](bloomfilter-summary.md)
- [Index Usage Best Practices](lakehouse-index-best-practice.md)
- [Inverted Index](om-inverted-index.md) — full-text search scenarios
