## Function

Adds a user to the current workspace, allowing them to access and operate on resources within the workspace.

> **Note**: `CREATE USER` adds a user who already exists in the instance user management system into the current workspace, rather than creating a brand-new account. If the user does not exist in the instance, the command will report an error.

## Syntax

```Plain
CREATE USER [IF NOT EXISTS] user_name
    [ DEFAULT_VCLUSTER = vc_name ]
    [ DEFAULT_SCHEMA = schema_name ]
    [ COMMENT = 'comment_text' ];
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `IF NOT EXISTS` | No | If the user already exists in the workspace, skip the operation without error |
| `user_name` | Yes | User identifier; must be a username already created in the instance user management system |
| `DEFAULT_VCLUSTER` | No | Specifies a default compute cluster for the user. When not specified, the workspace's global default cluster is used |
| `DEFAULT_SCHEMA` | No | Specifies a default Schema for the user. Once set, the user automatically uses this Schema upon login; the `USE` command can switch to a different Schema during the session. Priority: `USE` command > default Schema |
| `COMMENT` | No | Adds a note or description for the user |

## Usage Examples

1. Add user `uat_test` to the workspace, using the global default compute cluster and Schema:

   ```SQL
   CREATE USER uat_test;
   ```

2. Add a user while specifying both a default compute cluster and a default Schema:

   ```SQL
   CREATE USER uat_test DEFAULT_VCLUSTER=vcluster1 DEFAULT_SCHEMA=schema1;
   ```

3. Use `IF NOT EXISTS` to avoid errors when the user already exists:

   ```SQL
   CREATE USER IF NOT EXISTS uat_test;
   ```

4. Add a user with a comment:

   ```SQL
   CREATE USER uat_test COMMENT='UAT environment test account';
   ```

Successful execution returns an empty result set; no error message means the operation succeeded.

## Notes

- Executing this command requires the `workspace_admin` or `user_admin` role.
- `user_name` must be an account that already exists in the instance user management system (not at the workspace level); otherwise, an error `NotFound: user does not exist` is thrown.
- After a user is added to a workspace, they have no data permissions by default. Permissions must be granted via the `GRANT` command or by assigning roles.
- When using `IF NOT EXISTS`, if the user already exists, the command silently succeeds without modifying any existing configuration.
