## Function

The `SHOW USERS` command lists all user information in the current workspace, including username, default compute cluster, default Schema, and comments.

## Syntax

```SQL
SHOW USERS;
```

## Return Field Description

| Field Name | Description |
|---|---|
| `name` | Username |
| `default_vcluster` | Name of the user's default compute cluster; empty if not set |
| `default_schema` | The user's default Schema; empty if not set |
| `comment` | User comment; empty if not set |

## Usage Example

1. Query all users in the current workspace:

   ```SQL
   SHOW USERS;
   ```

   Example result:

   | name | default_vcluster | default_schema | comment |
   |---|---|---|---|
   | tester | | | |
   | qiliang | default | | |
   | sysservice_decision | | | |

## Notes

- `SHOW USERS` does not support `LIKE` or `WHERE` clause filtering; it only returns the full list of users.
- Executing this command requires the appropriate administrative permissions.
