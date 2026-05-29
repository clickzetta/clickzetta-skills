## Description

This statement is used to switch the schema in the current database, so that users can more easily operate and manage data tables under different schemas.

## Syntax
```SQL
USE [SCHEMA] schema_name;
```
## Parameter Description

1. `SCHEMA`: This is an optional keyword, you can use or omit it.
2. `schema_name`: Specifies the name of the schema to switch to.

## Usage Example

1. Switch to the schema named `ods_schema`:
   ```SQL
   USE ods_schema;
   ```
2. Switch to the schema named `reporting_schema`, omitting the `SCHEMA` keyword:
   ```SQL
   USE reporting_schema;
   ```
3. Switch to the schema named `customer_data` and perform some query operations after switching:
   ```SQL
   USE customer_data;
   SELECT * FROM customer_orders;
   SELECT COUNT(*) FROM customer_orders WHERE order_status = 'completed';
   ```
## Precautions

- When you use the `USE` statement in an SQL query to switch to a certain schema, the subsequent query operations will default to the data tables under that schema.
- If you need to frequently switch between multiple schemas, you can use the `USE` statement multiple times in the SQL query.
- When using the `USE` statement, please ensure that the specified schema name exists in the current database, otherwise it will cause an error.