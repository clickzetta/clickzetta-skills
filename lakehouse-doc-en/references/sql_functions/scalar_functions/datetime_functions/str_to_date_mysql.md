## Function 

`STR_TO_DATE_MYSQL` is a SQL function used to convert a string into a date, compatible with the `STR_TO_DATE` function in MySQL. This function can parse a string into a date type based on the specified format, making it very suitable for handling text fields that contain date information.

## Syntax
```SQL
STR_TO_DATE_MYSQL(date_string, format_string)
```
## Parameter Description

* **date\_string**: The date string to be converted.
* **format\_string**: The format of the date string. Refer to the [MySQL official website](https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html#function_date-format) for date string formats. This string defines how the date part of `date_string` should be parsed.

## Return Result

This function returns a date type (DATE | TIMESTAMP) value, representing the successfully parsed date.

## Example

Example 1: Basic usage
```SQL
SELECT STR_TO_DATE_MYSQL('2024-07-29', '%Y-%m-%d');
+------------+
|    res     |
+------------+
| 2024-07-29 |
+------------+
```
Example 2: Format as timestmap\_ltz
```SQL
SELECT STR_TO_DATE_MYSQL('20130101 1130','%Y%m%d %h%i') ;
+---------------------+
|         res         |
+---------------------+
| 2013-01-01 11:30:00 |
+---------------------+
```