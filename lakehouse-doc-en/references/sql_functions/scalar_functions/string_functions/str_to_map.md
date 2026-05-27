### STR_TO_MAP

###  Description

This function is used to split a string into key-value pairs according to specified delimiters and generate a result of type map.

### Parameter Description

* str (string type): The string to be split.
* pairDelim (string type, optional parameter, default value is ','): Used to specify the delimiter between each key-value pair.
* keyValueDelim (string type, optional parameter, default value is ':'): Used to specify the delimiter between the key and value.

### Return Value

Returns a result of type map, where both the keys and values are of string type.

### Usage Example

1. Basic Usage
   ```sql
   SELECT STR_TO_MAP('a:1,b:2,c:3');
   ```
Return results:
   ```json
   {"a" : "1", "b" : "2", "c" : "3"}
   ```
2. Custom Key-Value Pair Separator
   ```sql
   SELECT STR_TO_MAP('a/1;b/2;c/3', ';', '/');
   ```
Return results:
   ```json
   {"a" : "1", "b" : "2", "c" : "3"}
   ```
```markdown
3. Custom Key-Value Separators and Keys Without Values
```
   ```sql
   SELECT STR_TO_MAP('name:Tom;age:28;gender:;hobby:coding', ';', ':');
   ```
Return results:
   ```json
   {"name" : "Tom", "age" : "28", "gender" : "", "hobby" : "coding"}
   ```
### Precautions

* If there are missing keys or values in the input string, the function will treat it as a valid key-value pair and set the missing key or value to null.
* If the input string format is incorrect, the function will return an empty map type result.