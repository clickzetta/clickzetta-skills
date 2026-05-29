# Modify Workspace Properties

In this section, we will introduce how to modify the properties of a workspace, including modifying the workspace's comments. This will help you better manage and organize your workspace.

## Modify Workspace Comments

To modify the comments of a workspace, you can use the following SQL statement:
```
ALTER WORKSPACE wbname SET COMMENT 'comment';
```
Here, `wbname` represents the name of the workspace you want to modify, and `comment` is the new comment you want to set.

## Modify Workspace PROPERTIES
```SQL
ALTER WORKSPACE wbname SET PROPERTIES ('key'='value')
```
To view WorkspacePROPERTIES, please use the following syntax:
```SQL
SHOW PROPERTIES IN WORKSPACE <workspace_name>
```
## Example
**Case: Modifying Workspace Comments**

Suppose you have a workspace named `ql_ws`, and you want to add a comment to it: "This is a workspace for querying." You can modify it using the following SQL statement:
```
ALTER WORKSPACE ql_ws SET COMMENT 'This is a workspace for querying.';
```
After executing this statement, you can use the `DESC` command to view the detailed information of the workspace and confirm that the comment has been successfully modified:
```
DESC WORKSPACE ql_ws;
```
The query results will display something similar to the following:
```
+--------------------+-----------------------------------------+
|     info_name      |               info_value                |
+--------------------+-----------------------------------------+
| name               |                ql_ws                    |
| creator            |               UAT_TEST                  |
| created_time       |          2023-04-18 17:11:01.314        |
| last_modified_time |          2024-01-08 11:33:56.772        |
| comment            | This is a working environment for queries. |
+--------------------+-----------------------------------------+
```