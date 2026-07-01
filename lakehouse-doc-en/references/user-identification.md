# User Identity

Singdata employs a flexible user and identity management system, allowing differentiation and permission control for users at different levels and of different types.

This documentation covers the following topics in detail:

* User levels: including global account users and service instance users.
* User types: including normal users and service users.

***

## User Levels

Users in Singdata can be divided into two levels based on their scope: **global account users** and **Lakehouse service instance users**. These two levels help enterprises manage all users under an account globally across multi-cloud and multi-region service instances, while also differentiating permission scopes for different users based on the service instance.



^

### Global Users

Global users are users who perform global management and configuration on the Singdata platform. Each user has an independent identity in the system, with a unique username and password. Within an account, the username (user_name) must be unique to distinguish different user identities. Phone numbers, email addresses, and other information can be duplicated across different users.



^

### Service Instance Users

Service instance users are users within a specific service instance (instance) scope. A user can only be granted the various roles and permissions within a service instance if they belong to that instance. Global users are automatically synchronized to each service instance, becoming service instance users. Therefore, creation, deletion, and enable/disable status management of service instance users are all performed on the global "User Management" page. The "Users" list within a service instance only provides user information query functionality.

Service instance users are granted the "instance_user" role by default, which has no data or functional permissions. They need to be further granted permissions within the instance or workspace before they can perform operations.


***

## User Types

User types in the Lakehouse are mainly divided into **normal users** and **service users**:

A normal user typically represents an actual person within an enterprise, performing daily data querying, analysis, management, and other operations in the system.

A service user is a special type of user created to meet automation workflows or system-level operation requirements. Service users are **not allowed** to log in via the Web interface, but can use JDBC connections or be configured in scheduled tasks for automated or system-level calls to the Lakehouse.

In the Lakehouse, service users include **system service users** and **custom service users**:

Among them, **system service users** are default user identities created by the Lakehouse during account initialization, used to access resources within service instances to implement certain system functions.

**Custom service users** are identities that users can create on their own for their own business applications.

System service users in the Lakehouse are disabled by default. The system only prompts the user to "enable" them when the functionality being used involves a system service user, including:

sysservice_clickzetta -- Operates on temporary system resources and system data within the SYS workspace.

sysservice_auto_mv -- Enabled when auto_mv is activated, used for reading job_history and managing temporary MVs used by auto_mv.

^
