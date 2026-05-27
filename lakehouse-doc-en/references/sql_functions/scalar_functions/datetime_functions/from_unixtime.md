### FROM_UNIXTIME 
```
from_unixtime(unixTime [, fmt])
```
####  Description
The FROM_UNIXTIME function is used to convert a UNIX timestamp (in seconds) into a date-time string in the current time zone. If an optional fmt parameter is provided, the function returns the date-time string in the specified format. If the fmt parameter is not provided, it defaults to the 'yyyy-MM-dd HH:mm:ss' format.

#### Parameter Description
- `unixTime` (bigint): Represents the UNIX timestamp, in seconds.
- `fmt` (string, optional): Date-time format string, refer to the following for specific formats.

#### Return Result
Returns a string type date-time value.

#### Usage Instructions
- When the `fmt` parameter is empty or not provided, the default format 'yyyy-MM-dd HH:mm:ss' is used.
- The `fmt` parameter supports the following format characters:
  - `yyyy`: Year (four digits)
  - `M`: Month (two digits, 01-12)
  - `MM`: Month (two digits, 01-12, with leading zero)
  - `dd`: Day (two digits, 01-31)
  - `HH`: Hour (two digits, 00-23)
  - `mm`: Minute (two digits, 00-59)
  - `ss`: Second (two digits, 00-59)

#### Example
- Example 1: Convert UNIX timestamp 0 to a date-time string in the default format.
```sql
SELECT from_unixtime(0);
-- Result: 1970-01-01 08:00:00
```
- Example 2: Convert the UNIX timestamp 1617184000 to a date string in the 'yyyy-MM-dd' format.
```sql
SELECT from_unixtime(1617184000, 'yyyy-MM-dd');
-- Result: 2021-03-31
```
- Example 3: Convert the UNIX timestamp 1617184000 to a custom formatted date-time string.
```sql
SELECT from_unixtime(1617184000, 'yyyy year MM month dd day HH hour mm minute ss second');
-- Result: 2021 year 03 month 31 day 00 hour 00 minute 00 second
```
By the above example, you can flexibly use the FROM_UNIXTIME function to convert UNIX timestamps to the desired datetime format.