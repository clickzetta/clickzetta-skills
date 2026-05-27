### DEGREES

###  Description
The `degrees` function is used to convert radian values to degree values. In the fields of mathematics and physics, angles are typically measured in either radians or degrees. Radians are a more universal measurement method, while degrees are more intuitive for people. By using the `degrees` function, users can easily convert between the two.

### Parameter Description
`expr` (double type): The radian value that needs to be converted.

### Return Result
Returns the converted double-precision floating-point number, which is the degree value.

### Usage Example
The following example demonstrates how to use the `degrees` function to convert different radian values to degree values.

**Example 1**: Convert π radians to degrees.
```sql
SELECT degrees(3.141592653589793);
```
Results:
```
180.0
```
**Example 2**: Convert 2π radians to degrees.
```sql
SELECT degrees(6.283185307179586);
```
Results:
```
360.0
```
**Example 3**: Convert -π radians to degrees.
```sql
SELECT degrees(-3.141592653589793);
```
Results:
```
-180.0
```