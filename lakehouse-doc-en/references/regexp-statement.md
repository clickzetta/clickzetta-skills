# List of Functions Supported by Regular Expressions
| Function | Description | 
| -------------------- | ------------------------------------------------------- |
| RLIKE                | Used to check if a string matches a specified regular expression pattern. |
| REGEXP_EXTRACT      | Extracts matching text from an input string (str) using a specified regular expression (regexp). |
| REGEXP_EXTRACT_ALL | Used to extract all substrings from a string that match a regular expression. |
| REGEXP_REPLACE      | Finds all substrings in string str that match the regular expression regexp and replaces them with the specified string rep. |

# Instructions

The regular expression engine used by Lakehouse is [re2](https://github.com/google/re2):

* **POSIX Character Classes**: Allows the use of character classes like `[[:alnum:]]`.
* **Backslash Sequences**: Includes `\d` (digit), `\D` (non-digit), `\s` (whitespace), `\S` (non-whitespace), `\w` (word character), `\W` (non-word character), `\b` (word boundary), and `\B` (non-word boundary).
* **POSIX Wildcards**: Such as `.` (matches any single character) and `*` (matches zero or more occurrences of the preceding element).
* **Unicode Support**: All regular expression functions support Unicode characters.

# Handling Escape Characters
When using string literals in SQL statements, if they contain backslash sequences or metacharacters (such as `\d`, `\s`, `*`, `?`), these escape characters will be automatically escaped. For example, the output of `SELECT '\\' AS col;` will be `\`. For values actually stored in the table as `\\`, no escaping will occur; only string literals undergo this escaping.

Therefore, when writing regular expressions that need to match these special sequences, additional escape characters need to be added. For example:
```SQL
-- In string literals, backslash sequences will be automatically escaped
SELECT '\\\\' as col1, '\\' as col2;
+------+------+
| col1 | col2 |
+------+------+
| \\   | \    |
+------+------+
-- If \\ is stored in the table, there will be no automatic escaping
CREATE TABLE test_regex(col STRING);
INSERT INTO test_regex VALUES('\\');
SELECT * FROM test_regex;
+-----+
| col |
+-----+
| \\  |
+-----+
```
When using regular expressions for matching, it is necessary to escape strings that contain backslash sequences or metacharacters:
```SQL
SELECT col, RLIKE(col, '\\\\') FROM test_regex;
+-----+---------------------+
| col | RLIKE(col, '\\\\') |
+-----+---------------------+
| \\  | TRUE                |
+-----+---------------------+
```
# Usage of String Prefix r

To avoid manually handling escape characters when it is uncertain when they are needed, Lakehouse supports adding the `r` prefix to strings, indicating that escape characters in the [string](<STRING.md>) will not be escaped and can be directly input into the regular expression for execution. This way, users can write regular expressions as usual without worrying about SQL engine translation issues. For example:
```SQL
-- Use the r prefix to match data in the table
SELECT col, RLIKE(col, r'\\') FROM test_regex;
+-----+---------------------+
| col | RLIKE(col, '\\\\') |
+-----+---------------------+
| \\  | TRUE                |
+-----+---------------------+
-- Use the r prefix to match string constants
SELECT RLIKE(r'%SystemDrive%\Users\John', r'%SystemDrive%\\Users.*') as res;
+------+
| res  |
+------+
| TRUE |
+------+
-- Regular expression matching without using the r prefix
SELECT r'%SystemDrive%\Users\John' rlike '%SystemDrive\\\\\Users.*';
+------+
| res  |
+------+
| true |
+------+
```
By using the `r` prefix, Lakehouse simplifies the use of regular expressions, making text matching and data processing more intuitive and efficient.