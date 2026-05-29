# Snowflake → ClickZetta Migration Guide

> Comprehensive coverage of SQL compatibility issues when migrating from Snowflake to ClickZetta Lakehouse. All conclusions verified on a real Lakehouse instance.

---

## Object Concept Mapping

| Snowflake | ClickZetta | Description |
|---|---|---|
| DATABASE | WORKSPACE | Top-level container |
| SCHEMA | SCHEMA | Same |
| WAREHOUSE | VCLUSTER | Compute cluster |
| STAGE | VOLUME | File storage area |
| STORAGE INTEGRATION | STORAGE CONNECTION | Object storage authentication |
| SNOWPIPE | PIPE | Continuous ingestion pipeline |
| STREAM | TABLE STREAM | CDC change capture |
| DYNAMIC TABLE | DYNAMIC TABLE | Different syntax |
| TASK | Studio Task | Scheduled tasks |
| SEQUENCE | IDENTITY column | Auto-increment sequence |
| SHARE | SHARE | Cross-instance data sharing (same syntax) |

---

## DDL Differences

### CREATE TABLE

```sql
-- Snowflake
CREATE OR REPLACE TABLE orders (
    id NUMBER AUTOINCREMENT,
    customer_id NUMBER(10,0),
    amount NUMBER(18,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    meta VARIANT,
    tags ARRAY
) CLUSTER BY (DATE_TRUNC('month', created_at));

-- ClickZetta equivalent
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT IDENTITY(1),          -- AUTOINCREMENT → IDENTITY
    customer_id INT,                 -- NUMBER(10,0) → INT
    amount DECIMAL(18,2),            -- NUMBER(18,2) → DECIMAL(18,2)
    status STRING DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT current_timestamp(),
    meta JSON,                       -- VARIANT → JSON
    tags ARRAY<STRING>               -- ARRAY → ARRAY<T> (must specify element type)
)
CLUSTERED BY (customer_id) INTO 16 BUCKETS;  -- CLUSTER BY → CLUSTERED BY ... BUCKETS
```

### Unsupported DDL

```sql
-- ❌ CREATE OR REPLACE TABLE (use IF NOT EXISTS)
CREATE OR REPLACE TABLE t (...);
-- ✅ ClickZetta
CREATE TABLE IF NOT EXISTS t (...);

-- ❌ CREATE SEQUENCE (use IDENTITY column)
CREATE SEQUENCE my_seq START 1 INCREMENT 1;
-- ✅ ClickZetta
CREATE TABLE t (id BIGINT IDENTITY(1), ...);

-- ❌ CREATE TEMPORARY TABLE (use CTE instead)
CREATE TEMPORARY TABLE temp_t AS SELECT ...;
-- ✅ ClickZetta
WITH temp_t AS (SELECT ...) SELECT * FROM temp_t;

-- ❌ CREATE TRANSIENT TABLE (use data_lifecycle to control)
CREATE TRANSIENT TABLE t (...);
-- ✅ ClickZetta
CREATE TABLE t (...) PROPERTIES ('data_lifecycle' = '1');

-- ❌ CLUSTER BY (column-level)
CREATE TABLE t (...) CLUSTER BY (col1, col2);
-- ✅ ClickZetta (bucketing)
CREATE TABLE t (...) CLUSTERED BY (col1) INTO 16 BUCKETS;
```

---

## Data Type Mapping

| Snowflake | ClickZetta | Notes |
|---|---|---|
| `NUMBER(p,s)` / `NUMERIC(p,s)` | `DECIMAL(p,s)` | |
| `NUMBER(10,0)` / `INTEGER` | `INT` / `BIGINT` | |
| `FLOAT` / `FLOAT4` | `FLOAT` | |
| `FLOAT8` / `DOUBLE` | `DOUBLE` | |
| `VARCHAR(n)` / `TEXT` | `STRING` or `VARCHAR(n)` | |
| `CHAR(n)` | `CHAR(n)` | Same |
| `BOOLEAN` | `BOOLEAN` | Same, but different write rules (see below) |
| `DATE` | `DATE` | Same |
| `TIMESTAMP_LTZ` | `TIMESTAMP` | With local timezone |
| `TIMESTAMP_NTZ` | `TIMESTAMP_NTZ` | Without timezone |
| `TIMESTAMP_TZ` | `TIMESTAMP` | ClickZetta has no separate TZ type |
| `VARIANT` | `JSON` | Different access syntax (see below) |
| `ARRAY` | `ARRAY<T>` | Must specify element type |
| `OBJECT` | `MAP<STRING,STRING>` or `STRUCT<...>` | |
| `GEOGRAPHY` | Not supported | |
| `VECTOR(FLOAT, N)` | `VECTOR(FLOAT, N)` | Same |

---

## ⚠️ Type Conversion on Write (Important Difference)

Snowflake allows implicit string conversion to date/boolean types; ClickZetta **does not**:

```sql
-- ❌ Works in Snowflake, errors in ClickZetta
INSERT INTO t VALUES ('2024-01-15', 'true', '123');

-- ✅ ClickZetta requires explicit conversion
INSERT INTO t VALUES (DATE '2024-01-15', TRUE, CAST('123' AS INT));
INSERT INTO t VALUES (CAST('2024-01-15' AS DATE), CAST('true' AS BOOLEAN), 123);
```

| Target Type | Snowflake | ClickZetta |
|---|---|---|
| `DATE` ← `'2024-01-15'` | ✅ Implicit | ❌ Requires `DATE '...'` or `CAST` |
| `TIMESTAMP` ← `'2024-01-15 12:00'` | ✅ Implicit | ❌ Requires `TIMESTAMP '...'` or `CAST` |
| `BOOLEAN` ← `'true'` | ✅ Implicit | ❌ Requires `TRUE`/`FALSE` or `CAST` |
| `BOOLEAN` ← `1` | ✅ Implicit | ❌ Requires `CAST(1 AS BOOLEAN)` |
| `INT` ← `'123'` | ✅ Implicit | ❌ Requires `CAST('123' AS INT)` |
| `JSON` ← `'{"k":1}'` | ✅ Implicit | ❌ Requires `PARSE_JSON(...)` or `CAST` |
| String comparison in WHERE | ✅ | ✅ Allowed |

---

## DML Differences

### INSERT / UPDATE

```sql
-- Snowflake: strings can be implicitly converted
INSERT INTO orders VALUES (1, '2024-01-15', 'true');

-- ClickZetta: must explicitly convert
INSERT INTO orders VALUES (1, DATE '2024-01-15', TRUE);
UPDATE orders SET dt = CAST('2024-06-01' AS DATE) WHERE id = 1;
```

### MERGE INTO

```sql
-- Snowflake: supports multiple WHEN NOT MATCHED, supports WHEN NOT MATCHED BY SOURCE
MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
WHEN NOT MATCHED BY SOURCE THEN DELETE;  -- ❌ ClickZetta does not support

-- ClickZetta: WHEN NOT MATCHED can only appear once, UPDATE must come before DELETE
MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED AND s.flag = 0 THEN UPDATE SET t.val = s.val  -- UPDATE first
WHEN MATCHED AND s.flag = 1 THEN DELETE                    -- DELETE second
WHEN NOT MATCHED THEN INSERT (id, val) VALUES (s.id, s.val);
```

### Transactions

```sql
-- ❌ ClickZetta does not support transaction syntax
BEGIN;
BEGIN TRANSACTION;
START TRANSACTION;
COMMIT;
ROLLBACK;

-- ✅ Use MERGE for atomic UPSERT
MERGE INTO target USING source ON ...
```

---

## DQL Differences

### QUALIFY (Window Function Filtering)

```sql
-- Both support QUALIFY
SELECT * FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) = 1;
```

### PIVOT / UNPIVOT

```sql
-- Snowflake: natively supported
SELECT * FROM sales
PIVOT (SUM(amount) FOR month IN ('Jan', 'Feb', 'Mar'));

-- ClickZetta: use CASE WHEN
SELECT product,
    SUM(CASE WHEN month = 'Jan' THEN amount END) AS Jan,
    SUM(CASE WHEN month = 'Feb' THEN amount END) AS Feb
FROM sales GROUP BY product;
```

### LATERAL FLATTEN → LATERAL VIEW EXPLODE

```sql
-- Snowflake: LATERAL FLATTEN
SELECT f.value::STRING AS skill
FROM employees, LATERAL FLATTEN(input => skills) f;

-- ClickZetta: LATERAL VIEW EXPLODE
SELECT skill
FROM employees
LATERAL VIEW EXPLODE(skills) lv AS skill;

-- With position index
SELECT pos, skill
FROM employees
LATERAL VIEW POSEXPLODE(skills) lv AS pos, skill;
```

### JSON Access Syntax

```sql
-- Snowflake: colon syntax
SELECT data:address:city AS city FROM users;
SELECT data[0]:name AS name FROM users;
SELECT data:scores[2] AS score FROM users;

-- ClickZetta: bracket syntax
SELECT data['address']['city'] AS city FROM users;
SELECT data['phoneNumbers'][0]['name'] AS name FROM users;
SELECT data['scores'][2] AS score FROM users;

-- Type conversion
-- Snowflake: data:age::INT
-- ClickZetta: CAST(data['age'] AS INT)
```

### OBJECT_CONSTRUCT / ARRAY_CONSTRUCT

```sql
-- Snowflake
SELECT OBJECT_CONSTRUCT('name', 'Alice', 'age', 30) AS obj;
SELECT ARRAY_CONSTRUCT(1, 2, 3) AS arr;

-- ClickZetta
SELECT MAP('name', 'Alice') AS obj;          -- simple MAP
SELECT named_struct('id', 1, 'name', 'Alice') AS person;  -- ✅ named fields use named_struct
SELECT STRUCT(1, 'Alice') AS person;         -- positional parameter syntax
SELECT ARRAY(1, 2, 3) AS arr;               -- ARRAY_CONSTRUCT → ARRAY()
```

### ASOF JOIN / MATCH_RECOGNIZE

```sql
-- ❌ ClickZetta does not support
SELECT * FROM t1 ASOF JOIN t2 ON t1.id = t2.id;
SELECT * FROM t MATCH_RECOGNIZE (...);
```

---

## Function Differences

### Date Functions

```sql
-- Snowflake → ClickZetta
DATEADD(day, 7, dt)          → DATEADD(day, 7, dt)  ✅ same; also DATE_ADD(dt, 7)
DATEDIFF(day, start, end)    → DATEDIFF(end, start)  ⚠️ parameter order reversed!
DATE_TRUNC('month', dt)      → DATE_TRUNC('month', dt)  same
TO_DATE('2024-01-01')        → TO_DATE('2024-01-01')  same
CONVERT_TIMEZONE(tz, dt)     → CONVERT_TZ(dt, from_tz, to_tz)
SYSDATE() / GETDATE()        → CURRENT_TIMESTAMP() / NOW()
LAST_DAY(dt)                 → LAST_DAY(dt)  same
YEAR(dt) / MONTH(dt)         → YEAR(dt) / MONTH(dt)  same
```

### String Functions

```sql
-- Snowflake → ClickZetta
CHARINDEX(sub, s)            → INSTR(s, sub)  ⚠️ parameter order reversed!
EDITDISTANCE(s1, s2)         → LEVENSHTEIN(s1, s2)
STRTOK(s, delim, n)          → SPLIT_PART(s, delim, n)
ILIKE(s, pattern)            → ILIKE(s, pattern)  ✅ ClickZetta also supports!
CONTAINS(s, sub)             → INSTR(s, sub) > 0
STARTSWITH(s, prefix)        → s LIKE 'prefix%'
ENDSWITH(s, suffix)          → s LIKE '%suffix'
INITCAP(s)                   → INITCAP(s)  same
REGEXP_LIKE(s, p)            → RLIKE(s, p) or s RLIKE p
```

### Aggregate Functions

```sql
-- Snowflake → ClickZetta
LISTAGG(col, ',') WITHIN GROUP (ORDER BY col)  → GROUP_CONCAT(col ORDER BY col SEPARATOR ',')
ARRAY_AGG(col) WITHIN GROUP (ORDER BY col)     → ARRAY_AGG(col)  ⚠️ WITHIN GROUP not supported
OBJECT_AGG(key, value)                         → MAP_AGG(key, value)
APPROX_COUNT_DISTINCT(col)                     → APPROX_COUNT_DISTINCT(col)  same
MEDIAN(col)                                    → MEDIAN(col)  same
```

### Conditional Functions

```sql
-- Snowflake → ClickZetta
IFF(cond, a, b)              → IF(cond, a, b)
ZEROIFNULL(x)                → COALESCE(x, 0) or NVL(x, 0)
NULLIFZERO(x)                → NULLIF(x, 0)
DECODE(expr, v1, r1, ...)    → DECODE(expr, v1, r1, ...)  same
BOOLAND(a, b)                → a AND b
BOOLOR(a, b)                 → a OR b
```

---

## Stream Metadata Fields

```sql
-- Snowflake Stream
METADATA$ACTION        -- 'INSERT' / 'DELETE'
METADATA$ISUPDATE      -- TRUE/FALSE (UPDATE produces a DELETE+INSERT pair)
METADATA$ROW_ID        -- row unique identifier

-- ClickZetta Table Stream
__change_type          -- 'INSERT' / 'UPDATE_BEFORE' / 'UPDATE_AFTER' / 'DELETE'
__commit_version       -- commit version number
__commit_timestamp     -- commit timestamp

-- MERGE pattern for consuming Stream
-- Snowflake
MERGE INTO target t USING stream s ON t.id = s.id
WHEN MATCHED AND s.METADATA$ACTION = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED AND s.METADATA$ACTION = 'INSERT' THEN INSERT ...;

-- ClickZetta
MERGE INTO target t USING stream s ON t.id = s.id
WHEN MATCHED AND s.__change_type = 'UPDATE_AFTER' THEN UPDATE SET ...
WHEN MATCHED AND s.__change_type = 'DELETE' THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT' THEN INSERT ...;
```

---

## Dynamic Table Differences

```sql
-- Snowflake
CREATE DYNAMIC TABLE product_sales
    TARGET_LAG = '1 minutes'
    WAREHOUSE = my_warehouse
AS SELECT ...;

-- ClickZetta (does not support TARGET_LAG)
CREATE DYNAMIC TABLE product_sales
    REFRESH INTERVAL 1 MINUTE VCLUSTER default_ap
AS SELECT ...;
```

---

## Verified Compatibility (Snowflake has it, ClickZetta also has it)

- `SEMI JOIN` / `ANTI JOIN` ✅
- `QUALIFY` ✅ (ClickZetta also supports)
- `ILIKE` ✅ (ClickZetta also supports)
- `DATEADD` ✅ (ClickZetta also supports)
- `MINUS` (equivalent to EXCEPT) ✅
- `DECODE` ✅
- `INITCAP` ✅
- `MEDIAN` ✅
- `APPROX_COUNT_DISTINCT` ✅
- `TRY_CAST` ✅
- `NULLIF` / `COALESCE` / `NVL` ✅
- `GROUPING SETS` / `ROLLUP` / `CUBE` ✅
- `WITH CTE` ✅
- `REGEXP_LIKE` / `RLIKE` ✅
- `SPLIT_PART` ✅
- `LAST_DAY` ✅
- `IDENTITY` column (replaces AUTOINCREMENT/SEQUENCE) ✅
