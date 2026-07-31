# Dynamic Masking

Dynamic Masking automatically masks sensitive columns (phone numbers, ID numbers, bank cards, etc.) based on **user roles**. The underlying data remains unchanged; different roles see different display formats.

## How It Works

At query time, the system dynamically replaces display values of sensitive columns based on the current user's role:
- Authorized roles (e.g., data administrators): see the full data
- Unauthorized roles (e.g., regular analysts): see masked data (e.g., `138****8888`)

The data in the storage layer is not modified; masking only occurs when query results are returned.

## Quick Example

```sql
-- Create a masking policy: replace middle 4 digits of phone number with ****
CREATE MASKING POLICY phone_mask
  AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('data_admin') THEN val
    ELSE REGEXP_REPLACE(val, '(\\d{3})\\d{4}(\\d{4})', '$1****$2')
  END;

-- Apply the masking policy to a column
ALTER TABLE users MODIFY COLUMN phone
  SET MASKING POLICY phone_mask;
```

## Comparison with Row-Level Permission

| Policy | Granularity | Effect |
|------|---------|------|
| **Dynamic Masking** | Column-level | Data is visible but partially hidden (e.g., `138****8888`) |
| Row-Level Permission | Row-level | Rows that don't match conditions are completely invisible |

## Related Documents

- [Dynamic Masking Details](dynamic-mask.md)
- [Row-Level Permission](row-filter.md)
- [Network Policy](om-network-policy.md)
