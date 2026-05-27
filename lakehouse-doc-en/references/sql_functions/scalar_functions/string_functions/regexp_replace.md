### REGEXP_REPLACE 
```sql
regexp_replace(str, regexp, rep [, position])
```
#### Function Description
The REGEXP_REPLACE function is used to find all substrings in the string `str` that match the regular expression `regexp` and replace them with the specified string `rep`.

#### Parameter Description
* str (string): The string to be processed.
* regexp (string): The regular expression string. The current regular expression engine used is [re2](https://github.com/google/re2).
* rep (string): The string used to replace the matched substrings.
* position (int, optional): The position to start matching, greater than or equal to 0. The default value is 1, which means matching starts from the beginning of `str`. If `position` exceeds the length of `str`, the result will return `str`.

#### Return Result
Returns the processed string.

#### Usage Example
```sql
-- Example 1: Replace numbers in the string with "digit"
> SELECT regexp_replace('100-500',r'(\d+)', 'digit');
-- Result: digit-digit

-- Example 2: Replace specific characters in the string
> SELECT regexp_replace('a1b2c3', r'(\d)', 'x');
-- Result: axbxcx

-- Example 3: Use regular expressions to match and replace substrings in the string
> SELECT regexp_replace('hello world', r'(\w{5})', '$1!');
-- Result: hello! world!

-- Example 4: Specify the starting position for matching
> SELECT regexp_replace('abcdef', '(b.)', 'x', 2);
-- Result: axdef