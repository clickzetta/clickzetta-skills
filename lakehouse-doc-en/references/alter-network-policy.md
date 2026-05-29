# ALTER NETWORK POLICY

## Overview

Modifies the IP allowlist or blocklist of a network policy, or toggles the policy between active and inactive states. Requires instance administrator (`instance_admin`) privileges.

## Syntax

```Plain
-- Modify IP lists (overwrites existing values)
ALTER NETWORK POLICY [ IF EXISTS ] <name>
  SET ALLOWED_IP_LIST = ( [ '<ip_address>' [ , '<ip_address>' , ... ] ] )
      [ BLOCKED_IP_LIST = ( [ '<ip_address>' [ , '<ip_address>' , ... ] ] ) ]

-- Activate a policy
ALTER NETWORK POLICY <name> ACTIVATE

-- Deactivate a policy
ALTER NETWORK POLICY <name> INACTIVATE
```

## Parameters

- `<name>`: The name of the network policy to modify.
- `IF EXISTS`: Silently skips the operation if the policy does not exist, without returning an error.
- `SET ALLOWED_IP_LIST`: Overwrites the allowlist with new values. An empty list means all IPs are allowed.
- `BLOCKED_IP_LIST`: Overwrites the blocklist with new values. Optional. If omitted, the blocklist is cleared.
- `ACTIVATE`: Sets the policy status to active; the policy takes effect immediately.
- `INACTIVATE`: Sets the policy status to inactive; the policy no longer takes effect.

> ⚠️ **Note**: The `SET` operation **overwrites** — it does not append. After execution, the policy's IP lists are completely replaced with the new values, and all previous IPs are discarded. To retain existing IPs, you must include them again in the new statement.

## Examples

```sql
-- Update the allowlist (the blocklist is also set; omitting BLOCKED_IP_LIST would clear it)
ALTER NETWORK POLICY corp_policy
  SET ALLOWED_IP_LIST = ('192.168.11.1')
      BLOCKED_IP_LIST = ('192.168.11.99');

-- Deactivate a policy
ALTER NETWORK POLICY corp_policy INACTIVATE;

-- Reactivate a policy
ALTER NETWORK POLICY corp_policy ACTIVATE;

-- Silently skip if the policy does not exist
ALTER NETWORK POLICY IF EXISTS old_policy INACTIVATE;
```

## Notes

- All NETWORK POLICY operations require instance administrator (`instance_admin`) privileges.
- The policy name cannot be changed via ALTER.
- Deactivating a policy does not delete it; it can be reactivated at any time.

## Related Documentation

- [CREATE NETWORK POLICY](create-network-policy.md) — create a policy
- [DROP NETWORK POLICY](drop-network-policy.md) — delete a policy
- [DESC NETWORK POLICY](desc-network-policy.md) — view the current IP lists of a policy
- [Network Policy](network_policy.md) — how it works and usage guide
