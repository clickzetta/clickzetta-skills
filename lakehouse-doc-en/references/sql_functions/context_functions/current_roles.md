# CURRENT_ROLES

#### Introduction

The `CURRENT_ROLES` function returns all roles that the current user holds in the current Workspace. It takes no parameters and returns a string value, with multiple roles separated by commas.

The difference from `CURRENT_INSTANCE_ROLES()`: `CURRENT_ROLES()` returns Workspace-level roles as a STRING; `CURRENT_INSTANCE_ROLES()` returns Instance-level roles as an array.

#### Syntax

```sql
CURRENT_ROLES()
```

#### Return Value

`CURRENT_ROLES` returns a string representing all roles that the current user holds in the current Workspace. Multiple roles are separated by commas.

#### Examples

1. Query the current user's roles in the current Workspace:

```sql
SELECT CURRENT_ROLES();
```

   Example result:

   ```
   workspace_admin,system_admin,workspace_analyst
   ```
