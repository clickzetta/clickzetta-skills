### HEX 
```sql
HEX(expr)
```
####  Description
The HEX function is used to convert different types of data into a hexadecimal format string. This function accepts various input types, including strings, binary numbers, and big integers, and converts them into the corresponding hexadecimal representation.

#### Parameter Description
* **expr**: string/binary/bigint
  - The input data to be converted.

#### Return Result
Returns a string representing the hexadecimal form of the input data.

#### Usage Example
1. Convert a string to hexadecimal:
   ```sql
   SELECT HEX('HelloWorld');
   ```
Result: 
   ```
   48656C6C6F576F726C64
   ```
2. Convert Binary to Hexadecimal:
   ```sql
   SELECT HEX(CAST('11001010' AS BINARY));
   ```
Result:
   ```
   3131303031303130

   ```
3. Convert large integers to hexadecimal:
   ```sql
   SELECT HEX(1234567891234567);
   ```
Result:
   ```
   462D53C9BAF07
   ```
#### Notes
- For empty string input, the HEX function will return an empty string.
- When the input data cannot be converted to hexadecimal, the function will return NULL.