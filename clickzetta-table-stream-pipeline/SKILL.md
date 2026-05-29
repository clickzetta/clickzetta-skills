---
name: clickzetta-table-stream-pipeline
description: |
  Build and manage ClickZetta Table Stream change data capture pipelines, covering the
  end-to-end workflow from source table configuration, Stream creation, and data consumption
  to incremental ETL. Trigger when the user says "create Table Stream", "Table Stream CDC",
  "Table Stream pipeline", "Table Stream incremental consumption", or "Stream consumption".
  Includes change tracking enablement, mode selection, offset management, metadata field usage,
  and idempotent consumption — all ClickZetta-specific logic.
  Keywords: table stream, CDC, change capture, incremental ETL, stream
---

# Table Stream Change Data Capture Workflow

## Instructions

### Step 1: Enable Change Tracking on the Source Table (Required Prerequisite)
Execute SQL to enable `change_tracking` on the source table:
```sql
ALTER TABLE <source_table> SET PROPERTIES ('change_tracking' = 'true');
```
- This is a mandatory prerequisite. Without it, the Stream cannot correctly capture changes.
- Verify the property took effect (two methods):
```sql
-- Method 1: DESC EXTENDED to view properties
DESC EXTENDED <source_table>;

-- Method 2: Query information_schema
SELECT table_name, properties FROM information_schema.tables WHERE table_name = '<source_table>';
```

### Step 2: Create a Table Stream
Execute SQL to create the Stream:
```sql
CREATE [ OR REPLACE ] TABLE STREAM <stream_name>
  ON TABLE <source_table>
  [ TIMESTAMP AS OF '<timestamp>' ]
  [ COMMENT '<description>' ]
  WITH PROPERTIES (
    'TABLE_STREAM_MODE' = 'STANDARD | APPEND_ONLY',
    'SHOW_INITIAL_ROWS' = 'TRUE | FALSE'
  );
```
Key parameter selection:
- **STANDARD mode**: captures INSERT/UPDATE/DELETE, reflecting the current state of the table (delta changes) → suitable for data sync, incremental ETL
  - Delta changes refer to the net change between two transaction timestamps. For example: INSERT then DELETE the same row → delta is empty; INSERT then UPDATE → delta is one new row (final state)
- **APPEND_ONLY mode**: captures INSERT only, retaining all historical insert records → suitable for auditing, historical record retention
  - Even if a row is later DELETEd, APPEND_ONLY mode retains the INSERT record for that row
- **SHOW_INITIAL_ROWS = TRUE**: first consumption returns rows already in the table when the Stream was created
- **SHOW_INITIAL_ROWS = FALSE** (default): first consumption returns only new changes after Stream creation
- Optional: specify a starting timestamp
```sql
-- TIMESTAMP AS OF specifies the starting read offset for the Stream
-- Note: this feature may be unstable in some scenarios; prefer the default behavior (start from creation time)
CREATE TABLE STREAM <stream_name>
  ON TABLE <source_table>
  TIMESTAMP AS OF '<timestamp>'
  WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
```

### Step 3: Prepare the Target Table
Create a target table with a structure compatible with the source table:
- The target table column definitions must include the business columns from the source table
- Recommended: add extra metadata columns (e.g., sync_version, sync_timestamp) for tracking

### Step 4: Query Stream Data (Preview — Does Not Advance Offset)
Execute SELECT to preview change data in the Stream:
```sql
SELECT *, __change_type, __commit_version, __commit_timestamp
FROM <stream_name>;
```
- SELECT alone does not advance the offset
- Metadata fields: `__change_type` (values: `INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`), `__commit_version`, `__commit_timestamp`
- **UPDATE handling**: an UPDATE operation produces two records:
  - `UPDATE_BEFORE`: the old value before the update (typically ignored during consumption)
  - `UPDATE_AFTER`: the new value after the update (used when writing to the target table)
  - Always filter on `__change_type` during consumption to avoid writing `UPDATE_BEFORE` old values into the target table

### Step 5: Consume Stream Data (Advances Offset)
Execute a DML operation to consume data:

#### Method A: Full Consumption (INSERT INTO)
```sql
INSERT INTO <target_table>
SELECT <columns> FROM <stream_name>;
```

#### Method B: Idempotent Consumption (MERGE — recommended)
```sql
MERGE INTO <target_table> t
USING (SELECT * FROM <stream_name> WHERE __change_type != 'UPDATE_BEFORE') s
ON t.<pk_column> = s.<pk_column>
WHEN MATCHED AND s.__change_type IN ('INSERT', 'UPDATE_AFTER') THEN UPDATE SET t.col1 = s.col1, t.col2 = s.col2
WHEN MATCHED AND s.__change_type = 'DELETE' THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT' THEN INSERT (<columns>) VALUES (s.<columns>);
```
- DML operations (INSERT/UPDATE/MERGE) advance the offset
- ⚠️ Even with a WHERE clause that filters some rows, **the offset advances for all rows** (not just the matched ones)
- Use MERGE for idempotency to avoid duplicate data from repeated consumption
- Filter out `UPDATE_BEFORE` in the USING subquery to prevent old values from interfering with MERGE logic
- ⚠️ **MERGE clause ordering requirement**: when multiple `WHEN MATCHED` clauses are present, **UPDATE must come before DELETE**, otherwise an error occurs (error message: `update statement must be before delete statement`)

### Step 6: Verify Consumption Status
Execute a query to confirm consumption is complete:
```sql
SELECT COUNT(*) FROM <stream_name>;
```
- After successful consumption, COUNT should be 0 or contain only new changes
- Record the last consumed `__commit_version` for failure recovery

## Offset Advancement Rules

| Operation | Advances offset? | Notes |
|------|----------------|------|
| `SELECT * FROM stream` | No | Preview only; can be queried repeatedly |
| `INSERT INTO target SELECT ... FROM stream` | Yes | Consumes data |
| `MERGE INTO target USING stream ...` | Yes | Consumes data (recommended) |
| `UPDATE target SET ... FROM stream` | Yes | Consumes data |
| `DELETE FROM target USING stream` | Yes | Consumes data |
| DML with WHERE clause | Yes (all rows) | Even if WHERE filters some rows, offset advances for all rows |

> ⚠️ **Key note**: offset advancement is all-or-nothing. Once a DML consumes the Stream, the offset advances for all change records — partial consumption is not possible. If the DML fails (e.g., target table does not exist), the offset does not advance.

## Mode Selection Quick Reference

| Requirement | Recommended mode |
|------|---------|
| Data sync (keep target consistent with source) | STANDARD |
| Incremental ETL pipeline | STANDARD |
| Audit all insert records | APPEND_ONLY |
| Historical record retention | APPEND_ONLY |

## Performance Optimization Tips

- Select only necessary columns; avoid `SELECT *`
- Consume the Stream regularly to prevent data accumulation
- High-change-rate tables: consume more frequently; low-change-rate tables: reduce frequency
- Large Streams can be split by primary key range for parallel processing
- Set an appropriate data retention period on the source table

## Examples

### Example 1: Real-time Order Table Sync
```sql
-- 1. Enable change tracking on source table
ALTER TABLE orders SET PROPERTIES ('change_tracking' = 'true');

-- 2. Create Table Stream
CREATE TABLE STREAM orders_stream ON TABLE orders 
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD', 'SHOW_INITIAL_ROWS' = 'FALSE');

-- 3. Create target table (compatible structure with source)
CREATE TABLE orders_sync (order_id INT, status STRING, amount DOUBLE);

-- 4. Preview Stream data (does not advance offset)
SELECT *, __commit_version, __commit_timestamp FROM orders_stream;

-- 5. Consume Stream data (advances offset)
MERGE INTO orders_sync t 
USING (SELECT * FROM orders_stream WHERE __change_type != 'UPDATE_BEFORE') s 
ON t.order_id = s.order_id 
WHEN MATCHED AND s.__change_type IN ('INSERT', 'UPDATE_AFTER') THEN UPDATE SET t.status = s.status, t.amount = s.amount 
WHEN MATCHED AND s.__change_type = 'DELETE' THEN DELETE 
WHEN NOT MATCHED AND s.__change_type = 'INSERT' THEN INSERT (order_id, status, amount) VALUES (s.order_id, s.status, s.amount);

-- 6. Verify consumption is complete
SELECT COUNT(*) FROM orders_stream;
```

### Example 2: User Behavior Audit (Retain Full Insert History)
```sql
-- 1. Enable change tracking on source table
ALTER TABLE user_actions SET PROPERTIES ('change_tracking' = 'true');

-- 2. Create Table Stream (APPEND_ONLY mode)
CREATE TABLE STREAM user_actions_audit_stream ON TABLE user_actions 
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY', 'SHOW_INITIAL_ROWS' = 'TRUE');

-- 3. Preview Stream data
SELECT *, __commit_version, __commit_timestamp FROM user_actions_audit_stream;

-- 4. Consume Stream data (INSERT INTO advances offset)
INSERT INTO user_actions_audit 
SELECT *, __commit_version AS audit_version, __commit_timestamp AS audit_time 
FROM user_actions_audit_stream;
```

## Troubleshooting

Stream not capturing changes:
Cause: `change_tracking` not enabled on the source table
Solution: Execute `ALTER TABLE <table> SET PROPERTIES ('change_tracking' = 'true')`; confirm that DML was executed after the Stream was created

Cannot distinguish change types:
Cause: `__change_type` not filtered in MERGE/INSERT, causing `UPDATE_BEFORE` old values to be written to the target table
Solution: Filter `__change_type IN ('UPDATE_AFTER', 'DELETE')` in MERGE; ignore `UPDATE_BEFORE` records

Offset not advancing after consumption:
Cause: Only SELECT was used; no DML was executed
Solution: Data must be consumed via DML operations such as INSERT INTO / MERGE INTO / UPDATE

Duplicate data in target table from repeated consumption:
Cause: Using INSERT INTO instead of MERGE, or non-idempotent consumption logic
Solution: Switch to MERGE statements; record the last consumed `__commit_version` and `__commit_timestamp` for checkpoint recovery

COMMENT syntax error:
Cause: Used `COMMENT = '...'` (with equals sign) instead of `COMMENT '...'`
Solution: Correct syntax is `COMMENT 'description'` — no equals sign
