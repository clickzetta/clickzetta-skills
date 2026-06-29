## REGEXP_COUNT

### Function Description
The `REGEXP_COUNT` function is used to count the number of times substrings matching a specified regular expression pattern appear in a string. This function returns an integer representing the total number of matches. If the string is empty or no matches exist, it returns 0.

### Syntax

```sql
REGEXP_COUNT(string_expression, pattern_expression)
```

### Parameter Description

- string_expression: STRING, the string expression to be searched
- pattern_expression: STRING, Java regular expression pattern. See [List of Supported Regular Expression Functions](regexp-statement.md)

### Return Value

Return type: `INTEGER`

Returns the number of times the specified regular expression matches in the string. If the pattern does not match, returns 0.

### Usage Examples

**Example 1: Count Simple String Matches**

Count the occurrences of `hello` in a string:

```sql
SELECT REGEXP_COUNT('hello world hello', 'hello') as count_result;
```

Execution Result:

```
count_result
2
```

**Example 2: Count Digit Matches**

Count the number of digits in a date string:

```sql
SELECT REGEXP_COUNT('2024-10-28', '\\d+') as test2;
```

Execution Result:

```
test2
3
```

In this example, the date string `2024-10-28` contains 3 digit sequences: `2024`, `10`, and `28`.

**Example 3: Count Character Class Patterns**

Count the number of individual digit characters in a string:

```sql
SELECT REGEXP_COUNT('hello123world456', '[0-9]') as test3;
```

Execution Result:

```
test3
6
```

The string `hello123world456` contains 6 digit characters (1, 2, 3, 4, 5, 6).

**Example 4: Complex Pattern Matching**

Apply different patterns on multiple strings:

```sql
SELECT REGEXP_COUNT('apple apple apple', 'apple') as apple_count, REGEXP_COUNT('The quick brown fox', '[aeiou]') as vowel_count, REGEXP_COUNT('123-456-7890', '[0-9]') as digit_count;
```

Execution Result:

```
| apple_count | vowel_count | digit_count |
| ----------- | ----------- | ----------- |
| 3           | 5           | 10          |
```

* `apple` appears 3 times in the string
* Vowels appear 5 times in "The quick brown fox"
* Digit characters appear 10 times in the phone number

**Example 5: Edge Case Handling**

Test empty strings and non-matching patterns:

```sql
SELECT REGEXP_COUNT('', 'a') as empty_string, REGEXP_COUNT('hello', 'xyz') as no_match, REGEXP_COUNT('aaa', 'a+') as pattern_match;
```

Execution Result:

```
| empty_string | no_match | pattern_match |
| ------------ | -------- | ------------- |
| 0            | 0        | 1             |
```

* Empty string returns 0
* Non-existent pattern returns 0
* Greedy quantifier `a+` treats consecutive `aaa` as one match, returning 1