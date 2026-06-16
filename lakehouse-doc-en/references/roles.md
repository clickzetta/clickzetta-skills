# Roles

## Role Definition

In the Lakehouse, a **role** is a permission management tool used to group multiple permission points together and then grant this role to one or more users.

* When a user is granted a role, the user immediately gains all permissions contained in that role.
* A role can also be granted additional permission points, enabling flexible permission expansion and management.

Compared to granting permissions directly to users one by one (ACL mode), assigning permissions through "roles" significantly simplifies management processes and is easier to maintain and audit. Therefore, it is recommended to fully use **Role-Based Access Control (RBAC)** in daily permission management.

## Role Types

Roles in the Lakehouse are divided into two types: **preset roles** and **custom roles**.

1. **Preset Roles**

   * Preset roles are roles automatically configured by the platform when a service instance is created. They **cannot have their permissions modified** or be **deleted**, but preset roles can be directly granted to users.
   * The platform presets multiple roles, covering everything from instance-level management to workspace-level management and usage, helping users quickly complete basic authorization and use product features. For all system preset roles and their default permissions, see [System Built-in Role Permission List](permissions-of-built-in-workspace-level-roles.md)

2. **Custom Roles**

   * Users can create custom roles within a **workspace** scope according to their business needs, and flexibly configure and maintain permissions for those roles.
   * Custom role permissions can be modified or deleted at any time to adapt to changing business scenario requirements.
   * **Note**: Currently, custom roles can only be created within a workspace, not at the instance level. Custom role creation is only supported via SQL execution; Web interface operation is not yet supported.

## Role Levels

The big data platform classifies metadata objects into "**instance-level**" and "**workspace-level**" categories, and roles are correspondingly divided into "**instance roles**" and "**workspace roles**":

**Instance Role**: Instance-level roles have two use cases: 1) for global control of instance-level resources and operations; 2) for cross-workspace permission granting.

**Workspace Role**: Applies to objects within a specific workspace scope (such as schema, table, virtual cluster, etc.). Workspace roles are bounded by the workspace and do not affect each other.

## Role Management and Usage

### Viewing Roles

You can view role information for the current instance and workspaces under **Management > Security > Roles**.

Or click into a workspace's details page from the **Management > Workspaces** list, switch to the **Roles** tab, and view all roles under that workspace.

Alternatively, execute the following statement in SQL to query all workspace-level roles in the currently connected workspace:

```
SHOW ROLES;
```

### Granting Roles to Users

Once a custom role has been created and has the appropriate permissions, it must be granted to users before users can actually use the permissions contained in that role.

Roles can be granted to users via the Web interface or SQL.

**Web Interface Operation**

On the **Security > Roles** page, you can view instance-level roles and workspace-level roles under the current instance.



To authorize any role, click the role name to enter the role details page, where you can see all users who have been granted this role. Click **+ Grant User**, select the users to add in the dialog, and click **Authorize** to grant the role to the users.


To remove a user who has been granted a role, click the "..." to the right of the username and select **Remove User** to revoke that user's permission to use this role.

On the **Management > Workspaces** list, enter the workspace details page, and on the **Roles** tab you can also view the role list within that workspace and perform the above operations to grant or revoke roles to/from users.


**SQL Operation**

Only workspace-level users support authorization via SQL operations. Execute the following statement within a workspace to grant a role within the workspace to a specified user:

```SQL
GRANT ROLE <ROLE_NAME> TO USER <USER_NAME>;
```

Execute the following statement to remove a specified user from a role:

```SQL
REVOKE ROLE <ROLE_NAME> FROM USER <USER_NAME>;
```

### Creating Custom Roles

Currently, only workspace-level custom roles can be created. This operation requires a user with the workspace administrator (workspace_admin) role. Custom roles can only be created via SQL.

**Creation syntax example**:

```
CREATE ROLE <ROLE_NAME>;
```

### Adding Permissions to Custom Roles

Within a workspace, you can use the GRANT statement to add permissions to custom roles. Example:

```
-- Grant a custom role read and write permissions on all tables in schema my_schema
GRANT SELECT, READ METADATA, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA my_schema
TO ROLE my_custom_role;
```

## Frequently Asked Questions

1. **What is the difference between Roles and ACL (Access Control Lists)?**

   * ACL grants permissions directly to users; roles "package" permissions and then grant them to users.
   * For scenarios with frequent personnel changes or complex permission configurations, it is recommended to prioritize the role-based approach to reduce repetitive operations.

2. **Does the system support stacking permissions from multiple roles?**

   * Yes. A user can be granted multiple roles, and the effective permissions are the union of all granted role permission scopes.

3. **Can instance roles access workspaces?**

   * No. Instance roles and workspace roles are independent of each other. Instance roles do not have and cannot obtain permissions on workspace-level objects.

4. **Can preset roles be modified or deleted?**

   * No. Preset roles are system built-in, immutable roles; you can only choose whether to grant them to users.

^
