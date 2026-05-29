### ADD_MONTHS 
```sql
ADD_MONTHS(startDate DATE, numMonths INT)
```
####  Description
The `ADD_MONTHS` function is used to add a specified number of months `numMonths` to a given date `startDate`. The result will return a new date. If the resulting date exceeds the range of days in the target month, the function will automatically adjust the date to the last day of that month. If the calculated result exceeds the date range supported by the system, it will return `NULL`.

#### Parameter Description
- `startDate`: Date type, representing the starting date for the month addition calculation.
- `numMonths`: Integer type, representing the number of months to add. It can be a positive number (indicating a future date) or a negative number (indicating a past date).

#### Return Result
Returns a date type, representing the date after the month addition.

####  Example
1. Example of adding months:
```sql
SELECT ADD_MONTHS('2020-05-31', 3);
-- Result: 2020-08-31
```
2. Example of Reducing Months:
```sql
SELECT ADD_MONTHS('2020-05-31', -3);
-- Result: 2020-02-29
```
3. Example of exceeding the number of days in a month:
```sql
SELECT ADD_MONTHS('2020-04-30', 1);
-- Result: 2020-05-30
```
4. Example of exceeding the system date range:
```sql
SELECT ADD_MONTHS('9999-12-31', 1);
-- Result: NULL
```
#### Notes
- Ensure that the `startDate` parameter is in a valid date format, otherwise the function will return `NULL`.
- When `numMonths` is a relatively large or small integer, please check whether the resulting date is within the date range supported by the system.