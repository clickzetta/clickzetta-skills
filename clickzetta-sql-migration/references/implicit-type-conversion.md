# Implicit Type Conversion: Migration Pitfall

> **Why this matters for migration**: Snowflake, Databricks, and Spark all allow implicit string conversion in INSERT/UPDATE. ClickZetta does not. This is the #1 cause of unexpected errors when copying SQL from those systems.

---

## The Rule

ClickZetta strictly prohibits implicit type conversion in **write operations** (INSERT/UPDATE). Explicit `CAST` is required.
However, implicit conversion **is allowed** in SELECT/WHERE expressions.

---

## Behavior Comparison Table

| Target Column Type | Written Value | Snowflake | Databricks | Spark | ClickZetta INSERT/UPDATE | ClickZetta WHERE |
|---|---|---|---|---|---|---|
| `DATE` | `'2024-01-15'` (string) | ✅ implicit | ✅ implicit | ✅ implicit | ❌ Error | ✅ Allowed |
| `TIMESTAMP` | `'2024-01-15 12:00:00'` (string) | ✅ implicit | ✅ implicit | ✅ implicit | ❌ Error | ✅ Allowed |
| `BOOLEAN` | `'true'` / `'false'` (string) | ✅ implicit | ✅ implicit | ✅ implicit | ❌ Error | ✅ Allowed |
| `BOOLEAN` | `1` / `0` (integer) | ✅ implicit | ❌ | ❌ | ❌ Error | ✅ Allowed |
| `JSON` / `VARIANT` | `'{"k":1}'` (string) | ✅ implicit | N/A | N/A | ❌ Error | ✅ Allowed |
| `INT` / `BIGINT` | `'123'` (string) | ✅ implicit | ✅ implicit | ✅ implicit | ❌ Error | ✅ Allowed |
| `BIGINT` | `100` (INT) | ✅ | ✅ | ✅ | ✅ Allowed | ✅ Allowed |
| `DOUBLE` | `1.5` (FLOAT) | ✅ | ✅ | ✅ | ✅ Allowed | ✅ Allowed |
| `BIGINT` | `1.5` (FLOAT) | ✅ truncated | ✅ truncated | ✅ truncated | ✅ Allowed (truncated) | ✅ Allowed |

---

## Migration Pattern: How to Rewrite

```sql
-- ❌ Snowflake / Databricks / Spark style (errors in ClickZetta)
INSERT INTO orders VALUES (1, '2024-01-15', 'true', '{"k":1}', '123');

-- ✅ ClickZetta-compatible
INSERT INTO orders VALUES (
    1,
    DATE '2024-01-15',                       -- or CAST('2024-01-15' AS DATE)
    TRUE,                                    -- or CAST('true' AS BOOLEAN)
    PARSE_JSON('{"k":1}'),                   -- or CAST(... AS JSON)
    CAST('123' AS INT)
);
```

### DATE Column

```sql
-- All equivalent and correct
INSERT INTO t VALUES (CAST('2024-01-15' AS DATE));
INSERT INTO t VALUES (DATE '2024-01-15');
INSERT INTO t VALUES (TO_DATE('2024-01-15'));
INSERT INTO t VALUES (DATE('2024-01-15'));   -- function form
```

### TIMESTAMP Column

```sql
-- All equivalent and correct
INSERT INTO t VALUES (CAST('2024-01-15 12:00:00' AS TIMESTAMP));
INSERT INTO t VALUES (TIMESTAMP '2024-01-15 12:00:00');
INSERT INTO t VALUES (TO_TIMESTAMP('2024-01-15 12:00:00'));
INSERT INTO t VALUES (TIMESTAMP('2024-01-15 12:00:00'));  -- function form
INSERT INTO t VALUES (CURRENT_TIMESTAMP());
INSERT INTO t VALUES (CURRENT_DATE() - INTERVAL 7 DAY);
```

### BOOLEAN Column

```sql
-- Only TRUE/FALSE literals or explicit CAST
INSERT INTO t VALUES (TRUE);
INSERT INTO t VALUES (FALSE);
INSERT INTO t VALUES (CAST(1 AS BOOLEAN));
INSERT INTO t VALUES (CAST('true' AS BOOLEAN));
```

### JSON Column

```sql
-- Must use PARSE_JSON or CAST
INSERT INTO t VALUES (PARSE_JSON('{"key":"value"}'));
INSERT INTO t VALUES (CAST('{"key":"value"}' AS JSON));
```

### INT/BIGINT Column

```sql
-- Strings must be CAST
INSERT INTO t VALUES (CAST('123' AS INT));
INSERT INTO t VALUES (CAST('456' AS BIGINT));
```

---

## UPDATE Has the Same Restrictions

```sql
-- ❌ UPDATE also rejects implicit string conversion
UPDATE orders SET dt = '2024-06-01' WHERE id = 1;       -- Error
UPDATE orders SET flag = 0 WHERE id = 1;                 -- Error (BOOLEAN column)

-- ✅ Must explicitly convert
UPDATE orders SET dt = CAST('2024-06-01' AS DATE) WHERE id = 1;
UPDATE orders SET flag = CAST(0 AS BOOLEAN) WHERE id = 1;
```

---

## WHERE Clause Allows Implicit Comparison

This is **not** a write operation, so implicit conversion still works:

```sql
-- ✅ All allowed in WHERE
SELECT * FROM orders WHERE dt = '2024-01-15';
SELECT * FROM orders WHERE dt >= '2024-01-01' AND dt < '2025-01-01';
SELECT * FROM orders WHERE id = '123';
```

---

## Also Applies to RESTORE TABLE

```sql
-- ❌ Errors
RESTORE TABLE t TO TIMESTAMP AS OF '2024-01-15';

-- ✅ Use explicit cast
RESTORE TABLE t TO TIMESTAMP AS OF CAST('2024-01-15 10:00:00' AS TIMESTAMP);
```

---

## Quick Migration Checklist

When porting INSERT/UPDATE statements from Snowflake/Databricks/Spark, search for and fix:

1. String literals being inserted into DATE columns → wrap with `DATE '...'` or `CAST(... AS DATE)`
2. String literals being inserted into TIMESTAMP columns → wrap with `TIMESTAMP '...'` or `CAST(... AS TIMESTAMP)`
3. String `'true'` / `'false'` or integer `1` / `0` for BOOLEAN columns → use `TRUE` / `FALSE` literals
4. String JSON for VARIANT/JSON columns → wrap with `PARSE_JSON(...)`
5. String numerics for INT/BIGINT columns → wrap with `CAST(... AS INT)`
