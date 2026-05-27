### INSTR 
```sql
instr(str, substr)
```
####  Description
The INSTR function is used to find the first occurrence of a specified substring (substr) within a given string (str). When substr is found in str, it returns the integer index of its starting position (counting starts from 1); if not found, it returns 0.

#### Parameter Description
- str: The string to be searched.
- substr: The substring to be found.

#### Return Result
Returns an integer indicating the first occurrence position of substr in str. If substr does not appear in str, it returns 0.

#### Usage Example
1. Query the position of the substring "World" in "HelloWorld":
```sql
SELECT INSTR('HelloWorld', 'World'); -- Result: 6
```
2. Query the position of the substring "Java" in "HelloWorld" (expected not found, return 0):
```sql
SELECT INSTR('HelloWorld', 'Java'); -- Result: 0
```
3. Calculate the starting position of the substring "or" in "HelloWorld":
```sql
SELECT INSTR('HelloWorld', 'or'); -- Result: 7
```
4. Find the position of the substring "Program" in a longer text:
```sql
SELECT INSTR('Programming in C language is fun', 'Program'); -- Result: 1
```
5. When `substr` is an empty string, return 1, because the beginning of `str` always meets the condition:
```sql
SELECT INSTR('HelloWorld', ''); -- Result: 1
```
#### Notes
- If str or substr is NULL, the INSTR function returns NULL.
- The search is case-sensitive, meaning 'Hello' and 'hello' are considered different strings.
- To perform a case-insensitive search, you can first use the UPPER or LOWER function to convert str and substr to the same case, and then compare.

Through the above examples and explanations, you can better understand the usage and functionality of the INSTR function. In practical applications, you can flexibly use this function to find the position of a specific substring.