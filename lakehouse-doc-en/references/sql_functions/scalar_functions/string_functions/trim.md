### TRIM 
```
trim(str [, trimStr])
```
####  Description
The TRIM function is used to remove specified characters (or spaces) from both sides of the string `str`. If the `trimStr` parameter is not specified, all space characters on both sides of the string are removed by default.

#### Parameter Description
- `str` (string): The original string to be processed.
- `trimStr` (string, optional): The set of characters to be removed. If this parameter is omitted, space characters are removed by default.

#### Return Result
Returns the processed string.

####  Example
1. Remove spaces from both ends of the string:
   ```sql
   > SELECT '  Hello, World!  ' AS original, TRIM(original) AS trimmed;
    +----------------+--------+
    | original       | trimmed |
    +----------------+--------+
    |  Hello, World!  | Hello, World! |
    +----------------+--------+
   ```
2. Remove specific characters (such as asterisks) from both ends of a string:
   ```sql
   > SELECT '**Hello, World!**' AS original, TRIM('**Hello, World!**' ,'**' ) AS trimmed;
    +----------------+--------+
    | original       | trimmed |
    +----------------+--------+
    | **Hello, World!** | Hello, World! |
    +----------------+--------+
   ```
3. Remove leading zero characters from a string:
   ```sql
   > SELECT '000Hello, World!' AS original, TRIM('000Hello, World!', '0' ) AS trimmed;
    +----------------+--------+
    | original       | trimmed |
    +----------------+--------+
    | 000Hello, World! | Hello, World! |
    +----------------+--------+
   ```
4. Remove the percentage sign from the right side of the string:
   ```sql
   > SELECT 'Hello, World!%' AS original, TRIM('Hello, World!%', '%' ) AS trimmed;
    +----------------+--------+
    | original       | trimmed |
    +----------------+--------+
    | Hello, World!% | Hello, World! |
    +----------------+--------+
   ```