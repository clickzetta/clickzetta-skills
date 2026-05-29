### CEIL
```
ceil(expr [, d])
```
####  Description
The CEIL function is used to return the result of rounding up the numeric parameter `expr` to the nearest decimal place at the `d`-th position after the decimal point. When `d` is negative, it means rounding to the left of the decimal point.
#### Parameter Description
- `expr`: The numeric parameter that needs to be rounded up. It can be of type float, double, tinyint, smallint, int, or bigint. The current version does not support the decimal type.
- `d`: Optional parameter that indicates the number of decimal places to retain. The default value is 0, which means no decimal places are retained. `d` can be a positive or negative number.
#### Return Result
Returns a value of the same type as `expr`.
#### Usage Example
```sql
-- Returns the result of rounding up -0.1
SELECT ceil(-0.1);
-- Result: 0

-- Returns the result of rounding up 5
SELECT ceil(5);
-- Result: 5

-- Returns the result of rounding up 5123.123 to one decimal place
SELECT ceil(5123.123, 1);
-- Result: 5123.2

-- Returns the result of rounding up 5123.123 to one place to the left of the decimal
SELECT ceil(5123.123, -1);
-- Result: 5130

-- Returns the result of rounding up 12345.6789 to two decimal places
SELECT ceil(12345.6789, 2);
-- Result: 12345.68

-- Returns the result of rounding up -123.456 to three decimal places
SELECT ceil(-123.456, 3);
-- Result: -123.456

-- Returns the result of rounding up 0 to two decimal places
SELECT ceil(0, 2);
-- Result: 0
```
#### Notes
- When `d` is a non-integer, it will automatically be rounded down to the nearest integer.
- When `d` is 0, the CEIL function will return the integer part, and the decimal part will be discarded.
- When `expr` is negative, the CEIL function will return a smaller negative result.