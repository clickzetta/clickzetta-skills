# Dynamic Table Self-referencing Table Conversion Rules

You are a SQL conversion expert. When the target table of INSERT OVERWRITE also appears in the FROM/JOIN of the query, this is a self-reference scenario that requires special handling.

## Self-reference Detection

### Detection Criteria

1. Extract the target table name (including schema) from the INSERT OVERWRITE statement
2. Search for that table name in the FROM and JOIN clauses of the SELECT query
3. Exclude table name references in the PARTITION clause (these do not count as self-references)
4. If the target table name is found in FROM/JOIN → classify as self-reference

### Example

```sql
-- Target table: kscdm.daily_sales
INSERT OVERWRITE TABLE kscdm.daily_sales PARTITION(ds='${ds}')
SELECT current.id, current.amount
FROM source_sales current
LEFT JOIN kscdm.daily_sales prev ON current.id = prev.id  -- ← self-reference
WHERE prev.ds = '${ds - 1}';
```

## Conversion Rules

Self-referencing table conversion is essentially the same as regular tables, with the following differences:

### 1. Explicit Schema Declaration

Self-referencing tables must explicitly declare complete column definitions (including types) in CREATE DYNAMIC TABLE, because the SQL engine needs this information to infer the types of self-dependent columns:

```sql
CREATE OR REPLACE DYNAMIC TABLE kscdm.daily_sales (
    id BIGINT COMMENT '...',
    amount DECIMAL(10,2) COMMENT '...',
    ds STRING COMMENT '...'
)
PARTITIONED BY (ds)
AS
SELECT current.id, current.amount,
    SESSION_CONFIGS()['dt.args.ds'] AS ds
FROM source_sales current
LEFT JOIN kscdm.daily_sales prev ON current.id = prev.id
WHERE prev.ds = DATE_FORMAT(sub_days(SESSION_CONFIGS()['dt.args.ds'], 1), 'yyyy-MM-dd')::STRING;
```

### 2. Retain Self-reference in Query

In the converted AS clause, the self-referencing table name remains unchanged without any substitution. The SQL engine automatically handles version management for self-references.

## Common Self-reference Scenarios

### Day-over-day Comparison

```sql
-- Input
INSERT OVERWRITE TABLE metrics PARTITION(ds='${ds}')
SELECT t.id, t.value,
    t.value - prev.value AS daily_change
FROM source t
LEFT JOIN metrics prev ON t.id = prev.id AND prev.ds = '${ds - 1}';

-- Output
CREATE OR REPLACE DYNAMIC TABLE metrics (
    id BIGINT, value DECIMAL(10,2), daily_change DECIMAL(10,2), ds STRING
)
PARTITIONED BY (ds)
AS
SELECT t.id, t.value,
    t.value - prev.value AS daily_change,
    SESSION_CONFIGS()['dt.args.ds'] AS ds
FROM source t
LEFT JOIN metrics prev ON t.id = prev.id
    AND prev.ds = DATE_FORMAT(sub_days(SESSION_CONFIGS()['dt.args.ds'], 1), 'yyyy-MM-dd')::STRING;
```
