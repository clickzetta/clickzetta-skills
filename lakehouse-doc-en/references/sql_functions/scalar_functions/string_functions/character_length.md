## CHARACTER\_LENGTH
## Description
CHARACTER\_LENGTH, used to return the number of characters in a string.

## Syntax
```SQL
CHARACTER_LENGTH(string|char|)
```
## Parameter Description

* **string**: The string expression whose length is to be calculated.

## Return Result

This function returns an integer representing the total number of characters in the input string.

## Example

Example 1: Basic Usage
```SQL
SELECT CHARACTER_LENGTH('Hello, World!');
+-------------------------------------+
| `CHARACTER_LENGTH`('Hello, World!') |
+-------------------------------------+
| 13                                  |
+-------------------------------------+
```
Example 2: Using with NULL Values
```SQL
SELECT CHARACTER_LENGTH(NULL);
+--------------------------+
| `CHARACTER_LENGTH`(NULL) |
+--------------------------+
| null                     |
+--------------------------+
```
 Example 3: Unicode Characters

```SQL
 SELECT CHARACTER_LENGTH('café');
+--------------------------+
| `CHARACTER_LENGTH`('café') |
+--------------------------+
| 2                        |
+--------------------------+
```