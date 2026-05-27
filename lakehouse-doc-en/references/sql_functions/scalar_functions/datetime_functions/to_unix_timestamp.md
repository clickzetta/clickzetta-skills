### TO_UNIX_TIMESTAMP

###  Description

The `TO_UNIX_TIMESTAMP` function is used to convert different types of datetime expressions into Unix timestamps (UTC). A Unix timestamp is the total number of seconds from '1970-01-01 00:00:00' UTC to the specified time. If the `fmt` parameter is provided, `expr` is parsed according to that format; otherwise, it is parsed according to the default 'yyyy-MM-dd HH\:mm:ss' format. If the datetime in `expr` is illegal or cannot be parsed, the function will return null.

### Parameter Description

* `expr` (string): The datetime string to be converted.
* `fmt` (string, optional): The format of the datetime string. Defaults to 'yyyy-MM-dd HH\:mm:ss'.

### Return Result

Returns a Unix timestamp of type bigint.

### Usage Example

1. Convert a string in the default format to a Unix timestamp:
```sql
SELECT TO_UNIX_TIMESTAMP('2022-02-01 10:23:32') as res;
+------------+
|    res     |
+------------+
| 1643682212 |
+------------+
```
```markdown
2. Convert a custom formatted string to a Unix timestamp:
```
```sql
SELECT TO_UNIX_TIMESTAMP('2022/02/01 10:23:32.121', 'yyyy/MM/dd HH:mm:ss.SSS') as res;
+------------+
|    res     |
+------------+
| 1643682212 |
+------------+
```
3. Convert illegal date-time strings:
```sql
SELECT TO_UNIX_TIMESTAMP('2022-02-30 10:23:32');
+------+
| res  |
+------+
| null |
+------+
```
### Precautions

* When the `fmt` parameter is not provided or is incorrect, the default format will be used for parsing.
* If the input date-time string cannot be parsed or is illegal, the function will return null.
* Please ensure that the date-time string in the `expr` parameter matches the format of the `fmt` parameter (if any) to obtain the correct conversion result.