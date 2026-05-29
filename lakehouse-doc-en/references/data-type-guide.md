# Data Types

Singdata Lakehouse supports numeric, string, time, boolean, binary, and complex types (ARRAY, MAP, STRUCT, JSON, VECTOR, BITMAP). It is compatible with common type aliases from MySQL, PostgreSQL, Hive, and other systems, so migrated DDL scripts can run without manually replacing type names.

---

## Type Quick Reference

### Numeric Types

| Type | Storage | Use Case |
|------|---------|---------|
| `TINYINT` | 1 byte | Status codes, enum values |
| `SMALLINT` | 2 bytes | Year values, small-range counters |
| `INT` | 4 bytes | General integer IDs, counters |
| `BIGINT` | 8 bytes | Large-scale IDs, millisecond timestamps |
| `FLOAT` | 4 bytes | Low-precision floating point, scientific computing |
| `DOUBLE` | 8 bytes | High-precision floating point, statistical analysis |
| `DECIMAL(p,s)` | Variable | Monetary amounts, exact calculations (recommended) |

### String Types

| Type | Length | Use Case |
|------|--------|---------|
| `CHAR(n)` | Fixed, max 255 | Fixed-length codes (country codes, status codes) |
| `VARCHAR(n)` | Variable, max 1,048,576 | Fields with a length cap (usernames, email addresses) |
| `STRING` | Unlimited | Long text, JSON strings (recommended) |

> ⚠️ **Note**: All three string types silently truncate when the declared length is exceeded — no error is raised.

### Time Types

| Type | Timezone | Use Case |
|------|----------|---------|
| `DATE` | None | Date dimensions, birthdays |
| `TIMESTAMP` | With timezone (stored as UTC) | Cross-timezone event times, log timestamps |
| `TIMESTAMP_NTZ` | No timezone (stored as-is) | Local business time, no timezone conversion needed |
| `INTERVAL` | — | Time differences, date arithmetic |

### Other Basic Types

| Type | Description |
|------|-------------|
| `BOOLEAN` | `TRUE` / `FALSE` / `NULL` |
| `BINARY` | Binary byte sequence |

### Complex Types

| Type | Description | Use Case |
|------|-------------|---------|
| `ARRAY<T>` | Ordered collection of same-type elements | Tag lists, multi-value attributes |
| `MAP<K,V>` | Key-value pair collection | Dynamic attributes, configuration items |
| `STRUCT<...>` | Nested structure with fixed fields | Addresses, coordinates, and other structured nesting |
| `JSON` | Semi-structured JSON document | Flexible schema, event attributes |
| `VECTOR(n)` | Fixed-dimension floating-point vector | Embedding storage, vector search, RAG |
| `BITMAP` | Compressed integer set (Roaring Bitmap) | UV statistics, user tag segmentation |

---

## In This Chapter

| Page | Description |
|------|-------------|
| [Data Types Reference](data-type.md) | Full description of each type, type alias mapping, migration compatibility |
| [Data Type Conversion](datatype-conversion.md) | Explicit conversion (CAST / `::`) and implicit conversion rules |
| [Numeric Types](number_type_guide.md) | TINYINT / SMALLINT / INT / BIGINT / FLOAT / DOUBLE / DECIMAL in detail |
| [String Types](string_guide.md) | CHAR / VARCHAR / STRING comparison and selection guide |
| [Date/Time Types](time_date_guide.md) | DATE / TIMESTAMP / TIMESTAMP_NTZ / INTERVAL comparison and selection guide |
| [BINARY](binary.md) | Binary type reference |
| [BOOLEAN](boolean.md) | Boolean type reference |
| [ARRAY](ARRAY.md) | Array type syntax and functions |
| [MAP](MAP.md) | Map type syntax and functions |
| [STRUCT](STRUCT.md) | Nested struct type syntax and functions |
| [JSON](JSON.md) | JSON type syntax, field access, and query examples |
| [VECTOR](vector-type.md) | Vector type syntax, dimension configuration, and vector index usage |
| [BITMAP](bitmap-type.md) | Bitmap type syntax, set operation functions reference |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Data Type Conversion Guide](SQL_Type_Conversion_Guide.md) | Type mapping when migrating from MySQL / PostgreSQL / Hive |
| [TIMESTAMP_NTZ Reference](data-types-timestamp-ntz.md) | Detailed explanation and use cases for timezone-free timestamps |
| [CREATE TABLE](create-table-ddl.md) | Full syntax for using data types when creating tables |
