### LEAST 
```
least(expr1[, expr2, ...])
```
####  Description
The LEAST function is used to find and return the smallest value from a given list of parameters. If there are null values in the parameter list, those null values will be ignored.

#### Parameter Description
* expr: A comparable type expression, including but not limited to numeric types (float, double, decimal, tinyint, smallint, int, bigint), string types (char, varchar, string), and time types (date, timestamp), etc.

#### Return Result
The return type is the same as the input parameter expr type.

#### Usage Example
1. Comparison of numeric types:
```sql
SELECT least(10, 9, 1, 4, -1, null);
-- Return result: -1
```
2. Comparison of string types:
```sql
SELECT least('apple', 'banana', 'cherry', null);
-- Return result: 'apple'
```
3. Comparison of Time Types:
```sql
SELECT least('2023-01-01', '2022-12-31', null, '2024-01-01');
-- Return result: '2022-12-31'
```
4. Comparison of Mixed Types:
```sql
SELECT least(100, '10', 10.5, '1', null);
-- Return result: '1' (string type, but smaller value)
```
#### Notes
* When all parameters are null, the LEAST function will return null.
* The LEAST function is case-sensitive, so be aware of the impact of case when comparing strings.
* Comparing different types of data is not supported. It is recommended to ensure that all parameter types are consistent when using the LEAST function.