# Modify Share Object (SHARE)

##  Description

This statement is used to modify the share object (share). You can use this statement to add or remove target service instances (instance) for the share object.

## Syntax
```SQL
ALTER SHARE <share_name> [ADD | REMOVE] INSTANCE <instance_name>;
```
## Parameter Description

1. **share_name**: The name of the share object to be modified.
2. **ADD | REMOVE**: The operation on the share object, ADD means adding a target service instance to share, REMOVE means removing an already shared service instance.
3. **instance_name**: The name of the service instance, which must be globally unique. Service consumer users can find their service instance name on the right side of the homepage or in the URL of the service instance and provide it to the sharer for configuration.

## Usage Example

**Add a target service instance to share**

Suppose you have a share object named `SHARE_DEMO` and want to associate it with a service instance named `jymwxfyr`, you can use the following statement:

<Notes>
```SQL
ALTER SHARE SHARE_DEMO ADD INSTANCE jymwxfyr;
```
**Remove Shared Target Service Instance**

If you want to disassociate the shared object named `SHARE_DEMO` from the service instance named `jymwxfyr`, you can use the following statement:
```SQL
ALTER SHARE SHARE_DEMO REMOVE INSTANCE jymwxfyr;
```
## Precautions

- Ensure that you are logged into an account with the appropriate permissions when performing this operation.
- When adding or removing shared target service instances, make sure the instance names entered are correct.
- Operate with caution to avoid unnecessary trouble caused by mistakes.

By following the above steps, you can easily manage shared objects and their associated service instances.