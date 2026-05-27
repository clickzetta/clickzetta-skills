###  DIV

####  Description
The DIV operator is used to calculate the result of integer division between two numbers

#### Syntax
```
divisor div dividend
```
#### Parameter Description
- `divisor`: Dividend, must be an integer.
- `dividend`: Divisor, must be an integer.

#### Return Type
The return result is of type `bigint`.

#### Usage Example

1. Integer division:
```sql
SELECT 10 div 3; -- The result is 3
SELECT -10 div 3; -- The result is -3
```
#### Notes
- When the divisor is zero, it will cause the division operation to fail, resulting in NULL.