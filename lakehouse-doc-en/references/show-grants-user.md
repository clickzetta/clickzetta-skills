# SHOW GRANTS TO USER

## Description

Queries all permissions granted to a specified user in the current workspace, including directly granted object privileges and permissions inherited through roles.

## Syntax

```Plain
SHOW GRANTS TO USER user_name;
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `user_name` | Yes | The name of the user to query permissions for; the user must already exist in the current workspace |

## Return Column Description

| Column Name | Description |
|-------------|-------------|
| `granted_type` | Grant type: `ROLE` (role grant) or `PRIVILEGE` (object privilege grant) |
| `privilege` | Permission name, such as `SELECT TABLE`, `workspace_dev`, etc. |
| `conditions` | Additional conditions (usually empty) |
| `granted_on` | Type of object the permission is granted on, such as `ROLE`, `TABLE`, `SCHEMA`, etc. |
| `object_name` | Full name of the granted object (including workspace prefix) |
| `granted_to` | Type of the grantee; always `USER` |
| `grantee_name` | Full name of the granted user (including workspace prefix) |
| `grantor_name` | Name of the user who performed the grant operation |
| `grant_option` | Whether the permission can be re-granted: `true` means the permission can be granted to other users |
| `granted_time` | Time when the permission was granted |

## Usage Examples

1. Query all permissions held by user `tester`:

   ```SQL
   SHOW GRANTS TO USER tester;
   ```

   Example output:

   | granted_type | privilege | granted_on | object_name | grantee_name | grantor_name | grant_option | granted_time |
   |---|---|---|---|---|---|---|---|
   | ROLE | workspace_dev | ROLE | quick_start.workspace_dev | quick_start.tester | quick_start.qiliang | false | 2025-03-27 20:43:39.419 |

2. Query the permissions of the currently logged-in user:

   ```SQL
   SHOW GRANTS TO USER CURRENT_USER();
   ```

   > `CURRENT_USER()` returns the login username of the current session and can be used directly here.

## Notes

- Executing this command requires the `workspace_admin` or `security_admin` role, or the query must be for the currently logged-in user's own permissions.
- Results include both directly granted permissions and permissions obtained indirectly through roles (rows where `granted_type` is `ROLE` indicate permissions obtained through a role).
- To view the specific permissions contained in a role, use `SHOW GRANTS TO ROLE role_name`.
- Usernames are case-sensitive. Ensure correct input.
- If the user does not exist, the command raises an error rather than returning an empty result set.
