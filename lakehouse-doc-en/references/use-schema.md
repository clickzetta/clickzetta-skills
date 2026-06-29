
# USE Statement

Specifies the SCHEMA and compute resource for the current session.


## Syntax

```SQL
-- Switch schema
USE [SCHEMA] schema_name;
-- Switch compute resource
USE VCLUSTER vc_name;
```

## Parameters

1. `SCHEMA`: This is an optional keyword and can be omitted from the statement.
2. `schema_name`: Specifies the name of the schema to switch to.

## Examples

1. Switch to the schema named `ods_schema`:

   ```SQL
   USE ods_schema;
   -- Query the current SCHEMA
   SELECT CURRENT_SCHEMA();
   ```

2. Suppose the current workspace has a compute cluster named `sample_vc`. You can switch to this compute cluster using the following command:

   ```SQL
   USE VCLUSTER sample_vc;
   -- Query the current compute resource
   SELECT CURRENT_VCLUSTER();
   ```

3. To switch to a compute cluster named `high_performance_vc`, execute the following command:

   ```SQL
   USE VCLUSTER high_performance_vc;
   ```

## Usage Notes

- When connecting using client tools such as [SQLLine Client](<connect-with-cli.md>) or [DBeaver](<eco_integration/dbeaver-lakehouse.md>), the relevant operations take effect for the entire session duration.
- If you are using the Lakehouse Studio interface, it is recommended to switch schemas and compute clusters primarily through the page UI. If you use the command directly, its effect is only temporary, and you must select and execute it together with the SQL statements that depend on it for it to take effect.

> In the Studio UI, the schema and compute cluster selectors are located in the top toolbar of the SQL editor. You can switch them directly from the dropdown menus there without typing `USE` commands.
