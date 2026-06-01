# Functions

User-defined functions (Functions) extend the SQL computation capabilities of Lakehouse, allowing you to create reusable functions tailored to your business needs and call them in SQL queries just like built-in functions.

## Function Types

Lakehouse supports two types of user-defined functions:

### SQL Function

Functions defined using SQL expressions and executed inside the Lakehouse engine.

- **Scalar functions**: Process one or more columns from an input row and return a single result value per row.
- **Table functions**: Accept one or more input parameters and return a result set with multiple rows and columns.

SQL Functions are well-suited for simple computation logic such as formatting, conditional evaluation, and mathematical operations.

### External Function

Custom functions written in Python or Java and executed in a remote function compute service (Alibaba Cloud FC, Tencent Cloud SCF, AWS Lambda).

- **UDF** (User-Defined Function): Returns a single value per row.
- **UDAF** (User-Defined Aggregate Function): Aggregates multiple rows and returns a single value (Java only).
- **UDTF** (User-Defined Table Function): Returns a result set with multiple rows and columns (Java only).

External Functions are suited for calling external services (such as LLMs or image recognition APIs) or implementing complex business logic.

## Function Comparison

| Dimension | SQL Function | External Function |
|-----------|-------------|------------------|
| Development language | SQL | Python 3.10 / Java 8 |
| Execution location | Inside the Lakehouse engine | Remote function compute service |
| Use cases | Simple computation, formatting, conditional logic | Complex logic, AI model calls, unstructured data processing |
| Performance | High (local execution) | Subject to network latency |
| Dependency management | None | Dependencies must be packaged and uploaded |
| Supported types | Scalar function, table function | UDF, UDAF (Java), UDTF (Java) |

## Quick Start

### Create a SQL Scalar Function

```SQL
CREATE FUNCTION public.area(x DOUBLE, y DOUBLE)
RETURNS DOUBLE
RETURN x * y;

-- Use the function
SELECT public.area(3, 4);
-- Output: 12.0
```

### Create a SQL Table Function

```SQL
CREATE FUNCTION public.generate_series(start_val INT, end_val INT)
RETURNS TABLE(val INT)
AS SELECT generate_series(start_val, end_val);
```

### Create an External Function

```SQL
CREATE EXTERNAL FUNCTION public.upper_udf
AS 'com.example.GenericUdfUpper'
USING FILE 'volume://my_vol/upper.jar'
CONNECTION my_fc_connection
WITH PROPERTIES (
    'remote.udf.api' = 'java8.hive2.v0',
    'remote.udf.protocol' = 'http.arrow.v0'
);

-- Use the function
SELECT public.upper_udf('hello');
-- Output: HELLO
```

## Function Permissions

| Permission | Description |
|------------|-------------|
| `CREATE FUNCTION` | Create a function under a Schema |
| `ALTER FUNCTION` | Modify function properties |
| `USE FUNCTION` | Call the function in SQL |
| `DROP FUNCTION` | Delete the function |
| `READ METADATA` | View function metadata |

## Related Documentation

- [CREATE SQL FUNCTION](create-sql-function.md)
- [CREATE EXTERNAL FUNCTION](create_external_function.md)
- [External Function Usage Guide](remotefunction-best-practice.md)
- [External Function Development Guide (Python 3)](remotefunction-dev-guide-python3.md)
- [External Function Development Guide (Java)](external-function-dev-guide-java.md)
- [DROP FUNCTION](drop-function.md)
- [DESC FUNCTION](desc-function.md)
- [SHOW FUNCTIONS](show-functions.md)
- [SHOW EXTERNAL FUNCTIONS](show-external-functions.md)
