# Recovering from Data Mistakes: Using Time Travel to Restore Deleted or Corrupted Data

## Business Background

Accidental data modifications are something every data team encounters: an operations colleague accidentally deletes a batch of orders, a developer's UPDATE has a WHERE condition that's too broad and corrupts amounts, a DBA mistakenly runs DROP TABLE. Traditional databases handle these situations by restoring from a backup (slow, and any data written after the backup is lost) or replaying binlogs (complex, requires DBA involvement).

Singdata Lakehouse's Time Travel feature turns data recovery into a single SQL statement: every write operation generates a new version, historical versions are retained for 1 day by default (configurable up to 90 days), and you can query data at any historical point in time or roll back an entire table with one command.

Three recovery methods, each for a different type of incident:

| Incident type | Recovery method | When to use |
|---------|---------|---------|
| Accidentally deleted rows (DELETE) | `INSERT INTO ... SELECT ... TIMESTAMP AS OF` | Restores only the deleted rows without affecting new data written after the deletion |
| Corrupted data (UPDATE) | `RESTORE TABLE ... TO TIMESTAMP AS OF` | Rolls back the entire table to a specified point in time |
| Accidentally dropped table (DROP) | `UNDROP TABLE` | Restores the dropped table and all its data |

## SQL Commands Involved

| Command | Purpose |
|------|------|
| `DESC HISTORY` | View the table's version history to find the timestamp before the incident |
| `SELECT ... TIMESTAMP AS OF` | Query historical data at a specified point in time |
| `INSERT INTO ... SELECT ... TIMESTAMP AS OF` | Restore deleted rows from a historical version |
| `RESTORE TABLE ... TO TIMESTAMP AS OF` | Roll back the entire table to a specified point in time |
| `UNDROP TABLE` | Restore a table that was dropped |

## Prerequisites

### Create the Orders Table and Insert Initial Data

```sql
CREATE TABLE IF NOT EXISTS doc_orders (
    order_id   STRING,
    user_id    STRING,
    product_id STRING,
    amount     DECIMAL(10,2),
    status     STRING,
    order_time TIMESTAMP
);

INSERT INTO doc_orders VALUES
  ('O001','U101','P001', 598.00,'completed', CAST('2026-05-28 09:00:00' AS TIMESTAMP)),
  ('O002','U102','P002', 459.00,'completed', CAST('2026-05-28 09:10:00' AS TIMESTAMP)),
  ('O003','U103','P003', 389.00,'completed', CAST('2026-05-28 09:20:00' AS TIMESTAMP)),
  ('O004','U104','P001', 299.00,'completed', CAST('2026-05-28 09:30:00' AS TIMESTAMP)),
  ('O005','U105','P004', 256.00,'completed', CAST('2026-05-28 09:40:00' AS TIMESTAMP));
```

### View Version History and Record the Safe Version Timestamp

Every write operation generates a new version. Use `DESC HISTORY` to view the version list:

```sql
DESC HISTORY doc_orders;
```

```
+---------+-------------------------+----------+------+----------+
|version  |time                     |total_rows|user  |operation |
+---------+-------------------------+----------+------+----------+
|2        |2026-05-28T19:45:27.356  |5         |qiliang|INSERT_INTO|
|1        |2026-05-28T19:45:07.582  |0         |qiliang|CREATE    |
+---------+-------------------------+----------+------+----------+
```

Version 2 is the state after all 5 rows were written. Note the timestamp `2026-05-28 19:45:27` — you'll need it for recovery later.

> ⚠️ **Note**: `TIMESTAMP AS OF` only accepts constant literals; expressions like `NOW() - INTERVAL 1 HOUR` are not supported. To query data from "N minutes ago," you must first use `DESC HISTORY` to find the exact timestamp, then use it as a literal in your query.

## Scenario 1: Accidentally Deleted Rows — Precise Restoration

An operations colleague ran a DELETE with an incorrect WHERE condition, accidentally deleting 3 orders:

```sql
DELETE FROM doc_orders WHERE user_id IN ('U103','U104','U105');
```

Only 2 rows remain in the table.

**Step 1: Identify the timestamp before the deletion**

```sql
DESC HISTORY doc_orders;
```

```
+---------+-------------------------+----------+------+----------+
|version  |time                     |total_rows|user  |operation |
+---------+-------------------------+----------+------+----------+
|3        |2026-05-28T19:45:43.564  |2         |qiliang|DELETE    |
|2        |2026-05-28T19:45:27.356  |5         |qiliang|INSERT_INTO|
|1        |2026-05-28T19:45:07.582  |0         |qiliang|CREATE    |
+---------+-------------------------+----------+------+----------+
```

Version 2 (`19:45:27`) is the complete state before the deletion; version 3 is the post-deletion state with only 2 rows.

**Step 2: Preview the data to be restored**

```sql
SELECT * FROM doc_orders TIMESTAMP AS OF '2026-05-28 19:45:28'
ORDER BY order_id;
```

```
+--------+------+----------+-------+---------+---------------------+
|order_id|user_id|product_id|amount |status   |order_time           |
+--------+------+----------+-------+---------+---------------------+
|O001    |U101  |P001      |598.00 |completed|2026-05-28T09:00:00  |
|O002    |U102  |P002      |459.00 |completed|2026-05-28T09:10:00  |
|O003    |U103  |P003      |389.00 |completed|2026-05-28T09:20:00  |
|O004    |U104  |P001      |299.00 |completed|2026-05-28T09:30:00  |
|O005    |U105  |P004      |256.00 |completed|2026-05-28T09:40:00  |
+--------+------+----------+-------+---------+---------------------+
```

All 5 rows are visible and intact.

**Step 3: Restore only the deleted rows**

Use `NOT IN` to filter out rows already present in the current table, inserting only the missing ones:

```sql
INSERT INTO doc_orders
SELECT * FROM doc_orders TIMESTAMP AS OF '2026-05-28 19:45:28'
WHERE order_id NOT IN (SELECT order_id FROM doc_orders);
```

After execution, the table is restored to 5 rows. The advantage of this approach is that any new data written after the accidental deletion is not overwritten.

> 💡 **Tip**: Choose a timestamp that falls after the target version was fully written. The `time` field returned by `DESC HISTORY` is the time the version write completed. Adding 1 second to that timestamp ensures you hit that version.

## Scenario 2: Corrupted Data — Full Table Rollback

A developer's UPDATE had a WHERE condition that was too broad, multiplying all order amounts by 10:

```sql
UPDATE doc_orders SET amount = amount * 10
WHERE order_time > CAST('2026-01-01' AS TIMESTAMP);
```

> 💡 **Tip**: Singdata Lakehouse has a safety guard against DELETE/UPDATE statements without a WHERE clause — they are rejected with an error. However, UPDATE statements with an overly broad WHERE condition (such as one that covers the entire table) will still execute successfully and require human judgment. Time Travel is the last line of defense in such cases.

**Step 1: Identify the erroneous version**

```sql
DESC HISTORY doc_orders;
```

```
+---------+-------------------------+----------+------+----------+
|version  |time                     |total_rows|user  |operation |
+---------+-------------------------+----------+------+----------+
|5        |2026-05-28T19:46:57.926  |5         |qiliang|UPDATE    |
|4        |2026-05-28T19:46:21.359  |5         |qiliang|INSERT_INTO|
...
+---------+-------------------------+----------+------+----------+
```

Version 5 is the erroneous UPDATE; version 4 (`19:46:21`) is the correct state.

**Step 2: Compare the before and after states (optional)**

Before rolling back, confirm the scope of impact:

```sql
SELECT
    cur.order_id,
    cur.amount  AS amount_current,
    bad.amount  AS amount_bad_update,
    bad.amount - cur.amount AS diff
FROM doc_orders AS cur
JOIN (SELECT * FROM doc_orders TIMESTAMP AS OF '2026-05-28 19:46:58') AS bad
  ON cur.order_id = bad.order_id
ORDER BY cur.order_id;
```

```
+--------+---------------+------------------+---------+
|order_id|amount_current |amount_bad_update |diff     |
+--------+---------------+------------------+---------+
|O001    |598.00         |5980.00           |5382.00  |
|O002    |459.00         |4590.00           |4131.00  |
|O003    |389.00         |3890.00           |3501.00  |
|O004    |299.00         |2990.00           |2691.00  |
|O005    |256.00         |2560.00           |2304.00  |
+--------+---------------+------------------+---------+
```

All 5 orders were affected — amounts were inflated by 10x.

**Step 3: Roll back the entire table**

```sql
RESTORE TABLE doc_orders TO TIMESTAMP AS OF '2026-05-28 19:46:22';
```

After execution, the table is rolled back to the state at version 4 and amounts are restored to their correct values.

> ⚠️ **Note**: `RESTORE TABLE` overwrites the current state of the table. Any new data written after the erroneous operation will also be lost after the rollback. If legitimate new data was written after the incident, use the precise row restoration approach from Scenario 1 instead of a full table rollback.

## Scenario 3: Accidentally Dropped Table — UNDROP Recovery

A DBA accidentally ran DROP TABLE:

```sql
DROP TABLE doc_orders;
```

The table is gone and queries return `table or view not found`.

**Restore with a single command**:

```sql
UNDROP TABLE doc_orders;
```

After execution, the table and all its data are immediately restored, with the full version history intact.

> ⚠️ **Note**: `UNDROP TABLE` is only effective within the retention period (1 day by default). Once the retention period expires, historical versions are purged and cannot be recovered. For important tables, set a longer retention period in advance:
>
> ```sql
> ALTER TABLE doc_orders SET PROPERTIES ('data_retention_days' = '7');
> ```

> 💡 **Tip**: Whether the dropped object is a regular table, a Dynamic Table, a materialized view, or a Table Stream, the syntax to restore it is always `UNDROP TABLE`.

## Clean Up Resources

```sql
DROP TABLE IF EXISTS doc_orders;
```

## Key Takeaways

- **Always run `DESC HISTORY` before taking action**: Confirm the target version's timestamp before attempting recovery — don't estimate from memory
- **Timestamps must be literals**: `TIMESTAMP AS OF` does not support `NOW() - INTERVAL 1 HOUR`; you must provide an explicit time string
- **Three methods for three scenarios**: Use precise row restoration for accidentally deleted rows (preserves new data); use RESTORE for full-table corruption (simple but overwrites new data); use UNDROP for accidentally dropped tables (fastest)
- **Retention period determines the recovery window**: Default is 1 day; extend it in advance with `data_retention_days` for important tables, up to a maximum of 90 days
- **Singdata Lakehouse has write operation safety guards**: DELETE/UPDATE without a WHERE clause is rejected, but overly broad WHERE conditions still execute — Time Travel is the last line of defense

## Related Documentation

- [Time Travel Feature Overview](timetravel.md)
- [UNDROP TABLE](undrop-table.md)
- [RESTORE TABLE](restore.md)
- [DESC HISTORY](desc-history.md)
- [Historical Data Lookback Guide](SQL_Time_Travel_Guide.md)
