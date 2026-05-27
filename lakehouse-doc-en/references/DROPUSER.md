# Remove User from Current Workspace

## Description

This command is used to remove a specified user from the current workspace, ensuring that only authorized users can access and operate the workspace.

## Syntax
```SQL
DROP USER [IF EXISTS] user_name;
```
- `IF EXISTS`: Optional parameter used to check if the specified user exists in the current workspace. If it exists, the removal operation is executed; if it does not exist, no operation is performed.
- `user_name`: The name of the user to be removed from the current workspace.

##  Example

1. Remove the user named "uat\_test":
```SQL
DROP USER uat_test;
```
2. Remove the user named "john\_doe". If the user does not exist, do not perform any operation:
```SQL
DROP USER IF EXISTS john_doe;
```
## Notes

- Before executing this command, please ensure you have sufficient permissions to remove the specified user.
- After removing the user, they will no longer be able to access or operate any resources in the current workspace. Please proceed with caution to avoid unnecessary losses due to accidental operations.
- If you wish to remove multiple users, please execute the `DROP USER` command multiple times separately.