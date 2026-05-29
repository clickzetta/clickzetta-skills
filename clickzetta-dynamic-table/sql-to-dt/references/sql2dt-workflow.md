# SQL → Dynamic Table Complete Conversion Workflow

When the user gives you a set of CREATE TABLE DDL and INSERT OVERWRITE SQL and asks to convert them to a Dynamic Table, execute the following steps in order.

The detailed rules for each step are in the corresponding skill files, which you need to reference simultaneously.

## Workflow Steps

### Step 1: Pre-process Input

Remove from the INSERT OVERWRITE file:
- All `ALTER TABLE` statements
- `ANALYZE TABLE` statements
- SQL comments (`--` and `/* */`)

Retain: CREATE TABLE, INSERT OVERWRITE, WITH, SET, CREATE TEMPORARY FUNCTION.

### Step 2: Placeholder Replacement

Follow the rules in #[[file:sql2dt-placeholder-rules.md]]:
1. Normalize placeholder format (`{{ }}` → `${ }`)
2. Replace all placeholders with `SESSION_CONFIGS()` calls
3. Handle nodash variables, date arithmetic, macros functions
4. Decide handling based on quote context (remove quotes / CONCAT / direct replacement)

### Step 3: Self-reference Detection

Follow the rules in #[[file:sql2dt-self-reference-rules.md]]:
1. Check whether the INSERT OVERWRITE target table appears in FROM/JOIN
2. If it is a self-referencing table, mark it and add comments and use explicit schema in subsequent steps

### Step 4: Core Conversion

Follow the rules in #[[file:sql2dt-conversion-rules.md]]:
1. Parse CREATE TABLE DDL (extract columns, partitions, properties, etc.)
2. Parse INSERT OVERWRITE (extract query, partition type)
3. Assemble `CREATE OR REPLACE DYNAMIC TABLE ... AS SELECT ...`
4. Inject static partition values into SELECT (smart quote handling)
5. Merge table property template (default `data_lifecycle=15`)
6. Handle UNION ALL (inject into each branch independently)
7. Date function post-processing: convert all `DATE_SUB/DATE_ADD` to `sub_days`

### Step 5: Column Validation

Follow the rules in #[[file:sql2dt-column-validation-rules.md]]:
1. Count schema columns and SELECT columns
2. Verify they are equal
3. Check for duplicate aliases and missing partition columns
4. UNION ALL branch column count consistency check

### Step 6: Generate Companion Files

Follow the rules in #[[file:sql2dt-refresh-rules.md]]:
1. Extract all SESSION_CONFIGS variables from the DDL
2. Generate current-cycle refresh statement
3. Generate previous-cycle prev_refresh statement
4. Generate backfill statement

### Step 7: Post-conversion Improvement Suggestions

After DDL generation is complete, check the conversion result and proactively offer improvement suggestions to the user:

**Check 1: Non-partitioned table + continuous write risk**

Follow the judgment logic in #[[file:../best-practices/non-partitioned-merge-into-warning.md]]:
- The generated DT is a non-partitioned table (no `PARTITIONED BY` and no `SESSION_CONFIGS()`)
- And the SQL contains the `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ... DESC) WHERE rn = 1` deduplication pattern

→ When conditions are met, use the alert message template from that document to warn the user of the risk, and suggest switching to the MERGE INTO + Table Stream approach.

**Check 2: SQL performance optimization opportunities**

Follow the rules in #[[file:../best-practices/performance-optimization.md]], scan the generated DT SQL:
- Contains `LEFT/RIGHT/FULL OUTER JOIN` → suggest switching to INNER JOIN if business allows, to improve incremental efficiency
- Contains window functions without `PARTITION BY` → suggest adding PARTITION BY; otherwise every incremental refresh will do a full recomputation
- `GROUP BY` uses complex expressions (e.g., `DATE_TRUNC`, `SUBSTR`) → suggest pre-computing upstream or splitting into multi-level DTs

**Check 3: Whether there are dimension tables in JOINs**

Follow the recommended scenarios in #[[file:../best-practices/dimension-table-join-guide.md]]:
- SQL contains JOIN → ask the user whether the right-side table is a low-frequency-change dimension table (lookup table, dictionary table, config table, etc.)
- If yes → suggest adding `mv_const_tables` configuration in TBLPROPERTIES, and explain its behavior and data consistency tradeoffs

## Output Checklist

For each table, the final output is:

| File | Content | Condition |
|------|------|------|
| `table_name.sql` | Dynamic Table DDL | Always generated |
| `table_name_refresh.sql` | Current-cycle REFRESH statement | Always generated |
| `table_name_prev_refresh.sql` | Previous-cycle REFRESH statement | Only when partition variables exist |
| `table_name_backfill.sql` | Backfill statement | Only when partition variables exist |

## Quick Decision Path

```
Input DDL + INSERT OVERWRITE
  │
  ├─ Has placeholders? → Step 2 placeholder replacement
  │
  ├─ Self-reference? → Step 3 special handling
  │
  ├─ Has static partitions? → Step 4 inject partition values into SELECT
  │
  ├─ Has UNION ALL? → Step 4 inject into each branch independently
  │
  └─ Generate DDL → Step 5 validate → Step 6 generate companion files → Step 7 improvement suggestions
```
