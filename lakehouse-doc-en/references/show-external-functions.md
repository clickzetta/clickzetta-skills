# Show External Functions

This command lists the external functions created by the current user. With this command, users can easily view and manage the external functions they have created.

Related commands: [Create Connection](CREATE-CONNECTION.md), [Create External Function](CREATE_EXTERNAL_FUNCTION.md), [Drop Function](drop-function.md)

## Syntax

```
SHOW EXTERNAL FUNCTIONS [ LIKE '<pattern>' ];
```

## Parameters

**LIKE '<pattern>'**: This parameter is used to filter the command output by function name. Supports SQL wildcards `%` and `_`.

## Usage Notes

- Executing this command does not require starting a VirtualCluster (VC), so it does not consume CRU resources.
- Both the `SHOW FUNCTIONS` and `SHOW EXTERNAL FUNCTIONS` commands can be used to display external function information.

## Examples

1. Show all external functions:

   ```
   SHOW EXTERNAL FUNCTIONS;
   ```

2. Show external functions matching a pattern, for example, show functions whose names contain "hash":

   ```
   SHOW EXTERNAL FUNCTIONS LIKE 'hash%';
   ```

With the above examples, users can flexibly use the `LIKE` parameter to filter and view external functions. This helps users better manage and maintain external functions, ensuring the accuracy and availability of functions in the data warehouse.
