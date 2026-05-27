### ABS 
#### Description
The `ABS` function is used to calculate the absolute value of a given numerical expression. Whether the input value is positive or negative, the `ABS` function can return the corresponding non-negative value.

#### Syntax
```sql
ABS(expr)
```
#### Parameters
- `expr`: A numeric expression for which the absolute value needs to be calculated. It can be `smallint`, `tinyint`, `int`, `bigint`, `decimal`, `double`, or `float`.

#### Return Value
Returns the absolute value of the parameter `expr`. The return type is the same as the input parameter type.

#### Example Usage
1. Calculate the absolute value of a negative integer:
```sql
SELECT ABS(-10); -- Returns 10
```
2. Calculate the absolute value of a positive integer:
```sql
SELECT ABS(5); -- Returns 5
```
3. Calculate the absolute value of a decimal:
```sql
SELECT ABS(-3.14); -- The return result is 3.14
```
4. Calculate the absolute value of a negative number with a decimal point:
```sql
SELECT ABS(-0.5); -- Returns 0.5
```
5. Calculate the absolute value of a `decimal` type:
```sql
SELECT ABS(-123.456); -- Returns the result 123.456
```
6. Use the `ABS` function in a query to get the absolute value of employee salaries:
```sql
SELECT employee_name, ABS(salary - 100) AS adjusted_salary
FROM employees;
-- In the returned results, each employee's `adjusted_salary` will display as the absolute value of the difference between the salary and 100
```
#### Notes
- When `expr` is `NULL`, the `ABS` function will return `NULL`.
- The `ABS` function can be used in conjunction with other SQL functions, such as when sorting or filtering queries.