# Regular Expression Supported Functions
| Function | Description |
| -------------------- | ------------------------------------------------------- |
| RLIKE                | Checks whether a string matches the specified regular expression pattern.                                |
| REGEXP_EXTRACT       | Uses the specified regular expression (regexp) to extract matching text from the input string (str).                  |
| REGEXP_EXTRACT_ALL   | Extracts all substrings from a string that match a regular expression.                                 |
| REGEXP_REPLACE       | Finds all substrings in the string str that match the regular expression regexp and replaces them with the specified string rep. |

# Usage Notes

The regular expression engine used by Lakehouse is [re2](https://github.com/google/re2).

* **POSIX character classes**: Character classes such as `[[:alnum:]]` are supported.
* **Backslash sequences**: Includes `\d` (digits), `\D` (non-digits), `\s` (whitespace), `\S` (non-whitespace), `\w` (word characters), `\W` (non-word characters), `\b` (word boundary), and `\B` (non-word boundary).
* **POSIX wildcards**: Such as `.` (matches any single character) and `*` (matches zero or more occurrences of the preceding element).
* **Unicode support**: All regular expression functions support Unicode characters.

# Escape Character Handling
When using string constants in SQL statements, if they contain backslash sequences or metacharacters (such as `\d`, `\s`, `*`, `?`), these escape characters are automatically escaped. For example, the output of `SELECT '\\' AS col;` will be `\`. For values actually stored in a table as `\\`, no escaping occurs — only string constants undergo this escaping.

Therefore, when writing regular expressions that need to match these special sequences, additional escape characters are required. For example:

```SQL
-- In string constants, backslash sequences are automatically escaped
SELECT '\\\\' as col1, '\\' as col2;
+------+------+
| col1 | col2 |
+------+------+
| \\   | \    |
+------+------+
-- If \\ is stored in a table, automatic escaping does not occur
CREATE TABLE test_regex(col STRING);
INSERT INTO test_regex VALUES('\\');
SELECT * FROM test_regex;
+-----+
| col |
+-----+
| \\  |
+-----+
```

When matching with regular expressions, strings containing backslash sequences or metacharacters must be escaped:

```SQL
SELECT col, RLIKE(col, '\\\\') FROM test_regex;
+-----+---------------------+
| col | RLIKE(col, '\\\\') |
+-----+---------------------+
| \\  | TRUE                |
+-----+---------------------+
```

# Using the String Prefix r

To avoid manually handling escape characters when it is uncertain whether escaping is needed, Lakehouse supports adding an `r` prefix before a string, indicating that escape characters in the [string](../../../STRING.md) are not escaped and can be directly used in regular expressions. This allows users to write regular expressions normally without worrying about the SQL engine's escaping behavior. For example:

```SQL
-- Use the r prefix to match data in a table
SELECT col, RLIKE(col, r'\\') FROM test_regex;
+-----+---------------------+
| col | RLIKE(col, '\\\\') |
+-----+---------------------+
| \\  | TRUE                |
+-----+---------------------+
-- Use the r prefix to match a string constant
SELECT RLIKE(r'%SystemDrive%\Users\John', r'%SystemDrive%\\Users.*') as res;
+------+
| res  |
+------+
| TRUE |
+------+
-- Regular expression matching without the r prefix
SELECT r'%SystemDrive%\Users\John' rlike '%SystemDrive\\\\\Users.*';
+------+
| res  |
+------+
| true |
+------+
```

By using the `r` prefix, Lakehouse simplifies the use of regular expressions, making text matching and data processing more intuitive and efficient.
