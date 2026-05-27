## Overview

The `SHOW SCHEMAS` statement displays a list of all schemas (SCHEMA) in the current workspace (WORKSPACE). Users can use flexible filter conditions to view relevant SCHEMAs based on specific patterns or criteria. Additionally, the `EXTENDED` keyword can be used to obtain more detailed information for each SCHEMA, such as its type (MANAGED or EXTERNAL).

## Syntax

```Plain
SHOW SCHEMAS [EXTENDED] [LIKE 'pattern' | WHERE expr];
```

## Parameters

* `LIKE pattern`: This parameter supports filtering output results by pattern matching. The matching is case-insensitive and supports SQL wildcards `%` (representing any number of characters) and `_` (representing any single character). For example, `LIKE '%report%'` filters for all SCHEMA names containing the string "report". Note that the `LIKE` clause and the `WHERE` clause are mutually exclusive and cannot be used together.
* `EXTENDED`: When this keyword is used, the command returns additional columns with extra information, such as the `type` column showing the SCHEMA type.
* `WHERE expr`: This parameter allows users to perform more detailed filtering based on the fields displayed by the `SHOW SCHEMAS` command to find SCHEMAs matching specific criteria.

## Examples

Here are some usage examples of the `SHOW SCHEMAS` command:

1. View all SCHEMAs in the current workspace:

   ```SQL
   SHOW SCHEMAS;
   ```

2. Get all MANAGED type SCHEMAs and their detailed information:

   ```SQL
   SHOW SCHEMAS EXTENDED WHERE type='managed';
   ```

3. To find a specific SCHEMA name, use the `WHERE` clause to filter by SCHEMA name:

   ```SQL
   SHOW SCHEMAS WHERE SCHEMA_NAME='your_schema_name';
   ```

## Required Privileges

To execute the `SHOW SCHEMAS` command, the user must have the READ METADATA privilege on the corresponding SCHEMA.
