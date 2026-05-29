# Network Policy

Network Policy restricts access to Lakehouse by source IP through **IP whitelisting**, preventing unauthorized network access.

## How It Works

After creating a network policy, only IP addresses in the whitelist can connect to the Lakehouse instance. Different network policies can be applied to the entire instance or to specific users.

## Quick Example

```sql
-- Create a network policy: allow only specified IP ranges
CREATE NETWORK POLICY office_policy
  ALLOWED_IP_LIST = ('192.168.1.0/24', '10.0.0.1');

-- Apply the network policy to a user
ALTER USER analyst SET NETWORK_POLICY = office_policy;
```

## Relationship with Other Security Policies

| Policy | Control Dimension | Description |
|------|---------|------|
| **Network Policy** | Access source (IP) | Restricts which IPs can connect |
| Dynamic Masking | Data content (column-level) | Masks sensitive columns based on role |
| Row-Level Permission | Data scope (row-level) | Different users only see rows within their permission scope |
| Role Permissions | Operation permissions | Controls what operations users can perform |

## Related Documents

- [Network Policy Details](network_policy.md)
- [Dynamic Masking](om-dynamic-mask.md)
- [Row-Level Permission](om-row-level-permission.md)
