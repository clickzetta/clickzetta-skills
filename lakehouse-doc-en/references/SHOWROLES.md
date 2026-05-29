# Description

This command is used to query all role information under the current database space. By executing this command, users can easily understand and manage the permission allocation in the database.

# Workspace Role Management
```SQL
SHOW ROLES [LIKE pattern];
```
## Parameter Description

- **LIKE pattern** (Optional): This parameter is used to filter by role name, displaying only the role information that matches the given pattern. The filter uses case-insensitive pattern matching and supports SQL wildcards `%` and `_`. For example, using `LIKE '%admin%'` will only display role information that contains the text "admin".

## Usage Example

1. Query all roles in the current space:
   ```SQL
   SHOW ROLES;
   ```
```markdown
2. Query role names containing the text "admin":
```
   ```SQL
   SHOW ROLES LIKE '%admin%';
   ```
```markdown
3. Query detailed information of a specific role:
```
   ```SQL
   SHOW ROLES LIKE 'role_name';
   ```
Where `role_name` is the name of the role to be queried.

## Notes

- When executing this command, ensure that you have sufficient permissions to query role information.

Through the above instructions and examples, users can more easily understand and manage role information in the database. In practical applications, you can flexibly use the LIKE filter condition as needed to obtain the required data more efficiently.

# Instance Role Management

```sql
SHOW INSTANCE ROLES [LIKE pattern];
```

## Parameter Description

- **LIKE pattern** (Optional): This parameter is used to filter roles by name, displaying only the roles that match the given pattern. The filter uses case-insensitive pattern matching and supports SQL wildcards `%` and `_`. For example, using `LIKE '%admin%'` will display only the roles that contain the text "admin".

## Usage Example

1. Query all roles under the current instance:

   ```sql
   SHOW INSTANCE ROLES;
   ```