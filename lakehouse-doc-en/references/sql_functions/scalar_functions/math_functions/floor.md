### FLOOR 

####  Description
The FLOOR function is used to return the largest integer less than or equal to a given numeric expression (expr). Additionally, it can retain a specified number of decimal places (d) as needed. This function works correctly for various numeric input types, including float, double, decimal, tinyint, smallint, int, and bigint.

#### Parameter Description
- **expr**: The numeric expression to be processed, which can be of type float, double, decimal, tinyint, smallint, int, or bigint.
- **d** (optional): The parameter specifying the number of decimal places to retain, of type int. Negative values are supported, and the default value is 0.

#### Return Result
The return type is the same as the input expr type. If expr is of type decimal, the return result will be adjusted according to the specified scale value.

#### Usage Example
1. Calculate the largest integer result of -0.1:
```sql
SELECT FLOOR(-0.1); -- The result is -1
```
2. Calculate the maximum integer result of integer 5:
```sql
SELECT FLOOR(5); -- Result is 5
```
3. Calculate the maximum integer result of 5123.123 rounded to one decimal place:
```sql
SELECT FLOOR(5123.123, 1); -- The result is 5123.1
```
4. Calculate the maximum integer result of 5123.123 rounded to the nearest tenth:
```sql
SELECT FLOOR(5123.123, -1); -- The result is 5120
```
5. For decimal type, the result retains two decimal places:
```sql
SELECT FLOOR(123.456, 2); -- The result is 123.45
```
6. For the tinyint type, calculate the maximum integer result:
```sql
SELECT FLOOR(255); -- The result is 255
```
7. For bigint type, the result retains two decimal places:

```sql
SELECT FLOOR(1234567890123456789, 2); -- The result is 1234567890123456789
```