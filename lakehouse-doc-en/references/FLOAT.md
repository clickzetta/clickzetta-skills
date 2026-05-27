# FLOAT
32-bit floating point type (FLOAT) is a numerical data type used to store real numbers, with limited precision and range. In databases, the FLOAT type is typically used to store numbers with fractional parts.

## Syntax
```
FLOAT
```
## Example
```
-- Use FLOAT type to store positive numbers
SELECT 1.5F;

-- Use FLOAT type to store negative numbers
SELECT -3.2F;

-- Convert other numeric types to FLOAT type
SELECT CAST(6.1 AS FLOAT);

-- Use FLOAT type in SELECT statement
SELECT FLOAT(salary) FROM employees;

-- Use FLOAT type in WHERE clause for conditional filtering
SELECT * FROM products WHERE price < 50.0F;
```
## Notes
1. FLOAT type values may have precision loss, so it is recommended to use DECIMAL or NUMERIC types in scenarios requiring high precision calculations.
2. When comparing FLOAT type values, be aware of their precision and rounding errors to avoid comparison errors due to precision issues.
3. When using FLOAT type, it is recommended to explicitly specify the precision and scale of the values to avoid unexpected results due to implicit type conversion.

## Summary
32-bit floating-point (FLOAT) is a numeric data type used to store real numbers, suitable for storing values with fractional parts. When using it, pay attention to precision loss, rounding errors, and type conversion issues to ensure data accuracy and reliability.