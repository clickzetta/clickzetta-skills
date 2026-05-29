## Description

This document introduces the SQL syntax for creating custom roles and replacing existing roles.

## Syntax
```SQL
CREATE [OR REPLACE] ROLE [IF NOT EXISTS] role_name COMMENT '';
```
- **CREATE**: Create a new role.
- **OR REPLACE** (optional): If a role with the same name already exists, replace that role.
- **IF NOT EXISTS** (optional): If the specified role name does not exist, create a new role. If the role already exists, no error will be reported, and no new role will be created.
- **role_name**: Specify the name of the new role. Note that the role name cannot be the same as the system predefined role names.
- **COMMENT** (optional): Add a comment to the role, which can be left blank or provide information about the role.

## Example

1. Create a custom role named `simple_role`:
   ```SQL
   CREATE ROLE simple_role;
   ```
2. Create a role named `admin_role` and add a comment to it:
```SQL
CREATE ROLE admin_role COMMENT 'Role with advanced permissions';
```
```markdown
3. Replace the existing `existing_role` role:
```
   ```SQL
   CREATE OR REPLACE ROLE existing_role;
   ```
```markdown
4. Create a role named `new_role`. If the role already exists, a new role will not be created:
```
   ```SQL
   CREATE ROLE IF NOT EXISTS new_role;
   ```
# Instance Role Management

LakeHouse supports creating roles at the **instance level** to achieve unified permission control across workspaces, meeting the needs for fine-grained access control in multi-team collaboration scenarios. This operation requires `INSTANCE_ADMIN` privileges.

## Syntax Description

```sql
-- Create an Instance Role (if it does not exist)
CREATE INSTANCE ROLE IF NOT EXISTS <role_name>;

-- Drop an Instance Role (if it exists)
DROP INSTANCE ROLE IF EXISTS <role_name>;

-- Show all Instance Roles
SHOW INSTANCE ROLES;
```

#### Example

```sql
DROP INSTANCE ROLE IF EXISTS inst_role;

CREATE INSTANCE ROLE IF NOT EXISTS inst_role;

SHOW INSTANCE ROLES;
```