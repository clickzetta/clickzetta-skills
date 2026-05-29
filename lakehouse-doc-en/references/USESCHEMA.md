###  Description

The `USE SCHEMA` statement is designed to change the default SCHEMA setting for the current session. After you perform this operation, all SQL queries and commands that do not explicitly specify a SCHEMA will be executed within the newly set SCHEMA. This helps to simplify the writing of SQL statements and improve work efficiency.

### Syntax
```SQL
USE [SCHEMA] schema_name;
```
### Parameter Description

- `schema_name`: The name of the target SCHEMA you wish to switch to.

###  Example

1. Switch to the SCHEMA named `reporting`:
   ```SQL
   USE reporting;
   ```

2. When performing a series of operations on the `sales` data table, first switch to the corresponding SCHEMA:

   ```SQL
   USE sales_schema;
   SELECT * FROM sales_data;
   UPDATE sales_data SET quantity = 100 WHERE product_id = 12;
   ```
3. When frequent switching between different SCHEMAs is needed, you can quickly locate a specific data set using the `USE` statement:
```SQL
-- Switch from the current sales_schema to customer_schema
USE customer_schema;
-- Query customer information
SELECT * FROM customers;
-- Switch back to sales_schema
USE sales_schema;
```

4. If you want to specify a SCHEMA when creating a table but do not want to switch to that SCHEMA immediately, you can include the SCHEMA name in the CREATE TABLE statement without using the `USE` statement:
   ```SQL
   CREATE TABLE finance_schema.ledger (
     id INT PRIMARY KEY,
     amount DECIMAL(10, 2) NOT NULL
   );
   ```
### Notes

- When using the `USE SCHEMA` statement, ensure that the specified SCHEMA exists, otherwise it will cause an error.
- Switching SCHEMA only affects the current session and does not affect the default SCHEMA settings of other sessions or users.
- When executing cross-SCHEMA queries, you need to explicitly specify the relevant SCHEMA name, otherwise the default SCHEMA of the current session will be used.
- In some database management systems, the `USE` statement can also be used to specify a database. The specific behavior may vary depending on the system, so please operate according to the actual situation.
### Notes
- When connecting using client tools (such as [Client SQLLine](<connect-with-cli.md>), [DBeaver](<eco_integration/dbeaver-lakehouse.md>), etc.), the relevant operations will take effect for the entire session. If you are using the Lakehouse Studio interface, it is recommended to switch Schemas and compute clusters via the page. It should be noted that if you directly use the relevant commands, their effects will only be temporary and will only take effect if selected together with the SQL to be executed.  
![](.topwrite/assets/image_1741319941746.png)