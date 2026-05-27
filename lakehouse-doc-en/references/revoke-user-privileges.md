##  Description

This command is used to revoke permissions from a specified user or role. You can revoke various types of permissions from users or roles as needed, including but not limited to permissions on workspaces, roles, schemas, and workspace objects.

## Syntax 
```SQL
REVOKE [GRANT OPTION FOR]

workspacePriveleges ON WORKSPACE workspace_name
| workspaceObjectPriveleges ON { ROLE | SCHEMA | VCLUSTER | FUNCTION } workspace_object_name
| schemaPrivileges ON SCHEMA schema_name
| schemaObjectPriveleges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
FROM USER user_name

-- Parameter Explanation
workspacePriveleges ::=
    CREATE { SCHEMA | VCLUSTER }

-- Authorization for objects under the workspace
workspaceObjectPriveleges ::=
    -- SCHEMA
    ALTER | DROP | READ METADATA | ALL [PRIVILEGES]
    -- VCLUSTER
    ALTER | DROP | USE | READ METADATA | ALL [PRIVILEGES]
    --job
    ALTER | CANCEL | READ METADATA | ALL [PRIVILEGES]

-- Authorization to create objects under schema
schemaPrivileges ::=
    CREATE { TABLE | VIEW | MATERIALIZED VIEW } | ALL

-- Authorization for objects under schema
schemaObjectPriveleges ::=
    -- table
    ALTER | DROP | SELECT | INSERT | READ METADATA | ALL
    -- view
    ALTER | DROP | SELECT | ALL
    -- MATERIALIZED VIEW
    ALTER | DROP | SELECT | ALL
```
## Parameter Description

1. `workspacePriveleges`: Permissions to create objects within the workspace, such as creating schemas and virtual clusters (VCLUSTER).

2. `workspaceObjectPriveleges`: Permissions to modify and view metadata of objects within the workspace.

3. `schemaPrivileges`: Permissions to create objects within a schema, such as creating tables, views, and materialized views.

4. `schemaObjectPriveleges`: Permissions to modify, delete, and query objects within a schema.

##  Example

1. Revoke the permission for user `uat_demo` to create virtual clusters in the `lakehouse_public` workspace:
   ```SQL
   REVOKE CREATE VCLUSTER ON WORKSPACE lakehouse_public FROM USER uat_demo;
   ```
```markdown
2. Revoke the permissions of user `uat_demo` to modify the virtual cluster named `default`:
```
   ```SQL
   REVOKE ALTER VCLUSTER ON VCLUSTER default FROM USER uat_demo;
   ```
3. Revoke the permissions for user `uat_demo` to create tables and views in `public` mode:
   ```SQL
   REVOKE CREATE VIEW, CREATE TABLE ON SCHEMA public FROM USER uat_demo;
   ```
4. Reclaim the permissions for the user `uat_demo` to query the table named `my_table`:
   ```SQL
   REVOKE SELECT ON TABLE public.my_table FROM USER uat_demo;
   ```
5. Reclaim the permission of the role `reporting_role` to create views in `sales` mode:
   ```SQL
   REVOKE CREATE VIEW ON SCHEMA sales FROM ROLE reporting_role;
   ```
6. Reclaim all permissions of the user `data_engineer` in the `lakehouse_public` workspace:
   ```SQL
   REVOKE ALL PRIVILEGES ON WORKSPACE lakehouse_public FROM USER data_engineer;
   ```
Please choose the appropriate permission type and object to operate according to your actual needs. When executing this command, ensure that you have sufficient permissions to revoke the permissions of other users or roles.