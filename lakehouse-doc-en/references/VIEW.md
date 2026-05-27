# VIEW

A view is a virtual table defined by a SQL query. By creating a view, you can query it just like a regular table. When a user queries a view, the query result will only include data from the tables and fields specified in the query that defines the view.

## Creating a View

```sql
CREATE VIEW [IF NOT EXISTS] [schema_name.]<view_name>
[ (column_list) ]
[ COMMENT 'comment' ]
AS <query>;
```

### Parameter Description

| Parameter | Description |
|-----------|-------------|
| `IF NOT EXISTS` | Optional. If the view already exists, skip without raising an error |
| `schema_name` | Optional. Specifies the schema to which the view belongs |
| `view_name` | The name of the view |
| `column_list` | Optional. Specifies the column names of the view; the number must match the number of columns in the query result |
| `COMMENT` | Optional. Adds a comment to the view |
| `query` | The SELECT query that defines the view |

### Examples

```sql
-- Create a basic view
CREATE VIEW v_sales AS
SELECT revenue - cost AS profit, (revenue - cost) * tax_rate AS tax_amount
FROM sales_table;

-- Create a view with a comment
CREATE VIEW v_sales_department COMMENT 'Sales department employee view' AS
SELECT id, name, position, salary
FROM employees
WHERE department = 'Sales';

-- Create an aggregation view
CREATE VIEW v_monthly_sales AS
SELECT DATE_TRUNC('month', sale_date) AS month, SUM(revenue) AS total_sales
FROM sales_data
GROUP BY month;
```

## Advantages of Views

1. **Simplify complex SQL queries**: By defining complex queries as views, you can query the view directly when needed without rewriting the complex query each time.
2. **Protect data**: Views can restrict user access to data in the underlying tables, allowing access only to the data defined in the view.
3. **Better data organization**: Views help you better organize and manage data, making it easier to understand and use.

## Limitations of Views

1. Views are read-only; DML operations (INSERT, UPDATE, DELETE) cannot be performed on views.
2. View performance may be affected by the data volume of the underlying tables and the complexity of the query.
3. Views do not store data; the underlying query is re-executed each time the view is queried.
4. Views do not support Time Travel queries.

## View Management

- [Create View](create-view.md): Create a view by specifying a SQL query.
- [Drop View](drop-view.md): Delete an existing view.
- [View Details](desc-view.md): View the structure and definition of a view.
- [List Views](show-views.md): List all views under a specified schema.

## Differences Between Views and Materialized Views

| Dimension | View | Materialized View |
|-----------|------|-------------------|
| Data Storage | Does not store data | Stores pre-computed results |
| Query Performance | Re-calculated on each query | Reads pre-stored results directly for better performance |
| Data Freshness | Real-time | Depends on refresh frequency |
| Storage Cost | None | Occupies storage space |
| Use Cases | Simple queries, logical abstraction | Complex aggregations, frequent queries |
