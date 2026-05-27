# Display External Functions

This command is used to list the external functions created by the current user. With this command, users can easily view and manage the external functions they have created.

Related functions: [Create Connection](CREATECONNECTION.md), [Create External Function](<CREATE_EXTERNAL_FUNCTION.md>), [Drop Function](drop-function.md)

## Syntax
```
SHOW EXTERNAL FUNCTIONS [ LIKE '<pattern>' ];
```
## Parameter Description

**LIKE '<pattern>'**: This parameter is used to filter command output based on function names. SQL wildcards `%` and `_` are supported.

## Usage Instructions

- Executing this command does not require starting the Virtual Coordinator (VC), so it will not consume CRU resources.
- The commands `SHOW FUNCTIONS` and `SHOW EXTERNAL FUNCTIONS` can both be used to display external function information.

## Examples

1. Display all external functions:
   ```
   SHOW EXTERNAL FUNCTIONS;
   ```
2. Display external functions according to regular expression rules, for example, functions with "hash" in their name:
   ```
   SHOW EXTERNAL FUNCTIONS LIKE 'hash%';
   ```
Through the above example, users can flexibly use the `LIKE` parameter to filter and view external functions. This helps users better manage and maintain external functions, ensuring the accuracy and availability of functions in the data warehouse.