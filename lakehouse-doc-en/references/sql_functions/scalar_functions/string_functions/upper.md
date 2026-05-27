### UPPER 

#### Description
The UPPER function is used to convert all lowercase letters in the input string (str) to uppercase letters and return the converted string.

#### Syntax
```
UPPER(str)
```
#### Parameters
- str (string): The string that needs to be converted to uppercase.

#### Return Result
Returns a string where all lowercase letters have been converted to uppercase letters.

####  Example

1. Convert a simple string:
```sql
SELECT UPPER('hello world');
-- Output result: HELLO WORLD
```
2. Convert strings containing numbers and special characters:
```sql
SELECT UPPER('Hello123!@#');
-- Output result: HELLO123!@#
```
3. Convert a string that is already in uppercase: 
```sql
SELECT UPPER('HELLOWORLD');
-- Output result: HELLOWORLD
```
4. Use the UPPER function in queries to process column data:
```sql
SELECT UPPER(column_name) FROM table_name;
```
5. Use in combination with other string functions:
```sql
SELECT CONCAT(UPPER(first_name), UPPER(last_name)) AS full_name
FROM users;
-- Assuming the users table contains the first_name and last_name columns, this query will return a column named full_name, which contains the result of converting the user's first name and last name to uppercase.
```
#### Notes
- The UPPER function only applies to English letters contained in the input string. For other languages or special characters, the conversion effect may not meet expectations.
- When using the UPPER function, please ensure that the input string is in the correct format. If the input string is not valid text, the function may not work properly.