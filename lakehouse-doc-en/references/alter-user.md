## Description

Modifies the attributes of an existing user in the current workspace, including the default compute cluster, default Schema, and comment.

## Syntax

```Plain
ALTER USER user_name SET
    [ DEFAULT_VCLUSTER = vc_name ]
    [ DEFAULT_SCHEMA = schema_name ]
    [ COMMENT = 'comment_text' ];
```

## Parameters

| Parameter | Required | Description |
|------|------|------|
| `user_name` | Yes | The name of the user to modify. The user must already exist in the current workspace |
| `DEFAULT_VCLUSTER` | No | Specifies the default compute cluster for the user. If not specified, the workspace's global default cluster is used |
| `DEFAULT_SCHEMA` | No | Specifies the default Schema for the user. Once set, the user automatically uses this Schema upon login. Can be switched during a session using the `USE` command. Priority: `USE` command > default Schema |
| `COMMENT` | No | Adds or updates a comment for the user |

- After `SET`, at least one attribute must be specified. Multiple attributes are separated by spaces, without commas.
- Each `ALTER USER` only updates the specified attributes; unspecified attributes remain unchanged.

## Examples

1. Set the default compute cluster and default Schema for user `tester`:

   ```SQL
   ALTER USER tester SET DEFAULT_VCLUSTER=default_ap DEFAULT_SCHEMA=public;
   ```

2. Modify only the default compute cluster for user `tester`:

   ```SQL
   ALTER USER tester SET DEFAULT_VCLUSTER=default_ap;
   ```

3. Modify only the default Schema for user `tester`:

   ```SQL
   ALTER USER tester SET DEFAULT_SCHEMA=public;
   ```

All of the above commands return an empty result set upon success. No error message indicates the change has taken effect.

## Notes

- Executing this command requires the `workspace_admin` or `user_admin` role.
- When modifying `DEFAULT_VCLUSTER`, the specified compute cluster must exist; when modifying `DEFAULT_SCHEMA`, the specified Schema must exist.
- The current version does not support modifying user passwords via `ALTER USER`; password management is handled in the instance-level user management system.
- `ALTER USER` does not support renaming users (the `user_name` cannot be changed).
