## Description

This document introduces how to use the GRANT statement in Lakehouse SQL to grant specified permissions to a user or role. By using the GRANT statement, you can perform fine-grained permission control on users to ensure data security and compliance.

## Syntax

### 1. Grant specified permissions to a user
```SQL
GRANT workspacePrivileges ON WORKSPACE workspace_name
| workspaceObjectPrivileges ON { ROLE | SCHEMA | VCLUSTER | FUNCTION } workspace_object_name
| schemaPrivileges ON SCHEMA schema_name
| schemaObjectPrivileges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
TO USER username [ WITH GRANT OPTION];
--Parameter Explanation    
workspacePriveleges ::=
    CREATE   { SCHEMA | VCLUSTER  }
 
-- Authorization for objects under workspace
workspaceObjectPriveleges ::=
    -- SCHEMA
    ALTER ｜DROP｜READ METADATA | ALL [PRIVILEGES]
    -- VCLUSTER
    ALTER ｜DROP ｜ USE  |  READ METADATA | ALL [PRIVILEGES]
     --job
    ALTER ｜CANCEL ｜ READ METADATA  | ALL [PRIVILEGES]


-- Schema authorization
schemaPrivileges ::=
    CREATE  { TABLE |  VIEW | MATERIALIZED VIEW } | ALL

-- Authorization for objects under schema
schemaObjectPriveleges ::=
    -- table
   ALTER ｜DROP ｜SELECT | INSERT | READ METADATA | ALL 
    -- view
   ALTER ｜DROP ｜ SELECT  | ALL 
    -- MATERIALIZED VIEW
   ALTER ｜DROP | SELECT | ALL 
```
Parameter Description

**1.workspacePriveleges**
Permissions to create objects under the workspace, such as CREATE VCLUSTER

**2.workspaceObjectPriveleges**
Permissions to modify and show objects under the workspace

**3.schemaPrivileges**
Permissions to create objects under the schema

**4.schemaObjectPriveleges**
Permissions to modify, delete, and query tables under the schema

### 2 Grant specified permissions to a user
```
GRANT ROLE role_name TO USER user_name;
```
## Parameter Description

1. `workspacePrivileges`: Permissions to create objects in the workspace, such as `CREATE SCHEMA`, `CREATE VCLUSTER`, etc.
2. `workspaceObjectPrivileges`: Permissions to modify and query objects in the workspace, such as `ALTER`, `DROP`, `READ METADATA`, etc.
3. `schemaPrivileges`: Permissions to create objects in the schema, such as `CREATE TABLE`, `CREATE VIEW`, `CREATE MATERIALIZED VIEW`, etc.
4. `schemaObjectPrivileges`: Permissions to modify and query objects in the schema, such as `ALTER`, `DROP`, `SELECT`, etc.
5. `role_name`: Role name, supporting custom roles and system default roles. System default roles include `system_admin`, `user_admin`, `security_admin`, `audit_admin`, etc.
6. `username`: User name.
7. `WITH GRANT OPTION`: Indicates that the authorized user can re-authorize these permissions to other users.

## Usage Example

1. Grant the user `uat_demo` the permission to create a `VIRTUAL CLUSTER` in the `lakehouse_public` workspace:
   ```SQL
   GRANT CREATE VCLUSTER ON WORKSPACE lakehouse_public TO USER uat_demo;
   ```
2. Authorize the user `uat_demo` to modify the `VIRTUAL CLUSTER` named `default`:
   ```SQL
   GRANT ALTER VCLUSTER ON VCLUSTER default TO USER  uat_demo;
   ```
3. Grant the user `uat_demo` the permissions to create tables and views under the `public` schema:
   ```SQL
   GRANT CREATE TABLE, CREATE VIEW ON SCHEMA public TO USER uat_demo;
   ```
4. Grant the user `uat_demo` permission to query all tables and views under the `public` schema:
   ```SQL
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO USER uat_demo;
   ```
5. Permissions for the user `uat_demo` authorized to the role `user_admin` to create tables and views in the `security` schema under the `lakehouse_public` workspace:
   ```SQL
   GRANT CREATE TABLE, CREATE VIEW ON SCHEMA security TO ROLE user_admin;
   ```
By the above example, you can flexibly assign corresponding permissions to users or roles according to actual needs. Please ensure to follow the principle of least privilege when authorizing to reduce security risks.