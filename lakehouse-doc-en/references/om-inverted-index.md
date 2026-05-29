# Inverted Index

Inverted Index is Lakehouse's **full-text search acceleration index**. It tokenizes text content in columns and builds a mapping from words to rows, enabling keyword matching and full-text search queries.

## Comparison with Bloomfilter Index

| Aspect | Inverted Index | Bloomfilter Index |
|--------|----------|-------------------|
| Applicable Queries | Full-text search, keyword matching (`MATCH`) | Equality filtering (`=`, `IN`) |
| Applicable Column Types | Text columns (VARCHAR, STRING) | Any type, high-cardinality columns |
| Typical Scenarios | Log search, product name search | Point lookup by ID |

## Applicable Scenarios

- Log analysis: search for keywords in the `message` column
- Product search: full-text search in product names and descriptions
- User behavior: match specific behaviors in event description fields

## Create Example

```sql
-- Create Inverted Index at table creation
CREATE TABLE logs (
    log_id  BIGINT,
    message STRING,
    INDEX idx_message (message) USING INVERTED
);

-- Query using Inverted Index
SELECT * FROM logs
WHERE MATCH(message, 'error timeout');
```

## Related Documents

- [Inverted Index Details](inverted-index.md)
- [Index Usage Best Practices](lakehouse-index-best-practice.md)
- [Bloomfilter Index](om-bloomfilter.md) — equality filtering scenarios
