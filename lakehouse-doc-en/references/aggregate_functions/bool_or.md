### BOOL_OR Function
```sql
bool_or([distinct] expr)
```
#### Function Description
The BOOL_OR function is used to determine if there is a true value in a set of boolean values. When there is at least one true in the input dataset, the function returns true; if all values are false or null, it returns false. If the distinct parameter is not set, all boolean values are evaluated; after setting the distinct parameter, only the deduplicated dataset is evaluated.

#### Parameter Description
* expr (required): The boolean expression to be logically ORed.

#### Return Type
* The return value type is boolean.
* When all input data is null, it returns null.

#### Usage Example
1. Simple query without the distinct parameter:
```sql
SELECT bool_or(col) FROM VALUES (true), (true), (null) AS tab(col);
-- Return result: true
```
In this example, since there are two true values, the function returns true.

2. Query without the distinct parameter, all false:
```sql
SELECT bool_or(col) FROM VALUES (false), (false), (null) AS tab(col);
-- Return result: false
```
Due to all input values being false or null, the function returns false.

3. Query with distinct parameter:
```sql
SELECT bool_or(DISTINCT col) FROM VALUES (true), (true), (null) AS tab(col);
-- Return result: true
```
After setting the distinct parameter, even if there are two identical true values, the function will only treat them as one true value and return true.

4. Applied to actual data table queries:
```sql
SELECT bool_or(DISTINCT is_active) FROM users;
-- Assuming there are two active (is_active = true) users and one inactive (is_active = false) user in the users table, the return result should be true.
```
In this example, despite the presence of duplicate true values, the function counts only one true value due to the distinct parameter being set, and returns true.

#### Notes
* When all input data is null, the BOOL_OR function returns null.
* When using the BOOL_OR function, ensure that the input expression is of boolean type, otherwise unexpected results may occur.
* If you need to perform a distinct judgment on a specific column, use the DISTINCT keyword.