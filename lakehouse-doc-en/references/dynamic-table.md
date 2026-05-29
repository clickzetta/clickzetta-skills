# Dynamic Table

Dynamic Table DDL commands are used to create, modify, query, and delete dynamic table objects that auto-incrementally refresh based on SQL queries.

---

## This Chapter

| Page | Description |
|------|-------------|
| [Dynamic Table Introduction](dynamic-table-introduce.md) | How dynamic tables work, the incremental refresh mechanism, and differences from materialized views |
| [CREATE DYNAMIC TABLE](create-dynamic-table.md) | Create a dynamic table, specifying refresh interval and defining SQL |
| [ALTER DYNAMIC TABLE](alter-dynamic-table.md) | Modify refresh interval, suspend/resume refresh, rename |
| [DYNAMIC TABLE DML](dynamic-table-dml-sql.md) | DML operations supported by dynamic tables (direct writes allowed in some scenarios) |
| [DROP DYNAMIC TABLE](drop-dynamic-table.md) | Delete a dynamic table and its data |
| [RESTORE DYNAMIC TABLE](restore-dynamic-table.md) | Roll back a dynamic table to a historical version |
| [UNDROP DYNAMIC TABLE](undrop-dynamic-table.md) | Recover a deleted dynamic table (within the data retention period) |
| [DESC DYNAMIC TABLE](desc-dynamic-table.md) | View a dynamic table's column definitions and refresh status |
| [DESC HISTORY DYNAMIC TABLE](desc-history-dynamic-table.md) | View a dynamic table's list of historical versions |
| [SHOW DYNAMIC TABLES](show-dynamic-table.md) | List all dynamic tables under the current schema |
| [SHOW CREATE DYNAMIC TABLE](show-create-dynamic-table.md) | View the complete statement used to create a dynamic table |
| [SHOW DYNAMIC TABLE REFRESH HISTORY](refresh-history.md) | View a dynamic table's refresh history to monitor refresh status and duration |

---

## Common Operations

### Create a Dynamic Table

```SQL
-- Basic dynamic table (refresh every 10 minutes)
CREATE OR REPLACE DYNAMIC TABLE public.dws_category_sales
REFRESH INTERVAL 10 MINUTE
VCLUSTER default
AS
SELECT p.category,
       COUNT(*)          AS order_cnt,
       SUM(o.quantity)   AS total_quantity
FROM public.orders o
JOIN public.products p ON o.product_id = p.product_id
GROUP BY p.category;
```

### Modify Refresh Configuration

```SQL
-- Change refresh interval
ALTER DYNAMIC TABLE public.dws_category_sales SET REFRESH INTERVAL 30 MINUTE;

-- Suspend automatic refresh
ALTER DYNAMIC TABLE public.dws_category_sales SUSPEND;

-- Resume automatic refresh
ALTER DYNAMIC TABLE public.dws_category_sales RESUME;
```

### Manual Refresh

```SQL
-- Trigger a refresh immediately
REFRESH DYNAMIC TABLE public.dws_category_sales;
```

### View and Monitor

```SQL
-- View all dynamic tables
SHOW DYNAMIC TABLES;

-- View dynamic table status and refresh configuration
DESC DYNAMIC TABLE public.dws_category_sales;

-- View refresh history (last 10 runs)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'dws_category_sales' LIMIT 10;
```

### Delete and Restore

```SQL
-- Delete dynamic table
DROP DYNAMIC TABLE IF EXISTS public.dws_category_sales;

-- Restore deleted dynamic table
UNDROP DYNAMIC TABLE public.dws_category_sales;
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [Dynamic Table (Object Model)](om-dynamic-table.md) | Dynamic table mental model, incremental refresh principles, and data pipeline construction |
| [Materialized View](materialized_ddl.md) | Use materialized views for query acceleration (transparent rewriting) scenarios |
| [Table Stream](table-stream-title.md) | Capture changes from dynamic tables for downstream consumption |
