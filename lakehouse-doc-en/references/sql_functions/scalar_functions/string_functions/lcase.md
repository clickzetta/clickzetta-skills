### LCASE Function

```
lcase(str)
```

#### Description

The `LCASE` function is an alias for `LOWER`. It converts all uppercase characters in the input string to lowercase and returns the converted string.

#### Parameters

* `str`: The string to be converted to lowercase.

#### Return Type

* Returns a string with all characters converted to lowercase.

#### Notes

* The `LCASE` function is identical to the `LOWER` function and they can be used interchangeably.

#### Examples

1. Convert "HelloWorld" to "helloworld"

```sql
SELECT LCASE('HelloWorld');
+----------------------+
| LCASE('HelloWorld')  |
+----------------------+
| helloworld           |
+----------------------+
```

2. Convert "Python" and "JAVA" to lowercase

```sql
SELECT LCASE('Python'), LCASE('JAVA');
+------------------+-----------------+
| LCASE('Python')  | LCASE('JAVA')   |
+------------------+-----------------+
| python           | java            |
+------------------+-----------------+
```
