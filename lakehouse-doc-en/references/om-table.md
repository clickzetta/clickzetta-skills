# Table

A Table is the basic unit for storing data in the Lakehouse. Unlike row-oriented databases such as MySQL, Lakehouse tables use **Parquet columnar storage** — data is organized and compressed by column. Queries only need to read the relevant columns, dramatically reducing I/O. Unlike Hive's static partitioning, Lakehouse uses a **hidden partitioning** mechanism similar to Iceberg, where the partitioning strategy can be changed without affecting the data.

> A table is like a "manually managed data container" — you are responsible for writing data, and the system handles efficient storage and querying. If you need to **incrementally compute** processed results from upstream data, use a [Dynamic Table](om-dynamic-table.md). If you only need **transparent acceleration** of existing queries, use a [Materialized View](materializedview.md).

## Core Features

**Columnar storage**: Uses Parquet format by default. Queries only read the columns they need, making it well-suited for large-scale analytics.

**Primary key support**: Once a primary key is defined, the system automatically deduplicates by primary key during real-time writes, which is ideal for CDC sync scenarios. The default behavior is `ENABLE VALIDATE RELY`, meaning SQL writes also enforce primary key checks.

**Time Travel**: Based on MVCC version management, historical versions of data are retained, allowing you to query the state of data at any past point in time.

**Partitioning and bucketing**: Supports hidden partitioning (similar to Iceberg) and hash bucketing (`CLUSTER BY`) to optimize query performance.

## When to Use a Table?

### Suitable Scenarios

| Scenario | Reason |
|---|---|
| ODS layer raw data ingestion | Requires precise control over write timing and preserving raw data |
| Dimension tables | Small data volume, infrequent updates, needs JOIN acceleration |
| CDC sync target table | Sync jobs write directly; pairs with Table Stream to consume changes |
| Temporary data staging | Fast writes, later consumed by Dynamic Tables or scheduled jobs |

### Unsuitable Scenarios

| Scenario | Recommended Alternative | Reason |
|---|---|---|
| Aggregation results that need automatic refresh | Dynamic Table | Tables require manual data maintenance |
| Frequently queried intermediate results | Materialized View | Materialized views provide transparent acceleration without changing SQL |
| Federated queries over external data | External Table | No need to migrate data into the Lakehouse |

## Quick Example

### Creating a Partitioned Table with a Primary Key

```sql
-- Create table
CREATE TABLE orders (
    order_id    BIGINT       PRIMARY KEY,
    user_id     BIGINT       NOT NULL,
    amount      DECIMAL(10,2),
    created_at  TIMESTAMP
)
PARTITIONED BY (days(created_at));

-- Insert data
INSERT INTO orders VALUES (1, 101, 99.00, '2024-01-15 10:30:00');
INSERT INTO orders VALUES (2, 102, 199.00, '2024-01-16 14:20:00');

-- Query
SELECT * FROM orders WHERE created_at >= '2024-01-15';
+----------+---------+--------+---------------------+
| order_id | user_id | amount | created_at          |
+----------+---------+--------+---------------------+
| 1        | 101     | 99.00  | 2024-01-15 10:30:00 |
| 2        | 102     | 199.00 | 2024-01-16 14:20:00 |
+----------+---------+--------+---------------------+
```

> ⚠️ **Note**: The default primary key behavior is `ENABLE VALIDATE RELY`, which means SQL writes also enforce primary key checks. If you want deduplication only for real-time writes but not for SQL writes, use `PRIMARY KEY DISABLE NOVALIDATE RELY`.

## Table Design Best Practices

### 1. Partition Design

**Principle**: Partition by the filter field most commonly used in queries — typically a time field. Use transform partitions (`days`/`months`/`years`) to reduce cardinality.

```sql
-- ✅ Good: partition by day, suitable for time-range queries
CREATE TABLE orders (
    order_id BIGINT,
    amount DECIMAL(10,2),
    created_at TIMESTAMP
) PARTITIONED BY (days(created_at));

-- ❌ Bad: partition by user_id, cardinality too high
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL(10,2)
) PARTITIONED BY (user_id);  -- millions of users = millions of partitions!
```

> ⚠️ **Note**: A single job can write to at most 2048 partitions. Exceeding this limit will produce the error `The count of dynamic partitions exceeds the maximum number 2048`. Aim for partition sizes in the hundreds of MB to GB range.

### 2. Bucket Design

**Principle**: Bucket by fields commonly used in JOINs or GROUP BYs to optimize shuffle operations.

```sql
-- Suitable for scenarios with frequent JOINs on user_id
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL(10,2)
) CLUSTERED BY (user_id) INTO 16 BUCKETS;
```

### 3. Primary Key Design

**Principle**: Define a primary key for CDC sync scenarios so the system automatically deduplicates by primary key.

```sql
-- CDC sync scenario: define a primary key to ensure idempotent writes
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name STRING,
    email STRING,
    updated_at TIMESTAMP
);
```

> ⚠️ **Note**: Primary key constraints in the Lakehouse are primarily used for CDC deduplication and SQL write checks. If you only need deduplication for real-time writes, use `PRIMARY KEY DISABLE NOVALIDATE RELY`.

## Common Issues

### Issue 1: Partition Field Cardinality Too High

**Problem**: Partitioning by a high-cardinality field (such as `user_id`) causes partition explosion.

**Symptom**: Write fails with `The count of dynamic partitions exceeds the maximum number 2048`.

**Solution**:
- Keep the number of distinct values in the partition field within a reasonable range
- Prefer time fields with transform partitions (`days`/`months`/`years`)
- Avoid partitioning by highly dispersed fields like user IDs or order IDs

### Issue 2: Time Travel Storage Cost

**Problem**: Long Time Travel retention is enabled on a frequently updated table, causing historical versions to consume large amounts of storage.

**Solution**:
- Keep the default 1-day retention for non-critical tables
- Set `PROPERTIES ('data_retention_days'='0')` on temporary tables to disable Time Travel
- Periodically check Time Travel usage: `DESC TABLE <table> EXTENDED`

### Issue 3: Primary Key Behavior Not as Expected

**Problem**: With the default primary key behavior, SQL writes also enforce primary key checks, causing bulk inserts to fail.

**Solution**:
- If you only need deduplication for real-time writes: `PRIMARY KEY DISABLE NOVALIDATE RELY`
- If you need strict uniqueness: keep the default `ENABLE VALIDATE RELY`

## Cost Implications

### Storage Cost

- Data is compressed and stored in Parquet format, typically achieving a 3–10x compression ratio
- Time Travel retains historical versions, increasing storage (retention days × average daily change volume)

### Compute Cost

- Writing data consumes VCluster CRU
- Query cost depends on the amount of data scanned (partitions/indexes can reduce scan volume)

> 💡 **Tip**: For detailed billing rules, refer to the [Billing Documentation](billing.md).

## Lifecycle Management

```
Create Table → Write Data → Query & Analyze → Optimize → Archive Data → Drop Table
     ↓              ↓              ↓             ↓              ↓              ↓
  Metadata     Time Travel     Result Cache    OPTIMIZE    Lifecycle Mgmt   UNDROP recoverable
               Retain History  Accelerate      Merge Files  Auto Cleanup    (within retention)
```

### Data Archiving and Cleanup

```sql
-- Set data lifecycle (automatically clean up expired data)
ALTER TABLE orders SET PROPERTIES ('data_lifecycle'='365');

-- View table history versions
DESC HISTORY orders;

-- Recover an accidentally dropped table (within Time Travel retention period)
UNDROP TABLE orders;
```

## Related Documentation

- [CREATE TABLE](create-table-ddl.md) — Table creation syntax
- [ALTER TABLE](alter-table.md) — Modifying table structure
- [Partitioning](partition_table_guide.md) — Partition design guide
- [Bucketing](cluster-table-guide.md) — Bucket design guide
- [Time Travel](timetravel-summary.md) — Querying historical data
- [OPTIMIZE](optimize.md) — Small file compaction
- [Data Lifecycle](data-lifecycle.md) — Automatically cleaning up expired data
