# DML Differences vs Snowflake / Databricks / Spark

> Focuses only on the DML (INSERT/UPDATE/DELETE/MERGE/COPY) syntax that **differs** from Snowflake, Databricks, or Spark SQL.
> For the basic ClickZetta DML syntax that works the same as standard SQL, refer to the official ClickZetta Lakehouse documentation.

---

## Critical: Implicit Type Conversion

⚠️ **The single most common migration error.** See [implicit-type-conversion.md](implicit-type-conversion.md) for the full rules table.

Short version: ClickZetta rejects implicit string→date/timestamp/boolean/json/numeric conversion in INSERT/UPDATE. You must use explicit `CAST` or typed literals.

---

## INSERT Differences

### Snowflake → ClickZetta

| Snowflake | ClickZetta | Notes |
|---|---|---|
| `INSERT OVERWRITE` not supported | `INSERT OVERWRITE TABLE t SELECT ...` ✅ | Use TRUNCATE+INSERT in Snowflake |
| No `PARTITION (...)` clause | `INSERT INTO t PARTITION (dt='2024-01-01') VALUES ...` ✅ | Hive-style static partition |
| No dynamic partition syntax | `INSERT INTO t PARTITION (dt) SELECT ..., dt FROM s` ✅ | Hive-style dynamic partition |

### Spark → ClickZetta

INSERT syntax is largely identical. ClickZetta is fully compatible with Spark INSERT.

---

## UPDATE Differences

### Snowflake → ClickZetta

```sql
-- Snowflake: UPDATE ... FROM (JOIN-style update)
UPDATE orders o SET amount = c.discount * o.amount
FROM customers c WHERE o.customer_id = c.id;

-- ClickZetta: use subquery
UPDATE orders SET amount = (
    SELECT discount * orders.amount FROM customers WHERE customers.id = orders.customer_id
) * amount WHERE customer_id IN (SELECT id FROM customers);
```

ClickZetta additionally supports `ORDER BY + LIMIT` in UPDATE, which Snowflake does not:

```sql
-- ClickZetta-only: batch update
UPDATE orders SET status = 'archived'
WHERE created_at < '2020-01-01'
ORDER BY created_at ASC
LIMIT 10000;
```

### Spark → ClickZetta

Spark SQL itself does not support UPDATE (only Delta Lake does). ClickZetta natively supports UPDATE on all tables.

---

## DELETE Differences

### Spark → ClickZetta

Spark SQL itself does not support DELETE (only Delta Lake does). ClickZetta natively supports DELETE on all tables.

Snowflake DELETE syntax is essentially identical to ClickZetta.

---

## MERGE INTO: Important Limitations

### Multiple WHEN NOT MATCHED clauses

```sql
-- ❌ Snowflake supports multiple WHEN NOT MATCHED — ClickZetta does NOT
MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED AND s.type = 'A' THEN INSERT ...
WHEN NOT MATCHED AND s.type = 'B' THEN INSERT ...;

-- ✅ ClickZetta: only one WHEN NOT MATCHED — combine logic with CASE
MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED THEN INSERT (id, val) VALUES (
    s.id,
    CASE s.type WHEN 'A' THEN ... WHEN 'B' THEN ... END
);
```

### WHEN NOT MATCHED BY SOURCE (Databricks Delta Lake)

```sql
-- ❌ Databricks supports WHEN NOT MATCHED BY SOURCE — ClickZetta does NOT
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE ...
WHEN NOT MATCHED THEN INSERT ...
WHEN NOT MATCHED BY SOURCE THEN DELETE;  -- ❌ unsupported

-- ✅ ClickZetta: split into two operations
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.val = s.val
WHEN NOT MATCHED THEN INSERT (id, val) VALUES (s.id, s.val);

DELETE FROM target WHERE id NOT IN (SELECT id FROM source);
```

### Order of Multiple WHEN MATCHED clauses

```sql
-- ⚠️ ClickZetta requires UPDATE clauses BEFORE DELETE clauses
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED AND s.is_deleted = 0 THEN UPDATE SET ...   -- UPDATE first
WHEN MATCHED AND s.is_deleted = 1 THEN DELETE          -- DELETE after
WHEN NOT MATCHED THEN INSERT ...;
```

In Snowflake/Databricks, DELETE may appear before UPDATE.

---

## Transactions: Not Supported

```sql
-- ❌ All of these are unsupported in ClickZetta
BEGIN;
BEGIN TRANSACTION;
START TRANSACTION;
COMMIT;
ROLLBACK;

-- ✅ Use MERGE INTO for atomic UPSERT
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
```

For multi-statement atomicity, design idempotent operations or use the `__commit_version` from Time Travel for compensating reads.

---

## Bulk Load: Stage → Volume, COPY INTO Differences

### Snowflake → ClickZetta

```sql
-- Snowflake
COPY INTO orders
FROM @my_stage/data/2024/
FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1)
PATTERN = '.*\.csv';

-- ClickZetta
COPY INTO orders
FROM VOLUME my_oss_volume
USING CSV
OPTIONS('header' = 'true', 'sep' = ',')
SUBDIRECTORY 'data/2024/'
REGEXP '.*\.csv';
```

| Snowflake | ClickZetta |
|---|---|
| `@stage_name` | `VOLUME volume_name` |
| `FILE_FORMAT = (TYPE = CSV ...)` | `USING CSV OPTIONS(...)` |
| `PATTERN = '...'` | `REGEXP '...'` |
| `FILES = ('a.csv','b.csv')` | `FILES('a.csv','b.csv')` |

### Export

```sql
-- Snowflake
COPY INTO @my_stage FROM orders FILE_FORMAT = (TYPE = PARQUET);

-- ClickZetta
COPY INTO VOLUME my_oss_volume
SUBDIRECTORY 'export/orders/'
FROM orders
USING PARQUET;
```

---

## Other ClickZetta-Specific DML Notes

These are ClickZetta features without direct Snowflake/Databricks/Spark equivalents:

- `INSERT INTO ... PARTITION (col)` — Hive-style dynamic partition (Snowflake auto-clusters via CLUSTER BY)
- `COPY OVERWRITE INTO` — atomic overwrite-on-load
- `RESTORE TABLE ... TO TIMESTAMP AS OF ...` — Time Travel restore (Snowflake uses different syntax, Delta uses VERSION AS OF)

For the full DML syntax of these features, refer to ClickZetta Lakehouse documentation.
