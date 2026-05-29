# Security Policies

Security policies form Lakehouse's **multi-layered data access control system** — from the network layer (who can connect), to the identity layer (who can log in), to the permission layer (what operations are allowed), to the data layer (which column values are visible). Together they create a defense-in-depth posture.

## Security Policy Framework

Lakehouse's security controls are organized into four layers, tightening from the outside in:

| Layer | Policy type | Control dimension | Typical use |
|-------|-------------|-------------------|-------------|
| **Network** | Network Policy | Source IP | Allow only the corporate intranet or specific IP ranges |
| **Identity** | User management | Login identity | Create users, set passwords, bind roles |
| **Permission** | Role (RBAC) | Operation permissions | Control which operations users can perform on which objects |
| **Data** | Dynamic masking | Column values | Mask sensitive columns based on role |

**How the four layers relate**: The network policy is the first gate (connections from IPs not on the allowlist are rejected outright); user identity is the second gate (account and password verification); role permissions control what actions are allowed; dynamic masking controls what sensitive column values are visible.

## Policy Details

### Network Policy

Restricts access by IP allowlist. Different policies can be applied to the entire instance or to specific users.

```sql
-- Create a network policy: allow only the corporate intranet
CREATE NETWORK POLICY corp_policy
    ALLOWED_IP_LIST = ('192.168.0.0/16', '10.0.0.0/8');

-- Apply to a specific user (overrides the instance-level policy)
ALTER USER analyst SET NETWORK_POLICY = corp_policy;
```

### Roles (RBAC)

Bundle permissions into roles, then grant roles to users. Four system-defined roles are provided:

| Role | Scope | Permissions |
|------|-------|-------------|
| `account_admin` | Account level | Manage all resources under the account |
| `workspace_admin` | Workspace level | Manage all resources within the Workspace |
| `workspace_dev` | Workspace level | Development tasks, use data and compute clusters |
| `workspace_user` | Workspace level | Read-only view of jobs and instances |

```sql
-- Create a custom role and grant permissions
CREATE ROLE analyst;
GRANT SELECT ON TABLE orders TO ROLE analyst;
GRANT ROLE analyst TO USER alice;
```

### Dynamic Data Masking

Automatically masks sensitive columns (phone numbers, ID numbers, etc.) based on the user's role when query results are returned. **The data at the storage layer is unchanged** — masking only happens at result delivery time.

```sql
-- Create a masking function: admins see full data, other roles see masked data
CREATE FUNCTION phone_mask(val STRING)
RETURNS STRING ->
CASE
    WHEN array_contains(current_roles(), 'workspace_admin') THEN val
    ELSE REGEXP_REPLACE(val, '(\\d{3})\\d{4}(\\d{4})', '$1****$2')
END;

-- Bind to a column at table creation time
CREATE TABLE users (
    id INT,
    phone STRING MASK phone_mask
);

-- Bind to a column on an existing table
ALTER TABLE users CHANGE COLUMN phone SET MASK phone_mask;
```

## Common Issues

### Issue 1: Forgetting to verify masking after binding a policy

**Problem**: After creating a masking policy and binding it to a column, you query with the creator's account and find the data is not masked.

**Cause**: The creator typically holds the `account_admin` or `workspace_admin` role, and the policy is configured to show full data to admin roles.

**Solution**: Verify the masking effect using a regular user account, not an admin account.

### Issue 2: Misconfigured network policy locks you out

**Problem**: You apply a network policy to your own account, but the IP configuration is wrong, making it impossible to log in.

**Solution**: Log in with another admin account and run `ALTER USER ... UNSET NETWORK_POLICY` to remove the policy. Before applying a network policy, always confirm that your current IP is on the allowlist.

## Cost Impact

Security policies themselves incur no additional storage or compute costs:
- Network policies, roles, and users: only metadata is stored, at near-zero cost.
- Dynamic masking: performs string replacement when query results are returned; the impact on query performance is negligible.

## In This Section

| Page | Description |
|------|-------------|
| [Network Policy](om-network-policy.md) | IP allowlist configuration, instance-level and user-level policies |
| [Dynamic Data Masking](om-dynamic-mask.md) | Role-based masking of sensitive columns, creating and binding masking policies |
| [User Management](om-user-management.md) | User creation, password management, role binding |
| [Roles](om-roles.md) | RBAC role system, system-defined roles, custom roles |

## Related Documentation

| Document | Description |
|----------|-------------|
| [User and Permission Management](authority-management.md) | User hierarchy, lifecycle management, permission best practices |
| [Network Policy SQL Reference](network_policy.md) | Complete syntax for CREATE/ALTER/DROP NETWORK POLICY |
| [Dynamic Masking SQL Reference](dynamic-mask.md) | Complete masking policy syntax |
| [Role Management SQL Reference](roles.md) | Complete syntax for GRANT/REVOKE/CREATE ROLE |
