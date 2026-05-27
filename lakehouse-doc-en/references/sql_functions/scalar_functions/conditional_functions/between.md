### BETWEEN 

####  Description
The BETWEEN operator is used to determine whether an expression (expr1) falls within the range of two other expressions (expr2 and expr3). If the value of expr1 is between expr2 and expr3 (inclusive of expr2 and expr3), it returns true; otherwise, it returns false.

#### Syntax
```sql
expr1 [NOT] BETWEEN expr2 AND expr3
```
#### Parameter Description
- `expr1`: The expression to be evaluated, which can be of type smallint, tinyint, int, bigint, float, double, decimal, date, string, char, or varchar.
- `expr2`: The starting value of the range, an expression to be compared with expr1.
- `expr3`: The ending value of the range, an expression to be compared with expr1.
- `NOT` (optional): Using the NOT keyword negates the result, i.e., returns true if expr1 is not between expr2 and expr3.

#### Return Result
Returns a boolean value indicating whether expr1 is between expr2 and expr3.

#### Usage Example
1. Determine if a number is within a specified range:
   ```sql
   > SELECT 5 BETWEEN 3 AND 7;
   true
   ```
In the above example, the number 5 is between 3 and 7, so it returns true.

2. Determine if a string is within a specified range:
   ```sql
   > SELECT 'C' BETWEEN 'A' AND 'E';
   true
   ```
In the above example, the string 'C' is between 'A' and 'E', so it returns true.

3. Determine if the date is within the specified range:
   ```sql
   > SELECT '2021-08-01' BETWEEN '2021-01-01' AND '2021-12-31';
   true
   ```
In the above example, the date '2021-08-01' is between '2021-01-01' and '2021-12-31', so it returns true.

4. Use the NOT keyword to determine whether expr1 is not between expr2 and expr3:
   ```sql
   > SELECT 0 NOT BETWEEN 1 AND 3;
   true
   ```
In the above example, the number 0 is not between 1 and 3, so using the NOT keyword returns true.

#### Notes
- When the types of expr2 and expr3 are inconsistent, the system will attempt implicit type conversion to meet the requirements of the operator.
- For string type parameters, comparisons will be sorted in lexicographical order.
- For date type parameters, comparisons will consider the chronological order of the dates.