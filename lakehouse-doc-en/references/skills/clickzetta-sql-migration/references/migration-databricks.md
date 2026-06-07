# Databricks → ClickZetta Migration Guide

> Covers SQL compatibility issues when migrating from Databricks (Delta Lake) to ClickZetta Lakehouse. All conclusions verified on a real Lakehouse instance.

---

## Object Concept Mapping

| Databricks | ClickZetta | Description |
|---|---|---|
| Catalog (internal data) | WORKSPACE | Top-level namespace, Catalog.Schema.Table ≈ Workspace.Schema.Table |
| Catalog (external data sources) | EXTERNAL CATALOG | Top-level three-layer namespace for federated queries (catalog.schema.table) |
| Database / Schema | SCHEMA | Same |
| Cluster / SQL Warehouse | VCLUSTER | Compute cluster |
| Delta Table (regular) | TABLE | ClickZetta defaults to Parquet storage, supports Iceberg format |
| Delta Table (incremental) | DYNAMIC TABLE | Auto-incremental refresh, replaces DLT Pipeline |
| External Location | STORAGE CONNECTION + EXTERNAL VOLUME | STORAGE CONNECTION handles auth, EXTERNAL VOLUME mounts the path |
| Unity Catalog (metadata governance) | No full equivalent | ClickZetta uses RBAC + SCHEMA permissions for partial governance |
| Unity Catalog (external data federation) | EXTERNAL CATALOG | Supports Hive, Iceberg REST, Databricks Unity Catalog federation |
| Structured Streaming | PIPE + TABLE STREAM | PIPE handles continuous ingestion, TABLE STREAM handles CDC |
| APPLY CHANGES INTO (DLT CDC) | TABLE STREAM + MERGE INTO | Create Stream to capture changes, then consume with MERGE |
| Auto Loader | PIPE (EVENT_NOTIFICATION mode) | File upload triggers loading, only supports OSS/S3 |

---

## DDL Differences

### CREATE TABLE

```sql
-- Databricks Delta Lake
CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id INT,
    amount DECIMAL(18,2),
    status STRING DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT current_timestamp(),
    meta STRUCT<city: STRING, zip: STRING>,
    tags ARRAY<STRING>
)
USING DELTA
PARTITIONED BY (DATE(created_at))
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- ClickZetta equivalent
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT IDENTITY(1),           -- GENERATED ALWAYS AS IDENTITY → IDENTITY
    customer_id INT,
    amount DECIMAL(18,2),
    status STRING DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT current_timestamp(),
    meta STRUCT<city:STRING, zip:STRING>,
    tags ARRAY<STRING>
)
-- No need for USING DELTA (default is Parquet)
PARTITIONED BY (days(created_at));   -- DATE() → days() transform function
-- TBLPROPERTIES → PROPERTIES
-- CDC is implemented via TABLE STREAM, no need for enableChangeDataFeed
```

### Unsupported DDL

```sql
-- ❌ USING DELTA / USING PARQUET (ClickZetta defaults to Parquet, no need to specify)
CREATE TABLE t (...) USING DELTA;
CREATE TABLE t (...) USING PARQUET;

-- ❌ TBLPROPERTIES (use PROPERTIES)
CREATE TABLE t (...) TBLPROPERTIES ('key' = 'value');
-- ✅ ClickZetta
CREATE TABLE t (...) PROPERTIES ('data_lifecycle' = '30');

-- ❌ GENERATED ALWAYS AS IDENTITY (use IDENTITY)
id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1)
-- ✅ ClickZetta
id BIGINT IDENTITY(1)

-- ❌ OPTIMIZE ... ZORDER BY (ClickZetta has OPTIMIZE but no ZORDER)
OPTIMIZE orders ZORDER BY (customer_id, created_at);
-- ✅ ClickZetta (small file compaction only, no ZORDER)
OPTIMIZE orders;

-- ❌ VACUUM (ClickZetta manages storage automatically)
VACUUM orders RETAIN 168 HOURS;
```

---

## ⚠️ Type Conversion on Write (Important Difference)

Databricks allows implicit string conversion; ClickZetta **does not**:

```sql
-- ❌ Works in Databricks, errors in ClickZetta
INSERT INTO t VALUES ('2024-01-15', 'true', '123');

-- ✅ ClickZetta requires explicit conversion
INSERT INTO t VALUES (DATE '2024-01-15', TRUE, CAST('123' AS INT));
```

See [migration-snowflake.md](migration-snowflake.md) for the type conversion table (same rules apply).

---

## DML Differences

### MERGE INTO (WHEN NOT MATCHED BY SOURCE)

```sql
-- Databricks: supports WHEN NOT MATCHED BY SOURCE
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.val = s.val
WHEN NOT MATCHED THEN INSERT (id, val) VALUES (s.id, s.val)
WHEN NOT MATCHED BY SOURCE THEN DELETE;  -- ❌ ClickZetta does not support

-- ClickZetta alternative: two-step operation
-- Step 1: MERGE handles matched and new rows
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.val = s.val
WHEN NOT MATCHED THEN INSERT (id, val) VALUES (s.id, s.val);
-- Step 2: DELETE rows not in source
DELETE FROM target WHERE id NOT IN (SELECT id FROM source);
```

### APPLY CHANGES INTO (CDC)

```sql
-- Databricks: APPLY CHANGES INTO (DLT-specific)
APPLY CHANGES INTO target
FROM source
KEYS (id)
SEQUENCE BY ts
APPLY AS DELETE WHEN operation = 'DELETE';

-- ClickZetta: use TABLE STREAM + MERGE INTO
CREATE TABLE STREAM source_stream ON TABLE source
    WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

MERGE INTO target t
USING source_stream s ON t.id = s.id
WHEN MATCHED AND s.__change_type = 'UPDATE_AFTER' THEN UPDATE SET t.val = s.val
WHEN MATCHED AND s.__change_type = 'DELETE' THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT' THEN INSERT (id, val) VALUES (s.id, s.val);
```

### Transactions

```sql
-- ❌ ClickZetta does not support transaction syntax
BEGIN;
COMMIT;
ROLLBACK;
```

---

## DQL Differences

### QUALIFY (Window Function Filtering)

```sql
-- Both support QUALIFY
SELECT * FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) = 1;
```

### RECURSIVE CTE

```sql
-- Databricks: supports WITH RECURSIVE
WITH RECURSIVE nums AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 5
)
SELECT * FROM nums;

-- ❌ ClickZetta: does not support WITH RECURSIVE (verified)
-- Alternative: use Python/ZettaPark to generate sequences, or pre-build helper tables
```

### STRUCT Named Fields

```sql
-- Databricks: supports named fields
SELECT STRUCT(1 AS id, 'Alice' AS name) AS person;

-- ClickZetta: use named_struct for named fields
SELECT named_struct('id', 1, 'name', 'Alice') AS person;  -- ✅ recommended
SELECT STRUCT(1, 'Alice') AS person;  -- positional parameter syntax, access via person.col1, person.col2
```

---

## Partition Differences

### Partition Functions

```sql
-- Databricks: use column names directly
CREATE TABLE t (...) PARTITIONED BY (year, month);

-- ClickZetta: Iceberg hidden partitions with transform functions
CREATE TABLE t (...) PARTITIONED BY (years(created_at));  -- by year
CREATE TABLE t (...) PARTITIONED BY (months(created_at)); -- by month
CREATE TABLE t (...) PARTITIONED BY (days(created_at));   -- by day
CREATE TABLE t (...) PARTITIONED BY (bucket(16, user_id)); -- by bucket
```

### Partition Pruning

```sql
-- ✅ ClickZetta's YEAR() function in WHERE can trigger partition pruning (engine auto-converts)
SELECT * FROM t WHERE YEAR(dt) = 2024;  -- actually converts to range filter

-- ✅ Preferred approach (explicit range)
SELECT * FROM t WHERE dt >= DATE '2024-01-01' AND dt < DATE '2025-01-01';
```

---

## Delta Lake Feature Comparison

| Delta Lake Feature | ClickZetta Equivalent | Description |
|---|---|---|
| `OPTIMIZE ... ZORDER BY` | `OPTIMIZE table` (no ZORDER) | Only does small file compaction |
| `VACUUM` | Automatic management | No manual VACUUM needed |
| `DESCRIBE HISTORY` | `DESC HISTORY table` | Same functionality |
| `RESTORE TABLE ... VERSION AS OF` | `RESTORE TABLE ... TIMESTAMP AS OF` | Restore by timestamp |
| `Time Travel VERSION AS OF n` | `TIMESTAMP AS OF '...'` | ClickZetta uses timestamp, not version number |
| `enableChangeDataFeed` | TABLE STREAM | Different implementation |
| `MERGE ... WHEN NOT MATCHED BY SOURCE` | Not supported, requires two-step operation | |
| `APPLY CHANGES INTO` | TABLE STREAM + MERGE INTO | |
| `GENERATED ALWAYS AS IDENTITY` | `IDENTITY(seed)` | |
| `TBLPROPERTIES` | `PROPERTIES` | |
| `USING DELTA` | Not needed (default Parquet) | |

---

## Verified Compatibility (Databricks has it, ClickZetta also has it)

- `SEMI JOIN` / `ANTI JOIN` ✅
- `LATERAL VIEW EXPLODE` / `POSEXPLODE` ✅
- `QUALIFY` ✅
- `MERGE INTO` (basic syntax) ✅
- `GROUPING SETS` / `ROLLUP` / `CUBE` ✅
- `WITH CTE` (non-recursive) ✅
- `STRUCT` / `ARRAY` / `MAP` types ✅
- `TRANSFORM` / `FILTER` / `AGGREGATE` higher-order functions ✅
- `ARRAY_AGG` / `COLLECT_LIST` / `COLLECT_SET` ✅
- `REGEXP_EXTRACT` / `REGEXP_REPLACE` ✅
- `DATE_TRUNC` / `DATE_FORMAT` ✅
- `TRY_CAST` ✅
- `IDENTITY` column ✅
- `GENERATED ALWAYS AS (expr)` generated columns ✅
- `DEFAULT` values ✅
- `OPTIMIZE` (small file compaction) ✅
- `DESC HISTORY` ✅
- `RESTORE TABLE ... TIMESTAMP AS OF` ✅
- `UNDROP TABLE` ✅
