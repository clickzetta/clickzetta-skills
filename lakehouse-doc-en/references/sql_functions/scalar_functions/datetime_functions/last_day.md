### LAST_DAY 
#### Description
The `LAST_DAY` function is used to obtain the last day of the month for a given date (`date` type) or timestamp (`timestamp_ltz` type) parameter. This function is commonly used for date calculations and report generation, helping users quickly determine the end date of the month for a specific date.

#### Parameters
- `expr`: The input date or timestamp parameter, of type `date` or `timestamp_ltz`.

#### Return Value
Returns a result of type `date`, representing the last day of the month for the input parameter.

####  Example
1. Determine the last day of the month for a regular date:
```sql
SELECT LAST_DAY('2020-02-05'); -- Result is 2020-02-29
```
2. Determine the last day of the month for a timestamp:
```sql
SELECT LAST_DAY(TIMESTAMP_LTZ "2020-02-05 12:00:00"); -- Result is 2020-02-29
```
3. Calculate the last day of February in a leap year:
```sql
SELECT LAST_DAY('2020-02-05'); -- Result is 2020-02-29
```
In this example, since the year 2020 is a leap year, February has 29 days, so the return is 2020-02-29.
4. For February in non-leap years:
```sql
SELECT LAST_DAY('2021-02-05'); -- Result is 2021-02-28
```
In this example, the year 2021 is not a leap year, so the last day of February is 2021-02-28.

#### Notes
- When the input date or timestamp parameter is the last day of the current month, the `LAST_DAY` function will return the date or timestamp itself.
- When handling timestamp parameters, be aware of the impact of time zones. Timestamps of type `timestamp_ltz` do not include time zone information, so the current time zone will be considered in calculations.

With the above examples and explanations, you can better understand the purpose and usage of the `LAST_DAY` function, thereby performing date processing more effectively in actual work.