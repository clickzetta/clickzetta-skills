# View

A View is a **virtual table that does not store data**, essentially a saved SQL query. Each time a view is queried, the system executes the underlying SQL in real time and returns the results.

## Type Selection Reference

| Comparison Item | View | Materialized View | Dynamic Table |
|--------|------|----------|--------|
| Data storage | No storage | Stores data | Stores data |
| Query performance | Same as underlying tables | High (pre-computed) | High (pre-computed) |
| Data freshness | Real-time | Within refresh interval | Within refresh interval |
| Suitable scenarios | Logic encapsulation, permission isolation | Query acceleration | Data processing pipelines |

**When to use a view**: Encapsulating complex JOIN logic, exposing only certain columns externally (permission isolation), and scenarios where data storage is not needed.

## Typical Use Cases

- **Simplify queries**: Encapsulate multi-table JOINs as views so business users can query the view directly
- **Permission isolation**: Expose only certain columns to specific users, hiding sensitive fields
- **Logic reuse**: Define common calculation logic once and reference it in multiple places

## Quick Example

```sql
-- Create a view: hide sensitive fields
CREATE VIEW v_user_public AS
SELECT user_id, username, city
FROM users;
-- Do not expose sensitive columns like phone, id_card

-- Create a view: encapsulate complex JOINs
CREATE VIEW v_order_detail AS
SELECT o.order_id, u.username, p.product_name, o.amount
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN products p ON o.product_id = p.product_id;
```

## Related Documentation

- [CREATE VIEW](VIEW.md) — Full syntax
- [Materialized View](MATERIALIZEDVIEW.md) — When you need to store pre-computed results
- [Semantic View](semantic-view-overview.md) — Semantic layer for business analysis
