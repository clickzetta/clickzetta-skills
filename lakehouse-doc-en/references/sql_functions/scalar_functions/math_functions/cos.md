### Cosine Function (COS)
```sql
COS(expr)
```
#### Function Description
The cosine function `COS` is used to calculate the cosine value of a given angle (parameter `expr`). This function is widely used in fields such as mathematics, physics, and engineering, especially when solving problems related to periodic changes.

#### Parameter Description
- `expr` (type double): The angle for which the cosine value needs to be calculated, in radians. If the input angle is in degrees, it needs to be converted to radians first. Degrees can be converted to radians by multiplying by π/180.

#### Return Result
Returns the cosine value of the parameter `expr`, with the result type being double.

#### Usage Example
1. Calculate the cosine value of 0 radians:
```sql
SELECT COS(0);
// Result: 1.0
```
2. Calculate the cosine of 90 degrees (π/2 radians):
```sql
SELECT COS(PI()/2);
// Result: 0
```
3. Calculate the cosine of 180 degrees (π radians):
```sql
SELECT COS(PI());
// Result: -1
```
4. Calculate the cosine value of 270 degrees (3π/2 radians):
```sql
SELECT COS(3*PI()/2);
// Result: 0
```
5. Calculate the cosine value of a negative angle (-π/4 radians):
```sql
SELECT COS(-PI()/4);
// Result: approximately 0.7071
```
Through the above example, you can understand how to use the cosine function `COS` to calculate the cosine values of different angles. In practical applications, you can calculate the cosine values of any angle as needed to solve various problems related to periodic changes.