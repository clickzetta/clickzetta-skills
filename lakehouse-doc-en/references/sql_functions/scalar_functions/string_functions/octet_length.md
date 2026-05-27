### Function Name
OCTET_LENGTH

### Description
The OCTET_LENGTH function is used to calculate the byte length of a string or binary data. This function is very useful when handling text data, especially when it is necessary to determine the size of the data or perform character encoding conversions.

### Syntax
```
OCTET_LENGTH(expr)
```
Where `expr` is an expression of string or binary data type.

### Parameters
- `expr`: The string or binary data whose byte length needs to be calculated.

### Return Result
Returns an integer representing the byte length of the input data.

### Usage Example
1. Calculate the byte length of an English string:
```sql
SELECT OCTET_LENGTH('HelloWorld'); -- Result is 10
```
In the above example, the string "HelloWorld" contains 10 characters, so the returned byte length is 10.

2. Calculate the byte length of a Unicode string:
```sql
SELECT OCTET_LENGTH('hello'); -- Result is 5
```
The string "hello" contains 5 ASCII characters, each taking 1 byte, so the returned byte length is 5.

3. Calculate the byte length of binary data:
```sql
SELECT OCTET_LENGTH(X'48656C6C6F20576F726C64'); -- Result is 20
```
In the above example, the binary data "48656C6C6F20576F726C64" corresponds to the ASCII encoded string "HelloWorld", occupying 20 bytes.

4. Using the OCTET_LENGTH function in a query:
   ```sql
   SELECT username, OCTET_LENGTH(password) as password_length
   FROM users;
   ```
In this example, we select the username and the byte length of the password from the user table. This can help us understand the strength of the user's password.

### Notes
- When dealing with multi-byte character sets (such as UTF-8), the actual byte length of characters may differ from the number of characters.
- When comparing string lengths, be sure to consider the impact of character encoding and byte order.