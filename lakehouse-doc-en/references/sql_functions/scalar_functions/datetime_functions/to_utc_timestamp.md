### TO\_UTC\_TIMESTAMP 
```
to_utc_timestamp(expr, tz)
```
####  Description

The TO\_UTC\_TIMESTAMP function is used to convert a time in a specified time zone to UTC time. This function accepts two parameters: a timestamp expression (expr) and a time zone string (tz). The function returns a timestamp representing the converted UTC time.

#### Parameter Description

* **expr**: Timestamp type, representing the time to be converted.
* **tz**: String type, representing the time zone of the input time.

#### Return Result

* Returns a timestamp representing the converted UTC time.

#### Usage Example

1. Convert Beijing time to UTC time:
   ```sql
   SELECT TO_UTC_TIMESTAMP('2017-07-14 02:01:00', 'Asia/Shanghai') as res;
   +---------------------+
   |         res         |
   +---------------------+
   | 2017-07-13 18:01:00 |
   +---------------------+
   ```
2. Convert New York time to UTC time:
   ```sql
   SELECT TO_UTC_TIMESTAMP('2017-07-14 10:30:00', 'America/New_York')as res;
   +---------------------+
   |         res         |
   +---------------------+
   | 2017-07-14 14:30:00 |
   +---------------------+
   ```
3. Convert Los Angeles time to UTC time:
   ```sql
   SELECT TO_UTC_TIMESTAMP('2017-07-14 07:45:00', 'America/Los_Angeles') as res;
   +---------------------+
   |         res         |
   +---------------------+
   | 2017-07-14 14:45:00 |
   +---------------------+
   ```
4. Convert London time to UTC time:
   ```sql
   SELECT TO_UTC_TIMESTAMP('2017-07-14 12:00:00', 'Europe/London') as res;
   +---------------------+
   |         res         |
   +---------------------+
   | 2017-07-14 11:00:00 |
   +---------------------+
   ```
Through the above example, it can be seen that the TO\_UTC\_TIMESTAMP function can conveniently convert local times from different regions to UTC time, making it easier to perform cross-time zone time comparisons and calculations.