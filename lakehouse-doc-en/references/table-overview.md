# Data Tables

Singdata Lakehouse provides multiple table types to accommodate different data processing scenarios.

| Table Type | Description | Reference |
|--------|------|---------|
| Standard Table | Standard columnar storage table, supports DML and Time Travel | [Table](TABLE.md) |
| Dynamic Table | A query result table that refreshes incrementally, suitable for building data pipelines | [Dynamic Table](dynamic-table.md) |
| View | A virtual table that stores no data, providing logical encapsulation | [View](VIEW.md) |
| Materialized View | Pre-computes and stores query results, accelerating repeated queries | [Materialized View](MATERIALIZEDVIEW.md) |
| External Table | A table mapping to external data sources (Kafka, Delta Lake, Hudi) | [External Table](external-table-guide.md) |
| Table Stream | Change data capture stream that tracks INSERT/UPDATE/DELETE on a table | [Table Stream](table-stream-title.md) |
| Semantic View | A semantic layer for AI analytics, supporting natural language queries | [Semantic View](semantic-view-overview.md) |
