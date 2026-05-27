# Synonym

A Synonym creates an **alias** for data objects (tables, views, etc.) in the Lakehouse, allowing the same object to be accessed by different names without duplicating data.

## Typical Use Cases

| Scenario | Description |
|------|------|
| Simplify cross-schema references | Create synonyms for tables in other schemas, eliminating the need to write fully qualified paths in queries |
| Compatibility with old names | After renaming a table, create a synonym with the old name so existing SQL does not need modification |
| Simplify external table access | Create short names for external tables with complex paths |

## Quick Example

```sql
-- Create a synonym for a table in another schema
CREATE SYNONYM orders FOR ods.raw_orders;

-- Now you can query with "orders" directly, without writing "ods.raw_orders"
SELECT * FROM orders WHERE order_date = '2024-01-01';
```

## Related Documentation

- [CREATE SYNONYM](synonym.md) — Full syntax
