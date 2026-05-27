# DROP FUNCTION

**Function Description**

Delete the external function under the current or specified schema. It should be noted that once a function is deleted, it cannot be recovered and can only be recreated. Additionally, deleting a function does not clean up the function code and executable files stored in object storage.

**Syntax**
```
DROP FUNCTION [IF EXISTS] <function_name>;
```
**Parameter Description**

- `<function_name>`: The specified external function name.
- `IF EXISTS`: Optional parameter to check if the function exists. If it exists, the function is deleted; if it does not exist, no action is taken.
- `CASCADE`: Optional parameter to delete the function and all its dependent objects.
- `RESTRICT`: Optional parameter that, if set, only allows the function to be deleted if no other objects depend on it.

**Usage Instructions**

- When deleting a function, it is recommended to use the `IF EXISTS` parameter first to avoid errors caused by the function not existing.
- When deleting a function, ensure that no other objects depend on the function. If there are dependencies, you can use the `CASCADE` parameter to delete all dependent objects, or delete the dependent objects first, and then delete the function.
- After deleting the function, you need to recreate the function and reload the function code and executable files.

**Example**

1. Delete the external function named `ext_to_upper`.
   ```
   drop function if exists ext_to_upper;
   ```
```markdown
2. Delete the external function named `ext_to_upper` and all objects that depend on it.
```
   ```
   drop function ext_to_upper cascade;
   ```
3. Delete the external function named `ext_get_user_info` if it exists.
   ```
   drop function if exists ext_get_user_info;
   ```
```markdown
4. Delete the external function named `ext_get_user_info`, if this function exists and has other objects depending on it, also delete the dependent objects.
```
   ```
   drop function if exists ext_get_user_info cascade;
   ```
5. Delete the external function named `ext_sum_values` if it exists and has other objects dependent on it, but do not delete the dependent objects.

5. Delete the external function named `ext_sum_values`. If the function exists and has other objects depending on it, do not delete the dependent objects.
   ```
   drop function if exists ext_sum_values restrict;
   ```