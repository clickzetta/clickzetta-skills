# Getting Started: How to Quickly Create and Use a Workspace

## Applicable Scenarios

A workspace is a logical object used to organize Lakehouse resource objects (data objects, computing resources, users, etc.) and provide supporting data development capabilities (data integration, data development, data operations). After completing registration and login, and activating the Lakehouse product, a workspace named `quick_start` is initialized by default under the service instance. This workspace comes with some sample data and sample code. If you plan to use product features based on this workspace, you can skip this document and refer to the following documentation to start using the product:

* [How to Quickly Run a SQL Query](quick_start_sql_query.md)
* [How to Quickly Upload and Import Data](quick_start_upload_data.md)

If you want to create more workspaces to meet the needs of different usage scenarios, such as organizing workspaces by business line or by data warehouse layering, please read this document.

## Prerequisite Reading

Before reading this guide, it is recommended to complete reading and understanding the following documents:

* [Lakehouse Product Introduction](what_is_clickzetta_lakehouse.md)
* [Key Concepts](key_concepts.md)
* [Lakehouse Studio Quick Tour](lakehousestudiotour.md)

## Operation Guide

1. Click the button as shown below to enter the Lakehouse service instance:

   ![](.topwrite/assets/image_1747991184372.png)

2. Navigate to Management > Workspace page:

   ![](.topwrite/assets/image_1747991196958.png)

3. Click the "New" button, fill in the information according to the interface prompts, and complete the creation:

   * Note that the workspace name must be unique within the service instance and has naming constraints. Please follow the guidance prompts on the page.
   * "Storage Encryption" refers to whether tables under the workspace are physically stored with encryption enabled. This is an advanced configuration feature, enable as needed.
     ![](.topwrite/assets/image_1747991206223.png)

4. After the workspace is created, you may potentially perform the following operations:

   * Use this workspace in product modules such as task development. The workspace switching entry is located at the top right corner of the page, as shown below:

     ![](.topwrite/assets/image_1747991250081.png)

   * Add other users to the workspace for collaboration. For details, see: [How to Quickly Manage Users Under a Workspace](quick_start_workspace_user.md)

## Limitations

* Permission Control: Only users with the `instance_admin` role can create and maintain users. The first `account administrator account` that registered and activated the product has the `instance_admin` role by default. You can use this account to perform workspace creation operations.

## Related Documents

* [Workspace Management](workspace-introduction.md)
* [Using Workspaces to Build a Data Development Environment](quick_start_workspace.md)
* [Quickly Set Up a Lakehouse Data Development Environment for Your Team](quickstart_envirment_for_team.md)

## Next Steps

* [How to Quickly Manage Users Under a Workspace](quick_start_workspace_user.md)

^
