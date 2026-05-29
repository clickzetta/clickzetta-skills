# Permission Application

If you need to use data resources developed by others, you need to apply for permission to access those resources. This article introduces how to apply for resource permissions.

## Constraints and Limitations

* Currently, only single resource applications are supported, batch applications are not supported.
* In one application ticket, multiple resource applications (i.e., application object, authorization object, authorization time) can be created. During approval, only full approval or full rejection is supported, partial operations are not supported.

## Application Entry

* Entry Point One: In the "Data" function module, enter keywords or directly click search to enter the data search results page. In the result information flow, select the table you need to apply for, and click "Apply for Permission" on the far right.
* Entry Point Two: In the "Data" function module, click Data Management. On the Data Management page, click the target object, then click "Apply for Permission" in the upper right corner of the object details page.

## Application Operation Steps

According to the above application entry, select the target object, click "Permission Application", and a data object permission application pop-up window will appear.

\:-:
![](.topwrite/assets/image_1740571285907.png)

1. Application Information

* Object Permissions: The permission points that can be applied for on the current object. The types of permission options provided by different resource object levels are not exactly the same. The access permissions that the authorized party can obtain include three settings: all, read permissions, and write permissions.

  * All: Can perform all operations on the resource, such as Insert, Select, etc.
  * Read Permissions: Can only perform "read" operations on the resource, such as Select, Read, etc.
  * Write Permissions: Can only perform "write" operations on the resource, such as Alter, Drop, etc.

* Grant to User: Supports authorization in two ways, to roles and to users.

  * When selecting **Individual**, you can enter the tenant account keyword and then select other accounts from the dropdown for application, supporting multiple settings.
  * When selecting **User Group**, you can select roles created by default after instance creation or roles created by user customization from the dropdown (custom roles only support SQL creation, for details refer to [Create Role](CREATEROLE.md)).

* Authorization Time: The authorization time for the current resource object is permanently valid.

* Application Reason: Detailed explanation of the reason for applying for resource permissions.

2. You can click Add Application to add another similar resource application, where you need to re-fill object permissions, grant to user, authorization time, and application reason.

3. After applying for permissions, you can view all your application tickets under the Approval Center\_Application function, including application content, application status, etc., and you can also perform ticket cancellation or expedite operations.

^
