### ROUND 

####  Description
The ROUND function is used to round numerical expressions to a specified number of decimal places. This function supports various input data types, including float, double, decimal, smallint, tinyint, int, and bigint.

#### Syntax Format
```sql
ROUND(expr [, d])
```
#### Parameter Description
- `expr`: The numeric type expression that needs to be rounded.
- `d`: An integer used to specify the number of decimal places to retain, supports negative values. The default value is 0.

#### Return Result
Returns the rounded numeric result, with the same type as the input `expr`.

#### Usage Example

1. Retain one decimal place:
```sql
SELECT ROUND(3.14, 1); -- Result: 3.1
```
2. Retain two decimal places:
```sql
SELECT ROUND(3.1415926, 2); -- Result: 3.14
```
 3. Retain the Integer Part: 
```sql
SELECT ROUND(2.5); -- Result: 3
```
4. Omit the decimal part:
```sql
SELECT ROUND(314.1592, -1); -- Result: 310
```
5. Rounding negative numbers:
```sql
SELECT ROUND(-3.14, 1); -- Result: -3.1
```
6. Round the decimal type:
```sql
SELECT ROUND(123.4567, 2); -- Result: 123.46
```