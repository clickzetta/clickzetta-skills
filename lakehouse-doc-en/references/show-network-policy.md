# SHOW NETWORK POLICY

## Overview

Lists all network policies in the current instance along with their status. Requires instance administrator (`instance_admin`) privileges.

## Syntax

```Plain
SHOW NETWORK POLICY
```

## Return Columns

| Column | Description |
|--------|-------------|
| `name` | Policy name |
| `creator` | Username of the creator |
| `status` | Policy status: `active` or `inactive` |
| `created_time` | Creation time, format `yyyy-mm-dd hh:mm:ss` |

## Examples

```sql
SHOW NETWORK POLICY;
```

Sample output:

| name | creator | status | created_time |
|------|---------|--------|--------------|
| corp_policy | admin | active | 2024-03-01 10:00:00 |
| dev_policy | admin | inactive | 2024-06-15 14:30:00 |

## Related Documentation

- [DESC NETWORK POLICY](desc-network-policy.md) — view the IP list details of a specific policy
- [CREATE NETWORK POLICY](create-network-policy.md) — create a policy
- [ALTER NETWORK POLICY](alter-network-policy.md) — modify a policy
- [Network Policy](network_policy.md) — how it works and usage guide
