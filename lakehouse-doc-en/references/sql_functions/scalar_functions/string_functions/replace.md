### REPLACE
```sql
replace(str, search [, replace])
```
####  Description
This function is used to find the substring `search` in the string `str` and replace the found content with the `replace` string. If the `replace` parameter is not provided, `search` is replaced with an empty string by default.

#### Parameter Description
- `str` (string): The original string to be operated on.
- `search` (string): The substring to be found and replaced in `str`.
- `replace` (string, optional): The target string used to replace the found `search` substring. If this parameter is not provided, the `search` substring is deleted by default.

#### Return Result
Returns a new string where the `search` substring in `str` has been replaced with the `replace` string, or if the `replace` parameter is not provided, the `search` substring is deleted.

####  Example
1. Replace "World" with "Java" in the string "Hello World":
```sql
> SELECT replace('Hello World', 'World', 'Java');
'Hello Java'
```
2. Delete "100" from the string "100-500":
```sql
> SELECT replace('100-500', '100');
'-500'
```
3. Replace all "3" in the string "12345" with "X":
```sql
> SELECT replace('12345', '3', 'X');
'12X45'
```
4. Replace all hyphens ("-") in the string "data-science" with underscores ("_"):
```sql
> SELECT replace('data-science', '-', '_');
'data_science'
```
Through these examples, you can see that the `replace` function is very flexible and easy to use when handling strings. You can easily replace or remove specific content in a string as needed.