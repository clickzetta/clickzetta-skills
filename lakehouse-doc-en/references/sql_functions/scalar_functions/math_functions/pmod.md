### PMOD 
```
pmod(expr1, expr2)
```
####  Description
The PMOD function is used to calculate the modulus operation result between two numerical expressions and return the positive value of the result. Specifically, the function first calculates `expr1 % expr2`, then adds the result to `expr2`, and finally takes the modulus of `expr2` to ensure that the return value is always positive. This feature makes the PMOD function very useful when dealing with cyclic or periodic problems.

#### Parameter Description
* **expr1**: A numerical expression that can be of type float, double, decimal, tinyint, smallint, int, or bigint.
* **expr2**: A numerical expression of the same type as expr1.

#### Return Value
The return type is the same as the input parameters expr1 and expr2.

#### Usage Example
1. Calculate the modulus operation result between 2 and 1.8:
```sql
SELECT pmod(2, 1.8); -- The result is 0.2
```
2. Calculate the modulus of -10 and 3, and ensure the result is positive:
```sql
SELECT pmod(-10, 3); -- The result is 2
```
3. For mixed calculations of integers and decimals, the PMOD function is also applicable: {#pmod-mixed-calculations}

```sql
SELECT pmod(5.5, 3); -- The result is 2.5
```
4. When dealing with periodic issues, such as calculating the remaining time in a day, you can use the PMOD function:
```sql
SELECT pmod(12, 24); -- The result is 12, indicating that there are 12 hours remaining from 12:00
```