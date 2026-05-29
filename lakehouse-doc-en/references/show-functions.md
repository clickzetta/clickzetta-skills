## Function Description
This command is used to display all available functions within the current workspace, including built-in functions and external functions. Through this command, users can quickly understand and select the required functions for data query and processing.

## Syntax Format
```SQL
SHOW FUNCTIONS [ LIKE 'pattern' ]
```
## Parameter Description
- **LIKE 'pattern'**: This parameter is used to filter based on function names, displaying only functions that match the specified pattern. SQL wildcards are supported, including the percentage sign (%) to represent any number of characters and the underscore (_) to represent any single character.

## Usage Example

1. View all functions:
   ```SQL
   SHOW FUNCTIONS;
   ```
2. Filter results based on partial keywords in the function name, for example, find all functions that contain "ABS":
   ```SQL
   SHOW FUNCTIONS LIKE '%ABS%';
   ```
3. Find a specific function, for example, find a function named "SQRT":
   ```SQL
   SHOW FUNCTIONS LIKE 'SQRT';
   ```
4. Use wildcards to find all functions starting with "DATE":
   ```SQL
   SHOW FUNCTIONS LIKE 'DATE%';
   ```
5. Combine wildcards for more precise searches, for example, to find functions that contain "DATE" and end with "DIFF":
   ```SQL
   SHOW FUNCTIONS LIKE 'DATE%DIFF';
   ```
## Notes
- When the LIKE clause is not specified, all available functions will be displayed.
- When using wildcards, make sure they follow immediately after the LIKE keyword without any spaces in between.
- When using SQL wildcards, be careful to avoid using too many wildcards to prevent affecting query performance.

Through the above examples and instructions, users can more easily find and use the required functions, thereby improving the efficiency of data processing and analysis.