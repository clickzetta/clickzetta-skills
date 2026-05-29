# CREATE NETWORK POLICY

## Overview

Creates a network policy that restricts access to the Lakehouse instance by IP allowlist and blocklist. Requires instance administrator (`instance_admin`) privileges.

## Syntax

```Plain
CREATE [ OR REPLACE ] NETWORK POLICY <name>
  ALLOWED_IP_LIST = ( [ '<ip_address>' [ , '<ip_address>' , ... ] ] )
  [ BLOCKED_IP_LIST = ( [ '<ip_address>' [ , '<ip_address>' , ... ] ] ) ]
```

## Parameters

- `<name>`: The network policy name. Must be unique within the instance.
- `ALLOWED_IP_LIST`: IP allowlist. Supports IPv4 addresses or CIDR notation (e.g. `192.168.1.0/24`). An empty list means all IPs are allowed. `0.0.0.0/0` is not supported.
- `BLOCKED_IP_LIST`: IP blocklist. Optional. The blocklist takes priority over the allowlist; IPs matching the blocklist are always denied.

> ⚠️ **Note**: `0.0.0.0/0` is not supported. Duplicate IPs or CIDRs within the same allowlist or blocklist are not allowed, but overlapping ranges between the two lists are permitted.

A newly created policy is active by default.

## Examples

```sql
-- Allow access only from a specific IP range
CREATE NETWORK POLICY office_policy
  ALLOWED_IP_LIST = ('192.168.1.0/24', '10.0.0.1');

-- Allow a range while blocking a specific IP within it
CREATE NETWORK POLICY corp_policy
  ALLOWED_IP_LIST = ('192.168.11.1', '192.168.11.2', '10.0.0.1/24')
  BLOCKED_IP_LIST = ('192.168.11.99');

-- Replace an existing policy
CREATE OR REPLACE NETWORK POLICY office_policy
  ALLOWED_IP_LIST = ('10.0.0.0/8');
```

## Notes

- All NETWORK POLICY operations require instance administrator (`instance_admin`) privileges.
- If you add your current access IP to the blocklist, your connection will be immediately dropped once the policy takes effect. Proceed with caution.
- When multiple policies are active simultaneously, the system takes the union of all active allowlists and the union of all active blocklists before applying them.

## Related Documentation

- [ALTER NETWORK POLICY](alter-network-policy.md) — modify policy content or activate/deactivate
- [DROP NETWORK POLICY](drop-network-policy.md) — delete a policy
- [SHOW NETWORK POLICY](show-network-policy.md) — list all policies
- [DESC NETWORK POLICY](desc-network-policy.md) — view policy details
- [Network Policy](network_policy.md) — how it works and usage guide
