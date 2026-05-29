---
name: dynamic-table-alter
description: |
  Modify the structure and properties of ClickZetta Dynamic Tables. Supports direct ALTER operations
  (suspend, resume, rename_column, set_comment, set_column_comment, set/unset properties) as well as
  CREATE OR REPLACE rebuild operations (modify refresh interval, compute cluster, add column, drop column,
  change column type, change SQL definition). Triggers when the user says "modify dynamic table",
  "add column to dynamic table", "change refresh interval", or "suspend dynamic table".
---

# Dynamic Table Modification Workflow

## Instructions

### Step 1: Confirm the Dynamic Table Exists and Retrieve Its Current Definition
Execute `SHOW CREATE TABLE schema_name.table_name` to get the current definition of the Dynamic Table.
If unsure whether it is a Dynamic Table, first use `SHOW TABLES WHERE is_dynamic` to view the list.

### Step 2: Determine the Operation Type and Choose the Execution Method

Dynamic Table modification operations fall into two categories:

**A. Direct ALTER operations** (6 types, can be executed directly):

1. **suspend** — Pause the scheduled refresh:
```sql
ALTER DYNAMIC TABLE dt_name SUSPEND;
```

2. **resume** — Start the scheduled refresh:
```sql
ALTER DYNAMIC TABLE dt_name RESUME;
```

3. **set_comment** — Modify the table comment:
```sql
ALTER DYNAMIC TABLE dt_name SET COMMENT 'comment';
```

4. **rename_column** — Rename a column:
```sql
ALTER DYNAMIC TABLE dt_name RENAME COLUMN old_name TO new_name;
```

5. **set_column_comment** — Modify a column comment (note: use CHANGE COLUMN):
```sql
ALTER DYNAMIC TABLE dt_name CHANGE COLUMN column_name COMMENT 'comment';
```

6. **set/unset properties** — Modify table properties (currently reserved parameters):
```sql
-- Set a property
ALTER DYNAMIC TABLE dt_name SET PROPERTIES('key' = 'value');
-- Remove a property
ALTER DYNAMIC TABLE dt_name UNSET PROPERTIES('key');
```

**B. CREATE OR REPLACE operations** (6 types, require rebuilding the Dynamic Table):

> ⚠️ **The following operations do not support ALTER syntax.** Syntax like `ALTER DYNAMIC TABLE ... SET REFRESH INTERVAL` does not exist and will cause a syntax error. You must use `CREATE OR REPLACE DYNAMIC TABLE` to rebuild.

These operations involve changes to SQL query logic and cannot be completed via ALTER directly:

7. **Modify refresh interval** — ❌ `ALTER ... SET REFRESH INTERVAL` is not supported
8. **Modify compute cluster** — ❌ `ALTER ... SET VCLUSTER` is not supported
9. **Add column**
10. **Drop column**
11. **Modify column type**
12. **Modify SQL definition**

### Step 3: Execute CREATE OR REPLACE Rebuild (Type B operations only)

1. Execute `SHOW CREATE TABLE schema_name.table_name` to get the original DDL
   > ⚠️ `SHOW CREATE TABLE` does not support LIMIT/WHERE clauses; execute it directly
2. Parse out: column definitions, REFRESH clause, AS SELECT clause, COMMENT, etc.
3. Modify the relevant parts according to the operation
4. Execute the rebuild SQL

**About full refresh triggers:**
- Simple drop column / add column (where the added column is simply passed through from the source table without participating in JOIN keys, GROUP keys, or other computations) → **incremental refresh**
- Changes involving computation logic (modifying WHERE conditions, modifying aggregation logic, new column participates in computation, etc.) → **full refresh**
- Compatible type changes (e.g., INT → BIGINT) → **incremental refresh**

### Step 4: Verify the Modification
Use `DESC TABLE dt_name` to confirm the modification took effect.

---

## Examples

### Example 1: Modify Refresh Interval

```sql
-- Original table
CREATE DYNAMIC TABLE dt_name
REFRESH INTERVAL 10 MINUTE vcluster DEFAULT
AS SELECT * FROM student02;

-- After modification (changed to 20 minutes)
CREATE OR REPLACE DYNAMIC TABLE dt_name
REFRESH INTERVAL 20 MINUTE vcluster DEFAULT
AS SELECT * FROM student02;
```

### Example 2: Modify Compute Cluster

```sql
-- Original table
CREATE DYNAMIC TABLE dt_name
REFRESH INTERVAL 10 MINUTE vcluster DEFAULT
AS SELECT * FROM student02;

-- After modification (changed to alter_vc cluster)
CREATE OR REPLACE DYNAMIC TABLE dt_name
REFRESH INTERVAL 10 MINUTE vcluster alter_vc
AS SELECT * FROM student02;
```

### Example 3: Add Column

```sql
-- Original table
CREATE DYNAMIC TABLE change_table (i, j)
AS SELECT * FROM dy_base_a;

-- Add column col (involves computation logic; next refresh will be a full refresh)
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j, col)
AS SELECT i, j, j * 1 FROM dy_base_a;

REFRESH DYNAMIC TABLE change_table;
```

### Example 4: Drop Column

```sql
-- Original table has columns i, j
CREATE DYNAMIC TABLE change_table (i, j)
AS SELECT * FROM dy_base_a;

-- Drop column (simple pass-through; incremental refresh)
CREATE OR REPLACE DYNAMIC TABLE change_table (i)
AS SELECT i FROM dy_base_a;
```

### Example 5: Modify SQL Definition

```sql
-- Modify WHERE filter condition (full refresh)
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j)
AS SELECT * FROM dy_base_a WHERE i > 3;

REFRESH DYNAMIC TABLE change_table;
```

### Example 6: Modify Column Type

```sql
-- INT → BIGINT (compatible type; incremental refresh)
CREATE OR REPLACE DYNAMIC TABLE change_table (i, j)
AS SELECT CAST(i AS BIGINT), j FROM dy_base_a;

REFRESH DYNAMIC TABLE change_table;
```

---

## Platform-Specific Knowledge

- **CHANGE COLUMN syntax**: set a column comment with `CHANGE COLUMN col COMMENT 'xxx'`, not `ALTER COLUMN`
- **RENAME COLUMN syntax**: `RENAME COLUMN old TO new`
- **DML restrictions**: Dynamic Tables do not support UPDATE/DELETE/MERGE by default (due to hidden column MV__KEY); to use DML, first execute `SET cz.sql.dt.allow.dml = true;`
- **REFRESH format**: `REFRESH INTERVAL <N> MINUTE vcluster <name>`, supports SECOND/MINUTE/HOUR/DAY
- **CREATE OR REPLACE risk**: changes involving computation logic will trigger a full refresh, which may take a long time for large tables
- **Schema prefix**: all ALTER/CREATE statements should include the schema prefix in the table name
- **Column definitions can omit types**: `CREATE DYNAMIC TABLE dt (i, j) AS SELECT ...` — types are inferred from SELECT
- **DROP syntax**: must use `DROP DYNAMIC TABLE dt_name`; `DROP TABLE dt_name` will cause an error
- **UNDROP syntax**: must use `UNDROP TABLE dt_name`; `UNDROP DYNAMIC TABLE dt_name` is not supported
- **DESC syntax**: use `DESC TABLE dt_name` for Dynamic Tables; do not write `DESC DYNAMIC TABLE dt_name EXTENDED` (EXTENDED is not supported)

## Troubleshooting

| Error | Cause | Solution |
|---|---|---|
| ALTER reports "Syntax error at or near 'REFRESH'" | `ALTER ... SET REFRESH INTERVAL` syntax does not exist | Use `CREATE OR REPLACE DYNAMIC TABLE ... REFRESH INTERVAL ...` to rebuild |
| ALTER reports "unsupported operation" | Attempted a Type B ALTER operation on a Dynamic Table | Use CREATE OR REPLACE to rebuild |
| `DROP TABLE dt_name` fails | Dynamic Tables must use `DROP DYNAMIC TABLE` | Change to `DROP DYNAMIC TABLE dt_name` |
| `UNDROP DYNAMIC TABLE` fails | UNDROP does not support the DYNAMIC TABLE keyword | Change to `UNDROP TABLE dt_name` |
| `DESC DYNAMIC TABLE ... EXTENDED` fails | EXTENDED parameter is not supported | Change to `DESC TABLE dt_name` (without EXTENDED) |
| UPDATE/DELETE reports "MV__KEY" related error | Dynamic Tables have a hidden column MV__KEY; DML is disabled by default | First execute `SET cz.sql.dt.allow.dml = true;` |
| Data is empty after CREATE OR REPLACE | The AS SELECT clause references an incorrect source table or column | Verify that the SELECT clause returns data first |
| Full refresh triggered after CREATE OR REPLACE | The new column participates in computation logic (JOIN key, GROUP key, etc.) | Expected behavior; wait for the full refresh to complete |
