# Lakehouse SQL: CREATE SQL FUNCTION

## Overview

The `CREATE FUNCTION` statement is used to create SQL scalar functions or table functions in Lakehouse. These functions can accept a set of parameters and return a scalar value or a set of rows. This article will provide a detailed explanation of its syntax, parameters, and usage examples.

## Syntax

```sql
CREATE [OR REPLACE] FUNCTION [IF NOT EXISTS]
    function_name ( [ function_parameter [, ...] ] )
     [ RETURNS data_type | RETURNS TABLE(column_spec)]
   AS|RETURN { expression | query };

function_parameter
    parameter_name data_type;

column_spec
    column_name data_type;
```

## Parameter Description

- `OR REPLACE`
  - If specified, it will replace an existing function with the same name and signature (number and type of parameters).
  - Cannot be used with `IF NOT EXISTS`.
- `IF NOT EXISTS`: If specified, the function will only be created if it does not already exist.
- `function_name`: The name of the function, which can be schema-qualified.
- `function_parameter`
  - `parameter_name`: The parameter name must be unique within the function.
  - `data_type`: Any supported data type.
- `RETURNS data_type`
  - The return data type for scalar functions. If not provided, it will be derived from the function body.
- `AS|RETURN {expression | query}`
  - The body of the function. For scalar functions, it can be an expression or a query; for table functions, it must be a query.
* `RETURNS TABLE`：Defines the returned table structure, requiring column names and data types to be specified.
## Examples

### Creating and Using SQL Scalar Functions

```sql
-- Create a function with a specified return type
CREATE FUNCTION public.area(x DOUBLE, y DOUBLE) 
RETURNS DOUBLE
RETURN x * y;

-- Use the function in a query
SELECT public.area(3, 4);
-- Output: 12.0

-- Create a function using AS to specify the logic
CREATE FUNCTION public.area2(x DOUBLE, y DOUBLE)
RETURNS double
AS x * y;

SELECT public.area2(3, 4);
```

### Specifying Return Type

```sql
CREATE FUNCTION public.hello()
RETURNS STRING
AS 'Hello World!';
SELECT public.hello();
```

### Using Built-in Functions in Expressions

```sql
CREATE FUNCTION public.roll_dice(num_dice INT, num_sides INT)
RETURNS INT
COMMENT 'Roll a number of n-sided dice'
RETURN (rand() * num_sides)::INT + 1;

SELECT public.roll_dice(3, 10);
```

### Returns a table - valued type:

```
CREATE TABLE employee (
    id INT,
    name STRING,
    deptno INT
);
INSERT INTO employee (id, name, deptno)
VALUES
    (1, 'Alice', 10),
    (2, 'Bob', 10),
    (3, 'Charlie', 20),
    (4, 'David', 10),
    (5, 'Eve', 20);
CREATE OR REPLACE FUNCTION ga1_1.getemps(deptno INT)
    RETURNS TABLE (name STRING)
    RETURN SELECT name FROM employee e WHERE e.deptno = deptno;
SELECT * FROM ga1_1.getemps(10);
```

## Notes

- When using a function, you must specify the schema where the function was created; otherwise, it will result in a "function not found" error. You can avoid this error by setting the parameter `cz.sql.remote.udf.lookup.policy`. This parameter dynamically switches the resolution priority between UDFs and built-in functions. The default behavior requires specifying the schema prefix when using a UDF. Example:
    ```sql
    -- Create a function
    CREATE FUNCTION public.lower()
    RETURNS STRING
    AS 'Hello World!';

    -- Use the function; the schema must be specified, otherwise it will result in a "function not found" error
    SELECT public.lower();

    -- Policy 1: Prioritize built-in functions; the schema prefix is not required. If the name conflicts with a built-in function, the built-in function will be used.
    SET cz.sql.remote.udf.lookup.policy = builtin_first;
    SELECT lower();

    -- Policy 2: Prioritize UDFs (suitable for MC/Spark job scenarios). If the name conflicts with a built-in function, the UDF will be used.
    SET cz.sql.remote.udf.lookup.policy = udf_first;
    SELECT lower();
    ```