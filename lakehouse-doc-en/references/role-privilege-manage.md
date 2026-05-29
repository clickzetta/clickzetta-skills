# Roles and Privileges

Role and privilege commands are used to create roles, grant permissions to users or roles, and view or revoke existing grants.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [CREATE ROLE](create-role.md) | Create a custom role for bulk permission management |
| [DROP ROLE](drop-role.md) | Drop a role (does not affect users who have been granted the role) |
| [GRANT (User Privileges)](grant-user-privileges.md) | Grant object privileges or roles directly to a user |
| [REVOKE (User Privileges)](revoke-user-privileges.md) | Revoke object privileges or roles from a user |
| [SHOW GRANTS (User)](show-grants-user.md) | View all privileges held by a specific user |
| [GRANT (Role Privileges)](grant-privileges.md) | Grant object privileges to a role |
| [REVOKE (Role Privileges)](revoke-privileges.md) | Revoke object privileges from a role |
| [SHOW ROLES](show-roles.md) | List all roles in the current workspace |
| [SHOW GRANTS (Role)](show-grants.md) | View all privileges held by a specific role |

---

## Common Operations

### Create a Role and Grant Privileges

```SQL
-- Create a role
CREATE ROLE IF NOT EXISTS data_analyst;

-- Grant table privileges to the role
GRANT SELECT ON TABLE public.orders TO ROLE data_analyst;
GRANT SELECT ON TABLE public.customers TO ROLE data_analyst;

-- Grant privileges on all tables in a schema to the role
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ROLE data_analyst;
```

### Grant a Role to a User

```SQL
-- Assign a role to a user
GRANT ROLE data_analyst TO USER alice;

-- Grant privileges directly to a user (not recommended; prefer role-based management)
GRANT SELECT ON TABLE public.orders TO USER bob;
```

### View Privileges

```SQL
-- View privileges held by a user
SHOW GRANTS TO USER alice;

-- View privileges held by a role
SHOW GRANTS TO ROLE data_analyst;

-- List all roles
SHOW ROLES;
```

### Revoke Privileges

```SQL
-- Revoke a role from a user
REVOKE ROLE data_analyst FROM USER alice;

-- Revoke a table privilege from a role
REVOKE SELECT ON TABLE public.orders FROM ROLE data_analyst;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [User Management](authority-management.md) | Add users to a workspace |
| [Metadata Objects and Privilege Points](meta-objects-and-privileges.md) | All grantable object types and privilege point descriptions |
