# Data Tables

Data tables are the core objects for storing and processing data in Singdata Lakehouse. Standard tables and Dynamic Tables use **Parquet columnar storage** — at query time only the required columns are read, making them well-suited for large-scale analytical queries. Unlike row-oriented databases such as MySQL, data is automatically organized by column and compressed on write, dramatically reducing I/O. Unlike Hive's static partitions, Lakehouse uses a **hidden partition** mechanism similar to Apache Iceberg, allowing partition strategies to be modified without affecting existing data.

## Choosing a Table Type

| Table type | How data is maintained | Typical use cases |
|------------|------------------------|-------------------|
| **Standard Table** | Manual INSERT/UPDATE/DELETE | ODS raw data, dimension tables, CDC sync targets |
| **Dynamic Table** | Automatic incremental refresh | DWD/DWS/ADS layers, query-driven automatic computation |
| **View** | No data stored, computed dynamically at query time | Logic encapsulation, simplifying complex queries |
| **Materialized View** | Automatically refreshed, pre-computed results stored | Transparent query acceleration, single-table query optimization |
| **External Table** | Data in external systems, Lakehouse manages metadata | Federated queries, data lake access |
| **Semantic View** | Encapsulates business semantics, supports natural language queries | AI conversational analytics, unified business metric definitions |

### Which table type should you use?

**Step 1: Where does the data come from?**

- Synced from an external source (MySQL/PostgreSQL/Kafka) → sync job writes to a **Standard Table**
- File import (CSV/Parquet/JSON) → COPY INTO writes to a **Standard Table**
- SQL query results → **Dynamic Table** (auto-refresh) or **View** (no storage)

**Step 2: How will the data be used?**

| Scenario | Recommendation | Reason |
|----------|----------------|--------|
| ODS raw data layer | Standard Table | Precise control over write timing |
| DWD cleansed data layer | Dynamic Table | Automatically computes incrementally from ODS, no scheduling needed |
| DWS metrics summary layer | Dynamic Table | Automatically aggregates from DWD |
| Frequently queried intermediate results | Materialized View | Transparent acceleration, users don't need to change SQL |
| Simplifying complex queries | View | No data stored, zero cost |
| AI conversational analytics | Semantic View | Encapsulates business semantics |
| Federated queries on external data | External Table | Data stays outside Lakehouse |

## Storage Format

Lakehouse tables use **Parquet** columnar storage by default:

- **Efficient compression**: Consecutive storage of same-type data yields high compression ratios.
- **Query optimization**: Only the columns needed by a query are read, reducing I/O.
- **Schema evolution**: Supports adding columns, modifying column types, and other schema changes.

## Partitions and Bucketing

- **Partitions**: Similar to Iceberg hidden partitions, supporting transform partitions (years/months/days/hours). Partition strategies can be modified without affecting existing data.
- **Bucketing**: `CLUSTER BY` uses hash bucketing to optimize JOIN and aggregation operations.

## Cost Impact at a Glance

| Operation | Storage impact | Compute impact |
|-----------|----------------|----------------|
| Create table | Metadata only, near-zero cost | None |
| Write data | Billed by Parquet-compressed data size | Consumes VCluster CRU |
| Enable Time Travel | Retains historical versions, increases storage | None |
| Create partition | No additional storage | Reduces scan volume at query time |
| Create index | Index data occupies additional storage | Accelerates queries, reduces CRU |

## Related Documentation

- [Table](om-table.md) — Standard columnar storage table
- [Dynamic Table](om-dynamic-table.md) — Query result table with automatic incremental refresh
- [View](om-view.md) — Virtual table
- [Materialized View](materializedview.md) — Pre-computed query results
- [External Table](external-table-guide.md) — Maps external data sources
- [Semantic View](om-semantic-view.md) — AI semantic layer
