# Table

A Table is the **basic unit for storing data** in the Lakehouse, using columnar storage (Parquet format) suitable for analytical queries.

Unlike Dynamic Tables and Materialized Views, a table's data must be maintained manually through INSERT, UPDATE, DELETE, or COPY INTO — the system will not auto-refresh the data.

## Type Selection Reference

| Table Type | Data Maintenance Method | Suitable Scenarios |
|--------|------------|---------|
| **Table** | Manual writes | ODS raw data, scenarios requiring precise control over write timing |
| Dynamic Table | Automatic incremental refresh | DWD/DWS layers, automatically compute results based on queries |
| Materialized View | Automatic refresh | Pre-computed query results, transparent query acceleration |
| View | No data storage | Logic encapsulation, simplified queries |

## Core Features

**Columnar Storage**: Uses Parquet format by default, reading only the necessary columns during queries, suitable for large-scale analysis.

**Primary Key Support**: After defining a primary key, the system automatically deduplicates by primary key during real-time writes, suitable for CDC sync scenarios.

**Time Travel**: Retains historical version data, supporting queries of data states at historical points in time.

**Partitioning and Clustering**: Optimizes query performance through partition pruning and clustered joins.

## Quick Example

```sql
-- Create a table
CREATE TABLE orders (
    order_id    BIGINT       PRIMARY KEY,
    user_id     BIGINT       NOT NULL,
    amount      DECIMAL(10,2),
    created_at  TIMESTAMP
)
PARTITION BY (DATE(created_at));

-- Insert data
INSERT INTO orders VALUES (1, 101, 99.00, NOW());
```

## Related Documentation

- [CREATE TABLE](create-table-ddl.md) — Table creation syntax
- [ALTER TABLE](alter-table.md) — Modify table structure
- [Partitioning](partition_table_guide.md) — Partition design guide
- [Clustering](cluster-table-guide.md) — Clustering design guide
- [Time Travel](timetravel-summary.md) — Historical data queries
