# Description

This document describes how to use the GRANT statement in Lakehouse SQL to grant specified permissions to a role. Through this operation, the role will gain access and operation permissions to the specified resources.

# Syntax for Workspace User and Role Permission Management

### 1. Grant Workspace Level Permissions
```SQL
GRANT workspacePrivileges  ON WORKSPACE  workspace_name
| workspaceObjectPriveleges ON { ROLE | SCHEMA | VCLUSTER | DATALAKE | FUNCTION  workspace_object_name
| schemaPrivileges ON SCHEMA schema_name  
| schemaObjectPriveleges  ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
TO ROLE  rolename
```
- **Parameter Description:**
  - `workspacePrivileges`: Specifies the Workspace level privileges to be granted, such as: CREATE SCHEMA, CREATE VCLUSTER.
  - `workspace_name`: Specifies the name of the Workspace to be authorized.
  - `rolename`: Specifies the name of the role to be granted privileges.

### 2. Grant Workspace Object Privileges
```SQL
GRANT workspaceObjectPriveleges ON { ROLE | SCHEMA | VCLUSTER | DATALAKE | FUNCTION } workspace_object_name TO ROLE rolename;
```
- **Parameter Description:**
  - `workspaceObjectPriveleges`: Specifies the granted Workspace object privileges, such as: ALTER, DROP, READ METADATA, ALL [PRIVILEGES].
  - `workspace_object_name`: Specifies the name of the Workspace object to be authorized.
  - `rolename`: Specifies the name of the role to be granted permissions.

### 3. Grant Schema Level Permissions
```SQL
GRANT schemaPrivileges ON SCHEMA schema_name TO ROLE rolename;
```
- **Parameter Description:**
  - `schemaPrivileges`: Specifies the schema-level privileges to be granted, such as: CREATE TABLE, CREATE VIEW, CREATE MATERIALIZED VIEW, ALL.
  - `schema_name`: Specifies the name of the schema to be authorized.
  - `rolename`: Specifies the name of the role to be granted privileges.

### 4. Grant Schema Object Privileges
```SQL
GRANT schemaObjectPriveleges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name TO ROLE rolename;
```
- **Parameter Description:**
  - `schemaObjectPriveleges`: Specifies the schema object privileges to be granted, such as: ALTER, DROP, SELECT, INSERT, READ METADATA, ALL.
  - `schema_object_name`: Specifies the name of the schema object to be authorized.
  - `rolename`: Specifies the name of the role to be granted the privileges.

## Usage Example

Example 1: Granting a role the permission to create a VIRTUAL CLUSTER
```SQL
GRANT CREATE VCLUSTER ON WORKSPACE lakehouse_public TO ROLE simple_role;
```
Example 2: Grant Role Permission to Modify VIRTUAL CLUSTER
```SQL
GRANT ALTER VCLUSTER ON VCLUSTER default TO ROLE simple_role;
```
Example 3: Granting Role Permissions to Create Tables and Create Views
```SQL
GRANT CREATE VIEW, CREATE TABLE ON SCHEMA public TO ROLE simple_role;
```
Example 4: Granting a Role Query and Modification Permissions on a Specified Table
```SQL
GRANT SELECT, ALTER ON TABLE public.my_table TO ROLE my_role;
```
Example 5: Granting Role Query and Modification Permissions on a Specified View
```SQL
GRANT SELECT, ALTER ON VIEW public.my_view TO ROLE my_role;
```
Example 6: Granting Role Query and Modification Permissions on a Specified Materialized View
```SQL
GRANT SELECT, ALTER ON MATERIALIZED VIEW public.my_materialized_view TO ROLE my_role;
```
By the above example, you can grant appropriate permissions to roles based on actual needs. Please note that the granted permissions should match the responsibilities and job content of the roles to ensure data security and reasonable allocation of permissions.

# Instance Role Authorization

Instance Roles can be used to grant global permissions across workspaces, and the authorization targets can include users or other roles.

## Syntax Description

```sql
-- Grant an Instance Role to a user or role
GRANT INSTANCE ROLE <role_name> TO USER <user_name>;

-- Grant global permissions to an Instance Role
GRANT <privilege> ON WORKSPACE <workspace_name> TO INSTANCE ROLE <role_name>;

-- Revoke permissions from an Instance Role
REVOKE <privilege> ON WORKSPACE <workspace_name> FROM INSTANCE ROLE <role_name>;

-- View permissions granted to an Instance Role
SHOW GRANTS TO INSTANCE ROLE <role_name>;
```

#### Example

```sql
-- Grant an Instance Role to a user
GRANT INSTANCE ROLE inst_role TO USER lh_engine_test_01;

-- Grant all permissions on a workspace
GRANT ALL ON WORKSPACE ws1 TO INSTANCE ROLE inst_role;

-- View permissions (expected to include cross-workspace authorization records)
SHOW GRANTS TO INSTANCE ROLE inst_role;

-- Revoke permissions on a workspace
REVOKE ALL ON WORKSPACE ws1 FROM INSTANCE ROLE inst_role;

-- Verify permission revocation
SHOW GRANTS TO INSTANCE ROLE inst_role;

-- Grant permissions on a single table (standard syntax compatibility)
GRANT ALL ON TABLE ws1.schema.table TO INSTANCE ROLE inst_role;
```
# Instance Role Authorization

Instance Roles can be used to grant global permissions across workspaces, and the authorization targets can include users or other roles.

## Syntax Description

```sql
-- Grant an Instance Role to a user or role
GRANT INSTANCE ROLE <role_name> TO USER <user_name>;

-- Grant global permissions to an Instance Role
GRANT <privilege> ON WORKSPACE <workspace_name> TO INSTANCE ROLE <role_name>;

-- Revoke permissions from an Instance Role
REVOKE <privilege> ON WORKSPACE <workspace_name> FROM INSTANCE ROLE <role_name>;

-- View permissions granted to an Instance Role
SHOW GRANTS TO INSTANCE ROLE <role_name>;
```

#### Example

```sql
-- Grant an Instance Role to a user
GRANT INSTANCE ROLE inst_role TO USER lh_engine_test_01;

-- Grant all permissions on a workspace
GRANT ALL ON WORKSPACE ws1 TO INSTANCE ROLE inst_role;

-- View permissions (expected to include cross-workspace authorization records)
SHOW GRANTS TO INSTANCE ROLE inst_role;

-- Revoke permissions on a workspace
REVOKE ALL ON WORKSPACE ws1 FROM INSTANCE ROLE inst_role;

-- Verify permission revocation
SHOW GRANTS TO INSTANCE ROLE inst_role;

-- Grant permissions on a single table (standard syntax compatibility)
GRANT ALL ON TABLE ws1.schema.table TO INSTANCE ROLE inst_role;
```