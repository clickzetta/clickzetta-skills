# ClickZetta Lakehouse vs Spark SQL Differences

> Source: Product documentation + Spark Connector documentation

## Data Type Mapping

| ClickZetta | Spark SQL | Description |
|---|---|---|
| `BOOLEAN` | `BooleanType` | Same |
| `TINYINT` | `ByteType` | 1 byte |
| `SMALLINT` | `ShortType` | 2 bytes |
| `INT` | `IntegerType` | 4 bytes |
| `BIGINT` | `LongType` | 8 bytes |
| `FLOAT` | `FloatType` | 4-byte float |
| `DOUBLE` | `DoubleType` | 8-byte float |
| `DECIMAL(p,s)` | `DecimalType(p,s)` | Exact numeric |
| `STRING` / `VARCHAR` | `StringType` | String |
| `BINARY` | `BinaryType` | Binary |
| `DATE` | `DateType` | Date |
| `TIMESTAMP` | `TimestampType` | Timestamp with timezone |
| `TIMESTAMP_NTZ` | `TimestampNTZType` | Timestamp without timezone |
| `ARRAY<T>` | `ArrayType` | Array |
| `MAP<K,V>` | `MapType` | Key-value pairs |
| `STRUCT<f:T>` | `StructType` | Struct |

---

## Table Creation Syntax Differences

### Partitioning

```sql
-- Spark SQL: PARTITIONED BY
CREATE TABLE orders (id INT, amount DECIMAL, dt STRING)
USING PARQUET
PARTITIONED BY (dt);

-- ClickZetta: same syntax, but no USING clause needed
CREATE TABLE orders (id INT, amount DECIMAL, dt STRING)
PARTITIONED BY (dt);
```

### Bucketing

```sql
-- Spark SQL
CREATE TABLE orders (id INT, amount DECIMAL)
CLUSTERED BY (id) INTO 8 BUCKETS;

-- ClickZetta: same syntax
CREATE TABLE orders (id INT, amount DECIMAL)
CLUSTERED BY (id) INTO 8 BUCKETS;
```

### Table Properties

```sql
-- Spark SQL: TBLPROPERTIES
CREATE TABLE orders (id INT)
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- ClickZetta: PROPERTIES
CREATE TABLE orders (id INT)
PROPERTIES ('data_lifecycle' = '30');  -- data retention in days
```

---

## Query Syntax Differences

### LATERAL VIEW (Array Expansion)

```sql
-- Both have the same syntax (ClickZetta is compatible with Hive/Spark style)
SELECT id, skill
FROM employees
LATERAL VIEW EXPLODE(skills) t AS skill;

-- POSEXPLODE (with position index)
SELECT id, pos, skill
FROM employees
LATERAL VIEW POSEXPLODE(skills) t AS pos, skill;
```

### Window Functions

```sql
-- Both are basically the same
SELECT id, amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn,
    SUM(amount) OVER (PARTITION BY customer_id
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders;
```

### CTE (Common Table Expressions)

```sql
-- Both have the same syntax
WITH
    monthly_sales AS (
        SELECT DATE_TRUNC('month', order_date) AS month, SUM(amount) AS total
        FROM orders GROUP BY 1
    ),
    ranked AS (
        SELECT *, RANK() OVER (ORDER BY total DESC) AS rnk FROM monthly_sales
    )
SELECT * FROM ranked WHERE rnk <= 3;
```

### STRUCT / ARRAY Operations

```sql
-- Spark SQL
SELECT address.city FROM users;                    -- STRUCT field access
SELECT skills[0] FROM employees;                   -- ARRAY index
SELECT EXPLODE(skills) FROM employees;             -- expand array
SELECT TRANSFORM(skills, x -> UPPER(x)) FROM emp; -- array transform

-- ClickZetta (same syntax)
SELECT address.city FROM users;
SELECT skills[0] FROM employees;
SELECT EXPLODE(skills) FROM employees;
SELECT TRANSFORM(skills, x -> UPPER(x)) FROM emp;
```

---

## Function Differences

### Date Functions

```sql
-- Both are basically compatible
DATE_ADD(date, days)
DATE_SUB(date, days)
DATEDIFF(end_date, start_date)   -- note: ClickZetta parameter order is reversed from Snowflake
DATE_TRUNC('month', date)
DATE_FORMAT(date, 'yyyy-MM-dd')
FROM_UNIXTIME(unix_ts)
UNIX_TIMESTAMP(date_str)
```

### String Functions

```sql
-- Both are basically compatible
CONCAT(s1, s2, ...)
CONCAT_WS(',', s1, s2, ...)
SPLIT(str, ',')
REGEXP_EXTRACT(str, pattern, group)
REGEXP_REPLACE(str, pattern, replacement)
INSTR(str, substr)
SUBSTR(str, pos, len)
TRIM(str) / LTRIM(str) / RTRIM(str)
```

### Aggregate Functions

```sql
-- Both are basically compatible
COUNT(*) / COUNT(DISTINCT col)
SUM / AVG / MAX / MIN
COLLECT_LIST(col)    -- Spark: returns array (with duplicates)
COLLECT_SET(col)     -- Spark: returns deduplicated array
ARRAY_AGG(col)       -- ClickZetta: equivalent to COLLECT_LIST
```

---

## ClickZetta-Specific Features (No Spark Equivalent)

```sql
-- 1. VCLUSTER (compute cluster management)
CREATE VCLUSTER my_vc VCLUSTER_TYPE = ANALYTICS VCLUSTER_SIZE = 4;
USE VCLUSTER my_vc;

-- 2. DYNAMIC TABLE (incremental computation)
CREATE DYNAMIC TABLE sales_summary
    REFRESH INTERVAL 5 MINUTE VCLUSTER default
AS SELECT customer_id, SUM(amount) FROM orders GROUP BY 1;

-- 3. TABLE STREAM (CDC change capture)
CREATE TABLE STREAM orders_stream ON TABLE orders
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- 4. PIPE (continuous ingestion)
CREATE PIPE my_pipe
    AS COPY INTO orders FROM VOLUME my_volume USING CSV;

-- 5. VECTOR type (vector search)
CREATE TABLE embeddings (id INT, vec VECTOR(FLOAT, 1024));
SELECT id, cosine_distance(vec, vector(0.1, 0.2, ...)) AS dist
FROM embeddings ORDER BY dist LIMIT 10;

-- 6. Time Travel
SELECT * FROM orders TIMESTAMP AS OF '2024-01-01 00:00:00';
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-01 00:00:00';
UNDROP TABLE orders;

-- 7. SHARE (cross-instance data sharing)
CREATE SHARE my_share;
GRANT SELECT, READ METADATA ON TABLE public.orders TO SHARE my_share;
```

---

## Spark SQL-Specific Features (ClickZetta has no equivalent or different syntax)

```sql
-- 1. Delta Lake-specific syntax (ClickZetta has no equivalent)
OPTIMIZE table_name ZORDER BY (col);   -- ClickZetta has OPTIMIZE but no ZORDER
VACUUM table_name RETAIN 168 HOURS;   -- ClickZetta manages automatically, no manual VACUUM needed

-- 2. SHOW TABLES EXTENDED (ClickZetta has no equivalent)
SHOW TABLES EXTENDED IN schema LIKE 'orders*';

-- 3. DESCRIBE HISTORY (Delta) → ClickZetta uses DESC HISTORY
-- Spark/Delta:
DESCRIBE HISTORY orders;
-- ClickZetta:
DESC HISTORY orders;

-- 4. Generated columns (same syntax)
-- Spark:
CREATE TABLE orders (id INT, year INT GENERATED ALWAYS AS (YEAR(order_date)));
-- ClickZetta (same syntax, also supported):
CREATE TABLE orders (id INT, year INT GENERATED ALWAYS AS (YEAR(order_date)));
```
