### TIMESTAMPDIFF 
```sql
TIMESTAMPDIFF(unit, startTimestamp, endTimestamp)
```
####  Description

The TIMESTAMPDIFF function is used to calculate the time difference between two timestamps (startTimestamp and endTimestamp) and return the result in the specified unit (unit). This function supports various time units, including microseconds (MICROSECOND), milliseconds (MILLISECOND), seconds (SECOND), minutes (MINUTE), hours (HOUR), days (DAY), weeks (WEEK), months (MONTH), quarters (QUARTER), and years (YEAR).

#### Parameter Description

* unit: The unit of the desired time difference, optional values include MICROSECOND (microseconds), MILLISECOND (milliseconds), SECOND (seconds), MINUTE (minutes), HOUR (hours), DAY (days), WEEK (weeks), MONTH (months), QUARTER (quarters), and YEAR (years).
* startTimestamp: The start timestamp, must be of timestamp type.
* endTimestamp: The end timestamp, must be of timestamp type.

#### Return Result

Returns an integer value representing the time difference between startTimestamp and endTimestamp, with the unit determined by the unit parameter.

#### Usage Example

1. Calculate the number of microseconds between two timestamps:
```sql
SELECT TIMESTAMPDIFF(MICROSECOND, '2022-03-31 00:00:00', '2022-03-30 06:00:00') as res;
+--------------+
|     res      |
+--------------+
| -64800000000 |
+--------------+
```
```markdown
2. Calculate the number of hours between two timestamps:
```
```sql
SELECT TIMESTAMPDIFF(HOUR, '2022-03-31 00:00:00', '2022-03-30 06:00:00') as res ;
+-----+
| res |
+-----+
| -18 |
+-----+
```
3. Calculate the number of days between two timestamps:
```sql
SELECT TIMESTAMPDIFF(DAY, '2022-03-31 00:00:00', '2022-03-30 06:00:00') as res;
+-----+
| res |
+-----+
| 0   |
+-----+
```
4. Calculate the number of months between two timestamps:
```sql
SELECT TIMESTAMPDIFF(MONTH, '2022-03-31 00:00:00', '2022-02-28 06:00:00')as res;
+-----+
| res |
+-----+
| -1  |
+-----+
```

5. Calculate the number of years between two timestamps:

```sql
SELECT TIMESTAMPDIFF(YEAR, '2022-03-31 00:00:00', '2021-03-30 06:00:00') as res;
+-----+
| res |
+-----+
| -1  |
+-----+
```