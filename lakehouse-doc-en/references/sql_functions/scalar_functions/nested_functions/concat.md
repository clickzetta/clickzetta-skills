### CONCAT Function

#### Overview
The `CONCAT` function is used to concatenate multiple arrays, strings, or binary data to generate a new array, string, or binary data.

#### Syntax
```
CONCAT(array1, array2, ..., arrayN)
CONCAT(str1, str2, ..., strN)
CONCAT(binary1, binary2, ..., binaryN)
```
#### Function Description
1. Array Concatenation: Merge all elements from `array1` to `arrayN` into a new array.
2. String Concatenation: Concatenate all strings from `str1` to `strN` into a new string.
3. Binary Data Concatenation: Concatenate all binary data from `binary1` to `binaryN` into a new binary data.

#### Parameter Description
- `array1` to `arrayN`: `array<T>` type, representing the arrays to be concatenated.
- `str1` to `strN`: `string` type, representing the strings to be concatenated.
- `binary1` to `binaryN`: `binary` type, representing the binary data to be concatenated.

#### Return Value
- Array Concatenation Version: Returns a new `array<T>` type array.
- String Concatenation Version: Returns a new string.
- Binary Data Concatenation Version: Returns a new binary data.

#### Usage Example
```sql
-- Array concatenation example
SELECT CONCAT(array(1, 2), array(3, 4));
-- Result: [1, 2, 3, 4]

-- String concatenation example
SELECT CONCAT('hello', '-', 'world');
-- Result: 'hello-world'

-- Binary data concatenation example
SELECT CONCAT(CAST('123' AS BINARY), CAST('456' AS BINARY));
-- Result: '123456'
```
#### Notes
- When concatenating empty arrays or empty strings, the `CONCAT` function will return an empty array or empty string.
- When concatenating multiple binary data, ensure that they have the same length, otherwise, it may result in incorrect concatenation.
- When concatenating strings, if you need to add a separator between the concatenated strings, you can pass it as an additional parameter to the `CONCAT` function.

#### Summary
The `CONCAT` function provides a simple and efficient way to concatenate arrays, strings, and binary data. By using this function, you can easily combine multiple pieces of data into a unified data structure for further processing and analysis.