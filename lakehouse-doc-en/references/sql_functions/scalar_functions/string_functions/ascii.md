### ASCII 
```
ascii(chr)
```
####  Description
The ASCII function is used to obtain the ASCII code value or Unicode code point of a specified character (chr). If the input character length is greater than 1, the function will only return the ASCII code value or Unicode code point of the first character.

#### Parameter Description
* chr: Type is string, representing the character for which the ASCII code value or Unicode code point needs to be queried.

#### Return Result
* Returns an integer (int), representing the ASCII code value or Unicode code point of the input character.

#### Usage Example
1. Query the ASCII code value or Unicode code point of a single character:
```sql
SELECT ASCII('A'); -- Returns 65
```
2. Query the ASCII values or Unicode code points of multiple characters:
```sql
SELECT ASCII('é'), ASCII('a'), ASCII('Z'); -- Returns 233, 97, 90
```
3. Query the ASCII code value or Unicode code point of special characters:
```sql
SELECT ASCII('\n'); -- Returns 10
```
4. Query the ASCII code value or Unicode code point of an empty character:
```sql
SELECT ASCII(''); -- Returns 0
```
### Notes
* When the input character length is 1, the ASCII function will return the ASCII code value or Unicode code point of that character.
* When the input character length is greater than 1, the ASCII function will only return the ASCII code value or Unicode code point of the first character.
* For non-ASCII characters (such as Chinese characters), the ASCII function will return the corresponding Unicode code point.