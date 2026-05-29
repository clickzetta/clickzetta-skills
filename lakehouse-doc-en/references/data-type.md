# Data Types

Lakehouse supports numeric, string, time, boolean, binary, and complex types (ARRAY, MAP, STRUCT, JSON, VECTOR, BITMAP).

## Type Quick Reference

### Numeric Types

| Type | Storage | Range / Precision | Typical Usage |
|------|---------|-------------------|--------------|
| `TINYINT` | 1 byte | -128 ~ 127 | Status codes, enum values |
| `SMALLINT` | 2 bytes | -32,768 ~ 32,767 | Small-range integers |
| `INT` | 4 bytes | -2,147,483,648 ~ 2,147,483,647 | General integer IDs |
| `BIGINT` | 8 bytes | -9.2×10¹⁸ ~ 9.2×10¹⁸ | Large integers, millisecond timestamps |
| `FLOAT` | 4 bytes | ~7 significant digits | Approximate floating point |
| `DOUBLE` | 8 bytes | ~15 significant digits | High-precision floating point |
| `DECIMAL(p, s)` | Variable | Max precision p=38, scale s | Monetary amounts, exact calculations, e.g. `DECIMAL(18, 4)` |

### String Types

| Type | Max Length | Description |
|------|-----------|-------------|
| `STRING` | 16 MB | No length limit; recommended as the default |
| `VARCHAR(n)` | n ≤ 1,048,576 characters | Has a length constraint; silently truncated on overflow |
| `CHAR(n)` | n ≤ 255 characters | Fixed length; no space padding |

### Time Types

| Type | Format | Description |
|------|--------|-------------|
| `DATE` | `YYYY-MM-DD` | Date only, no time |
| `TIMESTAMP` | `YYYY-MM-DD HH:MM:SS` | With local timezone (equivalent to `TIMESTAMP_LTZ`) |
| `TIMESTAMP_NTZ` | `YYYY-MM-DD HH:MM:SS` | No timezone information; stores the raw time value |

> ⚠️ **Note**: When migrating from PostgreSQL, note that PostgreSQL's `TIMESTAMP` (no timezone) corresponds to Lakehouse's `TIMESTAMP_NTZ`. See the [section below](#timestamp-has-timezone-by-default) for details.

### Boolean and Binary Types

| Type | Description |
|------|-------------|
| `BOOLEAN` | `true` / `false` |
| `BINARY` | Fixed-length binary string |

### Complex Types

| Type | Syntax Example | Description |
|------|---------------|-------------|
| `ARRAY` | `ARRAY<INT>`, `ARRAY<STRING>` | Ordered collection of same-type elements |
| `MAP` | `MAP<STRING, INT>` | Key-value pairs; key type must be consistent |
| `STRUCT` | `STRUCT<name:STRING, age:INT>` | Multi-field record; field types can differ |
| `JSON` | `JSON` | Stores any JSON structure; supports dynamic field access |
| `VECTOR` | `VECTOR(FLOAT, 1024)` | Fixed-dimension numeric vector; used for AI embedding storage |
| `BITMAP` | `BITMAP` | Bitmap for efficient cardinality counting (UV calculation, etc.) |

**Complex type example:**

```sql
CREATE TABLE example (
    tags        ARRAY<STRING>,
    attributes  MAP<STRING, STRING>,
    address     STRUCT<city:STRING, zip:STRING>,
    metadata    JSON,
    embedding   VECTOR(FLOAT, 1536),
    user_bitmap BITMAP
);
```

---

Lakehouse supports multiple type aliases, primarily for compatibility with DDL and SQL scripts migrated from other databases (MySQL, PostgreSQL, Hive, etc.), so they can run directly without manually replacing type names.

| Alias | Canonical Type |
|-------|---------------|
| `BYTE` | `TINYINT` |
| `SHORT` | `SMALLINT` |
| `INTEGER` | `INT` |
| `LONG` | `BIGINT` |
| `REAL` | `FLOAT` |
| `NUMERIC(p, s)` | `DECIMAL(p, s)` |
| `TEXT` | `STRING` |
| `TIMESTAMP` | `TIMESTAMP_LTZ` |

**When aliases are converted and their visibility**

Aliases are converted to canonical types immediately during SQL parsing; the system does not retain the original alias. Once converted, aliases and canonical types are indistinguishable everywhere:

- `DESCRIBE` shows the canonical type name
- `SHOW CREATE TABLE` outputs the canonical type name
- `typeof()` returns the canonical type name
- No system view or metadata records the original alias

This means: a column built with `REAL` shows `float` in `DESCRIBE`; a column built with `INTEGER` outputs `int` in `SHOW CREATE TABLE`. This is expected behavior — the type has not been changed.

> ⚠️ **Note**: When exporting DDL from Lakehouse and re-importing it, aliases are replaced with canonical names. The exported script will differ from the original creation script in type names. If you need to keep scripts consistent, use canonical type names when creating tables.

**Example: what the system actually shows after creating a table with aliases**

Running a DDL migrated from MySQL directly:

```SQL
CREATE TABLE orders (
    id       INTEGER,
    amount   NUMERIC(18, 4),
    status   TEXT,
    created  TIMESTAMP
);
```

`DESCRIBE` shows canonical type names, not the aliases used at creation:

```SQL
DESCRIBE orders;
```

```
+---------+------------------+
| column  | data_type        |
+---------+------------------+
| id      | int              |
| amount  | decimal(18,4)    |
| status  | string           |
| created | timestamp_ltz    |
+---------+------------------+
```

`SHOW CREATE TABLE` also outputs canonical names:

```SQL
SHOW CREATE TABLE orders;
-- CREATE TABLE orders (id int, amount decimal(18,4), status string, created timestamp_ltz) ...
```

The table behaves exactly the same as if it had been created with canonical type names — the types have not been modified.

## VARCHAR/CHAR and STRING Relationship

Lakehouse supports `VARCHAR(n)`, `CHAR(n)`, and `STRING` as three independent string types — they are not aliases of each other:

| Type | Characteristics | `typeof()` Returns |
|------|----------------|-------------------|
| `STRING` | No length limit, max 16 MB | `string` |
| `VARCHAR(n)` | Max n characters (n ≤ 1048576) | `varchar(n)` |
| `CHAR(n)` | Max n characters (n ≤ 255), no space padding | `char(n)` |

When migrating from MySQL, `VARCHAR(n)` and `CHAR(n)` DDL can be used directly. Key behavioral differences from MySQL:

- All three types **do not pad with spaces**: storing `'abc'` in `CHAR(10)` returns `3` for `LENGTH`.
- Strings exceeding the declared length are **silently truncated** — no error is raised.
- Comparisons are based on actual content; there is no trailing-space-ignore logic.

If you do not need to preserve length constraints during migration, you can replace `VARCHAR(n)` with `STRING` uniformly to reduce truncation risk.

## TIMESTAMP Has Timezone by Default

Lakehouse's `TIMESTAMP` is equivalent to `TIMESTAMP_LTZ` (local timezone). This is similar to MySQL's `TIMESTAMP` behavior, but differs from PostgreSQL's `TIMESTAMP` (no timezone).

When migrating from PostgreSQL, note:

| Source | Corresponding Lakehouse Type |
|--------|------------------------------|
| PostgreSQL `TIMESTAMP` (no timezone) | `TIMESTAMP_NTZ` |
| PostgreSQL `TIMESTAMPTZ` | `TIMESTAMP` (i.e., `TIMESTAMP_LTZ`) |
| MySQL `TIMESTAMP` | `TIMESTAMP` (i.e., `TIMESTAMP_LTZ`) |
| MySQL `DATETIME` | `TIMESTAMP_NTZ` |

Migrating PostgreSQL `TIMESTAMP` DDL directly to Lakehouse will result in columns becoming timezone-aware `TIMESTAMP_LTZ`. Write and read results will be affected by the session timezone, which is inconsistent with the original database behavior.

## Lenient Mode: Type Errors Return NULL by Default

Lakehouse runs in lenient mode by default. Type conversion failures, numeric overflows, and similar errors **do not throw exceptions — they return NULL**. This differs from the default behavior of most databases:

| Scenario | Most Databases | Lakehouse Default |
|----------|---------------|-------------------|
| `CAST('abc' AS INT)` | Error | `NULL` |
| `CAST(200 AS TINYINT)` (overflow) | Error | `NULL` |
| `CAST('2023-02-29' AS DATE)` (invalid date) | Error | `NULL` |
| Mixed-type conversion failure in UNION ALL | Error | `NULL` |

The benefit of lenient mode is that ETL pipelines are not interrupted by a single bad row; the trade-off is that errors are silently swallowed, making data quality issues harder to detect.

You can adjust this behavior:

```SQL
-- Enable strict mode: conversion failures raise an error immediately
SET cz.sql.cast.mode = strict;

-- Or use TRY_CAST: returns NULL on failure (same as lenient mode, but intent is explicit)
SELECT TRY_CAST('abc' AS INT);
```

When migrating from another database, if the original SQL relied on type errors to surface data issues, add explicit NULL checks at key ETL nodes after migrating to Lakehouse, or enable strict mode.


## Related Documentation

**Type Reference**

| Document | Description |
|----------|-------------|
| [Data Type Conversion](datatype-conversion.md) | Implicit and explicit conversion rules between types |
| [Type Conversion Functions](datatype-cast.md) | CAST, TRY_CAST, and type conversion function reference |
| [TIMESTAMP_NTZ](data-types-timestamp-ntz.md) | Detailed explanation and use cases for timezone-free timestamps |
| [VECTOR Type](vector-type.md) | Vector type syntax, dimension configuration, and usage examples |
| [BITMAP Type](bitmap-type.md) | Bitmap type use cases and function reference |
| [Data Type Conversion Guide](SQL_Type_Conversion_Guide.md) | Type mapping when migrating from MySQL / PostgreSQL / Hive |
| [CREATE TABLE](create-table-ddl.md) | Full syntax for using data types when creating tables |

**Organizing Data Efficiently**

| Document | Description |
|----------|-------------|
| [Partitioning and Bucketing](partition_table_guide.md) | Partition by time or business fields to improve query pruning efficiency |
| [Bucketing (CLUSTERED BY)](cluster-table-guide.md) | Hash-bucket by field to improve JOIN and aggregation performance |
| [Primary Keys](primary-key.md) | Primary key table design; supports CDC real-time write deduplication |
| [Recommended Sort Columns](auto-index.md) | Accelerate range queries and filters via sort columns |
| [Bloom Filter Index](bloomfilter-summary.md) | Accelerate equality queries by skipping data files that don't contain the target value |
| [Inverted Index](inverted-index.md) | Accelerate full-text search; supports Chinese and English tokenization |
| [Vector Index](vector-search.md) | ANN approximate nearest neighbor search; suited for semantic search and RAG |
| [Table Design Best Practices](lakehouse_table_design_guide.md) | Comprehensive selection guidance for partitioning, bucketing, and indexing |
