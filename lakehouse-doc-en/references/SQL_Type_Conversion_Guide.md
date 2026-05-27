# Lakehouse Data Type Conversion Guide

## Overview

During data processing, it is often necessary to convert data from one type to another. Singdata Lakehouse provides multiple type conversion syntaxes, including standard `CAST`, shorthand `::`, safe conversion `TRY_CAST`, and automatic implicit conversion. This guide categorizes usage by common business scenarios to help you quickly master efficient and safe type conversion methods.

### Quick Navigation

* [Basic Type Conversion](#basic-type-conversion) -- Use CAST and :: for explicit conversion
* [Safe Type Conversion](#safe-type-conversion) -- Use TRY_CAST to handle dirty data
* [Date/Time Conversion](#datetime-conversion) -- Convert between strings and date/timestamp
* [JSON Data Conversion](#json-data-conversion) -- Parse strings into JSON type
* [Implicit Conversion Rules](#implicit-conversion-rules) -- Understand the boundaries of automatic conversion

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `CAST(expr AS type)` | Standard type conversion | General type conversion, standard SQL compatible |
| `expr::type` | Shorthand type conversion | Quick conversion, more concise code |
| `TRY_CAST(expr AS type)` | Safe type conversion | Handle data that may fail conversion, returns `NULL` instead of error |
| `PARSE_JSON(str)` | String to JSON | Parse JSON strings into JSON type |
| `TO_DATE(str, fmt)` | Formatted date conversion | Convert non-standard format strings to date |

***

## Prerequisites

The following examples use a simulated mixed-type table `mixed_data`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS mixed_data (
    id INT,
    str_val STRING,
    num_val DOUBLE,
    date_val STRING
);

-- Insert test data
INSERT INTO mixed_data VALUES
(1, '100', 3.14, '2024-06-01'),
(2, '200', 2.71, '2024/06/02'),
(3, 'abc', 1.41, 'invalid_date'),
(4, '300', NULL, '2024-06-04');
```

***

## Basic Type Conversion

Use `CAST` or `::` for explicit type conversion. Both are functionally equivalent; the `::` syntax is more concise.

```sql
-- Convert string to integer
SELECT 
    id,
    str_val,
    CAST(str_val AS INT) as cast_int,
    str_val::INT as shorthand_int
FROM mixed_data
WHERE str_val NOT IN ('abc');
```

**Result**:

| id | str_val | cast_int | shorthand_int |
|----|---------|----------|---------------|
| 1 | 100 | 100 | 100 |
| 2 | 200 | 200 | 200 |
| 4 | 300 | 300 | 300 |

> **Note**: If conversion fails (e.g., `'abc'` to `INT`), `CAST` throws an error and aborts the query.

***

## Safe Type Conversion

When data may contain unconvertible values, use `TRY_CAST` to avoid query errors. Failed conversions return `NULL`.

```sql
-- Safe conversion: returns NULL when conversion fails
SELECT 
    id,
    str_val,
    TRY_CAST(str_val AS INT) as safe_int
FROM mixed_data;
```

**Result**:

| id | str_val | safe_int |
|----|---------|----------|
| 1 | 100 | 100 |
| 2 | 200 | 200 |
| 3 | abc | NULL |
| 4 | 300 | 300 |

### Handling TRY_CAST Results

`TRY_CAST` returns `NULL` on failure, which can be filtered directly with `IS NULL`:

```sql
-- Filter rows that failed conversion
SELECT 
    id,
    str_val,
    TRY_CAST(str_val AS INT) as safe_int
FROM mixed_data
WHERE TRY_CAST(str_val AS INT) IS NOT NULL;
```

**Result**:

| id | str_val | safe_int |
|----|---------|----------|
| 1 | 100 | 100 |
| 2 | 200 | 200 |
| 4 | 300 | 300 |

***

## Date/Time Conversion

Convert strings to date or timestamp types, supporting standard and custom formats.

```sql
-- Standard format automatic conversion
SELECT 
    id,
    date_val,
    CAST(date_val AS DATE) as std_date
FROM mixed_data
WHERE date_val LIKE '____-__-__';
```

**Result**:

| id | date_val | std_date |
|----|----------|----------|
| 1 | 2024-06-01 | 2024-06-01 |
| 4 | 2024-06-04 | 2024-06-04 |

> **Note**: `CAST` is strict about date string format (recommended: `yyyy-MM-dd`). Non-standard formats (e.g., `2024/06/02`) return `NULL`; use `TO_DATE` instead.

### Custom Format Conversion

For non-standard formats, use `TO_DATE` with a format template:

```sql
-- Use TO_DATE to parse custom format
SELECT 
    id,
    date_val,
    TO_DATE(date_val, 'yyyy/MM/dd') as custom_date
FROM mixed_data
WHERE date_val = '2024/06/02';
```

***

## JSON Data Conversion

Parse JSON strings into Lakehouse's native `JSON` type for querying with JSON functions.

```sql
-- Parse a JSON string
SELECT 
    id,
    PARSE_JSON('{"name": "Alice", "age": 30}') as json_data,
    json_extract_string(PARSE_JSON('{"name": "Alice", "age": 30}'), '$.name') as name
FROM mixed_data
WHERE id = 1;
```

**Result**:

| id | json_data | name |
|----|-----------|------|
| 1 | {"name":"Alice","age":30} | Alice |

> **Tip**: In Lakehouse, `JSON` is a first-class citizen type. For semi-structured data storage, use `JSON` columns directly at table creation time for better performance than `STRING`.

***

## Implicit Conversion Rules

Lakehouse performs automatic implicit conversion in certain scenarios, but explicit conversion is recommended for code readability and stability.

### Supported Implicit Conversions

* Between numeric types: `INT` to `DOUBLE` (widening precision)
* String to date: In `WHERE` conditions, `date_col = '2024-06-01'` is automatically converted

### Unsupported Implicit Conversions

* **Write operations**: In `INSERT INTO`, strings cannot be implicitly converted to `DATE`, `TIMESTAMP`, `JSON`, or `BINARY`; explicit conversion is required.
* **Complex types**: `STRING` cannot be implicitly converted to `JSON` or `ARRAY`.

```sql
-- Wrong: implicit conversion during write
INSERT INTO target_table (date_col) VALUES ('2024-06-01');

-- Correct: explicit conversion
INSERT INTO target_table (date_col) VALUES (DATE '2024-06-01');
-- Or use CAST
INSERT INTO target_table (date_col) VALUES (CAST('2024-06-01' AS DATE));
```

***

## Clean Up Test Data

After completing type conversion verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS mixed_data;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **TRY_CAST Return Value**: Returns `NULL` on conversion failure; can be filtered directly with `IS NULL`.
2. **Strict Date Format**: `CAST` for date conversion requires standard format (`yyyy-MM-dd`); non-standard formats need `TO_DATE(str, fmt)`.
3. **Precision Loss**: `DOUBLE` to `INT` truncates the decimal part; `DECIMAL` to `INT` rounds.
4. **JSON Field Name Case**: `FROM_JSON` force-lowercases field names when parsing schemas. Use `PARSE_JSON` to preserve case.
5. **Date Literals**: Prefer `DATE '2024-06-01'` or `TIMESTAMP '2024-06-01 10:00:00'` syntax, which is more concise than `CAST`.

***

## Related Documentation

* [Data Types](data-type.md)
* [Data Type Conversion](datatype-conversion.md)
* [JSON Query Syntax](query-json-sy.md)
