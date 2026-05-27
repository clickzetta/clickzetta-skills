### HYPOT 

#### Description
The HYPOT function is used to calculate the square root of the sum of the squares of two numbers, which is the length of the hypotenuse of a right triangle. This function is very useful in solving geometric problems, especially when dealing with right triangles.

#### Syntax
```
HYPOT(expr1, expr2)
```
#### Parameters
- `expr1`: A double type numerical expression.
- `expr2`: A double type numerical expression.

#### Return Result
Returns a double type numerical value, representing the square root of the sum of the squares of the two parameters.

#### Usage Example

1. Calculate the length of the hypotenuse of a right triangle:
   ```sql
   > SELECT HYPOT(3, 4);
   5
   ```
In this example, we calculate the length of the hypotenuse of a right triangle, where the lengths of the two legs are 3 and 4 respectively. The HYPOT function returns the square root of the hypotenuse length, which is 5.

2. Calculate the distance from a point to the origin:
   ```sql
   > SELECT HYPOT(x, y) FROM points WHERE x = 3 AND y = 4;
   5
   ```
In this example, we query the distance from a point (3, 4) to the origin (0, 0) from a table containing point coordinates (points). The HYPOT function calculates the distance between the two points, returning a result of 5.

#### Notes
- Ensure that the parameters passed to the HYPOT function are of numeric type, otherwise, it may cause the function to return an error.
- When both parameters are 0, the HYPOT function will return 0, as the square root of the sum of the squares of 0 is still 0.