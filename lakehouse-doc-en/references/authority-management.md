# User Management

Users are the identity principals that perform operations in Singdata Lakehouse. Lakehouse uses a two-tier user model: instance-level user management and workspace-level user management.

## User Tiers

### Instance-Level Users

Instance-level users are created in the global account and represent independent identities in the system. Creating, deleting, enabling, and disabling instance-level users is done in the **Account Console → User Management** page.

- Multiple users can be created under one account; usernames must be unique.
- Instance-level users are granted the `instance_user` role by default and have no data or feature permissions.
- A user must be added to a workspace before they can be granted roles and permissions within that workspace.

### Workspace-Level Users

A workspace-level user is an instance-level user that has been added to a specific workspace. Only users who have been added to a workspace can be granted roles and permissions within it.

- Use `CREATE USER` to add an instance user to a workspace.
- Use `DROP USER` to remove a user from a workspace.
- A user can be a member of multiple workspaces simultaneously.

## User Types

| Type | Description | Login Method |
|------|-------------|-------------|
| Regular User | Actual personnel within the organization; performs daily data queries, analysis, and management | Web console login, JDBC connection |
| Service User | A special user for automated processes or system-level calls | JDBC connection only; cannot log in via the web console |

Service users include **system service users** (created by default when Lakehouse is initialized) and **custom service users** (created by users themselves).

---

## In This Chapter

| Page | Description |
|------|-------------|
| [CREATE USER](create-user.md) | Add an instance user to the current workspace; set default cluster and schema |
| [ALTER USER](alter-user.md) | Modify a user's default cluster, default schema, and other properties |
| [DROP USER](drop-user.md) | Remove a user from the current workspace (does not delete the instance user account) |
| [SHOW USERS](show-users.md) | List all users in the current workspace |

---

## User Lifecycle Management

### 1. Create an Instance User

Create a new user in the "User Management" page of the account console, setting the username, password, phone number, email, and other information.

### 2. Add the User to a Workspace

```SQL
CREATE USER user_name [DEFAULT_VCLUSTER = vc_name] [DEFAULT_SCHEMA = schema_name] [COMMENT = 'comment_text'];
```

### 3. Grant the User a Role or Permissions

```SQL
GRANT ROLE workspace_dev TO USER user_name;
GRANT SELECT ON TABLE public.my_table TO USER user_name;
```

### 4. Modify User Properties

```SQL
ALTER USER user_name SET DEFAULT_VCLUSTER = new_vc DEFAULT_SCHEMA = new_schema COMMENT = 'updated comment';
```

### 5. View User List and Permissions

```SQL
SHOW USERS;
SHOW GRANTS TO USER user_name;
```

### 6. Remove a User from the Workspace

```SQL
DROP USER [IF EXISTS] user_name;
```

> ⚠️ **Note**: `DROP USER` only removes the user from the current workspace. It does not delete the user's account and password from the instance user management system.

---

## Common Operations

### Add a User to a Workspace

```SQL
-- Add an instance user to the current workspace
CREATE USER alice;

-- Add with a default cluster and schema
CREATE USER bob
  DEFAULT_VCLUSTER = analytics_cluster
  DEFAULT_SCHEMA = public;
```

### Modify User Configuration

```SQL
-- Change the default cluster
ALTER USER bob SET DEFAULT_VCLUSTER = etl_cluster;

-- Change the default schema
ALTER USER bob SET DEFAULT_SCHEMA = dwd;
```

### View Users

```SQL
-- List all users
SHOW USERS;
```

### Remove a User from the Workspace

```SQL
-- Remove a user (instance account is preserved)
DROP USER IF EXISTS alice;
```

---

## Access Management Best Practices

1. **Use RBAC**: Manage permissions through roles rather than granting them directly to users.
2. **Follow the principle of least privilege**: Grant users only the minimum permissions needed to do their work.
3. **Review permissions regularly**: Use `SHOW GRANTS TO USER` to periodically audit user permissions.
4. **Use WITH GRANT OPTION with caution**: A user granted this option can re-grant the permission to others.

---

## Notes

- `CREATE USER` does not create a new account — it only adds an existing instance user to the workspace. Instance users are created in the console.
- `DROP USER` only removes workspace access; it does not delete the instance user's account and password.
- Before removing a user, run `SHOW GRANTS TO USER user_name` to confirm their permissions have been handled.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [Roles and Privileges](role-privilege-manage.md) | Grant roles and permissions to users |
| [CREATE USER](create-user.md) | Full syntax for adding an instance user to a workspace |
| [ALTER USER](alter-user.md) | Full syntax for modifying user properties |
| [DROP USER](drop-user.md) | Full syntax for removing a user from a workspace |
| [SHOW USERS](show-users.md) | View the workspace user list |
| [GRANT](grant-privileges.md) | Grant permissions to users or roles |
| [REVOKE](revoke-privileges.md) | Revoke permissions from users or roles |
| [SHOW GRANTS](show-grants.md) | View the permission list for a user or role |
| [Roles](roles.md) | Create and manage roles |
