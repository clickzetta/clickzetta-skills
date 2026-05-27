### TO_TIMESTAMP_NTZ 
```sql
to_timestamp_ntz(expr [, fmt])
```
###  Description

The TO\_TIMESTAMP\_NTZ function is used to convert different types of datetime expressions (expr) into a timestamp (timestamp\_ntz) type. If the fmt parameter is provided, the function will parse according to the specified format; if fmt is not provided, it will convert according to the default format. If the datetime format in expr is incorrect, the function will return null.

### Parameter Description

* expr (string): The string expression to be converted.
* fmt (string, optional): Specifies the format of the datetime in the string expression.

### Return Result

The converted timestamp (timestamp\_ntz).

### Examples

1. Convert a string to a timestamp according to the specified format:
```SQL
SELECT to_timestamp_ntz('2022/02/01 10:23:32.121', 'yyyy/MM/dd HH:mm:ss.SSS') as ntz;
+-------------------------+
|           ntz           |
+-------------------------+
| 2022-02-01 10:23:32.121 |
+-------------------------+
```
2. If the time format matches yyyy-MM-dd HH:mm:ss.SSS, then there is no need to specify the string format
```SQL
SELECT to_timestamp_ntz('2022-02-01 10:23:32.121') ntz;
+-------------------------+
|           ntz           |
+-------------------------+
| 2022-02-01 10:23:32.121 |
+-------------------------+
```
```markdown
3. Convert different types of date-time strings to timestamps:
```
```SQL
SELECT to_timestamp_ntz('01-02 10:23:32', 'dd-MM HH:mm:ss') ntz;
+---------------------+
|         ntz         |
+---------------------+
| 1970-02-01 10:23:32 |
+---------------------+
```