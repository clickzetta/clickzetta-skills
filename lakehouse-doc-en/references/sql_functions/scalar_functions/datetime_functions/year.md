### YEAR 

####  Description
The YEAR function is used to extract the year part from different types of date expressions and return it as an integer.

#### Syntax
```sql
YEAR(expr)
```
#### Parameter Description
- `expr`: Can be different types of date expressions, including strings (date/string), time (time/timez), and timestamps (timestamp/timestamptz).

#### Return Type
Integer (int)

#### Usage Example
1. Extract the year from a date in string form:
```sql
SELECT YEAR('2022-03-31');
-- Result: 2022
```
2. Extract the year from a date in timestamp format:
```sql
SELECT YEAR(TIMESTAMP "2022-03-31 14:59:59");
-- Result: 2022
```
3. Extract the year from the current timestamp:
```sql
SELECT YEAR(now());
-- Result: Returns the year based on the current timestamp
```
#### Notes
- When the input date expression is of string type, please ensure it conforms to the date format supported by the database, otherwise it may cause parsing errors.
- When the input time expression only contains the time part, the YEAR function will return 0000 as the year.
- When using the YEAR function, please ensure the parameter type is correct to avoid type mismatch errors.