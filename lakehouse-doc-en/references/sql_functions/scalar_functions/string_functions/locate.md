###  LOCATE
```sql
LOCATE(substr, str [, pos])
```
####  Description
The LOCATE function is used to find the substring substr in the string str and returns the position index of the first occurrence of substr after the pos position. If the pos parameter is specified, the search starts from that position; if pos is not specified, the search is conducted throughout the entire string str. The position index returned by this function starts counting from 1, and if pos is less than 1, it returns 0.

#### Parameter Description
* substr (string): The substring to be found.
* str (string): The main string to be searched.
* pos (bigint, optional): The starting position index for the search. The default value is 1.

#### Return Result
Returns the position index (bigint type) of the first occurrence of substr in str, and returns 0 if not found.

#### Usage Example
```sql
-- Example 1: Find "World" in the string "HelloWorldWorld", starting from position 1 by default
SELECT LOCATE('World', 'HelloWorldWorld');
-- Result: 6

-- Example 2: Find "World" in the string "HelloWorldWorld", starting from position 7
SELECT LOCATE('World', 'HelloWorldWorld', 7);
-- Result: 11

-- Example 3: Find "3" in the string "1234", starting from position 1 by default
SELECT LOCATE('3', '1234');
-- Result: 3

-- Example 4: Find "c" in the string "abcde", starting from position 2
SELECT LOCATE('c', 'abcde', 2);
-- Result: 3

-- Example 5: Find "shot" in the string "MoonshotAI", pos parameter not specified
SELECT LOCATE('shot', 'MoonshotAI');
-- Result: 5

-- Example 6: Find "World" in the string "HelloWorld", starting from position 9, not found after this position
SELECT LOCATE('World', 'HelloWorld', 9);
-- Result: 0
```
By the above example, you can better understand the usage and functionality of the LOCATE function. In practical applications, the LOCATE function can help you quickly locate and extract specific substrings within a string.