### TRANSLATE

###  Description
The `translate` function is used to convert certain characters in the input string `str` according to the specified replacement rules. Specifically, it matches the characters in `str` with the character set in the `from` parameter and replaces the matched characters with the characters at the corresponding positions in the `to` parameter. If a character in `from` does not have a corresponding replacement character in `to`, that character is removed from the resulting string.

### Parameter Description
- `str` (string type): The original string that needs character replacement.
- `from` (string type): Contains the set of characters that need to be replaced.
- `to` (string type): Contains the set of characters used for replacement. The order of characters should correspond to the order in the `from` parameter.

### Return Value
Returns the processed string.

###  Example
1. Suppose we have a string "HelloWorld" and we want to replace all "l" with "b", we can use the following statement:
   ```sql
   SELECT translate('HelloWorld', 'l', 'b');
   ```
The execution result is "HebboWorbd".

2. If we want to replace "lo" in the string "HelloWorld" with "ab", we can use the following statement:
   ```sql
   SELECT translate('HelloWorld', 'lo', 'ab');
   ```
The execution result is "HeaabWbrad".

3. Now, if we want to replace "l" and "o" in the string "HelloWorld" with "b" and "n" respectively, we can use the following statement:
   ```sql
   SELECT translate('HelloWorld', 'lo', 'bn');
   ```
The execution result is "HebbnWnrbd".

4. When the number of characters in the `to` parameter is less than the `from` parameter, the extra characters will be deleted. For example, to replace "lo" in the string "HelloWorld" with "a", you can use the following statement:
   ```sql
   SELECT translate('HelloWorld', 'lo', 'a');
   ```
The execution result is "HeaaWrad".

### Notes
- Ensure that the number of characters in the `from` and `to` parameters are equal, otherwise it may result in incomplete replacement or deletion of characters.
- If the `to` parameter is NULL, it will cause all `from` return results to also be NULL.
- This function is case-sensitive, so make sure the case of the input characters matches the case of the characters to be replaced.