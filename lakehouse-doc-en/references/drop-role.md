# DROP ROLE

Deletes a role from the current workspace.

## Workspace Role Management

### Syntax

```SQL
DROP ROLE [IF EXISTS] role_name;
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `IF EXISTS` | No | If the role does not exist, no error is thrown and the operation is skipped |
| `role_name` | Yes | The name of the role to drop |

## Usage Examples

1. Drop role `simple_role`:

   ```SQL
   DROP ROLE simple_role;
   ```

2. Use `IF EXISTS` to drop a role while avoiding errors when the role does not exist:

   ```SQL
   DROP ROLE IF EXISTS temporary_role;
   ```

3. Drop role `report_user`:

   ```SQL
   DROP ROLE report_user;
   ```

## Notes

- Executing this command requires the `workspace_admin` role.
- **Dropping a role automatically revokes the role from all users**. Users who had been assigned this role will immediately lose all permissions obtained through that role.
- Dropping a role also revokes all object permissions held by that role (permissions granted via `GRANT ... TO ROLE`).
- The drop operation is irreversible. Confirm that the role is no longer in use before dropping.
- Using the `IF EXISTS` option avoids error messages when the role does not exist.
- System preset roles (such as `workspace_admin`, `workspace_dev`, `workspace_analyst`, `workspace_sre`, `workspace_user`) cannot be dropped.
- Before dropping, it is recommended to first check the permissions held by the role using `SHOW GRANTS TO ROLE role_name`, and confirm which users hold the role using `SHOW GRANTS TO USER user_name`.

# Dropping an Instance Role

```SQL
DROP INSTANCE ROLE IF EXISTS <role_name>;
```

## Usage Notes

- Before executing the drop operation, ensure the role is no longer needed. Once dropped, the role cannot be recovered.
- Using the `IF EXISTS` option avoids error messages when the role does not exist.
- `INSTANCE_ADMIN` permission is required to perform this operation.
- Dropping an Instance Role automatically revokes the corresponding permissions from all users who had been granted that role.
