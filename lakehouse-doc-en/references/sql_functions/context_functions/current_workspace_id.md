# CURRENT_WORKSPACE_ID
```
current_workspace_id()
```
#### Function Description
The `current_workspace_id()` function is used to obtain the workspace ID of the current session. This function does not require any parameters and will return the unique identifier (integer value) of the workspace associated with the current session.

#### Usage Scenarios
In a multi-workspace environment, when specific operations need to be performed based on the workspace the current user is in, this function can be used to get the ID of the current workspace.

#### Return Result
The return value type is an integer (int), representing the workspace ID of the current session.

####  Example
The following example demonstrates how to use the `current_workspace_id()` function to get the current workspace ID and perform different operations based on different workspaces.

Example: Query the current workspace ID

```
SELECT current_workspace_id();
```
The execution result:
```
123
```