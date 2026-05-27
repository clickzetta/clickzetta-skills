### SUBSTRING 

#### Description
The SUBSTRING function is used to extract a substring from a string or binary data. Based on the specified starting position (pos) and length (len), the SUBSTRING function returns the corresponding substring.

#### Syntax
```
substring(str, pos [, len])
    
substring(str FROM pos [FOR len])
```
#### Parameters
- `str` (string/binary): The input string or binary data.
- `pos` (bigint): The starting position of the substring. If pos is greater than or equal to 1, it starts from the pos-th character from the left; if pos is less than or equal to -1, it starts from the -pos-th character from the right; if pos is equal to 0, it starts from the first character on the left.
- `len` (bigint, optional): The length of the substring. If not specified, the complete substring starting from pos is returned.

#### Return Result
Returns a string representing the substring extracted from the input string.

#### Usage Example

1. Extract the first two characters of the string:
   ```sql
   > SELECT substring('Hello, world!', 1, 2);
   He
   ```
2. Extract the complete substring starting from the fourth character:
   ```sql
   > SELECT substring('Hello, world!', 4);
   lo, world!
   ```
3. Extract the two characters starting from the second to last character of the string:
   ```sql
   > SELECT substring('Hello, world!', -2, 2);
   d!
   ```
4. Extract the domain name from the URL:
   ```sql
   > SELECT substring('http\://www\.example.com', LOCATE('://', 'http\://www\.example.com')+3);
   www.example.com
   ```
5. Extract specific parts of a string (e.g., extract month and date):
   ```sql
   > SELECT substring('2023-04-15', 5, 5);
   -04-1  
   ```
By the above examples, you can see the application of the SUBSTRING function in different scenarios. Using the SUBSTRING function allows you to conveniently extract the required substring from a string, thereby meeting various data processing needs.