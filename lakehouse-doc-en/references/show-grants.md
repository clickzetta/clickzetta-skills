# SHOW GRANTS

Queries the permissions held by the current user, a specified role, or a specified user, helping you understand permission settings and ensure data access security.

## View Permissions on an Object

View which permissions have been granted on a specific object (table, schema, workspace, VCluster, etc.).

```Plain
SHOW GRANTS ON TABLE [schema.]table_name;
SHOW GRANTS ON SCHEMA schema_name;
SHOW GRANTS ON WORKSPACE workspace_name;
SHOW GRANTS ON VCLUSTER vcluster_name;
SHOW GRANTS ON VOLUME [schema.]volume_name;
SHOW GRANTS ON ROLE role_name;
```

### Usage Examples

```SQL
-- View all grants on a table
SHOW GRANTS ON TABLE public.orders;

-- View all grants on a schema
SHOW GRANTS ON SCHEMA public;

-- View all grants on a VCluster
SHOW GRANTS ON VCLUSTER default;

-- View all grants on a workspace
SHOW GRANTS ON WORKSPACE my_workspace;
```

The returned columns are the same as those for `SHOW GRANTS TO ROLE`; see the return column description below.

---

## Workspace Role Permission Query Syntax

```Plain
-- View the current user's permissions
SHOW GRANTS;

-- Query permissions for a specified role
SHOW GRANTS TO ROLE role_name;

-- Query permissions for a specified user
SHOW GRANTS TO USER user_name;
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `role_name` | Yes (when querying a role) | The name of the role to query permissions for; the role must exist in the current workspace |
| `user_name` | Yes (when querying a user) | The name of the user to query permissions for; the user must exist in the current workspace |

### Return Column Description

| Column Name | Description |
|-------------|-------------|
| `granted_type` | Grant type: `ROLE` (role grant) or `PRIVILEGE` (object privilege grant) |
| `privilege` | Permission name, such as `SELECT TABLE`, `workspace_dev`, etc. |
| `conditions` | Additional conditions (usually empty) |
| `granted_on` | Type of object the permission is granted on, such as `ROLE`, `TABLE`, `SCHEMA`, etc. |
| `object_name` | Full name of the granted object (including workspace prefix) |
| `granted_to` | Type of the grantee, such as `ROLE` or `USER` |
| `grantee_name` | Full name of the grantee (including workspace prefix) |
| `grantor_name` | Name of the user who performed the grant operation |
| `grant_option` | Whether the permission can be re-granted: `true` means the permission can be granted to other users |
| `granted_time` | Time when the permission was granted |

## Usage Examples

1. View the current user's permissions:

   ```SQL
   SHOW GRANTS;
   ```

2. Query permissions for role `test_developer_role`:

   ```SQL
   SHOW GRANTS TO ROLE test_developer_role;
   ```

   Example output:

   | granted_type | privilege | granted_on | object_name | granted_to | grantee_name | grantor_name | grant_option | granted_time |
   |---|---|---|---|---|---|---|---|---|
   | PRIVILEGE | CREATE TABLE | SCHEMA | quick_start.semantic_model_test | ROLE | quick_start.test_developer_role | quick_start.qiliang | false | 2025-03-27 20:43:39.419 |

3. Query permissions for user `tester`:

   ```SQL
   SHOW GRANTS TO USER tester;
   ```

   Example output:

   | granted_type | privilege | granted_on | object_name | granted_to | grantee_name | grantor_name | grant_option | granted_time |
   |---|---|---|---|---|---|---|---|---|
   | ROLE | workspace_dev | ROLE | quick_start.workspace_dev | USER | quick_start.tester | quick_start.qiliang | false | 2025-03-27 20:43:39.419 |

## Notes

- Executing this command requires the `workspace_admin` or `security_admin` role, or the query must be for the currently logged-in user's own permissions.
- Results include directly granted permissions, as well as permissions obtained indirectly through roles (rows where `granted_type` is `ROLE` indicate permissions obtained through a role).
- Usernames and role names are case-sensitive. Ensure correct input.

## Instance Role Permission Query Syntax

```Plain
-- Query permissions for a specified Instance Role
SHOW GRANTS TO INSTANCE ROLE role_name;
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `role_name` | Yes | The name of the Instance Role to query permissions for |

## Instance Usage Example

```SQL
-- View permissions for an Instance Role
SHOW GRANTS TO INSTANCE ROLE instance_datamap_user;
```
