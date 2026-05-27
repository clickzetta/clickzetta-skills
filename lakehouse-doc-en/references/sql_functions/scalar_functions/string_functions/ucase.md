### UCASE Function

```
ucase(str)
```

#### Description

The `UCASE` function is an alias for `UPPER`. It converts all lowercase letters in the input string to uppercase and returns the converted string.

#### Parameters

* `str`: The string to be converted to uppercase.

#### Return Type

* Returns a string where all lowercase letters have been converted to uppercase.

#### Notes

* The `UCASE` function is identical to the `UPPER` function and they can be used interchangeably.
* The `UCASE` function only applies to English letters in the input string. Conversion results for other languages or special characters may not meet expectations.

#### Examples

1. Convert a simple string

```sql
SELECT UCASE('hello world');
+-----------------------+
| UCASE('hello world')  |
+-----------------------+
| HELLO WORLD           |
+-----------------------+
```

2. Convert a string containing digits and special characters

```sql
SELECT UCASE('Hello123!@#');
+-----------------------+
| UCASE('Hello123!@#')  |
+-----------------------+
| HELLO123!@#           |
+-----------------------+
```
