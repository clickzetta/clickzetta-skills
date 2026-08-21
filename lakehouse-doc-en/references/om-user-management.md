# User Management

A user is the **identity principal for login and operations** in the Lakehouse. Multiple users can be created under an account, each with an independent username, password, and permission configuration.

## Relationship Between Users and Accounts

```
Account                    ← External-facing organizational unit with a unique account name
└── Users (× N)            ← Identities that actually log in and perform operations
    └── Workspace Roles    ← Control permissions within a workspace
```

Users under the same account share the same set of data and compute resources, isolated from each other through roles and permissions.

## User Types

| Type | Description |
|------|------|
| Account Admin (account_admin) | Can manage all users, roles, and instance configurations under the account |
| Regular User | Obtains corresponding permissions through workspace roles |

## Create an Account and Add It to a Workspace

An account administrator must create login accounts and set their usernames and passwords in **Admin Center > Account Management > User Management**. For step-by-step instructions, see [How to Add and Manage Users](quick_start_user_management.md).

`CREATE USER` does not create a login account and does not accept a password. After the account has been created in the Admin Center and synchronized as an instance user, use this command to add it to the current workspace, then grant the required roles or privileges:

```sql
-- Add an existing instance user to the current workspace
CREATE USER alice;

-- Grant a workspace role
GRANT ROLE workspace_dev TO USER alice;

-- View users in the current workspace
SHOW USERS;
```

Maintain passwords and other login information in the Admin Center, not through Lakehouse SQL.

## Related Documentation

- [User Management Details](authority-management.md)
- [How to Add and Manage Users](quick_start_user_management.md)
- [CREATE USER](create-user.md)
- [Role Management](om-roles.md)
- [Workspace Roles](om-workspace.md)
