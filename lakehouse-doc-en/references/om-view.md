# View

A View is a **virtual table that stores no data** — it is essentially a saved SQL query. Each time a view is queried, the system executes the underlying SQL in real time and returns the results.

Think of a view as a "saved query template" — you write a complex SQL statement, give it a name, and query it by that name from then on. Unlike a Materialized View: a Materialized View pre-computes and stores results (uses storage but queries are fast), while a View stores no data at all (zero storage cost but recomputed on every query).

## Selection Reference

| Aspect | View | Materialized View | Dynamic Table |
|--------|------|----------|--------|
| Data storage | No storage | Stores pre-computed results | Stores computed results |
| Query performance | Same as underlying tables | High (reads results directly) | High (reads results directly) |
| Data freshness | Real-time | Within refresh interval | Within refresh interval |
| Suitable scenarios | Logic encapsulation, permission isolation | Query acceleration | Data processing pipelines |

**When to use a View**: Encapsulating complex JOIN logic, exposing only certain columns externally (permission isolation), and scenarios where data storage is not needed.

**When not to use a View**: If query performance is a bottleneck → use a Materialized View. If you need automatic incremental computation → use a Dynamic Table.

## Core Features

**Zero storage cost**: A view only saves the SQL definition and occupies no storage space.

**Real-time data**: Every query against a view executes the underlying SQL in real time, returning the latest data.

**Read-only**: Views do not support DML operations such as INSERT, UPDATE, or DELETE.

**No Time Travel support**: Views cannot query historical versions of data.

## Quick Examples

### Encapsulating Complex JOINs

```sql
-- Create source tables
CREATE TABLE IF NOT EXISTS users (
    user_id   BIGINT,
    username  STRING,
    city      STRING,
    phone     STRING
);

CREATE TABLE IF NOT EXISTS orders (
    order_id  BIGINT,
    user_id   BIGINT,
    amount    DECIMAL(10,2)
);

-- Insert test data
INSERT INTO users VALUES (1, 'Alice', 'Beijing', '13800000001');
INSERT INTO orders VALUES (101, 1, 99.00);

-- Create a view: encapsulate JOIN logic
CREATE VIEW v_order_detail AS
SELECT u.username, o.order_id, o.amount
FROM users u
JOIN orders o ON u.user_id = o.user_id;

-- Query the view
SELECT * FROM v_order_detail;
-- Result:
-- +----------+----------+--------+
-- | username | order_id | amount |
-- +----------+----------+--------+
-- | Alice    | 101      | 99.00  |
-- +----------+----------+--------+
```

### Permission Isolation (Hiding Sensitive Columns)

```sql
-- Create a view: expose only public fields, hide sensitive columns like phone
CREATE VIEW v_user_public AS
SELECT user_id, username, city
FROM users;

-- View the view's structure
DESC VIEW v_user_public;
-- Result:
-- +-------------+-----------+---------+
-- | column_name | data_type | comment |
-- +-------------+-----------+---------+
-- | user_id     | bigint    |         |
-- | username    | string    |         |
-- | city        | string    |         |
-- +-------------+-----------+---------+
```

### Permission Isolation (Row-Level Data Filtering)

```sql
-- Source table contains sales data for all regions
CREATE TABLE IF NOT EXISTS sales_all_regions (
    region      STRING,
    salesperson STRING,
    amount      DECIMAL(10,2)
);

INSERT INTO sales_all_regions VALUES
    ('North', 'Alice', 5000),
    ('North', 'Bob', 3000),
    ('South', 'Carol', 4000),
    ('South', 'Dave', 6000);

-- Create a view for the North region sales team — they can only see North region data
CREATE VIEW v_sales_north AS
SELECT salesperson, amount
FROM sales_all_regions
WHERE region = 'North';

-- North region sales team queries the view
SELECT * FROM v_sales_north;
-- Result:
-- +-------------+---------+
-- | salesperson | amount  |
-- +-------------+---------+
-- | Alice       | 5000.00 |
-- | Bob         | 3000.00 |
-- +-------------+---------+

-- Similarly, create v_sales_south for the South region — same table, different rows for different users
```

> 💡 **Tip**: **View vs. Dynamic Data Masking**: Views are a quick way to implement row- and column-level permission isolation with no extra configuration. For finer-grained dynamic access control (e.g., automatically masking sensitive columns based on user roles), use the Lakehouse's [Dynamic Data Masking](om-dynamic-mask.md).

## Common Issues

### Issue 1: View Performance Degrades as Underlying Data Grows

**Problem**: The view's underlying query involves complex JOINs or aggregations, and query performance degrades as the underlying table data grows.

**Symptom**: View queries are fast with small data volumes, but time out after data reaches the TB scale.

**Solution**:
- Views are suited for logic encapsulation, not performance optimization
- When query performance becomes a bottleneck, switch to a Materialized View (pre-computes and stores results)
- Or switch to a Dynamic Table (incremental computation with automatic refresh)

### Issue 2: Underlying Table Schema Changes Invalidate the View

**Problem**: A table the view depends on is dropped, or a column name is changed.

**Symptom**: Querying the view produces `table or view not found` or `column not found` errors.

**Solution**:
- Views do not check whether the underlying tables exist; a successful creation does not guarantee permanent validity
- Before modifying an underlying table's schema, use `DESC VIEW` to identify which views depend on it
- Add COMMENT to important views to document their dependencies

### Issue 3: Attempting DML Operations on a View

**Problem**: Running `INSERT INTO v_user_public VALUES (...)` on a view.

**Symptom**: Error: `view is read-only`.

**Solution**:
- Views are read-only and do not support INSERT/UPDATE/DELETE
- To write data, operate directly on the underlying base table

## Cost Implications

### Storage Cost

- A view only saves the SQL definition — essentially zero storage cost

### Compute Cost

- Every query against a view re-executes the underlying SQL, consuming VCluster CRU
- Complex views (multi-table JOINs, aggregations) are fully recomputed on every query, which can be costly

> 💡 **Tip**: For detailed billing rules, refer to the [Billing Documentation](Billing.md).

## Lifecycle Management

```
Create View → Query → Underlying Table Changes → View Invalidated/Rebuilt → Drop View
     ↓           ↓              ↓                         ↓                     ↓
  Save SQL   Real-time exec  Column/table changes    Error or wrong results   DROP VIEW
```

### Creating and Dropping

```sql
-- Create a view
CREATE VIEW my_view AS SELECT ...;

-- View the view's definition
DESC VIEW my_view;

-- Drop the view
DROP VIEW my_view;
```

## Related Documentation

- [CREATE VIEW](view.md) — Complete syntax
- [Materialized View](MATERIALIZEDVIEW.md) — When you need to store pre-computed results
- [Dynamic Table](om-dynamic-table.md) — When you need incremental computation with automatic refresh
- [Semantic View](om-semantic-view.md) — Semantic layer for business analysis
