# DML Complete Syntax Reference

> Based on ClickZetta Lakehouse product documentation, with Snowflake / Spark SQL difference annotations

---

## ⚠️ Implicit Type Conversion Rules (Applies to INSERT / UPDATE)

**ClickZetta strictly prohibits implicit type conversion for write operations (INSERT/UPDATE); explicit CAST is required.**
However, implicit conversion is allowed in SELECT/WHERE/expressions.

### Complete Rules Table (Verified)

| Target Column Type | Written Value | INSERT/UPDATE | WHERE/SELECT |
|---|---|---|---|
| `DATE` | `'2024-01-15'` (string) | ❌ Error | ✅ Allowed |
| `TIMESTAMP` | `'2024-01-15 12:00:00'` (string) | ❌ Error | ✅ Allowed |
| `BOOLEAN` | `'true'` / `'false'` (string) | ❌ Error | ✅ Allowed |
| `BOOLEAN` | `1` / `0` (integer) | ❌ Error | ✅ Allowed |
| `JSON` | `'{"k":1}'` (string) | ❌ Error | ✅ Allowed |
| `INT` / `BIGINT` | `'123'` (string) | ❌ Error | ✅ Allowed |
| `BIGINT` | `100` (INT) | ✅ Allowed | ✅ Allowed |
| `DOUBLE` | `1.5` (FLOAT) | ✅ Allowed | ✅ Allowed |
| `BIGINT` | `1.5` (FLOAT) | ✅ Allowed (truncated) | ✅ Allowed |

### Correct Syntax for Each Type

```sql
-- DATE (the following are equivalent)
INSERT INTO t VALUES (CAST('2024-01-15' AS DATE));
INSERT INTO t VALUES (DATE '2024-01-15');
INSERT INTO t VALUES (TO_DATE('2024-01-15'));
INSERT INTO t VALUES (DATE('2024-01-15'));   -- function form, also supported

-- TIMESTAMP (the following are equivalent)
INSERT INTO t VALUES (CAST('2024-01-15 12:00:00' AS TIMESTAMP));
INSERT INTO t VALUES (TIMESTAMP '2024-01-15 12:00:00');
INSERT INTO t VALUES (TO_TIMESTAMP('2024-01-15 12:00:00'));
INSERT INTO t VALUES (TIMESTAMP('2024-01-15 12:00:00'));  -- function form, also supported
INSERT INTO t VALUES (CURRENT_TIMESTAMP());
INSERT INTO t VALUES (CURRENT_DATE() - INTERVAL 7 DAY);

-- BOOLEAN (only accepts TRUE/FALSE literals or CAST)
INSERT INTO t VALUES (TRUE);
INSERT INTO t VALUES (FALSE);
INSERT INTO t VALUES (CAST(1 AS BOOLEAN));
INSERT INTO t VALUES (CAST('true' AS BOOLEAN));

-- JSON (must use PARSE_JSON or CAST)
INSERT INTO t VALUES (PARSE_JSON('{"key":"value"}'));
INSERT INTO t VALUES (CAST('{"key":"value"}' AS JSON));

-- INT/BIGINT (strings must be CAST)
INSERT INTO t VALUES (CAST('123' AS INT));
INSERT INTO t VALUES (CAST('456' AS BIGINT));
```

### UPDATE Has the Same Restrictions

```sql
-- ❌ UPDATE also does not allow implicit string conversion
UPDATE orders SET dt = '2024-06-01' WHERE id = 1;       -- Error
UPDATE orders SET flag = 0 WHERE id = 1;                 -- Error

-- ✅ Must explicitly convert
UPDATE orders SET dt = CAST('2024-06-01' AS DATE) WHERE id = 1;
UPDATE orders SET flag = CAST(0 AS BOOLEAN) WHERE id = 1;
```

### Strings Can Be Implicitly Compared in WHERE

```sql
-- ✅ Strings can be compared with date/numeric in WHERE
SELECT * FROM orders WHERE dt = '2024-01-15';
SELECT * FROM orders WHERE dt >= '2024-01-01' AND dt < '2025-01-01';
SELECT * FROM orders WHERE id = '123';
```

**Differences from Snowflake / Spark:**
- Snowflake / Spark: Strings can be implicitly converted to date/boolean/numeric types during INSERT/UPDATE
- ClickZetta: **Explicit conversion required** for writes, implicit comparison allowed in queries

> **Also applies to RESTORE TABLE**: `RESTORE TABLE t TO TIMESTAMP AS OF '2024-01-15'` will error; must use `CAST('2024-01-15 10:00:00' AS TIMESTAMP)` or a full millisecond timestamp string.

---

## INSERT

```sql
-- Append (single row)
INSERT INTO orders VALUES (1, 101, 100.0, 'pending');
INSERT INTO orders (id, customer_id, amount) VALUES (1, 101, 100.0);

-- Append (multiple rows)
INSERT INTO orders VALUES
    (1, 101, 100.0, 'pending'),
    (2, 102, 200.0, 'completed');

-- Append from query
INSERT INTO orders SELECT * FROM staging_orders WHERE status = 'new';

-- Overwrite entire table
INSERT OVERWRITE TABLE orders SELECT * FROM new_orders;

-- Overwrite specific partition (static partition)
INSERT OVERWRITE TABLE orders PARTITION (dt = '2024-01-01')
SELECT id, amount FROM staging WHERE dt = '2024-01-01';

-- Dynamic partition (automatically partitions based on data values)
INSERT INTO orders PARTITION (dt)
SELECT id, amount, dt FROM staging;

-- Not recommended for large data volumes with VALUES; suitable for testing
```

**Differences from Snowflake:**
- Snowflake has no `INSERT OVERWRITE`; use `TRUNCATE` + `INSERT` or `MERGE` instead
- Snowflake has no `PARTITION` clause (Snowflake uses CLUSTER BY for automatic management)
- ClickZetta supports Hive-style dynamic partitioning

**Differences from Spark SQL:**
- Syntax is basically the same; ClickZetta is fully compatible with Spark INSERT syntax

---

## UPDATE

```sql
-- Basic update
UPDATE orders SET status = 'cancelled' WHERE id = 123;

-- Multi-column update
UPDATE orders
SET status = 'completed', updated_at = current_timestamp()
WHERE id = 123;

-- Subquery update
UPDATE orders
SET amount = amount * 1.1
WHERE customer_id IN (
    SELECT id FROM customers WHERE tier = 'VIP'
);

-- With ORDER BY + LIMIT (batch update)
UPDATE orders
SET status = 'archived'
WHERE created_at < '2020-01-01'
ORDER BY created_at ASC
LIMIT 10000;
```

**Differences from Snowflake:**
- Snowflake `UPDATE ... FROM` syntax (JOIN update) → ClickZetta uses subquery instead
- ClickZetta additionally supports `ORDER BY + LIMIT` (Snowflake does not)

**Differences from Spark SQL:**
- Spark SQL does not support `UPDATE` (Delta Lake does); ClickZetta natively supports it

---

## DELETE

```sql
-- Basic delete
DELETE FROM orders WHERE id = 123;

-- Conditional delete
DELETE FROM orders WHERE created_at < '2020-01-01';

-- Subquery delete
DELETE FROM orders
WHERE order_id IN (
    SELECT order_id FROM order_details WHERE status = 'cancelled'
);

-- Delete all rows (equivalent to TRUNCATE, but records version)
DELETE FROM orders WHERE 1 = 1;
```

**Differences from Snowflake:**
- Syntax is basically the same

**Differences from Spark SQL:**
- Spark SQL does not support `DELETE` (Delta Lake does); ClickZetta natively supports it

---

## MERGE INTO (UPSERT)

```sql
-- Standard MERGE (⚠️ when multiple WHEN MATCHED clauses, UPDATE must come before DELETE)
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED AND s.is_deleted = 0 THEN UPDATE SET   -- UPDATE first
    t.amount = s.amount,
    t.status = s.status,
    t.updated_at = current_timestamp()
WHEN MATCHED AND s.is_deleted = 1 THEN DELETE        -- DELETE second
WHEN NOT MATCHED THEN INSERT (id, amount, status, created_at)
    VALUES (s.id, s.amount, s.status, current_timestamp());

-- Multiple WHEN MATCHED (UPDATE must come before DELETE)
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED AND s.action = 'update' THEN UPDATE SET t.amount = s.amount
WHEN MATCHED AND s.action = 'delete' THEN DELETE
WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.amount);

-- MERGE from subquery
MERGE INTO orders t
USING (
    SELECT id, SUM(amount) AS total FROM line_items GROUP BY id
) s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.total = s.total
WHEN NOT MATCHED THEN INSERT (id, total) VALUES (s.id, s.total);
```

**⚠️ ClickZetta MERGE Limitations:**
1. `WHEN NOT MATCHED` can only appear **once** (Snowflake supports multiple)
2. When multiple `WHEN MATCHED` clauses exist, `UPDATE` must come before `DELETE`
3. A single source row cannot match multiple target rows (otherwise errors)

**Differences from Snowflake:**
- Snowflake supports multiple `WHEN NOT MATCHED`; ClickZetta only supports one
- Snowflake `MERGE ... WHEN NOT MATCHED BY SOURCE THEN DELETE`; ClickZetta does not support
- Syntax structure is basically the same

**Differences from Spark SQL:**
- Spark SQL (Delta Lake) supports `WHEN NOT MATCHED BY SOURCE`; ClickZetta does not support
- Syntax structure is basically the same

---

## COPY INTO (Bulk Import/Export)

```sql
-- Import from Volume
COPY INTO orders
FROM VOLUME my_oss_volume
USING CSV
OPTIONS('header' = 'true', 'sep' = ',')
SUBDIRECTORY 'data/2024/';

-- Import from Volume (Parquet)
COPY INTO orders
FROM VOLUME my_oss_volume
USING PARQUET
FILES('part-00001.parquet', 'part-00002.parquet');

-- Regex file matching
COPY INTO orders
FROM VOLUME my_oss_volume
USING PARQUET
REGEXP '.*2024-0[1-6].parquet';

-- Overwrite import
COPY OVERWRITE INTO orders
FROM VOLUME my_oss_volume
USING CSV OPTIONS('header' = 'true');

-- Export to Volume
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/orders/'
FROM orders
USING PARQUET;

-- Export query results
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/2024/'
FROM (SELECT * FROM orders WHERE YEAR(created_at) = 2024)
USING CSV OPTIONS('header' = 'true');
```

**Differences from Snowflake:**
- Snowflake `COPY INTO t FROM @stage/path/file.csv` → ClickZetta `COPY INTO t FROM VOLUME v USING CSV`
- Snowflake Stage uses `@` prefix; ClickZetta Volume uses object name
- Snowflake `COPY INTO @stage FROM t` → ClickZetta `COPY INTO VOLUME v FROM t`
- Snowflake supports `PATTERN = '.*\.csv'`; ClickZetta uses `REGEXP`
- Snowflake `FILE_FORMAT = (TYPE = CSV)` → ClickZetta `USING CSV OPTIONS(...)`
