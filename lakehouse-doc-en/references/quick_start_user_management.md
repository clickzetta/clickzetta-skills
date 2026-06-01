# Quick Start: How to Add and Manage Users

## Use Cases

After completing product [registration and login](logging-in.md), you will receive an initial account with the highest global privileges, commonly referred to as the "account administrator" or "admin". You can use this account to access all product features. If you need to collaborate with colleagues and create individual accounts for different team members, please read this guide. Otherwise, you may skip this document and refer to the following guides to start using the product:

* [How to Quickly Run a SQL Query](quick_start_sql_query.md)
* [How to Quickly Upload and Import Data](quick_start_upload_data.md)

## Prerequisites

Before reading this guide, we recommend you review and understand the following documents:

* [Singdata Lakehouse Product Introduction](what_is_clickzetta_lakehouse.md)
* [Key Concepts](key_concepts.md)
* [Lakehouse Studio Quick Tour](lakehousestudiotour.md)

## Step-by-Step Guide

1. After logging in, you will be directed to the "Admin Center" account home page by default, as shown below:

   ![](.topwrite/assets/image_1747990064729.png)

2. In the Admin Center's left navigation bar, go to "Account Management > User Management" to access the user management page, as shown below:

   ![](.topwrite/assets/image_1747990075720.png)

3. Click the "Create" button in the upper-right corner and select "Create User" to begin creating a user account.

   ![](.topwrite/assets/image_1747990090897.png =297)

   > Note: "Custom Service User" is an identity created for automation tools, tasks, and applications. It cannot log in via the web UI. You can ignore this for now. For more details, see: [Service User Management](account_user_management.md)

4. Follow the on-screen instructions to fill in the required information. Please note the following:

   * Remember the password you set here, as you will need to provide the username and password to the user later.
   * The phone number must be the user's mobile number so that alerts and notifications can be delivered accurately.
     ![](.topwrite/assets/image_1747990274287.png)

5. After creating the new user account, provide the following two pieces of information to the user:

   * Username and password.
   * Account login URL in the format: `<account-name>.accounts.singdata.com`. You can also copy the browser URL shown in the screenshot below and send it to the user.

     ![](.topwrite/assets/image_1747990303813.png)

6. After the user logs in with the username and password, they can change the initial password by navigating to "Account Management > User Management" in the left sidebar, finding their account, and selecting "Change Password" from the actions menu.

   ![](.topwrite/assets/image_1747990312625.png)

## Limitations

* Permission Note: Only users with the account administrator (`account_admin`) role can create and manage users. This role is identified as follows:

  ![](.topwrite/assets/image_1747990332688.png =446)

## Related Documents

You can read the following documents for more details on managing accounts and users:

* [Manage Accounts](manageaccounts.md)
* [Manage Users](account_user_management.md)

## Next Steps

* After creating user accounts, you may need to add users to workspaces and assign permissions. See:
  * [How to Quickly Create and Use a Workspace](quick_start_create_workspace.md)
  * [How to Quickly Manage Workspace Users](quick_start_workspace_user.md)

* For the complete Lakehouse Studio user guide, see [Lakehouse Studio Complete User Guide](studio_manual.md)

^
