# REVOKE FROM USER

## Description

Revoke permissions that have been granted to a specified user or role. Supports revoking both object privileges and role grants.

## Syntax

### Revoke Object Permissions from a User

```Plain
REVOKE [GRANT OPTION FOR]
    workspacePrivileges ON WORKSPACE workspace_name
    | workspaceObjectPrivileges ON { ROLE | SCHEMA | VCLUSTER | FUNCTION } workspace_object_name
    | schemaPrivileges ON SCHEMA schema_name
    | schemaObjectPrivileges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
FROM USER user_name;
```

### Revoke a Role from a User

```Plain
REVOKE ROLE role_name FROM USER user_name;
```

### Privilege Type Definitions

```Plain
-- Workspace level: create objects
workspacePrivileges ::=
    CREATE { SCHEMA | VCLUSTER }

-- Workspace object privileges
workspaceObjectPrivileges ::=
    -- SCHEMA, FUNCTION
    ALTER | DROP | READ METADATA | ALL [PRIVILEGES]
    -- VCLUSTER
    ALTER | DROP | USE | READ METADATA | ALL [PRIVILEGES]
    -- JOB
    ALTER | CANCEL | READ METADATA | ALL [PRIVILEGES]

-- Schema level: create objects
schemaPrivileges ::=
    CREATE { TABLE | VIEW | MATERIALIZED VIEW } | ALL

-- Schema object privileges
schemaObjectPrivileges ::=
    -- TABLE
    ALTER | DROP | SELECT | INSERT | READ METADATA | ALL
    -- VIEW / MATERIALIZED VIEW
    ALTER | DROP | SELECT | ALL
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `GRANT OPTION FOR` | No | Revokes only the re-grant ability (`WITH GRANT OPTION`) while preserving the underlying permission itself |
| `workspace_name` | Yes (when revoking workspace privileges) | Workspace name |
| `workspace_object_name` | Yes (when revoking workspace object privileges) | Name of the object under the workspace |
| `schema_name` | Yes (when revoking schema privileges) | Schema name |
| `schema_object_name` | Yes (when revoking schema object privileges) | Full object name in the format `schema_name.object_name` |
| `user_name` | Yes | The name of the user whose permissions are being revoked |
| `role_name` | Yes (when revoking a role) | The name of the role to revoke |

## Usage Examples

1. Revoke the role `test_readonly_role` from user `tester`:

   ```SQL
   REVOKE ROLE test_readonly_role FROM USER tester;
   ```

2. Revoke user `tester`'s permission to query table `semantic_model_test.dim_customer`:

   ```SQL
   REVOKE SELECT ON TABLE semantic_model_test.dim_customer FROM USER tester;
   ```

3. Revoke user `tester`'s permission to create tables under schema `semantic_model_test`:

   ```SQL
   REVOKE CREATE TABLE ON SCHEMA semantic_model_test FROM USER tester;
   ```

4. Revoke user `tester`'s permission to create a VCluster in the workspace:

   ```SQL
   REVOKE CREATE VCLUSTER ON WORKSPACE quick_start FROM USER tester;
   ```

5. Revoke role `test_developer_role`'s permission to create views under schema `semantic_model_test`:

   ```SQL
   REVOKE CREATE VIEW ON SCHEMA semantic_model_test FROM ROLE test_developer_role;
   ```

A successful command returns an empty result set. No error message means the revocation succeeded.

## Notes

- Executing this command requires the `workspace_admin` or `security_admin` role.
- Revoking a permission that the user does not hold will **not raise an error**; the command silently succeeds and returns an empty result set.
- Revoking a role (`REVOKE ROLE`) only removes the association between the user and that role; it does not affect the role itself or other users who hold the role.
- Using `GRANT OPTION FOR` revokes only the user's ability to re-grant the permission, without affecting their own access to the resource.
- Permissions obtained indirectly through a role cannot be revoked directly with `REVOKE`; you must first revoke the role (`REVOKE ROLE`).
- Use `SHOW GRANTS TO USER user_name` to verify the revocation result.
