# Delete Role from Current Workspace

## Description

This command is used to delete a role from the current workspace. Please note that after performing this operation, the role will no longer have access to the associated resources and permissions.

## Syntax
```SQL
DROP ROLE [IF EXISTS] role_name;
```
- `role_name`: The name of the role to be deleted.


## Example

1. Delete the role named `simple_role`:
```SQL
DROP ROLE simple_role;
```
2. Use the `IF EXISTS` option to delete the role named `temporary_role` to avoid error messages when the role does not exist:
```SQL
DROP ROLE IF EXISTS temporary_role;
```
3. Delete the role `report_user` with specific permissions:
```SQL
DROP ROLE report_user;
```
## Precautions

- Executing this command will permanently delete the role and its associated permissions and resources. Please proceed with caution.
- Before deleting a role, ensure that the permissions and resources of that role have been assigned to other roles or users to prevent data loss or permission issues.
- If you are unsure whether a role is still in use, please perform a query operation first to ensure that important roles are not accidentally deleted.

# Deleting an Instance Role

```sql
DROP INSTANCE ROLE IF EXISTS <role_name>;
```

## Usage Notes

- Before executing the deletion, ensure that the role is no longer needed. Once deleted, the role cannot be recovered.
- Using the `IF EXISTS` option prevents errors from occurring if the role does not exist.
- This operation requires `INSTANCE_ADMIN` privileges.