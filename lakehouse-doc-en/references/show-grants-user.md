## Description

This command is used to query the permissions that a specified user has in the current database, helping the user understand their access and operation permissions in the database.

## Syntax
```SQL
-- Query the permissions owned by a specified user
SHOW GRANTS TO USER user_name;
```
**Parameter Description:**

- `user_name`: The name of the user whose permissions need to be queried. This user must exist within the current database space.

## Example

1. Query the permissions of the currently logged-in user:
   ```SQL
   SHOW GRANTS TO USER user_name;
   ```

2. Query the permissions owned by the specified user "john_doe":

```SQL
SHOW GRANTS TO USER john_doe;
```

## Notes

- The user executing this command needs to have query permissions.
- When querying the permissions of other users, ensure that the correct username is used.
- Handle permission management with care to avoid leaking sensitive information or making mistakes.

## Frequently Asked Questions

**Q: How to query the currently logged-in user?**

A: Use the `CURRENT_USER()` function instead of the `user_name` parameter