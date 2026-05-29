### DATEADD 
```
timestampadd(unit, count, ts)
dateadd(unit, count, ts)
```
####  Description
The alias function of `TIMESTAMPADD` is used to add or subtract a specified number of time units `unit` to a given timestamp `ts`. If `count` is positive, it means addition; if negative, it means subtraction.

Acceptable time units `unit` include (case insensitive):
- MICROSECOND
- MILLISECOND
- SECOND
- MINUTE
- HOUR
- DAY
- DAYOFYEAR
- WEEK
- MONTH
- QUARTER
- YEAR

#### Parameter Description
- `unit`: timestamp_ltz type, representing the time unit to be added.
- `count`: bigint type, representing the number to be added or subtracted.
- `ts`: timestamp_ltz type, representing the current timestamp.

#### Return Type
Returns a new timestamp_ltz type timestamp.

####  Example
1. Add 1 year:
```sql
SELECT dateadd(YEAR, 1, '2020-10-10 01:02:03');
-- Result: 2021-10-10 01:02:03 
```
2. Reduce by 30 days:
```sql
SELECT dateadd(DAY, -30, '2020-10-10 01:02:03');
-- Result: 2020-09-10 01:02:03
```
3. Add 12 hours:
```sql
SELECT dateadd(HOUR, 12, '2020-10-10 01:02:03');
-- Result: 2020-10-10 13:02:03
```
4. Reduce by 3 months:
```sql
SELECT dateadd(MONTH, -3, '2020-10-10 01:02:03');
-- Result: 2020-07-10 01:02:03
```
5. Add 2 milliseconds:
```sql
SELECT dateadd(MILLISECOND, 2, '2020-10-10 01:02:03.999');
-- Result: 2020-10-10 01:02:04.001
```
### Notes
- When handling timestamps, ensure that the parameter format is correct, otherwise it may cause the function to fail.
- When converting time units, pay attention to special cases such as leap years and the number of days in a month to avoid incorrect results.
- Please choose the appropriate time unit and increment according to actual needs to avoid unnecessary time errors.