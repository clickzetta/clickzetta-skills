### SINH

####  Description
The `sinh` function is used to calculate the hyperbolic sine of a given numeric expression. The hyperbolic sine function is a type of hyperbolic function in mathematics, defined as `sinh(x) = (e^x - e^(-x)) / 2`, where `e` is the base of the natural logarithm.

#### Syntax
```
sinh(expr)
```
#### Parameters
- `expr`: The numerical expression for which the hyperbolic sine needs to be calculated, of type `double`.

#### Return Value
Returns the calculated hyperbolic sine value, of type `double`.

#### Example 
1. Calculate `sinh(0)`:
```sql
SELECT sinh(0);
```
Results:
```
0.0
```
2. Calculate `sinh(1)` and `sinh(-1)`:
```sql
SELECT sinh(1) AS sinh1, sinh(-1) AS sinhNeg1;
```
Results:
```
sinh1: 1.1752011936438014
sinhNeg1: -1.1752011936438014
```
3. Calculate `sinh(2)` and `sinh(-2)`:
```sql
SELECT sinh(2) AS sinh2, sinh(-2) AS sinhNeg2;
```
Results:
```
sinh2: 3.62686176124242
sinhNeg2: -3.626860407847019
```

。