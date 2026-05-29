### DATE_TRUNC 
```sql
date_trunc(field, expr)
```
####  Description
The DATE_TRUNC function is used to truncate timestamp data to a specific point in time according to the specified field. This function can truncate time to different levels such as year, quarter, month, week, day, hour, minute, second, millisecond, or microsecond based on different field parameters.

#### Parameter Description
* field (string type): Represents the time field to truncate, common fields include 'YEAR', 'QUARTER', 'MONTH', 'WEEK', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'MILLISECOND', and 'MICROSECOND'. Field names are case-insensitive.
* expr (date/timestamp_ltz/string type): Represents the time data to be truncated.

#### Return Type
timestamp type.

####  Example
1. Truncate to the first day of the specified year (time part set to zero):
```sql
SELECT date_trunc('YEAR', '2022-03-26 16:24:52.656');
-- Return result: 2022-01-01 00:00:00
```
2. Truncate to the first day of the specified quarter (time part set to zero):
```sql
SELECT date_trunc('QUARTER', '2022-03-26 16:24:52.656');
-- Return result: 2022-01-01 00:00:00
```
3. Truncate to the first day of the specified month (time part set to zero):
```sql
   SELECT date_trunc('MONTH', '2022-03-26 16:24:52.656');
   -- Return result: 2022-03-01 00:00:00
   ```
4. Truncate to the Monday of the specified week (time part set to zero):
```sql
SELECT date_trunc('WEEK', '2022-03-26 16:24:52.656');
-- Return result: 2022-03-21 00:00:00
```
5. Truncate to the specified date (set the time part to zero):
```sql
SELECT date_trunc('DAY', '2022-03-26 16:24:52.656');
-- Return result: 2022-03-26 00:00:00
```
6. Truncate to the specified hour (minute, second, and millisecond parts set to zero):
```sql
SELECT date_trunc('HOUR', '2022-03-26 16:24:52.656');
-- Return result: 2022-03-26 16:00:00
```
7. Truncate to the specified minute (set the second and millisecond parts to zero):
```sql
SELECT date_trunc('MINUTE', '2022-03-26 16:24:52.656');
-- Return result: 2022-03-26 16:24:00
```
8. Truncate to the specified second (milliseconds set to zero):
```sql
SELECT date_trunc('SECOND', '2022-03-26 16:24:52.656');
-- Return result: 2022-03-26 16:24:52
```
#### Notes
* When the expr parameter is of string type, ensure the string format is correct, otherwise it may cause the function to fail.
* This function does not alter the original time data for truncation operations, it only returns the truncated time result.