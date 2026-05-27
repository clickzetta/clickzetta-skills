# Row-Level Permission

Row-Level Security ensures that when different users query the same table, they can only see **rows within their permission scope**, while other rows remain invisible to them.

## How It Works

By creating a row access policy, you define which roles or users can access which rows. Once the policy is bound to a table, the system automatically appends filtering conditions to the WHERE clause during queries, transparent to the user.

## Typical Scenarios

- **Multi-tenant data isolation**: The same orders table allows different merchants to see only their own orders
- **Regional data isolation**: Sales personnel can only view data for their assigned regions
- **Tiered data access**: Regular employees can only see public data, while management can see all data

## Quick Example

```sql
-- Create a row access policy: users can only see their own orders
CREATE ROW ACCESS POLICY order_policy
  AS (merchant_id BIGINT) RETURNS BOOLEAN ->
  merchant_id = CURRENT_MERCHANT_ID()
  OR CURRENT_ROLE() = 'platform_admin';

-- Bind the policy to a table
ALTER TABLE orders ADD ROW ACCESS POLICY order_policy ON (merchant_id);
```

## Comparison with Dynamic Masking

| Policy | Effect |
|------|------|
| **Row-Level Permission** | Rows that do not meet the criteria are **completely invisible** |
| Dynamic Masking | Rows are visible, but sensitive column content is **partially hidden** |

## Related Documentation

- [Row-Level Permission Details](row_level_permission.md)
- [Dynamic Masking](om-dynamic-mask.md)
