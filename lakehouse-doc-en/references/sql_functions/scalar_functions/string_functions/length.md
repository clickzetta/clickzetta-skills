### LENGTH 

####  Description
The LENGTH function is used to calculate the length of a string, returning the number of characters in the string or the number of bytes in a binary string. This function is very useful for processing text data, allowing you to quickly obtain the length information of the text.

#### Syntax
```sql
LENGTH(expr)
```
#### Parameter Description
- `expr`: Can be an expression of type string or binary.

#### Return Result
Returns an integer (int) representing the number of characters in the input string or the number of bytes in the binary string.

#### Usage Example
1. Calculate the length of a regular string:
```sql
SELECT LENGTH('HelloWorld'); -- The return result is 10
```
2. Calculate the length of a string containing Unicode characters:
```sql
SELECT LENGTH('αβγδ'); -- The return result is 4
```
3. Calculate the length of a string containing special characters:
```sql
SELECT LENGTH('Hello@World!'); -- The return result is 12
```
#### Precautions
- The LENGTH function only applies to string and binary types of data, and will return an error for other types of data.