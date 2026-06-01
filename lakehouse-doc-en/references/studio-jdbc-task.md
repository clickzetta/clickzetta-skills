# Studio JDBC Task Development Guide

Studio JDBC tasks connect to external databases via the JDBC protocol and execute SQL in those external databases. They are suitable for two scenarios:

- **Pre-sync exploration**: Before configuring a sync task, use a JDBC task to understand the source database's table structure, data volume, and field distribution to determine whether it is suitable for syncing
- **Data source issue investigation**: When a sync task errors or data is anomalous, execute diagnostic SQL directly in the source database to locate null values, anomalous values, duplicate data, and other issues

> ⚠️ **Note**: SQL in a JDBC task executes in the external database. Query results are displayed in the task log. Writing query results directly to Lakehouse is not supported, nor is referencing Lakehouse tables within a JDBC task.

---

## Core Mechanism

A JDBC task file can contain multiple SQL statements, executed sequentially in order, with each statement ending in `;`. Execution results (rows returned by SELECT) are visible in the Studio task log.

**Data source configuration**: JDBC tasks require an external database connection to be pre-configured in Studio under **Management → Data Sources**. At execution time, specify the data source name with `--datasource` and the database name with `--database`.

> ⚠️ **Supported data sources**: This article uses MySQL as an example, verified through actual testing. Support for other data sources such as Hive and ClickHouse is subject to the Studio data source configuration page.

---

## Scenario 1: Pre-Sync Exploration

Before configuring a batch sync task, use a JDBC task to understand the basic state of the source database.

### SQL Script

```sql
-- View the field structure of the target table
SELECT
    column_name,
    column_type,
    is_nullable,
    column_key,
    column_default
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND table_name = 'orders'
ORDER BY ordinal_position;

-- View data volume and time range
SELECT
    COUNT(*)        AS total_rows,
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date,
    COUNT(DISTINCT user_id) AS unique_users
FROM orders;

-- View distribution by status
SELECT status, COUNT(*) AS cnt
FROM orders
GROUP BY status
ORDER BY cnt DESC;

-- Sample the data
SELECT * FROM orders ORDER BY order_id DESC LIMIT 10;
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **JDBC** type, and enter a task name
2. Select the pre-configured external database connection from the **Data Source** dropdown, then select the corresponding database name
3. Paste the SQL script above
4. Click **Run** and view the results in the task log

**cz-cli** (see [Studio Task Development and Operations](cz-cli-studio-tasks.md))

```bash
cz-cli task create explore_orders --type jdbc --profile <your-profile>
cz-cli task save-content explore_orders --file explore.sql --profile <your-profile>
cz-cli task save-config explore_orders --retry-count 1 --profile <your-profile>
cz-cli task online explore_orders -y --profile <your-profile>
cz-cli task execute explore_orders \
  --datasource <datasource_name> \
  --database <database_name> \
  --profile <your-profile>
```

---

## Scenario 2: Data Source Issue Investigation

When a sync task errors or data is anomalous, use a JDBC task to diagnose directly in the source database. The following SQL covers the most common types of issues.

### Test Data Preparation

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS doc_orders_raw (
    order_id   INT PRIMARY KEY,
    user_id    INT,
    product    VARCHAR(50),
    amount     DECIMAL(10,2),
    status     VARCHAR(20),
    order_date DATE
);

-- Insert normal data
INSERT INTO doc_orders_raw VALUES
(1001, 101, 'iPhone',   7999.00, 'paid',      '2024-12-01'),
(1002, 102, 'MacBook',  14999.00,'paid',      '2024-12-01'),
(1003, 101, 'AirPods',  1799.00, 'pending',   '2024-12-01'),
(1004, 103, 'iPad',     8999.00, 'paid',      '2024-12-01'),
(1005, 102, 'Watch',    3299.00, 'cancelled', '2024-12-01');

-- Insert problematic data (simulating real-world scenarios)
INSERT INTO doc_orders_raw VALUES
(2001, NULL,  'iPhone',  7999.00, 'paid',    '2024-12-03'),  -- user_id is null
(2002, 106,   NULL,      5999.00, 'paid',    '2024-12-03'),  -- product is null
(2003, 107,   'MacBook', -100.00, 'paid',    '2024-12-03'),  -- negative amount
(2004, 108,   'iPad',    8999.00, 'unknown', '2024-12-03'),  -- invalid status value
(2005, 109,   'Watch',   3299.00, 'paid',    '2024-12-03'),  -- duplicate row
(2006, 109,   'Watch',   3299.00, 'paid',    '2024-12-03');  -- duplicate row
```

### Diagnostic SQL Script

```sql
-- ── 1. Overall data quality overview ─────────────────────────────────────
SELECT
    COUNT(*)                                                    AS total_rows,
    COUNT(DISTINCT order_id)                                    AS unique_orders,
    COUNT(*) - COUNT(DISTINCT order_id)                         AS duplicate_pks,
    SUM(CASE WHEN user_id IS NULL OR user_id = 0 THEN 1 END)   AS null_user_id,
    SUM(CASE WHEN product IS NULL OR product = '' THEN 1 END)  AS null_product,
    SUM(CASE WHEN amount <= 0 THEN 1 END)                      AS invalid_amount,
    SUM(CASE WHEN status NOT IN ('paid','pending','cancelled')
             THEN 1 END)                                        AS invalid_status
FROM doc_orders_raw;

-- ── 2. List all anomalous records ─────────────────────────────────────────
SELECT order_id, user_id, product, amount, status, order_date,
    CASE
        WHEN user_id IS NULL OR user_id = 0 THEN 'null_user_id'
        WHEN product IS NULL OR product = '' THEN 'null_product'
        WHEN amount <= 0                     THEN 'invalid_amount'
        WHEN status NOT IN ('paid','pending','cancelled') THEN 'invalid_status'
    END AS issue_type
FROM doc_orders_raw
WHERE user_id IS NULL OR user_id = 0
   OR product IS NULL OR product = ''
   OR amount <= 0
   OR status NOT IN ('paid','pending','cancelled')
ORDER BY order_id;

-- ── 3. Duplicate data check (same user, same product, same day) ───────────
SELECT user_id, product, order_date, COUNT(*) AS cnt
FROM doc_orders_raw
GROUP BY user_id, product, order_date
HAVING COUNT(*) > 1
ORDER BY cnt DESC;

-- ── 4. Data distribution check (for determining sync scope) ──────────────
SELECT
    order_date,
    COUNT(*)                                    AS total,
    SUM(CASE WHEN status = 'paid' THEN 1 END)   AS paid,
    SUM(CASE WHEN status = 'pending' THEN 1 END) AS pending,
    ROUND(SUM(amount), 2)                       AS total_amount
FROM doc_orders_raw
GROUP BY order_date
ORDER BY order_date;
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **JDBC** type
2. Select the data source and database name
3. Paste the diagnostic SQL and click **Run**
4. View the results of each SQL statement in the task log to locate issues

**cz-cli**

```bash
cz-cli task create diagnose_orders --type jdbc --profile <your-profile>
cz-cli task save-content diagnose_orders --file diagnose.sql --profile <your-profile>
cz-cli task online diagnose_orders -y --profile <your-profile>
cz-cli task execute diagnose_orders \
  --datasource <datasource_name> \
  --database <database_name> \
  --profile <your-profile>
```

### Execution Results

**Overall data quality overview** (SQL 1):

```
total_rows  unique_orders  duplicate_pks  null_user_id  null_product  invalid_amount  invalid_status
11          10             1              1             1             1               1
```

**Anomalous record details** (SQL 2):

```
order_id  user_id  product  amount   status   order_date   issue_type
2001      null     iPhone   7999.00  paid     2024-12-03   null_user_id
2002      106      null     5999.00  paid     2024-12-03   null_product
2003      107      MacBook  -100.00  paid     2024-12-03   invalid_amount
2004      108      iPad     8999.00  unknown  2024-12-03   invalid_status
```

**Duplicate data** (SQL 3):

```
user_id  product  order_date   cnt
109      Watch    2024-12-03   2
```

**Data distribution** (SQL 4):

```
order_date   total  paid  pending  total_amount
2024-12-01   5      3     1        36095.00
2024-12-03   6      5     0        30494.00
```

---

## Notes

- SQL in a JDBC task executes in the external database, not through the Lakehouse engine; syntax follows the external database's dialect
- Query results are only displayed in the task log and are not written to Lakehouse
- Referencing Lakehouse tables within a JDBC task is not supported (cross-database federated queries are not supported)
- After completing the diagnosis, decide based on the issues found whether to fix the data in the source database before configuring the sync task

---

## Related Documentation

- [Task Parameter Syntax Reference](task_param_reference.md)
- [Studio Batch Sync Tasks](batch_sync_sop.md)
- [Studio Shell Task Development Guide](studio-shell-task.md)
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md)
