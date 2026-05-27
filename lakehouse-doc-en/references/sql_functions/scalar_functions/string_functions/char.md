### CHAR 

#### Overview
The `CHAR` function is used to convert an integer (code) into the corresponding character. If the integer is within the ASCII range (i.e., less than or equal to 255), it is treated as an ASCII code and converted to the corresponding character; if the integer is greater than 255, it attempts to parse it as a Unicode code and convert it to the corresponding Unicode character. If the given integer cannot be represented as a valid Unicode character, it returns an empty character.

#### Syntax
```
CHAR(code)
```
#### Parameters
- `code`: Integer, representing the character code to be converted.

#### Return Result
- Returns a string, representing the converted character.

#### Usage Example

1. Convert ASCII code to the corresponding character:
```sql
SELECT CHAR(ASCII('é')), LENGTH(CHAR(ASCII(''))), CHAR(ASCII('a'));
```
Result:
```
   é	1	a
```
2. Convert Unicode code to corresponding character:
   ```sql
   SELECT CHAR(233) AS result;
   ```
Result:
```
result
é
```
3. Convert Illegal Unicode Codes:
   ```sql
   SELECT CHAR(-1) AS result;
   ```
The result is empty

4. Convert multiple character codes:
   ```sql
   SELECT CHAR(65), CHAR(66), CHAR(67) AS  ABC;
   ```
Result:
   ```
   A	B	C
   ```
#### Notes
- If the input integer exceeds the Unicode range, an empty character will be returned.
- Please ensure that the input integer is a valid character code, otherwise it may result in incorrect results.