### Binary

####  Description
The `BINARY()` function is used to convert string-type data into a binary form byte stream. This function accepts a string parameter and returns a result of binary data type.

#### Syntax
```
BINARY(str)
```
#### Parameters
- `str`: The string type data that needs to be converted.

#### Return Result
- Returns a byte stream of binary data type.

#### Usage Example
1. Convert the string "hello" to binary form:
   ```sql
   SELECT BINARY('hello');
    Result:
     [68 65 6c 6c 6f] 
   ```

2. Convert a string containing special characters "élle!" to binary form:
   ```sql
   SELECT BINARY('élle!');
    Result:
    [c3 a9 6c 6c 65 21]
   ```


#### Notes
- When the input string contains non-ASCII characters, the `BINARY()` function will perform an encoding conversion to correctly represent it in binary form.
- When handling binary data, pay attention to the character set and collation settings to ensure the correctness and consistency of the data.

By using the `BINARY()` function, you can easily store and manipulate binary data in the database, such as images, audio, and video files.