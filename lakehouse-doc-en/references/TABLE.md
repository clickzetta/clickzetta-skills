# Table

Table DDL commands are used to create, modify, query, and delete regular tables in a workspace.

---

## Table Types

Singdata Lakehouse provides multiple table types. Use the following comparison when choosing:

| Table Type | Description | Use Case |
|---|---|---|
| **Regular Table (Table)** | Structured two-dimensional data, manually INSERT/UPDATE/DELETE | Raw data storage, ODS layer |
| **Dynamic Table** | Data objects that auto-incrementally refresh based on query definitions | DWD/DWS/ADS layers, metric aggregation |
| **Materialized View** | Special views that pre-compute and store query results | Pre-computed query results, query rewriting |
| **View** | Virtual table, no data stored, dynamically computed at query time | Simplifying complex queries, logical abstraction |
| **External Table** | Data stored in external systems; Lakehouse manages only metadata | Federated queries, data lake access |

## Storage Format

Regular tables use **Parquet** columnar storage by default, with the following advantages:

- **Columnar storage**: reads only the columns involved in the query, reducing I/O
- **Efficient compression**: saves 50%–80% storage space compared to row-based storage
- **Vectorized execution**: combined with the Lakehouse execution engine, aggregation and filter performance is better

## Table Constraints

### NOT NULL

Add `NOT NULL` to a column definition; the system validates that the column cannot be empty on write.

```SQL
CREATE TABLE orders (
  order_id BIGINT NOT NULL,
  amount   DECIMAL(10, 2) NOT NULL,
  note     STRING  -- nullable
);
```

### PRIMARY KEY

The primary key constraint has two behavior modes; understand the differences when choosing:

| Mode | Syntax | Deduplication Scope | Use Case |
|---|---|---|---|
| `ENABLE VALIDATE RELY` (default) | `PRIMARY KEY (col)` | Both SQL writes and real-time writes deduplicate | General scenarios |
| `DISABLE NOVALIDATE RELY` | `PRIMARY KEY (col) DISABLE NOVALIDATE RELY` | Only real-time writes deduplicate; SQL writes are not checked | Tables written only via CDC real-time sync |

```SQL
-- Default mode: both SQL writes and real-time writes perform primary key deduplication
CREATE TABLE customers (
  customer_id BIGINT PRIMARY KEY,
  name        STRING,
  updated_at  TIMESTAMP
);

-- DISABLE NOVALIDATE RELY: only real-time writes deduplicate; SQL writes do not check primary key uniqueness
-- Suitable for tables written only via CDC real-time sync, not via INSERT SQL
CREATE TABLE customers_cdc (
  customer_id BIGINT,
  name        STRING,
  updated_at  TIMESTAMP,
  PRIMARY KEY (customer_id) DISABLE NOVALIDATE RELY
);
```

> ⚠️ **Note**: When using `DISABLE NOVALIDATE RELY`, inserting duplicate primary keys via INSERT SQL will not raise an error and will not auto-deduplicate. Only real-time sync (CDC) writes trigger deduplication logic.

---

## This Chapter

| Page | Description |
|------|-------------|
| [CREATE TABLE](create-table-ddl.md) | Create a regular table with options for partitioning, bucketing, primary keys, and identity columns |
| [Partition](partition_table.md) | Partition by time or other fields to accelerate partition pruning |
| [Bucket](cluster-table.md) | Hash-bucket by column values to optimize JOIN and aggregation |
| [Primary Key](primary-key.md) | Define primary key constraints for CDC real-time deduplication writes |
| [Identity Column](identity-column.md) | Columns that auto-generate unique incrementing integer values |
| [Generated Column](generated-column.md) | Columns automatically computed from expressions on other columns |
| [Default Value](default-value.md) | Default value definition when a column value is not specified on insert |
| [CREATE...CLONE](clone-doc.md) | Quickly clone table structure (and optionally data) into a new table |
| [ALTER TABLE](alter-table.md) | Modify table properties such as renaming, adding/modifying columns, and setting lifecycle |
| [ALTER TABLE COLUMN](alter-table-column.md) | Add, rename, modify column types, or drop columns |
| [DROP TABLE](drop-table.md) | Delete a table and its data |
| [RESTORE TABLE](restore.md) | Roll back a table to a historical version |
| [UNDROP TABLE](undrop-table.md) | Recover a deleted table (within the data retention period) |
| [DESC TABLE](desc-table.md) | View a table's column definitions, types, and constraints |
| [DESC HISTORY TABLE](desc-history-table.md) | View a table's list of historical versions |
| [SHOW TABLES](show-tables.md) | List all tables under the current schema |
| [SHOW COLUMNS](show-columns.md) | List all column information for a table |
| [SHOW CREATE TABLE](show-create-table.md) | View the table creation statement |
| [SHOW PARTITIONS](list-partition.md) | List all partitions of a partitioned table |
| [SHOW TABLES HISTORY](show-tables-history.md) | List deleted tables (available for UNDROP) |
| [ANALYZE TABLE](analyze-table.md) | Collect table statistics to help the optimizer generate better execution plans |
| [OPTIMIZE](optimize.md) | Merge small files to improve query performance |

---

## Common Operations

### Create Table

```SQL
-- Basic table creation
CREATE TABLE IF NOT EXISTS public.orders (
  order_id   BIGINT,
  customer_id BIGINT,
  amount     DECIMAL(10, 2),
  status     STRING,
  created_at TIMESTAMP
);

-- With partitioning (partition by day, recommended for time-series data)
CREATE TABLE IF NOT EXISTS public.events (
  event_id   BIGINT,
  event_type STRING,
  user_id    BIGINT,
  created_at TIMESTAMP
) PARTITIONED BY (days(created_at));

-- With primary key (CDC real-time write scenario)
CREATE TABLE IF NOT EXISTS public.customers (
  customer_id BIGINT PRIMARY KEY,
  name        STRING,
  email       STRING,
  updated_at  TIMESTAMP
);
```

### Modify Table

```SQL
-- Add column
ALTER TABLE public.orders ADD COLUMN discount DECIMAL(5, 2);

-- Rename table
ALTER TABLE public.orders RENAME TO public.orders_v2;

-- Set data retention period (days)
ALTER TABLE public.orders SET data_retention_days = 7;
```

### View Table

```SQL
-- View table structure
DESC TABLE public.orders;

-- View table creation statement
SHOW CREATE TABLE public.orders;

-- List all tables
SHOW TABLES;

-- View partition list
SHOW PARTITIONS public.events;
```

### Delete and Restore

```SQL
-- Delete table
DROP TABLE IF EXISTS public.temp_orders;

-- Restore deleted table
UNDROP TABLE public.temp_orders;

-- Roll back table to historical version
RESTORE TABLE public.orders TO TIMESTAMP AS OF '2024-01-15 00:00:00';
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [Regular Table (Object Model)](om-table.md) | Table storage format, type selection, and best practices |
| [COPY INTO (Import)](copy-into-table.md) | Batch import data from Volume or external storage |
| [Time Travel Guide](time_travel_guide.md) | Historical data queries and table rollback operations |
