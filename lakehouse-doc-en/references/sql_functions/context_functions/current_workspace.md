### CURRENT_WORKSPACE 

#### Description
The `CURRENT_WORKSPACE` function is used to obtain the name of the workspace to which the current database session is connected. This function does not require any parameters and returns a string representing the name of the workspace that the current session is operating on.

#### Usage Scenarios
In a multi-workspace environment, the `CURRENT_WORKSPACE` function can be used to quickly get the workspace of the current session, allowing for related operations such as permission management and data isolation.

#### Example
Here is an example of using the `CURRENT_WORKSPACE` function:

 Query the name of the workspace for the current session:
```sql
SELECT current_workspace();
```
The execution result:
```
"default"
```