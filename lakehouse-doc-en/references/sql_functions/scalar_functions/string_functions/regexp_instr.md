## REGEXP_INSTR

### Function Description
The `REGEXP_INSTR` function is used to return the position of the first occurrence of a substring matching a specified regular expression pattern in the source string. Position numbering starts from 1. If no match is found, it returns 0.

### Syntax

```sql
REGEXP_INSTR(string_expression, pattern_expression)
```

### Parameter Description

- string_expression: STRING, the string expression to be searched
- pattern_expression: STRING, Java regular expression pattern. See [List of Supported Regular Expression Functions](regexp-statement.md)

### Return Value

Return type: `INTEGER`

Returns the starting position (starting from 1) of the first substring matching the specified pattern. If no match is found, returns 0.

### Usage Examples

**Example 1: Find Position of Specific Character**

Find the position of the `@` symbol in an email address:

```sql
SELECT REGEXP_INSTR('email@example.com', '@') as position;
```

Execution Result:

```
position
6
```

The character `@` is located at position 6 in the email address (the 6th character).

**Example 2: Find First Occurrence Position of String**

Find the position of the first occurrence in text containing repeated strings:

```sql
SELECT REGEXP_INSTR('hello world hello', 'hello') as first_position;
```

Execution Result:

```
first_position
1
```

The first occurrence of `hello` in the string is at position 1.

**Example 3: Find Match Position Using Character Class**

Find the position of the first digit character:

```sql
SELECT REGEXP_INSTR('abc123def456ghi', '[0-9]') as first_digit_position;
```

Execution Result:

```
first_digit_position
4
```

The first digit `1` is located at position 4 in the string.

**Example 4: Parallel Search on Multiple Strings**

Find the position of different patterns on multiple strings:

```sql
SELECT REGEXP_INSTR('email@example.com', '@') as at_position, REGEXP_INSTR('hello world hello', 'hello') as hello_position, REGEXP_INSTR('test string', ' ') as space_position;
```

Execution Result:

```
at_position | hello_position | space_position
6           | 1              | 5
```

* The `@` symbol is at position 6
* The first `hello` is at position 1
* The space is at position 5

**Example 5: Use Complex Pattern Matching**

Use advanced patterns such as character classes and word boundaries:

```sql
SELECT REGEXP_INSTR('user@example.com', '[a-z]+') as letters_position, REGEXP_INSTR('file_123_backup.txt', '[0-9]') as digit_position, REGEXP_INSTR('www.example.com', '\\w+') as word_position;
```

Execution Result:

```
letters_position | digit_position | word_position
1                | 6              | 1
```

* The lowercase letter sequence starts at position 1
* The first digit is at position 6
* Word characters start at position 1

**Example 6: Handle Cases with No Match**

Test scenarios where no matches exist:

```sql
SELECT REGEXP_INSTR('', 'a') as empty_result, REGEXP_INSTR('hello', 'xyz') as no_match_result;
```

Execution Result:

```
empty_result | no_match_result
0            | 0
```

* Empty string returns 0
* Non-existent pattern returns 0

### Use Cases

* **Email Address Parsing**: Quickly locate the `@` symbol to separate the username and domain parts
* **Data Cleaning**: Locate specific patterns in mixed-format strings for splitting or extraction
* **File Path Processing**: Find the starting position of file extensions (the position of `.`)
* **Phone Number Formatting**: Locate the starting position of digit sequences for format conversion
* **URL Parsing**: Quickly locate the position of `://` or other protocol separators

### Important Notes

* The returned position is 1-based, not 0-based
* When using backslash as an escape character, use double backslash `\\` in SQL strings to represent a single `\`
* The function returns the position of the first match. To find subsequent matches, use in combination with other string functions (such as `SUBSTR`)
* The regular expression engine uses the RE2 specification
* Pattern matching is case-sensitive