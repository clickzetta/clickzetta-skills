### DATE\_FORMAT 
```sql
DATE_FORMAT(expr, fmt)
```
####  Description

The `DATE_FORMAT` function is used to convert different types of time expressions (such as strings, timestamps, etc.) into date strings according to a specified format.

#### Parameter Description

* **expr**: Can be an expression of types such as string, timestamp, timestamp with timezone, etc.
* **fmt**: A string used to describe the target date format. For specific formats, refer to the [DateTimePatterns](datetime_patterns.md) page.

#### Return Type

Returns a date string representing the date converted according to the specified format.

####  Example

1. Convert a string type time expression to a date string:

```sql
SELECT DATE_FORMAT('2022-05-01', 'yyyy-MM-dd');
-- Output result: 2022-05-01
```
2. Convert the current timestamp to a date string:
```sql
SELECT DATE_FORMAT(TIMESTAMP "2022-05-01 12:00:00", 'yyyy-MM-dd HH:mm:ss');
-- Output result: 2022-05-01 12:00:00
```
3. Convert the current timestamp to a date string with week information:
```sql
SELECT DATE_FORMAT(TIMESTAMP "2022-05-01 12:00:00", 'yyyy-MM-dd EE');
-- Output result: 2022-05-01 Sun
```
#### Notes 
* When the format of the input time expression does not match the actual type, it may lead to conversion failure.
* When using the `DATE_FORMAT` function, please ensure that the format of the `fmt` parameter is correct to avoid erroneous output results.

Through the above examples and explanations, you can flexibly use the `DATE_FORMAT` function to format time expressions to meet your needs in actual business scenarios.