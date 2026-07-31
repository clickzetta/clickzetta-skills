# GRANT

## Function Description

Grants specified privileges to a role or user, enabling fine-grained access control for workspace resources.

## Workspace User and Role Permission Management Syntax

```Plain
GRANT workspacePrivileges ON WORKSPACE workspace_name
    | workspaceObjectPrivileges ON { ROLE | SCHEMA | VCLUSTER | DATALAKE | FUNCTION } workspace_object_name
    | schemaPrivileges ON SCHEMA schema_name
    | schemaObjectPrivileges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
    | dynamicTablePrivileges ON DYNAMIC TABLE schema_object_name
TO { ROLE role_name | USER user_name } [WITH GRANT OPTION];
```

> ⚠️ **Note**: Dynamic Tables require `ON DYNAMIC TABLE` in the `GRANT` statement — `ON TABLE` does not work. Using `ON TABLE` against a Dynamic Table returns `Invalid privilege 'SELECT TABLE' for object type 'TABLE'`. Regular managed tables still use `ON TABLE`; the two are not interchangeable.

### Privilege Type Description

```Plain
-- Workspace level: create objects
workspacePrivileges ::=
    CREATE { SCHEMA | VCLUSTER }

-- Workspace object privileges
workspaceObjectPrivileges ::=
    ALTER | DROP | READ METADATA | ALL [PRIVILEGES]

-- Schema level: create objects
schemaPrivileges ::=
    CREATE { TABLE | VIEW | MATERIALIZED VIEW | DYNAMIC TABLE } | ALL

-- Schema object privileges (regular tables, views, materialized views)
schemaObjectPrivileges ::=
    ALTER | DROP | SELECT | INSERT | READ METADATA | ALL

-- Dynamic Table privileges
dynamicTablePrivileges ::=
    SELECT | ALTER DYNAMIC TABLE | DROP DYNAMIC TABLE | RESTORE DYNAMIC TABLE | READ METADATA | ALL [PRIVILEGES]
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `workspacePrivileges` | Yes (when granting workspace privileges) | Workspace-level privileges, such as `CREATE SCHEMA`, `CREATE VCLUSTER` |
| `workspaceObjectPrivileges` | Yes (when granting workspace object privileges) | Privileges on workspace objects, such as `ALTER`, `DROP`, `READ METADATA`, `ALL [PRIVILEGES]` |
| `schemaPrivileges` | Yes (when granting Schema privileges) | Schema-level privileges, such as `CREATE TABLE`, `CREATE VIEW`, `CREATE MATERIALIZED VIEW`, `ALL` |
| `schemaObjectPrivileges` | Yes (when granting Schema object privileges) | Privileges on Schema objects, such as `ALTER`, `DROP`, `SELECT`, `INSERT`, `READ METADATA`, `ALL` |
| `workspace_name` | Yes (when granting workspace privileges) | Workspace name |
| `workspace_object_name` | Yes (when granting workspace object privileges) | Name of the workspace object (Schema, VCluster, Function, etc.) |
| `schema_name` | Yes (when granting Schema privileges) | Schema name |
| `schema_object_name` | Yes (when granting Schema object privileges) | Full object name in the format `schema_name.object_name` |
| `role_name` | Yes (when granting to a role) | Name of the role being granted privileges |
| `user_name` | Yes (when granting to a user) | Name of the user being granted privileges |
| `WITH GRANT OPTION` | No | Allows the grantee to re-grant this privilege to other users |

## Usage Examples

1. Grant role `simple_role` the privilege to create VCLUSTERs in the workspace:

   ```SQL
   GRANT CREATE VCLUSTER ON WORKSPACE lakehouse_public TO ROLE simple_role;
   ```

2. Grant role `simple_role` the privilege to alter the VCLUSTER named `default`:

   ```SQL
   GRANT ALTER VCLUSTER ON VCLUSTER default TO ROLE simple_role;
   ```

3. Grant role `simple_role` the privilege to create tables and views in the `public` Schema:

   ```SQL
   GRANT CREATE VIEW, CREATE TABLE ON SCHEMA public TO ROLE simple_role;
   ```

4. Grant role `my_role` query and modification privileges on a specified table:

   ```SQL
   GRANT SELECT, ALTER ON TABLE public.my_table TO ROLE my_role;
   ```

5. Grant role `my_role` query privilege on a specified view:

   ```SQL
   GRANT SELECT ON VIEW public.my_view TO ROLE my_role;
   ```

6. Grant role `my_role` query privilege on a specified materialized view:

   ```sql
   GRANT SELECT ON MATERIALIZED VIEW public.my_materialized_view TO ROLE my_role;
   ```

7. Grant role `my_role` query privilege on a specified dynamic table:

   ```sql
   GRANT SELECT ON DYNAMIC TABLE public.my_dynamic_table TO ROLE my_role;
   ```

   Grant role all privileges on a dynamic table:

   ```sql
   GRANT ALL PRIVILEGES ON DYNAMIC TABLE public.my_dynamic_table TO ROLE my_role;
   ```

8. Grant user `tester` the role `test_readonly_role`:

   ```sql
   GRANT ROLE test_readonly_role TO USER tester;
   ```

9. Grant user `tester` query privilege on a specified table, with the ability to re-grant:

   ```sql
   GRANT SELECT ON TABLE public.my_table TO USER tester WITH GRANT OPTION;
   ```

Successful execution returns an empty result set; no error message means the grant was successful. You can verify the grant result using `SHOW GRANTS TO ROLE role_name` or `SHOW GRANTS TO USER user_name`.

## Notes

- Executing this command requires the `workspace_admin` or `security_admin` role, or having `WITH GRANT OPTION` permission on the target object.
- It is recommended to manage permissions through roles (`GRANT ROLE`) for easier batch granting and unified revocation.
- Follow the principle of least privilege, granting only the minimum permissions required to complete the work.
- Use `WITH GRANT OPTION` with caution, as the grantee may propagate permissions to other users.

## Instance Role Granting

Instance Roles can be used to grant cross-workspace global permissions. Grant targets include users or other roles.

### Syntax

```SQL
-- Grant an Instance Role to a user
GRANT INSTANCE ROLE <role_name> TO USER <user_name>;
-- Grant workspace permissions to an Instance Role
GRANT <privilege> ON WORKSPACE <workspace_name> TO INSTANCE ROLE <role_name>;
-- Grant table-level permissions to an Instance Role
GRANT <privilege> ON TABLE <workspace>.<schema>.<table> TO INSTANCE ROLE <role_name>;
-- View Instance Role permissions
SHOW GRANTS TO INSTANCE ROLE <role_name>;
```

### Examples

```SQL
-- Grant an Instance Role to a user
GRANT INSTANCE ROLE inst_role TO USER lh_engine_test_01;
-- Grant all permissions on a workspace
GRANT ALL ON WORKSPACE ws1 TO INSTANCE ROLE inst_role;
-- Grant all permissions on a single table
GRANT ALL ON TABLE ws1.schema.table TO INSTANCE ROLE inst_role;
-- View permissions (expected to include cross-workspace grant records)
SHOW GRANTS TO INSTANCE ROLE inst_role;
-- Revoke all permissions on a workspace
REVOKE ALL ON WORKSPACE ws1 FROM INSTANCE ROLE inst_role;
```
