### SQRT 
```
sqrt(expr)
```
####  Description
The SQRT function is used to calculate the square root of a specified numerical expression (expr). This function accepts a double type parameter and returns a double type result.

#### Parameter Description
* expr (double type): The numerical expression for which the square root needs to be calculated.

#### Return Result
Returns a double type value representing the square root of the parameter expr.

#### Usage Example
1. Calculate the square root of 0.16:
```sql
SELECT SQRT(0.16);
```
Results:
```
0.4
```
2. Calculate the square root of 25:
```sql
SELECT SQRT(25);
```
Results:
```
5.0
```
3. Calculate the square root of 9.8596 (rounded to two decimal places):
```sql
SELECT ROUND(SQRT(9.8596), 2);
```
Results:
```
3.14
```