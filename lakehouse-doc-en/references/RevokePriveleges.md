## Description

This command is used to revoke the permissions of a specified role. By using the REVOKE statement, you can revoke permissions at different levels, including workspace, workspace objects, schema, and schema object levels.

# Syntax for Workspace User and Role Permission Management
```SQL
REVOKE [workspacePrivileges | workspaceObjectPrivileges | schemaPrivileges | schemaObjectPrivileges]
ON [WORKSPACE | {ROLE | SCHEMA | VCLUSTER | DATALAKE | FUNCTION | workspace_object_name | SCHEMA | {TABLE | VIEW | MATERIALIZED VIEW} schema_object_name]
FROM ROLE role_name;
```
### Parameter Description

1. **workspacePrivileges**: The permissions to create objects in the workspace, such as `CREATE SCHEMA` and `CREATE VCLUSTER`.

2. **workspaceObjectPrivileges**: The permissions to modify and view metadata of objects in the workspace, such as `ALTER`, `DROP`, `READ METADATA`, and `ALL [PRIVILEGES]`.

3. **schemaPrivileges**: The permissions to create objects in the schema, such as `CREATE TABLE`, `CREATE VIEW`, and `CREATE MATERIALIZED VIEW`.

4. **schemaObjectPrivileges**: The permissions to modify, delete, query, etc., objects in the schema, such as `ALTER`, `DROP`, `SELECT`, `INSERT`, `READ METADATA`, and `ALL`.

## Example

1. Revoke the permission for the role `simple_role` to create `VIRTUAL CLUSTER` in the `lakehouse_public` workspace:
   ```SQL
   REVOKE CREATE VCLUSTER ON WORKSPACE lakehouse_public FROM ROLE simple_role;
   ```
2. Revoke the `ALTER` permission of the role `simple_role` on the `VIRTUAL CLUSTER` named `default`:
   ```SQL
   REVOKE ALTER VCLUSTER ON VCLUSTER default FROM ROLE simple_role;
   ```
3. Reclaim the permissions of the role `uat_demo` to create tables and views under the `public` schema:
   ```SQL
   REVOKE CREATE VIEW, CREATE TABLE ON SCHEMA public FROM ROLE uat_demo;
   ```
4. Revoke the `READ METADATA` permission of the role `reporting_role` on the `DATALAKE` named `sales_data`:
   ```SQL
   REVOKE READ METADATA ON DATALAKE sales_data FROM ROLE reporting_role;
   ```
5. Revoke the `ALTER` and `DROP` permissions of the role `admin_role` on the `FUNCTION` named `order_summary`:
   ```SQL
   REVOKE ALTER, DROP ON FUNCTION order_summary FROM ROLE admin_role;
   ```

6. Revoke the `SELECT` and `INSERT` permissions of the role `analyst_role` on the `TABLE` named `customer_orders` under the `public` schema:

   ```SQL
   REVOKE SELECT, INSERT ON TABLE public.customer_orders FROM ROLE analyst_role;
   ```
By the above example, you can flexibly revoke the permissions of roles according to actual needs. Please note that the user executing the REVOKE statement needs to have sufficient permissions to revoke the permissions of other roles.

# Instance Role Permission Management
LakeHouse supports fine-grained revocation of cross-workspace permissions for Instance Roles, ensuring the flexibility and security of permission control.

## Syntax Description
```sql
-- Revoke permissions of an Instance Role on a workspace
REVOKE <privilege> ON WORKSPACE <workspace_name> FROM INSTANCE ROLE <role_name>;

-- Revoke permissions of an Instance Role on a table or database
REVOKE <privilege> ON TABLE <workspace>.<schema>.<table> FROM INSTANCE ROLE <role_name>;

REVOKE <privilege> ON DATABASE <workspace>.<schema> FROM INSTANCE ROLE <role_name>;

-- Remove a user's Instance Role assignment
REVOKE INSTANCE ROLE <role_name> FROM USER <user_name>;
```

## Example
```sql
-- Revoke all permissions on a workspace
REVOKE ALL ON WORKSPACE ws1 FROM INSTANCE ROLE inst_role;

-- Verify the revocation result (expected to have no ALL permissions)
SHOW GRANTS TO INSTANCE ROLE inst_role;

-- Revoke permissions on a single table
REVOKE ALL ON TABLE ws1.public.sales FROM INSTANCE ROLE inst_role;

-- Remove the Instance Role from a user
REVOKE INSTANCE ROLE inst_role FROM USER lh_engine_test_01;
```