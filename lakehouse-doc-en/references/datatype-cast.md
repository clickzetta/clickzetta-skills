# Data Type Conversion

In SQL statements, data type conversion is a common operation. This article will introduce how to perform data type conversion in SQL, as well as related functions and syntax.

## Data Type Conversion Functions

### CAST Function

The CAST function is used to convert a value of one data type to another data type. If the conversion exceeds the range of the target data type, an overflow exception will be raised.

#### Syntax
```
CAST(expression AS type)
```
Parameter Description:

- expression: Required. The data source to be converted.
- type: Required. The target data type. Usage is as follows:
  - `CAST(double AS bigint)`: Converts a DOUBLE data type value to a BIGINT data type.
  - `CAST(string AS bigint)`: Converts a string to a BIGINT data type. If the string contains a number expressed as an integer, it is directly converted to the BIGINT type. If the string contains a number expressed as a floating point or exponential form, it is first converted to the DOUBLE data type, and then to the BIGINT data type.
  - `CAST(string AS timestamp)` or `CAST(timestamp AS string)`: Uses the default date format `yyyy-MM-dd HH:mm:ss`.

#### Example
```
SELECT CAST(rand() AS INT);
+---------------------+
| CAST(rand() AS int) |
+---------------------+
| 0                   |
+---------------------+
```
### TRY_CAST Function

The TRY_CAST function is used to convert a value from one data type to another. If the conversion is successful, it returns the converted value; if the conversion fails, it returns NULL.

#### Syntax
```
TRY_CAST(expression AS type)
```
Parameter Description:

- expression: Required. The expression to be converted.
- type: Required. The target data type.

#### Example
```
SELECT TRY_CAST('123' AS INT);
+------------------------+
| TRY_CAST('123' AS int) |
+------------------------+
| 123                    |
+------------------------+
```
```
SELECT TRY_CAST('abc' AS INT);
+------------------------+
| TRY_CAST('abc' AS int) |
+------------------------+
| NULL                   |
+------------------------+
```
## Conversion Operators

In addition to using functions for data type conversion, you can also use conversion operators.

### Syntax
```
expression::type
```
- expression: Required. The expression to be converted.
- type: Required. The target data type.

### Example
```
SELECT 123.45::INT;
+------------------+
| 123.45::int       |
+------------------+
| 123              |
+------------------+
```
```
SELECT '2021-08-15'::DATE;
+------------------+
| '2021-08-15'::date |
+------------------+
| 2021-08-15       |
+------------------+
```