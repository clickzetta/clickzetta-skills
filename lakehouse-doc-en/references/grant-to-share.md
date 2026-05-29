# GRANT TO SHARE Statement

##  Description

The main function of the `GRANT TO SHARE` statement is to add specified tables or views to an existing share object and grant the corresponding permissions. By using this statement, users can easily share and manage data while ensuring data security and accessibility.

## Syntax Format
```SQL
GRANT select, read metadata ON {TABLE <table_name> | VIEW <view_name>} TO SHARE <share_name>;
```
**Parameter Description**

1. **share_name**: The name of the share object to be operated on.
2. **table_name**: The name of the table to be added to the share object.
3. **view_name**: The name of the view to be added to the share object.
4. **select, read metadata**: The permission points to be granted to the share object. The `select` permission allows query operations on the shared data; the `read metadata` permission makes the metadata of the tables and views added to the share object visible to the share recipient. When the `read metadata` permission is granted to a table or view, the `read metadata` permission of its schema will also be automatically granted to the share object to ensure the visibility of the table and view to the data recipient.

##  Example

**Example 1: Share a specified table**

Suppose we have a share object named `share_demo` and a table named `share_demo_table`. We want to add the `share_demo_table` table to the `share_demo` share object and grant `select` and `read metadata` permissions. This can be achieved using the following statement:
```SQL
GRANT select, read metadata ON TABLE share_demo_table TO SHARE share_demo;
```
**Example 2: Share a Specific View** 

In this example, we have a share object named `share_demo` and a view named `share_demo_view`. We want to add the `share_demo_view` view to the `share_demo` share object and grant the appropriate permissions. You can use the following statements:
```SQL
GRANT select, read metadata ON VIEW share_demo_view TO SHARE share_demo;
```
**Example 3: Sharing Multiple Tables and Views Simultaneously**

Sometimes, we may need to add multiple tables and views to a share object. The following example demonstrates how to add `share_demo_table1`, `share_demo_table2`, and `share_demo_view` to the `share_demo` share object simultaneously and grant the appropriate permissions:
```SQL
GRANT select, read metadata ON TABLE share_demo_table1, share_demo_table2 TO SHARE share_demo;
GRANT select, read metadata ON VIEW share_demo_view TO SHARE share_demo;
```
## Precautions

1. Before executing the `GRANT TO SHARE` statement, please ensure that the share object already exists.
2. Please ensure you have sufficient permissions to execute this statement in order to add tables or views to the share object.
3. When sharing tables or views, please consider the security and accessibility of the data to avoid unnecessary risks.