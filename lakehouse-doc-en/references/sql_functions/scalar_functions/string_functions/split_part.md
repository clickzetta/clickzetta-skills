### SPLIT_PART
```sql
split_part(str, delim, partNum)
```
####  Description
The SPLIT_PART function is used to split a string (str) by a specified delimiter (delim) and return the substring at the specified position (partNum).

#### Parameter Description
* str (string): The string to be split.
* delim (string): The string used as a delimiter to split the input string into multiple substrings.
* partNum (bigint): Specifies the position of the substring to return. When partNum is greater than 0, it indicates the partNum-th substring from the left; when partNum is less than 0, it indicates the partNum-th substring from the right. If partNum exceeds the number of substrings after splitting, an empty string is returned. partNum cannot be 0.

#### Return Result
Returns a string (string) representing the substring at the specified position.

#### Usage Example
```sql
-- Example 1: Return the second substring
SELECT split_part('a,b,c', ',', 2);
-- Result: b

-- Example 2: Return the last substring
SELECT split_part('a,b,c', ',', -1);
-- Result: c

-- Example 3: Return the third substring (counting from the right)
SELECT split_part('a,b,c,d,e', ',', -2);
-- Result: d

-- Example 4: When partNum exceeds the number of substrings, return an empty string
SELECT split_part('a,b,c', ',', 4);
-- Result is empty

-- Example 5: Use multiple characters as delimiters
SELECT split_part('apple-orange-grape', '-|g', 1);
-- Result: apple-orange-grape
```
#### Notes
* When partNum is 0, the function will return an error.
* If the input string or delimiter is empty, the function will return an empty string.
* When partNum is negative, the position of the substring is calculated from the right side.
* If multiple characters are needed as delimiters, multiple characters can be used consecutively or a regular expression can be used for splitting.