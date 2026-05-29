# DDL Complete Syntax Reference

> Based on ClickZetta Lakehouse product documentation, with Snowflake / Spark SQL difference annotations

---

## SCHEMA Operations

```sql
-- Create
CREATE SCHEMA IF NOT EXISTS my_schema COMMENT 'description';

-- Alter
ALTER SCHEMA my_schema RENAME TO new_schema;
ALTER SCHEMA my_schema SET COMMENT 'new comment';

-- Drop (cascades all objects)
DROP SCHEMA IF EXISTS my_schema;

-- Show
SHOW SCHEMAS;
SHOW SCHEMAS EXTENDED;                          -- includes type column (MANAGED/EXTERNAL)
SHOW SCHEMAS LIKE 'sales%';
SHOW SCHEMAS WHERE schema_name = 'public';

-- Switch
USE SCHEMA my_schema;
USE my_schema;                                  -- SCHEMA keyword is optional
```

**Differences from Snowflake:**
- Snowflake uses `USE DATABASE` + `USE SCHEMA`; ClickZetta has no DATABASE layer, use `USE SCHEMA` directly
- Snowflake supports `CREATE OR REPLACE SCHEMA`; ClickZetta does not, use `IF NOT EXISTS`

---

## TABLE Operations

### CREATE TABLE

```sql
-- Basic table creation
CREATE TABLE IF NOT EXISTS orders (
    id          BIGINT,
    customer_id INT,
    amount      DECIMAL(18, 2)  NOT NULL,
    status      STRING          DEFAULT 'pending',
    created_at  TIMESTAMP,
    tags        ARRAY<STRING>,
    meta        JSON,
    COMMENT 'Orders table'
);

-- Primary key table (ENABLE VALIDATE RELY: SQL writes also deduplicate)
CREATE TABLE pk_orders (
    id     BIGINT PRIMARY KEY,
    amount DECIMAL(18, 2)
);

-- Primary key table (DISABLE NOVALIDATE RELY: only real-time writes deduplicate, SQL writes do not)
CREATE TABLE cdc_orders (
    id     BIGINT PRIMARY KEY DISABLE NOVALIDATE RELY,
    amount DECIMAL(18, 2)
);

-- Auto-increment column (BIGINT only, not guaranteed sequential)
CREATE TABLE auto_id_table (
    id  BIGINT IDENTITY(1),    -- starts from 1
    col STRING
);

-- Generated column (deterministic expression, cannot be manually inserted)
CREATE TABLE orders_with_year (
    id         BIGINT,
    created_at TIMESTAMP,
    year       INT GENERATED ALWAYS AS (YEAR(created_at))
);

-- Default values (supports non-deterministic functions)
CREATE TABLE t_default (
    id         INT,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    status     STRING    DEFAULT 'active',
    score      DOUBLE    DEFAULT random()
);

-- Partitioned table (Iceberg hidden partitions)
CREATE TABLE orders_partitioned (
    id         BIGINT,
    amount     DECIMAL(18, 2),
    created_at TIMESTAMP
)
PARTITIONED BY (days(created_at));             -- partition by day

-- Partition transform functions
-- years(col)   months(col)   days(col)   hours(col)
-- bucket(N, col)   truncate(col, W)

-- Bucketed table
CREATE TABLE orders_bucketed (
    id         BIGINT,
    customer_id INT,
    amount     DECIMAL(18, 2)
)
CLUSTERED BY (customer_id)
SORTED BY (id ASC)
INTO 16 BUCKETS;

-- Data retention period
CREATE TABLE orders (id BIGINT)
PROPERTIES ('data_lifecycle' = '30');          -- retain for 30 days

-- CTAS (Create Table As Select)
CREATE TABLE orders_copy AS
SELECT * FROM orders WHERE status = 'completed';

-- External table (maps to object storage)
CREATE EXTERNAL TABLE ext_orders (
    id     BIGINT,
    amount DECIMAL(18, 2)
)
LOCATION 'oss://bucket/orders/'
STORED AS PARQUET;
```

**Differences from Snowflake:**
- Snowflake `CREATE OR REPLACE TABLE` → ClickZetta `CREATE TABLE IF NOT EXISTS`
- Snowflake `CLUSTER BY (col)` → ClickZetta `CLUSTERED BY (col) INTO N BUCKETS`
- Snowflake `AUTOINCREMENT` → ClickZetta `IDENTITY[(seed)]`
- Snowflake `TRANSIENT TABLE` → ClickZetta has no equivalent (use `data_lifecycle` to control retention)
- Snowflake `TEMPORARY TABLE` → ClickZetta has no temporary table concept
- Snowflake `COPY GRANTS` → ClickZetta does not support

**Differences from Spark SQL:**
- Spark `USING PARQUET` → ClickZetta does not need it (default is Parquet)
- Spark `TBLPROPERTIES` → ClickZetta `PROPERTIES`
- Spark `LOCATION` external table syntax is basically the same

### ALTER TABLE

```sql
-- Rename
ALTER TABLE orders RENAME TO orders_v2;

-- Comment
ALTER TABLE orders SET COMMENT 'new comment';

-- Data retention period
ALTER TABLE orders SET PROPERTIES ('data_retention_days' = '7');

-- Add column
ALTER TABLE orders ADD COLUMN region STRING AFTER status;
ALTER TABLE orders ADD COLUMN region STRING FIRST;

-- Add nested field in complex types
ALTER TABLE t ADD COLUMN address.zip STRING;           -- STRUCT nested
ALTER TABLE t ADD COLUMN items.ELEMENT.price DOUBLE;   -- ARRAY<STRUCT> nested

-- Alter column type (limited)
ALTER TABLE orders ALTER COLUMN amount TYPE DOUBLE;

-- Rename column
ALTER TABLE orders RENAME COLUMN old_col TO new_col;

-- Drop column
ALTER TABLE orders DROP COLUMN unnecessary_col;

-- Alter column comment
ALTER TABLE orders ALTER COLUMN amount COMMENT 'Order amount';

-- Add index (tables with ARRAY/JSON columns must add separately)
-- ⚠️ Index syntax: BLOOMFILTER (not USING BLOOM_FILTER)
CREATE BLOOMFILTER INDEX IF NOT EXISTS id_bf ON TABLE orders(id);
CREATE BLOOMFILTER INDEX IF NOT EXISTS name_bf ON TABLE orders(name)
    PROPERTIES ('analyzer' = 'ngram', 'n' = '3');  -- ngram tokenizer

-- Inverted index
CREATE INVERTED INDEX IF NOT EXISTS content_inv ON TABLE articles(content);

-- Vector index (inline at table creation)
-- See CREATE TABLE examples

-- Drop index (⚠️ does not need ON table_name)
DROP INDEX IF EXISTS id_bf;
DROP INDEX id_bf;
```

**Differences from Snowflake:**
- Snowflake `ALTER TABLE ... ADD COLUMN` can only add to the end; ClickZetta supports `FIRST/AFTER/BEFORE`
- Snowflake does not support `DROP COLUMN` (requires table rebuild); ClickZetta supports it
- Snowflake has no BLOOM_FILTER/INVERTED/VECTOR indexes

### DROP / TRUNCATE TABLE

```sql
-- Drop table (can be recovered with UNDROP)
DROP TABLE IF EXISTS orders;
DROP TABLE my_schema.orders;

-- Truncate table (preserves structure)
TRUNCATE TABLE orders;
TRUNCATE TABLE IF EXISTS orders;               -- ✅ supports IF EXISTS

-- Truncate specific partition
TRUNCATE TABLE orders PARTITION (dt = '2024-01-01');
TRUNCATE TABLE orders PARTITION (dt > '2024-01-01');
TRUNCATE TABLE orders PARTITION (dt >= '2024-01-01' AND dt < '2024-02-01');
```

**Differences from Snowflake:**
- Snowflake `TRUNCATE TABLE` does not support partition conditions; ClickZetta does
- Snowflake `DROP TABLE ... PURGE` deletes immediately; ClickZetta can UNDROP within retention period

---

## VIEW Operations

```sql
-- Create view
CREATE VIEW IF NOT EXISTS order_summary AS
SELECT customer_id, COUNT(*) AS cnt, SUM(amount) AS total
FROM orders GROUP BY customer_id;

-- Replace view (ClickZetta supports OR REPLACE, same as Snowflake)
CREATE OR REPLACE VIEW order_summary AS
SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id;

-- With column aliases and comments
CREATE VIEW order_summary (cust_id COMMENT 'Customer ID', total COMMENT 'Total amount')
COMMENT 'Order summary view'
AS SELECT customer_id, SUM(amount) FROM orders GROUP BY 1;

-- Drop
DROP VIEW IF EXISTS order_summary;

-- Show
SHOW TABLES WHERE is_view = true;
SHOW TABLES IN my_schema WHERE is_view = true;
```

**Note:** ClickZetta's `CREATE OR REPLACE VIEW` is the same as Snowflake, but `CREATE OR REPLACE TABLE` is not supported.

---

## INDEX Operations

```sql
-- Show indexes
SHOW INDEX FROM table_name;
SHOW INDEX FROM my_schema.table_name;

-- Show index details
DESC INDEX index_name;
DESC INDEX EXTENDED index_name;

-- Build index on existing data (vector and inverted indexes only, not Bloom Filter)
BUILD INDEX index_name ON table_name;
BUILD INDEX index_name ON table_name WHERE partition_col = '2024-01-01';
```

---

## Viewing Object Information

```sql
-- Table structure
DESC table_name;
DESC EXTENDED table_name;                      -- includes size, record count, etc.
DESCRIBE TABLE table_name;                     -- same as DESC

-- Column information
SHOW COLUMNS IN table_name;
SHOW COLUMNS FROM table_name IN schema_name;

-- Create table statement
SHOW CREATE TABLE table_name;

-- Table list
SHOW TABLES;
SHOW TABLES IN my_schema;
SHOW TABLES LIKE 'order%';
SHOW TABLES WHERE is_view = false AND is_materialized_view = false;
SHOW TABLES WHERE is_dynamic = true;
SHOW TABLES WHERE is_external = true;

-- Partition information
SHOW PARTITIONS table_name;
SHOW PARTITIONS EXTENDED table_name;           -- includes file count, size, modification time
SHOW PARTITIONS table_name PARTITION (dt = '2024-01-01');
SHOW PARTITIONS table_name WHERE total_rows > 1000;

-- History versions
DESC HISTORY table_name;
SHOW TABLES HISTORY;                           -- includes deleted tables
```

---

## SYNONYM Operations

```sql
-- Create synonym for a table (cross-schema access)
CREATE SYNONYM my_orders FOR TABLE other_schema.orders;

-- Create synonym for a Volume
CREATE SYNONYM my_vol FOR VOLUME other_schema.data_volume;

-- Create synonym for a function
CREATE SYNONYM my_func FOR FUNCTION other_schema.udf_name;

-- Show synonyms
SHOW SYNONYMS;
SHOW SYNONYMS IN my_schema;
SHOW SYNONYMS LIKE 'my_%';

-- Drop synonym (must specify object type)
DROP SYNONYM my_orders FOR TABLE;
DROP SYNONYM my_vol FOR VOLUME;
DROP SYNONYM my_func FOR FUNCTION;
```

> Supported object types for synonyms: TABLE (including regular tables, Table Streams, materialized views, dynamic tables), VOLUME, FUNCTION.
> Use cases: cross-schema access, data consistency maintenance, application layer decoupling.

---

## Time Travel & Data Recovery

```sql
-- Query historical version
SELECT * FROM orders TIMESTAMP AS OF '2024-01-01 00:00:00';
SELECT * FROM orders TIMESTAMP AS OF CURRENT_TIMESTAMP() - INTERVAL 12 HOURS;
SELECT * FROM orders TIMESTAMP AS OF CAST('2024-01-01' AS TIMESTAMP);

-- Restore table to historical version (table not deleted)
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-01 00:00:00';

-- Restore deleted table
UNDROP TABLE orders;
UNDROP TABLE my_schema.orders;

-- Set retention period (0-90 days, default 1 day)
ALTER TABLE orders SET PROPERTIES ('data_retention_days' = '7');
```

**Differences from Snowflake:**
- Snowflake `AT (TIMESTAMP => ...)` → ClickZetta `TIMESTAMP AS OF ...`
- Snowflake `BEFORE (STATEMENT => ...)` → ClickZetta does not support rollback by statement_id
- Snowflake `UNDROP TABLE` → ClickZetta same
- Snowflake default retention 1 day (Enterprise 90 days); ClickZetta default 1 day, max 90 days
