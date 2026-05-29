### IS_NULL 

####  Description
The IS_NULL function is used to determine whether a given expression (expr) is NULL. If the expression is NULL, it returns true; otherwise, it returns false. This function has the same effect as the IS NULL statement in SQL.

#### Syntax
```
is_null(expr)
```
#### Parameter Description
- `expr`: An expression of any type.

#### Return Result
Returns a boolean value, true if the expression is NULL, otherwise false.

#### Usage Example

1. Determine if a number is NULL:
   ```sql
   > SELECT is_null(NULL);
   true
   ```
2. Determine if a string is NULL:
   ```sql
   > SELECT is_null('');
   false
   ```
3. Using the IS_NULL function in queries:
   ```sql
   > SELECT name, age, is_null(address) AS is_address_null FROM users;
   ```
The above query will return the results of whether the name, age, and address in the user table are NULL.
