# RLIKE

##  Description:
The `RLIKE` function is used to check if a string matches a specified regular expression pattern. It can be used both as an operator and as a function call, providing flexible string matching capabilities.

## Syntax:
- Used as an operator:
  ```sql
  str [NOT] RLIKE regex
  ```
- As a function:
  ```sql
  RLIKE(str, regex)
  ```
## Parameters:
- `str`: The string to be checked.
- `regex`: The regular expression used for matching.

## Return Values:
- Returns a boolean value. If the string matches the regular expression pattern, it returns `TRUE`; otherwise, it returns `FALSE`.
- If `[NOT] RLIKE` is used as the operator, the return value is the opposite, i.e., it returns `TRUE` when the pattern does not match.

##  Example

Below is an example of using the RLIKE function:

1. Match the beginning of a string:
```sql
select rlike('aabb', r'^a');
-- The result is true because the beginning of the string 'aabb' is 'a'
```
2. Matching the beginning and end of a string:
```sql
select rlike('aabb', r'^a.*b$');
-- The result is true because the string 'aabb' starts with 'a' and ends with 'b'
```

3. Use wildcards to match any character:

```sql
select rlike('footerbar', r'foo(.*?)(bar)');
-- The result is true because '.*?' in the regular expression can match any character of any length
```
4. Match Email Addresses:
```sql
   select rlike('user@example.com', r'^[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$');
   -- The result is true because this regular expression can match most valid email addresses
   ```

5. Match phone numbers:

```sql
select rlike('123-4567-8900', r'\d{3}-\d{4}-\d{4}');
-- The result is true because the regular expression can match a specific format of phone numbers
```
6. Usage of rlike
```sql
-- Use as a function
SELECT RLIKE('hello world', 'hello.*world') AS result;
-- Returns TRUE

-- Use as an operator
SELECT 'hello world' RLIKE r'hello.*world' AS result;
-- Returns TRUE

-- Use the NOT operator
SELECT 'hello world' NOT RLIKE r'hello.*world' AS result;
-- Returns FALSE
```