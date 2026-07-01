# Getting Started: How to Quickly Manage Users Under a Workspace

## Applicable Scenarios

If you already understand the concept of workspaces and need to collaborate with other users based on workspaces, please read this document. If you are working independently, you can skip this document and directly refer to the following guides to start using the product:

* [How to Quickly Run a SQL Query](quick_start_sql_query.md)
* [How to Quickly Upload and Import Data](quick_start_upload_data.md)

## Prerequisite Reading

Before reading this guide, it is recommended to first read and understand the following documents:

* [Lakehouse Product Introduction](datalake_overview.md)
* [Key Concepts](key-concepts.md)
* [Lakehouse Studio Quick Tour](lakehouse-studio-101.md)
* [Getting Started: Create and Use a Workspace](quick_start_create_workspace.md)

## Operation Guide

1. click the button to enter the Lakehouse service instance:



2. Navigate to "Management > Workspace" page



3. Click the workspace name to enter the details page. On this page, you can see the existing member users and defined roles under the workspace. The workspace creator is added as a member by default and granted the `workspace_admin` role.



4. Click "Add User" and select existing users to join the workspace. If the user has not been created yet, you can refer to this document to create a user first before adding: [Getting Started: How to Quickly Add and Manage Users](quick_start_user_management.md)

5. After selecting a user, to ensure the user has the necessary permissions to use features, it is recommended to use the "Add User and Grant Role" operation option.



6. Select the appropriate role based on the interface description. If you want the user to be able to develop and run tasks within the workspace, it is recommended to assign the `workspace_dev` role. Click "Grant Role" or the corresponding button to complete the entire add and authorization process.



7. On the workspace details page, you can view the user just added and the role granted.



## Limitations

* Permission Control: Only users with the workspace administrator role can perform operations of adding users and granting roles.

## Related Documents

* [Workspace](workspace-introduction.md)

* To learn more about roles and permissions, please read the following documents:

  * [Roles](roles.md)
  * [Built-in Role Permissions](permissions-of-built-in-workspace-level-roles.md)

## Next Steps

After completing the above operations, the user will have corresponding permissions within the workspace and can use relevant features. It is recommended to guide the user to read the following guides to get started:

* [How to Quickly Run a SQL Query](quick_start_sql_query.md)
* [How to Quickly Upload and Import Data](quick_start_upload_data.md)

^
