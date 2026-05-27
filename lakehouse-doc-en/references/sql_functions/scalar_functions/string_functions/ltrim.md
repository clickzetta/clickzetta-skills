### LTRIM 
```
LTRIM(str [, trimStr])
```
####  Description
The LTRIM function is used to remove specified characters or spaces from the left side of the string `str`. If the `trimStr` parameter is not provided, all space characters on the left side of `str` are removed by default.

#### Parameter Description
- `str` (string): The original string to be processed.
- `trimStr` (string, optional): Specifies the set of characters to be removed from the left side of `str`.

#### Return Result
Returns the processed string.

#### Usage Example
1. Remove all spaces from the left side of the string:
```sql
SELECT 'X' || LTRIM('    HelloWorld    ') || 'X';
-- Result: XHelloWorld    X
```
2. Remove specific characters from the left side of the string:
```sql
SELECT LTRIM('HelloWorld', 'He');
-- Result: World
```
3. Delete multiple characters (character set) from the left side of the string:
```sql
SELECT LTRIM('!!!HelloWorld!!!', '!');
-- Result: HelloWorld
```
4. When `trimStr` is an empty string, `str` will not be modified:
```sql
SELECT LTRIM('Hello', '');
-- Result: Hello
```
5. If `trimStr` contains characters that do not exist in `str`, the LTRIM function will still remove the spaces on the left side of `str`:
```sql
SELECT LTRIM('Hello', 'abc');
-- Result: Hello
```
#### Notes
- When the `trimStr` parameter is empty or contains only spaces, the behavior of the LTRIM function is the same as the default behavior of the `LTRIM` function, which removes all spaces from the left side of the string.
- If the `trimStr` parameter contains non-printable characters or special characters, these characters will also be used to remove characters from the left side of `str`.