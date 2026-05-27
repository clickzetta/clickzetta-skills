### PI 
#### Description
The `pi()` function is used to return the value of the constant π (pi). This function does not require any parameters.
#### Syntax
```
pi()
```
#### Return Type
This function returns a value of type double.
#### Usage Example
Query the value of pi:
```
SELECT pi();
```
Return Results:
```
3.141592653589793
```
Calculating the area of a circle with a known radius of 5:
```
SELECT pi() * 5 * 5;
```
Return Results: 
```
78.53981633974483
```
Calculating the volume of a sphere with a known radius of 3:
```
SELECT 4/3 * pi() * 3 * 3 * 3;
```
Return Results: 
```
113.09724459528809
```
#### Notes
- The `pi()` function returns an approximate value of π, and the specific precision depends on the database system used.
- In practical applications, retain an appropriate number of decimal places as needed.