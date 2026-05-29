### RTRIM Function

#### Overview
The RTRIM function is used to remove specified characters or spaces from the right side of the string `str`. If the `trimStr` parameter is not provided, all spaces on the right side of the string are removed by default.

#### Syntax
```
rtrim(str, [trimStr])
```
#### Parameters
- `str` (string): The original string that needs to be processed.
- `trimStr` (string, optional): Specifies the set of characters to be removed from the right side of the string.

#### Return Value
Returns the processed string.

#### Usage Example

1. Remove all spaces from the right side of the string:
   ```sql
   > SELECT rtrim('   Hello World   ');
   'Hello World'
   ```
2. Remove specific characters from the right side of the string:
   ```sql
   > SELECT rtrim('Hello-World-', '-');
   'Hello-World'
   ```
3. Combining the RTRIM Function with Other String Operations:
   ```sql
   > SELECT 'X' || rtrim('    HelloWorld    ') || 'X';
   'XHello WorldX'
   ```
4. Use the RTRIM function in the query to process the result column:
   ```sql
   > SELECT rtrim(column_name) AS trimmed_column FROM table_name;
   ```
5. Use the RTRIM function to process user input data to remove unwanted trailing characters:
   ```sql
   > SELECT rtrim(user_input, '!?.');
   ```
Through the above example, you can see that the RTRIM function is very flexible and practical when handling strings. You can freely adjust and combine the use of the RTRIM function as needed to remove unwanted characters in various scenarios.