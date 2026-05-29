### DATEDIFF 

####  Description
The DATEDIFF function is used to calculate the time difference between two dates. This function supports multiple time units, including microseconds (MICROSECOND), milliseconds (MILLISECOND), seconds (SECOND), minutes (MINUTE), hours (HOUR), days (DAY), weeks (WEEK), months (MONTH), quarters (QUARTER), and years (YEAR).

#### Syntax
```
DATEDIFF(unit, startTimestamp, endTimestamp)
```
or
```
DATEDIFF(endDate, startDate)
```
#### Parameter Description
- `unit` (string): Specifies the unit for calculating the time difference. Optional values include: MICROSECOND, MILLISECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR.
- `startTimestamp` (timestamp): The timestamp when the calculation starts.
- `endTimestamp` (timestamp): The timestamp when the calculation ends.
- `endDate` (date): The date when the calculation ends.
- `startDate` (date): The date when the calculation starts.

#### Return Result
Returns an integer representing the time difference between two timestamps or dates.

#### Usage Example
1. Calculate the number of days between two dates:
```sql
SELECT DATEDIFF('2022-03-31', '2022-03-30'); -- The return result is 1
```
2. Calculate the difference in hours between two timestamps:
```sql
SELECT DATEDIFF(HOUR, '2022-03-31 00:00:00', '2022-03-30 06:00:00'); -- Returns result as -18
```
3. Calculate the difference in milliseconds between two timestamps:
```sql
SELECT DATEDIFF(MILLISECOND, '2022-03-30 10:30:00', '2022-03-30 10:30:10'); -- The return result is 10000
```
4. Calculate the difference in the number of quarters between two dates:
```sql
SELECT DATEDIFF(QUARTER, '2022-01-15', '2022-10-20'); -- Returns result as 3
```
5. Calculate the difference in minutes between two timestamps:
```sql
SELECT DATEDIFF(MINUTE, '2022-03-30 08:45:00', '2022-03-30 09:30:00'); -- The return result is 45
```
#### Notes
- When using the DATEDIFF function to calculate the time difference between timestamps, please ensure that the timestamp format is correct.
- When using string parameters, please ensure the date format is correct, otherwise it may lead to inaccurate calculation results.
- When calculating the time difference, please note that a negative result indicates that the startTimestamp or startDate is later than the endTimestamp or endDate.