### CONCAT_WS 

#### Overview
The `CONCAT_WS` function is used to concatenate multiple strings or string elements in an array into a single string. The function can concatenate the input strings or string elements in an array based on the specified separator `sep`. If the input string is `NULL`, it is ignored in the result.

#### Syntax
```
CONCAT_WS(sep, str1, str2, ..., strN)
CONCAT_WS(sep, array1, array2, ..., arrayN)
```
#### Parameters
- `sep`: Separator string used to join the input strings.
- `str1, str2, ..., strN`: Strings to be joined.
- `array1, array2, ..., arrayN`: Arrays containing the string elements to be joined.

#### Return Result
Returns a concatenated string.

#### Usage Example

1. Basic usage:
```sql
SELECT CONCAT_WS('-', 'hello', 'world');
```
Results:
```
hello-world
```
2. Connecting multiple strings:
```sql
SELECT CONCAT_WS('-', 'hello', 'my', 'friend', '!');
```
Results:
```
hello-my-friend-!
```
3. Ignore `NULL` values:
```sql
SELECT CONCAT_WS('-', 'hello', NULL, 'world', NULL);
```
Results:
```
hello-world
```
4. Using Arrays to Join Strings:

```sql
SELECT CONCAT_WS('-', array('hello', 'my', 'friend'), array('is', NULL, 'awesome'));
```
Results:
```
hello-my-friend-is-awesome
```
5. Use in conjunction with other functions:
```sql
SELECT CONCAT_WS('-', UPPER('hello'), LENGTH('world'), LOWER('!'));
```
Results:
```
HELLO-5-!
```
#### Notes
- When the input string or array element is `NULL`, the `CONCAT_WS` function will ignore these values.
- If all input strings or array elements are `NULL`, an empty string is returned.
- If the separator `sep` is also `NULL`, a NULL is returned.

Through the above examples and explanations, you can better understand the usage and functionality of the `CONCAT_WS` function. In practical applications, you can flexibly use this function to concatenate strings or array elements as needed.