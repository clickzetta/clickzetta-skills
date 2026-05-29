# Lakehouse Table Cloning and Fast Backup Guide

## Overview

In data warehouse operations, you often need to quickly create table copies for testing, backup, or data recovery. Singdata Lakehouse provides the `CREATE TABLE ... CLONE` syntax, supporting zero-copy cloning that instantly creates table replicas without copying the actual data. This guide categorizes by business scenario to help you quickly master efficient table cloning methods.

### Quick Navigation

* [Full Table Clone](#full-table-clone) -- Clone table structure and all data
* [Point-in-time Clone](#point-in-time-clone) -- Clone the table state at a specific point in time
* [Clone Structure Only](#clone-structure-only) -- Clone structure without data using LIKE
* [Post-clone Verification](#post-clone-verification) -- Confirm clone results match the source table
* [Clone and Independent Modification](#clone-and-independent-modification) -- Verify cloned table independence

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE TABLE ... CLONE` | Zero-copy table cloning | Fast backup, test environment setup |
| `CREATE TABLE ... CLONE ... AT` | Point-in-time clone | Restore to a historical state |
| `CREATE TABLE ... LIKE` | Clone table structure only | Create an empty table for data loading |

***

## Prerequisites

The following examples use a simulated orders table `orders_clone`:

```sql
-- Create source table
CREATE TABLE IF NOT EXISTS orders_clone (
    order_id INT,
    customer_id INT,
    amount DOUBLE,
    order_date DATE
);

-- Insert test data
INSERT INTO orders_clone VALUES
(1, 101, 500, '2024-06-01'),
(2, 102, 300, '2024-06-02'),
(3, 103, 800, '2024-06-03');
```

***

## Full Table Clone

Use `CREATE TABLE ... CLONE` to instantly create a replica of the table. The cloned table shares underlying data files with the source, consuming no additional storage space (until you perform write operations on the cloned table).

```sql
-- Clone the table
CREATE TABLE orders_clone_backup CLONE orders_clone;
```

**Result Verification**:

```sql
SELECT * FROM orders_clone_backup ORDER BY order_id;
```

| order_id | customer_id | amount | order_date |
|----------|-------------|--------|------------|
| 1 | 101 | 500 | 2024-06-01 |
| 2 | 102 | 300 | 2024-06-02 |
| 3 | 103 | 800 | 2024-06-03 |

> 💡 **Tip**: Zero-copy cloning is a core Lakehouse feature. The clone operation completes instantly, regardless of table size.

***

## Point-in-time Clone

Use the `AT` clause to clone the table state at a specific point in time, commonly used to restore to a historical version.

```sql
-- Clone the table state from 1 minute ago
CREATE TABLE orders_clone_history CLONE orders_clone 
TIMESTAMP AS OF (CURRENT_TIMESTAMP() - INTERVAL '1' MINUTE);
```

**Use Cases**:
* Restore to a previous state after erroneous operations
* Audit historical data
* Compare data changes

> ⚠️ **Note**: The point in time must be within the Time Travel retention period (default 1 day).

***

## Clone Structure Only

Use the `LIKE` syntax to clone the table structure without copying data, suitable for creating empty tables for subsequent data loading.

```sql
-- Clone table structure only
CREATE TABLE orders_clone_empty LIKE orders_clone;
```

**Result Verification**:

```sql
SELECT COUNT(*) FROM orders_clone_empty;
```

| COUNT(*) |
|----------|
| 0 |

***

## Post-clone Verification

After cloning, it is recommended to verify consistency between the cloned table and the source table.

```sql
-- Compare row counts
SELECT 
    (SELECT COUNT(*) FROM orders_clone) as source_count,
    (SELECT COUNT(*) FROM orders_clone_backup) as clone_count;
```

**Result Explanation**:

| source_count | clone_count |
|--------------|-------------|
| 3 | 3 |

***

## Clone and Independent Modification

Once created, the cloned table is independent -- modifications to the cloned table will not affect the source table.

```sql
-- Insert new data into the cloned table
INSERT INTO orders_clone_backup VALUES (4, 104, 600, '2024-06-04');

-- Compare source and cloned tables
SELECT 'source' as tbl, COUNT(*) as cnt FROM orders_clone
UNION ALL
SELECT 'clone' as tbl, COUNT(*) as cnt FROM orders_clone_backup;
```

**Result Explanation**:

| tbl | cnt |
|-----|-----|
| source | 3 |
| clone | 4 |

> ⚠️ **Note**: When performing write operations on the cloned table, Lakehouse creates independent data files for the new data, without affecting the source table's shared files.

***

## Clean Up Test Data

After completing clone verification, it is recommended to clean up test tables:

```sql
-- Drop test tables
DROP TABLE IF EXISTS orders_clone;
DROP TABLE IF EXISTS orders_clone_backup;
DROP TABLE IF EXISTS orders_clone_history;
DROP TABLE IF EXISTS orders_clone_empty;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Zero-copy Property**: Cloned tables share data files with the source, consuming no additional storage space (until new data is written).
2. **Time Travel Dependency**: Point-in-time cloning depends on Time Travel functionality and must be within the retention period.
3. **Permission Inheritance**: Cloned tables do not automatically inherit source table permissions; separate configuration is required.
4. **Dynamic Table Cloning**: Dynamic Tables can also be cloned, but the clone becomes a regular table and no longer auto-refreshes.
5. **Materialized View Cloning**: Materialized views also become regular tables after cloning.

***

## Related Documentation

* [CREATE...CLONE](clone-doc.md)
* [Time Travel](TIMETRAVEL.md)
* [UNDROP TABLE](UNDROP-TABLE.md)
