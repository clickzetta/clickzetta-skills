### EXP 
```
EXP(expr)
```
####  Description
The EXP function is used to calculate the `e` power of the expression `expr`, which is the natural exponential function. `e` is a mathematical constant, approximately equal to 2.71828.

#### Parameter Description
- `expr`: The value for which the exponent needs to be calculated, of type double precision floating point (double).

#### Return Result
The return type is double precision floating point (double), representing the calculation result.

####  Example
1. Calculate the 1st power of `e`:
```sql
SELECT EXP(1.0); -- Result is approximately: 2.718281828459045
```
2. Calculate `e` to the power of 2:
```sql
SELECT EXP(2.0); -- Result is approximately: 7.38905609893033
```
3. Simulate continuous compound interest calculation, assuming the principal is 1000 yuan, the annual interest rate is 5%, and the deposit is for 3 years:
```sql
SELECT 1000 * EXP(0.05 * 3); -- Result is approximately: 1161.834242728283
```
#### Notes
- When `expr` is negative, the EXP function returns a positive number less than 1.
- When `expr` is 0, the EXP function returns 1.
- When `expr` is positive infinity, the EXP function returns positive infinity.
- When `expr` is negative infinity, the EXP function returns 0.