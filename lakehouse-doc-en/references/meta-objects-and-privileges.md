# Metadata Objects and Privileges

## Privilege Definitions

The granting of access control privileges determines the operations a user can perform on specific objects. Each metadata object in Singdata Lakehouse has a set of privileges that can be granted. For detailed information on all metadata objects and their privileges in Singdata Lakehouse, refer to the Privileges documentation.

Metadata objects can be expressed in three ways:

1. By object type and object name, representing an already created object. For example: table mytable (a table named mytable) or vcluster myvcluster (a compute cluster named myvcluster);

2. By using the keyword ALL plus the object category, representing all existing and future objects of that type. For example: ALL tables in schema my\_schema (all table-type objects in the schema named my\_schema);

3. By using the keyword ALL plus the keyword OBJECTS, representing all types of objects, both existing and future. For example: ALL OBJECTS in workspace my\_workspace (all objects in the workspace named my\_workspace).

Privileges can be expressed in two ways:

1. By specific privilege points, for example: select, read metadata, update, etc.;

2. By using the keyword ALL plus the keyword PRIVILEGES, representing all privilege points. For example: ALL PRIVILEGES on table mytable (all privilege points on the table mytable).

When managing privileges using SQL statements, use the GRANT  and REVOKE  commands. Adding with grant option at the end of the GRANT  statement indicates that the grantee is allowed to grant that privilege to other roles or users.

## Metadata Objects

The metadata objects in Lakehouse and their parent objects are shown in the table below:

| **Metadata Object** | **Parent Object** |
| ------------------- | ----------------- |
| workspace           | instance          |
| share               | instance          |
| network policy      | instance          |
| schema              | workspace         |
| virtual cluster     | workspace         |
| connection          | workspace         |
| table               | schema            |
| view                | schema            |
| materialized view   | schema            |
| dynamic table       | schema            |
| table stream        | schema            |
| volume              | schema            |
| index               | schema            |
| function            | schema            |
| job                 | schema            |

Metadata objects can be authorized through SQL. Objects within a workspace can be authorized via the web interface under "Management" - "Security" - "Privileges".

### ALL Objects

ALL objects are a special type of metadata object representing all current and future instances of a particular type. For example: all tables represent all current and future tables; all vclusters represent all current and future compute clusters.

When using ALL objects, they need to be used with the keyword "in" to specify the scope described by the ALL object. The keyword "in" is followed by the parent object of the ALL object. For example: all tables in schema my\_schema; all vclusters in workspace my\_workspace.

A special use of ALL objects is to refer to all sub-objects under a parent object. For example: all objects in schema my\_schema, representing all types of objects under my\_schema, including tables, views, functions, etc.

Note: Although ALL objects can improve the efficiency of authorization operations, use the all objects method with caution. Only use all objects when you are sure that the scope of all objects matches the authorization expectations to avoid exceeding the expected authorization scope.

## Business Objects

In addition to metadata objects, business objects are generated during data development and data governance processes, as shown in the table below:

| **Business Object** | **Business Category** |
| ------------------- | --------------------- |
| Script              | Data Development      |
| Task and Instance   | Monitor Rules         |
|                     | Announce Policy       |
| Data Quality        | DQC Rule              |

Business objects cannot be authorized through SQL. Users obtain relevant permissions by being granted preset roles that include business object permissions. Fine-grained authorization for business objects is not currently supported.

## Privileges on Objects

### Instance Privileges

| **Permission Point**  | **Purpose**           | **Description**                                                                                           |
| --------------------- | --------------------- | --------------------------------------------------------------------------------------------------------- |
| create workspace      | Create Workspace      | Default granted to instance administrator (instance\_admin role), not supported for other roles or users. |
| create network policy | Create Network Policy | Default granted to instance administrator (instance\_admin role), not supported for other roles or users. |
| drop workspace        | Drop Workspace        | Default granted to instance administrator (instance\_admin role), not supported for other roles or users. |

### Workspace Privileges

| **Permission Point** | **Purpose**                    | **Description**                                                                                                              |
| -------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| alter workspace      | Modify Workspace               | Default granted to the space administrator (workspace\_admin role) of the space, not supported for other roles or users.     |
| create connection    | Create Connection Object       |                                                                                                                              |
| create vcluster      | Create Virtual Cluster Object  |                                                                                                                              |
| create schema        | Create Schema Object           |                                                                                                                              |
| create user          | Add Instance User to Workspace | Default granted to the space administrator (workspace\_admin role) of the workspace, not supported for other roles or users. |
| create role          | Create Space-Level Role        | Default granted to the space administrator (workspace\_admin role) of the workspace, not supported for other roles or users. |

Authorization Example:

```SQL
grant alter workspace on workspace demo_workspace to user demo_user1;
grant create vcluster on workspace demo_workspace to user demo_user1;
grant create schema on workspace demo_workspace to user demo_user1;
grant create connection on workspace demo_workspace to user demo_user1;
```

### Schema Privileges

| **Permission**           | **Usage**                                                             | **Description** |
| ------------------------ | --------------------------------------------------------------------- | --------------- |
| alter schema             | Modify schema                                                         |                 |
| drop schema              | Delete schema                                                         |                 |
| read metadata            | Query schema metadata, used for desc schema and show schemas commands |                 |
| create table             | Create table                                                          |                 |
| create view              | Create view                                                           |                 |
| create materialized view | Create materialized view                                              |                 |
| create dynamic table     | Create dynamic table                                                  |                 |
| create index             | Create index                                                          |                 |
| create function          | Create function                                                       |                 |
| create table steam       | Create table stream                                                   |                 |
| all privileges           | Includes all permissions for schema objects                           |                 |

Authorization Example:

```SQL
grant alter schema on schema public to user demo_user1;
grant drop schema on schema public to user demo_user1;
grant read metadata on schema public to user demo_user1;
```

### Virtual Cluster Privileges

| **Permission** | **Usage**                                                                         | **Description** |
| -------------- | --------------------------------------------------------------------------------- | --------------- |
| alter vcluster | Modify virtual cluster properties or power state                                  |                 |
| drop vcluster  | Delete virtual cluster                                                            |                 |
| read metadata  | Query virtual cluster metadata, used for show vclusters or desc vcluster commands |                 |
| use vcluster   | Use virtual cluster                                                               |                 |
| all privileges | Includes all permissions for the vcluster object                                  |                 |

Authorization Example:

```SQL
grant alter vcluster on vcluster default to user demo_user1;
grant drop vcluster on vcluster default to user demo_user1;
grant read metadata on vcluster default to user demo_user1;
grant use vcluster on vcluster default to user demo_user1;
```

### Connection Privileges

| **Permission Point** | **Usage**                                          | **Description** |
| -------------------- | -------------------------------------------------- | --------------- |
| read metadata        | Used to query the metadata of the connection       |                 |
| alter connection     | Used to modify connection properties               |                 |
| drop connection      | Used to delete a specified connection              |                 |
| all privileges       | Includes all permissions for the connection object |                 |

### Table Privileges

| **Permission Point** | **Usage**                                                                             | **Description** |
| -------------------- | ------------------------------------------------------------------------------------- | --------------- |
| read metadata        | Query the metadata of the table. Used to execute show tables or desc table statements |                 |
| select               | Used to query data in the table                                                       |                 |
| alter table          | Used to modify the properties or definition of the table                              |                 |
| drop table           | Used to delete a specified table object                                               |                 |
| insert table         | Used to write data into the table                                                     |                 |
| delete table         | Used to delete data in the table                                                      |                 |
| restore table        | Used to restore data in the table to a specified version                              |                 |
| truncate table       | Used to empty the table                                                               |                 |
| update table         | Update data in the table                                                              |                 |
| all privileges       | Includes all permissions for the table object                                         |                 |

Description:

1. merge into table operation: requires insert, update, and delete privileges for the table;

2. insert overwrite operation: requires insert and delete privileges for the table;

3. copy into table operation: requires insert privileges for the table.

### View Privileges

| **Permission Point** | **Usage**                                                                           | **Description** |
| -------------------- | ----------------------------------------------------------------------------------- | --------------- |
| read metadata        | Query the metadata of the table. Used to execute show views or desc view statements |                 |
| select               | Used to query data in the view                                                      |                 |
| alter view           | Used to modify the properties or definition of the view                             |                 |
| drop view            | Used to delete a specified view object                                              |                 |
| all privileges       | Includes all privileges for the view object                                         |                 |

### Dynamic Table Privileges

| **Privilege**         | **Usage**                                                                                                     | **Description** |
| --------------------- | ------------------------------------------------------------------------------------------------------------- | --------------- |
| read metadata         | Query the metadata of the dynamic table. Used to execute show dynamic tables or desc dynamic table statements |                 |
| select                | Used to query data in the dynamic table                                                                       |                 |
| alter dynamic table   | Used to modify the attributes or definition of the dynamic table                                              |                 |
| drop dynamic table    | Used to delete the specified dynamic table                                                                    |                 |
| restore dynamic table | Used to restore the dynamic table to a specified version                                                      |                 |
| all privileges        | Includes all privileges of the dynamic table object                                                           |                 |

### Materialized View Privileges

| **Privilege**              | **Usage**                                                                                                                 | **Description** |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------- |
| read metadata              | Query the metadata of the materialized view. Used to execute show materialized views or desc materialized view statements |                 |
| select                     | Used to query data in the materialized view                                                                               |                 |
| alter materialized view    | Used to modify the attributes and definition of the materialized view                                                     |                 |
| delete materialized view   | Used to delete data in the materialized view                                                                              |                 |
| drop materialized view     | Used to delete the specified materialized view                                                                            |                 |
| update materialized view   | Used to refresh the materialized view object                                                                              |                 |
| truncate materialized view | Used to clear data in the specified materialized view                                                                     |                 |
| all privileges             | Includes all privileges of the materialized view                                                                          |                 |

### Function Privileges

| **Privilege**  | **Usage**                                                                                      | **Description** |
| -------------- | ---------------------------------------------------------------------------------------------- | --------------- |
| read metadata  | Query the metadata of the function. Used to execute show functions or desc function statements |                 |
| alter function | Used to modify the specified function                                                          |                 |
| use function   | Can use the specified function                                                                 |                 |
| drop function  | Used to delete the specified function                                                          |                 |
| all privileges | Includes all privileges of the function object                                                 |                 |

### Volume Privileges&#x20;

| **Privilege**  | **Usage**                                                                                                                                                                                        | **Description** |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| read metadata  | View the metadata of the Volume object.                                                                                                                                                          |                 |
| read volume    | Permission to read files and directories under the Volume object. Required when viewing the file list under the Volume, reading Volume files via SQL, and downloading files via the GET command. |                 |
| write volume   | Permission to write data to the Volume. Required when uploading files via the PUT command and deleting files via the REMOVE command.                                                             |                 |
| alter volume   | Permission required for the ALTER VOLUME command. For example: ALTER VOLUME  REFRESH to refresh the metadata information of the files under the Volume.                                          |                 |
| all privileges | Includes all privileges of the volume object                                                                                                                                                     |                 |

### Table Stream Privileges&#x20;

| **Privilege**      | **Usage**                                                      | **Description** |
| ------------------ | -------------------------------------------------------------- | --------------- |
| read metadata      | View the metadata of the table stream object                   |                 |
| alter table stream | Modify the attributes or definition of the table stream object |                 |
| select             | Query data in the table stream                                 |                 |
| drop table stream  | Delete the specified table stream object                       |                 |
| all privileges     | Includes all privileges of the table stream object             |                 |

### Index Privileges&#x20;

| **Privilege**  | **Usage**                                   | **Description** |
| -------------- | ------------------------------------------- | --------------- |
| read metadata  | View the metadata of the index object       |                 |
| drop index     | Used to delete the specified index          |                 |
| all privileges | Includes all privileges of the index object |                 |

### Job Privileges&#x20;

| **Privilege**  | **Usage**                                  | **Description**                                                                                                             |
| -------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| read metadata  | View job object metadata                   | Not available for authorization. Workspace admin role (workspace\_admin) and job executors have this permission by default. |
| terminate job  | Used to terminate a specified job          | Not available for authorization. Job executors have this permission by default.                                             |
| all privileges | Includes all permissions of the job object | Not available for authorization. Job executors have this permission by default.                                             |

### **All Privileges**

The "**All Privileges**" permission point exists on various metadata objects and represents all available permission points for a given object. However, "**All Privileges**" is an independent permission point and does not inherently grant or revoke other specific privileges.

Granting the "**All Privileges**" permission point allows the user to perform all operations on the object at that moment. However, revoking "**All Privileges**" does not remove any individual privileges that were separately granted.

#### **Example**

If the user `my_user` is granted both the `SELECT` privilege and "**All Privileges**" on `example_table`, they will be able to perform all operations on `example_table` due to the "**All Privileges**" assignment. When checking their permissions, the system will display both the `SELECT` privilege and "**All Privileges**" explicitly. If "**All Privileges**" is later revoked, `my_user` will still retain the `SELECT` privilege on `example_table`.

#### **Usage**

The "**All Privileges**" permission point provides a convenient way to grant all available permissions on an object. For example:

```
Grant all privileges on table example_table to user my_user;
```

^
