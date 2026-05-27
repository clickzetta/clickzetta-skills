### UNBASE64 
```
unbase64(str)
```
####  Description
The UNBASE64 function is used to convert a string in BASE64 encoding format to binary format. This function accepts a string parameter and returns the corresponding binary data.

#### Parameter Description
* str: The input string in BASE64 encoding format.

#### Return Result
Returns data in binary format.

####  Example
1. Convert a BASE64 string to text data:
```
SELECT CAST(unbase64('SGVsbG9Xb3JsZA==') AS STRING);
```
Results:
```
HelloWorld
```
2. Convert BASE64 string to BLOB data:
```
SELECT unbase64('SGVsbG9Xb3JsZA==') AS BLOB;
```
Results:
```
[48 65 6c 6c 6f 57 6f 72 6c 64]

```
3. Convert multiple BASE64 strings to text data and concatenate them:
```
SELECT CONCAT(CAST(unbase64('SGVsbG8=') AS STRING), CAST(unbase64('U3RyaW5n') AS STRING)) AS RESULT;
```
Results:
```
HelloString
```
4. Extract the BASE64 encoded field from the table and convert it to text data:
```
SELECT CAST(unbase64(base64_column) AS STRING) AS text_data
FROM my_table;
```
Results:
```
text_data
----------
HelloWorld
```