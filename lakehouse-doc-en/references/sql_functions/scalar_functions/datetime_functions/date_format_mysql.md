### DATE_FORMAT_MYSQL 
```
date_format_mysql(expr, fmt)
```
####  Description
The DATE_FORMAT_MYSQL function is used to convert different types of timestamps (including datetime, timestamp_ltz, string, etc.) into a string format according to the specified format. This function is compatible with MySQL database date and time formatting rules.

#### Parameter Description
- `expr`: The input timestamp, which can be in datetime, timestamp_ltz, or string format.
- `fmt`: A string describing the date and time format. For specific formatting options, please refer to the MySQL official documentation: [DATE_FORMAT()](https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html#function_date-format)

Formatting options description:

| Option | Description |
| ---- | ---- |
| `%a` | Abbreviated weekday name (e.g., Sun to Sat) |
| `%b` | Abbreviated month name (e.g., Jan to Dec) |
| `%c` | Month number (00 to 12) |
| `%D` | Day of the month with English suffix (e.g., 1st, 2nd, 3rd, ...) |
| `%d` | Day of the month, numeric (00 to 31) |
| `%e` | Day of the month, numeric (0 to 31) |
| `%f` | Microseconds (000000 to 999999) |
| `%H` | Hour (00 to 23) |
| `%h` | Hour (01 to 12) |
| `%I` | Hour (01 to 12) |
| `%i` | Minutes (00 to 59) |
| `%j` | Day of the year (001 to 366) |
| `%k` | Hour (0 to 23) |
| `%l` | Hour (1 to 12) |
| `%M` | Month name (January to December) |
| `%m` | Month number (00 to 12) |
| `%p` | AM or PM |
| `%S` | Seconds (00 to 59) |
| `%s` | Seconds (00 to 59) |
| `%T` | 24-hour time (hh:mm:ss) |
| `%v` | Week number (01 to 53), with Monday as the first day of the week; [WEEK()](https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html#function_week) mode 3; used with `%x` |
| `%W` | Weekday name (Sunday to Saturday) |
| `%w` | Day of the week (0 for Sunday, 6 for Saturday) |
| `%x` | Year for the week where Monday is the first day of the week, numeric, four digits; used with `%v` |
| `%Y` | Year, numeric, four digits |
| `%y` | Year, numeric, two digits |
| `%%` | A literal `%` character |

#### Return Result
Returns the date and time string converted according to the specified format.

####  Example
1. Convert the current time to a string format with seconds:
```sql
SELECT date_format_mysql(now(), '%Y-%m-%d %H:%i:%s');
```
2. Convert the timestamp to a format that only includes hours and minutes:
```sql
SELECT date_format_mysql(timestamp '2023-03-22 13:45:00', '%H:%i');
```
Through the above examples, you can see the application of the DATE_FORMAT_MYSQL function in different scenarios. You can adjust the `fmt` parameter as needed to get your desired date and time format.