###  POSITION
```sql
POSITION(substr, str [, pos])
```
#### Description
The POSITION function is used to find the position of one substring (substr) within another string (str). It returns the position of the first occurrence of substr in str after the pos position. If pos is not provided, the search is performed on the entire str by default. This function is very useful when handling text data, especially when you need to determine the position of a specific character or substring within the text.

#### Parameter Description
* substr (string): The substring to be found.
* str (string): The original string to be searched.
* pos (bigint, optional): The position to start the search. The default value is 1. If pos is less than 1, the function will return 0.

#### Return Result
Returns a bigint value indicating the position of the first occurrence of substr in str. The position count starts from 1. If substr is not found in str, it returns 0.

#### Usage Example
```sql
-- Example 1: Find the position of the substring "World" in "HelloWorldWorld"
SELECT POSITION('World', 'HelloWorldWorld'); -- Result is 6

-- Example 2: Find "World" in "HelloWorldWorld" starting from the 7th character
SELECT POSITION('World', 'HelloWorldWorld', 7); -- Result is 11

-- Example 3: Find "World" in "HelloWorld" (Note: pos not provided, will search the entire string)
SELECT POSITION('World', 'HelloWorld'); -- Result is 6

-- Example 4: Find the position of "a" in "banana", starting from the 3rd character
SELECT POSITION('a', 'banana', 3); -- Result is 4

-- Example 5: Find the position of "apple" in "I love apples", case-sensitive
SELECT POSITION('apple', 'I love apples'); -- Result is 8

-- Example 6: Find the position of "Apple" in "I love apples", case-sensitive, returns 0
SELECT POSITION('Apple', 'I love apples'); -- Result is 0
```