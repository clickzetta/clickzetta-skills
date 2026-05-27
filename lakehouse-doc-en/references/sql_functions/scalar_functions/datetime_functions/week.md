### `WEEK`

###  Description
The `WEEK` function is used to calculate and return the week number of a given date (`date` or `timestamp_ltz` type) within the year. Note that this function defines the start of the week as Monday, and the first week of the year is defined as the first week that contains at least three days.

### Parameter Description
- `expr`: The input date or timestamp (`date` or `timestamp_ltz`) parameter.

### Return Type
- Returns an integer representing the week number of the given date within the year.

### Usage Example
1. Calculate the week number of a specific date within the year:
```sql
SELECT WEEK('2022-03-31'); -- Result: 13
```
2. For a timestamp type of data, you can also calculate the week number it belongs to:
```sql
SELECT WEEK(TIMESTAMP "2022-03-31 03:21:00"); -- The result is also: 13
```
3. You can use the `WEEK` function in combination with other date functions for more complex date calculations, such as finding the week number of the current time:
```sql
SELECT WEEK(CURRENT_TIMESTAMP()) AS week_number; -- The result will display the week number of the current date
```
### Notes
- This function has certain requirements for the input date format, ensure that the input date format is correct.
- When the input timestamp contains timezone information, the function will consider the result after timezone conversion for calculation.

The above is the detailed description and usage example of the `WEEK` function. With this function, users can easily obtain the week position of a specific date in a year, thereby performing related date calculations and data analysis.