# Data Type Compatibility Reference

When migrating DDL and SQL from existing databases to Lakehouse, this document lists common compatibility differences to help you avoid issues in advance.

## Data Type Mapping

Lakehouse supports multiple type aliases, so DDL from other databases can be used directly without manually replacing type names. Aliases are immediately converted to Lakehouse canonical types during parsing; `DESCRIBE` and `SHOW CREATE TABLE` display canonical names, not the original aliases.

### MySQL

| MySQL type | Lakehouse type | Notes |
|-----------|---------------|------|
| `TINYINT` | `TINYINT` | Directly supported |
| `SMALLINT` | `SMALLINT` | Directly supported |
| `INT` / `INTEGER` | `INT` | Directly supported; `INTEGER` is an alias |
| `BIGINT` | `BIGINT` | Directly supported |
| `FLOAT` | `FLOAT` | Directly supported |
| `DOUBLE` | `DOUBLE` | Directly supported |
| `DECIMAL(p,s)` / `NUMERIC(p,s)` | `DECIMAL(p,s)` | Directly supported; `NUMERIC` is an alias |
| `VARCHAR(n)` | `VARCHAR(n)` | Directly supported; max length 1048576 |
| `CHAR(n)` | `CHAR(n)` | Directly supported; max length 255 |
| `TEXT` | `STRING` | Directly supported; `TEXT` is an alias |
| `DATE` | `DATE` | Directly supported |
| `DATETIME` | `TIMESTAMP_NTZ` | MySQL DATETIME has no timezone; maps to TIMESTAMP_NTZ |
| `TIMESTAMP` | `TIMESTAMP` (i.e. `TIMESTAMP_LTZ`) | Both are timezone-aware timestamps |
| `BOOLEAN` / `BOOL` | `BOOLEAN` | Directly supported; `BOOL` alias not supported, change to `BOOLEAN` |

> ⚠️ MySQL's `DATETIME` should map to `TIMESTAMP_NTZ`, not `TIMESTAMP`. Using `TIMESTAMP` incorrectly will cause writes and reads to be affected by session timezone, inconsistent with MySQL behavior.

### PostgreSQL

| PostgreSQL type | Lakehouse type | Notes |
|----------------|---------------|------|
| `SMALLINT` / `INT2` | `SMALLINT` | `INT2` alias not supported; change to `SMALLINT` or `SHORT` |
| `INTEGER` / `INT4` | `INT` | `INT4` alias not supported; change to `INT` or `INTEGER` |
| `BIGINT` / `INT8` | `BIGINT` | `INT8` alias not supported; change to `BIGINT` or `LONG` |
| `REAL` / `FLOAT4` | `FLOAT` | `REAL` supported; `FLOAT4` not supported, change to `FLOAT` |
| `DOUBLE PRECISION` / `FLOAT8` | `DOUBLE` | `FLOAT8` not supported; change to `DOUBLE` |
| `NUMERIC(p,s)` / `DECIMAL(p,s)` | `DECIMAL(p,s)` | Directly supported |
| `VARCHAR(n)` | `VARCHAR(n)` | Directly supported |
| `CHAR(n)` | `CHAR(n)` | Directly supported |
| `TEXT` | `STRING` | Directly supported; `TEXT` is an alias |
| `DATE` | `DATE` | Directly supported |
| `TIMESTAMP` (no timezone) | `TIMESTAMP_NTZ` | PostgreSQL default TIMESTAMP has no timezone |
| `TIMESTAMPTZ` | `TIMESTAMP` (i.e. `TIMESTAMP_LTZ`) | Timezone-aware timestamp |
| `BOOLEAN` | `BOOLEAN` | Directly supported |
| `BYTEA` | `BINARY` | Binary type; must be manually replaced |

> ⚠️ PostgreSQL's `TIMESTAMP` (no timezone) should map to `TIMESTAMP_NTZ`. Migrating directly to Lakehouse's `TIMESTAMP` changes it to a timezone-aware type with different behavior.

### Hive

| Hive type | Lakehouse type | Notes |
|----------|---------------|------|
| `TINYINT` | `TINYINT` | Directly supported |
| `SMALLINT` | `SMALLINT` | Directly supported |
| `INT` | `INT` | Directly supported |
| `BIGINT` | `BIGINT` | Directly supported |
| `FLOAT` | `FLOAT` | Directly supported |
| `DOUBLE` | `DOUBLE` | Directly supported |
| `DECIMAL(p,s)` | `DECIMAL(p,s)` | Directly supported |
| `STRING` | `STRING` | Directly supported |
| `VARCHAR(n)` | `VARCHAR(n)` | Directly supported |
| `CHAR(n)` | `CHAR(n)` | Directly supported |
| `DATE` | `DATE` | Directly supported |
| `TIMESTAMP` | `TIMESTAMP_NTZ` | Hive TIMESTAMP has no timezone semantics |
| `BOOLEAN` | `BOOLEAN` | Directly supported |
| `BINARY` | `BINARY` | Directly supported |
| `ARRAY<T>` | `ARRAY<T>` | Directly supported |
| `MAP<K,V>` | `MAP<K,V>` | Directly supported |
| `STRUCT<...>` | `STRUCT<...>` | Directly supported |

### Spark SQL

| Spark type | Lakehouse type | Notes |
|-----------|---------------|------|
| `BooleanType` | `BOOLEAN` | Directly supported |
| `ByteType` | `TINYINT` | Spark Byte maps to Lakehouse TINYINT |
| `ShortType` | `SMALLINT` | Directly supported |
| `IntegerType` | `INT` | Directly supported |
| `LongType` | `BIGINT` | Directly supported |
| `FloatType` | `FLOAT` | Directly supported |
| `DoubleType` | `DOUBLE` | Directly supported |
| `DecimalType` | `DECIMAL(p,s)` | Directly supported |
| `StringType` | `STRING` | Directly supported |
| `BinaryType` | `BINARY` | Directly supported |
| `DateType` | `DATE` | Directly supported |
| `TimestampType` | `TIMESTAMP_LTZ` | Spark default is timezone-aware |
| `TimestampNTZType` | `TIMESTAMP_NTZ` | New timezone-naive type in Spark 3.4+ |
| `ArrayType` | `ARRAY<T>` | Directly supported |
| `MapType` | `MAP<K,V>` | Directly supported |
| `StructType` | `STRUCT<...>` | Directly supported |

> ⚠️ Spark's `TimestampType` is timezone-aware by default, mapping to Lakehouse's `TIMESTAMP_LTZ`. If Spark code uses `TimestampNTZType`, map to `TIMESTAMP_NTZ`.

> ⚠️ When writing to Lakehouse via Spark Connector, **all columns must be written — partial column writes are not supported**; and **writing to primary key tables (PK tables) is not supported**.

## Behavioral Differences

### Type Conversion Failure Handling

| Scenario | MySQL / PostgreSQL | Spark SQL | Lakehouse default |
|------|-------------------|-----------|----------------|
| `CAST('abc' AS INT)` | Error | Returns `NULL` | Returns `NULL` |
| Numeric overflow (e.g. `CAST(200 AS TINYINT)`) | Error | Returns `NULL` | Returns `NULL` |
| Invalid date (e.g. `CAST('2023-02-29' AS DATE)`) | Error | Returns `NULL` | Returns `NULL` |

Lakehouse runs in lenient mode by default, consistent with **Spark SQL**: conversion failures do not raise errors and silently return NULL. When migrating from strict-mode databases like MySQL/PostgreSQL, add explicit NULL checks at critical ETL nodes, or enable strict mode:

```sql
SET cz.sql.cast.mode = strict;
```

### CHAR Does Not Pad with Spaces

MySQL and standard SQL `CHAR(n)` pads short strings with spaces to length n. Lakehouse does not pad. `LENGTH(CAST('abc' AS CHAR(10)))` returns `3`, not `10`.

Comparisons also use actual content: `'abc' = 'abc  '` returns `false`.

### VARCHAR/CHAR Silently Truncates Overflow

Strings exceeding the declared length are silently truncated on write without error. When migrating from databases with strict length validation, it is recommended to retain length validation logic in the application layer.

### Strings in INSERT VALUES Are Not Implicitly Converted to Date Types

In `INSERT VALUES`, strings are not implicitly converted to `DATE`, `TIMESTAMP`, or `TIMESTAMP_NTZ` — explicit type declaration is required:

```sql
-- Error
INSERT INTO t(dt) VALUES ('2024-01-15');

-- Correct
INSERT INTO t(dt) VALUES (DATE'2024-01-15');
INSERT INTO t(dt) VALUES (CAST('2024-01-15' AS DATE));
```

Strings can implicitly match date columns in `SELECT`; this restriction applies only to `INSERT VALUES`.

### NOT IN Containing NULL

`v NOT IN (1, NULL)` always returns `NULL` under three-valued logic (not `true` or `false`), causing the filter condition to fail. This is consistent with MySQL, PostgreSQL, and Spark SQL behavior, but is easy to overlook:

```sql
-- The following query always returns empty results because the subquery may contain NULL
SELECT * FROM t WHERE id NOT IN (SELECT id FROM other);

-- Safe alternative
SELECT * FROM t WHERE NOT EXISTS (SELECT 1 FROM other WHERE other.id = t.id);
```

### Spark SQL Compatibility Notes

Spark SQL and Lakehouse are highly consistent in type conversion behavior (both return NULL in lenient mode). For the complete Spark SQL migration guide (including CREATE TABLE syntax, JSON processing, window functions, LATERAL VIEW, configuration mapping, etc.), see [Spark SQL Migration Guide](migration-spark-sql.md).

**Key notes:**
- `TimestampType` → `TIMESTAMP_LTZ`; `TimestampNTZType` → `TIMESTAMP_NTZ`
- DataFrame writes must include all columns; PK tables not supported
- Function compatibility is good; 40+ common functions fully supported

## Unsupported Aliases

The following aliases are common in other databases but not supported in Lakehouse — replace them manually during migration:

| Unsupported syntax | Replace with | Source |
|-------------|--------|------|
| `BOOL` | `BOOLEAN` | MySQL |
| `INT2` | `SMALLINT` | PostgreSQL |
| `INT4` | `INT` | PostgreSQL |
| `INT8` | `BIGINT` | PostgreSQL |
| `FLOAT4` | `FLOAT` | PostgreSQL |
| `FLOAT8` | `DOUBLE` | PostgreSQL |
| `NUMBER(p,s)` | `DECIMAL(p,s)` | Oracle |
| `DOUBLE PRECISION` | `DOUBLE` | Oracle/PostgreSQL |
| `INT16` | `SMALLINT` | Spark |
| `INT32` | `INT` | Spark |
| `INT64` | `BIGINT` | Spark |
| `FLOAT32` | `FLOAT` | Spark |
| `FLOAT64` | `DOUBLE` | Spark |

## Related Documentation

- [Data Types](data-type.md): Complete list of type aliases
- [Data Type Conversion](datatype-conversion.md): Explicit and implicit conversion rules
- [Migration Guide](tutorial_migration.md): Data migration operations
