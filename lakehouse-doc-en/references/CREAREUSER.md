## Description

Add users to the workspace so that they can access and operate the resources within it.

## Syntax
```SQL
CREATE USER [IF NOT EXISTS] user_name
[DEFAULT_VCLUSTER= vc_name] 
[DEFAULT_SCHEMA=schema_name]
[COMMENT  "" ];
```
**1.user\_name**: User identifier, must be a username already created in the user management system.

**2.DEFAULT\_VCLUSTER**: Assign default computing resources to the user. If not specified, the global default computing resources will be used.

**3.DEFAULT\_SCHEMA**: Assign a default schema to the user. If the user does not specify a default schema, they need to specify the schema to access upon login, otherwise an error will occur. If a default schema is specified, the user will use this schema by default upon login. The `USE` command can be used to switch to other schemas during the session. Priority: `USE` command > default schema.

**4.COMMENT**: Add comment information for the user.

## Example

1. Add user uat\_test to the workspace, using global default computing resources and schema:
   ```SQL
   CREATE USER uat_test;
   ```

2. Add the user uat_test to the workspace and assign the computing resource vcluster1 and the default mode schema1:

   ```SQL
   CREATE USER uat_test DEFAULT_VCLUSTER=vcluster1 DEFAULT_SCHEMA=schema1;
   ```

3. Add user uat_test to the workspace and add comment information for it:

   ```SQL
   CREATE USER uat_test COMMENT "This is a test user for UAT environment.";
   ```
By the above example, you can add users to the workspace as needed and assign them appropriate resources and roles.