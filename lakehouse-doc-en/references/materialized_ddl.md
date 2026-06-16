# Materialized Views

Materialized view DDL commands are used to create, refresh, alter, and drop materialized view objects that store pre-computed results.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [CREATE MATERIALIZED VIEW](create-materialized-view.md) | Create a materialized view based on a SELECT query; supports automatic refresh |
| [ALTER MATERIALIZED VIEW](alter-materialized-view.md) | Modify the refresh schedule or properties of a materialized view |
| [REFRESH MATERIALIZED VIEW](refresh-materialized-view.md) | Manually trigger a materialized view refresh to update pre-computed data |
| [DROP MATERIALIZED VIEW](drop-materialized-view.md) | Drop a materialized view and its stored data |
| [UNDROP MATERIALIZED VIEW](undrop-materialized-view.md) | Restore a dropped materialized view (within the data retention period) |
| [DESC MATERIALIZED VIEW](desc-materialized-view.md) | View the column definitions and refresh status of a materialized view |
| [SHOW MATERIALIZED VIEWS](show-materialized-view.md) | List all materialized views in the current schema |
| [SHOW CREATE MATERIALIZED VIEW](show-create-materialized-view.md) | View the full statement used to create a materialized view |

---

## Common Operations

### Create a Materialized View

```SQL
-- Create a materialized view with automatic refresh
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_daily_sales AS
SELECT DATE_TRUNC('day', created_at) AS sale_date,
       SUM(amount) AS total_amount,
       COUNT(*) AS order_count
FROM public.orders
GROUP BY 1;

-- Specify a refresh interval
CREATE MATERIALIZED VIEW public.mv_category_stats
REFRESH INTERVAL 30 MINUTE
AS
SELECT category, COUNT(*) AS cnt, AVG(price) AS avg_price
FROM public.products
GROUP BY category;
```

### Manual Refresh

```SQL
-- Manually trigger a refresh
REFRESH MATERIALIZED VIEW public.mv_daily_sales;
```

### Modify Refresh Configuration

```SQL
-- Change the refresh interval (requires CREATE OR REPLACE)
CREATE OR REPLACE MATERIALIZED VIEW public.mv_daily_sales
    REFRESH INTERVAL 60 MINUTE VCLUSTER default
    AS SELECT date_trunc('day', order_date) AS day, SUM(amount) AS total FROM orders GROUP BY 1;

-- Suspend automatic refresh
ALTER MATERIALIZED VIEW public.mv_daily_sales SUSPEND;

-- Resume automatic refresh
ALTER MATERIALIZED VIEW public.mv_daily_sales RESUME;
```

### View and Manage

```SQL
-- List all materialized views
SHOW MATERIALIZED VIEWS;

-- View materialized view status
DESC MATERIALIZED VIEW public.mv_daily_sales;

-- View the creation statement
SHOW CREATE MATERIALIZED VIEW public.mv_daily_sales;

-- Drop a materialized view
DROP MATERIALIZED VIEW IF EXISTS public.mv_daily_sales;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [Materialized Views (Object Model)](materializedview.md) | How materialized views work, query rewriting, and selection guidance |
| [Dynamic Tables](dynamic-table.md) | Consider dynamic tables for data processing pipeline scenarios |
