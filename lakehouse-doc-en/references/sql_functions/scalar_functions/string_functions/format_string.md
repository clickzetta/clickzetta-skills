## FORMAT_STRING
## Description

`FORMAT_STRING` is a SQL function used for formatting strings. It generates formatted strings based on `printf` style format strings. This function uses the `java.util.Formatter` class and formats using `Locale.US`.

## Syntax
```SQL
FORMAT_STRING(strfmt [, obj1 [, ...]])
```
## Parameter Description

* **strfmt**: An expression of type `STRING` that defines the format of the string. This should include formatting directives such as `%d`, `%s`, etc.
* **obj1, ...**: One or more expressions of type `STRING` or numeric types, which will be formatted and inserted into the corresponding positions in `strfmt`.

## Return Result

This function returns a value of type `STRING`, representing the formatted string.

## Example

Example 1: Basic Usage
```SQL
SELECT FORMAT_STRING('Hello World %d %s', 100, 'days') as res;
+----------------------+
|         res          |
+----------------------+
| Hello World 100 days |
+----------------------+
```
Example 2: Using Numeric Parameters
```SQL
SELECT FORMAT_STRING('The square of %d is %d', 5, 5*5) as res;
+-----------------------+
|          res          |
+-----------------------+
| The square of 5 is 25 |
+-----------------------+
```
Example 3: Using Multiple Parameters
```SQL
SELECT FORMAT_STRING('Name: %s, Age: %d, Location: %s', 'Alice', 30, 'Wonderland') as res;
+--------------------------------------------+
|                    res                     |
+--------------------------------------------+
| Name: Alice, Age: 30, Location: Wonderland |
+--------------------------------------------+
```