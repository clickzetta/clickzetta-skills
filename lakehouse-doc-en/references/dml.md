# Data Write and Modification

DML commands are used to write, update, and delete data in tables, and to merge changes from multiple data sources.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [INSERT INTO](INSERT.md) | Append rows to a table; supports VALUES and SELECT as sources |
| [UPDATE](update.md) | Modify column values in existing rows based on a condition |
| [DELETE](delete.md) | Delete rows from a table based on a condition |
| [MERGE INTO](merge.md) | Perform INSERT/UPDATE/DELETE on a target table based on match conditions; suited for CDC upsert scenarios |
| [TRUNCATE](truncate.md) | Clear all data from a table while preserving the table structure; more efficient than DELETE |

---

## Common Operations

### INSERT

```SQL
-- Insert a single row
INSERT INTO orders (order_id, customer_id, amount) VALUES (1001, 42, 299.00);

-- Insert from a query result
INSERT INTO orders_archive
SELECT * FROM orders WHERE created_at < '2024-01-01';

-- Overwrite write (clear then rewrite)
INSERT OVERWRITE orders_staging
SELECT * FROM orders WHERE status = 'PENDING';
```

### UPDATE

```SQL
-- Update based on condition
UPDATE orders
SET status = 'SHIPPED', updated_at = CURRENT_TIMESTAMP()
WHERE order_id = 1001;
```

### DELETE

```SQL
-- Delete based on condition
DELETE FROM orders WHERE status = 'CANCELLED' AND created_at < '2023-01-01';
```

### MERGE INTO (Upsert)

```SQL
-- CDC Upsert: update if matched, insert if not, delete if flagged
MERGE INTO orders AS target
USING orders_changes AS source
ON target.order_id = source.order_id
WHEN MATCHED AND source.op = 'D' THEN DELETE
WHEN MATCHED THEN UPDATE SET
  target.status = source.status,
  target.updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT (order_id, customer_id, amount, status, created_at)
  VALUES (source.order_id, source.customer_id, source.amount, source.status, source.created_at);
```

### TRUNCATE

```SQL
-- Clear a table (preserves table structure)
TRUNCATE TABLE orders_staging;
```

---

## Notes

- `INSERT OVERWRITE` clears the target table (or target partition) before rewriting — this operation is irreversible.
- The columns used in the `ON` condition of `MERGE INTO` should be unique; behavior is undefined if one source row matches multiple target rows.
- `TRUNCATE` is more efficient than `DELETE FROM table` (without WHERE) but is equally irreversible; Time Travel can restore data within the retention period.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [COPY INTO (Import)](copy-into-table.md) | Bulk import data from a Volume or external storage |
| [Table Stream](table-stream-title.md) | Capture DML changes for downstream consumption |
