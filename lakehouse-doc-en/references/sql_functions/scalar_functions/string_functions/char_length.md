## CHAR_LENGTH 
## Description

CHAR\_LENGTH is equivalent to CHARACTER\_LENGTH and is used to return the number of characters in a string.

## Syntax
```SQL
CHAR_LENGTH(string|char|)
```
## Parameter Description

* **string**: The string expression whose character length is to be calculated.

## Return Result

This function returns an integer representing the total number of characters in the input string.

## Example

Example 1: Basic Usage
```SQL
SELECT CHAR_LENGTH('Hello, World!');
+-------------------------------------+
| `CHAR_LENGTH`('Hello, World!') |
+-------------------------------------+
| 13                                  |
+-------------------------------------+
```
Example 2: Using with NULL Values
```SQL
SELECT CHAR_LENGTH(NULL);
+--------------------------+
| `CHAR_LENGTH`(NULL) |
+--------------------------+
| null                     |
+--------------------------+
```
Example 3: Unicode Characters
```SQL
 SELECT CHAR_LENGTH('café');
+--------------------------+
| `CHARA_LENGTH`('café') |
+--------------------------+
| 2                        |
+--------------------------+
```