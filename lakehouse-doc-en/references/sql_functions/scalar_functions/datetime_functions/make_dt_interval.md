### MAKE\_DT\_INTERVAL

The `MAKE_DT_INTERVAL` function is used to construct a time interval value of type `interval day to time`. This function accepts four optional parameters: days, hours, minutes, and seconds. The seconds parameter supports decimals with millisecond precision.

#### Function 
```
make_dt_interval([days[, hours[, mins[, secs]]]])
```
* `days`: int type, represents the number of days.
* `hours`: int type, represents the number of hours.
* `mins`: int type, represents the number of minutes.
* `secs`: decimal type, represents the number of seconds, supports decimals, precision up to milliseconds.

#### Return Result

The function returns a value of type `interval day to time`.

####  Example

**Example 1**: Create a time interval of 1 day, 2 hours, 3 minutes, and 4 seconds.
```sql
SELECT make_dt_interval(1, 2, 3, 4);
+------------------------------+
| make_dt_interval(1, 2, 3, 4) |
+------------------------------+
| 1 02:03:04.000000000         |
+------------------------------+
```
**Example 2**: Create a time interval that only includes seconds (e.g., 1 minute 20 seconds).
```sql
SELECT make_dt_interval(0, 0, 0, 80);
+-------------------------------+
| make_dt_interval(0, 0, 0, 80) |
+-------------------------------+
| 0 00:01:20.000000000          |
+-------------------------------+
```
**Example 3**: Create a time interval that only includes days (e.g., 5 days).
```sql
SELECT make_dt_interval(5);
+----------------------+
| make_dt_interval(5)  |
+----------------------+
| 5 00:00:00.000000000 |
+----------------------+
```
**Example 4**: Create a time interval that includes days, hours, and seconds (e.g., 3 days, 10 hours, 30 seconds).
```sql
SELECT make_dt_interval(3, 10, 0, 30);
+--------------------------------+
| make_dt_interval(3, 10, 0, 30) |
+--------------------------------+
| 3 10:00:30.000000000           |
+--------------------------------+
```