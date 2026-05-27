### SPLIT 

#### Description
The `SPLIT` function is used to split a string (`str`) into multiple substrings based on a specified regular expression (`regex`), and store these substrings in an array. This function is very useful when processing and analyzing text data, as it can help you quickly extract the required information.

#### Parameters
* `str` (string): The original string to be split.
* `regex` (string): The regular expression used to define the splitting rules.
* `limit` (int, optional): The maximum length of the returned array. When `limit` is greater than 0, the length of the returned array will not exceed the value specified by `limit`. When `limit` is less than or equal to 0, it means that the length of the array is not limited. The default value is 0.

#### Return Value
Returns an array (`array<string>`) containing the split substrings.

#### Example

**Example 1**: Basic usage
```sql
SELECT SPLIT('1a2b3c', '[abc]');
```
Results:
```
["1","2","3",""]

```
**Example 2**: Limit the length of the returned array
```sql
SELECT SPLIT('1a2b3c', '[abc]', 2);
```
Results:
```
["1", "2b3c"]
```
**Example 3**: Using different delimiters
```sql
SELECT SPLIT('apple,banana,cherry', ',');
```
Results:
```
["apple", "banana", "cherry"]
```
**Example 4**: Handling Nested Delimiters
```sql
SELECT SPLIT('1-a2-b3-c', '-([a-z]+)-');
```
Results:
```
["1-a2-b3-c"]

```
**Example 5**: Using with the `limit` parameter
```sql
SELECT SPLIT('one:two:three:four', ':', 3);
```
Results:
```
["one", "two", "three:four"]
```