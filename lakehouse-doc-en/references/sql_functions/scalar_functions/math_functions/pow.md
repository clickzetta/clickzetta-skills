### POW

####  Description
The `POW` function is used to calculate a specified power of a number, that is, to solve for `expr1` raised to the power of `expr2`. This function has a wide range of applications in fields such as mathematics, science, and engineering calculations.

#### Syntax
```
POW(expr1, expr2)
```
#### Parameter Description
* `expr1`: Base, type is double precision floating point number (double).
* `expr2`: Exponent, type is double precision floating point number (double).

#### Return Result
The return value type is double precision floating point number (double), representing the result of `expr1` raised to the power of `expr2`.

#### Usage Example
1. Calculate 2 to the power of 3:
```sql
SELECT POW(2, 3); -- The result is 8.0
```
2. Calculate 5 to the power of 2:
```sql
SELECT POW(5, 2); -- The result is 25.0
```
3. Calculate 3 to the power of 0.5 (i.e., find the square root):
```sql
SELECT POW(3, 0.5); -- The result is 1.7320508075688772
```
4. Calculate 10 to the power of 5 divided by 2 to the power of 3:
```sql
SELECT POW(10, 5) / POW(2, 3); -- The result is 12500.0
```
#### Notes
* When `expr2` is negative, it represents the calculation of the negative exponent of `expr1`. For example, `POW(2, -3)` calculates 1/(2^3).
* When `expr2` is 0, for any non-zero `expr1`, the result is always 1. If `expr1` is 0, the result is undefined.
* When `expr1` is negative and `expr2` is non-integer, the result may be a complex number. In some database systems, this may cause an error or return a specific complex number representation. Please refer to the relevant documentation of the database system you are using to ensure correct handling.