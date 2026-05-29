### CSC
```sql
csc(expr)
```
####  Description
The cosecant function `csc` is used to calculate the cosecant value of a given angle `expr`. The cosecant function is the reciprocal of the sine function, i.e., `csc(x) = 1/sin(x)`. This function is widely used in fields such as mathematics, physics, and engineering.

#### Parameter Description
* `expr` (type double): The angle value for which the cosecant value needs to be calculated, in radians.

#### Return Result
The return type is `double`, representing the calculated cosecant value.

#### Usage Example
1. Calculate the cosecant value for an angle of 1 radian:
```sql
SELECT csc(1);
```
Results:
```
1.1883951057781212
```
2. Calculate the cosecant value for an angle of π/2 radians (90°):
```sql
SELECT csc(PI()/2);
```
Results:
```
1.0
```
#### Notes
* When the `expr` parameter value is 0, the result of the cosecant function is infinity (`Infinity`).
* The cosecant function only accepts angle values in radians. To convert degrees to radians, use the `radians()` function.