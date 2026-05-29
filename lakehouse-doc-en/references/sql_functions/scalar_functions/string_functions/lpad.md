### LPAD 
``` sql
lpad(str, len[, pad])
```
####  Description
The LPAD function is used to perform left-side padding on a string. When the length of the given string `str` is less than the specified `len`, the LPAD function will pad the left side of `str` with the `pad` string until the total length of the new string equals `len`. If the length of `str` is already equal to or greater than `len`, the original string is returned. If `len` is less than 1, an empty string is returned. If the `pad` string is not specified, the default padding character is a space (' ').

#### Parameter Description
- `str` (required): The original string that needs left-side padding.
- `len` (required): The target length of the string.
- `pad` (optional): The string used for padding. The default value is a space character (' ').

#### Return Value
Returns a new string with a length of `len`, padded on the left side with the `pad` string.

#### Usage Example
1. Padding with a single character:
```sql
> SELECT lpad('hello', 7, '#');
##hello
```


2. Using the default padding character (space):
```sql
> SELECT lpad('world', 10);
      world     
```
In this example, the length of the original string "world" is 5, and we need to pad it to 10 characters. Since the `pad` string is not specified, the LPAD function uses the default space character for padding, resulting in the new string "     world".

3. Specify the padding string as a special character:
```sql
> SELECT lpad('!', 6, '@@');
@@@@@!
```


4. When `len` is less than 1, return an empty string:
```sql
> SELECT lpad('example', 0, '%');
```
In this example, the specified target length `len` is 0, and the LPAD function will return an empty string.