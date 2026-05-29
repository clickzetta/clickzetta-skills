## Function 

`LENGTHB` is a function in SQL that returns the byte length of a string argument. Unlike the `CHAR_LENGTH` or `CHARACTER_LENGTH` functions, `LENGTHB` calculates the number of bytes rather than the number of characters, which is particularly important when dealing with multi-byte character sets (such as UTF-8).

## Syntax
```SQL
LENGTHB(string)
```
## Parameter Description

* **string**: The string expression whose byte length is to be calculated.

## Return Result

This function returns an integer representing the total number of bytes in the input string. For NULL input, the return value is also NULL.

## Example

 Example 1: Basic Usage
```SQL
SELECT LENGTHB('Hello, World!');
```
This will return 13

Example 2: Handling NULL Values
```SQL
SELECT LENGTHB(NULL);
```
This will return `NULL` because the input parameter is NULL.

Example 3: Chinese Characters
```SQL
SELECT LENGTHB('Chinese')
union all
SELECT CHARACTER_LENGTH('Chinese');
+---------------+
| LENGTHB('Chinese') |
+---------------+
| 3             |
| 6             |
+---------------+
```