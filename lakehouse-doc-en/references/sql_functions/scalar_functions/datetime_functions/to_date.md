### TO_DATE 
```sql
TO_DATE(expr [, fmt])
```
####  Description
The TO_DATE function is used to convert a string expression (expr) to a date type according to the specified format (fmt). If the fmt parameter is not provided, the conversion will be based on the system's default date format. If the expression contains an invalid date format, the conversion result will be null.

#### Parameter Description
- **expr** (string): The string expression to be converted.
- **fmt** (string, optional): The format of the date in the string expression. If this parameter is not provided, the conversion will be based on the system's default date format.

#### Return Result
Returns the converted date type result.

#### Usage Example
1. Convert a string to a date (default format):
```sql
SELECT TO_DATE('2022-02-01');
-- Return result: 2022-02-01
```
2. Convert the string to a date in the specified format:
```sql
SELECT TO_DATE('01/02/2022', 'dd/MM/yyyy');
-- Return result: 2022-02-01
```
3. Using Different Country Date Formats for Conversion:
```sql
SELECT TO_DATE('02/01/2022', 'MM/dd/yyyy');
-- Return result: 2022-02-01 (In the US format, the month and day are reversed)
```
4. Handling illegal date formats during the conversion process:
```sql
SELECT TO_DATE('2022/13/01', 'yyyy/MM/dd');
-- Return result: null (because the 13th month is not a valid month)
```
#### Notes
- Ensure that the input string expression conforms to the specified date format, otherwise the conversion result may be null.
- When handling user input dates, it is recommended to validate the input values to avoid potential security risks.
- The implementation of the TO_DATE function may vary slightly in different database systems, please refer to the relevant documentation for the specific database system being used.