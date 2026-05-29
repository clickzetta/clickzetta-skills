# Authorization

## 1. Access Control Model

All metadata objects in Singdata Lakehouse are authorized for access based on an access control system. The access control models supported by Singdata Lakehouse include **Access Control List** (ACL) and **Role-Based Access Control** (RBAC).

* **Access Control List** (**ACL, Access Control List**)

Permissions are directly granted to users.

* **Role-Based Access Control** (RBAC, Role-Based Access Control)

Permissions are granted to roles, and users gain corresponding permissions by being granted roles.

* **DAC (Discretionary Access Control) Mode Compatibility**

Singdata Lakehouse does not directly support DAC mode. DAC mode means that the owner of a metadata object (table, view, virtual cluster, etc.) has all permissions for that object by default and can grant permissions to other entities. In Singdata Lakehouse, after a metadata object is created, its creator has all permissions for that object by default but cannot re-authorize.

^

The main concepts in the Singdata Lakehouse access control system include:

* **Metadata Object (Object)**

A metadata object is an entity that can be granted access permissions. A metadata object contains multiple permission points, and related operations will be denied unless explicitly granted permission.

* **Role (Role)**

A role is an entity that can be granted permissions. Roles can be assigned to users but cannot be assigned to other roles.

* **Privilege (Privilege)**

A privilege is the smallest level of definition for accessing a metadata object. Multiple different permission points can be used to control the scope of granted operations.

* **User (User)**

A user is an identity recognized by Singdata Lakehouse, which can be a user identity or a service identity.

## 2. Roles

### 2.1 Role Types

There are two types of roles in Singdata Lakehouse: **predefined roles** and **custom roles**.

To facilitate users in quickly completing basic authorization and using product features, Singdata Lakehouse has predefined multiple roles. Predefined roles are automatically created with the service instance, cannot be modified or deleted, but can be granted to users.

Users can create custom roles as needed and authorize these roles. Custom roles can be modified or deleted at any time. Currently, custom roles can only be created within a workspace and do not support instance-level custom roles.

### 2.2 Role Levels

Metadata objects in Singdata Lakehouse are divided into two levels: "Instance" and "Workspace". Correspondingly, roles are also divided into "Instance Roles" and "Workspace Roles". There is no subordinate relationship between the two levels of objects. Instance-level roles do not have and cannot be granted any permissions for workspace-level metadata objects (workspace users, workspace roles, schema, table, compute cluster, etc.).

Workspace roles are isolated by workspace boundaries. Roles with the same name are allowed in different workspaces. Permissions cannot be granted across workspaces to roles in another workspace.

### 2.3 Predefined System Roles

The predefined roles and permissions in the current system are shown in the table below:

|          |          |                    |                                                                                          |                                                        |                                 |
| -------- | -------- | ------------------ | ---------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------- |
| **Role Level** | **Role Name** | **Role Code**           | **Permissions**                                                                                 | **Role Description**                                               | **Default Granted**                        |
| Instance Role     | Instance Administrator    | instance\_admin    | Workspace - Create Workspace - View Instance Role - Grant/Revoke                                                              | Manage the creation and deletion of all workspaces within the instance, and manage the granting and revoking of instance-level roles within the instance. The instance administrator does not have any permissions within any workspace. | The user who creates the service instance. Multiple users can be granted this role, at least one user must be granted this role.     |
|          | Instance User     | instance\_user     | Data Source - View Operations Center - View                                                                          | All users within the service instance are granted this role by default and it cannot be revoked.                                  | All users are granted this role by default and it cannot be revoked.                 |
|          | Datasource Administrator   | datasource\_admin  | Data Source - Manage                                                                                  | Has management permissions for data sources, can add, delete, and modify all data source objects.                                |                                 |
|          | Data Catalog Administrator  | datacatalog\_admin | Business Category - Manage Metadata Objects - View                                                                        | Has management permissions for functions and objects within the data catalog.                                     |                                 |
|          | Data Catalog User   | datacatalog\_user  | Business Category - View Metadata Objects - View                                                                        | Has read-only permissions for the data catalog.                                           |                                 |
|          | Instance SRE Administrator | instance\_sre      | Operations Center - View Tasks - Manage Task Instances - Manage Jobs - Manage                                                             | Has operational permissions for submitting, modifying, taking offline, and rerunning all task instances within the service instance.                      |                                 |
| Workspace Role     | Workspace Administrator    | workspace\_admin   | Workspace Members - Manage Workspace Roles - Manage Environment - Manage Task Directory - Manage Task Scripts - Manage Operations Center - Manage Task Instances - Publish Metadata Permissions - ALL Data Permissions - ALL Compute Resource Permissions - ALL | Has all permissions for all objects within the workspace and can reauthorize. Can manage members and roles within the workspace.                    | By default, granted to the user who creates the workspace. Multiple users can be granted this role, at least one user must be granted this role. |
|          | Workspace Member     | workspace\_user    | Workspace Members - View Workspace Roles - View Environment - View Task Directory - View Task Scripts - View Operations Center - View Task Instances - View Metadata - Read-Only                           | Has read-only permissions for tasks, environment, and all data objects within the workspace, and has read-only permissions for roles and members within the workspace.               | Not granted by default, needs to be actively granted.                   |
|          | Development | workspace\_dev     | Space Member——View Space Role——View Task Directory——Manage Task Scripts——Develop Jobs——Manage Metadata——ALL Data——ALL Task Development Scripts——Publish Compute Cluster——Use         | Has management permissions for task directories within the space, editing permissions for task scripts, and read and write permissions for all data objects within the space.              |                                 |

### 2.4 User-Defined Roles

Currently, it is only supported to create custom roles within the workspace using SQL syntax. The syntax for creating custom roles is:
```Plain
CREATE ROLE <role_name>;
```
Only users who are granted the workspace administrator role (workspace\_admin) can create custom roles within the workspace and manage and delete permissions for custom roles at any time.

## 3. Privileges

### 3.1 Privilege Definition

The granting of access control privileges determines the specific operations a user can perform on a particular object. For each metadata object in Singdata Lakehouse, there is a set of privileges that can be granted. For detailed information on all metadata objects and their privileges in Singdata Lakehouse, refer to the Privileges document.

Metadata objects can be expressed in three ways:

1) By object type and object name, representing an already created object. For example: table mytable (a table named mytable) or vcluster myvcluster (a compute cluster named myvcluster);

2) By the keyword ALL plus the object category, representing all existing and future objects of that type. For example: ALL tables in schema my\_schema (all table-type objects in the schema named my\_schema);

3) By the keyword ALL plus the keyword OBJECTS, representing all existing and future objects of all types. For example: ALL OBJECTS in workspace my\_workspace (all objects in the workspace named my\_workspace).

Privileges can be expressed in two ways:

1) By specific privilege points, for example: select, read metadata, update, etc.;

2) By the keyword ALL plus the keyword PRIVILEGES, representing all privilege points. For example: ALL PRIVILEGES on table mytable (all privilege points on the table mytable).

When managing privileges using SQL statements, use the GRANT <privilege> and REVOKE <privilege> commands. Adding with grant option at the end of the GRANT <privilege> statement indicates that the grantee is allowed to grant that privilege to other roles or users.

### 3.2 Metadata Objects

The metadata objects in Lakehouse and their parent objects are shown in the table below:

|                   |           |
| ----------------- | --------- |
| **Metadata Object** | **Parent Object** |
| workspace         | instance  |
| share             | instance  |
| network policy    | instance  |
| schema            | workspace |
| virtual cluster   | workspace |
| connection        | workspace |
| table             | schema    |
| view              | schema    |
| materialized view | schema    |
| dynamic table     | schema    |
| table stream      | schema    |
| volume            | schema    |
| index             | schema    |
| function          | schema    |
| job               | schema    |

Metadata objects can be authorized through SQL.

### 3.3 Business Objects

In addition to metadata objects, business objects are generated during data development and data governance processes, as shown in the table below:

|                    |                       |
| ------------------ | --------------------- |
| **Business Object** | **Business Category** |
| Script             | Data Development      |
| Task and Instance  | Monitoring Rules      |
|                    | Notification Policy   |
| Data Quality       | Quality Rules         |

Business objects cannot be authorized through SQL. Users obtain related permissions by being granted preset roles that include business object permissions. Fine-grained authorization is not supported at this time.

### 3.4 ALL Objects

ALL objects are a special type of object that represents **current** and **future** individuals of a category. For example: all tables represent all current and future tables; all vclusters represent all current and future compute clusters.
By using the `ALL` keyword, you can grant permissions to a collection of objects (such as all tables under a certain schema) at once, thereby reducing the tedious repetitive authorization operations. At the same time, the ALL keyword provides a "Future Grants" mechanism. For example: `all tables in schema s1` means all table-type objects currently and potentially added in the future within schema s1.

When using ALL objects, it needs to be used together with the keyword "in" to clarify the scope described by the ALL object. The keyword "in" is followed by the parent object of the ALL object. For example: all tables in schema my\_schema; all vclusters in workspace my\_workspace.

A special usage of ALL objects is to refer to all sub-objects under a certain parent object. For example: all objects in schema my\_schema, which means all types of objects under my\_schema, including tables, views, functions, etc.

Note: Although ALL objects can improve the efficiency of authorization operations, please use the all objects method for authorization with caution. Only use all objects to refer to when you are sure that the scope referred to by all objects meets the authorization expectations, to avoid the authorization scope exceeding expectations.

^
^

### 3.5 Permission Points

All operation types of metadata objects are as follows:

|                  |          |                                                  |
| ---------------- | -------- | ------------------------------------------------ |
| **Operation**    | **Type** | **Description**                                  |
| Alter            | DDL      | Modify object attributes                         |
| Create           | DDL      | Create object                                    |
| Desc             | DDL      | Display all attributes of a single object        |
| Drop             | DDL      | Delete an object                                 |
| Set              | DDL      | Set parameters                                   |
| Unset            | DDL      | Clear the setting of a parameter                 |
| Show             | DDL      | Display the list of the object                   |
| Truncate         | DDL      | Delete data in the table                         |
| Undrop           | DDL      | Restore a deleted object                         |
| Use              | DDL      | Use the object in a session context, such as use database, use vcluster |
| Cancel           | DDL      | Cancel the object (applied to job objects)       |
| Select           | DML      | Table data operation, query records              |
| Delete           | DML      | Table data operation, delete records             |
| Insert           | DML      | Table data operation, insert records             |
| Insert Overwrite | DML      | Table data operation, insert and overwrite records                                    |
| Merge            | DML      | Table data operation, merge records                                       |
| Update           | DML      | Table data operation, update records                                       |
| Replace          | DML      | Table data operation, replace records                                       |
| Copy Into        | DML      | Load data from file into table                                     |
| Get              | DML      | File operation, download file                                        |
| List             | DML      | File operation, get file list                                      |
| Put              | DML      | File operation, upload file                                        |
| Remove           | DML      | File operation, delete file                                        |
| Grant            | DCL      | Grant permissions                                             |
| Revoke           | DCL      | Revoke permissions                                             |

All operation types for business objects are as follows:

| **Object**                | **Included Operations**                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------- |
| Script                | View&#xA;Modify code&#xA;Schedule configuration [“Development” feature page]&#xA;Format&#xA;Save&#xA;Publish&#xA;Run&#xA;Rollback (version)                  |
| Task and Instance     | View&#xA;Schedule configuration [“Development” feature page]&#xA;Pause&#xA;Supplement data&#xA;Start&#xA;Offline&#xA;Rerun&#xA;Set success/Set failure&#xA;Recover             |
| Monitor Rules         | Create monitor rule&#xA;View monitor rule&#xA;View alert events&#xA;Subscribe/Unsubscribe&#xA;Edit rule&#xA;Enable rule&#xA;Disable rule&#xA;Suppress alert events&#xA;Close alert events |
| Announce Policy       | View notification history&#xA;View notification policy&#xA;Create notification policy&#xA;Edit notification policy&#xA;Delete notification policy&#xA;Copy notification policy&#xA;Create notification configuration&#xA;Modify notification configuration       |
| DQC Rule              | Create rule&#xA;View rule&#xA;View validation object&#xA;View validation results&#xA;Edit rule&#xA;Delete rule&#xA;Test run rule&#xA;Set validation result success/Set failure&#xA;Revalidate   |

Each operation corresponds to a unique permission point. When granted a certain permission point for an object, the corresponding operation can be performed on that object.

### 3.6 ALL Permission Points

ALL permission points are a permission point that exists on all types of metadata objects, representing all permission points for that object. The ALL permission point is an **independent** permission point and does not imply other permission points. Therefore, granting the ALL permission point does not cover other permission points, and revoking the ALL permission point does not revoke other permission points.
For example: The user my\_user is granted the select and ALL privilege points on example\_table successively. At this time, since the my\_user user is granted the ALL privilege point, they can perform all operations on example\_table; when querying the my\_user user's privileges on example\_table, it shows that they have both select and all privilege points. When the ALL privilege point is revoked from the my\_user user, the my\_user user still retains the select privilege on example\_table.

Using the ALL privilege point can quickly grant all privileges on an object, for example:
```SQL
Grant all privileges on table example_table to user my_user;
```
## 4. Grants

### 4.1 Grant Definition

The basic model of grants is to grant "**privilege points**" of an "**object**" to an "**identity**". The object can be a metadata object or a business object, the privilege point is one or more privilege points contained in this object, and the identity currently refers to two types: "user" and "role".

### 4.2 Grant Relationship Management

A user can obtain the privileges of an object in two ways: 1) directly granted the privileges of the object; 2) granted through a role that has the privileges of the object.

When a user is granted multiple roles at the same time, the user's privilege scope is the union of the privilege scopes of multiple roles.

Roles are not allowed to be granted to roles.

### 4.3 View Grants

Grants can be viewed from two perspectives: the granted identity and the granted object.

From the perspective of the granted identity, for example: show grants to user my\_user; will display all roles granted to the user, as well as privileges **directly** granted.

From the perspective of the granted object, for example: show grants on table my\_table; will display all privileges granted on the object, including those granted to users and roles.

### 4.4 Grant Operations

Grant operations for metadata objects can be performed using SQL operations, see the relevant introduction of the GRANT and REVOKE statements. They can also be performed on the web interface in the "Management" - "Security" - "Privileges" page.

Currently, granting business objects is only supported by granting predefined roles, and individual business object grants are not supported.