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

## Common Operations

```sql
-- Create a user
CREATE USER alice PASSWORD = 'SecurePass123!';

-- Grant a workspace role
GRANT ROLE workspace_dev TO USER alice;

-- Change a user's password
ALTER USER alice SET PASSWORD = 'NewPass456!';

-- View all users
SHOW USERS;
```

## Related Documentation

- [User Management Details](authority-management.md)
- [Role Management](om-roles.md)
- [Workspace Roles](om-workspace.md)
