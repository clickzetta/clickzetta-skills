### BROUND

####  Description
The Round Half to Even function (BROUND) is used to round a numeric expression `expr` to a specified number of decimal places `d` and return the processed numeric result. This function follows the round half to even rule and is applicable to various numeric types, including float, double, decimal, smallint, tinyint, int, and bigint.

#### Parameter Description
- `expr` (required): The numeric expression that needs to be processed using the round half to even rule.
- `d` (optional): The number of decimal places to retain, of int type, supports negative values, with a default value of 0.

#### Return Result
Returns the processed numeric result, with the same type as the input `expr`.

#### Usage Example
1. Retain one decimal place:
```sql
SELECT BROUND(3.14, 1); -- The result is 3.1
SELECT BROUND(3.15, 1); -- The result is 3.2
```
2. Keep two decimal places:
```sql
SELECT BROUND(3.164, 2); -- The result is 3.16
SELECT BROUND(3.264, 2); -- The result is 3.26
```
3. Retain negative decimal places (thousands):
```sql
SELECT BROUND(3141592, -3); -- Result is 3142000
```
4. Default number of decimal places retained (0 places):
```sql
SELECT BROUND(2.5); -- Result is 2
```
5. Handling decimal type:
```sql
SELECT BROUND(123.4567, 2) AS result; -- The result is 123.46
```
6. Handling Different Numeric Types:
```sql
SELECT BROUND(12345, -2) AS result; -- The result is 12300 
SELECT BROUND(123.456, -1) AS result; -- The result is 120 
```
### Summary
The round half to even function (BROUND) is a practical numerical processing function that can perform round half to even calculations on various types of numbers. By specifying the number of decimal places to retain, users can flexibly handle various numerical scenarios.