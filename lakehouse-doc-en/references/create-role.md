# CREATE ROLE

This document describes how to create custom roles.

## Workspace Role Management

### Syntax

```SQL
CREATE [OR REPLACE] ROLE [IF NOT EXISTS] role_name [COMMENT ''];
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `OR REPLACE` | No | If a role with the same name already exists, replace it. Cannot be used together with `IF NOT EXISTS` |
| `IF NOT EXISTS` | No | Creates the role if it does not exist; if it already exists, no error is thrown and no new role is created. Cannot be used together with `OR REPLACE` |
| `role_name` | Yes | The name of the new role. Must be unique within the workspace and cannot be the same as a system preset role name |
| `COMMENT` | No | Adds a comment or description for the role |

## Usage Examples

1. Create role `simple_role`:

   ```SQL
   CREATE ROLE simple_role;
   ```

2. Create a role with a comment:

   ```SQL
   CREATE ROLE admin_role COMMENT 'Role with elevated permissions';
   ```

3. Use `IF NOT EXISTS` to avoid errors when the role already exists:

   ```SQL
   CREATE ROLE IF NOT EXISTS test_temp_role;
   ```

4. Use `OR REPLACE` to replace an existing role with the same name:

   ```SQL
   CREATE OR REPLACE ROLE existing_role;
   ```

After creation, you can verify with `SHOW ROLES`:

```SQL
SHOW ROLES;
```

Example output (including the newly created role):

| name | comment |
|------|---------|
| test_developer_role | Test role |
| test_readonly_role | Read-only role for testing |
| test_temp_role | |
| workspace_admin | System preset role with management permissions for tasks, environments, and all data objects in the workspace, as well as permissions for managing members and roles in the workspace. |
| workspace_dev | System preset role with management permissions for task directories in the workspace, editing permissions for task scripts, and read and write permissions for all data objects in the workspace. |

## Notes

- Executing this command requires the `workspace_admin` role.
- After creation, the role has no permissions. Permissions must be granted to the role via the `GRANT` statement.
- Use `GRANT ROLE role_name TO USER user_name` to assign the role to a user.
- System preset roles (such as `workspace_admin`, `workspace_dev`, etc.) cannot be deleted or replaced via `OR REPLACE`.

# Instance Role Management

LakeHouse supports creating roles at the instance granularity (Instance-Level), enabling unified cross-workspace permission control for fine-grained access management in multi-team collaboration scenarios. Executing this operation requires `INSTANCE_ADMIN` permission.

## Syntax

```SQL
-- Create an Instance Role (if not exists)
CREATE INSTANCE ROLE IF NOT EXISTS <role_name>;
-- Drop an Instance Role (if exists)
DROP INSTANCE ROLE IF EXISTS <role_name>;
-- View all Instance Roles
SHOW INSTANCE ROLES;
```

## Examples

```SQL
DROP INSTANCE ROLE IF EXISTS inst_role;

CREATE INSTANCE ROLE IF NOT EXISTS inst_role;

SHOW INSTANCE ROLES;
```
