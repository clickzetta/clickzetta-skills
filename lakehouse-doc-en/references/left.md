## LEFT 

In Lakehouse, the LEFT function is used to extract a specified number of characters from the left side of a given string. It is important to note that the unit of character length is utf8 characters, which means that a Chinese character will be considered as one length unit.

###  Syntax

The syntax format of the LEFT function is as follows:
```Plaintext
LEFT(str, len)
```
- `str`: The string from which characters are to be extracted. This parameter accepts data of type VARCHAR.
- `len`: The number of characters to be extracted from the left side of the string. This parameter should be a positive integer.

### Return Value

The LEFT function returns a string containing the specified number of characters extracted from the left side of the input string. The return value's data type is VARCHAR.

###  Example

Below are several usage examples of the LEFT function:

Example 1:
```SQL
SELECT LEFT('Hello, welcome to Lakehouse', 5);
```
This query will return the first 5 characters on the left side of the string 'Hello, welcome to Lakehouse', which is 'Hello'.

 Example 2:
```SQL
SELECT LEFT('Lakehouse, a powerful real-time data warehouse.', 9);
```
This query will return the first 9 characters from the left side of the string 'Lakehouse, a powerful real-time data warehouse.', which is 'Lakehouse'.

Example 3:
```SQL
SELECT LEFT('The quick brown fox jumps over the lazy dog', 9);
```
This query will return the first 9 characters from the left side of the string 'The quick brown fox jumps over the lazy dog', which is 'The quick'.

### Notes

- Ensure that the `len` parameter is a positive integer, otherwise the function will return an error.
- If the `len` parameter is greater than the length of the input string, the LEFT function will return the entire input string.