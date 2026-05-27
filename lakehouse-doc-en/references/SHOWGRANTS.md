# Description

**View Permission Information**: This command is used to query the permissions owned by the current user or specified role, helping users understand the permission settings and ensure the security of data access.

# Workspace Role Permission Query Syntax
```SQL
-- View the current user's permissions
SHOW GRANTS;

-- Query the permissions of a specified role
SHOW GRANTS TO ROLE role_name;
```
**Parameter Description:**

- **role_name**: The name of the role whose permissions need to be queried. This role must exist in the current database space.

## Usage Example

**Example 1**: View the permissions of the current user
```SQL
SHOW GRANTS;
```
After executing this command, the system will list all the permissions information that the current user has.

**Example 2**: Query the permissions of a specified role
```SQL
SHOW GRANTS TO ROLE simple_role;
```
After executing this command, the system will list the permission information owned by the `simple_role` role.

**Example 3**: Querying role information with multiple permissions

Assuming there is a role named `admin_role` with multiple permissions, you can use the following command to query:
```SQL
SHOW GRANTS TO ROLE admin_role;
```
After executing this command, the system will list all the permissions that the `admin_role` role has.
# Instance Role Permission Query Syntax

```sql
-- Query the permissions of a specified role
SHOW GRANTS TO INSTANCE ROLE role_name;
```

**Parameter Description:**

- **role_name**: The name of the role whose permissions need to be queried. This role must exist in the current database workspace.

## Usage Example

```sql
-- View the permissions of a specific role
SHOW GRANTS TO INSTANCE ROLE instanc_datamap_user;
```