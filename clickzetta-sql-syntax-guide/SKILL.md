---
name: clickzetta-sql-syntax-guide
description: |
  Complete SQL syntax reference for ClickZetta Lakehouse, plus comprehensive compatibility
  guides for migrating from Snowflake, Databricks, and Spark SQL. Covers full DDL/DML/DQL
  syntax, implicit type conversion rules, and migration pitfall quick reference.
  Helps users migrating from Snowflake or Databricks quickly find the correct syntax and
  avoid common errors.
  Triggered when user says "Snowflake migration", "Databricks migration", "Spark SQL migration",
  "syntax differences", "how to write in ClickZetta", "TARGET_LAG", "QUALIFY", "VARIANT",
  "METADATA$ACTION", "CREATE OR REPLACE", "LISTAGG", "IFF", "DATEADD", "FLATTEN", "PIVOT",
  "SQL syntax reference", "data types", "DATEDIFF", "CHARINDEX", "ZEROIFNULL",
  "OBJECT_CONSTRUCT", "ARRAY_SIZE", "APPLY CHANGES INTO", "ZORDER",
  "WHEN NOT MATCHED BY SOURCE", "WITH RECURSIVE", "BEGIN TRANSACTION",
  "implicit cast", "implicit type conversion", "date insert", "BOOLEAN insert", "UNION", "INTERSECT",
  "EXCEPT", "set operations", "STRUCT AS", "named_struct", "JSON", "semi-structured",
  "wide table", "VARIANT", "JSON fields", "flexible schema", "customer case".
  Keywords: SQL syntax, DDL, DML, DQL, migration, Snowflake, Databricks, Spark SQL, compatibility
---

# ClickZetta Lakehouse SQL Syntax Guide

## Reference Document Index

| Document | Content |
|---|---|
| [Snowflake Migration Guide](references/migration-snowflake.md) | Object mapping, type conversion, syntax differences, function comparison (complete) |
| [Databricks Migration Guide](references/migration-databricks.md) | Delta Lake differences, APPLY CHANGES, ZORDER alternatives |
| [DDL Reference](references/ddl-reference.md) | Schema/Table/View/Index/Time Travel complete syntax |
| [DML Reference](references/dml-reference.md) | INSERT/UPDATE/DELETE/MERGE/COPY INTO + type conversion rules |
| [DQL Reference](references/dql-reference.md) | SELECT/JOIN/Window Functions/CTE/JSON/ARRAY/LATERAL VIEW |
| [Functions Reference](references/functions-reference.md) | Numeric/String/Date/Conditional/Aggregate/Vector functions complete list |
| [vs Snowflake](references/vs-snowflake.md) | Differences summary (including implicit conversion rules table) |
| [vs Spark SQL](references/vs-spark.md) | Data type mapping + syntax differences summary |

---

## ⚠️ Most Common Migration Pitfalls (Quick Reference)

| Scenario | Snowflake / Spark | ClickZetta Correct Syntax |
|---|---|---|
| Replace regular table | `CREATE OR REPLACE TABLE t` | `CREATE OR REPLACE TABLE t` ✅ ClickZetta supports this; `CREATE OR REPLACE TABLE IF NOT EXISTS t` ❌ OR REPLACE and IF NOT EXISTS cannot be used together |
| OR REPLACE + IF NOT EXISTS | `CREATE OR REPLACE TABLE IF NOT EXISTS t` | ❌ Cannot use both together, will throw error |
| Dynamic table refresh | `TARGET_LAG = '1 hour'` (SF) | `PROPERTIES ('target_lag' = '1 hour', 'warehouse' = 'vc')` |
| Stream metadata | `METADATA$ACTION` | `__change_type` |
| Object storage import | `COPY INTO t FROM @stage` | `COPY INTO t FROM VOLUME v USING CSV` |
| Window filter | `QUALIFY ROW_NUMBER() = 1` | `QUALIFY ROW_NUMBER() = 1` ✅ ClickZetta supports this too! |
| Array expansion | `LATERAL FLATTEN(input => arr)` (SF) | `LATERAL VIEW EXPLODE(arr)` |
| Semi-structured access | `data:key` (SF) | `data['key']` |
| List aggregation | `LISTAGG(col, ',')` (SF) | `GROUP_CONCAT(col SEPARATOR ',')` |
| Conditional function | `IFF(cond, a, b)` (SF) | `IF(cond, a, b)` |
| Date arithmetic | `DATEADD(day, 7, dt)` (SF) | `DATEADD(day, 7, dt)` ✅ also supported; or use `DATE_ADD(dt, 7)` |
| DATEDIFF order | `DATEDIFF(day, start, end)` (SF) | `DATEDIFF(day, start, end)` ✅ three-parameter form also supported; or `DATEDIFF(end, start)` two-parameter form (returns days) |
| Find substring position | `CHARINDEX(sub, s)` (SF) | `INSTR(s, sub)` ← parameter order is reversed! |
| Case-insensitive match | `ILIKE` (SF) | `ILIKE` ✅ ClickZetta supports this too! |
| Set difference | `MINUS` (Oracle/DB2) | `MINUS` ✅ ClickZetta supports this too! |
| Recursive CTE | `WITH RECURSIVE` (SF/Databricks) | ❌ Not supported, use Python/ZettaPark instead |
| **⚠️ Timestamp string insert** | `INSERT INTO t VALUES (1, '2026-05-01 10:00:00')` | ❌ **Error**: must explicitly convert `CAST('2026-05-01 10:00:00' AS TIMESTAMP)` or `TIMESTAMP '2026-05-01 10:00:00'` |
| Set operations | `UNION` / `UNION ALL` / `INTERSECT` / `EXCEPT` | ✅ All supported |
| Transactions | `BEGIN; COMMIT; ROLLBACK;` | ❌ Not supported, use MERGE INTO for atomic operations |
| MERGE unmatched delete | `WHEN NOT MATCHED BY SOURCE THEN DELETE` | ❌ Not supported, requires two steps: MERGE INTO + DELETE |
| Delta ZORDER | `OPTIMIZE t ZORDER BY (col)` | `OPTIMIZE t` (only does small file compaction, no ZORDER) |
| STRUCT named fields | `STRUCT(1 AS id, 'Alice' AS name)` | `named_struct('id', 1, 'name', 'Alice')` ✅ |
| SEQUENCE object | `CREATE SEQUENCE seq` | ❌ Not supported, use `IDENTITY(1)` column instead |
| IDENTITY column type | `id INT IDENTITY` | `id BIGINT IDENTITY` (IDENTITY only supports BIGINT; INT/SMALLINT will error) |
| Current time function | `NOW()` | `NOW()` ✅ ClickZetta supports this too! Also `CURRENT_TIMESTAMP()` |
| Boolean type name | `BOOL` | `BOOLEAN` (ClickZetta does not support BOOL shorthand) |
| String type | `VARCHAR(n)` | Recommend `STRING` (no length limit, max 16MB); `VARCHAR(n)` also supported but not recommended |
| Numeric type | `NUMBER(p,s)` (SF) | `DECIMAL(p,s)` |
| Semi-structured type | `VARIANT` (SF) | `JSON` |
| Row limit | `SELECT TOP 10` (SF) | `SELECT ... LIMIT 10` |
| NULL to 0 | `ZEROIFNULL(x)` (SF) | `COALESCE(x, 0)` |
| 0 to NULL | `NULLIFZERO(x)` (SF) | `NULLIF(x, 0)` |
| Object aggregation | `OBJECT_AGG(k, v)` (SF) | `MAP_AGG(k, v)` |
| Array size | `ARRAY_SIZE(arr)` (SF) | `SIZE(arr)` or `ARRAY_SIZE(arr)` ✅ both supported |
| PIVOT | Native PIVOT syntax (SF) | `CASE WHEN` manual implementation |
| Temporary table | `CREATE TEMPORARY TABLE` (SF) | Not supported, use CTE instead |
| Date string insert | `INSERT ... VALUES (..., '2024-01-15', ...)` | `CAST('2024-01-15' AS DATE)` or `DATE '2024-01-15'` or `TO_DATE(...)` |
| Timestamp string insert | `INSERT ... VALUES (..., '2024-01-15 12:00:00', ...)` | `CAST(... AS TIMESTAMP)` or `TIMESTAMP '...'` or `TO_TIMESTAMP(...)` |
| BOOLEAN insert | `INSERT ... VALUES (..., 'true', ...)` or `..., 1, ...` | `TRUE` / `FALSE` or `CAST(1 AS BOOLEAN)` |
| JSON insert | `INSERT ... VALUES (..., '{"k":1}', ...)` | `PARSE_JSON('{"k":1}')` or `CAST(... AS JSON)` |
| String to numeric column | `INSERT ... VALUES (..., '123', ...)` | `CAST('123' AS INT)` |
| UPDATE same restriction | `UPDATE t SET dt = '2024-01-01'` | `UPDATE t SET dt = CAST('2024-01-01' AS DATE)` |
| WHERE allows it | N/A | `WHERE dt = '2024-01-01'` ✅ Strings can be implicitly compared in WHERE |
| Index syntax keyword | `USING BLOOM_FILTER` | `BLOOMFILTER` (no USING); vector/inverted inline at table creation use `USING VECTOR` / `USING INVERTED` |
| DROP INDEX | `DROP INDEX idx ON table` | `DROP INDEX idx` (no ON table) |
| TRUNCATE IF EXISTS | `TRUNCATE TABLE IF EXISTS t` | ❌ Does not support `IF EXISTS`; use `TRUNCATE TABLE t` directly (errors if table doesn't exist) |
| DESC TABLE extended | `DESC TABLE t EXTENDED` / `DESC TABLE t HISTORY` | ❌ Does not support EXTENDED/HISTORY parameters; use `DESC TABLE t` or `SHOW CREATE TABLE t` |
| TABLESAMPLE | `SELECT * FROM t TABLESAMPLE (50 PERCENT)` | ❌ Does not support PERCENT syntax; use `ORDER BY RAND() LIMIT n` instead |
| MERGE multiple MATCHED order | DELETE can precede UPDATE | UPDATE must come before DELETE |
| Synonym | `CREATE SYNONYM s FOR t` (Oracle) | `CREATE SYNONYM s FOR TABLE t` ✅ supports TABLE/VOLUME/FUNCTION objects |

---

## Data Type Quick Reference

```sql
-- Numeric
TINYINT / SMALLINT / INT / BIGINT
FLOAT / DOUBLE
DECIMAL(p, s)          -- Exact numeric (Snowflake uses NUMBER)

-- String
STRING                 -- Recommended, no length limit
VARCHAR(n)             -- Max 65533 characters
CHAR(n)                -- Fixed-length, 1-255

-- Temporal
DATE                   -- YYYY-MM-DD
TIMESTAMP              -- With local timezone (≈ Snowflake TIMESTAMP_LTZ)
TIMESTAMP_NTZ          -- Without timezone (same as Snowflake TIMESTAMP_NTZ)

-- Boolean / Binary
BOOLEAN / BINARY

-- Semi-structured
JSON                   -- Replaces Snowflake VARIANT
ARRAY<T>               -- Must specify element type, e.g., ARRAY<INT>
MAP<K, V>              -- e.g., MAP<STRING, INT>
STRUCT<f1:T1, f2:T2>   -- Struct type

-- AI-specific
VECTOR(FLOAT, 1024)    -- Vector type (ClickZetta-specific)
```

---

## ClickZetta-Specific Objects (No Snowflake/Spark Equivalent)

```sql
-- Compute cluster
CREATE VCLUSTER my_vc VCLUSTER_TYPE = ANALYTICS VCLUSTER_SIZE = 4;
USE VCLUSTER my_vc;

-- Dynamic Table (incremental computation)
CREATE DYNAMIC TABLE sales_daily
    REFRESH INTERVAL 5 MINUTE VCLUSTER default_ap
AS SELECT DATE(created_at) AS dt, SUM(amount) AS total FROM orders GROUP BY 1;

-- Table Stream (CDC)
CREATE TABLE STREAM orders_stream ON TABLE orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
-- Metadata fields: __change_type (INSERT/UPDATE_BEFORE/UPDATE_AFTER/DELETE)

-- Pipe (continuous ingestion)
CREATE PIPE oss_pipe
    AS COPY INTO orders FROM VOLUME my_volume USING CSV OPTIONS('header'='true');

-- Volume (object storage)
CREATE EXTERNAL VOLUME my_vol
    LOCATION 'oss://bucket/path'
    USING CONNECTION my_oss_conn;

-- Share (cross-instance data sharing)
CREATE SHARE my_share;
GRANT SELECT, READ METADATA ON TABLE public.orders TO SHARE my_share;

-- Synonym (create aliases for objects)
CREATE SYNONYM my_orders FOR TABLE other_schema.orders;
CREATE SYNONYM my_vol FOR VOLUME other_schema.data_volume;
CREATE SYNONYM my_func FOR FUNCTION other_schema.udf_name;
DROP SYNONYM my_orders FOR TABLE;
SHOW SYNONYMS;

-- Time Travel
SELECT * FROM orders TIMESTAMP AS OF '2024-01-01 00:00:00';
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-01 00:00:00';
UNDROP TABLE orders;

-- Vector search
CREATE TABLE docs (id INT, vec VECTOR(FLOAT, 1024),
    INDEX vec_idx (vec) USING VECTOR PROPERTIES ("distance.function"="cosine_distance"));
SELECT id, cosine_distance(vec, CAST('[0.1,0.2,...]' AS VECTOR(1024))) AS dist
FROM docs ORDER BY dist LIMIT 10;
```

---

## ❌ Explicitly Unsupported Features

The following features exist in Snowflake/Databricks/Spark but are **not supported** in ClickZetta. Using them will throw errors; use the alternatives instead.

### String Functions

| Unsupported Function | Alternative |
|---|---|
| `INITCAP(s)` | `CONCAT(UPPER(SUBSTR(s, 1, 1)), LOWER(SUBSTR(s, 2)))` |
| `SOUNDEX(s)` | No alternative |
| `CHARINDEX(sub, s)` | `INSTR(s, sub)` (note: parameter order is reversed) |

### JSON Functions

| Unsupported Function | Alternative |
|---|---|
| `JSON_ARRAY_LENGTH(json)` | `SIZE(CAST(json_str AS ARRAY<STRING>))` |
| `JSON_OBJECT_KEYS(json)` | No direct alternative, requires manual parsing |

### Collection/Array/MAP Functions

| Unsupported Function | Alternative |
|---|---|
| `MAP_FROM_ZIP(keys, values)` | `MAP_FROM_ARRAYS(keys, values)` |
| `TO_ARRAY(expr)` | `ARRAY(expr)` or `CAST(expr AS ARRAY<T>)` |
| `ARRAY_SIZE(arr)` (Snowflake) | `SIZE(arr)` or `ARRAY_SIZE(arr)` ✅ both supported |

### Regex Functions

| Unsupported Function | Alternative |
|---|---|
| `REGEXP_SUBSTR(s, pattern)` | `REGEXP_EXTRACT(s, '(pattern)')` |

### Table Functions/Generators

| Unsupported Function | Alternative |
|---|---|
| `GENERATE(start, end)` | No direct alternative, use CTE + UNION ALL or application layer |
| `RANGE(n)` | No direct alternative |
| `TABLESAMPLE (n PERCENT)` | `ORDER BY RAND() LIMIT n` |

### Geospatial/Network

| Unsupported Function | Alternative |
|---|---|
| `ST_GeomFromWKT(wkt)` | Geospatial functions not supported |
| `TO_IPV4(ip_string)` | IP address functions not supported |

### Approximate Computation

| Unsupported Function | Alternative |
|---|---|
| `HLL_APPROX(col)` | `APPROX_COUNT_DISTINCT(col)` |

### Bitwise Operations

| Unsupported Function | Alternative |
|---|---|
| `BITAND(a, b)` | `a & b` (bitwise operator) |
| `BITOR(a, b)` | `a \| b` |
| `BITXOR(a, b)` | `a ^ b` |

### DDL/DML Limitations

| Unsupported Syntax | Alternative |
|---|---|
| `TRUNCATE TABLE IF EXISTS t` | Check if table exists first, then `TRUNCATE TABLE t` |
| `DESC TABLE t EXTENDED` | `DESC TABLE t` or `SHOW CREATE TABLE t` |
| `DESC TABLE t HISTORY` | `SHOW TABLES HISTORY WHERE table_name = 't'` |
| `CREATE TEMPORARY TABLE` | Use CTE instead, or create a regular table and delete manually |
| `CREATE OR REPLACE TABLE` | `CREATE OR REPLACE TABLE t (...)` ✅ directly supported |
| `BEGIN; COMMIT; ROLLBACK;` | Transactions not supported, use MERGE for atomic operations |
| `WITH RECURSIVE` | Recursive CTE not supported, use Python/ZettaPark instead |
