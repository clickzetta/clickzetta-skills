### BASE64 
#### Description
The BASE64 function is used to convert binary data into a string in BASE64 encoded format. This function is very useful for handling binary data in situations where text format is required, such as sending images in emails or embedding audio files in web pages.

#### Syntax
```sql
base64(bin)
```
#### Parameters
- bin (binary): The binary data to be converted.

#### Return Result
- Returns a string representing the BASE64 encoding of the input binary data.

#### Usage Example
1. Convert a string to BASE64 encoding:
```sql
> SELECT base64('Hello, world!');
SGVsbG8sIHdvcmxkIQ==
```
2. Use in combination with other functions, for example, convert the current time to datetime format and then to BASE64 encoding:
```sql
> SELECT base64(now()::string);
MjAyNC0wNC0wOCAxNTo1NjoyMy4yNDM0OQ==
```
#### Notes
- The input binary data must be a valid binary string, otherwise it may cause conversion failure.