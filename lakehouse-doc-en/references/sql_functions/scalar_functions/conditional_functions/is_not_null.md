### IS_NOT_NULL 
```sql
is_not_null(expr)
```
####  Description
The IS_NOT_NULL function is used to check whether a given expression (expr) is not null. If the expression is not null, the function returns true; otherwise, it returns false. This function works the same as the IS NOT NULL condition in SQL statements.

#### Parameter Description
- `expr`: An expression of any type, used to check whether its value is null.

#### Return Result
Returns a boolean value, true if expr is not null, otherwise false.

####  Example

1. Check if a number is not null
```sql
SELECT is_not_null(1);       -- Returns true
SELECT is_not_null(NULL);     -- Returns false
```
2. Check if the string is not null
```sql
SELECT is_not_null('hello');  -- Returns true
SELECT is_not_null('');       -- Returns false
```
3. Check if the date is not null
```sql
SELECT is_not_null('2022-01-01');  -- Returns true
SELECT is_not_null(NULL);          -- Returns false
```
4. Use IS_NOT_NULL in queries to filter non-null records
```sql
SELECT id, name, age
FROM users
WHERE is_not_null(age);            -- Only return records where the age field is not null
```