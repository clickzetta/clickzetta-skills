### EXP2 
```
exp2(expr)
```
####  Description
The EXP2 function is used to calculate the power of expr with base 2. This function accepts a parameter of type double and returns a result of type double.

#### Parameter Description
* expr (type double): The value for which the power needs to be calculated.

#### Return Result
Returns a value of type double, representing the power of expr with base 2.

#### Usage Example
Here are some examples of using the EXP2 function:

1. Calculate 2 to the power of 3:
```sql
SELECT exp2(3); -- Result: 8.0
```
2. Calculate -5 to the power of 2:
```sql
SELECT exp2(-5); -- Result: 0.03125
```
3. Calculate 2 to the power of 0:
```sql
SELECT exp2(0); -- Result: 1.0
```
4. Calculate the power of 2 for a series of values:
```sql
SELECT exp2(-2), exp2(1), exp2(5); -- Results: 0.25, 2.0, 32.0
```