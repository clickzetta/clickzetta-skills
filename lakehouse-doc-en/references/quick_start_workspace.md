# Building a Data Development Environment Using Workspaces

## Basic Concepts

A workspace is one of the core concepts in the Lakehouse product. It is used to organize Lakehouse resource objects (such as data objects and computing resources) and provides a relatively isolated environment for data development and scheduling task management and operations.

To achieve both isolation and ease of data exchange within a service instance, permissions between different workspaces are isolated: a service instance user needs to be added to a workspace by the workspace administrator role (workspace\_admin) to be authorized and use the data or computing resources within the workspace.

When a user has permissions for data objects within a workspace, they can perform cross-space queries or other operations within the scope of their permissions on these data objects in other workspaces.


As shown in the figure above, multiple workspaces can be created within a Lakehouse service instance. A service instance user can be added to multiple workspaces simultaneously and be granted permissions for objects within those workspaces.

Using the objects in the figure above as an example, the isolation and data interoperability of workspaces are introduced:

When the user user\_a is added to both workspace A (workspace\_a) and workspace B (workspace\_b) and is granted the necessary permissions for using computing clusters and querying data objects in both workspaces, user\_a can execute the following statements in the task script demo\_script\_ws\_a in workspace A and the task script demo\_script\_ws\_b in workspace B and obtain the query results normally.

```
select * from table workspace_a.schema_a.table_a limit 10;
```

User **user\_b** is only added to **Workspace B (workspace\_b**) and granted a set of permissions within **Workspace B**. When executing the task script **demo\_script\_ws\_b** to query **workspace\_a.schema\_a.table\_a**, an error message will indicate that **user\_b** does not have the **SELECT** permission on the table.

## Usage Scenarios

A service instance (instance) can create multiple workspaces. You can choose to use a single workspace or multiple workspaces based on your business needs. A single workspace facilitates unified management of data assets and computing resources; multiple workspaces facilitate natural boundaries of permissions, data, and computing resources between multiple teams or projects.

## Using a Single Workspace

When you are in the following usage scenarios, it is recommended to use only the default workspace as a single workspace to use Lakehouse:

* **Individual or Small Team**: The team size is small, and the scale of data and computing is not large, hoping to collaborate and manage in the same environment.
* **Single Product Line or Business Department**: Only need to manage the data and data processing flow of one business domain, with relatively low demand for fine-grained data and access control.

After the service instance is activated, the system will create a workspace named "quick\_start" by default. You can directly use this workspace for task development and other work.

In the "Account Home" of the control center, click on the activated service instance to enter the homepage of the service instance.


On the homepage of the service instance, click on any function in the left function menu such as "Development", "Computing", "Operations Monitoring", etc. The workspaces that the current account has permission to access will be listed in the upper right corner of the page, supporting switching. When using a single workspace, it defaults to the only workspace within the service instance. At this time, all task scripts and scheduling jobs are within this workspace.


## Creating and Using Multiple Workspaces

When you are in the following usage scenarios, it is recommended to create and use multiple workspaces:

* **Cross-department or Multi-project Isolation**: When data and resource access need to be isolated between business departments or projects, multiple workspaces can achieve natural permission boundaries.
* **High Security and Compliance Requirements**: Industries such as finance, healthcare, and government agencies that have high requirements for data security, compliance, and auditability need to enhance data security through strong isolation.
* **Different Billing or Budget Centers**: If multiple departments or projects bear the budget separately, independent workspaces can facilitate financial settlement and cost tracking.

The instance administrator (instance\_admin) role of the service instance can create workspaces. The operation method is as follows:

Enter the "Management - Workspace" menu, click "New Space" on the workspace management page, fill in the required information, and create it.


^

Once the workspace name is created, it cannot be changed. The new workspace will create a schema named "public" by default, and three different types of computing clusters (general computing cluster, analytical computing cluster, and synchronization computing cluster) to facilitate quick operations in the workspace.

The user who creates the new workspace will be granted the workspace administrator (workspace\_admin) role by default.

When using multiple workspaces, you can switch between different workspace environments through the workspace button in the upper right corner of the "Development", "Computing", "Operations Monitoring" and other function pages.


^

A service instance user, if they need to use the data and computing resources in a workspace, needs to be added to the workspace and granted the corresponding permissions. This operation needs to be performed by a user with the workspace administrator (workspace\_admin) role. For more operation instructions, please refer to the relevant content in "Access Control" - "Configure Access Control" under [Workspace Level Management](access-control-configuration.md).
