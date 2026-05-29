### UNHEX 
```
unhex(expr)
```
####  Description
UNHEX function is used to convert a string in hexadecimal format to binary format. This function accepts a string parameter and returns the corresponding binary data.

#### Parameter Description
* expr (string): The hexadecimal format string that needs to be converted.

#### Return Result
Returns data in binary format.

####  Example
1. Convert a hexadecimal string to text content:
```sql
SELECT STRING(UNHEX('48656C6C6F576F726C64'));
```
Results:
```
HelloWorld
```
2. Convert hexadecimal string to image data:
```sql
SELECT UNHEX('89504E470D0A1A0A0000') AS image_data;
```
Results:
```
 [89 50 4e 47 0d 0a 1a 0a 00 00]
```
3. Convert the hexadecimal string to audio data:
```sql
SELECT UNHEX('25504446') AS audio_data;
```
Results:
```
 [25 50 44 46]
```
4. Convert hexadecimal string to video data:
```sql
SELECT UNHEX('000001BA') AS video_data;
```
Results:
```
[00 00 01 ba]
```