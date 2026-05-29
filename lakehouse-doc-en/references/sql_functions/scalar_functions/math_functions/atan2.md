### ATAN2 
```sql
ATAN2(y, x)
```
####  Description
The `ATAN2` function is used to calculate the arctangent value of two floating-point numbers `y` and `x`, with the return value in radians. Unlike the `ATAN` function, `ATAN2` can handle cases where `x` is zero or `y` and `x` have opposite signs, thus obtaining the correct quadrant result.

#### Parameter Description
* `y` (double type): The floating-point value of the y-axis coordinate.
* `x` (double type): The floating-point value of the x-axis coordinate.

#### Return Result
Returns the arctangent value of `y/x`, with the type being double.

#### Usage Example
```sql
-- Example 1
SELECT ATAN2(0, 0); -- The result is 0.0 because the intersection of the two axes is at the origin

-- Example 2
SELECT ATAN2(1, 1); -- The result is approximately 0.7853981633974483, which is 45°, indicating the angle in the first quadrant

-- Example 3
SELECT ATAN2(-1, 1); -- The result is approximately -0.7853981633974483, which is -45°, indicating the angle in the second quadrant

-- Example 4
SELECT ATAN2(1, -1); -- The result is approximately 2.356194490192345, which is 135°, indicating the angle in the second quadrant

-- Example 5
SELECT ATAN2(-1, -1); -- The result is approximately -2.356194490192345, which is 180°, indicating the angle in the third quadrant

-- Example 6
SELECT ATAN2(1, 0); -- The result is approximately 1.570796326794896

-- Example 7
SELECT ATAN2(0, 1); -- The result is approximately 0.0 because y/x is on the y-axis

-- Example 8
SELECT ATAN2(0, -1); -- The result is approximately 3.141592653589793
```