# CURRENT_INSTANCE_ROLES

#### Introduction

The `CURRENT_INSTANCE_ROLES` function returns the list of roles that the current user holds at the Instance level. It takes no parameters and returns `ARRAY<STRING>`, where each element is an instance-level role name.

The difference from `CURRENT_ROLES()`: `CURRENT_ROLES()` returns Workspace-level roles as a comma-separated string; `CURRENT_INSTANCE_ROLES()` returns Instance-level roles as a string array.

#### Syntax

```sql
CURRENT_INSTANCE_ROLES()
```

#### Return Value

`ARRAY<STRING>` — each element is the name of one Instance-level role held by the current user. The order of results is not guaranteed.

#### Examples

Query the current user's list of instance-level roles:

```sql
SELECT CURRENT_INSTANCE_ROLES();
```

Example result:

```
["instance_sre","instance_datasource_admin","instance_admin"]
```

#### Notes

- Returns Instance-level roles only; Workspace-level roles are not included. Use `CURRENT_ROLES()` to see Workspace-level roles.
- The set of roles returned depends on the current session user. The role names shown in the example are illustrative; actual results vary by user permissions.
- The return type is `ARRAY<STRING>`, which can be used with array functions such as `ARRAY_CONTAINS`.

#### Related Functions

- `CURRENT_USER()`: returns the username of the current session.
- `CURRENT_ROLES()`: returns the Workspace-level roles of the current user as a comma-separated string.
