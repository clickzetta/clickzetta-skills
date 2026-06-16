## CREATE VIEW

This command is used to create a new view in the current or specified schema based on query results from one or more existing tables. A view acts as a saved SQL query shortcut; it does not store data itself and executes the underlying SQL in real time on each query.

## Syntax

```Plain
CREATE [ OR REPLACE ] VIEW [ IF NOT EXISTS ] [schema_name.]view_name
    [ (column_name COMMENT 'comment' [, ...]) ]
    [ COMMENT 'comment' ]
    AS query;
```

## Parameter Description

- **OR REPLACE**: Replaces an existing view with the same name (if one exists). Cannot be used together with `IF NOT EXISTS`. The effect is equivalent to `DROP VIEW` followed by re-creating.
- **IF NOT EXISTS**: If a view with the same name already exists, the creation is skipped without error. Cannot be used together with `OR REPLACE`.
- **column_name**: Assign aliases or add comments to view columns. The number and order of columns must correspond one-to-one with the output columns of the `query`.
- **COMMENT**: Add descriptive information for the view, helping other users understand its purpose.
- **query**: The SQL query statement that defines the view content.

## Examples

### Example 1: Create a basic filter view

Create a view containing only high-value orders (amount greater than 500):

```SQL
CREATE OR REPLACE VIEW doc_test.v_high_value_orders AS
SELECT order_id, customer_id, amount
FROM doc_test.orders
WHERE amount > 500;
```

Query the view:

```SQL
SELECT * FROM doc_test.v_high_value_orders LIMIT 3;
```

Result:

```
order_id | customer_id | amount
---------|-------------|--------
1002     | 2           | 2999.00
1003     | 1           | 3499.00
1001     | 1           | 5999.00
```

### Example 2: Create a view with column comments and view comment

```SQL
CREATE OR REPLACE VIEW doc_test.v_completed_orders (
    order_id    COMMENT 'Order ID',
    customer_id COMMENT 'Customer ID',
    product     COMMENT 'Product Name',
    amount      COMMENT 'Order Amount'
)
COMMENT 'Completed orders view'
AS
SELECT order_id, customer_id, product, amount
FROM doc_test.orders
WHERE status = 'completed';
```

Query the view:

```SQL
SELECT * FROM doc_test.v_completed_orders;
```

Result:

```
order_id | customer_id | product | amount
---------|-------------|---------|--------
1001     | 1           | Laptop  | 5999.00
1003     | 1           | Tablet  | 3499.00
```

### Example 3: Use OR REPLACE to update view definition

Add a `status` column to an existing view:

```SQL
CREATE OR REPLACE VIEW doc_test.v_high_value_orders AS
SELECT order_id, customer_id, amount, status
FROM doc_test.orders
WHERE amount > 500;
```

### Example 4: Create a view in a specified schema

```SQL
CREATE VIEW my_schema.v_recent_orders AS
SELECT order_id, customer_id, amount
FROM my_schema.orders
WHERE order_date >= '2024-01-01';
```

### Example 5: Drop a view

```SQL
DROP VIEW IF EXISTS doc_test.v_high_value_orders;
```

## Notes

- `OR REPLACE` and `IF NOT EXISTS` cannot be used together.
- Views do not store data. Each query on a view executes the underlying SQL in real time, so query performance depends on the data volume and query complexity of the underlying tables.
- After dropping the underlying table, queries on views that depend on that table will error.
- Views cannot be restored via `UNDROP` after being dropped. Save the creation statement before dropping (use `SHOW CREATE TABLE <view_name>` to obtain it).

## View vs Dynamic Table vs Materialized View

| Object | Use Case |
|------|----------|
| **VIEW** | Encapsulate commonly used query logic; real-time computation on each query with no extra storage overhead |
| **Dynamic Table** | Pre-compute results to accelerate queries; supports incremental refresh; suitable for data processing with medium latency |
| **Materialized View** | Persist query results; suitable for high-frequency aggregate or complex computation scenarios |

## Related Commands

- [DROP VIEW](drop-view.md): Drop a view
- [SHOW TABLES WHERE is_view=true](show-views.md): List all views
- [SHOW CREATE TABLE](show-create-external-table.md): View the creation statement of a view
- [Views and Materialized Views](sql_view_guide.md): Comparison of view and materialized view usage scenarios, typical query acceleration patterns
