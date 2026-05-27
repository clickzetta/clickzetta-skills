### TANH 
```sql
TANH(expr)
```
####  Description
The TANH function is used to calculate the hyperbolic tangent of a given numerical expression `expr`, and returns the result as the hyperbolic tangent value.

#### Parameter Description
* `expr`: The numerical expression to be calculated, of type double.

#### Return Result
Returns the hyperbolic tangent value of the calculation result, of type double.

#### Usage Example
```sql
-- Calculate the hyperbolic tangent of 0
> SELECT TANH(0);
0.0

-- Calculate the hyperbolic tangent of 1
> SELECT TANH(1);
0.7615941559557649

-- Calculate the hyperbolic tangent of -1
> SELECT TANH(-1);
-0.7615941559557649

-- Calculate the hyperbolic tangent of a negative value -2
> SELECT TANH(-2);
0.9640275800758169 

-- Calculate the hyperbolic tangent of a large positive value 5
> SELECT TANH(5);
0.9999092042625951

-- Calculate the hyperbolic tangent of a small negative value -0.5
> SELECT TANH(-0.5);
-0.46211715726
