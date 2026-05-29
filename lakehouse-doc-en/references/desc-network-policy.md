# DESC NETWORK POLICY

## Overview

Displays the IP allowlist and blocklist details of a specified network policy. Requires instance administrator (`instance_admin`) privileges.

## Syntax

```Plain
DESC NETWORK POLICY <name>
```

## Parameters

- `<name>`: The name of the network policy to query.

## Return Columns

| Column | Description |
|--------|-------------|
| `name` | Policy name |
| `allowed_ip_list` | Allowlist of IPs/CIDRs, comma-separated |
| `blocked_ip_list` | Blocklist of IPs/CIDRs, comma-separated; empty means no blocklist is set |

## Examples

```sql
DESC NETWORK POLICY corp_policy;
```

Sample output:

| info_name | info_value |
|-----------|------------|
| name | corp_policy |
| allowed_ip_list | 192.168.1.0/24,10.0.0.1 |
| blocked_ip_list | 192.168.1.99 |

## Related Documentation

- [SHOW NETWORK POLICY](show-network-policy.md) — list all policies
- [ALTER NETWORK POLICY](alter-network-policy.md) — modify IP lists
- [Network Policy](network_policy.md) — how it works and usage guide
