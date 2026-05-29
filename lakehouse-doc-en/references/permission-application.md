# Permission Application

If you need to use data resources developed by others, you must apply for permission to access those resources. This document describes how to apply for resource permissions.

## Limitations

* Currently, only permission applications for individual resources are supported; batch applications are not supported.
* A single application work order can contain multiple requested resources (i.e., application objects, grant targets, and grant durations). During approval, only full approval or full rejection is supported; partial operations are not allowed.

## Application Entry Points

* Entry point 1: In the **Data** functional section, enter keywords or click to search and go to the data search results page. In the results feed, select the table you want to apply for, and click **Apply for Permission** on the far right.
* Entry point 2: In the **Data** functional section, click **Data Management**. On the data management page, click the target object, then click **Apply for Permission** in the upper-right corner of the object details page.

## Application Steps

Follow the entry points above, select the target object, and click **Apply for Permission** to open the data object permission application dialog.

\:-:
![](.topwrite/assets/image_1734438890426.png =501)

1) Application Information

* Object Permission: The permission points available to apply for on the current object. Different resource object levels provide different permission type options. Available access permissions include three options: All, Read, and Write.

  * All: Allows all operations on the resource, such as Insert, Select, etc.
  * Read: Allows only "read" operations on the resource, such as Select, Read, etc.
  * Write: Allows only "write" operations on the resource, such as Alter, Drop, etc.

* Grant To: Supports granting to both roles and users.

  * When **Individual** is selected, you can enter account keywords and select other accounts from the dropdown list to apply for. Multiple selections are supported.
  * When **User Group** is selected, the dropdown shows default roles created after instance creation or custom roles created by users (custom roles can only be created via SQL; see [Create Role](create-role.md) for details).

* Grant Duration: The grant duration for the current resource is permanently valid.

* Application Reason: A detailed explanation of why you are applying for resource permissions.

2) You can click **Add Application** to add another resource request. In the additional resource request, you need to re-enter the object permission, grant target, grant duration, and application reason.

3) After applying for permissions, you can view all your submitted work orders under **Approval Center > Applications**, including application content, application status, etc. You can also withdraw or send reminder actions for a work order.

![](.topwrite/assets/image_1734438910731.png =344)
