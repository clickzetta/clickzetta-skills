### SIGN 

####  Description
The `SIGN` function is used to determine the sign of a given numeric expression `expr`. Based on the value of `expr`, the function returns the following results:
- When `expr` is positive, it returns 1.0;
- When `expr` is negative, it returns -1.0;
- When `expr` is 0, it returns 0.

#### Syntax
```sql
SIGN(expr)
```
#### Parameters
- `expr`: The numerical expression to determine the sign, of type `DOUBLE`.

#### Return Value
Returns a result of type `DOUBLE`, which is 1.0, -1.0, or 0 depending on the sign of `expr`.

#### Example Usage
The following example demonstrates how to use the `SIGN` function to determine the sign of different numbers:
```sql
-- When expr is a positive number, returns 1.0
SELECT SIGN(10.5);
-- Result: 1.0

-- When expr is a negative number, returns -1.0
SELECT SIGN(-20.25);
-- Result: -1.0

-- When expr is 0, returns 0
SELECT SIGN(0);
-- Result: 0.0

-- Determine the sign of a numeric expression with decimals
SELECT SIGN(3.14159);
-- Result: 1.0

-- Determine the sign of a numeric expression converted from a string
SELECT SIGN(CAST('123.45' AS DOUBLE));
-- Result: 1.0

```
#### Notes
- When `expr` is `NULL`, the `SIGN` function will return `NULL`.