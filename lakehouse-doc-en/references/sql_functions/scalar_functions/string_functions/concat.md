### CONCAT 

#### Description
The `CONCAT` function is used to concatenate multiple strings, arrays, or binary data. Depending on the type of input parameters, the `CONCAT` function can perform the following operations:
1. Combine multiple array elements into a new array.
2. Concatenate multiple strings into a new string.
3. Concatenate multiple binary data into new binary data.

#### Syntax
```
CONCAT(array1, array2, ..., arrayN)
CONCAT(str1, str2, ..., strN)
CONCAT(binary1, binary2, ..., binaryN)
```
#### Parameters
- `array1 ~ arrayN`: Type `array<T>`, representing the arrays to be concatenated.
- `str1 ~ strN`: Type `string`, representing the strings to be concatenated.
- `binary1 ~ binaryN`: Type `binary`, representing the binary data to be concatenated.

#### Return Results
- Array overload version: Returns a new array of type `array<T>`.
- String overload version: Returns a concatenated string.
- Binary overload version: Returns concatenated binary data.

#### Examples
1. Concatenate two arrays:
```sql
SELECT CONCAT(array(1, 2), array(3, 4));
```
Results:
```
[1, 2, 3, 4]
```
2. Connecting multiple strings:
```sql
SELECT CONCAT('hello', '-', 'world');
```
Results:
```
hello-world
```
3. Connect two binary data:
```sql
SELECT CONCAT(CAST('123' AS BINARY), CAST('456' AS BINARY));
```
Results:
```
[31 32 33 34 35 36] 
```
4. Connecting Strings and Numbers (Note: Numbers need to be converted to strings first):
```sql
SELECT CONCAT('The price is ', CAST(100 AS STRING), ' dollars.');
```
Results:
```
The price is 100 dollars.
```
5. Using the `CONCAT` function to concatenate multiple fields:
```sql
SELECT CONCAT(first_name, ' ', last_name) AS full_name
FROM users;
```
Results:
```
full_name
----------
John Doe
Jane Smith
```