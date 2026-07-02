---
name: clickzetta-table-stream-pipeline
description: |
  Build and manage ClickZetta Table Stream change data capture pipelines, covering source change tracking, Stream creation, offset management, and idempotent incremental-ETL consumption.
  Includes change tracking setup, mode selection, metadata field usage — all ClickZetta-specific logic.

  Trigger when the user says: "create Table Stream", "Table Stream CDC", "Table Stream pipeline",
  "Table Stream incremental consumption", "Stream consumption", "change data capture",
  "capture table changes", "CDC with Table Stream", "incremental ETL from table",
  "track row changes", "consume stream data", "stream offset".
  Keywords: table stream, CDC, change capture, incremental ETL, stream, offset
---

# Table Stream Change Data Capture Workflow

## Step 1: Enable Change Tracking on Source Table (required prerequisite)

```sql
ALTER TABLE <source_table> SET PROPERTIES ('change_tracking' = 'true');
```

This is a mandatory prerequisite — without it, the Stream cannot capture changes correctly.

Verify it took effect:
```sql
-- Method 1
DESC EXTENDED <source_table>;

-- Method 2
SELECT table_name, properties FROM information_schema.tables WHERE table_name = '<source_table>';
```

## Step 2: Create Table Stream

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

**Mode selection:**

| Mode | Captures | Use case |
|---|---|---|
| `STANDARD` | INSERT / UPDATE_BEFORE / UPDATE_AFTER / DELETE | Data sync, incremental ETL — reflects net changes between two transaction points |
| `APPEND_ONLY` | INSERT only (retains all historical inserts even after DELETE) | Audit trail, history retention |

**SHOW_INITIAL_ROWS:**
- `TRUE`: first consumption returns rows that existed in the table when the Stream was created
- `FALSE` (default): first consumption returns only changes after Stream creation

> `TIMESTAMP AS OF` specifies the Stream's starting read position. This feature may be unstable in some scenarios — prefer the default behavior (start from creation time).

## Step 3: Prepare Target Table

Create a target table compatible with the source table structure. Add metadata columns for tracking:

```sql
CREATE TABLE <target_table> (
  -- source business columns
  order_id INT, status STRING, amount DOUBLE,
  -- optional tracking columns
  sync_version BIGINT, sync_timestamp TIMESTAMP
);
```

## Step 4: Preview Stream Data (does not advance offset)

```sql
SELECT *, __change_type, __commit_version, __commit_timestamp
FROM <stream_name>;
```

Metadata fields:
- `__change_type`: `INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`
- `__commit_version`: internal version number
- `__commit_timestamp`: when the change was committed

**UPDATE handling**: UPDATE produces two records — `UPDATE_BEFORE` (old value, usually ignored) and `UPDATE_AFTER` (new value, write to target). Always filter `__change_type` to avoid writing `UPDATE_BEFORE` stale values to the target table.

## Step 5: Consume Stream Data (advances offset)

### Option A: Full consumption (INSERT INTO)

```sql
INSERT INTO <target_table>
SELECT <columns> FROM <stream_name>;
```

### Option B: Idempotent consumption (MERGE — recommended)

```sql
MERGE INTO <target_table> t
USING (SELECT * FROM <stream_name> WHERE __change_type != 'UPDATE_BEFORE') s
ON t.<pk_column> = s.<pk_column>
WHEN MATCHED AND s.__change_type IN ('INSERT', 'UPDATE_AFTER') THEN UPDATE SET t.col1 = s.col1, t.col2 = s.col2
WHEN MATCHED AND s.__change_type = 'DELETE' THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT' THEN INSERT (<columns>) VALUES (s.<columns>);
```

MERGE is preferred because it's idempotent — re-running won't create duplicates. Filter out `UPDATE_BEFORE` in the USING subquery to prevent stale values from interfering with MERGE logic.

> ⚠️ **MERGE clause order**: when multiple `WHEN MATCHED` clauses exist, **UPDATE must come before DELETE**, otherwise: `update statement must be before delete statement`

## Step 6: Verify Consumption

```sql
SELECT COUNT(*) FROM <stream_name>;
-- After successful consumption, COUNT should be 0 or contain only new changes
```

Record the last consumed `__commit_version` for fault recovery.

---

## Offset Advancement Rules

| Operation | Advances offset | Notes |
|---|---|---|
| `SELECT * FROM stream` | ❌ No | Preview only, can query repeatedly |
| `INSERT INTO target SELECT ... FROM stream` | ✅ Yes | Consumes data |
| `MERGE INTO target USING stream ...` | ✅ Yes | Consumes data (recommended) |
| DML with WHERE filter | ✅ Yes (all rows) | Even if WHERE filters some rows, ALL rows' offsets advance |

> ⚠️ Offset advancement is all-or-nothing. Once a DML consumes the Stream, all change records advance — partial consumption is not possible. If DML fails (e.g. target table doesn't exist), offset does not advance.

---

## Mode Selection Quick Reference

| Requirement | Recommended mode |
|---|---|
| Data sync (keep target consistent with source) | STANDARD |
| Incremental ETL pipeline | STANDARD |
| Audit all insert records | APPEND_ONLY |
| History retention | APPEND_ONLY |

---

## Performance Tips

- Select only necessary columns, avoid `SELECT *`
- Consume Stream regularly to prevent data accumulation
- High change rate tables: consume more frequently; low change rate: reduce frequency
- Large Streams: split by primary key range for parallel processing
- Set appropriate data retention period on source table

---

## Examples

### Example 1: Orders table real-time sync

```sql
-- 1. Enable change tracking
ALTER TABLE orders SET PROPERTIES ('change_tracking' = 'true');

-- 2. Create Stream
CREATE TABLE STREAM orders_stream ON TABLE orders
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD', 'SHOW_INITIAL_ROWS' = 'FALSE');

-- 3. Create target table
CREATE TABLE orders_sync (order_id INT, status STRING, amount DOUBLE);

-- 4. Preview (no offset advance)
SELECT *, __commit_version, __commit_timestamp FROM orders_stream;

-- 5. Consume (advances offset)
MERGE INTO orders_sync t
USING (SELECT * FROM orders_stream WHERE __change_type != 'UPDATE_BEFORE') s
ON t.order_id = s.order_id
WHEN MATCHED AND s.__change_type IN ('INSERT', 'UPDATE_AFTER') THEN UPDATE SET t.status = s.status, t.amount = s.amount
WHEN MATCHED AND s.__change_type = 'DELETE' THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT' THEN INSERT (order_id, status, amount) VALUES (s.order_id, s.status, s.amount);

-- 6. Verify
SELECT COUNT(*) FROM orders_stream;
```

### Example 2: User behavior audit (retain all insert history)

```sql
ALTER TABLE user_actions SET PROPERTIES ('change_tracking' = 'true');

CREATE TABLE STREAM user_actions_audit_stream ON TABLE user_actions
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY', 'SHOW_INITIAL_ROWS' = 'TRUE');

INSERT INTO user_actions_audit
SELECT *, __commit_version AS audit_version, __commit_timestamp AS audit_time
FROM user_actions_audit_stream;
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| Stream not capturing changes | Source table change_tracking not enabled | `ALTER TABLE <table> SET PROPERTIES ('change_tracking' = 'true')`, confirm DML runs after Stream creation |
| Cannot distinguish change types | Not filtering `__change_type` in MERGE/INSERT, `UPDATE_BEFORE` written to target | Filter `__change_type IN ('UPDATE_AFTER', 'DELETE')` in MERGE, ignore `UPDATE_BEFORE` |
| Offset not advancing after consumption | Only used SELECT, no DML executed | Must consume via INSERT INTO / MERGE INTO / UPDATE |
| Duplicate data in target after re-consumption | Used INSERT INTO instead of MERGE, or non-idempotent logic | Switch to MERGE; record last consumed `__commit_version` for checkpoint recovery |
| COMMENT syntax error | Used `COMMENT = '...'` (with equals sign) | Correct syntax: `COMMENT 'content'` (no equals sign) |
