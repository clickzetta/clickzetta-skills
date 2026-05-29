# STRING Type

`STRING` type is used to represent all character sequences with a length greater than or equal to 0. This type can store text data up to 16MB. During batch or real-time data import, the length of the field will be checked. If you encounter data exceeding 16MB during import, you can adjust the string length limit by modifying the table properties, for example, setting the `STRING` length to 32MB:
```
ALTER TABLE table_name SET PROPERTIES("cz.storage.write.max.string.bytes"="33554432");
```
## Syntax
```
[r]'c [ ... ]'
```
- `r`: Optional prefix indicating that escape characters in the string will not be escaped. This is useful for strings containing special characters, as it allows the string to be interpreted as-is, rather than being converted into escape sequences.
- `c`: Any character in the Unicode character set.

## Escape Sequences

In regular string literals (without the `r` prefix), the following escape sequences are recognized and replaced according to the following rules:

- `\0` -> `\u0000`, Unicode character with code 0;
- `\b` -> `\u0008`, backspace;
- `\n` -> `\u000a`, newline;
- `\r` -> `\u000d`, carriage return;
- `\t` -> `\u0009`, horizontal tab;
- `\Z` -> `\u001A`, substitute;
- `\%` -> `\%`;
- `\_` -> `\_`;
- `\<other char>` -> `<other char>`, skip the backslash and keep the character as-is.

If the string has the `r` prefix, these escape sequences are not recognized.

## Examples

Here are some examples using the `STRING` type and escape sequences:
```
-- No r added, escape sequences are interpreted
SELECT 'Hello \n World!' AS col;
+---------+
|   col   |
+---------+
| Hello 
 World! |
+---------+

-- r added, escape sequences are not interpreted
SELECT r'Hello \n World!' AS col;
+-----------------+
|       col       |
+-----------------+
| Hello \n World! |
+-----------------+

-- Using an empty string
SELECT '' AS col;
+-----+
| col |
+-----+
|     |
+-----+

-- Using a backslash
SELECT '\\' AS col;
+-----+
| col |
+-----+
| \   |
+-----+

-- Using r prefix, backslash is not escaped
SELECT r'\\' AS col;
+-----+
| col |
+-----+
| \\  |
+-----+
```