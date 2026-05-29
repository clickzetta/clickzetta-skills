# Access Control Overview

This document introduces the overall framework and key concepts of access control in Singdata Lakehouse. By understanding the core principles and related elements of access control, users and administrators can securely and flexibly allocate and manage permissions on the Singdata Lakehouse platform, ensuring compliant use of data and metadata objects.

## 1. Access Control Model

Singdata Lakehouse adopts a flexible access control mechanism, supporting two main models:

* **Access Control List (ACL**): Permissions are directly assigned to users. This method is more intuitive in small or simple scenarios; however, in large orgnizations, the management difficulty increases with the number of users and permission requirements.

:-: ![](.topwrite/assets/ACL.png =391)

* **Role-Based Access Control (RBAC**): Permissions are first assigned to roles, and then roles are granted to users, achieving indirect management of permissions. RBAC helps simplify permission maintenance in complex environments. When business needs change, permissions can be adjusted at the role level without maintaining each user individually.

:-: ![](<.topwrite/assets/Untitled Diagram.drawio.png> =591)

Unlike traditional DAC (Discretionary Access Control), Singdata Lakehouse does not directly support the DAC model of secondary authorization based on object ownership. It is recommended to use RBAC for centralized, controllable unified management of permissions.

In Singdata Lakehouse, RBAC and ACL authorization methods coexist. A user can be directly granted multiple permissions and multiple roles simultaneously. When the user performs any operation, their permission scope is the sum of the "directly granted permissions" and the "granted role" permissions. Users do not need to declare their current identity or role for operations; the authentication system will traverse all the permissions currently owned by the user and provide the authentication result.

## 2. Objects and Their Ownership

### Object

Metadata objects are entities that can be granted permissions, including workspace, schema, table, view, virtual cluster, etc. These objects are created with full permissions by the creator by default but cannot be secondarily authorized. When accessing objects, if not explicitly authorized, access is denied by default.

For all metadata objects in Singdata Lakehouse, see the authorization documentation.

### Object Ownership

The user who initially creates the object owns the object's ownership. The role owning the object can perform all operations on the object, including modification and deletion. Currently, transferring object ownership is not supported.

To achieve a more flexible permission allocation mechanism and more secure access control, it is recommended to manage object access through a unified authorization method using the role permission system, with instance\_admin and workspace\_admin roles.

## 3. Role Hierarchy and Types

### Role

Roles are carriers of permissions. After assigning permission points to a role, granting the role to a user can achieve indirect transmission of permissions. When a user has multiple roles, their permissions are the union of these role permissions.

### Role Hierarchy

Roles can be divided into two hierarchical scopes:

* **Instance Role**: Used for global control of instance-level resources and operations.
* **Workspace Role**: Applies to objects within a specific workspace (such as schema, table, virtual cluster, etc.). Workspace roles are bounded by the workspace and do not affect each other.

:-: ![](.topwrite/assets/role-levels.drawio.png =531)

This hierarchical structure helps achieve fine-grained access control at both global and local levels. When the business scale expands and permission requirements become complex, a clear role hierarchy between instance roles and workspace roles can simplify permission allocation.

### Predefined Roles and Custom Roles

Singdata Lakehouse provides several predefined roles (such as instance administrator, data source administrator, space administrator, etc.) to meet basic usage scenarios. Users can also create custom roles within the workspace (via SQL statements) to flexibly define and adjust permission sets that meet their business needs.

For all predefined roles and their default permissions in Singdata Lakehouse, see the authorization documentation.

## 4. Privilege and Authorization Management

### Privilege

Privileges define the smallest access units for operations on objects, including querying tables, inserting data, managing schemas, or using virtual clusters. Privilege points can finely define the read, write, modify, and delete operations that users can perform on objects.

^

For all metadata objects and their privilege points in Singdata Lakehouse, see the authorization documentation.

### Grant & Revoke

Use the `GRANT` and `REVOKE` commands to authorize or revoke permissions on metadata objects, with permission changes taking effect immediately. Corresponding visual operations can also be performed in the web interface.

Example:

`GRANT SELECT ON TABLE my_table TO ROLE analyst_role;`

`REVOKE INSERT ON TABLE my_table FROM ROLE analyst_role;`
Business objects (such as scripts, tasks, and data quality rules) do not currently support SQL fine-grained authorization. Their access permissions are granted through corresponding predefined roles.

## No Super-User Concept

There are no super-users or super-roles in Singdata Lakehouse that can bypass permission checks. All access operations must be explicitly authorized to ensure data access security and compliance.
