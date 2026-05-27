### TO\_TIMESTAMP 
```sql
to_timestamp(expr [, fmt])
```
####  Description

The TO\_TIMESTAMP function is used to convert different types of date-time expressions (expr) into a timestamp type. If the fmt parameter is provided, the function will parse according to the specified format; if fmt is not provided, it will convert according to the default format. If the date-time format in expr is incorrect, the function will return null.

#### Parameter Description

* expr (string): The string expression to be converted.
* fmt (string, optional): Specifies the format of the date-time in the string expression.

#### Return Result

The converted timestamp.

#### Usage Example

1. Convert a string to a timestamp (without specifying the fmt parameter):
   ```sql
   SELECT to_timestamp('2022-02-01 10:23:32.121') as res;
   +-------------------------+
   |           res           |
   +-------------------------+
   | 2022-02-01 10:23:32.121 |
   +-------------------------+
   ```

2. Convert the string to a timestamp according to the specified format:
   ```sql
   SELECT to_timestamp('2022/02/01 10:23:32.121', 'yyyy/MM/dd HH:mm:ss.SSS') as res;
   +-------------------------+
   |           res           |
   +-------------------------+
   | 2022-02-01 10:23:32.121 |
   +-------------------------+
   ```
3. Convert different types of date-time strings to timestamps:
   ```sql
   SELECT to_timestamp('01-02 10:23:32', 'dd-MM HH:mm:ss') as res;
   +---------------------+
   |         res         |
   +---------------------+
   | 1970-02-01 10:23:32 |
   +---------------------+
   ```

4. Convert illegal date-time strings:

   ```sql
   SELECT to_timestamp('2022-02-30 10:23:32.121') as res;
   +-----+
   | res |
   +-----+
   |     |
   +-----+
   ```
Please note that the TO\_TIMESTAMP function will return null when processing illegal date-time strings. Therefore, when using this function, ensure that the input string format is correct. Additionally, you can flexibly handle date-time strings in different formats through the fmt parameter.