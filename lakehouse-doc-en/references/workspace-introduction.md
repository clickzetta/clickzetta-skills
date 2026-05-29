# WorkSpace Management Guide

WorkSpace is the basic unit in Singdata Lakehouse used to organize and isolate resource objects (such as data objects, computing resources, and users). It provides supporting data development capabilities, including data integration, data development, and data operations. By using WorkSpace, you can better manage and control resources and data in the Lakehouse.

## WorkSpace List

After logging into Singdata Lakehouse and entering the Lakehouse instance, you can view the WorkSpace list on the "Management" page in the left menu. Multiple WorkSpaces can be created under one service instance, and they are isolated from each other by default. Users need to join a WorkSpace to use the data and computing resources within it. Data objects (such as Schema, Table, and View) in different WorkSpaces can share data through cross-WorkSpace authorization.

![](.topwrite/assets/image_1739954449060.png)

## Create WorkSpace

:-: To create a new WorkSpace, click the "New" button on the right side of the WorkSpace list. The user who creates the WorkSpace will be granted the "workspace\_admin" role by default, with permissions to use and manage all resource objects under the WorkSpace and manage members within the space.
![](.topwrite/assets/image_1739954456362.png =724)

## Join WorkSpace

Only users who join a WorkSpace can be granted corresponding roles and permissions to use the computing and data resources within the WorkSpace. When a new user is created for an account, the user initially does not join any WorkSpace and therefore does not have access or usage permissions for any WorkSpace.

Users with the "workspace\_admin" role can add other users to the WorkSpace to further grant roles and permissions. The space administrator can click the WorkSpace name in "Management" - "WorkSpace" to enter the WorkSpace details page and perform "Add User" and "Remove User" operations on users in the WorkSpace.

:-: ![](.topwrite/assets/image_1739954463923.png =789)

Please note that when you add a user to a WorkSpace, the operated user only joins the specified WorkSpace but does not yet have any permissions. You need to grant WorkSpace roles or permissions to enable them to use the resources within the WorkSpace.

A user can join multiple WorkSpaces simultaneously. At least one user is required in a WorkSpace.

## WorkSpace Roles

To facilitate quick authorization, the system predefines the following space-level roles in each WorkSpace:

| Role Name         | Role Code          | Default Permissions                                                                                                                                             |
| ----------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Workspace admin   | workspace\_admin   | Manage space members, roles, development tasks, operations center, task instances, all permissions for data and computing clusters within the space.            |
| Workspace member  | workspace\_user    | View space members, roles, development tasks, operations center, task instances, etc., but cannot access data and computing clusters within the space.          |
| Workspace dev     | workspace\_dev     | Manage development tasks, operations center, task instances, etc., with all permissions for data within the space and usage permissions for computing clusters. |
| Workspace analyst | Workspace\_analyst | System preset role，with all vcluster usage privileges and can access to development function.                                                                   |
| Workspace sre     | Workspace\_sre     | System preset role, possessing management authority over all tasks and jobs within the workspace.                                                               |
|                   |                    |                                                                                                                                                                 |

The creator of the WorkSpace is granted the "workspace\_admin" role by default. Other users do not receive any roles by default when joining a WorkSpace. A user can be granted multiple roles simultaneously, and their actual permissions are the union of these roles' permissions. A role can be granted to multiple users simultaneously.

At least one user must be granted the "workspace\_admin" role. The permissions of instance-level roles do not overlap with the permissions of roles within the WorkSpace. All resources within the WorkSpace are managed by space-level roles. Users granted any instance-level roles do not directly have permissions to operate objects within the WorkSpace.
