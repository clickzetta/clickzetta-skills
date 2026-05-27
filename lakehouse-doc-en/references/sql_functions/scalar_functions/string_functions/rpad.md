###  RPAD
``` sql
rpad(str, len[, pad])
```
####  Description
The RPAD function is used to pad the right side of a string. It adds the specified `pad` string to the right side of the given string `str` until the total length reaches `len`. If `len` is less than the length of the string `str`, the function will truncate the original string to the length of `len` and return it. If `len` is less than 1, the function returns an empty string. If the `pad` string is not specified, a space character (' ') is used as the default padding character.

#### Parameter Description
- `str`: The input string.
- `len`: The target total length.
- `pad` (optional): The string used for padding, default is a space character (' ').

#### Return Result
Returns a new string with a length of `len`, padded on the right side with the `pad` string.

#### Usage Example
1. Basic usage: Add the specified padding character to the right side of the string.
   ```sql
   > SELECT rpad('hello', 10, '123');
  hello12312  
   ```
2. When `len` is greater than the length of `str`, use the default padding character (space).
   ```sql
   > SELECT rpad('world', 12);
   world      
   ```
3. When `len` is less than the length of `str`, truncate the original string to the length of `len`.
   ```sql
   > SELECT rpad('hello world', 5);
   hello
   ```
4. When `len` is less than 1, return an empty string.
   ```sql
   > SELECT rpad('test', 0);
   
   ```
5. Use Custom Padding Characters.
   ```sql
   > SELECT rpad('abc', 8, '##');
   abc#####
   ```
#### Notes
- When the length of the `pad` string is greater than `len` minus the length of `str`, the `pad` string will be truncated to fit the target length.
- If the `pad` string is empty, a single space character will be used as the padding character.

By using the RPAD function, you can easily format and align strings to meet different data processing needs.