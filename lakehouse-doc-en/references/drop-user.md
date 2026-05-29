# Remove a User from the Current Workspace

## Function

Removes the specified user from the current workspace. After removal, the user can no longer access any resources within the workspace.

## Syntax

```Plain
DROP USER [IF EXISTS] user_name;
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `IF EXISTS` | No | If the user does not exist in the current workspace, skip the operation without error |
| `user_name` | Yes | The name of the user to remove from the workspace |

## Usage Examples

1. Remove user `uat_test`:

   ```SQL
   DROP USER uat_test;
   ```

2. Use `IF EXISTS` to safely remove a user (no error if the user does not exist):

   ```SQL
   DROP USER IF EXISTS uat_test;
   ```

   Successful execution returns an empty result set; no error message means the operation succeeded.

## Notes

- Executing this command requires the `workspace_admin` or `user_admin` role.
- `DROP USER` only removes the user from the current workspace. It does not delete the user's account in the instance user management system, nor does it affect the user's permissions in other workspaces.
- After a user is removed, all permissions granted to that user in this workspace (including directly granted object permissions and roles) will be cleared together.
- Removing a user does **not** delete the data objects (tables, views, Schemas, etc.) created by that user; these objects still exist in the workspace.
- To remove multiple users, execute separate `DROP USER` commands for each.
- You cannot drop the currently logged-in user.
