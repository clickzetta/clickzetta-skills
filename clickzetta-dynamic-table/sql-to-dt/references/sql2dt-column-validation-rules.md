# Dynamic Table Column Validation and Consistency Rules

You are a SQL conversion expert. After generating the Dynamic Table DDL, you need to validate whether the columns defined in the schema match the columns produced by the SELECT query.

## Column Count Validation (Must Pass)

### Rule

The number of columns defined in the parentheses of the generated DDL must equal the number of columns produced by the SELECT query after AS.

```sql
CREATE OR REPLACE DYNAMIC TABLE t (
    col1 BIGINT,    -- 1
    col2 STRING,    -- 2
    dt STRING       -- 3  → schema column count = 3
)
AS
SELECT col1, col2, '2024-01-01' AS dt  -- → SELECT column count = 3 ✓
FROM source;
```

### Counting SELECT Columns

1. Find the SELECT clause after AS
2. Find the top-level FROM (not inside a subquery/parentheses)
3. Count top-level commas between SELECT and FROM + 1 = column count
4. Top-level commas: commas not inside parentheses `()`, square brackets `[]`, or quotes `''`/`""`

### Column Count for UNION ALL

Use the column count of the first branch (all branches should have the same column count).

### Validation Failure

If schema column count ≠ SELECT column count, conversion fails with error:
```
Schema column count (N) != SELECT column count (M)
```

## Column Name Validation (Optional)

### Rule

Compare schema column names against inferred aliases from SELECT, position by position. Recommended to enable after column count validation passes, if most columns in SELECT have explicit aliases (AS or bare identifiers).

### Inferring SELECT Column Aliases

In order of priority from high to low:

1. **AS alias**: `expression AS alias` → alias is `alias`
2. **Trailing identifier**: `table.column` → alias is `column`
3. **Bare identifier**: `column_name` → alias is `column_name`
4. **Cannot infer**: `func(a, b)` without AS → mark as `<expr>`, skip validation

### Comparison Rules

- Compare position by position (1st column vs 1st column, 2nd vs 2nd, ...)
- If a position is `<expr>` (cannot infer), skip that position
- Comparison is case-insensitive
- On mismatch, report error and list the specific misaligned columns

## Column Count After Static Partition Injection

After injecting static partition columns, the SELECT column count increases. Validation should be performed after injection.

### Avoid Duplicate Injection

Before injection, check whether SELECT already contains the partition column:

1. Parse the final alias of each expression in SELECT
2. If the alias (case-insensitive) matches the partition column name → the column already exists; skip injection
3. Only inject partition columns not already present in SELECT

## UNION ALL Consistency

### Branch Column Count Consistency

All UNION ALL branches must have the same column count. If inconsistent, record a warning:
```
UNION branch column counts are inconsistent: [12, 13, 12]
```

### Post-injection Recheck

After static partition injection, recheck whether all branch column counts are consistent:
```
UNION branch column counts after injection: [13, 13, 13]
```

## Duplicate Alias Detection

If SELECT contains duplicate column aliases, record a warning:
```
Duplicate column aliases detected: ['dt']
```

Duplicate aliases may cause:
- Column count appears correct but actual semantics are wrong
- Ambiguous references in downstream queries

## Missing Partition Column Detection

If SELECT is missing some partition columns (before injection), record information:
```
Missing partition columns detected: ['dt', 'ds']
```

These columns will be automatically added in the injection step.

## Complete Validation Flow

```
1. Generate DDL (including static partition injection)
2. Extract schema column count
3. Extract SELECT column count
4. Compare column counts → fail if unequal
5. (Optional) Compare column names position by position → fail if mismatched
```
