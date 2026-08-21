# Roles

Roles are the **fundamental unit of permission management** in the Lakehouse, packaging a set of privileges under a name and granting them to users. Role-Based Access Control (RBAC) enables centralized permission management and batch authorization.

## RBAC Model

```
Privilege
  └── Role           ← Privileges packaged as roles
        └── User      ← Roles granted to users
```

A user can have multiple roles, and the effective permissions are the union of all assigned role permissions.

## System Preset Roles

| Role | Scope | Permission Description |
|------|------|---------|
| `account_admin` | Account-level | Manage all resources under the account |
| `workspace_admin` | Workspace-level | Manage all resources within the workspace |
| `workspace_analyst` | Workspace-level | Use development features and compute clusters; read metadata of data objects by default |
| `workspace_dev` | Workspace-level | Develop tasks, use data and compute clusters |
| `workspace_sre` | Workspace-level | Manage all tasks and jobs within the workspace |

## Custom Roles

```sql
-- Create a custom role
CREATE ROLE analyst;

-- Grant privileges
GRANT SELECT ON TABLE orders TO ROLE analyst;
GRANT USAGE ON SCHEMA ods TO ROLE analyst;

-- Grant a role to a user
GRANT ROLE analyst TO USER alice;

-- View role privileges
SHOW GRANTS TO ROLE analyst;
```

## Related Documentation

- [Role Management Details](roles.md)
- [User Management](om-user-management.md)
- [Dynamic Masking](om-dynamic-mask.md) — Role-based masking control
- [Row-Level Permission](row-filter.md) — Role-based row-level access control
