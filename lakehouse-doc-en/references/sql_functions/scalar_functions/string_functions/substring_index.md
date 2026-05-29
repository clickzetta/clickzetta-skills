### SUBSTRING_INDEX
```sql
substring_index(expr, delim, count) 
```
####  Description
The SUBSTRING_INDEX function is used to extract the substring before the delimiter delim appears count times in a string or binary data. This function is very useful when processing text data, especially when you need to split or extract strings based on a specific delimiter.

#### Parameter Description
* **expr** (string/binary): The original string or binary data to be processed.
* **delim** (string/binary): The string or binary data used as the delimiter, of the same type as expr.
* **count** (bigint): Indicates the count of the delimiter's occurrences. If count is positive, counting starts from the left side of the string; if count is negative, counting starts from the right side; if count is 0, an empty string is returned.

#### Return Result
Returns a string or binary data representing the substring before the delimiter appears count times in expr.

#### Usage Example
```sql
-- Example 1: Extract substring from left to right
SELECT substring_index('a,b,c,d', ',', 2);
-- Result: 'a,b'

-- Example 2: Extract substring from right to left
SELECT substring_index('a,b,c,d', ',', -2);
-- Result: 'c,d'

-- Example 3: Extract the entire string before the delimiter
SELECT substring_index('a,b,c,d', ',', 1);
-- Result: 'a'

-- Example 4: Use negative count to extract substring from right to left
SELECT substring_index('a,b,c,d', ',', -1);
-- Result: 'd'

-- Example 5: Return an empty string when count is 0
SELECT substring_index('a,b,c,d', ',', 0);
-- Result: ''

-- Example 6: Extract substring from binary data
SELECT substring_index('hello,world,123', ',world,', 1);
-- Result: 'hello'
```
#### Notes
* When count is a positive number, the function will start searching for the delimiter delim from the left side of the string and return the substring before it.
* When count is a negative number, the function will start searching for the delimiter delim from the right side of the string and return the substring before it.
* When the absolute value of count is greater than the number of occurrences of the delimiter, the function will return an empty string.
* If expr or delim is NULL, it returns NULL.