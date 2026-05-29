# Data Governance

Data governance features help you manage historical versions, lifecycle, and change tracking for your data. The core capability is Time Travel — based on the MVCC mechanism, every data change retains historical versions, allowing you to query the data state at any point in time, recover accidentally deleted data, or roll back unintended operations.

![](/.topwrite/assets/19-time-travel.png)

---

## This Section

| Page | Description |
|------|------|
| [Time Travel Overview](timetravel-summary.md) | Time Travel feature introduction, retention period configuration, supported operations |
| [Time Travel](om-time-travel.md) | Quick examples: query historical data, roll back a table, recover a dropped table |
| [Time Travel Concept](time-travel-concept.md) | MVCC working mechanism, three core capabilities (query/recover/rollback), typical scenarios |
| [Data Lifecycle Management](data-lifecycle.md) | Automatically reclaim expired data to control storage costs |

---

## Quick Reference

| What I want to do | Method | Reference |
|-----------|------|------|
| Query historical data at a specific point in time | SELECT ... TIMESTAMP AS OF '...' | [TIME TRAVEL](TIMETRAVEL.md) |
| View the version history of a table | `DESC HISTORY table_name` | [DESC HISTORY](desc-history.md) |
| Recover an accidentally dropped table | `UNDROP TABLE table_name` | [UNDROP TABLE](UNDROP-TABLE.md) |
| Roll back table data to a historical version | RESTORE TABLE ... TO TIMESTAMP AS OF '...' | [RESTORE TABLE](restore.md) |
| Set the number of days to retain historical data | ALTER TABLE ... SET PROPERTIES ('data_retention_days'='7') | [Time Travel Overview](timetravel-summary.md) |
| Automatically clean up expired data | ALTER TABLE ... SET PROPERTIES ('data_lifecycle'='30') | [Data Lifecycle Management](data-lifecycle.md) |

---

## Two Easily Confused Concepts

| Concept | Purpose | Parameter | Default |
|------|------|------|--------|
| `data_retention_days` | Controls how long Time Travel can access historical versions; versions older than this are physically deleted | 0–90 days | 1 day |
| `data_lifecycle` | Controls how long table data survives from its last modification time; data is automatically reclaimed after expiry | Positive integer (days) | Disabled (-1) |

> The two settings work independently: `data_retention_days` governs historical versions; `data_lifecycle` governs the survival time of current data.

---

## Common Scenarios

**Recovering after accidental data deletion**

```sql
-- Check the row count before the accidental deletion
SELECT COUNT(*) FROM orders TIMESTAMP AS OF '2024-01-15 09:59:00';

-- Roll the table back to before the deletion
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-15 09:59:00';
```

**Recovering after an accidental DROP TABLE**

```sql
-- View deleted tables
SHOW TABLES HISTORY LIKE 'orders%';

-- Recover the table
UNDROP TABLE orders;
```

**Tracing data change history**

```sql
-- View the version history of a table (operator, time, row count)
DESC HISTORY orders;
```

> ⚠️ `TIMESTAMP AS OF` only accepts literal constants; expressions like `NOW() - INTERVAL 1 DAY` are not supported.
