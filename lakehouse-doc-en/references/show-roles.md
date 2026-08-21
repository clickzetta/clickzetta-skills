# SHOW ROLES

Queries all role information in the current workspace or instance.

## Workspace Roles

### Syntax

```Plain
SHOW ROLES [LIKE 'pattern'];
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `LIKE 'pattern'` | No | Filters by role name. Supports SQL wildcards `%` (matches any string) and `_` (matches a single character). Case-insensitive |

### Return Column Description

| Column Name | Description |
|-------------|-------------|
| `name` | Role name |
| `comment` | Role description |

### Usage Examples

1. Query all roles in the current workspace:

   ```SQL
   SHOW ROLES;
   ```

   Example output:

   | name | comment |
   |------|---------|
   | system_admin | system role |
   | test_developer_role | Test role |
   | test_readonly_role | Read-only role for testing |
   | workspace_admin | System preset role with management permissions for tasks, environments, and all data objects in the workspace, as well as permissions for managing members and roles in the workspace. |
   | workspace_analyst | System preset role with development feature usage permissions and all compute cluster usage permissions. |
   | workspace_dev | System preset role with management permissions for task directories in the workspace, editing permissions for task scripts, and read and write permissions for all data objects in the workspace. |
   | workspace_sre | System preset role with management permissions for all tasks and jobs in the workspace. |

2. Query roles whose names contain `admin`:

   ```SQL
   SHOW ROLES LIKE '%admin%';
   ```

   Example output:

   | name | comment |
   |------|---------|
   | system_admin | system role |
   | workspace_admin | System preset role with management permissions for tasks, environments, and all data objects in the workspace, as well as permissions for managing members and roles in the workspace. |

3. Exact match for a role name:

   ```SQL
   SHOW ROLES LIKE 'workspace_dev';
   ```

### Notes

- Executing this command requires permission to query role information.
- System preset roles (`workspace_admin`, `workspace_analyst`, `workspace_dev`, `workspace_sre`) cannot be dropped but can be granted to users.
- `LIKE` filtering is case-insensitive.

## Instance Roles

### Syntax

```Plain
SHOW INSTANCE ROLES [LIKE 'pattern'];
```

### Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `LIKE 'pattern'` | No | Filters by role name; rules are the same as for Workspace roles |

### Return Column Description

| Column Name | Description |
|-------------|-------------|
| `name` | Instance role name |
| `comment` | Role description |

### Usage Examples

1. Query all roles in the current instance:

   ```SQL
   SHOW INSTANCE ROLES;
   ```

   Example output:

   | name | comment |
   |------|---------|
   | instance_admin | System preset role for managing the creation and deletion of all workspaces in the instance, and for managing the granting of instance-level roles. |
   | instance_datamap_admin | System preset role with management permissions for functions and objects in data assets. |
   | instance_datamap_user | System preset role with read-only permissions for data assets. |
   | instance_datasource_admin | System preset role with management permissions for data sources. |
   | instance_sensitivedata_viewer | System preset role with permission to view sensitive data. |
   | instance_sre | System preset role with management permissions for all tasks and jobs across all workspaces. |
   | instance_user | System preset role initially assigned to service instance members; has no data or functional permissions. |

2. Query instance roles whose names contain `admin`:

   ```SQL
   SHOW INSTANCE ROLES LIKE '%admin%';
   ```

### Notes

- Instance roles apply to the entire instance scope, with permissions higher than workspace roles. Grant them with caution.
- Executing this command requires instance-level role query permission.
