# Configuring Access Control

This document describes how to configure access control policies for accounts and metadata objects in Singdata Lakehouse. By properly configuring access control, you can ensure that access to data and objects is limited to authorized users and roles, following the principle of least privilege to enhance system security.

## Instance-Level Management

### Assigning Additional Administrator Users for an Instance

In Singdata Lakehouse, the user who creates a service instance is granted the "instance administrator" (`instance_admin`) role by default. To ensure there is always at least one user who can perform instance-level management tasks (such as creating workspaces and managing instance-level roles), you must retain at least one user when removing users with the `instance_admin` role; otherwise, an error will be returned. It is recommended to designate at least one additional user as an instance administrator to avoid disruptions caused by user unavailability or other exceptional circumstances.

^

### Granting Instance-Level Roles

Service instance-level roles can only be granted via the Web UI. Only users with the `instance_admin` role can perform this operation.

In the service instance, navigate to **Admin** -> **Security**, and switch to the **Roles** tab.

:-: ![](.topwrite/assets/image_1734853864093.png =791)

Click on the instance role you want to grant to enter its detail page, then click **Grant to User**:

:-: ![](.topwrite/assets/image_1734853972562.png =793)

In the dialog, select the users to grant, then click the **Grant** button to complete the instance role assignment.

^

## Workspace-Level Management

### Designating a Workspace Administrator

The user who creates a workspace is granted the "workspace administrator" (`workspace_admin`) role for that workspace by default. This role has full permissions to manage the workspace. Each workspace must have at least one user granted the workspace administrator role; multiple users can hold this role simultaneously.

### Managing Roles and Members in a Workspace

Roles and members in each workspace are independent of other workspaces and must be granted separately. Only users with the `workspace_admin` role in a given workspace can manage role grants, creation, and deletion, as well as adding and removing members within that workspace.

#### Managing Workspace Members

For a user to use compute clusters (VClusters) and execute SQL within a workspace, they must first join that workspace. Workspace administrators can add users to a workspace using the following two methods:

**Via Web UI**

After entering the service instance, click **Admin** -> **Workspaces** in the menu to go to the workspace list. Click on a workspace name to enter its detail page.

:-: ![](.topwrite/assets/image_1734854163713.png =795)

On the workspace detail page, click the **+ Add User** button, and select users in the dialog. Only users who exist in the service instance and are not currently members of this workspace will be displayed. Select one or more users and click **Add User** or **Add User and Grant Role** to add the selected users to the workspace. After successful addition, you can find the new users in the workspace's **Users** list.

In the workspace's **Users** list, click the **...** menu next to a user and select **Remove User** to remove that user from the workspace. The removed user will immediately lose all granted workspace roles and lose the ability to use compute clusters (VClusters) or execute SQL in that workspace.

:-: ![](.topwrite/assets/image_1734876545148.png =788)

Note that users removed from a workspace will retain any data permissions directly granted to them, meaning they can exercise those data permissions in other workspaces to query or modify data. Therefore, it is recommended to manage permissions through role grants to reduce the complexity of permission management in such scenarios.

**Via SQL**

To add a user to a workspace via JDBC, execute the following statement:

```SQL
CREATE USER <user_name>;
```

Replace `<user_name>` with the username to add. Only users who exist in the service instance and are not currently members of this workspace can be added.

To remove a user from a workspace:

```SQL
DROP USER <user_name>;
```

Replace `<user_name>` with the username to remove. This operation does not delete the user identity; it only removes the user from the current workspace.

### Using Workspace-Level Roles

#### Development Within a Workspace

Development within a workspace requires: the ability to execute SQL in the workspace (granted upon joining the workspace); access to compute resources in the workspace; and permissions on the relevant data objects.

Each workspace includes the following preset roles that have one or more of the above permissions by default. You can grant these roles to users to quickly get started with data development.

**Workspace Developer (`workspace_dev`) Role**

The `workspace_dev` role has read/write permissions on all data objects (tables, views, dynamic tables, etc. — see 'Metadata Objects') and usage permissions on all compute clusters within the workspace by default.

After being granted the `workspace_dev` role, users can directly use the **Development** feature in the Web UI or connect via JDBC for data development.

Note that the default data object read/write permissions of the `workspace_dev` role do not allow re-granting to others. To grant read or write permissions on data objects to other roles, use a user with the `workspace_admin` role.

**Workspace Analyst (`workspace_analyst`) Role**

The `workspace_analyst` role has usage permissions on all compute clusters and read metadata permissions on all data objects (tables, views, dynamic tables, etc.) within the workspace by default. However, it does not have SELECT permissions on data objects, meaning it cannot execute SELECT queries on any tables or views. To perform data query and analysis with the `workspace_analyst` role, you must grant SELECT permission on the target data objects.

For granting data permissions to the `workspace_analyst` role, refer to the GRANT statement documentation.

**Using Custom Roles or Users**

Custom roles and users can also execute SQL for development or data query analysis within a workspace after being granted appropriate permissions, but they cannot use the **Development** feature in the Web UI. Granting permissions to custom roles and users must be performed by users with the `workspace_admin` role. Refer to the following statements for authorization:

```SQL
-- Grant usage and metadata read permissions on all compute clusters in the workspace to a custom role
GRANT USE, READ METADATA ON ALL VCLUSTERS TO ROLE <CUSTOM_ROLE_NAME>;
-- [Optional] Grant usage and metadata read permissions on a specific compute cluster to a custom role
GRANT USE, READ METADATA ON VCLUSTER <VCLUSTER_NAME> TO ROLE <CUSTOM_ROLE_NAME>;

-- Grant select and metadata read permissions on all objects in a schema to a custom role
GRANT SELECT, READ METADATA ON ALL OBJECTS IN SCHEMA <SCHEMA_NAME> TO ROLE <CUSTOM_ROLE_NAME>;
-- Grant select and metadata read permissions on a specific table to a custom role
GRANT SELECT, READ METADATA ON TABLE <TABLE_NAME> TO ROLE <CUSTOM_ROLE_NAME>;
```

To grant permissions to a user, replace `TO ROLE <CUSTOM_ROLE_NAME>` with `TO USER <USER_NAME>` in the above statements.

#### Submitting and Maintaining Scheduled Tasks

Submitting scheduled tasks in a workspace can only be done through the **Development** feature in the Web UI. The `workspace_admin` and `workspace_dev` roles have the permission to submit job scripts as scheduled tasks.

:-: ![](.topwrite/assets/image_1734876961826.png =802)

^

The system role for maintaining scheduled tasks in a workspace is `workspace_sre` (Workspace SRE). Users with this role can manage scheduled tasks within their workspace through the **Task Operations** and **Monitoring & Alerting** features under the **Operations** menu, as well as the **Data Quality** feature under the **Data** menu.

The `workspace_sre` role has operational management permissions for all scheduled tasks in the workspace, but does not have compute resource usage or data object query permissions.

For unified management of scheduled tasks across all workspaces in an instance, you can grant the instance-level role `instance_sre` (Instance SRE). This role's permissions are the union of all `workspace_sre` role permissions within the service instance.

#### Creating Custom Roles

To practice the principle of least privilege, it is recommended to create custom roles aligned with your organization's business functions and assign them permissions for specific objects and operations. This allows you to precisely control user access to specific data or objects.

General process for creating custom roles:

1. Create a custom role (CREATE ROLE statement).
2. Grant required permissions to the role (GRANT statement).
3. Grant the role to the appropriate users (GRANT ROLE statement or via Web UI).

**Note**: In Singdata Lakehouse, roles cannot be granted to other roles; that is, role hierarchy is not supported. All roles are granted directly to users, eliminating the complexity of determining a user's effective permissions through hierarchical role inheritance.

#### Granting or Revoking Roles from Users

You can grant or revoke roles from users via the Web UI or SQL. Only users with the `instance_admin` or `workspace_admin` role can grant or revoke roles. The `instance_admin` role can grant instance-level roles to all users in the instance; the `workspace_admin` role can grant workspace-level roles to members within the workspace.

**Via Web UI**

On the **Security** -> **Roles** page, you can view instance-level and workspace-level roles in the current instance.

:-: ![](.topwrite/assets/image_1734878372389.png =784)

The `instance_admin` role can view all instance-level roles and all workspace-level roles, and manage grants for all instance-level roles.

The `workspace_admin` role can view all roles within their workspace and manage grants for those roles. If a user holds the `workspace_admin` role in multiple workspaces, they can manage role grants across all those workspaces.

To grant a role, click the role name to enter its detail page, where you can view all users currently granted the role. Click **+ Grant to User**, select users in the dialog, and click **Grant** to assign the role to users.
:-: ![](.topwrite/assets/image_1734878510613.png =798)

To revoke a role, click the **...** menu next to a user and select **Remove User** to remove the user's association with that role.

In the **Admin** -> **Workspaces** list, enter a workspace detail page, and on the **Roles** tab you can also view the role list within the workspace and grant or revoke roles using the same process.

:-: ![](.topwrite/assets/image_1734878871234.png =795)

***

**Via SQL**

Only workspace-level users support SQL-based authorization. Execute the following statement in a workspace to grant a workspace role to a user:

```SQL
Grant ROLE <ROLE_NAME> TO USER <USER_NAME>;
```

Execute the following to revoke a role from a user:

```SQL
REVOKE ROLE <ROLE_NAME> FROM USER <USER_NAME>;
```

### Example: Creating a Custom Role and Granting Permissions

**Tip**: Creating custom roles and granting permissions to custom roles is currently not supported via the Web UI. You must use SQL.

Suppose you want to create a workspace-level role `r1` to manage a specific table `t1` in schema `s1`. You need to grant `r1`:

* Usage permission (USAGE) on a compute cluster (e.g., named `v1`).
* [Optional] READ METADATA permission on the compute cluster (e.g., `v1`) so it appears on the compute cluster page or in SHOW VCLUSTERS results.
* ALL permission on table `s1.t1` to perform operations such as SELECT, INSERT, UPDATE, ALTER.

#### Create the Custom Role

```
CREATE ROLE r1;
```

#### Grant Permissions to the Role

```
-- Grant usage permission on compute cluster (e.g., v1) to role r1
GRANT use ON VCLUSTER v1 TO ROLE r1;
-- [Optional] Grant read metadata permission on compute cluster (e.g., v1) to role r1
GRANT read metadata ON VCLUSTER v1 TO ROLE r1;


-- Grant all permissions on table s1.t1 to role r1
GRANT all ON table s1.t1 to ROLE r1;

```

#### Grant the Role to a User

```
GRANT ROLE r1 TO USER u1;
```

### Example: Creating a Read-Only Role

If you need a role that can only query (read-only access) all tables in a schema, follow the same process as creating a custom role. The difference is that you grant only SELECT and READ METADATA permissions, without any write, modify, or delete permissions. Use `ALL TABLES IN SCHEMA s1` to cover all current and future table objects in `s1`, simplifying the grant expression.

For example, to grant SELECT and READ METADATA permissions on all tables in schema `s1` to the `read_only` role:

```
GRANT SELECT, READ METADATA ON ALL TABLES IN SCHEMA s1 TO ROLE read_only;
```

Note that if the `read_only` role does not have usage permission on a compute cluster, it cannot use compute resources to query tables. You must also grant the role usage permission on at least one compute cluster (VCluster).

For example, granting the `read_only` role usage permission on a compute cluster named `demo_vcluster`:

```
GRANT USE ON VCLUSTER demo_vcluster TO ROLE read_only;
```

### Viewing Granted Permissions

Use the SHOW GRANTS command to view the current permission state of an object or role. For example:

```
-- View granted permissions on schema d1.s1
SHOW GRANTS ON SCHEMA d1.s1;

-- View permissions granted to role r1
SHOW GRANTS TO ROLE r1;

-- View permissions and roles granted to user smith
SHOW GRANTS TO USER smith;
```

^
