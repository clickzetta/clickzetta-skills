# GRANT TO USER

## Description

Grant specified permissions to a user or role to achieve fine-grained access control over workspace resources.

## Syntax

### Grant Object Permissions to a User

```Plain
GRANT
    workspacePrivileges ON WORKSPACE workspace_name
    | workspaceObjectPrivileges ON { ROLE | SCHEMA | VCLUSTER | FUNCTION } workspace_object_name
    | schemaPrivileges ON SCHEMA schema_name
    | schemaObjectPrivileges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
TO USER user_name [WITH GRANT OPTION];
```

### Grant a Role to a User

```Plain
GRANT ROLE role_name TO USER user_name;
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
| `workspace_name` | Yes (when granting workspace privileges) | Workspace name |
| `workspace_object_name` | Yes (when granting workspace object privileges) | Name of the object under the workspace (Schema, VCluster, Function, etc.) |
| `schema_name` | Yes (when granting schema privileges) | Schema name |
| `schema_object_name` | Yes (when granting schema object privileges) | Full object name in the format `schema_name.object_name` |
| `user_name` | Yes | The name of the user being granted permissions |
| `role_name` | Yes (when granting a role) | Role name; supports custom roles and system preset roles |
| `WITH GRANT OPTION` | No | Allows the grantee to re-grant these permissions to other users |

## Usage Examples

1. Grant the role `test_readonly_role` to user `tester`:

   ```SQL
   GRANT ROLE test_readonly_role TO USER tester;
   ```

2. Grant user `tester` the permission to query table `semantic_model_test.dim_customer`:

   ```SQL
   GRANT SELECT ON TABLE semantic_model_test.dim_customer TO USER tester;
   ```

3. Grant user `tester` the permission to create tables under schema `semantic_model_test`:

   ```SQL
   GRANT CREATE TABLE ON SCHEMA semantic_model_test TO USER tester;
   ```

4. Grant user `tester` the permission to create a VCluster in the workspace:

   ```SQL
   GRANT CREATE VCLUSTER ON WORKSPACE quick_start TO USER tester;
   ```

5. Grant role `test_developer_role` the permission to create views under schema `semantic_model_test`:

   ```SQL
   GRANT CREATE VIEW ON SCHEMA semantic_model_test TO ROLE test_developer_role;
   ```

6. Grant user `tester` the permission to modify VCluster `default`, with the ability to re-grant:

   ```SQL
   GRANT ALTER VCLUSTER ON VCLUSTER default TO USER tester WITH GRANT OPTION;
   ```

A successful command returns an empty result set. No error message means the grant succeeded.

## Notes

- Executing this command requires the `workspace_admin` or `security_admin` role, or `WITH GRANT OPTION` on the target object.
- Follow the principle of least privilege: grant only the minimum permissions a user needs to complete their work.
- Granting roles (`GRANT ROLE`) is the recommended permission management approach, as it simplifies bulk management and permission revocation.
- Use `WITH GRANT OPTION` with caution, as the grantee may propagate the permission to other users.
- Use `SHOW GRANTS TO USER user_name` to verify the grant result.
