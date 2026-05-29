# DROP NETWORK POLICY

## Overview

Deletes the specified network policy. The deletion is irreversible and the policy takes effect immediately upon deletion. Requires instance administrator (`instance_admin`) privileges.

## Syntax

```Plain
DROP NETWORK POLICY [ IF EXISTS ] <name>
```

## Parameters

- `<name>`: The name of the network policy to delete.
- `IF EXISTS`: Silently skips the operation if the policy does not exist, without returning an error. If omitted and the policy does not exist, an error is returned.

## Examples

```sql
DROP NETWORK POLICY corp_policy;

-- No error if the policy does not exist
DROP NETWORK POLICY IF EXISTS old_policy;
```

## Notes

- Deletion is irreversible and the policy stops taking effect immediately.
- Requires instance administrator (`instance_admin`) privileges.

## Related Documentation

- [CREATE NETWORK POLICY](create-network-policy.md) — create a policy
- [SHOW NETWORK POLICY](show-network-policy.md) — view the list of existing policies before deleting
- [Network Policy](network_policy.md) — how it works and usage guide
