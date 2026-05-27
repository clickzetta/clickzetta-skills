### SUBSTR 

####  Description
The SUBSTR function is used to extract a substring of specified position and length from a string or binary data.

#### Syntax
```
SUBSTR(str, pos [, len])
```
or
```
SUBSTR(str FROM pos [FOR len])
```
#### Parameter Description
- `str` (string/binary): Input string or binary data.
- `pos` (bigint): Starting position of the substring. If `pos` is greater than or equal to 1, extraction starts from the `pos`-th character from the left; if `pos` is less than or equal to -1, extraction starts from the `-pos`-th character from the right; if `pos` is equal to 0, extraction starts from the first character on the left.
- `len` (bigint, optional): Length of the substring to extract. If not specified, the full substring starting from `pos` is returned.

#### Return Result
Returns the extracted substring, type is string.

####  Example
1. Extract 5 characters from the string "Hello, world!" starting from the second character:
```sql
SELECT SUBSTR('Hello, world!', 2, 5);
-- Output result: ello,
```
2. Extract all characters from the fourth character onwards from the string "123456789":
```sql
SELECT SUBSTR('123456789', 4);
-- Output result: 456789
```
3. Extract 1 character from the string "Database" starting from the second character, and specify the character set as UTF-8:
```sql
SELECT SUBSTR('Database' FROM 2 FOR 1 );
-- Output result: a
```
#### Notes
- If the value of `pos` or `len` exceeds the range of the input string, the function will return an empty string.
- When extracting a string, the units for `pos` and `len` are characters, not bytes.