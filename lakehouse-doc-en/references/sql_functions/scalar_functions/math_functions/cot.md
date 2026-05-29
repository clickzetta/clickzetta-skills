### COT
```
COT(expr)
```
####  Description
The COT function is used to calculate the cotangent value of a given angle, i.e., cotangent. Cotangent is the reciprocal of tangent, i.e., cot(x) = 1/tan(x). This function has a wide range of applications in trigonometric calculations.

#### Parameter Description
* expr (type double): The angle for which the cotangent value needs to be calculated, in radians.

#### Return Result
The return type is double, representing the cotangent value of the given angle.

#### Usage Example
1. Calculate the cotangent value of 1 radian:
```sql
SELECT COT(1);
```
Results:
```
0.6420926159343306
```
2. Calculate the cotangent value of π/4 (45°):
```sql
SELECT COT(PI()/4);
```
Results:
```
1.0000000000000002
```
3. Calculate the cotangent value of 0 radians:
```sql
SELECT COT(0);
```
Results:
```
Infinity
```
4. Calculate the cotangent value of -π/2 (-90°):
```sql
SELECT COT(-PI()/2);
```
Results:
```
-6.123233995736766E-17
```
#### Notes
* When the given angle is 0 or π (180°), the COT function will return infinity because the value of the tangent function is undefined at these angles.
* When the given angle is an integer multiple of π (180°), the COT function will return 0 because the value of the tangent function is 0 at these angles.