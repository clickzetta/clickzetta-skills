# ClickZetta Lakehouse vs Snowflake SQL Differences

> Source: Product documentation + migration practice

## Object Concept Mapping

| ClickZetta Lakehouse | Snowflake | Description |
|---|---|---|
| WORKSPACE | DATABASE | Workspace ≈ Database |
| SCHEMA | SCHEMA | Same |
| VCLUSTER | WAREHOUSE | Compute cluster |
| STORAGE CONNECTION | STORAGE INTEGRATION | Object storage authentication |
| VOLUME | STAGE | File storage area |
| TABLE | TABLE | Same |
| PIPE | SNOWPIPE | Continuous ingestion pipeline |
| TABLE STREAM | STREAM | Change data capture |
| DYNAMIC TABLE | DYNAMIC TABLE | Incremental computation table (different syntax) |
| Studio Task | TASK | Scheduled tasks |

---

## DDL Differences

### CREATE OR REPLACE vs IF NOT EXISTS

```sql
-- Snowflake: supports CREATE OR REPLACE
CREATE OR REPLACE TABLE orders (id INT, amount DECIMAL);

-- ClickZetta: does not support CREATE OR REPLACE, use IF NOT EXISTS
CREATE TABLE IF NOT EXISTS orders (id INT, amount DECIMAL);
-- Use ALTER TABLE to modify existing tables
```

### Comment Syntax

```sql
-- Snowflake: supports // and ///
// This is a comment
/// This is also a comment

-- ClickZetta: only supports -- and /* */
-- This is a comment
/* This is also a comment */
```

### Data Type Differences

| ClickZetta | Snowflake | Description |
|---|---|---|
| `STRING` | `VARCHAR` / `TEXT` | ClickZetta recommends STRING |
| `TIMESTAMP` | `TIMESTAMP_LTZ` | Local timezone timestamp |
| `TIMESTAMP_NTZ` | `TIMESTAMP_NTZ` | Without timezone timestamp |
| `JSON` | `VARIANT` | Semi-structured data |
| `ARRAY<T>` | `ARRAY` | ClickZetta requires element type |
| `MAP<K,V>` | `OBJECT` | Key-value pairs |
| `STRUCT<f:T,...>` | `OBJECT` | Struct type |
| `VECTOR(FLOAT, N)` | No native support | Vector type (ClickZetta-specific) |
| `TINYINT` | `NUMBER(3,0)` | 1-byte integer |
| `SMALLINT` | `NUMBER(5,0)` | 2-byte integer |
| No `NUMBER` | `NUMBER(p,s)` | ClickZetta uses `DECIMAL(p,s)` |

### ⚠️ Implicit Type Conversion on Write (Important Difference)

Snowflake allows implicit string conversion to date/boolean types on write; ClickZetta **does not**:

| Operation | Snowflake | ClickZetta |
|---|---|---|
| INSERT string→DATE | ✅ Allowed | ❌ Error, requires `CAST` or `DATE '...'` |
| INSERT string→TIMESTAMP | ✅ Allowed | ❌ Error, requires `CAST` or `TIMESTAMP '...'` |
| INSERT string→BOOLEAN | ✅ Allowed | ❌ Error, requires `TRUE`/`FALSE` or `CAST` |
| INSERT string→INT | ✅ Allowed | ❌ Error, requires `CAST('123' AS INT)` |
| INSERT string→JSON | ✅ Allowed | ❌ Error, requires `PARSE_JSON(...)` or `CAST` |
| UPDATE string→DATE | ✅ Allowed | ❌ Error, requires `CAST` |
| WHERE string=DATE | ✅ Allowed | ✅ Allowed (implicit comparison in queries) |

### Table Creation Syntax Differences

```sql
-- Snowflake: CLUSTER BY
CREATE TABLE orders (id INT, dt DATE)
CLUSTER BY (dt);

-- ClickZetta: CLUSTERED BY + PARTITIONED BY
CREATE TABLE orders (
    id INT,
    dt DATE
)
PARTITIONED BY (dt)
CLUSTERED BY (id) INTO 8 BUCKETS;

-- ClickZetta-specific: Sort Key (inline index)
CREATE TABLE orders (
    id INT,
    amount DECIMAL,
    INDEX amount_bf (amount) USING BLOOM_FILTER
);
```

---

## DML Differences

### INSERT

```sql
-- Both are basically the same; ClickZetta additionally supports:
INSERT OVERWRITE TABLE orders SELECT * FROM staging;  -- overwrite (Hive style)
INSERT INTO orders PARTITION (dt='2024-01-01') VALUES (1, 100);  -- static partition
```

### UPDATE

```sql
-- Snowflake
UPDATE orders SET amount = amount * 1.1 WHERE status = 'VIP';

-- ClickZetta: same syntax, additionally supports ORDER BY + LIMIT
UPDATE orders SET amount = amount * 1.1
WHERE status = 'VIP'
ORDER BY created_at DESC
LIMIT 1000;
```

### MERGE INTO

```sql
-- ClickZetta limitation: WHEN NOT MATCHED can only appear once
-- Snowflake supports multiple WHEN NOT MATCHED

-- ClickZetta MERGE example (⚠️ UPDATE must come before DELETE)
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.amount = s.amount
WHEN MATCHED AND s.action = 'DELETE' THEN DELETE
WHEN NOT MATCHED THEN INSERT (id, amount) VALUES (s.id, s.amount);
```

---

## Query Syntax Differences

### SELECT Extensions

```sql
-- ClickZetta-specific: SELECT * EXCEPT(col)
SELECT * EXCEPT(sensitive_col) FROM users;

-- ClickZetta-specific: GROUP BY ALL (auto-infer grouping columns)
SELECT year, month, SUM(amount)
FROM orders
GROUP BY ALL;

-- Both support: GROUPING SETS / ROLLUP / CUBE
SELECT region, product, SUM(sales)
FROM orders
GROUP BY GROUPING SETS ((region), (product), ());
```

### JSON Queries

```sql
-- Snowflake: VARIANT type, access with :
SELECT data:address:city FROM users;
SELECT data[0]:name FROM users;

-- ClickZetta: JSON type, access with []
SELECT data['address']['city'] FROM users;
SELECT data['phoneNumbers'][0]['number'] FROM users;

-- Both support PARSE_JSON
SELECT parse_json('{"name":"Alice"}')['name'];
```

### LATERAL VIEW (Array Expansion)

```sql
-- ClickZetta (Hive style)
SELECT e.id, s.skill
FROM employees e
LATERAL VIEW EXPLODE(e.skills) s AS skill;

-- Snowflake (uses FLATTEN)
SELECT e.id, f.value::STRING AS skill
FROM employees e,
LATERAL FLATTEN(input => e.skills) f;
```

### QUALIFY (Window Function Filtering)

```sql
-- Both support QUALIFY
SELECT * FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) = 1;
```

### PIVOT / UNPIVOT

```sql
-- Snowflake natively supports PIVOT
SELECT * FROM sales
PIVOT (SUM(amount) FOR month IN ('Jan', 'Feb', 'Mar'));

-- ClickZetta: use CASE WHEN
SELECT
    product,
    SUM(CASE WHEN month = 'Jan' THEN amount END) AS Jan,
    SUM(CASE WHEN month = 'Feb' THEN amount END) AS Feb
FROM sales GROUP BY product;
```

---

## Stream Differences

```sql
-- Snowflake Stream metadata fields
METADATA$ACTION        -- 'INSERT' / 'DELETE'
METADATA$ISUPDATE      -- TRUE/FALSE
METADATA$ROW_ID        -- row unique identifier

-- ClickZetta Table Stream metadata fields
__change_type          -- 'INSERT' / 'UPDATE_BEFORE' / 'UPDATE_AFTER' / 'DELETE'
__commit_version       -- commit version number
__commit_timestamp     -- commit timestamp
```

---

## Dynamic Table Differences

```sql
-- Snowflake Dynamic Table
CREATE DYNAMIC TABLE product_sales
    TARGET_LAG = '1 minutes'
    WAREHOUSE = my_warehouse
AS SELECT ...;

-- ClickZetta Dynamic Table (does not support TARGET_LAG)
CREATE DYNAMIC TABLE product_sales
    REFRESH INTERVAL 1 MINUTE VCLUSTER default_ap
AS SELECT ...;
```

---

## Object Storage (Stage vs Volume)

```sql
-- Snowflake: Stage
CREATE STAGE my_stage
    URL = 's3://bucket/path'
    STORAGE_INTEGRATION = my_integration;

COPY INTO orders FROM @my_stage/data.csv;

-- ClickZetta: Volume
CREATE EXTERNAL VOLUME my_volume
    LOCATION = 'oss://bucket/path'
    USING CONNECTION my_oss_conn;

COPY INTO orders FROM VOLUME my_volume USING CSV;
```

---

## Function Differences

### Date Functions

```sql
-- Snowflake
DATEADD(day, 7, order_date)
DATEDIFF(day, start_date, end_date)
DATE_TRUNC('month', order_date)
TO_DATE('2024-01-01')
CURRENT_TIMESTAMP()

-- ClickZetta (compatible with Hive/Spark style, also supports Snowflake style)
DATEADD(day, 7, order_date)       -- ✅ same Snowflake syntax also supported
DATE_ADD(order_date, 7)           -- or Hive style
DATEDIFF(end_date, start_date)    -- note: parameter order reversed!
DATE_TRUNC('month', order_date)   -- same
TO_DATE('2024-01-01')             -- same
CURRENT_TIMESTAMP()               -- same, also supports NOW()
```

### String Functions

```sql
-- Snowflake
CHARINDEX('sub', str)     -- find substring position
EDITDISTANCE(s1, s2)      -- edit distance
SOUNDEX(str)              -- phonetic similarity
INITCAP(str)              -- capitalize first letter

-- ClickZetta
INSTR(str, 'sub')         -- find substring position (Hive style)
LOCATE('sub', str)        -- also supported
LEVENSHTEIN(s1, s2)       -- edit distance
INITCAP(str)              -- same
```

### Conditional Functions

```sql
-- Snowflake
IFF(condition, true_val, false_val)
ZEROIFNULL(expr)
NULLIFZERO(expr)
DECODE(expr, val1, res1, val2, res2, default)

-- ClickZetta
IF(condition, true_val, false_val)   -- or CASE WHEN
COALESCE(expr, 0)                    -- replaces ZEROIFNULL
NULLIF(expr, 0)                      -- replaces NULLIFZERO
DECODE(expr, val1, res1, ...)        -- supported (compatible)
```

### Aggregate Functions

```sql
-- Snowflake
LISTAGG(col, ',') WITHIN GROUP (ORDER BY col)
ARRAY_AGG(col)
OBJECT_AGG(key, value)
APPROX_COUNT_DISTINCT(col)

-- ClickZetta
GROUP_CONCAT(col ORDER BY col SEPARATOR ',')  -- replaces LISTAGG
ARRAY_AGG(col)                                -- same
MAP_AGG(key, value)                           -- replaces OBJECT_AGG
APPROX_COUNT_DISTINCT(col)                    -- same
```

---

## Permission System Differences

| Concept | ClickZetta | Snowflake |
|---|---|---|
| Top-level container | WORKSPACE | DATABASE |
| Permission objects | VCLUSTER / SCHEMA / TABLE / VIEW | WAREHOUSE / DATABASE / SCHEMA / TABLE |
| Role grant | `GRANT ROLE r TO USER u` | `GRANT ROLE r TO USER u` |
| View permissions | `SHOW GRANTS TO USER u` | `SHOW GRANTS TO USER u` |
| System roles | instance_admin / workspace_admin / workspace_dev / workspace_analyst | ACCOUNTADMIN / SYSADMIN / USERADMIN |
